"""The built page's behaviour in a browser: the pause beside the reader and the comments on the text.

Each class builds one standalone page, adds the scripted reader fixtures/page/behaviour.js to it and
runs it once in headless Chrome; each test checks one thing the reader saw. Without a Chrome binary
the tests are skipped with the reason.
"""
import contextlib
import html
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[2]
SCRIPT = SKILL / "scripts/build_page.py"
spec = importlib.util.spec_from_file_location("build_page", SCRIPT)
bp = importlib.util.module_from_spec(spec)
sys.modules["build_page"] = bp
spec.loader.exec_module(bp)

FIXTURES = Path(__file__).resolve().parent / "fixtures/page"
EXAMPLE_BODY = SKILL / "assets/page-body-example.html"
MAC_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
CHROME_NAMES = ("google-chrome", "chromium", "chromium-browser")
ALL_CUES = tuple(json.loads((FIXTURES / "cues.json").read_text(encoding="utf-8")))
OUTPUT = re.compile(r'<pre id="behaviour-out">(.*?)</pre>', re.S)
# A body without a decision whose every top-level element follows a "Where to look" section: the page finds no part to
# give a words field, so comments are the only answer it takes.
FIELDLESS_BODY = '<section class="look"></section>\n<h1>Fresh thumbnails</h1>\n<p data-say="1.1 1.2 1.3 1.4 1.5"></p>\n'


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


def find_chrome() -> str | None:
    """$CHROME, then the macOS application, then the first of CHROME_NAMES on PATH."""
    named = os.environ.get("CHROME")
    if named:
        return named
    if MAC_CHROME.is_file():
        return str(MAC_CHROME)
    for name in CHROME_NAMES:
        found = shutil.which(name)
        if found:
            return found
    return None


CHROME = find_chrome()


@unittest.skipIf(CHROME is None, "no Chrome: set $CHROME or install google-chrome, chromium or chromium-browser")
class Reader(unittest.TestCase):
    """Builds BODY into a standalone page, runs behaviour.js on it once, and keeps what it saw in `seen`."""
    BODY = ""
    CUES = tuple(c for c in ALL_CUES if c["paragraph"] == 1)
    ARGS: tuple[str, ...] = ()

    @classmethod
    def setUpClass(cls):
        work = tempfile.TemporaryDirectory(prefix="page-behaviour-")
        cls.addClassCleanup(work.cleanup)
        folder = Path(work.name)
        config = folder / "config"
        config.mkdir()
        (folder / "body.html").write_text(cls.BODY, encoding="utf-8")
        (folder / "cues.json").write_text(json.dumps(list(cls.CUES)), encoding="utf-8")
        page = folder / "page.html"
        argv = ["--body", str(folder / "body.html"), "--cues", str(folder / "cues.json"), "--report", str(FIXTURES / "report.md"),
                "--out", str(page), "--standalone", *cls.ARGS]
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = bp.main(argv, {"XDG_CONFIG_HOME": str(config), "HOME": str(folder)})
        if code != 0:
            raise AssertionError(f"build_page exit {code}: {err.getvalue()}")
        harness = (FIXTURES / "behaviour.js").read_text(encoding="utf-8")
        page.write_text(page.read_text(encoding="utf-8").replace("</body>", f"<script>{harness}</script>\n</body>"), encoding="utf-8")
        done = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                               f"--user-data-dir={folder / 'profile'}", "--window-size=1000,1400", "--virtual-time-budget=6000",
                               "--dump-dom", page.as_uri()], capture_output=True, text=True, timeout=120)
        found = OUTPUT.search(done.stdout)
        if not found:
            raise AssertionError(f"the page wrote no output; Chrome exit {done.returncode}: {done.stderr[-2000:]}")
        cls.seen = json.loads(html.unescape(found.group(1)))
        cls.strings = bp.STRINGS

    def setUp(self):
        self.assertNotIn("error", self.seen, self.seen.get("error"))


