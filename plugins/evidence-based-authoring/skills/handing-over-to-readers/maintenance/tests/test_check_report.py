"""check_report.py: the story form of the operator profile and the list form of the client profile."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import check_report as cr  # noqa: E402


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


SOURCE = "package x;\n\nclass Router {\n    boolean retryOnTimeout = false;\n    int limit = 3;\n}\n"

STORY = """The task was to switch retries off after a timeout. That is done: an order now goes out once, and the tests pass. Nothing is needed from you.

## How it works

The router repeated a request after a timeout, so a slow server got it twice. It now sends once.

```
attempt 1   order sent      `Router` waits
attempt 2   no resend       wf_abcdef12 is a label in a picture
```

## Where to look

- the switch: `src/Router.java:4` `retryOnTimeout = false`
- the tests: 3 of 3 passed in 12 s, `./gradlew test` exit 0
"""

GOOD_CLIENT = """# Questions on the arrival feed

1. The feed now runs over one channel, and a channel drop loses data. If you need a second channel, we build it on your side. Do you need a second channel?
2. The time format in your file differs from the tracker's by a time zone. The answer decides where we convert it. In which time zone do you want the time?
"""

FOREIGN_HEADING = "Где смотреть"


def run_script(*args, config_home: Path | None = None):
    """Run the script as a caller does; the lexicon default resolves under config_home, never the user's own."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"], "XDG_CONFIG_HOME": str(config_home or Path(tempfile.gettempdir()) / "check-report-no-config")}
    return subprocess.run([sys.executable, "-I", str(SCRIPTS / "check_report.py"), *args], capture_output=True, text=True, env=env)


