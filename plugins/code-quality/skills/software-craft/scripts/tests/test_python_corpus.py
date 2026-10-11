#!/usr/bin/env python3
"""Unit tests for python-corpus.py: the merge and drop rules, batch cutting, the brief's
section order and explanation cut, the done list of the triage args, triage-merge over two
batch files, topic-args and save-run. Offline; every fixture lives in a temporary directory.

Run:  python3 -m unittest scripts/tests/test_python_corpus.py   (from the skill directory)
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("python_corpus", os.path.join(SCRIPTS, "python-corpus.py"))
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)


def item(source, code, name="", **fields):
    """One items.jsonl record; fields replace status, category, explanation or any other key."""
    base = {"source": source, "code": code, "name": name, "title": f"{source} {code} title",
            "summary": f"{source} {code} summary", "explanation": "", "url": f"https://example.org/{source}/{code}",
            "default_on": True, "category": "", "status": "stable", "cache_path": f"src/{source}/{code or name}"}
    return base | fields


TOPICS = [
    {"number": 1, "slug": "python-data-model-and-idioms", "title": "Python data model and idioms", "domain": "code",
     "owns": "mutable default arguments", "catalogs": "Ruff B"},
    {"number": 2, "slug": "python-exceptions-and-context-managers", "title": "Python exceptions and context managers",
     "domain": "errors", "owns": "bare except", "catalogs": "Ruff BLE"},
]
UNIVERSAL = [
    {"rule_id": "ERR-08", "title": "A local handler catches only the error types it can handle", "domain": "errors"},
    {"rule_id": "CODE-01", "title": "A name never promises a type", "domain": "code"},
    {"rule_id": "CODE-02", "title": "A routine named as a query hides no state change", "domain": "code"},
]
FIXTURE_ITEMS = [
    item("ruff", "PLW0102", "dangerous-default-value-ruff"),
    item("pylint", "W0102", "dangerous-default-value", category="W"),
    item("ruff", "B006", "mutable-argument-default", explanation="Function defaults are evaluated once. " * 40),
    item("bugbear", "B006"),
    item("ruff", "S602", "subprocess-popen-with-shell-equals-true"),
    item("bandit", "B602", "subprocess_popen_with_shell_equals_true"),
    item("pylint", "E1101", "no-member", category="E"),
    item("pylint", "", "astroid-error", category="F"),
    item("pylint", "C0103", "invalid-name", category="C"),
    item("pylint", "C0301", "line-too-long", category="C"),
    item("pylint", "C0200", "consider-using-enumerate", category="C"),
    item("ruff", "E999", "removed-rule", status="removed"),
    item("sonar", "S5717", "default-mutation"),
    item("ruff", "BLE001", "blind-except"),
    item("ruff", "", "pytest-fixture-autouse", status="preview"),
]


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.harvest = os.path.join(self.tmp, "harvest")
        self.state = os.path.join(self.tmp, "state")
        os.makedirs(self.harvest)
        os.makedirs(self.state)
        with open(os.path.join(self.harvest, "items.jsonl"), "w", encoding="utf-8") as handle:
            for i in FIXTURE_ITEMS:
                handle.write(json.dumps(i) + "\n")
        self.topics = self.write("topics.json", TOPICS)
        self.universal = self.write("universal.json", UNIVERSAL)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, relative, obj, raw=None):
        path = os.path.join(self.tmp, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(raw if raw is not None else json.dumps(obj))
        return path

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = pc.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def read(self, path):
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)


class MergeAndDrop(unittest.TestCase):
    def setUp(self):
        self.kept, self.absorbed, self.dropped = pc.prepare_items([dict(i) for i in FIXTURE_ITEMS])
        self.by_key = {(i["source"], pc.item_id(i)): i for i in self.kept}

    def test_ruff_pylint_reimplementation_absorbs_the_pylint_item(self):
        host = self.by_key[("ruff", "PLW0102")]
        self.assertEqual([(a["source"], a["code"]) for a in host["also"]], [("pylint", "W0102")])
        self.assertNotIn(("pylint", "W0102"), self.by_key)

    def test_ruff_bugbear_code_absorbs_the_bugbear_item(self):
        self.assertEqual([(a["source"], a["code"]) for a in self.by_key[("ruff", "B006")]["also"]], [("bugbear", "B006")])
        self.assertNotIn(("bugbear", "B006"), self.by_key)

    def test_ruff_bandit_code_absorbs_the_bandit_item_with_the_same_digits(self):
        host = self.by_key[("ruff", "S602")]
        self.assertEqual(host["also"][0]["code"], "B602")
        self.assertEqual(set(host["also"][0]), set(pc.LOCATOR_FIELDS))
        self.assertNotIn(("bandit", "B602"), self.by_key)

    def test_absorbed_items_map_to_their_hosts(self):
        self.assertEqual(self.absorbed, {("pylint", "W0102"): ("ruff", "PLW0102"), ("bugbear", "B006"): ("ruff", "B006"),
                                         ("bandit", "B602"): ("ruff", "S602")})

    def test_drop_reasons_are_counted(self):
        self.assertEqual(dict(self.dropped), {"pylint type E": 1, "pylint type F": 1, "pylint C01xx": 1,
                                              "pylint C03xx": 1, "status removed": 1})

    def test_other_pylint_conventions_and_preview_items_stay(self):
        self.assertIn(("pylint", "C0200"), self.by_key)
        self.assertIn(("ruff", "pytest-fixture-autouse"), self.by_key)

    def test_order_is_source_then_code_prefix_then_number(self):
        order = [(i["source"], pc.item_id(i)) for i in self.kept]
        self.assertEqual(order, [("ruff", "B006"), ("ruff", "BLE001"), ("ruff", "PLW0102"), ("ruff", "S602"),
                                 ("ruff", "pytest-fixture-autouse"), ("pylint", "C0200"), ("sonar", "S5717")])

    def test_input_items_are_not_mutated(self):
        originals = [dict(i) for i in FIXTURE_ITEMS]
        pc.prepare_items(originals)
        self.assertTrue(all("also" not in i for i in originals))


class BatchesAndBrief(unittest.TestCase):
    def test_batches_are_cut_by_size_with_two_digit_ids(self):
        batches = pc.cut_batches(list(range(5)), 2)
        self.assertEqual([(b, len(items)) for b, items in batches], [("batch-01", 2), ("batch-02", 2), ("batch-03", 1)])

    def test_a_batch_size_below_one_is_refused(self):
        with self.assertRaises(pc.CorpusError):
            pc.cut_batches([1], 0)

    def test_explanation_is_whitespace_collapsed_and_cut_at_a_word(self):
        self.assertEqual(pc.collapse_head("alpha  beta\n\ngamma delta", 13), "alpha beta …")
        self.assertEqual(pc.collapse_head("alpha beta", 50), "alpha beta")

    def test_verdict_definitions_come_from_the_triage_workflow(self):
        lines = pc.verdict_definitions()
        self.assertEqual([line.split(" — ")[0][2:] for line in lines[:7]], list(pc.VERDICTS))

    def test_brief_sections_follow_the_fixed_order(self):
        kept, _, _ = pc.prepare_items([dict(i) for i in FIXTURE_ITEMS])
        context = pc.BriefContext(TOPICS, UNIVERSAL, pc.verdict_definitions(), 30, "/h")
        brief = pc.render_brief("batch-01", kept, context)
        marks = ["## Criteria of a corpus card", "## Verdicts", "- python-specific-new — ", "## Topics",
                 "## Universal cards", "### code", "- CODE-01 · A name never promises a type", "### errors",
                 "## Items", "### ruff B006 mutable-argument-default"]
        positions = [brief.index(m) for m in marks]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("also: bugbear B006 https://example.org/bugbear/B006 /h/src/bugbear/B006", brief)
        self.assertIn("explanation: Function defaults are …\n", brief)
        self.assertIn("### ruff pytest-fixture-autouse\n", brief)


class TriageBriefsCommand(Fixture):
    def test_writes_briefs_batches_and_args_with_the_done_list(self):
        self.write("state/triage/batch-01.json", {"verdicts": [], "batch_note": ""})
        self.write("state/triage/batch-02.json", None, raw="{ cut off")
        code, out, _ = self.run_cli("triage-briefs", "--harvest", self.harvest, "--state", self.state, "--topics", self.topics,
                                    "--universal", self.universal, "--batch-size", "3")
        self.assertEqual(code, 0)
        batches = self.read(os.path.join(self.state, "triage", "batches.json"))
        self.assertEqual([b["id"] for b in batches], ["batch-01", "batch-02", "batch-03"])
        self.assertEqual([b["item_count"] for b in batches], [3, 3, 1])
        self.assertTrue(all(os.path.isabs(b["brief_path"]) and os.path.isfile(b["brief_path"]) for b in batches))
        self.assertEqual(batches[0]["codes"], ["ruff B006", "ruff BLE001", "ruff PLW0102"])
        args = self.read(os.path.join(self.state, "triage", "args.json"))
        self.assertEqual(args["state_dir"], self.state)
        self.assertEqual(args["done"], ["batch-01"])
        self.assertEqual(set(args["batches"][0]), {"id", "brief_path", "item_count"})
        self.assertIn("7 item(s) kept, 3 merged, 5 dropped", out)

    def test_a_brief_of_an_earlier_cut_is_removed(self):
        stale = self.write("state/triage/briefs/batch-09.md", None, raw="old")
        self.run_cli("triage-briefs", "--harvest", self.harvest, "--state", self.state, "--topics", self.topics,
                     "--universal", self.universal)
        self.assertFalse(os.path.exists(stale))

    def test_missing_items_file_is_one_line_and_a_failure(self):
        os.remove(os.path.join(self.harvest, "items.jsonl"))
        code, _, err = self.run_cli("triage-briefs", "--harvest", self.harvest, "--state", self.state, "--topics", self.topics,
                                    "--universal", self.universal)
        self.assertEqual(code, 1)
        self.assertEqual(len(err.strip().splitlines()), 1)
        self.assertIn("items.jsonl not found", err)


def verdict(code, source, kind, *new_rule, **fields):
    """One triage verdict; new_rule is (topic, rule_key, statement) of a python-specific-new verdict."""
    topic, rule_key, statement = new_rule or ("", "", "")
    base = {"code": code, "source": source, "verdict": kind, "universal_id": "", "duplicate_of": "",
            "topic": topic, "rule_key": rule_key, "statement": statement, "note": "n"}
    return base | fields


class TriageMergeCommand(Fixture):
    def setUp(self):
        super().setUp()
        self.run_cli("triage-briefs", "--harvest", self.harvest, "--state", self.state, "--topics", self.topics,
                     "--universal", self.universal, "--batch-size", "3")
        self.write("state/triage/batch-01.json", {"batch_note": "B006 text short", "verdicts": [
            verdict("B006", "ruff", "python-specific-new", "python-data-model-and-idioms", "mutable-default-argument",
                    "A mutable default is shared.", note="first"),
            verdict("BLE001", "ruff", "universal-instance", universal_id="ERR-08", note="blind catch"),
            verdict("PLW0102", "ruff", "duplicate-of", duplicate_of="B006"),
        ]})
        self.write("state/triage/batch-02.json", {"batch_note": "", "verdicts": [
            verdict("S5717", "sonar", "python-specific-new", "python-data-model-and-idioms", "mutable-default-argument",
                    "Second statement.", note="second"),
            verdict("C0200", "pylint", "python-specific-new", "no-such-topic", "use-enumerate", "Use enumerate."),
            verdict("S602", "ruff", "out-of-scope", note="security design"),
        ]})

    def merge(self):
        code, out, _ = self.run_cli("triage-merge", "--state", self.state, "--harvest", self.harvest, "--topics", self.topics)
        self.assertEqual(code, 0)
        return (self.read(os.path.join(self.state, "candidates.json")),
                self.read(os.path.join(self.state, "triage", "summary.json")), out)

    def test_one_rule_key_in_two_batches_is_one_candidate_with_every_item(self):
        candidates, _, _ = self.merge()
        mutable = next(c for c in candidates if c["key"] == "mutable-default-argument")
        self.assertEqual(mutable["topic"], "python-data-model-and-idioms")
        self.assertEqual(mutable["statement"], "A mutable default is shared.")
        self.assertEqual(mutable["notes"], "first | second")
        self.assertEqual([(i["source"], i["code"]) for i in mutable["items"]],
                         [("ruff", "B006"), ("bugbear", "B006"), ("sonar", "S5717"), ("ruff", "PLW0102"), ("pylint", "W0102")])
        self.assertEqual(mutable["codes"], ["B006", "B006", "S5717", "PLW0102", "W0102"])
        self.assertTrue(os.path.isabs(mutable["items"][0]["cache_path"]))
        self.assertEqual(mutable["items"][0]["summary"], "ruff B006 summary")

    def test_an_unknown_topic_goes_to_unassigned(self):
        candidates, summary, _ = self.merge()
        self.assertEqual([(c["key"], c["topic"]) for c in candidates][-1], ("use-enumerate", "unassigned"))
        self.assertEqual(summary["unassigned"], 1)

    def test_summary_lists_universal_instances_and_the_other_verdict_kinds(self):
        _, summary, out = self.merge()
        self.assertEqual(summary["universal_instances"],
                         [{"code": "BLE001", "source": "ruff", "name": "blind-except", "universal_id": "ERR-08", "note": "blind catch"}])
        self.assertEqual(summary["verdicts"], {"python-specific-new": 3, "universal-instance": 1, "duplicate-of": 1, "out-of-scope": 1})
        self.assertEqual(summary["out_of_scope"][0]["code"], "S602")
        self.assertEqual(summary["duplicates"][0]["duplicate_of"], "B006")
        self.assertEqual(summary["batch_notes"], [{"batch": "batch-01", "note": "B006 text short"}])
        self.assertEqual(summary["missing_batches"], ["batch-03"])
        self.assertIn("python-specific-new 3", out)

    def test_items_without_a_verdict_are_listed(self):
        _, summary, _ = self.merge()
        self.assertEqual(summary["unjudged_items"], [{"batch": "batch-02", "item": "ruff pytest-fixture-autouse"}])

    def test_a_rule_key_in_two_topics_takes_a_suffix_in_the_later_topic(self):
        self.write("state/triage/batch-03.json", {"batch_note": "", "verdicts": [
            verdict("BLE001", "ruff", "python-specific-new", "python-exceptions-and-context-managers", "mutable-default-argument", "x")]})
        candidates, _, _ = self.merge()
        keys = [(c["key"], c["topic"]) for c in candidates]
        self.assertIn(("mutable-default-argument", "python-data-model-and-idioms"), keys)
        self.assertIn(("mutable-default-argument-python-exceptions-and-context-managers", "python-exceptions-and-context-managers"), keys)


class TopicArgsCommand(Fixture):
    def setUp(self):
        super().setUp()
        self.write("state/candidates.json", [
            {"key": "mutable-default-argument", "topic": "python-data-model-and-idioms", "statement": "s", "items": [], "notes": "", "codes": []},
            {"key": "bare-except", "topic": "python-exceptions-and-context-managers", "statement": "s", "items": [], "notes": "", "codes": []},
        ])
        self.papers = self.write("papers.json", {"papers": [
            {"id": "arXiv:1", "title": "a", "topics": ["python-data-model-and-idioms"], "relayed": "r", "url": "u"},
            {"id": "arXiv:2", "title": "b", "topics": ["python-typing"], "relayed": "r", "url": "u"}]})
        self.cards = os.path.join(self.tmp, "cards")
        os.makedirs(self.cards)
        for name in ("py-01--a.md", "py-03--c.md", "err-07--universal.md"):
            self.write(f"cards/{name}", None, raw="")
        slug_dir = "state/python-data-model-and-idioms"
        self.write(f"{slug_dir}/spine/spine.json", {"spine": {"summary": "s", "rules": [], "dropped": []}})
        self.write(f"{slug_dir}/draft/mutable-default-argument.json", {"key": "mutable-default-argument", "status": "card"})
        self.write(f"{slug_dir}/draft/broken.json", None, raw='{"key": ')
        self.write(f"{slug_dir}/verdict/mutable-default-argument.json", {"key": "mutable-default-argument", "verdict": "accept"})

    def topic_args(self, *extra):
        code, out, err = self.run_cli("topic-args", "--state", self.state, "--topic", "python-data-model-and-idioms",
                                      "--topics", self.topics, "--universal", self.universal, "--harvest", self.harvest,
                                      "--skill", SCRIPTS, "--root", self.tmp, "--cards-dir", self.cards, "--papers", self.papers, *extra)
        self.assertEqual(code, 0)
        return self.read(os.path.join(self.state, "python-data-model-and-idioms", "args.json")), out, err

    def test_args_carry_the_topic_its_candidates_domain_titles_and_papers(self):
        args, _, _ = self.topic_args()
        self.assertEqual(args["topic"]["prefix"], "PY")
        self.assertEqual(args["topic"]["group"], "python")
        self.assertEqual(args["candidates_count"], 1)
        self.assertEqual(args["candidates_path"], os.path.join(self.state, "python-data-model-and-idioms", "candidates.json"))
        self.assertEqual([c["key"] for c in self.read(args["candidates_path"])], ["mutable-default-argument"])
        self.assertEqual(args["universal_titles"], ["CODE-01 · A name never promises a type",
                                                    "CODE-02 · A routine named as a query hides no state change"])
        self.assertEqual([p["id"] for p in args["papers"]], ["arXiv:1"])
        self.assertEqual(args["state_dir"], os.path.join(self.state, "python-data-model-and-idioms"))
        self.assertIsNone(args["only_keys"])

    def test_next_id_follows_the_highest_python_card(self):
        args, _, _ = self.topic_args()
        self.assertEqual(args["next_id"], 4)

    def test_done_is_scanned_and_an_unparseable_file_is_reported_and_skipped(self):
        args, out, err = self.topic_args()
        self.assertEqual(args["done"]["spine"]["summary"], "s")
        self.assertEqual(list(args["done"]["drafts"]), ["mutable-default-argument"])
        self.assertEqual(list(args["done"]["verdicts"]), ["mutable-default-argument"])
        self.assertEqual(args["done"]["closing"], {})
        self.assertIn("broken.json", err)
        self.assertIn("1 unparseable file(s) skipped", out)

    def test_only_keys_become_a_list(self):
        args, _, _ = self.topic_args("--only-keys", "a,b")
        self.assertEqual(args["only_keys"], ["a", "b"])

    def test_an_unknown_topic_fails_in_one_line(self):
        code, _, err = self.run_cli("topic-args", "--state", self.state, "--topic", "nope", "--topics", self.topics,
                                    "--universal", self.universal, "--harvest", self.harvest, "--skill", SCRIPTS,
                                    "--root", self.tmp, "--cards-dir", self.cards, "--papers", self.papers)
        self.assertEqual(code, 1)
        self.assertIn("topic 'nope'", err)


class SaveRunCommand(Fixture):
    def test_copies_a_run_that_holds_cards(self):
        source = self.write("out.json", {"result": {"cards": [{"rule_id": "PY-01"}, {"rule_id": "PY-02"}]}})
        code, out, _ = self.run_cli("save-run", "--state", self.state, "--topic", "t", "--from", source)
        self.assertEqual(code, 0)
        self.assertEqual(len(self.read(os.path.join(self.state, "t", "run.json"))["result"]["cards"]), 2)
        self.assertIn("2 card(s)", out)

    def test_refuses_an_output_without_cards(self):
        source = self.write("out.json", {"result": {"summary": "x"}})
        code, _, err = self.run_cli("save-run", "--state", self.state, "--topic", "t", "--from", source)
        self.assertEqual(code, 1)
        self.assertIn("result.cards", err)
        self.assertFalse(os.path.exists(os.path.join(self.state, "t", "run.json")))


if __name__ == "__main__":
    unittest.main()
