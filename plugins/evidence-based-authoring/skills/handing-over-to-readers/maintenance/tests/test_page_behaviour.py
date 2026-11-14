"""The built page's behaviour in a browser: the pause beside the reader, the comments on the text, the part list
of a long page and the questions after a part.

Each class builds one standalone page, adds the scripted reader fixtures/page/behaviour.js to it with the name of
the scenario it plays, and runs it once in headless Chrome; each test checks one thing the reader saw. Without a
Chrome binary the tests are skipped with the reason.
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
OPENING = " ".join(c["text"] for c in ALL_CUES if c["paragraph"] == 1)
FIELDLESS_BODY = f'<section class="look"></section>\n<h1>Fresh thumbnails</h1>\n<p data-say>{OPENING}</p>\n'
# The example body with a question closing each of its parts "How it broke" and "What is left"; a question is not spoken,
# so the story and its cues stay the example's.
QUESTION = '<figure class="quiz"><details class="q"><summary>{}</summary><p class="answer">{}</p></details></figure>\n'
FIRST_QUESTION = ("A picture is uploaded a third time. Under which key is its thumbnail stored?",
                  "Under the key with version three, because the version grows with every upload.")
SECOND_QUESTION = ("Who still reads a thumbnail cached under the old key?",
                   "Nobody: the entry stays until it expires, up to a day after it was written.")
QUIZ_BODY = (EXAMPLE_BODY.read_text(encoding="utf-8")
             .replace('<h2 data-part="What is left.">', QUESTION.format(*FIRST_QUESTION) + '<h2 data-part="What is left.">')
             .replace('<h2 data-part="What to decide.">', QUESTION.format(*SECOND_QUESTION) + '<h2 data-part="What to decide.">'))
STEP_NAMES = ("two", "three", "four", "five", "six", "seven")


def steps_body(parts: int) -> str:
    """A body of `parts` parts: an opening and parts - 1 headed parts of one sentence each."""
    headed = "".join(f'<h2 data-part="Step {name}.">Step {name}</h2>\n<p data-say>This is what happens in step {name}.</p>\n'
                     for name in STEP_NAMES[:parts - 1])
    return '<h1>The steps of the work</h1>\n<p data-say>The work runs in several steps.</p>\n' + headed


def timed_cues(body: str) -> tuple[dict, ...]:
    """A cue for every sentence of the body, in speech order, two seconds apart."""
    sentences = bp.Story(bp.BodyScan(body), bp.load_splitter()).sentences()
    return tuple({"paragraph": s.part, "sentence": s.number, "text": s.text, "start": 2.0 * i, "end": 2.0 * i + 1.5}
                 for i, s in enumerate(sentences))


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
    """Builds BODY into a standalone page, runs the SCENARIO of behaviour.js on it once, and keeps what it saw in `seen`.
    CUES None builds a silent page."""
    BODY = ""
    CUES: tuple[dict, ...] | None = None
    ARGS: tuple[str, ...] = ()
    SCENARIO = ""

    @classmethod
    def setUpClass(cls):
        work = tempfile.TemporaryDirectory(prefix="page-behaviour-")
        cls.addClassCleanup(work.cleanup)
        folder = Path(work.name)
        config = folder / "config"
        config.mkdir()
        (folder / "body.html").write_text(cls.BODY, encoding="utf-8")
        page = folder / "page.html"
        argv = ["--body", str(folder / "body.html"), "--report", str(FIXTURES / "report.md"), "--out", str(page), "--standalone", *cls.ARGS]
        if cls.CUES is not None:
            (folder / "cues.json").write_text(json.dumps(list(cls.CUES)), encoding="utf-8")
            argv += ["--cues", str(folder / "cues.json")]
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = bp.main(argv, {"XDG_CONFIG_HOME": str(config), "HOME": str(folder)})
        if code != 0:
            raise AssertionError(f"build_page exit {code}: {err.getvalue()}")
        harness = (FIXTURES / "behaviour.js").read_text(encoding="utf-8")
        reader = f"<script>window.behaviourScenario = {json.dumps(cls.SCENARIO)};</script>\n<script>{harness}</script>\n</body>"
        page.write_text(page.read_text(encoding="utf-8").replace("</body>", reader), encoding="utf-8")
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
    SCENARIO = "voiced"

    def test_four_parts_keep_their_buttons_open_without_a_control(self):
        self.assertEqual((False, False, 4), (self.seen["partsToggleExists"], self.seen["partListHidden"], self.seen["partButtons"]))

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

    def test_the_now_line_names_a_part_after_the_opening_by_its_number_and_the_count(self):
        self.assertEqual("Part 2/4: How it broke", self.seen["nowPart"])

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
    SCENARIO = "silent"

    def test_the_answer_bar_shows_after_a_comment_before_where_to_look(self):
        self.assertEqual((True, True, True), (self.seen["barHiddenBefore"], self.seen["barShownAfter"], self.seen["barBeforeLook"]))

    def test_a_selection_opens_the_window_and_enter_keeps_the_comment(self):
        self.assertEqual((True, True, True, 1), (self.seen["popShown"], self.seen["focusInPop"], self.seen["popClosed"], self.seen["listed"]))

    def test_the_copied_text_is_the_comment_line(self):
        self.assertEqual("On the text “That is fixed” (Opening): a comment without voice", self.seen["composed"])

    def test_without_voice_there_is_no_side_group_and_the_hint_names_the_selection_only(self):
        self.assertEqual((False, self.strings["hintNote"]), (self.seen["sideExists"], self.seen["hint"]))


class ManyParts(Reader):
    BODY = steps_body(7)
    CUES = timed_cues(BODY)
    ARGS = ("--voice", "story.wav")
    SCENARIO = "parts"

    def closed(self):
        return {"hidden": True, "expanded": "false"}

    def test_every_part_has_its_button(self):
        self.assertEqual(7, self.seen["partButtons"])

    def test_the_list_starts_closed_behind_a_control_that_is_not_expanded(self):
        self.assertEqual(self.closed(), self.seen["atStart"])

    def test_the_control_stands_before_the_list_names_it_and_is_labelled_from_the_strings(self):
        self.assertEqual((self.strings["parts"], "parts", True),
                         (self.seen["toggleText"], self.seen["toggleControls"], self.seen["toggleBeforeList"]))

    def test_a_click_on_the_control_opens_the_list(self):
        self.assertEqual({"hidden": False, "expanded": "true"}, self.seen["afterOpen"])

    def test_choosing_a_part_closes_the_list_and_starts_that_part(self):
        start = next(c["start"] for c in self.CUES if (c["paragraph"], c["sentence"]) == (4, 1))
        self.assertEqual(self.closed(), self.seen["afterChoice"])
        self.assertTrue(self.seen["playingAfterChoice"])
        self.assertAlmostEqual(start - 0.05, self.seen["timeAfterChoice"], places=3)

    def test_escape_closes_the_list(self):
        self.assertEqual(self.closed(), self.seen["afterEscape"])

    def test_a_click_elsewhere_closes_the_list(self):
        self.assertEqual(self.closed(), self.seen["afterClickElsewhere"])


class SixParts(Reader):
    """The bound: six parts still stand open."""
    BODY = steps_body(6)
    CUES = timed_cues(BODY)
    ARGS = ("--voice", "story.wav")
    SCENARIO = "observe"

    def test_six_parts_keep_their_buttons_open_without_a_control(self):
        self.assertEqual((False, False, 6), (self.seen["partsToggleExists"], self.seen["partListHidden"], self.seen["partButtons"]))


class Quiz(Reader):
    BODY = QUIZ_BODY
    CUES = ALL_CUES
    ARGS = ("--voice", "story.wav")
    SCENARIO = "quiz"

    def returns(self, *parts):
        return {"hidden": not parts, "lead": self.strings["returnTo"], "parts": list(parts)}

    def test_a_closed_answer_has_no_marks(self):
        self.assertEqual(0, self.seen["marksWhileClosed"])

    def test_an_opened_answer_has_the_two_marks_from_the_strings_neither_pressed(self):
        self.assertEqual([self.strings["knew"], self.strings["missed"]], self.seen["markLabels"])
        self.assertEqual(["false", "false"], self.seen["pressedAtOpen"])

    def test_the_list_of_parts_to_return_to_is_hidden_while_no_question_is_missed(self):
        self.assertEqual(self.returns(), self.seen["returnsBefore"])

    def test_missed_lists_the_part_of_its_question_under_the_string(self):
        self.assertEqual(["false", "true"], self.seen["pressedAfterMissed"])
        self.assertEqual(self.returns("How it broke"), self.seen["returnsAfterMissed"])

    def test_knew_after_missed_clears_it_and_empties_the_list(self):
        self.assertEqual(["true", "false"], self.seen["pressedAfterKnew"])
        self.assertEqual(self.returns(), self.seen["returnsAfterKnew"])

    def test_the_list_names_the_part_of_each_question_marked_missed(self):
        self.assertEqual(self.returns("What is left"), self.seen["returnsAtEnd"])

    def test_a_click_on_a_question_its_answer_or_its_marks_leaves_the_voice_as_it_was(self):
        self.assertTrue(self.seen["openedByClick"], "the click on the question opened its answer")
        self.assertEqual({"playingAfterQuestion": True, "playingAfterAnswer": True, "pausedAfterAnswer": True, "pausedAfterMark": True},
                         {key: self.seen[key] for key in ("playingAfterQuestion", "playingAfterAnswer", "pausedAfterAnswer", "pausedAfterMark")})

    def test_no_count_of_answers_appears_on_the_page(self):
        self.assertEqual((True, []), (self.seen["articleDigitsKept"], self.seen["quizDigits"]))

    def test_a_comment_on_a_piece_of_an_answer_opens_its_window_and_is_kept(self):
        self.assertEqual((True, SECOND_QUESTION[1][:9], 1),
                         (self.seen["answerPopShown"], self.seen["answerQuote"], self.seen["answerNoteListed"]))

    def test_the_copied_answer_holds_the_words_and_the_comment_and_no_mark(self):
        self.assertEqual(["Opening: words on the opening", f"On the text “{SECOND_QUESTION[1][:9]}” (What is left): a comment in an answer"],
                         self.seen["composed"].splitlines())

    def test_the_stored_answer_holds_no_mark(self):
        stored = json.loads(self.seen["storedAnswer"])
        self.assertEqual({"choices", "words", "remarks", "notes", "text", "savedAt"}, set(stored))
        kept = json.dumps(stored, ensure_ascii=False)
        self.assertEqual([], [word for word in ("knew", "missed", FIRST_QUESTION[0], SECOND_QUESTION[0]) if word in kept])

    def test_the_marks_stay_in_the_browser_under_a_key_of_their_own(self):
        self.assertEqual([FIRST_QUESTION[0], SECOND_QUESTION[0]], self.seen["questionTexts"])
        self.assertEqual({FIRST_QUESTION[0]: "knew", SECOND_QUESTION[0]: "missed"}, self.seen["storedMarks"])


del Reader  # the base runs no page of its own

if __name__ == "__main__":
    unittest.main()
