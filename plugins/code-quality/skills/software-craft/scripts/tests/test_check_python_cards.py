#!/usr/bin/env python3
"""Unit tests for check-python-cards.py: each of the seven checks on a fixture harvest and
draft files — the source and fragment checks on the provenance line's citations, their quotes
and their statuses — the citation split, the elision replacement, the relayed and --no-network
exemptions, the fetch retry and cache, the pending and spine skips, the markdown fallback and
the command line.
Offline: the fetch opener is a fake and no socket opens.

Run:  python3 -m unittest scripts/tests/test_check_python_cards.py   (from the skill directory)
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
SKILL = os.path.dirname(SCRIPTS)
spec = importlib.util.spec_from_file_location("check_python_cards", os.path.join(SCRIPTS, "check-python-cards.py"))
cpc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cpc)

RUFF_EXPLANATION = ("## What it does\nChecks for uses of mutable objects as function argument defaults.\n\n"
                    "## Why is this bad?\nFunction defaults are evaluated once, when the function is defined.\n\n"
                    "The same mutable object is then shared across all calls to the function.")
PYLINT_DETAILS = "Default argument values are evaluated *once*, when the ``def`` statement runs.\n"
SONAR_HTML = ("<p>In Python, function parameters can have default values.</p>\n<p>These default values are expressions "
              "which are evalutated when the function is defined, i.e. only once.</p>")
PEP_PAGE = "<html><body><p>Default values are computed once.</p></body></html>"
TITLE = "A mutable default argument is replaced by None and a fresh object created in the body"
BAD = ["bad:  def append_to(item, bucket=[]):", "          bucket.append(item)", "          return bucket"]
GOOD = ["good: def append_to(item, bucket=None):", "          if bucket is None:", "              ...",
        "          return bucket"]
CITATIONS = ("Ruff B006 mutable-argument-default (astral-sh/ruff mutable_argument_default.rs), fetched — "
             "'Function defaults are evaluated once, when the function is defined.'; "
             "Pylint dangerous-default-value (W0102), fetched — \"Default argument values are evaluated once\"; "
             "SonarSource python S5717 — 'These default values are expressions which are evalutated when the function is defined' (fetched); "
             "PEP 8 §Programming Recommendations (https://peps.python.org/pep-0008/), fetched — \"Default values are computed once.\"")


def provenance(citations, rule_id="PY-01"):
    """A provenance line in the map's shape around the given citations."""
    return (f"- **{rule_id}** · {citations}"
            " · topic: python-data-model-and-idioms (research/software-craft-python/python-data-model-and-idioms.md)"
            " · formulation: none · reception: not contested · notes: confidence high")


PROVENANCE = provenance(CITATIONS)


DEFAULT_TRIGGERS = "['def\\s+\\w+\\([^)]*=\\s*(\\[\\]|\\{\\})']"


def card(**overrides):
    """A card in the corpus schema; overrides replace title, triggers, good or rule_id, and `tail`
    is appended after the last block."""
    title = overrides.get("title", TITLE)
    triggers = overrides.get("triggers", DEFAULT_TRIGGERS)
    rule_id = overrides.get("rule_id", "PY-01")
    example = "\n".join(BAD) + "\n" + "\n".join(overrides.get("good", GOOD))
    return f"""---
title: {title}
rule_id: {rule_id}
domain: code
step: [design, implement]
applies_to: [python]
triggers: {triggers}
scope: hunk
check_kind: mechanical
severity_default: major
---

# {title}

## Thesis
A Python default argument value is evaluated once, when the def statement runs, so a list or dict default is shared by every call.

## Rationale
Every call that mutates the shared default changes what later calls receive.

## Example
```python
{example}
```

## Limits
A default that no call mutates is harmless.

## Validator
Grep the hunk for a def whose default is a list or dict literal. Validator question: **does a def in the hunk take a mutable literal as a default?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: {rule_id}`, severity major, `file`, `symbol`, `code` = the def line, `fix` = the None default, `rationale` = the shared default).
{overrides.get("tail", "")}"""


def draft(**overrides):
    """A draft object as the topic workflow writes it; overrides replace any of its fields."""
    base = {"key": "mutable-default", "status": "card", "filename": "py-01--mutable-default-argument.md",
            "card_markdown": card(), "provenance_line": PROVENANCE, "pending_entry": "", "checks": "", "notes": ""}
    return base | overrides


