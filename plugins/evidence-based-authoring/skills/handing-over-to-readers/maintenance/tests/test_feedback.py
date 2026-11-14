"""feedback.py: the usage journal, its switch and its summary, and the one line each script adds to it."""
from __future__ import annotations

import contextlib
import datetime
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures/page"
sys.path.insert(0, str(SCRIPTS))
import feedback as fb  # noqa: E402


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


PLUGIN_VERSION = fb.plugin_version(fb.read_manifest(fb.MANIFEST))
TODAY = datetime.date.today().isoformat()
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
TIME_OF_DAY = re.compile(r"\d{1,2}:\d{2}")

# One example of every event of the schema, every field set.
EXAMPLES = {
    "report": {"profile": "client", "errors": 2, "warnings": 0, "codes": {"DATE": 1, "PATH": 1}},
    "card": {"mode": "hook", "outcome": "resent", "questions": 1, "candidates": 2, "codes": {}},
    "answer": {"count": 3},
    "reader_find": {"found": False},
    "reader_add": {"holds": 2, "lacks": 0, "use": "none", "depth": "change", "turns": 3},
    "ledger_find": {"found": 0},
    "ledger_add": {"kind": "default"},
    "ledger_note": {},
    "ledger_supersede": {},
    "cold_read": {"questions": 3, "answered": 1, "partly": 1, "unsupported": 0, "missing": 1, "unexplained": 0, "dropped": 2},
    "page": {"outcome": "built", "sentences": 4, "parts": 2, "decisions": 1, "look": 4, "violations": 0},
    "voice": {"backend": "module", "outcome": "written", "sentences": 9, "paragraphs": 3, "seconds": 41},
    "page_check": {"outcome": "findings", "parts": 4, "findings": 2, "shots": 8},
}

# A good card of the card form, as in test_check_question.py.
GOOD = {
    "question": "The acknowledgement timeout is 250 ms and the worker p99 is 180 ms. The answer changes the retry limit and its test; after rollout the decision is irreversible. Keep 250 ms?",
    "header": "Timeout",
    "options": [
        {"label": "250 ms", "description": "Fewer retries; at a p99 spike some jobs go to retry, cost of error: a duplicate job."},
        {"label": "400 ms", "description": "Almost no retries; the acknowledgement arrives 150 ms later, cost of error: a missed update."},
    ],
}
BARE = {"question": "Which one?", "options": [{"label": "A", "description": "a"}]}

COLD_REPORT = "The task was to add a retry to the payment call. The retry is in, and two of three tests pass.\n"
COLD_QUESTIONS = {"questions": ["What was the task?", "How did it end?", "What do I decide?"]}
COLD_ANSWERS = {
    "answers": [
        {"question": "What was the task?", "found": "yes", "quotes": ["The task was to add a retry to the payment call."]},
        {"question": "How did it end?", "found": "partly", "quotes": ["The retry is in"]},
        {"question": "What do I decide?", "found": "no", "missing": "the decision"},
    ],
    "unexplained": [{"term": "retry", "quote": "The retry is in"}, {"term": "gateway", "quote": "a sentence the report lacks"}],
}

CUES = [
    {"paragraph": 1, "sentence": 1, "text": "The cache served old thumbnails.", "start": 0.0, "end": 2.0},
    {"paragraph": 1, "sentence": 2, "text": "Now it does not.", "start": 2.3, "end": 3.5},
    {"paragraph": 2, "sentence": 1, "text": "How it broke.", "start": 4.1, "end": 5.0},
    {"paragraph": 2, "sentence": 2, "text": "The key had no version.", "start": 5.3, "end": 7.0},
]
BODY = ('<p data-say>The cache served old thumbnails. Now it does not.</p>\n'
        '<h2 data-part="How it broke.">How it broke</h2>\n<p data-say>The key had no version.</p>\n')
FIXTURE_LOOK_ITEMS = 4  # the items under "Where to look" of fixtures/page/report.md

# A TTS command: a silent WAV of one second per word at 10 frames a second; the word "fail" exits 3.
FAKE_COMMAND = '''
import sys, wave
text, out = sys.argv[sys.argv.index("--text") + 1], sys.argv[sys.argv.index("--out") + 1]
if "fail" in text:
    sys.exit(3)
with wave.open(out, "wb") as audio:
    audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(10)
    audio.writeframes(b"\\0\\0" * 10 * len(text.split()))
'''