class VoicedPage(Reader):
    BODY = EXAMPLE_BODY.read_text(encoding="utf-8")
    CUES = ALL_CUES
    ARGS = ("--voice", "story.wav", "--root", str(FIXTURES / "repo"))

    def note_lines(self):
        prefix = self.strings["noteLine"].split("{quote}")[0]
        return [line for line in self.seen["composed"].splitlines() if line.startswith(prefix)]

    def test_a_selection_opens_the_window_with_the_cursor_in_its_field(self):
        self.assertEqual((True, True, "load test was not run"), (self.seen["popShown"], self.seen["focusInPop"], self.seen["quote"]))

    def test_enter_saves_marks_the_piece_and_lists_one_comment(self):
        self.assertEqual((True, True, 1), (self.seen["popClosed"], self.seen["highlight"], self.seen["listed"]))

    def test_a_click_on_the_text_pauses_and_space_resumes(self):
        self.assertEqual("2.3", self.seen["lit"])
        self.assertEqual((True, True), (self.seen["pausedByClick"], self.seen["resumedBySpace"]))

    def test_the_side_group_stands_beside_the_spoken_sentence_and_there_is_no_corner_button(self):
        self.assertTrue(self.seen["sideShown"])
        self.assertLessEqual(self.seen["sideOffset"], 2, "the pause button is centred on the spoken sentence's first line")
        self.assertTrue(self.seen["sideLeftOfText"])
        self.assertFalse(self.seen["cornerExists"])

    def test_the_pause_button_is_labelled_from_the_strings(self):
        self.assertEqual((self.strings["pause"], self.strings["resume"]), (self.seen["labelPlaying"], self.seen["labelPaused"]))

    def test_the_key_c_opens_the_window_for_the_spoken_sentence_and_pauses(self):
        self.assertEqual((True, True), (self.seen["popForSpoken"], self.seen["pausedForNote"]))
        self.assertEqual("So the cache answered with the thumbnail of the old file.", self.seen["spokenQuote"])

    def test_after_enter_the_voice_goes_on_from_the_start_of_the_interrupted_sentence(self):
        self.assertTrue(self.seen["resumedAfterNote"])
        self.assertAlmostEqual(32.55, self.seen["timeAfterNote"], places=3)  # sentence 2.5 starts at 32.6

    def test_a_comment_opened_while_paused_leaves_the_voice_paused(self):
        self.assertEqual((True, True), (self.seen["pausedPopShown"], self.seen["stillPausedAfterNote"]))

    def test_escape_closes_without_saving(self):
        self.assertEqual((True, True, 3, True), (self.seen["escapePopShown"], self.seen["escapeClosed"],
                                                 self.seen["notesAfterEscape"], self.seen["stillPausedAfterEscape"]))

    def test_a_click_on_a_commented_piece_opens_it_with_its_text(self):
        self.assertEqual((True, "first comment"), (self.seen["editOpens"], self.seen["editText"]))

    def test_focusing_a_part_words_field_pauses_the_voice(self):
        self.assertTrue(self.seen["pausedByField"])

    def test_the_copied_text_ends_with_the_comment_lines_in_page_order(self):
        lines = self.seen["composed"].splitlines()
        self.assertEqual("Opening: words on the opening", lines[0])
        self.assertEqual(["On the text “So the cache answered with the thumbnail of the old file.” (How it broke): second comment",
                          "On the text “Thumbnails cached before the change still sit under the old keys.” (What is left): third comment",
                          "On the text “load test was not run” (What is left): first comment"], lines[1:])
        self.assertEqual(lines[1:], self.note_lines())

    def test_the_stored_answer_holds_the_comments(self):
        notes = self.seen["storedNotes"]
        self.assertEqual(["second comment", "third comment", "first comment"], [n["text"] for n in notes])
        self.assertEqual({"sb", "so", "eb", "eo", "quote", "part", "text"}, set(notes[0]))

    def test_the_hint_names_the_pause_and_both_ways_to_comment(self):
        self.assertEqual(" ".join(self.strings[k] for k in ("hintPause", "hintNote", "hintNoteSpoken")), self.seen["hint"])


class FieldlessPageWithoutVoice(Reader):
    BODY = FIELDLESS_BODY

    def test_the_answer_bar_shows_after_a_comment_before_where_to_look(self):
        self.assertEqual((True, True, True), (self.seen["barHiddenBefore"], self.seen["barShownAfter"], self.seen["barBeforeLook"]))

    def test_a_selection_opens_the_window_and_enter_keeps_the_comment(self):
        self.assertEqual((True, True, True, 1), (self.seen["popShown"], self.seen["focusInPop"], self.seen["popClosed"], self.seen["listed"]))

    def test_the_copied_text_is_the_comment_line(self):
        self.assertEqual("On the text “That is fixed” (Opening): a comment without voice", self.seen["composed"])

    def test_without_voice_there_is_no_side_group_and_the_hint_names_the_selection_only(self):
        self.assertEqual((False, self.strings["hintNote"]), (self.seen["sideExists"], self.seen["hint"]))


del Reader  # the base runs no page of its own

if __name__ == "__main__":
    unittest.main()
