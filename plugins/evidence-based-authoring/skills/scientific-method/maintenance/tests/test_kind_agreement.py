"""kind_agreement.py: the draw of the sample, the readers' brief and the score of two readers."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
EVAL = SKILL / "evals" / "kind-agreement"
SCRIPT = EVAL / "kind_agreement.py"
METHOD = SKILL / "references" / "method.md"
PROTOCOL = EVAL / "protocol.md"
sys.path.insert(0, str(EVAL))
import kind_agreement as ka  # noqa: E402

# Candidates built per corpus: two more than the number drawn, so the draw has a choice.
PREFIXES = {"audit": "R", "craft": "CR", "craft-python": "PY", "craft-java": "JV"}


def run_script(*args):
    return subprocess.run([sys.executable, "-I", str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True, encoding="utf-8")


def card_text(rule_id, thesis=True):
    body = f"## Thesis\n\nThe thesis of {rule_id} — «один».\n\n" if thesis else ""
    return (f"---\ntitle: The title of {rule_id}\nrule_id: {rule_id}\n---\n\n# The title of {rule_id}\n\n"
            f"{body}## Rationale\nWhy {rule_id}.\n")


def build_corpora(root: Path, extra=0, short=None) -> dict[str, list[str]]:
    """Four corpora under root in the real layouts; returns the candidate ids per corpus.

    Each map also carries a non-rule line, an id without a card and an id with two cards, none of
    which is a candidate. `short` names a corpus built with one candidate fewer than it draws.
    """
    candidates = {}
    for corpus, cards_rel, map_rel, count in ka.CORPORA:
        cards = root / cards_rel
        cards.mkdir(parents=True)
        prefix = PREFIXES[corpus]
        total = count - 1 if corpus == short else count + 2 + extra
        ids = [f"{prefix}-{n:02d}" for n in range(1, total + 1)]
        for rule_id in ids:
            (cards / f"{rule_id.lower()}--a-slug.md").write_text(card_text(rule_id), encoding="utf-8")
        (cards / f"{prefix.lower()}-98--one.md").write_text(card_text(f"{prefix}-98"), encoding="utf-8")
        (cards / f"{prefix.lower()}-98--two.md").write_text(card_text(f"{prefix}-98"), encoding="utf-8")
        lines = [f"# {corpus} provenance", "", "Rule lines:"]
        lines += [f"- **{rule_id}** · source of {rule_id} · locator: «где»" for rule_id in ids]
        lines += [f"- **{prefix}-98** · two cards", f"- **{prefix}-99** · no card"]
        map_path = root / map_rel
        map_path.parent.mkdir(parents=True, exist_ok=True)
        map_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        candidates[corpus] = ids
    return candidates


def expected_draw(seed, ids, count):
    return sorted(ids, key=lambda i: hashlib.sha256(f"{seed}:{i}".encode("utf-8")).hexdigest())[:count]


def section(text, heading):
    """The section from its heading to the next `## ` line, computed independently of the script."""
    match = re.search(rf"^{re.escape(heading)}\n.*?(?=^## |\Z)", text, re.S | re.M)
    return match.group(0).strip("\n")


class TempRoot(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.root = self.dir / "repo"
        self.root.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def sample(self, seed="20261120", name="sample.json"):
        out = self.dir / name
        run = run_script("sample", "--root", self.root, "--seed", seed, "--out", out)
        self.assertEqual(run.returncode, 0, run.stderr)
        return run, json.loads(out.read_text(encoding="utf-8"))


class Sample(TempRoot):
    def test_same_seed_same_draw_another_seed_another(self):
        build_corpora(self.root, extra=6)
        run, first = self.sample()
        self.assertEqual(run.stdout, "30 rules drawn\n")
        _, again = self.sample(name="again.json")
        _, other = self.sample(seed="7", name="other.json")
        self.assertEqual(first, again)
        self.assertEqual(other["seed"], "7")
        self.assertNotEqual([r["id"] for r in first["rules"]], [r["id"] for r in other["rules"]])

    def test_draw_is_the_first_n_by_sha256_of_seed_and_id(self):
        candidates = build_corpora(self.root)
        _, sample = self.sample()
        expected = []
        for corpus, cards_rel, map_rel, count in ka.CORPORA:
            for rule_id in expected_draw("20261120", candidates[corpus], count):
                number = 3 + candidates[corpus].index(rule_id) + 1
                card = f"{cards_rel}/{rule_id.lower()}--a-slug.md"
                expected.append({"id": rule_id, "corpus": corpus, "card": card, "provenance": map_rel, "line": number})
        self.assertEqual(sample, {"seed": "20261120", "rules": expected})
        map_lines = (self.root / sample["rules"][0]["provenance"]).read_text(encoding="utf-8").splitlines()
        self.assertTrue(map_lines[sample["rules"][0]["line"] - 1].startswith(f"- **{sample['rules'][0]['id']}**"))

    def test_an_id_without_exactly_one_card_is_not_a_candidate(self):
        candidates = build_corpora(self.root)
        everything = [(c, d, m, len(candidates[c])) for c, d, m, _ in ka.CORPORA]
        drawn = {r["id"] for r in ka.draw(self.root, "s", everything)}
        self.assertEqual(drawn, {i for ids in candidates.values() for i in ids})
        self.assertFalse({"R-98", "R-99", "PY-98", "PY-99"} & drawn)
        one_more = [(c, d, m, n + 1) for c, d, m, n in everything]
        with self.assertRaises(ka.InputError):
            ka.draw(self.root, "s", one_more)

    def test_too_few_candidates_exits_2(self):
        build_corpora(self.root, short="craft-python")
        out = self.dir / "sample.json"
        run = run_script("sample", "--root", self.root, "--seed", "1", "--out", out)
        self.assertEqual(run.returncode, 2)
        self.assertIn("craft-python", run.stderr)
        self.assertFalse(out.exists())


class Brief(TempRoot):
    def brief(self, sample_path):
        out = self.dir / "brief.md"
        run = run_script("brief", "--root", self.root, "--sample", sample_path, "--method", METHOD,
                         "--protocol", PROTOCOL, "--out", out)
        return run, out

    def test_brief_holds_sections_titles_theses_and_fenced_lines(self):
        build_corpora(self.root)
        _, sample = self.sample()
        run, out = self.brief(self.dir / "sample.json")
        self.assertEqual(run.returncode, 0, run.stderr)
        text = out.read_text(encoding="utf-8")
        self.assertEqual(run.stdout, f"30 rules, {len(text.encode('utf-8'))} bytes written\n")
        self.assertTrue(text.startswith("# Kind agreement — brief\n"))
        method, protocol = METHOD.read_text(encoding="utf-8"), PROTOCOL.read_text(encoding="utf-8")
        kinds = section(method, "## Kinds of statement")
        reading = section(protocol, "## Reading rule")
        block = re.search(r"^```json\n.*?^```$", section(protocol, "## Readers"), re.S | re.M).group(0)
        answer = f"## Answer\n\n{block}\n\n{ka.ANSWER_SENTENCE}"
        positions = [text.index(part) for part in (kinds, reading, answer, "\n## Rules\n")]
        self.assertEqual(positions, sorted(positions))
        for rule in sample["rules"]:
            rule_id = rule["id"]
            map_line = (self.root / rule["provenance"]).read_text(encoding="utf-8").splitlines()[rule["line"] - 1]
            entry = (f"### {rule_id}\n\nTitle: The title of {rule_id}\n\nThe thesis of {rule_id} — «один».\n\n"
                     f"~~~~\n{map_line}\n~~~~")
            with self.subTest(rule_id):
                self.assertIn(entry, text)
        ids = re.findall(r"^### (\S+)$", text, re.M)
        self.assertEqual(ids, [r["id"] for r in sample["rules"]])

    def test_a_card_without_thesis_exits_2(self):
        build_corpora(self.root)
        _, sample = self.sample()
        card = self.root / sample["rules"][3]["card"]
        card.write_text(card_text(sample["rules"][3]["id"], thesis=False), encoding="utf-8")
        run, out = self.brief(self.dir / "sample.json")
        self.assertEqual(run.returncode, 2)
        self.assertIn("Thesis", run.stderr)
        self.assertFalse(out.exists())

    def test_a_missing_card_or_line_exits_2(self):
        build_corpora(self.root)
        _, sample = self.sample()
        cases = {"card": dict(sample["rules"][0], card="no/such--card.md"),
                 "line": dict(sample["rules"][0], line=sample["rules"][0]["line"] + 1)}
        for name, rule in cases.items():
            with self.subTest(name):
                path = self.dir / f"{name}.json"
                path.write_text(json.dumps({"seed": "x", "rules": [rule]}), encoding="utf-8")
                run, _ = self.brief(path)
                self.assertEqual(run.returncode, 2)
                self.assertTrue(run.stderr)


IDS = [f"R-{n:02d}" for n in range(1, 31)]


class Score(TempRoot):
    def write(self, name, obj):
        path = self.dir / name
        path.write_text(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False), encoding="utf-8")
        return path

    def score(self, a_kinds, b_kinds, ids=IDS, *extra):
        sample = self.write("sample.json", {"seed": "s", "rules": [{"id": i} for i in ids]})
        a = self.write("a.json", answers(ids, a_kinds) if isinstance(a_kinds, list) else a_kinds)
        b = self.write("b.json", answers(ids, b_kinds) if isinstance(b_kinds, list) else b_kinds)
        return run_script("score", "--sample", sample, "--a", a, "--b", b, *extra)

    def test_identical_answers_hold(self):
        kinds = [ka.KINDS[n % 4] for n in range(30)]
        run = self.score(kinds, kinds)
        self.assertEqual(run.returncode, 0, run.stderr)
        lines = run.stdout.splitlines()
        self.assertEqual(lines[-4:], ["agreed: 30 of 30", "kappa: 1.00", "threshold: 24", "holds"])
        self.assertEqual(len(lines), 9)
        self.assertEqual(lines[1].split(), ["decision", "8", "0", "0", "0"])

    def test_one_kind_for_every_rule_has_kappa_1(self):
        run = self.score(["norm"] * 30, ["norm"] * 30)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("kappa: 1.00", run.stdout.splitlines())

    def test_hand_computed_kappa(self):
        # Ten rules. Reader a: decision on R-01..R-06, norm on R-07..R-10. Reader b agrees except on
        # R-06, where it says norm. agreed k = 9, po = 9/10 = 0.9. Counts: a decision 6, norm 4;
        # b decision 5, norm 5. pe = 0.6*0.5 + 0.4*0.5 = 0.5. kappa = (0.9 - 0.5) / (1 - 0.5) = 0.80.
        ids = IDS[:10]
        a = ["decision"] * 6 + ["norm"] * 4
        b = ["decision"] * 5 + ["norm"] * 5
        run = self.score(a, b, ids, "--threshold", "9")
        self.assertEqual(run.returncode, 0, run.stderr)
        lines = run.stdout.splitlines()
        self.assertEqual(lines[0], "R-06: a=decision b=norm")
        self.assertEqual([line.split() for line in lines[1:6]],
                         [["a", "\\", "b", *ka.KINDS], ["decision", "5", "0", "1", "0"],
                          ["definition", "0", "0", "0", "0"], ["norm", "0", "0", "4", "0"],
                          ["claim", "0", "0", "0", "0"]])
        self.assertEqual(lines[6:], ["agreed: 9 of 10", "kappa: 0.80", "threshold: 9", "holds"])

    def test_below_threshold_is_refuted(self):
        a = ["claim"] * 30
        b = ["claim"] * 23 + ["norm"] * 7
        run = self.score(a, b)
        self.assertEqual(run.returncode, 1, run.stderr)
        lines = run.stdout.splitlines()
        self.assertEqual(lines[:7], [f"{i}: a=claim b=norm" for i in IDS[23:]])
        self.assertEqual(lines[-4], "agreed: 23 of 30")
        self.assertEqual(lines[-1], "refuted")

    def test_invalid_input_exits_2(self):
        good = answers(IDS, ["claim"] * 30)
        missing = {"answers": good["answers"][1:]}
        twice = {"answers": good["answers"] + [good["answers"][0]]}
        outside = {"answers": good["answers"] + [{"id": "R-99", "kind": "claim", "why": "w"}]}
        bad_kind = answers(IDS, ["claim"] * 29 + ["opinion"])
        cases = {"malformed JSON": "{not json", "answers not a list": {"answers": "claim"}, "an id absent": missing,
                 "an id given twice": twice, "an id outside the sample": outside, "a kind outside the four": bad_kind}
        for name, obj in cases.items():
            with self.subTest(name):
                run = self.score(good, obj)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(run.stdout, "")
                self.assertTrue(run.stderr)
        sample = self.write("sample.json", {"seed": "s", "rules": [{"id": i} for i in IDS]})
        run = run_script("score", "--sample", sample, "--a", self.dir / "absent.json", "--b", self.write("b.json", good))
        self.assertEqual((run.returncode, run.stdout), (2, ""))
        self.assertIn("absent.json", run.stderr)


def answers(ids, kinds):
    return {"answers": [{"id": i, "kind": k, "why": f"the ground of {i}"} for i, k in zip(ids, kinds)]}


class Wrap(unittest.TestCase):
    def test_long_lines_break_at_a_space_and_keep_every_word(self):
        text = "short\n" + " ".join(["word"] * 400) + "\nlast"
        wrapped = ka.wrap_lines(text, 100)
        self.assertLessEqual(max(len(line) for line in wrapped.split("\n")), 100)
        self.assertEqual(wrapped.split(), text.split())

    def test_a_line_without_a_space_stays_whole(self):
        self.assertEqual(ka.wrap_lines("a" * 50, 10), "a" * 50)


class WithoutRecord(unittest.TestCase):
    def test_the_record_is_cut_from_a_rule_line(self):
        line = "- **R-1** · a source · notes · kind: decision · owner: the owner · goal: a goal"
        self.assertEqual(ka.without_record(line), "- **R-1** · a source · notes")

    def test_a_line_without_a_record_is_unchanged(self):
        line = "- **R-1** · a source · a kind: of thing in the free text"
        self.assertEqual(ka.without_record(line), line)


if __name__ == "__main__":
    unittest.main()