class FakeOpener:
    """Answers from a URL table; records every call."""

    def __init__(self, pages=None, statuses=None):
        self.pages = pages or {}
        self.statuses = statuses or {}
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        answers = self.statuses.get(url)
        if answers:
            answer = answers.pop(0)
            if isinstance(answer, Exception):
                raise answer
            return answer, b""
        if url in self.pages:
            return 200, self.pages[url].encode("utf-8")
        return 404, b""


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.harvest = os.path.join(self.tmp, "harvest")
        self.state = os.path.join(self.tmp, "topic", "draft")
        os.makedirs(self.state)
        self.put("harvest/src/ruff/rules.json", json.dumps([{"code": "B006", "name": "mutable-argument-default",
                                                              "summary": "Checks for mutable defaults.", "explanation": RUFF_EXPLANATION}]))
        self.put("harvest/src/pylint/dangerous-default-value/details.rst", PYLINT_DETAILS)
        self.put("harvest/src/pylint/dangerous-default-value/bad.py", "def f(x=[]):\n    pass\n")
        self.put("harvest/src/pylint/dangerous-default-value/good.py", "def f(x=None):\n    pass\n")
        self.put("harvest/src/sonar/S5717.html", SONAR_HTML)
        items = [
            {"source": "ruff", "code": "B006", "name": "mutable-argument-default", "title": "t", "summary": "s",
             "explanation": RUFF_EXPLANATION, "url": "u", "default_on": True, "category": "c", "status": "stable",
             "cache_path": "src/ruff/rules.json"},
            {"source": "pylint", "code": "W0102", "name": "dangerous-default-value", "title": "t", "summary": "s",
             "explanation": PYLINT_DETAILS, "url": "u", "default_on": True, "category": "W", "status": "stable",
             "cache_path": "src/pylint/dangerous-default-value"},
            {"source": "sonar", "code": "S5717", "name": "default-mutation", "title": "t", "summary": "s",
             "explanation": "e", "url": "u", "default_on": True, "category": "c", "status": "stable",
             "cache_path": "src/sonar/S5717.html"},
        ]
        self.put("harvest/items.jsonl", "".join(json.dumps(i) + "\n" for i in items))
        self.universal = os.path.join(self.tmp, "universal.json")
        self.put("universal.json", json.dumps([{"rule_id": "CODE-09", "title": "A routine does one thing", "domain": "code"}]))
        self.opener = FakeOpener({"https://peps.python.org/pep-0008/": PEP_PAGE})

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def put(self, relative, text):
        path = os.path.join(self.tmp, relative)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
        return path

    def save(self, obj, name=None):
        return self.put(os.path.join("topic", "draft", f"{name or obj['key']}.json"), json.dumps(obj))

    def check(self, keys=None, network=True, universal=True):
        fetcher = cpc.Fetcher(os.path.join(self.tmp, "topic", "check-cache"), network=network, opener=self.opener)
        titles = cpc.load_universal_titles(self.universal) if universal else None
        context = cpc.CheckContext(cpc.Harvest(self.harvest), fetcher, titles, SKILL)
        results, checked, skipped = cpc.check_all(self.state, context, keys)
        return results, checked, skipped

    def failures(self, key="mutable-default", **kwargs):
        results, _, _ = self.check(**kwargs)
        return results[key].failures