class StoryForm(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "Router.java").write_text(SOURCE, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def codes(self, text, level=None):
        return [f.code for f in cr.check(text, "operator", self.root) if level is None or f.level == level]

    def test_good_story_has_no_findings(self):
        self.assertEqual([], self.codes(STORY))

    def test_operator_is_the_default_profile(self):
        self.assertEqual([], [f.code for f in cr.check(STORY, root=self.root)])

    def test_code_in_the_story_is_an_error(self):
        self.assertIn("STORY-CODE", self.codes(STORY.replace("The router repeated", "`Router` repeated"), cr.ERROR))
        self.assertIn("STORY-CODE", self.codes(STORY.replace("It now sends once.", "The build ended with exit code 1."), cr.ERROR))
        self.assertIn("STORY-CODE", self.codes(STORY.replace("## How it works", "## How `Router` works"), cr.ERROR))

    def test_missing_list_is_an_error(self):
        self.assertIn("WHERE-TO-LOOK", self.codes(STORY.split("## Where to look")[0], cr.ERROR))

    def test_list_heading_forms(self):
        for heading in ("Where to look:", "**Where to look**", "### where to look"):
            self.assertNotIn("WHERE-TO-LOOK", self.codes(STORY.replace("## Where to look", heading)))

    def test_anchor_file_line_and_fragment(self):
        self.assertIn("ANCHOR", self.codes(STORY.replace("src/Router.java:4", "src/Gone.java:4"), cr.ERROR))
        self.assertIn("ANCHOR", self.codes(STORY.replace("src/Router.java:4", "src/Router.java:40"), cr.ERROR))
        self.assertIn("ANCHOR-FRAGMENT", self.codes(STORY.replace("`retryOnTimeout = false`", "`retryOnTimeout = true`"), cr.ERROR))
        self.assertIn("ANCHOR-FRAGMENT", self.codes(STORY.replace("src/Router.java:4", "src/Router.java:5"), cr.WARNING))
        self.assertIn("ANCHOR-FRAGMENT", self.codes(STORY.replace(" `retryOnTimeout = false`", ""), cr.WARNING))

    def test_long_list_is_a_warning(self):
        long_list = STORY + "".join(f"- place {n}: exit 0\n" for n in range(4))
        self.assertIn("WHERE-TO-LOOK", self.codes(long_list, cr.WARNING))

    def test_thin_or_missing_opening_is_a_warning(self):
        thin = STORY.replace("That is done: an order now goes out once, and the tests pass. Nothing is needed from you.", "That is done.")
        self.assertIn("OPENING-SHORT", self.codes(thin, cr.WARNING))
        headed = "## Summary\n\n" + STORY
        self.assertIn("OPENING-SHORT", self.codes(headed, cr.WARNING))

    def test_long_story_sentence_is_a_warning(self):
        long_sentence = "The router repeated " + "the same request to the same gateway " * 4 + "and never looked at its kind."
        self.assertIn("STORY-SENTENCE", self.codes(STORY.replace("It now sends once.", long_sentence), cr.WARNING))

    def test_list_lines_and_headings_carry_no_sentence_warning(self):
        long_item = STORY.replace("## How it works\n", "## How it works\n\n- " + "a place named at length " * 6 + "\n")
        long_heading = STORY.replace("## How it works", "## " + "a heading named at length " * 6)
        self.assertNotIn("STORY-SENTENCE", self.codes(long_item))
        self.assertNotIn("STORY-SENTENCE", self.codes(long_heading))

    def test_three_numbers_in_a_story_sentence_is_a_warning(self):
        numbers = STORY.replace("It now sends once.", "It waited 200, 400 and 800 ms.")
        self.assertIn("NUMBERS", self.codes(numbers, cr.WARNING))

    def test_self_report_needs_an_exit_code_under_the_list(self):
        self.assertNotIn("SELF-REPORT", self.codes(STORY))
        no_exit = STORY.replace(", `./gradlew test` exit 0", "")
        self.assertIn("SELF-REPORT", self.codes(no_exit, cr.WARNING))

    def test_identifiers_flagged_but_commit_hash_allowed(self):
        with_agent_id = STORY.replace("It now sends once.", "Agent a9facb10357345e1e returned it.")
        self.assertIn("IDENTIFIER", self.codes(with_agent_id, cr.ERROR))
        with_hash = STORY.replace("It now sends once.", "The approval is bound to commit f8a3c9a.")
        self.assertEqual([], self.codes(with_hash))

    def test_long_prose_is_a_warning(self):
        filler = "This sentence adds ten words that answer no question here. "
        long_report = STORY.replace("It now sends once.", "It now sends once.\n\n" + filler * 30)
        self.assertIn("LENGTH", self.codes(long_report, cr.WARNING))
        self.assertNotIn("LENGTH", self.codes(STORY))


class Anchors(unittest.TestCase):
    """STORY anchors line 4 of a file of 30 lines; the fragment stands on the lines a test chooses."""

    FRAGMENT_LINE = "    boolean retryOnTimeout = false;"
    NOT_ON_THAT_LINE = "`src/Router.java:4`: fragment `retryOnTimeout = false` is not on that line; "

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def fragment_findings(self, *places):
        lines = [self.FRAGMENT_LINE if number in places else f"    int field{number} = {number};" for number in range(1, 31)]
        (self.root / "src" / "Router.java").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return [(f.level, f.message) for f in cr.check(STORY, "operator", self.root) if f.code == "ANCHOR-FRAGMENT"]

    def test_the_error_names_where_the_fragment_stands(self):
        cases = (
            ((17,), "it stands on line 17"),
            ((7,), "it stands on line 7"),  # three lines below the anchor, one past the warning's reach
            ((17, 25), "it stands on lines 17 and 25"),
            ((10, 12, 14, 16, 18), "it stands on lines 10, 12, 14, 16 and 18"),
            ((10, 12, 14, 16, 18, 20), "it stands on lines 10, 12, 14, 16, 18 and 1 more"),
            ((), "it stands nowhere in the file"),
        )
        for places, where in cases:
            with self.subTest(places=places):
                self.assertEqual([(cr.ERROR, self.NOT_ON_THAT_LINE + where)], self.fragment_findings(*places))

    def test_a_fragment_within_two_lines_of_the_anchor_stays_a_warning(self):
        expected = [(cr.WARNING, "`src/Router.java:4`: fragment found within two lines of the anchor, not on it")]
        self.assertEqual(expected, self.fragment_findings(6, 20))


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

    def test_numbers_and_identifiers(self):
        text = GOOD_CLIENT + "3. The sample has 12 files, 3 classes and 7 tests, built at f8a3c9a. Is the sample enough?\n"
        self.assertIn("NUMBERS", self.codes(text, cr.WARNING))
        self.assertIn("IDENTIFIER", self.codes(text, cr.ERROR))

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
            report.write_text(STORY, encoding="utf-8")
            ok = run_script("--root", d, str(report))
            self.assertEqual(ok.returncode, 0, ok.stdout)
            report.write_text(STORY.split("## Where to look")[0], encoding="utf-8")
            bad = run_script("--root", d, "--json", str(report))
            self.assertEqual(bad.returncode, 1)
            self.assertIn('"WHERE-TO-LOOK"', bad.stdout)
            self.assertEqual(run_script("--root", d, str(root / "missing.md")).returncode, 2)

    def test_strict_fails_on_a_warning(self):
        with tempfile.TemporaryDirectory() as d:
            report = Path(d) / "report.md"
            report.write_text(STORY.replace(" `retryOnTimeout = false`", "").replace("src/Router.java:4", "Router.java:4"), encoding="utf-8")
            (Path(d) / "Router.java").write_text(SOURCE, encoding="utf-8")
            self.assertEqual(run_script("--root", d, str(report)).returncode, 0)
            self.assertEqual(run_script("--root", d, "--strict", str(report)).returncode, 1)


class Lexicon(unittest.TestCase):
    """A lexicon file adds a language's headings and words to the English ones; the patterns are rebuilt from it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "Router.java").write_text(SOURCE, encoding="utf-8")
        self.report = self.root / "report.md"
        self.report.write_text(STORY.replace("## Where to look", f"## {FOREIGN_HEADING}"), encoding="utf-8")
        self.lexicon = self.root / "lexicon.json"
        self.lexicon.write_text(json.dumps({"check_report": {"WHERE_TO_LOOK": [FOREIGN_HEADING]}}), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_report_on_stdin_is_read_as_utf8_under_another_stream_encoding(self):
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONIOENCODING": "cp1252", "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"], "XDG_CONFIG_HOME": str(self.root / "no-config")}
        done = subprocess.run([sys.executable, str(SCRIPTS / "check_report.py"), "--root", str(self.root), "--lexicon", str(self.lexicon), "-"],
                              input=self.report.read_bytes(), capture_output=True, env=env)
        self.assertEqual(done.returncode, 0, done.stdout.decode("utf-8", "replace") + done.stderr.decode("utf-8", "replace"))
        self.assertIn("0 error(s)", done.stdout.decode("utf-8"))
        cr.build_patterns()

    def test_list_heading_from_the_lexicon_is_accepted(self):
        without = run_script("--root", str(self.root), str(self.report))
        self.assertEqual(without.returncode, 1)
        self.assertIn("WHERE-TO-LOOK", without.stdout)
        with_lexicon = run_script("--root", str(self.root), "--lexicon", str(self.lexicon), str(self.report))
        self.assertEqual(with_lexicon.returncode, 0, with_lexicon.stdout)

    def test_lexicon_rebuilds_the_exported_heading_pattern(self):
        self.assertIsNone(cr.LOOK_HEADING.match(f"## {FOREIGN_HEADING}"))
        cr.apply_lexicon(str(self.lexicon))
        self.assertIsNotNone(cr.LOOK_HEADING.match(f"## {FOREIGN_HEADING}"))
        self.assertIsNotNone(cr.LOOK_HEADING.match("## Where to look"))

    def test_default_file_is_read(self):
        config = self.root / "config"
        (config / "handing-over-to-readers").mkdir(parents=True)
        (config / "handing-over-to-readers" / "lexicon.json").write_text(self.lexicon.read_text(encoding="utf-8"), encoding="utf-8")
        run = run_script("--root", str(self.root), str(self.report), config_home=config)
        self.assertEqual(run.returncode, 0, run.stdout)

    def test_missing_default_file_is_no_lexicon(self):
        run = run_script("--root", str(self.root), str(self.report), config_home=self.root / "no-config")
        self.assertEqual(run.returncode, 1)
        self.assertNotIn("lexicon", run.stderr)

    def test_unknown_key_or_bad_regex_is_unreadable(self):
        self.lexicon.write_text(json.dumps({"check_report": {"DANGER": ["Risk"]}}), encoding="utf-8")
        unknown = run_script("--root", str(self.root), "--lexicon", str(self.lexicon), str(self.report))
        self.assertEqual(unknown.returncode, 2)
        self.assertIn("unknown keys", unknown.stderr)
        self.lexicon.write_text(json.dumps({"check_report": {"WHERE_TO_LOOK": ["Look("]}}), encoding="utf-8")
        bad = run_script("--root", str(self.root), "--lexicon", str(self.lexicon), str(self.report))
        self.assertEqual(bad.returncode, 2)
        self.assertIn("regex", bad.stderr)
        self.lexicon.write_text(json.dumps({"other_script": {}}), encoding="utf-8")
        section = run_script("--root", str(self.root), "--lexicon", str(self.lexicon), str(self.report))
        self.assertEqual(section.returncode, 2)
        self.assertIn("sections", section.stderr)


if __name__ == "__main__":
    unittest.main()
