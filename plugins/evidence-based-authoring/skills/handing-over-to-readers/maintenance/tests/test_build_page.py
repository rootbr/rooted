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
EXAMPLE_BODY = SKILL / "assets/page-body-example.html"

# Two paragraphs: an opening of two sentences and a part of two sentences.
CUES = [
    {"paragraph": 1, "sentence": 1, "text": "The cache served old thumbnails.", "start": 0.0, "end": 2.0},
    {"paragraph": 1, "sentence": 2, "text": "Now it does not.", "start": 2.3, "end": 3.5},
    {"paragraph": 2, "sentence": 1, "text": "How it broke.", "start": 4.1, "end": 5.0},
    {"paragraph": 2, "sentence": 2, "text": "The key had no version.", "start": 5.3, "end": 7.0},
]
BODY = '<p data-say="1.1 1.2"></p>\n<h2 data-lit="2.1">How it broke</h2>\n<p data-say="2.2"></p>\n'
DECISION = ('<section class="decision" data-decision="purge" data-title="Old thumbnails">'
            '<div class="option" data-option="purge" data-mine="1"><h4>Purge</h4></div>'
            '<div class="option" data-option="wait"><h4>Wait</h4></div></section>\n')


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

    def build(self, body=BODY, cues=None, report=None, args=()):
        """(exit code, stderr, page text or None)."""
        (self.dir / "body.html").write_text(body, encoding="utf-8")
        (self.dir / "cues.json").write_text(json.dumps(CUES if cues is None else cues), encoding="utf-8")
        report_path = FIXTURES / "report.md"
        if report is not None:
            report_path = self.dir / "report.md"
            report_path.write_text(report, encoding="utf-8")
        out = self.dir / "page.html"
        argv = ["--body", str(self.dir / "body.html"), "--cues", str(self.dir / "cues.json"),
                "--report", str(report_path), "--out", str(out), *args]
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            code = bp.main(argv, self.environ)
        return code, err.getvalue(), out.read_text(encoding="utf-8") if out.exists() else None

    def data(self, page):
        block = re.search(r'<script type="application/json" id="page-data">(.*?)</script>', page, re.S)
        return json.loads(block.group(1))


