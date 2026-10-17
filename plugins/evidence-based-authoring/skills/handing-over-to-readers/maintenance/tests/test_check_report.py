"""check_report.py: the report form of the operator profile and the list form of the client profile."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_report as cr  # noqa: E402

SOURCE = "package x;\n\nclass Router {\n    boolean retryOnTimeout = false;\n    int limit = 3;\n}\n"

GOOD_OPERATOR = """**Risk:** medium: the change touches the order path.
**From the reader:** approve the diff.
**Not done:** the JMH run.
**Wrong if:** the limit is set at runtime.
**Status:** findings; checked 3 units; failed steps: none.

## Claims
- Retry is off: `src/Router.java:4` `retryOnTimeout = false`; evidence: the test fails on rollback.
- The limit is read from the configuration; evidence: exit code 0 of `LimitsTest`.

## Decisions
- The field name stays; basis: the glossary; overturned by: a rename.

## Questions
- The timeout is 250 ms and the exchange p99 is 180 ms. The answer changes the retry limit; the decision is irreversible after rollout. Keep 250 ms?

## Internal
- Transcript: 2 files of 2 read.
"""

GOOD_CLIENT = """# Questions on the quote feed

1. The feed now runs over one channel, and a channel drop loses data. If you need a second channel, we build it on your side. Do you need a second channel?
2. The time format in your file differs from the exchange's by a time zone. The answer decides where we convert it. In which time zone do you want the time?
"""


def run_script(*args, stdin=None):
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_report.py"), *args], input=stdin, capture_output=True, text=True)


class OperatorProfile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "Router.java").write_text(SOURCE, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def codes(self, text, level=None):
        return [f.code for f in cr.check(text, "operator", self.root) if level is None or f.level == level]

    def test_good_report_has_no_errors(self):
        self.assertEqual(self.codes(GOOD_OPERATOR, cr.ERROR), [])

    def test_missing_first_page_lines(self):
        text = GOOD_OPERATOR.replace("**Wrong if:** the limit is set at runtime.\n", "")
        self.assertIn("FIRST-PAGE", self.codes(text, cr.ERROR))

    def test_first_page_line_without_value(self):
        text = GOOD_OPERATOR.replace("**Not done:** the JMH run.", "**Not done:**")
        self.assertIn("FIRST-PAGE", self.codes(text, cr.ERROR))

    def test_status_needs_enumerated_value_and_count(self):
        bad_value = GOOD_OPERATOR.replace("**Status:** findings; checked 3 units", "**Status:** all good; checked 3 units")
        self.assertIn("STATUS", self.codes(bad_value, cr.ERROR))
        no_count = GOOD_OPERATOR.replace("**Status:** findings; checked 3 units; failed steps: none.", "**Status:** clean")
        self.assertIn("STATUS", self.codes(no_count, cr.ERROR))
        not_run = GOOD_OPERATOR.replace("**Status:** findings; checked 3 units; failed steps: none.", "**Status:** not-run")
        self.assertNotIn("STATUS", self.codes(not_run, cr.ERROR))

    def test_anchor_file_line_and_fragment(self):
        missing = GOOD_OPERATOR.replace("src/Router.java:4", "src/Gone.java:4")
        self.assertIn("ANCHOR", self.codes(missing, cr.ERROR))
        out_of_range = GOOD_OPERATOR.replace("src/Router.java:4", "src/Router.java:40")
        self.assertIn("ANCHOR", self.codes(out_of_range, cr.ERROR))
        wrong_fragment = GOOD_OPERATOR.replace("`retryOnTimeout = false`", "`retryOnTimeout = true`")
        self.assertIn("ANCHOR-FRAGMENT", self.codes(wrong_fragment, cr.ERROR))
        moved = GOOD_OPERATOR.replace("src/Router.java:4", "src/Router.java:5")
        findings = cr.check(moved, "operator", self.root)
        self.assertIn(("ANCHOR-FRAGMENT", cr.WARNING), [(f.code, f.level) for f in findings])
        no_fragment = GOOD_OPERATOR.replace(" `retryOnTimeout = false`", "")
        self.assertIn("ANCHOR-FRAGMENT", self.codes(no_fragment, cr.WARNING))

    def test_claim_without_evidence(self):
        text = GOOD_OPERATOR.replace("- The limit is read from the configuration; evidence: exit code 0 of `LimitsTest`.", "- The limit is read from the configuration.")
        self.assertIn("CLAIM-EVIDENCE", self.codes(text, cr.ERROR))

    def test_question_item_form(self):
        no_mark = GOOD_OPERATOR.replace("Keep 250 ms?", "Keep 250 ms.")
        self.assertIn("QUESTION", self.codes(no_mark, cr.ERROR))
        two_marks = GOOD_OPERATOR.replace("Keep 250 ms?", "Keep 250 ms? Or raise it?")
        self.assertIn("QUESTION", self.codes(two_marks, cr.ERROR))
        not_last = GOOD_OPERATOR.replace("Keep 250 ms?", "Keep 250 ms? This matters.")
        self.assertIn("QUESTION", self.codes(not_last, cr.ERROR))

    def test_identifiers_flagged_but_commit_hash_allowed(self):
        with_agent_id = GOOD_OPERATOR.replace("## Internal", "Agent a9facb10357345e1e returned the report.\n\n## Internal")
        self.assertIn("IDENTIFIER", self.codes(with_agent_id, cr.ERROR))
        with_hash = GOOD_OPERATOR.replace("## Internal", "The approval is bound to commit `f8a3c9a`.\n\n## Internal")
        self.assertNotIn("IDENTIFIER", self.codes(with_hash, cr.ERROR))

    def test_warnings_self_report_and_numbers(self):
        text = GOOD_OPERATOR.replace("## Decisions", "All tests pass.\nThe sample has 12 files, 3 classes and 7 tests.\n\n## Decisions")
        warnings = self.codes(text, cr.WARNING)
        for code in ("SELF-REPORT", "NUMBERS"):
            self.assertIn(code, warnings)
        self.assertEqual(self.codes(text, cr.ERROR), [])

    def test_fenced_blocks_are_skipped(self):
        text = GOOD_OPERATOR + "\n```\nwf_abcdef12 all tests pass? really?\n```\n"
        self.assertEqual(self.codes(text, cr.ERROR), [])


class ClientProfile(unittest.TestCase):
    def codes(self, text, level=None):
        return [f.code for f in cr.check(text, "client") if level is None or f.level == level]

    def test_good_list_has_no_errors(self):
        self.assertEqual(self.codes(GOOD_CLIENT, cr.ERROR), [])

    def test_paths_sections_dates_effort_flagged(self):
        text = GOOD_CLIENT + (
            "3. Details are in section 4.2 of our report and in the file src/feed.py. We deliver by 12.11.2026, which takes 3 days of work, as agreed. Do you agree?\n"
        )
        codes = self.codes(text, cr.ERROR)
        for code in ("PATH", "SECTION-REF", "DATE", "EFFORT", "AS-AGREED"):
            self.assertIn(code, codes)

    def test_item_without_question_and_duplicate(self):
        text = GOOD_CLIENT + (
            "3. We build the second channel on your side when the first one drops.\n"
            "4. The feed now runs over one channel, and a channel drop loses data. Do you need a second channel on your side?\n"
        )
        findings = cr.check(text, "client")
        self.assertIn("QUESTION", [f.code for f in findings if f.level == cr.ERROR])
        self.assertIn("DUPLICATE", [f.code for f in findings if f.level == cr.WARNING])

    def test_internal_block_is_exempt(self):
        text = GOOD_CLIENT + "\n## Internal\n- Our file src/feed.py and the deadline by Friday.\n"
        self.assertEqual(self.codes(text, cr.ERROR), [])


class CommandLine(unittest.TestCase):
    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "Router.java").write_text(SOURCE, encoding="utf-8")
            report = root / "report.md"
            report.write_text(GOOD_OPERATOR, encoding="utf-8")
            ok = run_script("--root", d, str(report))
            self.assertEqual(ok.returncode, 0, ok.stdout)
            report.write_text(GOOD_OPERATOR.replace("**Status:** findings; checked 3 units; failed steps: none.\n", ""), encoding="utf-8")
            bad = run_script("--root", d, "--json", str(report))
            self.assertEqual(bad.returncode, 1)
            self.assertIn('"STATUS"', bad.stdout)


class Lexicon(unittest.TestCase):
    """A lexicon file adds a language's labels and words to the English ones; the patterns are rebuilt from it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "Router.java").write_text(SOURCE, encoding="utf-8")
        self.report = self.root / "report.md"
        self.report.write_text(GOOD_OPERATOR.replace("**Risk:**", "**Danger:**"), encoding="utf-8")
        self.lexicon = self.root / "lexicon.json"
        self.lexicon.write_text(json.dumps({"check_report": {"RISK": ["Danger"]}}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_label_from_the_lexicon_is_accepted(self):
        without = run_script("--root", str(self.root), str(self.report))
        self.assertEqual(without.returncode, 1)
        self.assertIn("FIRST-PAGE", without.stdout)
        with_lexicon = run_script("--root", str(self.root), "--lexicon", str(self.lexicon), str(self.report))
        self.assertEqual(with_lexicon.returncode, 0, with_lexicon.stdout)

    def test_unknown_key_or_bad_regex_is_unreadable(self):
        self.lexicon.write_text(json.dumps({"check_report": {"DANGER": ["Risk"]}}), encoding="utf-8")
        unknown = run_script("--root", str(self.root), "--lexicon", str(self.lexicon), str(self.report))
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("unknown keys", unknown.stderr)
        self.lexicon.write_text(json.dumps({"check_report": {"RISK": ["Danger("]}}), encoding="utf-8")
        bad = run_script("--root", str(self.root), "--lexicon", str(self.lexicon), str(self.report))
        self.assertEqual(bad.returncode, 2)
        self.assertIn("regex", bad.stderr)
        self.lexicon.write_text(json.dumps({"other_script": {}}), encoding="utf-8")
        section = run_script("--root", str(self.root), "--lexicon", str(self.lexicon), str(self.report))
        self.assertEqual(section.returncode, 2)
        self.assertIn("sections", section.stderr)

    def test_missing_default_file_is_no_lexicon(self):
        env = {"XDG_CONFIG_HOME": str(self.root / "no-config"), "PATH": "/usr/bin:/bin"}
        run = subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_report.py"), "--root", str(self.root), str(self.report)], capture_output=True, text=True, env=env)
        self.assertEqual(run.returncode, 1)
        self.assertNotIn("lexicon", run.stderr)


if __name__ == "__main__":
    unittest.main()