class Checks(Fixture):
    def test_a_valid_card_passes_every_check(self):
        self.save(draft())
        results, checked, skipped = self.check()
        self.assertEqual(results["mutable-default"].failures, [])
        self.assertEqual((checked, skipped), (1, 0))
        self.assertEqual(self.opener.calls, ["https://peps.python.org/pep-0008/"])

    def test_a_good_half_that_does_not_parse_fails(self):
        good = ["good: def append_to(item, bucket=None)", "          return bucket"]
        self.save(draft(card_markdown=card(good=good)))
        failures = self.failures()
        self.assertEqual(len(failures), 1)
        self.assertTrue(failures[0].startswith("example: the good half does not parse: "), failures[0])
        self.assertIn("line 1", failures[0])

    def test_a_trigger_that_matches_no_bad_line_fails(self):
        self.save(draft(card_markdown=card(triggers="['lambda\\s*:']")))
        self.assertEqual(self.failures(), ["triggers: no trigger matches a line of the bad half"])

    def test_signal_only_triggers_pass_with_a_note(self):
        self.save(draft(card_markdown=card(triggers="['signal:many_parameters']")))
        results, _, _ = self.check()
        self.assertEqual(results["mutable-default"].failures, [])
        self.assertIn("triggers: signal triggers only; nothing to match", results["mutable-default"].notes)

    def test_an_unknown_ruff_code_fails(self):
        self.save(draft(provenance_line=PROVENANCE.replace("Ruff B006", "Ruff B999")))
        failures = self.failures()
        self.assertEqual(failures, ["source: no ruff entry B999 in the harvest: "
                                    "Ruff B999 mutable-argument-default (astral-sh/ruff mutable_…"])

    def test_a_fragment_absent_from_its_citations_text_fails(self):
        citations = "Ruff B006 mutable-argument-default, fetched — 'Defaults are re-created on each call of the function'"
        self.save(draft(provenance_line=provenance(citations)))
        self.assertEqual(self.failures(), ["fragment: Ruff B006 mutable-argument-default: not found: "
                                           "Defaults are re-created on each call of the function"])

    def test_a_fragment_is_checked_against_its_own_citation_alone(self):
        citations = ("Ruff B006 mutable-argument-default, fetched — \"Default argument values are evaluated once\"; "
                     "Pylint dangerous-default-value (W0102), fetched — \"Default argument values are evaluated once\"")
        self.save(draft(provenance_line=provenance(citations)))
        self.assertEqual(self.failures(), ["fragment: Ruff B006 mutable-argument-default: not found: "
                                           "Default argument values are evaluated once"])

    def test_a_fragment_found_with_markup_and_elision_passes(self):
        citations = ("Pylint dangerous-default-value (W0102), fetched — \"evaluated `once`, when the def statement runs\"; "
                     "Ruff B006 mutable-argument-default — 'Function defaults are evaluated once ... shared across all calls' (fetched)")
        self.save(draft(provenance_line=provenance(citations)))
        self.assertEqual(self.failures(), [])

    def test_a_source_block_in_the_card_fails_the_validator(self):
        tail = "\n## Source\n- Ruff B006 mutable-argument-default (astral-sh/ruff x.rs)\n"
        self.save(draft(card_markdown=card(tail=tail)))
        self.assertEqual(self.failures(), ["validator: a `## Source` block is present; a card carries no citation — "
                                           "its sources live on its provenance line, keyed by rule_id"])

    def test_a_title_equal_to_a_universal_title_fails(self):
        self.save(draft(card_markdown=card(title="A routine does one thing")))
        self.assertIn("title: the title equals the title of universal card CODE-09", self.failures())

    def test_a_relayed_citation_is_exempt_from_the_fetch_and_the_fragment_check(self):
        citations = (CITATIONS.split("; ")[0] + "; arXiv:2301.12633, abstract, **relayed** — "
                     "\"a statement no fetched text holds anywhere at all\"")
        self.save(draft(provenance_line=provenance(citations)))
        results, _, _ = self.check()
        notes = results["mutable-default"].notes
        self.assertEqual(results["mutable-default"].failures, [])
        self.assertIn("source: relayed, not fetched: arXiv:2301.12633, abstract", notes)
        self.assertIn("fragment: relayed, not checked: a statement no fetched text holds anywhere at all", notes)
        self.assertEqual(self.opener.calls, [])

    def test_a_status_after_a_quote_belongs_to_that_quote_alone(self):
        citations = ("arXiv:2301.12633 — 'a statement no fetched text holds anywhere at all' (relayed); "
                     "Ruff B006 mutable-argument-default — 'Defaults are re-created on each call of the function' (fetched)")
        self.save(draft(provenance_line=provenance(citations)))
        self.assertEqual(self.failures(), ["fragment: Ruff B006 mutable-argument-default: not found: "
                                           "Defaults are re-created on each call of the function"])
        self.assertEqual(self.opener.calls, [])

    def test_quote_statuses_read_the_leading_and_the_trailing_form(self):
        citations = ("A, fetched — \"one quote of the first citation\", \"two quote of the first citation\"; "
                     "B, **relayed** — \"three quote of the second citation\"; "
                     "C — 'four quote of the third citation in single quotes' (fetched)")
        self.assertEqual([(f.split()[0], s) for f, _start, s in cpc.quote_statuses(citations)],
                         [("one", "fetched"), ("two", "fetched"), ("three", "relayed"), ("four", "fetched")])

    def test_citations_split_at_semicolons_outside_quotes_and_after_no_initial(self):
        line = provenance("Soto, J.; McCall, J., SE-0117 (https://example.org/se-0117), fetched — \"one; two\"; "
                          "Ruff B006 mutable-argument-default")
        self.assertEqual(cpc.citations_of(line), ["Soto, J.; McCall, J., SE-0117 (https://example.org/se-0117), fetched — \"one; two\"",
                                                  "Ruff B006 mutable-argument-default"])

    def test_a_semicolon_inside_parentheses_or_before_a_bare_quote_splits_no_citation(self):
        line = provenance("Ruff B006 mutable-argument-default (astral-sh/ruff a.rs; b.rs), fetched — \"one\"; \"two\" (fetched); "
                          "Pylint dangerous-default-value (W0102)")
        self.assertEqual(cpc.citations_of(line), ["Ruff B006 mutable-argument-default (astral-sh/ruff a.rs; b.rs), fetched — "
                                                  "\"one\"; \"two\" (fetched)", "Pylint dangerous-default-value (W0102)"])

    def test_no_network_skips_pep_and_url_fetches_with_a_note(self):
        citations = (CITATIONS + "; CPython Doc/reference/compound_stmts.rst §Function definitions "
                     "(https://docs.python.org/3/reference/compound_stmts.html), fetched — \"evaluated from left to right\"")
        self.save(draft(provenance_line=provenance(citations)))
        results, _, _ = self.check(network=False)
        notes = results["mutable-default"].notes
        self.assertEqual(results["mutable-default"].failures, [])
        self.assertEqual(len([n for n in notes if n.startswith("source: --no-network, not fetched")]), 2, notes)
        self.assertEqual(len([n for n in notes if n.startswith("fragment: not checked, no text")]), 2, notes)
        self.assertEqual(self.opener.calls, [])

    def test_a_github_locator_is_fetched_from_main_then_master(self):
        url = "https://raw.githubusercontent.com/python/cpython/master/Doc/tutorial/controlflow.rst"
        self.opener.pages[url] = "The default value is evaluated only once."
        citations = ("CPython Doc/tutorial/controlflow.rst §Default Argument Values (python/cpython Doc/tutorial/controlflow.rst), "
                     "fetched — \"The default value is evaluated only once.\"")
        self.save(draft(provenance_line=provenance(citations)))
        self.assertEqual(self.failures(), [])
        self.assertEqual(self.opener.calls, [url.replace("/master/", "/main/"), url])

    def test_a_page_that_answers_404_fails_the_source_check(self):
        self.save(draft(provenance_line=provenance("PEP 9999 §Nothing (python/peps peps/pep-9999.rst), fetched — \"anything\"")))
        failures = self.failures()
        self.assertEqual(len(failures), 1, failures)
        self.assertTrue(failures[0].startswith("source: https://peps.python.org/pep-9999/ answered HTTP 404"), failures[0])

    def test_an_unrecognised_citation_fails(self):
        self.save(draft(provenance_line=provenance(CITATIONS + "; a book I once read, fetched — \"a line of that book\"")))
        self.assertIn("source: locator not recognised: a book I once read", self.failures())

    def test_a_card_draft_without_a_provenance_line_fails(self):
        self.save(draft(provenance_line=""))
        self.assertEqual(self.failures(), ["provenance: the draft carries no provenance line"])

    def test_a_provenance_line_without_its_rule_id_and_topic_fails(self):
        self.save(draft(provenance_line="- **PY-02** · Ruff B006"))
        failures = self.failures()
        self.assertIn("provenance: does not begin with '- **PY-01** · '", failures)
        self.assertIn("provenance: holds no ' · topic: '", failures)

    def test_a_validator_error_goes_to_the_card_it_names(self):
        broken = card().replace("`rule_id: PY-01`", "`rule_id: PY-0`")
        self.save(draft(card_markdown=broken))
        other = card(title="A second mutable default card title", rule_id="PY-02")
        self.save(draft(key="second", card_markdown=other, filename="py-02--second.md",
                        provenance_line=PROVENANCE.replace("PY-01", "PY-02")))
        results, checked, _ = self.check()
        self.assertEqual(checked, 2)
        self.assertEqual(results["mutable-default"].failures, ["validator: Finding output does not name `rule_id: PY-01`"])
        self.assertEqual(results["second"].failures, [])


