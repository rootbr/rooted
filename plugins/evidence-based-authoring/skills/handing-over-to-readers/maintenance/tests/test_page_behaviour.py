"""The built page's behaviour in a browser: the voice started part by part, the tools of a selection and the comments
made from them, the questions after a part, the map of an explanation and the references that open in place.

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
from urllib.parse import quote

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
# The example body as an explanation: its first part "How it broke" holds the pseudocode, and a question closes each of
# its parts "How it broke" and "What is left". Neither figure is spoken, so the story and its cues stay the example's.
PSEUDOCODE = ('<figure class="pseudo" data-nav="The rule of the key"><pre>key = "thumb:" + picture number + ":v" + version\n'
              'version grows with every upload</pre></figure>\n')
QUESTION = '<figure class="quiz"><details class="q"><summary>{}</summary><p class="answer">{}</p></details></figure>\n'
FIRST_QUESTION = ("A picture is uploaded a third time. Under which key is its thumbnail stored?",
                  "Under the key with version three, because the version grows with every upload.")
SECOND_QUESTION = ("Who still reads a thumbnail cached under the old key?",
                   "Nobody: the entry stays until it expires, up to a day after it was written.")
QUIZ_BODY = (EXAMPLE_BODY.read_text(encoding="utf-8")
             .replace('<figure aria-labelledby="h-broke">', '<figure aria-labelledby="h-broke" data-nav="The key before and now">')
             .replace('<h2 data-part="What is left.">', PSEUDOCODE + QUESTION.format(*FIRST_QUESTION) + '<h2 data-part="What is left.">')
             .replace('<h2 data-part="What to decide.">', QUESTION.format(*SECOND_QUESTION) + '<h2 data-part="What to decide.">'))
# An explanation whose first part "The whole mechanism" holds the pseudocode: its line lit on sentence 2.3 opens with
# key(picture), and its last line ends in a link to the part "A miss".
EXPLANATION_BODY = (FIXTURES / "explanation-body.html").read_text(encoding="utf-8")
# The explanation with two references: the pseudocode's key line names the method that builds the key, and a paragraph
# of "A miss" names the source of the idea.
KEY_LINE_END = '":v" + picture.version</span>'
SOURCE_PARAGRAPH = '<p>The version in the key is a <span data-ref="generation">generation number</span>.</p>\n'
REFS_BODY = (EXPLANATION_BODY
             .replace(KEY_LINE_END, KEY_LINE_END + '<span class="by" data-ref="key-value">ThumbKey.value</span>')
             .replace('<figure class="factor wide"', SOURCE_PARAGRAPH + '<figure class="factor wide"'))
THUMB_KEY = FIXTURES / "repo/src/cache/ThumbKey.java"
EDITOR_URL = "vscode://file{path}:{line}"


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
    """Builds BODY into a standalone page, runs the SCENARIO of behaviour.js on it once in a window of WINDOW pixels, and
    keeps what it saw in `seen`. CUES None builds a silent page."""
    BODY = ""
    CUES: tuple[dict, ...] | None = None
    ARGS: tuple[str, ...] = ()
    SCENARIO = ""
    WINDOW = (1000, 1400)

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
        width, height = cls.WINDOW
        done = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
                               f"--user-data-dir={folder / 'profile'}", f"--window-size={width},{height}", "--virtual-time-budget=8000",
                               "--dump-dom", page.as_uri()], capture_output=True, text=True, timeout=120)
        found = OUTPUT.search(done.stdout)
        if not found:
            raise AssertionError(f"the page wrote no output; Chrome exit {done.returncode}: {done.stderr[-2000:]}")
        cls.seen = json.loads(html.unescape(found.group(1)))
        cls.strings = bp.STRINGS

    def setUp(self):
        self.assertNotIn("error", self.seen, self.seen.get("error"))

    def note_lines(self):
        prefix = self.strings["noteLine"].split("{quote}")[0]
        return [line for line in self.seen["composed"].splitlines() if line.startswith(prefix)]


class VoiceByPart(Reader):
    BODY = EXAMPLE_BODY.read_text(encoding="utf-8")
    CUES = ALL_CUES
    ARGS = ("--voice", "story.wav", "--root", str(FIXTURES / "repo"))
    SCENARIO = "voice"

    def button(self, label, *, playing=False, marked_next=False):
        return {"label": label, "playing": playing, "next": marked_next}

    def test_each_part_has_its_button_at_the_end_of_its_heading_labelled_from_the_strings(self):
        titles = ("Opening", "How it broke", "What is left", "What to decide")
        self.assertEqual([{"in": tag, "label": self.strings["playPart"], "name": f"{self.strings['playPart']}: {title}", "text": ""}
                          for tag, title in zip(("h1", "h2", "h2", "h2"), titles, strict=True)], self.seen["partButtons"])

    def test_the_page_has_no_player_no_side_group_no_audio_controls_and_no_map(self):
        self.assertEqual((False, False, False, False, False), (self.seen["playerExists"], self.seen["sideExists"], self.seen["audioControls"],
                                                               self.seen["mapExists"], self.seen["noAudioShown"]))

    def test_nothing_starts_the_voice_at_load_and_space_before_the_first_start_is_left_to_the_browser(self):
        self.assertEqual((0, False, True), (self.seen["playsAtLoad"], self.seen["earlySpacePrevented"], self.seen["pausedAfterEarlySpace"]))

    def test_a_part_button_plays_its_part_from_just_before_its_first_sentence(self):
        self.assertTrue(self.seen["playingAfterPress"])
        self.assertAlmostEqual(22.45, self.seen["timeAfterPress"], places=3)  # sentence 2.1 starts at 22.5
        self.assertEqual(self.button(self.strings["pause"], playing=True), self.seen["secondWhilePlaying"])
        self.assertEqual(f"{self.strings['pause']}: How it broke", self.seen["secondNameWhilePlaying"])

    def test_a_click_on_the_text_and_the_key_c_leave_the_voice_running_and_open_no_window(self):
        self.assertEqual((True, False, True), (self.seen["playingAfterTextClick"], self.seen["popAfterC"], self.seen["playingAfterC"]))

    def test_the_voice_stops_where_the_next_part_starts_and_marks_its_button(self):
        self.assertTrue(self.seen["pausedAtEnd"])
        self.assertAlmostEqual(42.45, self.seen["timeAtEnd"], places=3)  # sentence 3.1 starts at 42.45
        self.assertEqual(self.button(self.strings["playPart"]), self.seen["secondAfterEnd"])
        self.assertEqual(self.button(self.strings["playNext"], marked_next=True), self.seen["thirdAfterEnd"])

    def test_after_the_first_start_space_is_taken_and_speaks_the_next_part(self):
        self.assertEqual((True, True), (self.seen["lateSpacePrevented"], self.seen["playingAfterSpace"]))
        self.assertEqual(self.button(self.strings["pause"], playing=True), self.seen["thirdAfterSpace"])

    def test_the_button_of_the_part_being_spoken_pauses_and_resumes_it_where_it_was(self):
        self.assertTrue(self.seen["pausedByButton"])
        self.assertEqual(self.button(self.strings["resume"]), self.seen["thirdWhilePaused"])
        self.assertTrue(self.seen["resumedByButton"])
        self.assertAlmostEqual(42.45, self.seen["timeAfterResume"], places=3)

    def test_space_pauses_and_another_part_button_moves_the_voice_to_its_part(self):
        self.assertTrue(self.seen["pausedBySpace"])
        self.assertTrue(self.seen["playingAfterOther"])
        self.assertAlmostEqual(22.45, self.seen["timeAfterOther"], places=3)
        self.assertEqual((self.button(self.strings["pause"], playing=True), self.button(self.strings["playPart"])),
                         (self.seen["otherWhilePlaying"], self.seen["thirdAfterOther"]))

    def test_a_comment_pauses_the_voice_and_after_enter_it_goes_on_from_the_start_of_the_interrupted_sentence(self):
        self.assertEqual((True, True), (self.seen["pausedForNote"], self.seen["resumedAfterNote"]))
        self.assertAlmostEqual(32.55, self.seen["timeAfterNote"], places=3)  # sentence 2.5 starts at 32.6

    def test_focusing_a_part_words_field_pauses_the_voice(self):
        self.assertTrue(self.seen["pausedByField"])


class SelectionTools(Reader):
    BODY = EXAMPLE_BODY.read_text(encoding="utf-8")
    CUES = ALL_CUES
    ARGS = ("--voice", "story.wav", "--root", str(FIXTURES / "repo"))
    SCENARIO = "selection"

    def test_a_selection_shows_the_toolbar_labelled_from_the_strings_and_no_comment_window(self):
        self.assertEqual((True, False), (self.seen["toolsShown"], self.seen["popAfterSelect"]))
        self.assertEqual(("toolbar", self.strings["selectionTools"], [self.strings["copySelection"], self.strings["comment"]]),
                         (self.seen["toolsRole"], self.seen["toolsLabel"], self.seen["toolsButtons"]))

    def test_the_toolbar_stands_above_the_selection_and_covers_none_of_it(self):
        self.assertEqual((True, False), (self.seen["toolsAboveFirstLine"], self.seen["toolsCoverText"]))

    def test_at_the_top_of_the_window_the_toolbar_stands_under_the_selection(self):
        self.assertTrue(self.seen["toolsUnderLastLine"])

    def test_the_copy_button_and_nothing_before_it_writes_the_selected_text_to_the_clipboard(self):
        self.assertEqual(0, self.seen["clipboardBeforeCopy"])
        self.assertEqual(["load test was not run"], self.seen["clipboardWrites"])
        self.assertEqual((self.strings["copiedSelection"], "load test was not run"), (self.seen["copyStatus"], self.seen["selectionKept"]))

    def test_a_copy_the_browser_refuses_is_said_in_the_toolbar_in_its_own_words(self):
        self.assertEqual(self.strings["copySelectionFailed"], self.seen["failedStatus"])
        self.assertNotEqual(self.strings["copyFailed"], self.strings["copySelectionFailed"])

    def test_the_comment_button_opens_the_window_on_that_piece_with_the_cursor_in_its_field(self):
        self.assertEqual((True, "load test was not run", True, True),
                         (self.seen["popShown"], self.seen["quote"], self.seen["focusInPop"], self.seen["toolsHiddenWithPop"]))

    def test_enter_saves_marks_the_piece_and_lists_one_comment(self):
        self.assertEqual((True, True, 1), (self.seen["popClosed"], self.seen["highlight"], self.seen["listed"]))

    def test_a_click_on_a_commented_piece_opens_it_with_its_text(self):
        self.assertEqual((True, "first comment"), (self.seen["editOpens"], self.seen["editText"]))

    def test_escape_and_a_collapsed_selection_hide_the_toolbar(self):
        self.assertEqual((True, True, True), (self.seen["toolsBeforeEscape"], self.seen["toolsAfterEscape"], self.seen["toolsAfterCollapse"]))

    def test_a_selection_in_the_pages_own_controls_shows_no_toolbar(self):
        self.assertFalse(self.seen["toolsOnControl"])

    def test_the_copied_answer_ends_with_the_comment_lines_in_page_order(self):
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


class FieldlessPageWithoutVoice(Reader):
    BODY = FIELDLESS_BODY
    SCENARIO = "silent"

    def test_the_answer_bar_shows_after_a_comment_before_where_to_look(self):
        self.assertEqual((True, True, True), (self.seen["barHiddenBefore"], self.seen["barShownAfter"], self.seen["barBeforeLook"]))

    def test_a_comment_from_the_toolbar_opens_the_window_and_enter_keeps_it(self):
        self.assertEqual((True, True, True, 1), (self.seen["popShown"], self.seen["focusInPop"], self.seen["popClosed"], self.seen["listed"]))

    def test_the_copied_text_is_the_comment_line(self):
        self.assertEqual("On the text “That is fixed” (Opening): a comment without voice", self.seen["composed"])

    def test_without_voice_the_page_says_so_and_has_no_part_button(self):
        self.assertEqual((True, []), (self.seen["noAudioShown"], self.seen["partButtons"]))


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


class PseudocodeComments(Reader):
    BODY = EXPLANATION_BODY
    SCENARIO = "pseudocode"

    def test_a_selection_in_a_pseudocode_line_opens_the_window_with_the_selected_text(self):
        self.assertEqual((True, True, "key(picture)"), (self.seen["linePopShown"], self.seen["lineFocusInPop"], self.seen["lineQuote"]))

    def test_the_saved_comment_carries_the_selected_text_and_the_title_of_its_part(self):
        notes = self.seen["notesAfterLine"] or []
        self.assertEqual([{"quote": "key(picture)", "part": "The whole mechanism", "text": "a comment on a line"}],
                         [{key: n[key] for key in ("quote", "part", "text")} for n in notes])

    def test_a_selection_in_a_paragraph_opens_the_window_the_same_way(self):
        self.assertEqual((True, "Without the version"), (self.seen["paragraphPopShown"], self.seen["paragraphQuote"]))

    def test_the_copied_answer_holds_the_line_of_each_comment_in_page_order(self):
        self.assertEqual(["On the text “key(picture)” (The whole mechanism): a comment on a line",
                          "On the text “Without the version” (A miss): a comment on a paragraph"],
                         self.seen["composed"].splitlines())

    def test_a_click_on_the_link_of_a_pseudocode_line_follows_it_and_opens_no_window(self):
        self.assertEqual(("#h-miss", True), (self.seen["hashAfterLink"], self.seen["popHiddenAfterLink"]))


class PageMap(Reader):
    """An explanation in a wide window, low enough that the factor table can reach a third of its height."""
    BODY = EXPLANATION_BODY
    SCENARIO = "map"
    WINDOW = (1000, 700)

    def state(self, open):
        label = self.strings["mapClose"] if open else self.strings["mapOpen"]
        return {"expanded": "true" if open else "false", "label": label, "hidden": not open}

    def test_the_map_holds_a_group_per_part_and_an_entry_per_figure_with_its_kind_and_name(self):
        s = self.strings
        quiz = "A picture is uploaded a third time. Which key does its…"
        self.assertEqual([{"title": "Opening", "entries": []},
                          {"title": "The whole mechanism", "entries": [[s["kindPseudo"], "The rule of the cache"]]},
                          {"title": "Your questions", "entries": [[s["kindTable"], "Your questions and their parts"]]},
                          {"title": "A miss", "entries": [[s["kindTable"], "The key without and with the version"],
                                                          [s["kindQuestion"], quiz], [s["kindTable"], "Terms of the cache"]]}],
                         self.seen["groups"])

    def test_the_map_is_a_navigation_named_from_the_strings_whose_links_reach_their_figures(self):
        self.assertEqual((self.strings["map"], True, True), (self.seen["navLabel"], self.seen["linksResolve"], self.seen["toggleControls"]))

    def test_a_figure_named_by_data_nav_takes_the_name_as_its_label(self):
        self.assertEqual(["The rule of the cache", "Your questions and their parts", "The key without and with the version", None,
                          "Terms of the cache"], self.seen["figureLabels"])

    def test_in_a_wide_window_the_map_starts_open_beside_the_text_without_a_filter(self):
        self.assertEqual((self.state(True), True, False), (self.seen["atStart"], self.seen["besideText"], self.seen["filterShown"]))

    def test_after_a_scroll_one_link_is_current_and_its_group_is_shown(self):
        self.assertEqual([["location", self.strings["kindTable"] + "The key without and with the version"]], self.seen["currentAfterScroll"])
        self.assertEqual(("false", "true"), (self.seen["missBeforeScroll"], self.seen["missExpanded"]))

    def test_leaving_a_part_closes_the_group_the_page_opened_and_keeps_the_one_the_reader_opened(self):
        self.assertEqual({"miss": "false", "questions": "true", "current": 1}, self.seen["afterLeaving"])

    def test_the_toggle_hides_and_shows_the_map_and_keeps_the_choice(self):
        self.assertEqual((self.state(False), "closed"), (self.seen["afterClose"], self.seen["storedAfterClose"]))
        self.assertEqual((self.state(True), "open"), (self.seen["afterOpen"], self.seen["storedAfterOpen"]))
        self.assertGreater(self.seen["textLeftOpen"], self.seen["textLeftClosed"], "the open map pushes the text")

    def test_the_block_at_the_top_keeps_its_offset_when_the_map_opens(self):
        self.assertLessEqual(abs(self.seen["offsetShift"]), 1)


class NarrowPageMap(Reader):
    BODY = EXPLANATION_BODY
    SCENARIO = "narrowMap"
    WINDOW = (500, 900)

    def closed(self):
        return {"expanded": "false", "label": self.strings["mapOpen"], "hidden": True}

    def test_below_840_pixels_the_map_starts_closed(self):
        self.assertEqual(500, self.seen["width"])
        self.assertEqual(self.closed(), self.seen["atStart"])

    def test_opened_it_lies_over_the_text_within_the_window(self):
        self.assertEqual({"expanded": "true", "label": self.strings["mapClose"], "hidden": False}, self.seen["afterOpen"])
        self.assertEqual((True, True, True), (self.seen["overText"], self.seen["pageFitsWidth"], self.seen["toggleFitsWidth"]))

    def test_a_jump_and_escape_close_it_and_hand_the_focus_to_the_toggle(self):
        self.assertEqual((self.closed(), True), (self.seen["afterJump"], self.seen["focusAfterJump"]))
        self.assertEqual((self.closed(), True), (self.seen["afterEscape"], self.seen["focusAfterEscape"]))

    def test_a_click_outside_closes_it_and_no_choice_is_kept(self):
        self.assertEqual((self.closed(), None), (self.seen["afterClickOutside"], self.seen["stored"]))


class ReferencesInPlace(Reader):
    """An explanation with its map open, in a window wide enough for the text to keep 480 px beside the map and the panel."""
    BODY = REFS_BODY
    ARGS = ("--refs", str(FIXTURES / "refs.json"), "--root", str(FIXTURES / "repo"), "--editor-url", EDITOR_URL)
    SCENARIO = "refs"
    WINDOW = (1300, 1400)

    def test_each_reference_is_a_control_of_its_panel(self):
        control = {"tabindex": "0", "role": "button", "expanded": "false", "underlined": True, "title": False}
        self.assertEqual([control, control], self.seen["controls"])

    def test_focus_shows_the_preview_with_the_place_and_the_first_lines(self):
        self.assertEqual({"shown": True, "where": "src/cache/ThumbKey.java:23", "lines": list(range(20, 30)), "hit": 23, "describedBy": True},
                         self.seen["previewOnFocus"])

    def test_escape_hides_the_preview_and_keeps_the_focus_and_leaving_the_focus_hides_it(self):
        self.assertEqual({"shown": False, "focusKept": True}, self.seen["afterEscape"])
        self.assertEqual((True, True), (self.seen["shownAgain"], self.seen["hiddenOnBlur"]))

    def test_the_pointer_shows_the_preview_of_a_source_until_a_moment_after_it_leaves(self):
        entry = json.loads((FIXTURES / "refs.json").read_text(encoding="utf-8"))["generation"]
        self.assertEqual({"shown": True, "text": entry["title"] + entry["note"]}, self.seen["sourcePreview"])
        self.assertEqual((True, True), (self.seen["shownJustAfterLeaving"], self.seen["hiddenAfterLeaving"]))

    def test_a_click_opens_the_panel_with_the_whole_excerpt_its_line_marked_and_the_editor_link(self):
        editor = "vscode://file" + quote(THUMB_KEY.resolve().as_posix()) + ":23"
        self.assertEqual({"shown": True, "label": self.strings["refPanel"], "heading": "ThumbKey.value", "where": "src/cache/ThumbKey.java:23",
                          "lines": 16, "hit": 23, "links": [[self.strings["refEditor"], editor]], "focusInPanel": True, "expanded": "true",
                          "previewShown": False}, self.seen["panel"])

    def test_where_the_text_keeps_480_pixels_the_panel_stands_beside_it_and_the_reference_keeps_its_place(self):
        beside = self.seen["beside"]
        self.assertTrue(self.seen["panelBesideText"])
        self.assertTrue(beside["mapBeside"], "the map stands open beside the text")
        self.assertLess(beside["textAfter"], beside["textBefore"], "the panel pushes the text")
        self.assertGreaterEqual(beside["textAfter"], 480)
        self.assertLessEqual(abs(beside["refShift"]), 1)

    def test_closing_the_panel_returns_the_focus_to_the_reference_without_a_preview(self):
        self.assertEqual({"hidden": True, "focusBack": True, "expanded": "false", "previewShown": False}, self.seen["afterClose"])

    def test_enter_opens_a_source_with_its_title_note_and_a_link_in_a_new_tab_and_escape_closes_it(self):
        entry = json.loads((FIXTURES / "refs.json").read_text(encoding="utf-8"))["generation"]
        self.assertEqual({"shown": True, "texts": [entry["title"], entry["note"], self.strings["refSource"]],
                          "links": [[self.strings["refSource"], entry["href"], "_blank", "noopener noreferrer"]]}, self.seen["sourcePanel"])
        self.assertEqual({"hidden": True, "focusBack": True}, self.seen["afterSourceEscape"])

    def test_space_on_a_reference_opens_its_panel(self):
        self.assertTrue(self.seen["spaceOpens"])


class ReferencesOverMappedText(Reader):
    """At 1000 px the open map leaves the text about 700 px, less than 480 once the 380 px panel stood beside it."""
    BODY = REFS_BODY
    ARGS = ("--refs", str(FIXTURES / "refs.json"), "--root", str(FIXTURES / "repo"))
    SCENARIO = "refsOver"

    def test_the_panel_lies_over_the_text_which_keeps_its_width(self):
        over = self.seen["over"]
        self.assertTrue(self.seen["mapBeside"], "the map stands open beside the text")
        self.assertEqual((True, False, True), (over["shown"], over["besideClass"], over["overText"]))
        self.assertEqual(over["textBefore"], over["textAfter"])
        self.assertLess(over["textBefore"] - 380, 480)


class ReferencesWithoutEditor(Reader):
    BODY = REFS_BODY
    ARGS = ("--refs", str(FIXTURES / "refs.json"), "--root", str(FIXTURES / "repo"))
    SCENARIO = "refsPlain"

    def test_a_code_panel_has_no_editor_link_when_the_data_has_none(self):
        self.assertEqual(0, self.seen["panelLinks"])


del Reader  # the base runs no page of its own

if __name__ == "__main__":
    unittest.main()