class Workspace(unittest.TestCase):
    """A temporary directory with a journal directory of its own and the inputs of every script."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.journal_dir = self.dir / "journal"
        self.work = self.dir / "work"
        self.make_inputs()

    def tearDown(self):
        self._tmp.cleanup()

    def make_inputs(self):
        """The inputs at fixed paths under work, made anew: a run leaves outputs a second run must not see."""
        shutil.rmtree(self.work, ignore_errors=True)
        self.work.mkdir()
        files = {
            "short.md": "Short.\n",
            "good.json": json.dumps({"questions": [GOOD]}),
            "cold-report.md": COLD_REPORT,
            "cold-questions.json": json.dumps(COLD_QUESTIONS),
            "cold-answers.json": json.dumps(COLD_ANSWERS),
            "body.html": BODY,
            "bad-body.html": BODY + '<p><a href="#nowhere">back</a></p>\n',
            "cues.json": json.dumps(CUES),
            "story.txt": "One two three.\n\nFour five.\n",
            "fail.txt": "This will fail.\n",
            "tts.py": FAKE_COMMAND,
        }
        for name, text in files.items():
            (self.work / name).write_text(text, encoding="utf-8")

    def env(self, **extra):
        return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.dir / "home"), "XDG_CONFIG_HOME": str(self.dir / "config"),
                "XDG_STATE_HOME": str(self.work / "state"), "HANDOVER_LEDGER_FILE": str(self.work / "ledger.jsonl"),
                "HANDOVER_READER_FILE": str(self.work / "reader.jsonl"), "HANDOVER_FEEDBACK_DIR": str(self.journal_dir), **extra}

    def run_script(self, script, *args, stdin=None, env=None):
        """A run as a caller makes it, under -I: (exit code, stdout, stderr) as bytes."""
        done = subprocess.run([sys.executable, "-I", str(SCRIPTS / script), *args], input=stdin, capture_output=True, env=env or self.env(), cwd=self.work)
        return done.returncode, done.stdout, done.stderr

    def turn_on(self):
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        (self.journal_dir / fb.SWITCH_FILE).write_text('{"journal": true}\n', encoding="utf-8")

    def events(self):
        """The journal's lines as objects, without day and version, which test_a_line_holds_exactly_the_keys_of_the_schema checks."""
        path = self.journal_dir / fb.JOURNAL_FILE
        if not path.exists():
            return []
        lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        for line in lines:
            self.assertEqual((line.pop("day"), line.pop("version")), (TODAY, PLUGIN_VERSION))
        return lines

    def tts(self):
        return f"{sys.executable} {self.work / 'tts.py'} --text {{text}} --out {{out}}"

    def card_payload(self, card, session="session-1"):
        return json.dumps({"session_id": session, "tool_input": {"questions": [card]}}).encode("utf-8")

    def write_ledger(self, question):
        record = {"id": "a-0001", "date": "2026-11-01", "kind": "answer", "question": question, "answer": "Keep 250 ms", "basis": "b", "status": "active"}
        (self.work / "ledger.jsonl").write_text(json.dumps(record) + "\n", encoding="utf-8")

    def records(self, *args):
        return self.run_script("records.py", *args)

    def all_runs(self):
        """One run of each command of each script, every event of the schema among them."""
        self.write_ledger(GOOD["question"])
        w = self.work
        runs = [
            self.run_script("check_report.py", str(w / "short.md")),
            self.run_script("check_question.py", "--hook", stdin=self.card_payload(GOOD)),
            self.run_script("check_question.py", "--questions", str(w / "good.json")),
            self.records("reader", "add", "--topic", "retry policy of the payment client", "--basis", "b", "--holds", "the retry", "--turns", "1"),
            self.records("reader", "find", "--topic", "retry policy of the payment client"),
            self.records("ledger", "add", "--kind", "closure", "--question", "Which log format does the exporter write?", "--answer", "JSON", "--basis", "b"),
            self.records("ledger", "find", "--question", "Which log format does the exporter write?"),
            self.records("ledger", "note", "a-0002", "--scope", "the exporter"),
            self.records("ledger", "supersede", "a-0001", "--by", "a-0002"),
            self.run_script("records.py", "ledger", "capture", "--hook", stdin=json.dumps({"tool_input": {"questions": [GOOD]}, "tool_response": {}}).encode("utf-8")),
            self.run_script("check_cold_read.py", "--report", str(w / "cold-report.md"), "--questions", str(w / "cold-questions.json"), "--answers", str(w / "cold-answers.json")),
            self.run_script("build_page.py", "--body", str(w / "body.html"), "--cues", str(w / "cues.json"), "--report", str(FIXTURES / "report.md"), "--out", str(w / "page.html")),
            self.run_script("voice_cues.py", "--tts-command", self.tts(), str(w / "story.txt"), str(w / "out.wav"), str(w / "out.json")),
            self.run_script("check_page.py", str(w / "page.html"), "--chrome", str(w / "no-browser")),
        ]
        return runs