class Expansion(Build):
    def test_data_say_is_filled_with_one_span_per_sentence(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertIn('<p data-say="1.1 1.2"><span class="s" data-lit="1.1">The cache served old thumbnails.</span> '
                      '<span class="s" data-lit="1.2">Now it does not.</span></p>', page)
        self.assertIn('<p data-say="2.2"><span class="s" data-lit="2.2">The key had no version.</span></p>', page)

    def test_the_sentence_text_is_escaped(self):
        cues = [dict(CUES[0], text="A <b> & C."), *CUES[1:]]
        code, err, page = self.build(cues=cues)
        self.assertEqual(0, code, err)
        self.assertIn('<span class="s" data-lit="1.1">A &lt;b&gt; &amp; C.</span>', page)


class Violations(Build):
    def assertViolation(self, body, fragment, cues=None):
        code, err, page = self.build(body, cues=cues)
        self.assertEqual(1, code, err)
        self.assertIn(fragment, err)
        self.assertIsNone(page)

    def test_a_cue_id_the_cues_do_not_have(self):
        self.assertViolation(BODY + '<p data-say="3.1"></p>', "data-say names 3.1, which the cues do not have")

    def test_a_data_lit_id_the_cues_do_not_have(self):
        self.assertViolation(BODY + '<figure data-lit="2.9"></figure>', "data-lit names 2.9")

    def test_a_spoken_sentence_on_no_element(self):
        self.assertViolation('<p data-say="1.1 1.2"></p>\n<h2 data-lit="2.1">How</h2>\n', "spoken sentence 2.2 lands on no element")

    def test_a_non_empty_data_say_element(self):
        self.assertViolation(BODY.replace('<p data-say="2.2"></p>', '<p data-say="2.2">typed by hand</p>'), "body.html:3: <p data-say> holds content")

    def test_a_child_element_in_data_say(self):
        self.assertViolation(BODY.replace('<p data-say="2.2"></p>', '<p data-say="2.2"><b></b></p>'), "holds content")

    def test_a_sentence_written_twice(self):
        self.assertViolation(BODY + '<p data-say="2.2"></p>', "sentence 2.2 is written twice")

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
        code, err, _ = self.build(BODY + '<p data-say="3.1"></p><script></script>')
        self.assertEqual(1, code)
        self.assertEqual(2, len(err.strip().splitlines()), err)


class Parts(Build):
    def test_a_part_takes_the_title_of_the_h2_that_lights_its_first_sentence(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual([{"paragraph": 1, "cue": "1.1", "start": 0.0, "title": "Opening"},
                          {"paragraph": 2, "cue": "2.1", "start": 4.1, "title": "How it broke"}], self.data(page)["parts"])

    def test_a_part_without_its_h2_is_named_by_number(self):
        code, err, page = self.build('<p data-say="1.1 1.2 2.1 2.2"></p>')
        self.assertEqual(0, code, err)
        self.assertEqual(["Opening", "Part 2"], [part["title"] for part in self.data(page)["parts"]])

    def test_the_fallback_titles_come_from_the_strings(self):
        (self.dir / "strings.json").write_text(json.dumps({"opening": "Суть", "part": "Часть"}), encoding="utf-8")
        code, err, page = self.build('<p data-say="1.1 1.2 2.1 2.2"></p>', args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual(["Суть", "Часть 2"], [part["title"] for part in self.data(page)["parts"]])


class WhereToLook(Build):
    REPORT = ("Opening.\n\n## Where to look\n\n"
              "- the key: `src/cache/ThumbKey.java:23` `\":v\" + version`\n"
              "- past the end: `src/cache/ThumbKey.java:99`\n"
              "- outside the root: `../page/report.md:1`\n"
              "- the tests: 9 of 9 passed\n")

    def look(self, page):
        return page[page.index('<section class="look"'):]

    def test_a_resolving_anchor_opens_three_lines_around_it(self):
        code, err, page = self.build(report=self.REPORT, args=["--root", str(FIXTURES / "repo")])
        self.assertEqual(0, code, err)
        first = self.look(page).split("</li>")[0]
        self.assertIn("<summary>the key: <code>src/cache/ThumbKey.java:23</code> <code>&quot;:v&quot; + version</code></summary>", first)
        self.assertEqual(["20", "21", "22", "23", "24", "25", "26"], re.findall(r'<span class="ln">(\d+)</span>', first))
        self.assertEqual(1, first.count('<span class="hit">'))
        self.assertIn('<span class="hit"><span class="ln">23</span>          return &quot;thumb:&quot;', first)

    def test_an_anchor_past_the_end_of_its_file_is_shown_as_text(self):
        code, err, page = self.build(report=self.REPORT, args=["--root", str(FIXTURES / "repo")])
        self.assertEqual(0, code, err)
        self.assertIn('<li class="look-item">past the end: <code>src/cache/ThumbKey.java:99</code></li>', self.look(page))

    def test_an_anchor_outside_the_root_is_shown_as_text(self):
        code, err, page = self.build(report=self.REPORT, args=["--root", str(FIXTURES / "repo")])
        self.assertEqual(0, code, err)
        self.assertIn('<li class="look-item">outside the root: <code>../page/report.md:1</code></li>', self.look(page))

    def test_an_item_without_an_anchor_is_shown_as_text(self):
        code, err, page = self.build(report=self.REPORT, args=["--root", str(FIXTURES / "repo")])
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
        "hintPause": "Pause: click the text, press Space, or use the button beside the spoken sentence.",
        "hintNote": "Comment: select a piece of text.",
        "hintNoteSpoken": "Press C to comment on the spoken sentence.",
        "pause": "Pause",
        "resume": "Resume",
        "noteSpoken": "Comment on the spoken sentence",
        "noteField": "Your comment on this piece of text, typed or dictated",
        "noteSave": "Save",
        "noteCancel": "Cancel",
        "noteDelete": "Delete",
        "noteKeys": "Enter saves, Esc closes.",
        "notes": "Comments on the text:",
        "noteEdit": "Edit",
        "noteLine": "On the text “{quote}” ({part}): {text}",
    }

    def test_the_pause_and_comment_strings_have_english_defaults(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        strings = self.strings(page)
        self.assertEqual(self.PAUSE_AND_NOTES, {key: strings[key] for key in self.PAUSE_AND_NOTES})

    def test_the_pause_and_comment_strings_are_overridden_from_a_file(self):
        overrides = {"pause": "Anhalten", "resume": "Weiter", "noteLine": "Zum Text „{quote}“ ({part}): {text}"}
        (self.dir / "strings.json").write_text(json.dumps(overrides), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual(overrides, {key: self.strings(page)[key] for key in overrides})
        self.assertEqual(self.PAUSE_AND_NOTES["noteSave"], self.strings(page)["noteSave"])

    def test_the_strings_option_overrides_keys(self):
        (self.dir / "strings.json").write_text(json.dumps({"copy": "Скопировать ответ"}), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual("Скопировать ответ", self.strings(page)["copy"])
        self.assertEqual(bp.STRINGS["choose"], self.strings(page)["choose"])

    def test_the_config_file_is_read_without_the_option(self):
        (self.config / "handing-over-to-readers/page-strings.json").write_text(json.dumps({"now": "сейчас:"}), encoding="utf-8")
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual("сейчас:", self.strings(page)["now"])

    def test_home_config_is_used_when_xdg_is_empty(self):
        self.environ["XDG_CONFIG_HOME"] = ""
        (self.dir / ".config/handing-over-to-readers").mkdir(parents=True)
        (self.dir / ".config/handing-over-to-readers/page-strings.json").write_text(json.dumps({"now": "jetzt:"}), encoding="utf-8")
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual("jetzt:", self.strings(page)["now"])

    def test_the_option_wins_over_the_config_file(self):
        (self.config / "handing-over-to-readers/page-strings.json").write_text(json.dumps({"now": "config"}), encoding="utf-8")
        (self.dir / "strings.json").write_text(json.dumps({"now": "option"}), encoding="utf-8")
        code, err, page = self.build(args=["--strings", str(self.dir / "strings.json")])
        self.assertEqual(0, code, err)
        self.assertEqual("option", self.strings(page)["now"])

    def test_an_unknown_key_is_exit_2(self):
        (self.dir / "strings.json").write_text(json.dumps({"copyy": "Copy"}), encoding="utf-8")
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
                               "--report", str(FIXTURES / "report.md"), "--out", str(out)], capture_output=True, env=env)
        self.assertEqual(done.returncode, 0, done.stderr.decode("utf-8", "replace"))
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

    def test_the_data_holds_cues_parts_strings_voice_and_id(self):
        code, err, page = self.build(args=["--voice", "story.wav", "--id", "thumbs"])
        self.assertEqual(0, code, err)
        data = self.data(page)
        self.assertEqual(["cues", "id", "parts", "strings", "voice"], sorted(data))
        self.assertEqual(("story.wav", "thumbs", CUES), (data["voice"], data["id"], data["cues"]))

    def test_the_defaults_are_no_voice_and_the_id_report(self):
        code, err, page = self.build()
        self.assertEqual(0, code, err)
        self.assertEqual(("", "report"), (self.data(page)["voice"], self.data(page)["id"]))

    def test_the_json_survives_a_closing_script_tag_in_a_sentence(self):
        cues = [dict(CUES[0], text="It printed </script><script>alert(1)</script> twice."), *CUES[1:]]
        code, err, page = self.build(cues=cues)
        self.assertEqual(0, code, err)
        self.assertEqual(cues[0]["text"], self.data(page)["cues"][0]["text"])
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

    def test_unreadable_cues_are_exit_2(self):
        code, err, page = self.build(cues=[{"paragraph": 1}])
        self.assertEqual(2, code)
        self.assertIn("entry 1", err)
        self.assertIsNone(page)


class TheTemplate(unittest.TestCase):
    TEXT = (SKILL / "assets/page-template.html").read_text(encoding="utf-8")

    def test_every_string_key_the_template_names_has_a_default(self):
        named = set(re.findall(r'data-string="(\w+)"', self.TEXT)) | set(re.findall(r"\bS\.(\w+)", self.TEXT))
        self.assertTrue(named)
        self.assertEqual(set(), named - set(bp.STRINGS))

    def test_every_default_string_is_used_by_the_template_or_the_parts(self):
        named = set(re.findall(r'data-string="(\w+)"', self.TEXT)) | set(re.findall(r"\bS\.(\w+)", self.TEXT)) | {"opening", "part"}
        self.assertEqual(set(), set(bp.STRINGS) - named)

    def test_the_copy_bar_follows_the_last_field_of_the_page(self):
        self.assertIn("compareDocumentPosition", self.TEXT)

    def test_a_hidden_element_stays_hidden_under_a_class_that_sets_display(self):
        self.assertIn("[hidden] { display: none !important; }", self.TEXT)

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
    def test_the_example_body_builds_with_every_sentence_on_the_page(self):
        cues = json.loads((FIXTURES / "cues.json").read_text(encoding="utf-8"))
        code, err, page = self.build(EXAMPLE_BODY.read_text(encoding="utf-8"), cues=cues,
                                     args=["--root", str(FIXTURES / "repo"), "--standalone", "--voice", "story.wav"])
        self.assertEqual(0, code, err)
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


if __name__ == "__main__":
    unittest.main()
