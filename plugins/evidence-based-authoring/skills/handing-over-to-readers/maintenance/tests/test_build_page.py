import contextlib
import html
import importlib.util
import io
import json
import os
import re
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


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


FIXTURES = Path(__file__).resolve().parent / "fixtures/page"
REPORT = FIXTURES / "report.md"
EXAMPLE_BODY = SKILL / "assets/page-body-example.html"
# An explanation in its order: the opening, the first part with its pseudocode, a part with the table of questions,
# a part with a factor table and a question, and the table of terms at the end.
EXPLANATION = (FIXTURES / "explanation-body.html").read_text(encoding="utf-8")

# Two parts: an opening of two sentences and a part of two sentences, the first of them its heading's phrase.
CUES = [
    {"paragraph": 1, "sentence": 1, "text": "The cache served old thumbnails.", "start": 0.0, "end": 2.0},
    {"paragraph": 1, "sentence": 2, "text": "Now it does not.", "start": 2.3, "end": 3.5},
    {"paragraph": 2, "sentence": 1, "text": "How it broke.", "start": 4.1, "end": 5.0},
    {"paragraph": 2, "sentence": 2, "text": "The key had no version.", "start": 5.3, "end": 7.0},
]
BODY = ('<p data-say>The cache served old thumbnails. Now it does not.</p>\n'
        '<h2 data-part="How it broke.">How it broke</h2>\n'
        '<p data-say>The key had no version.</p>\n')
STORY = "The cache served old thumbnails. Now it does not.\n\nHow it broke. The key had no version.\n"
DECISION = ('<section class="decision" data-decision="purge" data-title="Old thumbnails">'
            '<div class="option" data-option="purge" data-mine="1"><h4>Purge</h4></div>'
            '<div class="option" data-option="wait"><h4>Wait</h4></div></section>\n')


def load_voice_cues():
    path = SKILL / "scripts/voice_cues.py"
    voice_spec = importlib.util.spec_from_file_location("voice_cues_for_tests", path)
    module = importlib.util.module_from_spec(voice_spec)
    voice_spec.loader.exec_module(module)
    return module


class Build(unittest.TestCase):
    """Each test builds in its own temporary directory, with an empty configuration directory."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.config = self.dir / "config"
        (self.config / "handing-over-to-readers").mkdir(parents=True)
        self.environ = {"XDG_CONFIG_HOME": str(self.config), "HOME": str(self.dir)}

    def tearDown(self):
        self._tmp.cleanup()

    def run_main(self, argv):
        """(exit code, stdout, stderr) of one run in this process."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            code = bp.main(argv, self.environ)
        return code, out.getvalue(), err.getvalue()

    def build(self, body=BODY, cues=CUES, report=REPORT, look=None, args=()):
        """(exit code, stderr, page text or None). cues None: a silent page; report: a path, a report's text, or None for
        none; look: a list written as JSON or a text written as it is."""
        (self.dir / "body.html").write_text(body, encoding="utf-8")
        argv = ["--body", str(self.dir / "body.html"), "--out", str(self.dir / "page.html")]
        if cues is not None:
            (self.dir / "cues.json").write_text(json.dumps(cues), encoding="utf-8")
            argv += ["--cues", str(self.dir / "cues.json")]
        if isinstance(report, str):
            (self.dir / "report.md").write_text(report, encoding="utf-8")
            report = self.dir / "report.md"
        if report is not None:
            argv += ["--report", str(report)]
        if look is not None:
            (self.dir / "look.json").write_text(look if isinstance(look, str) else json.dumps(look), encoding="utf-8")
            argv += ["--look", str(self.dir / "look.json")]
        code, _, err = self.run_main(argv + list(args))
        out = self.dir / "page.html"
        return code, err, out.read_text(encoding="utf-8") if out.exists() else None

    def relative(self, err):
        """The lines of stderr, each without the directory of this test's files."""
        return [line.replace(f"{self.dir}{os.sep}", "", 1) for line in err.splitlines()]

    def data(self, page):
        block = re.search(r'<script type="application/json" id="page-data">(.*?)</script>', page, re.S)
        return json.loads(block.group(1))

    def article(self, page):
        return page[page.index('<article class="sheet" id="article">'):page.index("</article>")]