class Skips(Fixture):
    def test_a_pending_draft_is_skipped_with_a_note(self):
        self.save(draft(status="pending", card_markdown=""))
        results, checked, skipped = self.check()
        self.assertEqual((checked, skipped), (0, 1))
        self.assertEqual(results["mutable-default"].notes, ["input: status pending; skipped"])

    def test_a_spine_file_is_passed_over(self):
        self.put("topic/draft/spine.json", json.dumps({"spine": {"rules": []}}))
        self.save(draft())
        results, checked, _ = self.check()
        self.assertNotIn("spine", results)
        self.assertEqual(checked, 1)

    def test_a_markdown_draft_without_json_is_read_with_a_note(self):
        self.put("topic/draft/mutable-default.md", card())
        results, checked, _ = self.check(keys=["mutable-default"])
        self.assertEqual(checked, 1)
        self.assertEqual(results["mutable-default"].failures, [])
        self.assertTrue(any("provenance not checked" in n for n in results["mutable-default"].notes))

    def test_a_key_with_no_file_fails_its_input(self):
        results, _, _ = self.check(keys=["absent"])
        self.assertTrue(results["absent"].failures[0].startswith("input: neither absent.json nor absent.md"))


class Elisions(unittest.TestCase):
    def test_an_elision_after_a_colon_and_a_bare_elision_line_become_pass(self):
        code = "def f(): ...\nclass C:\n    ...\ndef g(): { ... }\nif x:\n    { ... }"
        replaced = cpc.replace_elisions(code)
        self.assertEqual(replaced, "def f(): pass\nclass C:\n    pass\ndef g(): pass\nif x:\n    pass")
        self.assertIsNone(cpc.parse_good(code))

    def test_a_lambda_elision_parses_as_written(self):
        self.assertIsNone(cpc.parse_good("handler = lambda: ..."))

    def test_labels_are_stripped_and_the_code_dedented(self):
        bad, good, err = cpc.split_example(card())
        self.assertIsNone(err)
        self.assertEqual(bad, "def append_to(item, bucket=[]):\n    bucket.append(item)\n    return bucket")
        self.assertTrue(good.startswith("def append_to(item, bucket=None):\n    if bucket is None:\n        ..."))