class Switch(Workspace):
    def main(self, *argv, manifest=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = fb.main(list(argv), {"HANDOVER_FEEDBACK_DIR": str(self.journal_dir)}, manifest or self.dir / "absent.json")
        return code, out.getvalue(), err.getvalue()

    def test_off_by_default_a_run_of_each_script_writes_no_file(self):
        runs = self.all_runs()
        self.assertEqual(len(runs), 14)
        self.assertFalse(self.journal_dir.exists())

    def test_on_sets_the_switch_and_says_what_the_journal_holds_and_where(self):
        code, out, err = self.main("on")
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(fb.is_on(self.journal_dir))
        self.assertEqual(json.loads((self.journal_dir / fb.SWITCH_FILE).read_text(encoding="utf-8")), {"journal": True})
        self.assertEqual(len(out.splitlines()), 2)
        self.assertIn(f"no text, to {self.journal_dir / fb.JOURNAL_FILE}.", out)

    def test_off_clears_the_switch_and_names_the_events_it_keeps(self):
        self.main("on")
        (self.journal_dir / fb.JOURNAL_FILE).write_text(fb.event_line("answer", {"count": 1}, "6.0.0", TODAY), encoding="utf-8")
        code, out, err = self.main("off")
        self.assertEqual((code, err), (0, ""))
        self.assertFalse(fb.is_on(self.journal_dir))
        self.assertEqual(json.loads((self.journal_dir / fb.SWITCH_FILE).read_text(encoding="utf-8")), {"journal": False})
        self.assertEqual(out, f"The usage journal is off: the scripts add nothing to {self.journal_dir / fb.JOURNAL_FILE}, which holds 1 event(s); feedback.py reset deletes them.\n")

    def test_status_counts_the_events_and_the_days_with_use(self):
        self.main("on")
        lines = [fb.event_line("answer", {"count": 1}, "6.0.0", day) for day in ("2026-11-01", "2026-11-01", "2026-11-03")]
        (self.journal_dir / fb.JOURNAL_FILE).write_text("".join(lines), encoding="utf-8")
        code, out, _ = self.main("status")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), ["the usage journal is on", f"directory: {self.journal_dir}", "3 event(s) on 2 day(s) with use"])

    def test_status_of_an_untouched_directory_is_off_and_empty(self):
        code, out, _ = self.main("status")
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines(), ["the usage journal is off", f"directory: {self.journal_dir}", "0 event(s) on 0 day(s) with use"])
        self.assertFalse(self.journal_dir.exists())

    def test_reset_deletes_the_journal_and_keeps_the_switch(self):
        self.main("on")
        journal = self.journal_dir / fb.JOURNAL_FILE
        journal.write_text(fb.event_line("ledger_note", {}, "6.0.0", TODAY) * 2, encoding="utf-8")
        code, out, _ = self.main("reset")
        self.assertEqual(code, 0)
        self.assertEqual(out, f"removed 2 event(s) from {journal}; the journal stays on\n")
        self.assertFalse(journal.exists())
        self.assertTrue(fb.is_on(self.journal_dir))

    def test_a_directory_that_cannot_be_written_is_exit_2(self):
        self.journal_dir.write_text("a file where the directory must be", encoding="utf-8")
        for command in ("on", "off", "reset"):
            code, out, err = self.main(command)
            self.assertEqual((command, code, out), (command, 2, ""))
            self.assertIn("feedback.py: cannot", err)

    def test_a_switch_other_than_journal_true_is_off(self):
        self.journal_dir.mkdir()
        for content in ('{"journal": 1}', '{"journal": "true"}', '{"journal": true, "more": 1}', "[true]", "not json", ""):
            (self.journal_dir / fb.SWITCH_FILE).write_text(content, encoding="utf-8")
            self.assertEqual((content, fb.is_on(self.journal_dir)), (content, False))

    def test_status_is_utf8_under_another_stream_encoding(self):
        """A directory name outside ASCII reaches stdout as UTF-8 although the process's streams are cp1252."""
        self.journal_dir = self.dir / "журнал"
        done = subprocess.run([sys.executable, str(SCRIPTS / "feedback.py"), "status"], capture_output=True,
                              env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONIOENCODING": "cp1252", "HANDOVER_FEEDBACK_DIR": str(self.journal_dir)})
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
        self.assertIn(f"directory: {self.journal_dir}", done.stdout.decode("utf-8"))


class Record(Workspace):
    """record() in process, the journal directory named by the environment."""

    def setUp(self):
        super().setUp()
        environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": str(self.journal_dir)})
        environment.start()
        self.addCleanup(environment.stop)

    def record(self, event, **fields):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            fb.record(event, **fields)
        self.assertEqual((out.getvalue(), err.getvalue()), ("", ""))

    def test_each_event_of_the_schema_is_written(self):
        self.turn_on()
        for event, fields in EXAMPLES.items():
            self.record(event, **fields)
        self.assertEqual(self.events(), [{"event": event, **fields} for event, fields in EXAMPLES.items()])

    def test_the_examples_cover_the_schema(self):
        self.assertEqual({event: set(fields) for event, fields in EXAMPLES.items()}, {event: set(fields) for event, fields in fb.SCHEMA.items()})

    def test_an_event_outside_the_schema_is_dropped_whole(self):
        self.turn_on()
        dropped = [
            ("unknown event", "draft", {}),
            ("unknown field", "answer", {"count": 1, "note": 1}),
            ("text field", "answer", {"text": "the question was about timeouts"}),
            ("word outside its set", "report", {"profile": "maintainer"}),
            ("negative number", "answer", {"count": -1}),
            ("float", "voice", {"seconds": 1.5}),
            ("boolean for a count", "answer", {"count": True}),
            ("string for a boolean", "reader_find", {"found": "yes"}),
            ("nested list", "answer", {"count": [1]}),
            ("nested mapping", "page", {"look": {"n": 1}}),
            ("None", "ledger_add", {"kind": None}),
            ("code in lower case", "report", {"codes": {"anchor": 1}}),
            ("code of one letter", "report", {"codes": {"A": 1}}),
            ("code of 33 characters", "report", {"codes": {"A" * 33: 1}}),
            ("code with a space", "report", {"codes": {"STORY CODE": 1}}),
            ("code with a newline", "report", {"codes": {"ANCHOR\n": 1}}),
            ("code count zero", "report", {"codes": {"ANCHOR": 0}}),
            ("code count text", "report", {"codes": {"ANCHOR": "1"}}),
            ("codes as a list", "report", {"codes": ["ANCHOR"]}),
            ("field outside the schema of the page check", "page_check", {"outcome": "clean", "seconds": 3}),
            ("outcome outside its set", "page_check", {"outcome": "passed"}),
        ]
        for _, event, fields in dropped:
            self.record(event, **fields)
        self.assertEqual(self.events(), [])

    def test_the_bounds_of_a_code_are_accepted(self):
        self.turn_on()
        self.record("report", codes={"AB": 1, "A" * 32: 1, "A-9": 2})
        self.assertEqual(self.events(), [{"event": "report", "codes": {"A" * 32: 1, "A-9": 2, "AB": 1}}])

    def test_a_line_holds_exactly_the_keys_of_the_schema_and_no_time_of_day(self):
        self.turn_on()
        self.record("report", profile="operator", errors=0, warnings=1, codes={"LENGTH": 1})
        raw = (self.journal_dir / fb.JOURNAL_FILE).read_text(encoding="utf-8")
        line = json.loads(raw)
        self.assertEqual(list(line), ["day", "version", "event", "profile", "errors", "warnings", "codes"])
        self.assertEqual(line["day"], TODAY)
        self.assertIsNone(TIME_OF_DAY.search(raw))

    @unittest.skipIf(os.name != "posix", "file modes are POSIX")
    def test_the_journal_is_created_with_mode_0600(self):
        self.turn_on()
        self.record("ledger_note")
        self.assertEqual((self.journal_dir / fb.JOURNAL_FILE).stat().st_mode & 0o777, 0o600)

    def test_with_the_journal_off_nothing_is_written(self):
        self.record("answer", count=1)
        self.assertFalse(self.journal_dir.exists())

    def test_a_failure_to_write_is_silent(self):
        self.turn_on()
        (self.journal_dir / fb.JOURNAL_FILE).mkdir()
        self.record("answer", count=1)
        self.assertTrue((self.journal_dir / fb.JOURNAL_FILE).is_dir())

    def test_the_version_comes_from_the_plugin_manifest(self):
        self.turn_on()
        manifest = self.dir / "plugin.json"
        cases = [('{"version": "1.2.3-rc.1+b7"}', "1.2.3-rc.1+b7"), ('{"version": "1.2 3"}', "unknown"),
                 (json.dumps({"version": "1" * 25}), "unknown"), ('{"version": 7}', "unknown"), ("not json", "unknown")]
        for content, version in cases:
            manifest.write_text(content, encoding="utf-8")
            fb.append_event(self.journal_dir, manifest, "ledger_note", {})
        fb.append_event(self.journal_dir, self.dir / "absent.json", "ledger_note", {})
        lines = [json.loads(line) for line in (self.journal_dir / fb.JOURNAL_FILE).read_text(encoding="utf-8").splitlines()]
        self.assertEqual([line["version"] for line in lines], [version for _, version in cases] + ["unknown"])

    def test_the_directory_defaults_to_the_state_home(self):
        self.assertEqual(fb.feedback_dir({"HOME": "/h"}), Path("/h/.local/state/handing-over-to-readers"))
        self.assertEqual(fb.feedback_dir({"HOME": "/h", "XDG_STATE_HOME": ""}), Path("/h/.local/state/handing-over-to-readers"))
        self.assertEqual(fb.feedback_dir({"HOME": "/h", "XDG_STATE_HOME": "/s"}), Path("/s/handing-over-to-readers"))
        self.assertEqual(fb.feedback_dir({"HOME": "/h", "XDG_STATE_HOME": "/s", "HANDOVER_FEEDBACK_DIR": "/f"}), Path("/f"))


class ScriptEvents(Workspace):
    """Each script, run as a child with the journal on, adds its one event with the right counts."""

    def setUp(self):
        super().setUp()
        self.turn_on()

    def test_report(self):
        code, _, _ = self.run_script("check_report.py", str(self.work / "short.md"))
        self.assertEqual(code, 1)
        self.assertEqual(self.events(), [{"event": "report", "profile": "operator", "errors": 1, "warnings": 1, "codes": {"OPENING-SHORT": 1, "WHERE-TO-LOOK": 1}}])

    def test_card(self):
        """passed in file mode; form; returned by the gate; resent once every record was shown; passed without a ledger."""
        self.write_ledger(GOOD["question"])
        self.run_script("check_question.py", "--questions", str(self.work / "good.json"))
        self.run_script("check_question.py", "--hook", stdin=self.card_payload(BARE))
        self.assertEqual(self.run_script("check_question.py", "--hook", stdin=self.card_payload(GOOD))[0], 2)
        self.assertEqual(self.run_script("check_question.py", "--hook", stdin=self.card_payload(GOOD))[0], 0)
        (self.work / "ledger.jsonl").unlink()
        self.run_script("check_question.py", "--hook", stdin=self.card_payload(GOOD))
        self.assertEqual(self.events(), [
            {"event": "card", "mode": "file", "outcome": "passed", "questions": 1},
            {"event": "card", "mode": "hook", "outcome": "form", "questions": 1, "codes": {"FACT": 1, "OPTIONS": 1, "WHY-ASKED": 1}},
            {"event": "card", "mode": "hook", "outcome": "returned", "questions": 1, "candidates": 1},
            {"event": "card", "mode": "hook", "outcome": "resent", "questions": 1, "candidates": 1},
            {"event": "card", "mode": "hook", "outcome": "passed", "questions": 1, "candidates": 0},
        ])

    def test_answer(self):
        payload = {"tool_input": {"questions": [GOOD, dict(GOOD, question="Which log format does the exporter write?")]}, "tool_response": {}}
        self.run_script("records.py", "ledger", "capture", "--hook", stdin=json.dumps(payload).encode("utf-8"))
        self.assertEqual(self.events(), [{"event": "answer", "count": 2}])

    def test_reader_find(self):
        self.records("reader", "add", "--topic", "retry policy of the payment client", "--basis", "b")
        self.assertEqual(self.records("reader", "find", "--topic", "retry policy of the payment client")[0], 0)
        self.assertEqual(self.records("reader", "find", "--topic", "colour of the dashboard header")[0], 1)
        self.assertEqual(self.events()[1:], [{"event": "reader_find", "found": True}, {"event": "reader_find", "found": False}])

    def test_reader_add(self):
        self.records("reader", "add", "--topic", "t", "--basis", "b", "--holds", "x", "y", "--lacks", "z", "--use", "decide", "--turns", "2")
        self.records("reader", "add", "--topic", "t", "--basis", "b", "--depth", "mechanism")
        self.assertEqual(self.events(), [
            {"event": "reader_add", "holds": 2, "lacks": 1, "use": "decide", "depth": "none", "turns": 2},
            {"event": "reader_add", "holds": 0, "lacks": 0, "use": "none", "depth": "mechanism"},
        ])

    def test_ledger_find(self):
        self.write_ledger(GOOD["question"])
        self.records("ledger", "find", "--question", GOOD["question"])
        self.records("ledger", "find", "--question", "What colour should the dashboard header have?")
        self.assertEqual(self.events(), [{"event": "ledger_find", "found": 1}, {"event": "ledger_find", "found": 0}])

    def test_ledger_add(self):
        self.records("ledger", "add", "--kind", "closure", "--question", "q?", "--answer", "a", "--basis", "b")
        self.assertEqual(self.events(), [{"event": "ledger_add", "kind": "closure"}])

    def test_ledger_note(self):
        self.write_ledger(GOOD["question"])
        self.assertEqual(self.records("ledger", "note", "a-0001", "--scope", "the worker")[0], 0)
        self.assertEqual(self.events(), [{"event": "ledger_note"}])

    def test_ledger_supersede(self):
        self.write_ledger(GOOD["question"])
        self.records("ledger", "add", "--kind", "answer", "--question", "q?", "--answer", "a", "--basis", "b")
        self.assertEqual(self.records("ledger", "supersede", "a-0001", "--by", "a-0002")[0], 0)
        self.assertEqual(self.events()[1:], [{"event": "ledger_supersede"}])

    def test_cold_read(self):
        w = self.work
        code, _, _ = self.run_script("check_cold_read.py", "--report", str(w / "cold-report.md"), "--questions", str(w / "cold-questions.json"), "--answers", str(w / "cold-answers.json"))
        self.assertEqual(code, 1)
        self.assertEqual(self.events(), [{"event": "cold_read", "questions": 3, "answered": 1, "partly": 1, "unsupported": 0, "missing": 1, "unexplained": 1, "dropped": 1}])

    def test_page(self):
        w = self.work
        args = ["--cues", str(w / "cues.json"), "--report", str(FIXTURES / "report.md"), "--out", str(w / "page.html")]
        self.assertEqual(self.run_script("build_page.py", "--body", str(w / "body.html"), *args)[0], 0)
        self.assertEqual(self.run_script("build_page.py", "--body", str(w / "bad-body.html"), *args)[0], 1)
        self.assertEqual(self.events(), [
            {"event": "page", "outcome": "built", "sentences": 4, "parts": 2, "decisions": 0, "look": FIXTURE_LOOK_ITEMS, "violations": 0},
            {"event": "page", "outcome": "refused", "sentences": 4, "decisions": 0, "look": FIXTURE_LOOK_ITEMS, "violations": 1},
        ])

    def test_voice(self):
        """written with its counts; failed when the chosen backend fails; nothing when the input is unusable."""
        w = self.work
        outputs = [str(w / "out.wav"), str(w / "out.json")]
        self.assertEqual(self.run_script("voice_cues.py", "--tts-command", self.tts(), str(w / "story.txt"), *outputs)[0], 0)
        self.assertEqual(self.run_script("voice_cues.py", "--tts-command", self.tts(), str(w / "fail.txt"), *outputs)[0], 2)
        self.assertEqual(self.run_script("voice_cues.py", "--tts-command", self.tts(), str(w / "absent.txt"), *outputs)[0], 2)
        self.assertEqual(self.events(), [  # 5 words of 1 s, a gap of 0.25 s and a pause of 0.6 s after each of 2 sentences: 6.7 s
            {"event": "voice", "backend": "command", "outcome": "written", "sentences": 2, "paragraphs": 2, "seconds": 7},
            {"event": "voice", "backend": "command", "outcome": "failed", "paragraphs": 1},
        ])

    def test_page_check_without_a_browser(self):
        w = self.work
        (w / "page.html").write_text("<title>A page</title>\n", encoding="utf-8")
        self.assertEqual(self.run_script("check_page.py", str(w / "page.html"), "--chrome", str(w / "no-browser"))[0], 3)
        self.assertEqual(self.events(), [{"event": "page_check", "outcome": "no_browser"}])

    @unittest.skipIf(os.name != "posix", "the fake browser is started by its first line, as POSIX starts a script")
    def test_page_check_with_a_browser(self):
        """clean with the parts and the pictures counted; findings with their number."""
        w = self.work
        (w / "page.html").write_text("<title>A page</title>\n", encoding="utf-8")
        browser = w / "fake-browser"
        browser.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(FIXTURES / 'fake_browser.py'))} \"$@\"\n", encoding="utf-8")
        browser.chmod(0o755)
        parts = [{"title": "Opening", "top": 0, "bottom": 300}, {"title": "How it broke", "top": 300, "bottom": 900}]
        clean = {"errors": [], "figures": [], "parts": parts}
        fake = {"FAKE_BROWSER_LOG": str(w / "runs.jsonl"), "FAKE_BROWSER_PICTURE": "1"}
        args = [str(w / "page.html"), "--chrome", str(browser)]
        self.assertEqual(self.run_script("check_page.py", *args, "--shots", str(w / "shots"), env=self.env(**fake, FAKE_BROWSER_PROBE=json.dumps(clean)))[0], 0)
        self.assertEqual(self.run_script("check_page.py", *args, env=self.env(**fake, FAKE_BROWSER_PROBE=json.dumps({**clean, "errors": ["boom"]})))[0], 1)
        self.assertEqual(self.events(), [
            {"event": "page_check", "outcome": "clean", "parts": 2, "findings": 0, "shots": 4},
            {"event": "page_check", "outcome": "findings", "parts": 2, "findings": 1, "shots": 0},
        ])

    def test_a_run_that_stops_on_unusable_input_records_nothing(self):
        w = self.work
        runs = [
            self.run_script("check_report.py", str(w / "absent.md")),
            self.run_script("check_question.py", stdin=b"not json"),
            self.run_script("check_question.py", "--hook", stdin=b"not json"),
            self.records("ledger", "find", "--question", "?!"),
            self.run_script("records.py", "ledger", "capture", "--hook", stdin=b"not json"),
            self.run_script("check_cold_read.py", "--report", str(w / "absent.md"), "--questions", str(w / "cold-questions.json"), "--answers", str(w / "cold-answers.json")),
            self.run_script("build_page.py", "--body", str(w / "absent.html"), "--cues", str(w / "cues.json"), "--report", str(FIXTURES / "report.md"), "--out", str(w / "page.html")),
            self.run_script("voice_cues.py", str(w / "story.txt"), str(w / "out.wav"), str(w / "out.json")),
            self.run_script("check_page.py", str(w / "absent.html"), "--chrome", str(w / "no-browser")),
        ]
        self.assertEqual([code for code, _, _ in runs], [2, 2, 0, 2, 0, 2, 2, 2, 2])
        self.assertEqual(self.events(), [])

    def test_reader_add_turns_is_stored_and_bounded(self):
        for turns in ("1", "3"):
            self.assertEqual(self.records("reader", "add", "--topic", "t", "--basis", "b", "--turns", turns)[0], 0)
        for turns in ("0", "4", "two"):
            self.assertEqual(self.records("reader", "add", "--topic", "t", "--basis", "b", "--turns", turns)[0], 2)
        stored = [json.loads(line) for line in (self.work / "reader.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual([record["turns"] for record in stored], [1, 3])
        self.assertEqual([event["turns"] for event in self.events()], [1, 3])
        self.assertIn("turns: 3", self.records("reader", "show")[1].decode("utf-8"))


class SameOutput(Workspace):
    def outputs(self):
        self.make_inputs()
        return self.all_runs()

    def test_every_script_prints_and_exits_the_same_with_the_journal_on_off_or_unwritable(self):
        off = self.outputs()
        self.turn_on()
        on = self.outputs()
        self.assertEqual(len(self.events()), 14)
        (self.journal_dir / fb.JOURNAL_FILE).unlink()
        (self.journal_dir / fb.JOURNAL_FILE).mkdir()
        unwritable = self.outputs()
        self.assertEqual(on, off)
        self.assertEqual(unwritable, off)
        self.assertEqual([code for code, _, _ in off], [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 3])


class Summary(unittest.TestCase):
    MANIFEST = {"version": "6.0.0", "repository": "https://example.org/owner/repo/"}
    JOURNAL = [
        ("2026-11-01", "5.9.0", "report", {"profile": "operator", "errors": 0, "warnings": 2, "codes": {"LENGTH": 1, "STORY-SENTENCE": 1}}),
        ("2026-11-01", "5.9.0", "report", {"profile": "operator", "errors": 1, "warnings": 1, "codes": {"ANCHOR": 1, "STORY-SENTENCE": 1}}),
        ("2026-11-02", "6.0.0", "report", {"profile": "client", "errors": 2, "warnings": 0,
                                           "codes": {"DATE": 1, "PATH": 1, "EFFORT": 1, "AS-AGREED": 1, "NUMBERS": 1, "ANCHOR": 1}}),
        ("2026-11-02", "6.0.0", "card", {"mode": "hook", "outcome": "passed", "questions": 1, "candidates": 0}),
        ("2026-11-02", "6.0.0", "card", {"mode": "file", "outcome": "form", "questions": 2, "codes": {"WHY-ASKED": 2, "FACT": 1}}),
        ("2026-11-02", "6.0.0", "card", {"mode": "hook", "outcome": "returned", "questions": 1, "candidates": 2}),
        ("2026-11-02", "6.0.0", "card", {"mode": "hook", "outcome": "resent", "questions": 1, "candidates": 2}),
        ("2026-11-02", "6.0.0", "answer", {"count": 2}),
        ("2026-11-03", "6.0.0", "answer", {"count": 1}),
        ("2026-11-03", "6.0.0", "reader_find", {"found": True}),
        ("2026-11-03", "6.0.0", "reader_find", {"found": False}),
        ("2026-11-03", "6.0.0", "reader_add", {"holds": 1, "lacks": 2, "use": "decide", "depth": "mechanism", "turns": 2}),
        ("2026-11-03", "6.0.0", "reader_add", {"holds": 0, "lacks": 0, "use": "none", "depth": "none"}),
        ("2026-11-03", "6.0.0", "ledger_find", {"found": 2}),
        ("2026-11-03", "6.0.0", "ledger_find", {"found": 0}),
        ("2026-11-03", "6.0.0", "ledger_add", {"kind": "closure"}),
        ("2026-11-03", "6.0.0", "ledger_add", {"kind": "default"}),
        ("2026-11-03", "6.0.0", "ledger_note", {}),
        ("2026-11-03", "6.0.0", "cold_read", {"questions": 3, "answered": 3, "partly": 0, "unsupported": 0, "missing": 0, "unexplained": 0, "dropped": 0}),
        ("2026-11-03", "6.0.0", "cold_read", {"questions": 3, "answered": 2, "partly": 0, "unsupported": 1, "missing": 0, "unexplained": 1, "dropped": 0}),
        ("2026-11-03", "6.0.0", "page", {"outcome": "built", "sentences": 9, "parts": 3, "decisions": 1, "look": 3, "violations": 0}),
        ("2026-11-03", "6.0.0", "page", {"outcome": "refused", "sentences": 9, "decisions": 1, "look": 3, "violations": 2}),
        ("2026-11-03", "6.0.0", "voice", {"backend": "module", "outcome": "written", "sentences": 9, "paragraphs": 3, "seconds": 40}),
        ("2026-11-03", "6.0.0", "voice", {"backend": "command", "outcome": "written", "sentences": 4, "paragraphs": 2, "seconds": 15}),
        ("2026-11-03", "6.0.0", "voice", {"backend": "command", "outcome": "failed", "paragraphs": 1}),
        ("2026-11-03", "6.0.0", "page_check", {"outcome": "clean", "parts": 4, "findings": 0, "shots": 8}),
        ("2026-11-03", "6.0.0", "page_check", {"outcome": "findings", "parts": 4, "findings": 2, "shots": 8}),
        ("2026-11-03", "6.0.0", "page_check", {"outcome": "no_browser"}),
    ]
    EXPECTED = [
        "handing-over-to-readers: usage summary",
        "plugin versions 5.9.0, 6.0.0; 3 day(s) with use; 28 event(s)",
        "reports checked: 3 (operator 2, client 1); 1 without an error; most frequent codes: ANCHOR 2, STORY-SENTENCE 2, AS-AGREED 1, DATE 1, EFFORT 1",
        "question cards: 1 passed, 1 returned for the form (WHY-ASKED 2, FACT 1), 1 returned with earlier answers, 1 sent again after a return",
        "answers recorded: 3",
        "reader lookups: 1 known, 1 unknown; intakes recorded: 2 (1 after 2 card(s), 1 without a count of cards; depth: mechanism 1, none 1)",
        "ledger: 2 lookup(s), 1 found a record; 1 closure(s), 1 default decision(s)",
        "cold reads: 1 with every question answered, 1 left a gap",
        ("pages: 1 built, 1 refused; voiced: 1 by module, 1 by command, 1 failed; 55 seconds of audio; "
         "checked in a browser: 1 clean, 1 with findings, 1 without a browser"),
        fb.HOLDS_LINE,
        "Paste this summary into the feedback form: https://example.org/owner/repo/issues/new?template=handing-over-feedback.yml",
    ]

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.journal = self.dir / fb.JOURNAL_FILE
        self.journal.write_text("".join(fb.event_line(event, fields, version, day) for day, version, event, fields in self.JOURNAL), encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_the_summary_line_by_line(self):
        lines = fb.summary_lines(fb.read_events(self.dir), self.MANIFEST)
        self.assertEqual(lines, self.EXPECTED)
        self.assertIsNone(DATE.search("\n".join(lines)))

    def test_the_page_line_names_the_browser_checks_only_when_one_ran(self):
        pages = {"page": [{"outcome": "built"}], "voice": []}
        self.assertEqual("pages: 1 built, 0 refused; voiced: 0 by module, 0 by command; 0 seconds of audio", fb.page_line(pages))

    def test_without_a_repository_the_last_line_names_the_form_without_an_address(self):
        for manifest in ({"version": "6.0.0"}, {"repository": 7}, {"repository": "not an address"}, {}):
            self.assertEqual(fb.summary_lines(fb.read_events(self.dir), manifest)[-1], "Paste this summary into the feedback form of the plugin's repository.")

    def test_an_empty_or_absent_journal_is_one_line_and_the_closing_lines(self):
        self.journal.write_text("", encoding="utf-8")
        empty = fb.summary_lines(fb.read_events(self.dir), self.MANIFEST)
        self.journal.unlink()
        absent = fb.summary_lines(fb.read_events(self.dir), {})
        self.assertEqual(empty, ["handing-over-to-readers: the usage journal holds no event.", *self.EXPECTED[-2:]])
        self.assertEqual(absent, ["handing-over-to-readers: the usage journal holds no event.", fb.HOLDS_LINE,
                                  "Paste this summary into the feedback form of the plugin's repository."])

    def test_a_journal_line_outside_the_schema_is_skipped(self):
        foreign = [
            {"day": "2026-11-04", "version": "6.0.0", "event": "answer", "count": 1, "note": "the operator's question"},
            {"day": "2026-11-04T10:00", "version": "6.0.0", "event": "answer", "count": 1},
            {"day": "2026-11-04", "version": "6.0.0 with text", "event": "answer", "count": 1},
            {"day": "2026-11-04", "version": "6.0.0", "event": "report", "codes": {"a path/in/a/code": 1}},
            {"version": "6.0.0", "event": "answer", "count": 1},
        ]
        with self.journal.open("a", encoding="utf-8") as handle:
            handle.write("not json\n[1]\n" + "".join(json.dumps(line) + "\n" for line in foreign))
        self.assertEqual(fb.summary_lines(fb.read_events(self.dir), self.MANIFEST), self.EXPECTED)

    def test_the_command_prints_the_summary_with_the_plugin_manifest(self):
        manifest = fb.read_manifest(fb.MANIFEST)
        done = subprocess.run([sys.executable, "-I", str(SCRIPTS / "feedback.py"), "summary"], capture_output=True, text=True, encoding="utf-8",
                              env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HANDOVER_FEEDBACK_DIR": str(self.dir)})
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        self.assertEqual(done.stdout.splitlines(), fb.summary_lines(fb.read_events(self.dir), manifest))
        self.assertEqual(done.stdout.splitlines()[-1], f"Paste this summary into the feedback form: {manifest['repository'].rstrip('/')}{fb.FORM_PATH}")


if __name__ == "__main__":
    unittest.main()