class Expansion(Build):
    def test_a_data_say_element_is_filled_with_one_span_per_sentence_in_speech_order(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertIn('<p data-say><span class="s" data-lit="1.1">The cache served old thumbnails.</span> '
                      '<span class="s" data-lit="1.2">Now it does not.</span></p>', page)
        self.assertIn('<p data-say><span class="s" data-lit="2.2">The key had no version.</span></p>', page)

    def test_the_sentence_text_is_escaped(self):
        code, err, page = self.build('<p data-say>A &lt;b&gt; &amp; C.</p>\n', cues=None, report=None)
        self.assertEqual(0, code, err)
        self.assertIn('<span class="s" data-lit="1.1">A &lt;b&gt; &amp; C.</span>', page)
        self.assertEqual("A <b> & C.", self.data(page)["cues"][0]["text"])

    def test_a_part_heading_is_lit_by_its_own_sentence_and_keeps_no_data_part(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertIn('<h2 data-lit="2.1">How it broke</h2>', page)
        self.assertNotIn("data-part", self.article(page))

    def test_a_voiced_element_is_lit_by_its_own_sentences_and_keeps_no_data_voice(self):
        body = BODY + '<figure class="x"\n  data-voice="The figure shows it. It shows it twice."><figcaption>Keys</figcaption></figure>\n'
        code, err, page = self.build(body, cues=None, report=None)
        self.assertEqual(0, code, err)
        self.assertIn('<figure class="x" data-lit="2.3 2.4"><figcaption>Keys</figcaption></figure>', page)
        self.assertNotIn("data-voice", self.article(page))

    def test_a_rebuilt_start_tag_keeps_its_other_attributes_escaped_and_its_closing_slash(self):
        body = BODY.replace("Now it", "[@fixed] Now it") + '<svg class="fig"><rect title="a &amp; &quot;b&quot;" data-lit="@fixed" x=1 hidden/></svg>\n'
        code, err, page = self.build(body)
        self.assertEqual(0, code, err)
        self.assertIn('<svg class="fig"><rect title="a &amp; &quot;b&quot;" x="1" hidden data-lit="1.2"/></svg>', page)

    def test_a_name_mark_is_neither_on_the_page_nor_in_the_cues(self):
        code, err, page = self.build(BODY.replace("Now it", "[@fixed] Now it"), cues=None, report=None)
        self.assertEqual(0, code, err)
        self.assertNotIn("[@", page)
        self.assertEqual("Now it does not.", self.data(page)["cues"][1]["text"])


class Names(Build):
    NAMED = BODY.replace("Now it", "[@fixed] Now it") + '<figure data-lit="@fixed"><figcaption>After</figcaption></figure>\n'

    def lit_text(self, page):
        """The id that lights the figure and the text of the sentence with that id."""
        lit = re.search(r'<figure data-lit="([^"]+)">', page).group(1)
        return lit, re.search(rf'<span class="s" data-lit="{re.escape(lit)}">([^<]+)</span>', page).group(1)

    def test_an_element_with_a_name_in_data_lit_is_lit_by_that_sentence(self):
        code, err, page = self.build(self.NAMED)
        self.assertEqual(0, code, err)
        self.assertEqual(("1.2", "Now it does not."), self.lit_text(page))

    def test_after_a_sentence_is_inserted_before_it_the_same_element_is_lit_by_the_same_sentence(self):
        inserted = self.NAMED.replace("thumbnails. ", "thumbnails. It took a day. ")
        code, err, page = self.build(inserted, cues=None, report=None)
        self.assertEqual(0, code, err)
        self.assertEqual(("1.3", "Now it does not."), self.lit_text(page))

    def test_a_name_may_be_written_in_any_alphabet(self):
        body = BODY.replace("Now it", "[@сейчас_2] Now it") + '<figure data-lit="@сейчас_2"></figure>\n'
        code, err, page = self.build(body)
        self.assertEqual(0, code, err)
        self.assertIn('<figure data-lit="1.2"></figure>', page)

    def test_two_names_on_one_element_light_it_for_both_sentences(self):
        body = BODY.replace("The cache", "[@before] The cache").replace("Now it", "[@after] Now it") + '<figure data-lit="@after @before"></figure>\n'
        code, err, page = self.build(body)
        self.assertEqual(0, code, err)
        self.assertIn('<figure data-lit="1.2 1.1"></figure>', page)


class Violations(Build):
    def assertViolation(self, body, *fragments, cues=None):
        code, err, page = self.build(body, cues=cues, report=None)
        self.assertEqual(1, code, err)
        for fragment in fragments:
            self.assertIn(fragment, err)
        self.assertIsNone(page)

    def test_data_say_with_a_value_names_the_new_form(self):
        self.assertViolation('<p data-say="1.1 1.2"></p>\n', 'body.html:1: data-say="1.1 1.2" names sentences by number',
                             "write the sentences inside the element and leave data-say without a value")

    def test_a_number_in_data_lit_names_the_new_form(self):
        self.assertViolation(BODY + '<figure data-lit="2.2"></figure>\n',
                             'body.html:4: data-lit names sentence 2.2 by its number: set a mark [@name] before that sentence and write data-lit="@name"')

    def test_the_body_of_sentence_numbers_is_refused_once_per_old_reference(self):
        old = '<p data-say="1.1 1.2"></p>\n<h2 data-lit="2.1">How it broke</h2>\n<p data-say="2.2"></p>\n'
        code, err, _ = self.build(old, cues=CUES, report=None)
        self.assertEqual(1, code)
        expected = ('body.html:1: data-say="1.1 1.2" names sentences by number',
                    "body.html:2: data-lit names sentence 2.1 by its number",
                    'body.html:3: data-say="2.2" names sentences by number')
        lines = err.splitlines()
        self.assertEqual(len(expected), len(lines), err)
        for want, line in zip(expected, lines, strict=True):
            self.assertIn(want, line)

    def test_an_element_inside_data_say(self):
        self.assertViolation(BODY.replace("had no version", "had <b>no</b> version"), "body.html:3: <p data-say> holds an element <b>: data-say takes text alone")

    def test_a_data_say_element_without_text(self):
        self.assertViolation(BODY + "<p data-say>  </p>\n", "body.html:4: <p data-say> holds no text")

    def test_a_data_say_element_left_open(self):
        self.assertViolation(BODY + "<div><p data-say>The end.</div>\n", "body.html:4: <p data-say> is not closed before </div>")

    def test_data_part_on_an_element_other_than_h2(self):
        self.assertViolation(BODY + '<h3 data-part="Next.">Next</h3>\n', 'body.html:4: data-part on <h3>: a part starts at an <h2 data-part="…">')

    def test_data_voice_on_an_h2(self):
        self.assertViolation(BODY + '<h2 data-voice="Next.">Next</h2>\n', "body.html:4: data-voice on <h2>: the h2 that starts a part takes data-part")

    def test_an_empty_data_part(self):
        self.assertViolation(BODY + '<h2 data-part="">Next</h2>\n', "body.html:4: <h2 data-part> holds no text")

    def test_an_empty_data_voice(self):
        self.assertViolation(BODY + '<figure data-voice=" "></figure>\n', "body.html:4: <figure data-voice> holds no text")

    def test_two_holders_on_one_element(self):
        self.assertViolation(BODY + '<p data-say data-voice="Said.">Shown.</p>\n', "body.html:4: <p> carries data-say and data-voice")

    def test_a_holder_that_does_not_end_in_a_sentence_mark(self):
        self.assertViolation(BODY.replace('data-part="How it broke."', 'data-part="How it broke"'),
                             "body.html:2: <h2 data-part> ends without a sentence mark (. ! ? …): its last sentence 'How it broke' would run into the next one")

    def test_a_mark_inside_a_sentence(self):
        self.assertViolation(BODY.replace("had no", "had [@none] no"),
                             "body.html:3: the sentence 'The key had [@none] no version.' holds a mark after its start")

    def test_a_mark_without_a_space_after_the_period_stands_inside_a_sentence(self):
        self.assertViolation(BODY.replace("thumbnails. Now", "thumbnails.[@fixed] Now"), "body.html:1: the sentence 'The cache served old thumbnails.[@fixed] Now it does not.' holds a mark")

    def test_a_malformed_name(self):
        for mark in ("[@2key]", "[@]", "[@a key]"):
            with self.subTest(mark=mark):
                self.assertViolation(BODY.replace("The key", f"{mark} The key"), f"body.html:3: the mark {mark} holds no name")

    def test_a_mark_before_no_sentence(self):
        self.assertViolation(BODY.replace("no version.", "no version. [@end]"), "body.html:3: the mark [@end] stands before no sentence")

    def test_a_name_set_twice(self):
        body = BODY.replace("The cache", "[@key] The cache").replace("The key", "[@key] The key")
        self.assertViolation(body, "body.html:3: the name @key is set twice (first on line 1)")

    def test_data_lit_naming_a_sentence_no_mark_sets(self):
        self.assertViolation(BODY + '<figure data-lit="@nowhere"></figure>\n', "body.html:4: data-lit names @nowhere, which no [@nowhere] mark sets")

    def test_data_lit_holding_a_word_that_is_no_name(self):
        self.assertViolation(BODY + '<figure data-lit="cause"></figure>\n', "body.html:4: data-lit holds 'cause': name a sentence as @name")

    def test_a_decision_with_one_option(self):
        one = DECISION.replace('<div class="option" data-option="wait"><h4>Wait</h4></div>', "")
        self.assertViolation(BODY + one, "decision 'purge' has 1 option(s)")

    def test_a_decision_with_two_choices_of_the_author(self):
        self.assertViolation(BODY + DECISION.replace('data-option="wait"', 'data-option="wait" data-mine="1"'), "marks 2 options data-mine=\"1\"")

    def test_a_decision_without_a_title(self):
        self.assertViolation(BODY + DECISION.replace(' data-title="Old thumbnails"', ""), "lacks data-decision or data-title")

    def test_a_decision_key_used_twice(self):
        self.assertViolation(BODY + DECISION + DECISION, "decision key 'purge' is used twice")

    def test_a_script_element(self):
        self.assertViolation(BODY + "<script>alert(1)</script>", "a <script> element")

    def test_a_handler_attribute(self):
        self.assertViolation(BODY + '<button onclick="go()">go</button>', "a handler attribute onclick=")

    def test_violations_are_one_line_each(self):
        code, err, _ = self.build(BODY + '<p data-say="3.1"></p><script></script>', cues=None, report=None)
        self.assertEqual(1, code)
        self.assertEqual(2, len(err.strip().splitlines()), err)


class Links(Build):
    def test_a_link_to_a_missing_id_is_refused(self):
        code, err, page = self.build(BODY + '<p><a href="#nowhere">back</a></p>\n')
        self.assertEqual(1, code, err)
        self.assertIn('body.html:4: href="#nowhere" names no id of the page', err)
        self.assertIsNone(page)

    def test_a_link_to_an_id_of_the_body_passes(self):
        code, err, _ = self.build(BODY.replace("<h2 ", '<h2 id="broke" ') + '<p><a href="#broke">back</a></p>\n')
        self.assertEqual(0, code, err)

    def test_a_link_to_the_look_heading_passes_on_a_page_with_where_to_look(self):
        code, err, _ = self.build(BODY + '<p><a href="#look-heading">where to look</a></p>\n')
        self.assertEqual(0, code, err)

    def test_a_link_to_the_look_heading_is_refused_on_a_page_without_where_to_look(self):
        code, err, _ = self.build(BODY + '<p><a href="#look-heading">where to look</a></p>\n', report=None)
        self.assertEqual(1, code, err)
        self.assertIn('href="#look-heading" names no id of the page', err)


def line_of(body, fragment):
    """The number of the first line of `body` that holds `fragment`."""
    return next(number for number, line in enumerate(body.splitlines(), 1) if fragment in line)


def figure_of(body, kind):
    """The figure of `body` whose class attribute starts with `kind`, as written, with the line break after it."""
    start = body.index(f'<figure class="{kind}')
    return body[start:body.index("</figure>\n", start) + len("</figure>\n")]


class Explanation(Build):
    FIRST_PART = "the first part of an explanation gives the mechanism whole, with its rule as pseudocode, one line a step"
    NO_PSEUDOCODE = f'no <figure class="pseudo"> holding a <pre> of two or more lines stands in the first part: {FIRST_PART}'
    NO_PART = f'the body has no <h2 data-part>, so the explanation has no first part to hold <figure class="pseudo">: {FIRST_PART}'
    EARLY = '<figure class="questions"> opens before the first part ends: the table of questions follows the first part'
    NO_NAV = "<figure> has no data-nav: give the figure a short name for the map of the page"
    HEADING = 'data-part="The whole mechanism."'  # the heading of the fixture's first part
    QUESTIONS = '<figure class="questions"'  # the start tag of the fixture's table of questions, up to its data-nav

    def refusals(self, body, *args):
        """The lines of a refused build, each without the directory of the body."""
        code, err, page = self.build(body, cues=None, report=None, args=args)
        self.assertEqual((1, None), (code, page), err)
        return self.relative(err)

    def assertBuilt(self, body, *args):
        code, err, page = self.build(body, cues=None, report=None, args=args)
        self.assertEqual((0, ""), (code, err))
        return page

    def first_part_only(self):
        """The fixture's opening and first part, its link to a later part made text."""
        return EXPLANATION[:EXPLANATION.index('<h2 id="h-questions"')].replace('<a href="#h-miss">render and store</a>', "render and store")

    def test_a_report_body_is_built_as_before(self):
        self.assertBuilt(BODY + '<figure class="factor"><figcaption>A factor table marks no explanation.</figcaption></figure>\n')

    def test_the_option_checks_a_report_body_as_an_explanation(self):
        self.assertEqual([f"body.html:2: {self.NO_PSEUDOCODE}"], self.refusals(BODY, "--explanation"))

    def test_each_marking_class_makes_a_body_an_explanation(self):
        for kind in ("pseudo", "questions", "quiz"):
            with self.subTest(kind):
                lines = self.refusals(BODY + f'<figure class="{kind}" data-nav="A block"><figcaption>A block.</figcaption></figure>\n')
                self.assertEqual(f"body.html:2: {self.NO_PSEUDOCODE}", lines[0])

    def test_a_table_of_terms_makes_no_explanation_and_stands_anywhere(self):
        terms = figure_of(EXPLANATION, "terms")
        page = self.assertBuilt(BODY + terms)
        self.assertFalse(self.data(page)["map"])
        self.assertBuilt(EXPLANATION.replace(terms, "").replace('<h2 id="h-whole"', terms + '<h2 id="h-whole"'))

    def test_a_conforming_explanation_is_built_with_or_without_the_option(self):
        page = self.assertBuilt(EXPLANATION)
        self.assertIn('<figure class="pseudo" data-nav="The rule of the cache">\n  <pre><span data-lit="2.2">on upload(picture): picture.version += 1</span>', page)
        self.assertEqual(["Opening", "The whole mechanism", "Your questions", "A miss"], [part["title"] for part in self.data(page)["parts"]])
        self.assertBuilt(EXPLANATION, "--explanation")

    def test_the_data_of_an_explanation_asks_for_the_map_and_a_reports_does_not(self):
        self.assertTrue(self.data(self.assertBuilt(EXPLANATION))["map"])
        self.assertTrue(self.data(self.assertBuilt(self.first_part_only(), "--explanation"))["map"])
        self.assertFalse(self.data(self.assertBuilt(BODY))["map"])

    def test_the_opening_and_the_first_part_alone_are_built(self):
        self.assertBuilt(self.first_part_only(), "--explanation")

    def test_a_pre_of_one_line_is_refused_at_the_heading_of_the_first_part(self):
        for case, pre in (("one line", "<pre>on upload(picture): picture.version += 1</pre>"),
                          ("one line among empty ones", "<pre>\non upload(picture): picture.version += 1\n   \n</pre>"),
                          ("no pre", "<p>on upload(picture): picture.version += 1</p>")):
            with self.subTest(case):
                body = re.sub(r"<pre>.*?</pre>", lambda _: pre, EXPLANATION, flags=re.S)
                self.assertEqual([f"body.html:{line_of(body, self.HEADING)}: {self.NO_PSEUDOCODE}"], self.refusals(body))

    def test_the_pseudocode_counts_only_in_the_first_part(self):
        pseudo = figure_of(EXPLANATION, "pseudo").replace('<a href="#h-miss">render and store</a>', "render and store")
        without = EXPLANATION.replace(figure_of(EXPLANATION, "pseudo"), "")
        cases = {"in the opening": without.replace('<h2 id="h-whole"', pseudo + '<h2 id="h-whole"'),
                 "in the second part": without.replace(self.QUESTIONS, pseudo + self.QUESTIONS),
                 "nowhere": without}
        for case, body in cases.items():
            with self.subTest(case):
                self.assertEqual(case != "nowhere", pseudo in body)
                self.assertEqual([f"body.html:{line_of(body, self.HEADING)}: {self.NO_PSEUDOCODE}"], self.refusals(body))

    def test_a_table_of_questions_inside_the_first_part_is_refused_at_its_line(self):
        questions = figure_of(EXPLANATION, "questions")
        body = EXPLANATION.replace(questions, "").replace('<h2 id="h-questions"', questions + '<h2 id="h-questions"')
        self.assertEqual([f"body.html:{line_of(body, self.QUESTIONS)}: {self.EARLY}"], self.refusals(body))

    def test_in_a_body_of_one_part_a_table_of_questions_anywhere_is_refused(self):
        questions = figure_of(EXPLANATION, "questions").replace('<a href="#h-miss">A miss</a>', "A miss")
        body = self.first_part_only() + questions
        self.assertEqual([f"body.html:{line_of(body, self.QUESTIONS)}: {self.EARLY}"], self.refusals(body))

    def test_a_body_without_a_part_is_refused_at_line_1(self):
        body = ('<p data-say>The cache keeps thumbnails.</p>\n'
                '<figure class="pseudo" data-nav="The rule"><pre>key = id + version\nserve cache[key]</pre></figure>\n')
        self.assertEqual([f"body.html:1: {self.NO_PART}"], self.refusals(body))

    def test_a_class_list_is_matched_by_token(self):
        marked = EXPLANATION.replace('<figure class="pseudo"', '<figure class="wide pseudo"')
        self.assertNotEqual(EXPLANATION, marked)
        self.assertBuilt(marked)
        self.assertBuilt(BODY + '<figure class="pseudocode quizzes"><figcaption>Neither token marks an explanation.</figcaption></figure>\n')

    def test_a_table_of_questions_among_other_classes_is_refused_inside_the_first_part(self):
        questions = figure_of(EXPLANATION, "questions")
        early = EXPLANATION.replace(questions, "").replace('<h2 id="h-questions"', questions.replace('class="questions"', 'class="compact questions"')
                                                           + '<h2 id="h-questions"')
        self.assertEqual([f"body.html:{line_of(early, 'compact questions')}: {self.EARLY}"], self.refusals(early))

    def test_a_figure_without_a_name_for_the_map_is_refused_at_its_line(self):
        cases = {"no data-nav": ' data-nav="The key without and with the version"',
                 "an empty data-nav": ' data-nav="  "'}
        for case, nameless in cases.items():
            with self.subTest(case):
                body = EXPLANATION.replace(' data-nav="The key without and with the version"', "" if case == "no data-nav" else nameless)
                self.assertNotEqual(EXPLANATION, body)
                line = line_of(body, '<figure class="factor wide"')
                self.assertEqual([f"body.html:{line}: {self.NO_NAV}"], self.refusals(body))

    def test_a_figure_of_any_class_needs_its_name_and_a_question_needs_none(self):
        plain = '<figure aria-labelledby="h-miss"><figcaption>A miss in pictures.</figcaption></figure>\n'
        body = EXPLANATION.replace('<figure class="quiz">', plain + '<figure class="quiz">')
        self.assertEqual([f"body.html:{line_of(body, plain.strip())}: {self.NO_NAV}"], self.refusals(body))
        self.assertIn('<figure class="quiz">', EXPLANATION)
        self.assertBuilt(EXPLANATION)

    def test_a_report_needs_no_name_for_its_figures(self):
        self.assertBuilt(BODY + '<figure><figcaption>A figure of a report.</figcaption></figure>\n')

    def test_the_refusals_stand_among_the_other_violations_sorted_by_line(self):
        lines = self.refusals(BODY + '<figure class="questions" data-nav="Questions"><script></script></figure>\n')
        self.assertEqual([f"body.html:2: {self.NO_PSEUDOCODE}", f"body.html:4: {self.EARLY}",
                          "body.html:4: a <script> element: the body carries no script, the page's script is the template's"], lines)


class Terms(Build):
    """The list of terms: each barred word in the body's own text refuses the body at its line."""
    VERSION = {"term": "version", "is": "the count of a picture's uploads", "code": "picture.version", "not": ["generation", "revision*"]}
    CACHE = {"term": "thumbnail cache", "not": ["cache", "thumbnail store"]}

    def build_with(self, body, terms, *, cues=None, report=None, args=()):
        """(exit code, stderr lines without the directory, page or None) of a build with the list of terms."""
        path = self.dir / "terms.json"
        path.write_text(terms if isinstance(terms, str) else json.dumps(terms), encoding="utf-8")
        code, err, page = self.build(body, cues=cues, report=report, args=["--terms", str(path), *args])
        return code, self.relative(err), page

    def stands_for(self, found, term):
        return f'"{found}" stands for "{term}": write the term'

    def test_a_barred_word_is_refused_at_its_line_in_any_case(self):
        body = BODY + "<p>The picture keeps its generation.</p>\n<p>Generation grows by one.</p>\n"
        code, lines, page = self.build_with(body, [self.VERSION], cues=CUES)
        self.assertEqual((1, None), (code, page))
        self.assertEqual([f"body.html:4: {self.stands_for('generation', 'version')}", f"body.html:5: {self.stands_for('Generation', 'version')}"],
                         lines)

    def test_a_barred_word_inside_its_own_term_is_passed(self):
        body = "<p>The thumbnail cache keeps one picture per upload.</p>\n<p>The Thumbnail  Cache answers, and the cache misses.</p>\n"
        code, lines, _ = self.build_with(body, [self.CACHE])
        self.assertEqual((1, [f"body.html:2: {self.stands_for('cache', 'thumbnail cache')}"]), (code, lines))

    def test_a_barred_phrase_is_found_across_a_line_break_at_its_first_line(self):
        body = "<p>The thumbnail\n  store keeps one picture.</p>\n"
        code, lines, _ = self.build_with(body, [self.CACHE])
        self.assertEqual((1, [f"body.html:1: {self.stands_for('thumbnail store', 'thumbnail cache')}"]), (code, lines))

    def test_a_starred_entry_matches_every_word_that_starts_with_it_and_no_other(self):
        body = "<p>Two revisions of the picture.</p>\n<p>One revision.</p>\n<p>A prevision and a version stay.</p>\n"
        code, lines, _ = self.build_with(body, [self.VERSION])
        self.assertEqual((1, [f"body.html:1: {self.stands_for('revisions', 'version')}", f"body.html:2: {self.stands_for('revision', 'version')}"]),
                         (code, lines))

    def test_a_barred_word_in_a_spoken_attribute_is_refused_at_the_attributes_line(self):
        body = (BODY.replace('data-part="How it broke."', 'data-part="How the generation broke."')
                + '<figure class="x"\n  data-voice="The figure shows the revisions."><figcaption>Keys</figcaption></figure>\n')
        code, lines, _ = self.build_with(body, [self.VERSION])
        self.assertEqual((1, [f"body.html:2: {self.stands_for('generation', 'version')}", f"body.html:5: {self.stands_for('revisions', 'version')}"]),
                         (code, lines))

    def test_a_barred_word_in_an_attribute_the_reader_sees_or_hears_is_refused_at_its_line(self):
        body = (BODY + '<figure data-nav="The generation of a key"><img src="key.png" alt="two revisions"\n'
                '  data-title="A generation" title="One generation"><figcaption>Keys</figcaption></figure>\n'
                '<p aria-label="The generation">Keys.</p>\n')
        code, lines, _ = self.build_with(body, [self.VERSION])
        self.assertEqual((1, [f"body.html:4: {self.stands_for('generation', 'version')}", f"body.html:4: {self.stands_for('revisions', 'version')}",
                              f"body.html:5: {self.stands_for('generation', 'version')}", f"body.html:6: {self.stands_for('generation', 'version')}"]),
                         (code, lines))

    def test_a_sentence_mark_is_not_searched(self):
        body = BODY.replace("Now it", "[@generation] Now it")
        code, lines, _ = self.build_with(body, [self.VERSION])
        self.assertEqual((0, []), (code, lines))

    def test_the_look_section_is_not_searched(self):
        lifetime = {"term": "lifetime", "not": ["lives", "tests"]}
        self.assertIn("how long an entry lives", REPORT.read_text(encoding="utf-8"))
        code, lines, page = self.build_with(BODY, [lifetime], cues=CUES, report=REPORT)
        self.assertEqual((0, []), (code, lines))
        self.assertIn("how long an entry lives", page)

    def test_an_empty_list_passes_every_body(self):
        self.assertEqual((0, []), self.build_with(BODY, [])[:2])

    def test_an_unusable_list_exits_2_naming_the_entry(self):
        cases = {"no JSON": ("[{", "cannot read the list of terms"),
                 "no list": ('{"term": "version"}', "is not a JSON list of objects"),
                 "an entry without a term": ('[{"not": ["generation"]}]', 'entry 1 has no non-empty "term"'),
                 "an empty term": ('[{"term": "  "}]', 'entry 1 has no non-empty "term"'),
                 "a word list that is a text": ('[{"term": "version"}, {"term": "key", "not": "slot"}]', 'the "not" of entry 2'),
                 "a star alone": ('[{"term": "version", "not": ["*"]}]', 'the "not" of entry 1'),
                 "an unknown key": ('[{"term": "version", "nto": []}]', "entry 1 holds unknown key(s) nto"),
                 "a key twice": ('[{"term": "version", "term": "key"}]', 'the key "term" appears twice'),
                 "an explanation that is not a text": ('[{"term": "version", "is": 1}]', 'the "is" of entry 1 is not a text')}
        for case, (text, message) in cases.items():
            with self.subTest(case):
                code, lines, page = self.build_with(BODY, text)
                self.assertEqual((2, None), (code, page))
                self.assertIn(message, "\n".join(lines))
                self.assertIn("terms.json", "\n".join(lines))


class References(Build):
    """The file of references: each data-ref of the body names an entry, resolved into the page's data."""
    KEY_VALUE = {"path": "src/cache/ThumbKey.java", "fragment": 'return "thumb:"'}
    SOURCE = {"title": "Generation numbers in cache keys", "href": "https://example.org/cache-keys"}
    BODY = BODY + '<p>The key is built in <code data-ref="key-value">ThumbKey.value</code>.</p>\n'  # the data-ref stands on line 4
    ROOT = FIXTURES / "repo"
    JAVA = (ROOT / "src/cache/ThumbKey.java").read_text(encoding="utf-8").splitlines()

    def build_with(self, refs, *, body=None, args=("--root", str(ROOT))):
        """(exit code, stderr lines without the directory, page or None) of a build with the file of references."""
        path = self.dir / "refs.json"
        path.write_text(refs if isinstance(refs, str) else json.dumps(refs), encoding="utf-8")
        code, err, page = self.build(self.BODY if body is None else body, cues=None, report=None, args=["--refs", str(path), *args])
        return code, self.relative(err), page

    def excerpt(self, first, last, anchored):
        return [[n, self.JAVA[n - 1], n == anchored] for n in range(first, last + 1)]

    def test_a_code_entry_resolves_to_its_line_and_twelve_lines_below_in_the_page_data(self):
        code, lines, page = self.build_with({"key-value": self.KEY_VALUE})
        self.assertEqual((0, []), (code, lines))
        self.assertEqual({"key-value": {"kind": "code", "path": "src/cache/ThumbKey.java", "line": 23, "excerpt": self.excerpt(20, 35, 23)}},
                         self.data(page)["refs"])
        self.assertEqual(35, len(self.JAVA))  # the file ends at line 35, so the twelve lines below stop there
        self.assertIn('<code data-ref="key-value">ThumbKey.value</code>', page)

    def test_lines_bounds_the_excerpt_below_the_line(self):
        code, _, page = self.build_with({"key-value": dict(self.KEY_VALUE, lines=2)})
        self.assertEqual(0, code)
        self.assertEqual(self.excerpt(20, 25, 23), self.data(page)["refs"]["key-value"]["excerpt"])

    def test_lines_outside_one_to_sixty_is_unreadable_input(self):
        for lines in (0, 61, 2.5, True, "12"):
            with self.subTest(lines=lines):
                code, err, page = self.build_with({"key-value": dict(self.KEY_VALUE, lines=lines)})
                self.assertEqual((2, None), (code, page))
                self.assertIn('entry "key-value" has "lines"', "\n".join(err))

    def test_a_key_the_file_lacks_is_refused_at_its_line(self):
        body = self.BODY.replace("key-value", "key-text") + '<p><span data-ref="generation">A generation number</span>.</p>\n'
        code, lines, page = self.build_with({"generation": self.SOURCE}, body=body)
        self.assertEqual((1, None, ['body.html:4: data-ref="key-text" names no entry of the references']), (code, page, lines))

    def test_a_data_ref_on_a_page_built_without_references_is_refused(self):
        code, err, page = self.build(self.BODY, cues=None, report=None)
        self.assertEqual((1, None), (code, page))
        self.assertEqual(['body.html:4: data-ref="key-value" names no entry of the references'], self.relative(err))

    def test_an_entry_whose_file_is_missing_is_refused_naming_it(self):
        code, lines, page = self.build_with({"key-value": dict(self.KEY_VALUE, path="src/cache/Gone.java")})
        self.assertEqual((1, None, ['refs.json: entry "key-value": src/cache/Gone.java is no file under --root']), (code, page, lines))

    def test_a_fragment_on_two_lines_is_refused_naming_the_lines(self):
        code, lines, page = self.build_with({"key-value": dict(self.KEY_VALUE, fragment="pictureId;")})
        self.assertEqual((1, None), (code, page))
        self.assertEqual(['refs.json: entry "key-value": \'pictureId;\' stands on lines 10, 14, 19 of src/cache/ThumbKey.java: '
                          'lengthen it so it names one line'], lines)

    def test_a_code_entry_without_root_is_refused(self):
        code, lines, page = self.build_with({"key-value": self.KEY_VALUE}, args=())
        self.assertEqual((1, None, ['refs.json: entry "key-value": a code entry needs --root']), (code, page, lines))

    def test_an_unused_entry_warns_is_not_resolved_and_the_page_builds(self):
        code, lines, page = self.build_with({"key-value": self.KEY_VALUE, "gone": dict(self.KEY_VALUE, path="src/cache/Gone.java")})
        self.assertEqual((0, ['refs.json: warning: entry "gone" is not used']), (code, lines))
        self.assertEqual(["key-value"], list(self.data(page)["refs"]))

    def test_an_unused_entry_is_named_after_the_refusals_of_a_refused_body(self):
        code, lines, _ = self.build_with({"gone": self.SOURCE}, body=self.BODY.replace("key-value", "key-text"))
        self.assertEqual((1, ['body.html:4: data-ref="key-text" names no entry of the references', 'refs.json: warning: entry "gone" is not used']),
                         (code, lines))

    def test_a_source_entry_passes_through_with_an_empty_note_when_it_has_none(self):
        noted = dict(self.SOURCE, note="A key that carries the version never meets an older entry.")
        body = self.BODY.replace("key-value", "generation") + '<p><span data-ref="noted">The same idea</span>.</p>\n'
        code, lines, page = self.build_with({"generation": self.SOURCE, "noted": noted}, body=body)
        self.assertEqual((0, []), (code, lines))
        self.assertEqual({"generation": dict(self.SOURCE, kind="source", note=""), "noted": dict(noted, kind="source")}, self.data(page)["refs"])

    def test_an_unusable_file_exits_2_naming_the_entry(self):
        cases = {"no JSON": ("{", "cannot read the references"),
                 "a list": ("[]", "are not a JSON object"),
                 "a key twice": ('{"key-value": {}, "key-value": {}}', 'the key "key-value" appears twice'),
                 "neither kind": (json.dumps({"key-value": {"path": "src/cache/ThumbKey.java"}}), 'entry "key-value" is neither a code entry'),
                 "both kinds": (json.dumps({"key-value": dict(self.KEY_VALUE, **self.SOURCE)}), 'entry "key-value" is neither a code entry'),
                 "an empty fragment": (json.dumps({"key-value": dict(self.KEY_VALUE, fragment=" ")}), 'entry "key-value" has a "path" or a "fragment"'),
                 "a script address": (json.dumps({"key-value": dict(self.SOURCE, href="javascript:alert(1)")}), "not an http: or https: address"),
                 "a file address": (json.dumps({"key-value": dict(self.SOURCE, href="file:///etc/hosts")}), "not an http: or https: address"),
                 "a note that is no text": (json.dumps({"key-value": dict(self.SOURCE, note=1)}), 'a "note" that is not a text')}
        for case, (text, message) in cases.items():
            with self.subTest(case):
                code, lines, page = self.build_with(text)
                self.assertEqual((2, None), (code, page))
                self.assertIn(message, "\n".join(lines))

    def test_editor_url_fills_the_absolute_path_and_the_line(self):
        code, lines, page = self.build_with({"key-value": self.KEY_VALUE},
                                            args=("--root", str(self.ROOT), "--standalone", "--editor-url", "vscode://file{path}:{line}"))
        self.assertEqual((0, []), (code, lines))
        target = (self.ROOT / "src/cache/ThumbKey.java").resolve().as_posix()
        self.assertEqual(f"vscode://file{quote(target)}:23", self.data(page)["refs"]["key-value"]["editor"])

    def test_a_source_entry_takes_no_editor_link(self):
        body = self.BODY.replace("key-value", "generation")
        code, _, page = self.build_with({"generation": self.SOURCE}, body=body,
                                        args=("--root", str(self.ROOT), "--standalone", "--editor-url", "vscode://file{path}:{line}"))
        self.assertEqual(0, code)
        self.assertNotIn("editor", self.data(page)["refs"]["generation"])

    def test_editor_url_is_refused_without_standalone_refs_or_root_or_without_its_path(self):
        url = ("--editor-url", "vscode://file{path}:{line}")
        root = ("--root", str(self.ROOT))
        for case, args in {"no --standalone": (*root, *url), "no --root": ("--standalone", *url)}.items():
            with self.subTest(case):
                code, lines, page = self.build_with({"key-value": self.KEY_VALUE}, args=args)
                self.assertEqual((2, None), (code, page))
                self.assertIn("--editor-url needs --standalone, --refs and --root", "\n".join(lines))
        code, err, _ = self.build(self.BODY, cues=None, report=None, args=["--standalone", *root, *url])
        self.assertEqual(2, code)
        self.assertIn("--editor-url needs --standalone, --refs and --root", err)
        code, lines, _ = self.build_with({"key-value": self.KEY_VALUE}, args=(*root, "--standalone", "--editor-url", "vscode://file"))
        self.assertEqual(2, code)
        self.assertIn("holds no {path}", "\n".join(lines))


class Story(Build):
    def story(self, body, *args):
        (self.dir / "body.html").write_text(body, encoding="utf-8")
        story = self.dir / "story.txt"
        code, _, err = self.run_main(["--body", str(self.dir / "body.html"), "--story-out", str(story), *args])
        return code, err, story.read_text(encoding="utf-8") if story.exists() else None

    def test_story_out_writes_one_paragraph_per_part_with_the_announcing_phrase_first_and_no_mark(self):
        code, err, story = self.story(BODY.replace("Now it", "[@fixed] Now it"))
        self.assertEqual(0, code, err)
        self.assertEqual(STORY, story)

    def test_story_out_runs_without_cues_and_without_out(self):
        code, err, story = self.story(BODY)
        self.assertEqual(0, code, err)
        self.assertIsNotNone(story)
        self.assertEqual(["body.html", "config", "story.txt"], sorted(path.name for path in self.dir.iterdir()))

    def test_the_voice_reads_the_story_as_the_body_numbers_it(self):
        body = ('<p data-say>The&nbsp;cache   served\n   old thumbnails!  Now it does not?</p>\n'
                '<h2 data-part="How it broke…">How</h2>\n<div class="x" data-voice="It had no version. None."></div>\n')
        code, err, story = self.story(body, "--out", str(self.dir / "page.html"))
        self.assertEqual(0, code, err)
        voice = load_voice_cues()
        heard = [(p, s, paragraph[a:b]) for p, paragraph in enumerate(voice.paragraphs(story), 1)
                 for s, (a, b) in enumerate(voice.sentence_spans(paragraph), 1)]
        shown = [(c["paragraph"], c["sentence"], c["text"]) for c in self.data((self.dir / "page.html").read_text(encoding="utf-8"))["cues"]]
        self.assertEqual(heard, shown)
        self.assertEqual(5, len(shown))

    def test_an_opening_without_a_spoken_sentence_is_no_part(self):
        body = '<h1>Thumbnails</h1>\n<h2 data-part="How it broke.">How it broke</h2>\n<p data-say>The key had no version.</p>\n'
        code, err, story = self.story(body, "--out", str(self.dir / "page.html"))
        self.assertEqual(0, code, err)
        self.assertEqual("How it broke. The key had no version.\n", story)
        parts = self.data((self.dir / "page.html").read_text(encoding="utf-8"))["parts"]
        self.assertEqual([{"paragraph": 1, "cue": "1.1", "start": 0.0, "title": "How it broke"}], parts)


class Cues(Build):
    def test_without_cues_the_page_is_silent(self):
        code, err, page = self.build(cues=None)
        self.assertEqual(0, code, err)
        data = self.data(page)
        self.assertEqual([dict(cue, start=0.0, end=0.0) for cue in CUES], data["cues"])
        self.assertEqual("", data["voice"])

    def test_with_cues_the_page_takes_their_times(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual(CUES, self.data(page)["cues"])

    def test_cues_with_a_changed_sentence_are_refused_naming_the_sentence(self):
        code, err, page = self.build(cues=[*CUES[:3], dict(CUES[3], text="The key had a version.")])
        self.assertEqual(1, code)
        self.assertIn("body.html:3: sentence 2.2 reads 'The key had no version.', its cue 2.2 reads 'The key had a version.'", err)
        self.assertIn("voice the story again", err)
        self.assertIsNone(page)

    def test_cues_without_the_last_sentence_are_refused_naming_it(self):
        code, err, _ = self.build(cues=CUES[:3])
        self.assertEqual(1, code)
        self.assertIn("body.html:3: sentence 2.2 'The key had no version.' has no cue", err)

    def test_cues_past_the_last_sentence_are_refused(self):
        code, err, _ = self.build(cues=[*CUES, dict(CUES[3], sentence=3, text="And more.")])
        self.assertEqual(1, code)
        self.assertIn("cue 2.3 'And more.' follows the body's last sentence", err)

    def test_voice_without_cues_is_exit_2(self):
        code, err, page = self.build(cues=None, args=["--voice", "story.wav"])
        self.assertEqual(2, code)
        self.assertIn("--voice needs --cues", err)
        self.assertIsNone(page)

    def test_unreadable_cues_are_exit_2(self):
        code, err, page = self.build(cues=[{"paragraph": 1}])
        self.assertEqual(2, code)
        self.assertIn("entry 1", err)
        self.assertIsNone(page)


class Warnings(Build):
    def warned(self, sentence):
        """(exit code, stderr, page) of BODY with one more paragraph, on line 4, saying `sentence`."""
        return self.build(BODY + f"<p data-say>{sentence}</p>\n", cues=None, report=None)

    def test_a_sentence_that_starts_with_a_lowercase_letter(self):
        code, err, page = self.warned("Use the key, e.g. the version.")
        self.assertEqual(0, code, err)
        self.assertIn("body.html:4: warning: sentence 2.4 starts with a lowercase letter", err)
        self.assertIsNotNone(page)

    def test_a_sentence_that_ends_in_a_number_before_its_period(self):
        code, err, page = self.warned("The tests passed 9 of 9.")
        self.assertEqual(0, code, err)
        self.assertIn("body.html:4: warning: sentence 2.3 ends in a number before its period (9.)", err)
        self.assertIsNotNone(page)

    def test_a_sentence_that_holds_a_decimal_fraction(self):
        code, err, page = self.warned("The page loads in 1.5 seconds.")
        self.assertEqual(0, code, err)
        self.assertIn("body.html:4: warning: sentence 2.3 holds the decimal fraction 1.5", err)
        self.assertIsNotNone(page)

    def test_a_sentence_that_holds_a_number_with_an_ordinary_space_inside(self):
        code, err, page = self.warned("The cache holds 500 000 entries.")
        self.assertEqual(0, code, err)
        self.assertIn("body.html:4: warning: sentence 2.3 holds the number '500 000' with an ordinary space inside", err)
        self.assertIsNotNone(page)

    def test_near_misses_give_no_warning(self):
        code, err, _ = self.warned("Upload 2 of 3 took 42 seconds, and 9 of 9 tests pass. In 2024 100 pictures moved.")
        self.assertEqual(0, code, err)
        self.assertEqual("", err)


class WhereToLook(Build):
    REPORT = ("Opening.\n\n## Where to look\n\n"
              "- the key: `src/cache/ThumbKey.java:23` `\":v\" + version`\n"
              "- past the end: `src/cache/ThumbKey.java:99`\n"
              "- outside the root: `../page/report.md:1`\n"
              "- the tests: 9 of 9 passed\n")
    ROOT = ("--root", str(FIXTURES / "repo"))
    KEY = {"what": "the key", "path": "src/cache/ThumbKey.java", "fragment": "\":v\" + version"}

    def look(self, page):
        return page[page.index('<section class="look"'):]

    def test_a_resolving_anchor_opens_three_lines_around_it(self):
        code, err, page = self.build(report=self.REPORT, args=self.ROOT)
        self.assertEqual(0, code, err)
        first = self.look(page).split("</li>")[0]
        self.assertIn("<summary>the key: <code>src/cache/ThumbKey.java:23</code> <code>&quot;:v&quot; + version</code></summary>", first)
        self.assertEqual(["20", "21", "22", "23", "24", "25", "26"], re.findall(r'<span class="ln">(\d+)</span>', first))
        self.assertEqual(1, first.count('<span class="hit">'))
        self.assertIn('<span class="hit"><span class="ln">23</span>          return &quot;thumb:&quot;', first)

    def test_an_anchor_past_the_end_of_its_file_is_shown_as_text(self):
        code, err, page = self.build(report=self.REPORT, args=self.ROOT)
        self.assertEqual(0, code, err)
        self.assertIn('<li class="look-item">past the end: <code>src/cache/ThumbKey.java:99</code></li>', self.look(page))

    def test_an_anchor_outside_the_root_is_shown_as_text(self):
        code, err, page = self.build(report=self.REPORT, args=self.ROOT)
        self.assertEqual(0, code, err)
        self.assertIn('<li class="look-item">outside the root: <code>../page/report.md:1</code></li>', self.look(page))

    def test_an_item_without_an_anchor_is_shown_as_text(self):
        code, err, page = self.build(report=self.REPORT, args=self.ROOT)
        self.assertEqual(0, code, err)
        self.assertIn('<li class="look-item">the tests: 9 of 9 passed</li>', self.look(page))

    def test_without_root_no_anchor_resolves(self):
        code, err, page = self.build(report=self.REPORT)
        self.assertEqual(0, code, err)
        self.assertNotIn("<details>", self.look(page))

    def test_the_section_takes_the_report_heading_text(self):
        code, err, page = self.build(report=self.REPORT)
        self.assertEqual(0, code, err)
        self.assertIn('<h2 id="look-heading">Where to look</h2>', page)

    def test_a_heading_of_the_lexicon_is_found(self):
        lexicon = self.config / "handing-over-to-readers/lexicon.json"
        lexicon.write_text(json.dumps({"check_report": {"WHERE_TO_LOOK": ["где смотреть"]}}), encoding="utf-8")
        code, err, page = self.build(report="Вводный абзац.\n\n## Где смотреть\n\n- тесты: 9 из 9\n")
        self.assertEqual(0, code, err)
        self.assertIn('<h2 id="look-heading">Где смотреть</h2>', page)

    def test_a_report_without_the_heading_is_exit_2(self):
        code, err, page = self.build(report="Opening.\n\n## Something else\n\n- an item\n")
        self.assertEqual(2, code)
        self.assertIn("Where to look", err)
        self.assertIsNone(page)

    def test_a_look_fragment_resolves_to_its_line_and_shows_the_lines_around_it(self):
        code, err, page = self.build(report=None, look=[self.KEY], args=self.ROOT)
        self.assertEqual(0, code, err)
        item = self.look(page).split("</li>")[0]
        self.assertIn("<summary>the key: <code>src/cache/ThumbKey.java:23</code> <code>&quot;:v&quot; + version</code></summary>", item)
        self.assertEqual(["20", "21", "22", "23", "24", "25", "26"], re.findall(r'<span class="ln">(\d+)</span>', item))
        self.assertIn('<span class="hit"><span class="ln">23</span>', item)

    def test_a_fragment_on_no_line_is_refused(self):
        code, err, page = self.build(report=None, look=[dict(self.KEY, fragment="nowhere")], args=self.ROOT)
        self.assertEqual(1, code)
        self.assertIn("look.json: item 1 (the key): 'nowhere' stands on no line of src/cache/ThumbKey.java", err)
        self.assertIsNone(page)

    def test_a_fragment_on_two_lines_is_refused_naming_the_lines(self):
        code, err, _ = self.build(report=None, look=[dict(self.KEY, fragment="pictureId;")], args=self.ROOT)
        self.assertEqual(1, code)
        self.assertIn("item 1 (the key): 'pictureId;' stands on lines 10, 14, 19 of src/cache/ThumbKey.java", err)

    def test_a_fragment_item_without_root_is_refused(self):
        code, err, _ = self.build(report=None, look=[self.KEY])
        self.assertEqual(1, code)
        self.assertIn("item 1 (the key): a fragment item needs --root", err)

    def test_a_fragment_item_outside_the_root_is_refused(self):
        code, err, _ = self.build(report=None, look=[dict(self.KEY, path="../report.md", fragment="Opening")], args=self.ROOT)
        self.assertEqual(1, code)
        self.assertIn("item 1 (the key): ../report.md lies outside --root", err)

    def test_a_fragment_item_of_a_missing_file_is_refused(self):
        code, err, _ = self.build(report=None, look=[dict(self.KEY, path="src/cache/Gone.java")], args=self.ROOT)
        self.assertEqual(1, code)
        self.assertIn("item 1 (the key): src/cache/Gone.java is no file under --root", err)

    def test_a_text_item_is_shown_as_text(self):
        code, err, page = self.build(report=None, look=[{"what": "the tests: 9 of 9 passed, `./gradlew test` exit 0"}])
        self.assertEqual(0, code, err)
        self.assertIn('<li class="look-item">the tests: 9 of 9 passed, <code>./gradlew test</code> exit 0</li>', self.look(page))

    def test_a_fragment_with_backticks_keeps_them_in_its_code_span(self):
        (self.dir / "root").mkdir()
        (self.dir / "root/notes.md").write_text("a line\nwrite `x` here\n", encoding="utf-8")
        look = [{"what": "the mark", "path": "notes.md", "fragment": "`x`"}]
        code, err, page = self.build(report=None, look=look, args=["--root", str(self.dir / "root")])
        self.assertEqual(0, code, err)
        self.assertIn("<summary>the mark: <code>notes.md:2</code> <code>`x`</code></summary>", page)

    def test_the_heading_of_a_look_list_is_the_string_look(self):
        (self.dir / "strings.json").write_text(json.dumps({"look": "Где смотреть"}), encoding="utf-8")
        code, err, page = self.build(report=None, look=[{"what": "the tests"}], args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertIn('<h2 id="look-heading">Где смотреть</h2>', page)

    def test_report_with_look_is_exit_2(self):
        code, err, page = self.build(look=[{"what": "the tests"}])
        self.assertEqual(2, code)
        self.assertIn("--report or --look, not both", err)
        self.assertIsNone(page)

    def test_neither_gives_a_page_without_the_section(self):
        code, err, page = self.build(report=None)
        self.assertEqual(0, code, err)
        self.assertNotIn('<section class="look"', page)

    def test_an_unusable_look_list_is_exit_2(self):
        cases = {
            "not json": ("[", "cannot read the look list"),
            "not a list of objects": ('{"what": "x"}', "is not a JSON list of objects"),
            "an item without what": ('[{"path": "a", "fragment": "b"}]', 'item 1 has no "what"'),
            "a path without a fragment": ('[{"what": "x", "path": "a"}]', 'item 1 has a "path" without a "fragment"'),
            "a fragment without a path": ('[{"what": "x", "fragment": "a"}]', 'item 1 has a "path" without a "fragment" or the reverse'),
            "an empty what": ('[{"what": " "}]', "the 'what' of item 1 is not a text"),
        }
        for case, (text, message) in cases.items():
            with self.subTest(case):
                code, err, page = self.build(report=None, look=text, args=self.ROOT)
                self.assertEqual(2, code)
                self.assertIn(message, err)
                self.assertIsNone(page)


class TextOut(Build):
    BODY = ('<h1>Fresh thumbnails</h1>\n'
            '<p data-say>The key had no version. [@now] Now it has one.</p>\n'
            '<h2 data-part="How it broke.">How it broke</h2>\n'
            '<figure><table><tr><th>upload</th><th data-lit="@now">key</th></tr><tr><td>1</td><td><code>thumb:42:v1</code></td></tr></table>\n'
            '<svg class="fig"><g data-voice="The figure says this."><rect/><text>old <tspan>key</tspan></text></g></svg>\n'
            '<figcaption>The key before and after.</figcaption></figure>\n'
            '<details><summary>Why a version?</summary><p>Because a number repeats.</p></details>\n'
            '<h3>Ways</h3>\n<ul><li class="plus">fast</li><li class="minus">wrong for a day</li><li>plain</li></ul>\n'
            '<pre>line 1\n  line 2</pre>\n')
    TEXT = ("# Fresh thumbnails\n"
            "The key had no version. Now it has one.\n"
            "## How it broke\n"
            "upload | key\n"
            "1 | `thumb:42:v1`\n"
            "old key\n"
            "The key before and after.\n"
            "Why a version?\n"
            "Because a number repeats.\n"
            "### Ways\n"
            "+ fast\n"
            "- wrong for a day\n"
            "- plain\n"
            "```\nline 1\n  line 2\n```\n"
            "## Where to look\n"
            "- the key: `src/cache/ThumbKey.java:23` `\":v\" + version`\n")

    def text(self, body, *args):
        (self.dir / "body.html").write_text(body, encoding="utf-8")
        (self.dir / "look.json").write_text(json.dumps([WhereToLook.KEY]), encoding="utf-8")
        text = self.dir / "text.md"
        code, _, err = self.run_main(["--body", str(self.dir / "body.html"), "--text-out", str(text), "--look", str(self.dir / "look.json"),
                                      "--root", str(FIXTURES / "repo"), *args])
        return code, err, text.read_text(encoding="utf-8") if text.exists() else None

    def test_the_text_holds_what_the_page_shows_top_to_bottom(self):
        code, err, text = self.text(self.BODY)
        self.assertEqual(0, code, err)
        self.assertEqual(self.TEXT, text)

    def test_spoken_text_that_is_not_shown_stays_out(self):
        code, err, text = self.text(self.BODY)
        self.assertEqual(0, code, err)
        for spoken in ("How it broke.", "The figure says this.", "[@"):
            self.assertNotIn(spoken, text)

    def test_the_text_runs_without_out_and_without_cues(self):
        code, err, text = self.text(self.BODY)
        self.assertEqual(0, code, err)
        self.assertEqual(["body.html", "config", "look.json", "text.md"], sorted(path.name for path in self.dir.iterdir()))

    def test_the_pseudocode_keeps_its_lines_between_fences_through_its_spans_and_links(self):
        code, err, text = self.text(EXPLANATION)
        self.assertEqual(0, code, err)
        self.assertIn("## The whole mechanism\n"
                      "Every upload raises the picture's version by one. The key joins the picture's number and its version. "
                      "A request is served from the cache under that key, and a miss renders the thumbnail and stores it there.\n"
                      "```\n"
                      "on upload(picture): picture.version += 1\n"
                      'key(picture) = "thumb:" + picture.id + ":v" + picture.version\n'
                      "on request(picture): cache[key(picture)] or render and store\n"
                      "```\n"
                      "The rule of the cache, one step a line.\n"
                      "## Your questions\n", text)


class Parts(Build):
    def test_a_part_takes_the_title_of_its_data_part_heading(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual([{"paragraph": 1, "cue": "1.1", "start": 0.0, "title": "Opening"},
                          {"paragraph": 2, "cue": "2.1", "start": 4.1, "title": "How it broke"}], self.data(page)["parts"])

    def test_a_part_heading_without_text_is_named_by_number(self):
        code, err, page = self.build(BODY.replace(">How it broke</h2>", "></h2>"))
        self.assertEqual(0, code, err)
        self.assertEqual(["Opening", "Part 2"], [part["title"] for part in self.data(page)["parts"]])

    def test_the_fallback_titles_come_from_the_strings(self):
        (self.dir / "strings.json").write_text(json.dumps({"opening": "Суть", "part": "Часть"}), encoding="utf-8")
        code, err, page = self.build(BODY.replace(">How it broke</h2>", "></h2>"), args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual(["Суть", "Часть 2"], [part["title"] for part in self.data(page)["parts"]])


class Strings(Build):
    def strings(self, page):
        return self.data(page)["strings"]

    def test_the_defaults_are_english(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual(bp.STRINGS, self.strings(page))

    def test_the_part_words_label_and_the_write_status_have_english_defaults(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual(("Your words on this part, typed or dictated", "Add your words to any part."),
                         (self.strings(page)["partWords"], self.strings(page)["write"]))

    def test_the_part_words_label_and_the_write_status_are_overridden_from_a_file(self):
        (self.dir / "strings.json").write_text(json.dumps({"partWords": "Ваши слова к этой части", "write": "Добавьте слова к любой части."}),
                                               encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual(("Ваши слова к этой части", "Добавьте слова к любой части."),
                         (self.strings(page)["partWords"], self.strings(page)["write"]))

    PAUSE_AND_NOTES = {
        "playPart": "Play this part",
        "playNext": "Play the next part",
        "pause": "Pause",
        "resume": "Resume",
        "selectionTools": "The selected text",
        "copySelection": "Copy",
        "copiedSelection": "Copied.",
        "copySelectionFailed": "The page could not copy: use the copy command of the browser.",
        "comment": "Comment",
        "noteField": "Your comment on this piece of text, typed or dictated",
        "noteSave": "Save",
        "noteCancel": "Cancel",
        "noteDelete": "Delete",
        "noteKeys": "Enter saves, Esc closes.",
        "notes": "Comments on the text:",
        "noteEdit": "Edit",
        "noteLine": "On the text “{quote}” ({part}): {text}",
    }

    def test_the_voice_selection_and_comment_strings_have_english_defaults(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        strings = self.strings(page)
        self.assertEqual(self.PAUSE_AND_NOTES, {key: strings[key] for key in self.PAUSE_AND_NOTES})

    def test_the_voice_selection_and_comment_strings_are_overridden_from_a_file(self):
        overrides = {"playPart": "Diesen Teil abspielen", "pause": "Anhalten", "resume": "Weiter", "comment": "Kommentieren",
                     "noteLine": "Zum Text „{quote}“ ({part}): {text}"}
        (self.dir / "strings.json").write_text(json.dumps(overrides), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual(overrides, {key: self.strings(page)[key] for key in overrides})
        self.assertEqual(self.PAUSE_AND_NOTES["noteSave"], self.strings(page)["noteSave"])

    QUESTIONS = {"knew": "I had it", "missed": "I did not", "returnTo": "Worth returning to:"}

    def test_the_question_strings_have_english_defaults(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        strings = self.strings(page)
        self.assertEqual(self.QUESTIONS, {key: strings[key] for key in self.QUESTIONS})

    def test_the_question_strings_are_overridden_from_a_file(self):
        overrides = {"knew": "Я знал", "missed": "Я не знал", "returnTo": "Стоит вернуться:"}
        (self.dir / "strings.json").write_text(json.dumps(overrides), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual(overrides, {key: self.strings(page)[key] for key in overrides})

    MAP_AND_REFERENCES = {
        "map": "Map of the page",
        "mapOpen": "Show the map",
        "mapClose": "Hide the map",
        "mapFilter": "Find on the map",
        "kindFigure": "figure",
        "kindTable": "table",
        "kindPseudo": "pseudocode",
        "kindQuestion": "question",
        "kindText": "text",
        "refPanel": "The code or the source behind the text",
        "refClose": "Close",
        "refEditor": "Open in the editor",
        "refSource": "Open the source",
    }

    def test_the_map_and_reference_strings_have_english_defaults(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        strings = self.strings(page)
        self.assertEqual(self.MAP_AND_REFERENCES, {key: strings[key] for key in self.MAP_AND_REFERENCES})

    def test_a_retired_key_warns_and_is_dropped_and_the_page_builds(self):
        path = self.dir / "strings.json"
        path.write_text(json.dumps({"now": "now:", "parts": "Parts", "copy": "Copy all"}), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(path)])
        self.assertEqual(0, code, err)
        self.assertEqual([f'{path}: warning: key "now" is retired and ignored', f'{path}: warning: key "parts" is retired and ignored'],
                         err.splitlines())
        self.assertEqual("Copy all", self.strings(page)["copy"])
        self.assertEqual(set(), {"now", "parts"} & set(self.strings(page)))

    def test_every_retired_key_is_out_of_the_strings(self):
        self.assertEqual({"now", "notPlaying", "jump", "hintPause", "hintNote", "hintNoteSpoken", "noteSpoken", "parts"}, set(bp.RETIRED_STRINGS))
        self.assertEqual(set(), bp.RETIRED_STRINGS & set(bp.STRINGS))

    def test_the_look_string_has_an_english_default(self):
        self.assertEqual("Where to look", bp.STRINGS["look"])

    def test_the_strings_option_overrides_keys(self):
        (self.dir / "strings.json").write_text(json.dumps({"copy": "Скопировать ответ"}), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual("Скопировать ответ", self.strings(page)["copy"])
        self.assertEqual(bp.STRINGS["choose"], self.strings(page)["choose"])

    def test_the_config_file_is_read_without_the_option(self):
        (self.config / "handing-over-to-readers/page-strings.json").write_text(json.dumps({"copy": "Скопировать"}), encoding="utf-8")
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual("Скопировать", self.strings(page)["copy"])

    def test_home_config_is_used_when_xdg_is_empty(self):
        self.environ["XDG_CONFIG_HOME"] = ""
        (self.dir / ".config/handing-over-to-readers").mkdir(parents=True)
        (self.dir / ".config/handing-over-to-readers/page-strings.json").write_text(json.dumps({"copy": "Kopieren"}), encoding="utf-8")
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual("Kopieren", self.strings(page)["copy"])

    def test_the_option_wins_over_the_config_file(self):
        (self.config / "handing-over-to-readers/page-strings.json").write_text(json.dumps({"copy": "config"}), encoding="utf-8")
        (self.dir / "strings.json").write_text(json.dumps({"copy": "option"}), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual("option", self.strings(page)["copy"])

    def test_an_unknown_key_is_exit_2_beside_a_retired_one(self):
        (self.dir / "strings.json").write_text(json.dumps({"copyy": "Copy", "jump": "Jump"}), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(2, code)
        self.assertIn("copyy", err)
        self.assertIsNone(page)


class Output(Build):
    def test_the_closing_line_is_utf8_under_another_stream_encoding(self):
        (self.dir / "body.html").write_text(BODY, encoding="utf-8")
        (self.dir / "cues.json").write_text(json.dumps(CUES), encoding="utf-8")
        out = self.dir / "страница.html"
        env = dict(self.environ, PATH=os.environ.get("PATH", "/usr/bin:/bin"), PYTHONIOENCODING="cp1252", HANDOVER_FEEDBACK_DIR=os.environ["HANDOVER_FEEDBACK_DIR"])
        done = subprocess.run([sys.executable, str(SCRIPT), "--body", str(self.dir / "body.html"), "--cues", str(self.dir / "cues.json"),
                               "--report", str(REPORT), "--out", str(out)], capture_output=True, env=env)
        self.assertEqual(0, done.returncode, done.stderr.decode("utf-8", "replace"))
        self.assertIn(out.name, done.stdout.decode("utf-8"))

    def test_without_standalone_the_page_starts_with_title_and_has_no_document_tags(self):
        code, err, page = self.build(args=["--title", "Thumbnails & keys"])
        self.assertEqual(0, code, err)
        self.assertTrue(page.startswith("<title>Thumbnails &amp; keys</title>"), page[:80])
        self.assertIsNone(re.search(r"<(?:html|head|body)\b|<!doctype", page, re.I))

    def test_standalone_wraps_a_complete_document(self):
        code, err, page = self.build(args=["--standalone"])
        self.assertEqual(0, code, err)
        self.assertTrue(page.startswith("<!doctype html>\n<html>\n<head>\n<meta charset=\"utf-8\">"), page[:80])
        self.assertIn('<meta name="viewport"', page)
        head, body = page.split("</head>", 1)
        self.assertIn("<style>", head)
        self.assertIn("<body>", body)
        self.assertIn('id="page-data"', body)
        self.assertTrue(page.rstrip().endswith("</body>\n</html>"))

    def test_the_data_holds_cues_parts_strings_voice_id_map_and_refs(self):
        code, err, page = self.build(args=["--voice", "story.wav", "--id", "thumbs"])
        self.assertEqual(0, code, err)
        data = self.data(page)
        self.assertEqual(["cues", "id", "map", "parts", "refs", "strings", "voice"], sorted(data))
        self.assertEqual((False, {}), (data["map"], data["refs"]))
        self.assertEqual(("story.wav", "thumbs", CUES), (data["voice"], data["id"], data["cues"]))

    def test_the_defaults_are_no_voice_and_the_id_report(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual(("", "report"), (self.data(page)["voice"], self.data(page)["id"]))

    def test_the_json_survives_a_closing_script_tag_in_a_sentence(self):
        sentence = "It printed </script><script>alert(1)</script> twice."
        code, err, page = self.build(f"<p data-say>{html.escape(sentence)}</p>\n", cues=None)
        self.assertEqual(0, code, err)
        self.assertEqual(sentence, self.data(page)["cues"][0]["text"])
        self.assertIn("\\u003c/script>", page)
        self.assertEqual(1, page.count("<script>"))  # the template's own script, nothing from the sentence

    def test_an_id_with_a_slash_is_exit_2(self):
        code, err, _ = self.build(args=["--id", "answers/x"])
        self.assertEqual(2, code)
        self.assertIn("--id", err)

    def test_a_template_without_its_markers_is_exit_2(self):
        (self.dir / "template.html").write_text("<title><!--TITLE--></title>/*DATA*/", encoding="utf-8")
        code, err, _ = self.build(args=["--template", str(self.dir / "template.html")])
        self.assertEqual(2, code)
        self.assertIn("<!--BODY-->", err)

    def test_a_run_without_an_output_is_exit_2(self):
        (self.dir / "body.html").write_text(BODY, encoding="utf-8")
        code, _, err = self.run_main(["--body", str(self.dir / "body.html")])
        self.assertEqual(2, code)
        self.assertIn("at least one of --out, --story-out and --text-out", err)

    def test_an_output_that_cannot_be_written_is_exit_2(self):
        (self.dir / "body.html").write_text(BODY, encoding="utf-8")
        (self.dir / "taken").mkdir()
        code, _, err = self.run_main(["--body", str(self.dir / "body.html"), "--story-out", str(self.dir / "taken")])
        self.assertEqual(2, code)
        self.assertIn(f"cannot write {self.dir / 'taken'}", err)


class TheTemplate(unittest.TestCase):
    TEXT = (SKILL / "assets/page-template.html").read_text(encoding="utf-8")
    BUILDER_STRINGS = {"opening", "part", "look"}  # the strings the builder itself writes into the page

    def test_every_string_key_the_template_names_has_a_default(self):
        named = set(re.findall(r'data-string="(\w+)"', self.TEXT)) | set(re.findall(r"\bS\.(\w+)", self.TEXT))
        self.assertTrue(named)
        self.assertEqual(set(), named - set(bp.STRINGS))

    def test_every_default_string_is_used_by_the_template_or_the_builder(self):
        named = set(re.findall(r'data-string="(\w+)"', self.TEXT)) | set(re.findall(r"\bS\.(\w+)", self.TEXT)) | self.BUILDER_STRINGS
        self.assertEqual(set(), set(bp.STRINGS) - named)

    def test_a_part_button_is_named_by_its_label_and_the_parts_title(self):
        self.assertIn('b.setAttribute("aria-label", label + ": " + PARTS[n].title);', self.TEXT)

    def test_the_template_has_no_part_list_no_side_group_and_no_key_c(self):
        for gone in ("side-tools", "parts-toggle", "noteOnSpoken", "KeyC"):
            self.assertNotIn(gone, self.TEXT)

    def test_the_reason_of_a_decision_is_styled_outside_its_options(self):
        self.assertIn(".decision .why {", self.TEXT)
        self.assertNotIn(".option .why", self.TEXT)

    def test_the_copy_bar_follows_the_last_field_of_the_page(self):
        self.assertIn("compareDocumentPosition", self.TEXT)

    def test_a_hidden_element_stays_hidden_under_a_class_that_sets_display(self):
        self.assertIn("[hidden] { display: none !important; }", self.TEXT)

    def test_the_blocks_of_an_explanation_take_the_rules_of_the_article(self):
        """The pre of figure.pseudo is a pre of the article, one line a step that scrolls inside the figure; a span of it
        lights as every span does; the cells of figure.factor take the colours of a verdict."""
        pre = re.search(r"^\.sheet pre \{([^}]*)\}", self.TEXT, re.M).group(1)
        self.assertEqual(("white-space: pre;", "overflow-x: auto;"), tuple(rule for rule in ("white-space: pre;", "overflow-x: auto;") if rule in pre))
        self.assertRegex(self.TEXT, r"\.sheet :is\([^)]*\bspan\b[^)]*\)\.lit \{ background: var\(--lit\);")
        self.assertIn("figure td.good { color: var(--keep); } figure td.bad { color: var(--drop); }", self.TEXT)

    def test_the_template_labels_the_marks_the_return_list_the_map_and_the_references_from_the_strings(self):
        for key in ("knew", "missed", "returnTo", "map", "mapOpen", "mapClose", "refPanel", "refClose", "refEditor", "refSource"):
            self.assertRegex(self.TEXT, rf"\bS\.{key}\b")

    def test_the_answer_bar_has_a_class_of_its_own_beside_the_answer_of_a_question(self):
        self.assertIn('el("div", "answer-bar")', self.TEXT)
        self.assertIsNone(re.search(r"^\.answer\s*\{", self.TEXT, re.M))

    def test_the_template_adds_the_part_fields_and_keeps_their_remarks(self):
        for name in (r"\bS\.partWords\b", r"\bS\.write\b", r"\bremarks\b", r'"part-words-"'):
            self.assertRegex(self.TEXT, name)

    def test_the_template_loads_nothing_from_elsewhere(self):
        self.assertIsNone(re.search(r"https?:|<script[^>]+src=|<link\b", self.TEXT))

    def test_the_template_holds_no_cyrillic_letter_and_no_word_of_the_prototype(self):
        self.assertIsNone(re.search("[\u0400-\u04ff]", self.TEXT))
        for word in ("PROTO", "corner"):
            self.assertNotIn(word, self.TEXT)


class Example(Build):
    FIXTURE_CUES = json.loads((FIXTURES / "cues.json").read_text(encoding="utf-8"))

    def test_the_example_body_builds_with_every_sentence_on_the_page(self):
        cues = self.FIXTURE_CUES
        code, err, page = self.build(EXAMPLE_BODY.read_text(encoding="utf-8"), cues=cues,
                                     args=["--root", str(FIXTURES / "repo"), "--standalone", "--voice", "story.wav"])
        self.assertEqual(0, code, err)
        self.assertEqual("", err)
        spoken = {f"{c['paragraph']}.{c['sentence']}" for c in cues}
        on_page = {name for value in re.findall(r'data-lit="([^"]+)"', page) for name in value.split()}
        self.assertEqual(spoken, on_page)
        # The part headings light 2.1, 3.1 and 4.1, the two option blocks 4.3 and 4.4; every other sentence is written out.
        written = [f"{c['paragraph']}.{c['sentence']}" for c in cues if f"{c['paragraph']}.{c['sentence']}" not in {"2.1", "3.1", "4.1", "4.3", "4.4"}]
        self.assertEqual(written, re.findall(r'<span class="s" data-lit="([^"]+)">', page))
        self.assertIn(html.escape(cues[0]["text"], quote=False), page)
        self.assertEqual(["Opening", "How it broke", "What is left", "What to decide"], [p["title"] for p in self.data(page)["parts"]])
        look = page[page.index('<section class="look"'):]
        self.assertEqual(4, look.count('<li class="look-item">'))
        self.assertEqual(2, look.count("<details>"))
        self.assertEqual(1, page.count('class="decision"'))

    def test_the_example_lights_the_table_cells_by_the_names_of_their_sentences(self):
        code, err, page = self.build(EXAMPLE_BODY.read_text(encoding="utf-8"), cues=self.FIXTURE_CUES)
        self.assertEqual(0, code, err)
        self.assertIn('<th data-lit="2.3">key before</th><th data-lit="2.6">key now</th>', page)
        self.assertIn('<td class="bad" data-lit="2.5"><code>thumb:42</code>, the old thumbnail</td>', page)

    def test_the_reason_stands_after_the_options_and_before_the_question(self):
        code, err, page = self.build(EXAMPLE_BODY.read_text(encoding="utf-8"), cues=self.FIXTURE_CUES)
        self.assertEqual(0, code, err)
        decision = page[page.index('<section class="decision"'):]
        self.assertLess(decision.rindex('class="option"'), decision.index('<p class="why"'))
        self.assertLess(decision.index('<p class="why"'), decision.index('<p class="ask"'))

    def test_the_story_of_the_example_is_the_story_of_the_fixture_cues(self):
        story = self.dir / "story.txt"
        code, _, err = self.run_main(["--body", str(EXAMPLE_BODY), "--story-out", str(story)])
        self.assertEqual(0, code, err)
        self.assertEqual((FIXTURES / "story.txt").read_text(encoding="utf-8"), story.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