class Fetching(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_a_5xx_answer_is_retried_once_and_a_404_never(self):
        opener = FakeOpener(statuses={"https://a/": [503, 503], "https://b/": [404, 200]})
        fetcher = cpc.Fetcher(self.tmp, opener=opener)
        self.assertEqual(fetcher.get("https://a/")[0], 503)
        self.assertEqual(fetcher.get("https://b/")[0], 404)
        self.assertEqual(opener.calls, ["https://a/", "https://a/", "https://b/"])

    def test_a_timeout_is_retried_and_the_answer_cached(self):
        opener = FakeOpener(pages={"https://c/": "page"}, statuses={"https://c/": [TimeoutError("slow")]})
        fetcher = cpc.Fetcher(self.tmp, opener=opener)
        self.assertEqual(fetcher.get("https://c/"), (200, "page", ""))
        self.assertEqual(fetcher.get("https://c/"), (200, "page", ""))
        self.assertEqual(opener.calls, ["https://c/", "https://c/"])


class CommandLine(Fixture):
    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cpc.main(list(argv), opener=self.opener)
        return code, out.getvalue(), err.getvalue()

    def test_json_output_and_exit_status_on_a_failure(self):
        self.save(draft(card_markdown=card(triggers="['lambda\\s*:']")))
        code, out, _ = self.run_main("--state", self.state, "--harvest", self.harvest, "--universal", self.universal, "--json")
        self.assertEqual(code, 1)
        report = json.loads(out)
        self.assertEqual(report["summary"], {"cards": 1, "failures": 1, "skipped": 0})
        self.assertEqual(report["cards"]["mutable-default"]["failures"], ["triggers: no trigger matches a line of the bad half"])

    def test_text_output_ends_with_the_summary_line(self):
        self.save(draft())
        code, out, _ = self.run_main("--state", self.state, "--harvest", self.harvest, "--keys", "mutable-default")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip().splitlines()[-1], "check-python-cards: 1 card(s), 0 failure(s), 0 skipped")

    def test_a_missing_state_directory_is_one_line_and_status_2(self):
        code, _, err = self.run_main("--state", os.path.join(self.tmp, "nope"), "--harvest", self.harvest)
        self.assertEqual(code, 2)
        self.assertEqual(len(err.strip().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
