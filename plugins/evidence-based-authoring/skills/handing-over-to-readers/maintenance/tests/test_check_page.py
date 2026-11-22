"""check_page.py: a built page checked in a browser without a window, its script errors, the text outside the frame
of its figure, the pictures of its parts, and the runs that find no browser or no page.

The classes Clean and Findings build pages with build_page.py and run the Chrome or Chromium that check_page.py finds;
without one they are skipped with the reason. FakeBrowser runs check_page.py against fixtures/page/fake_browser.py,
which answers as a browser would without loading the page, wherever a script starts by its first line (POSIX). The
other classes need neither.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shlex
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SKILL = Path(__file__).resolve().parents[2]
SCRIPT = SKILL / "scripts/check_page.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures/page"
EXAMPLE_BODY = SKILL / "assets/page-body-example.html"
EXAMPLE_PICTURES = [f"{name}-{theme}.png" for name in ("01-opening", "02-how-it-broke", "03-what-is-left", "04-what-to-decide")
                    for theme in ("dark", "light")]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_SIZE = slice(16, 24)  # the width and the height, two big-endian 32-bit numbers in the header chunk of a PNG


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


cp = load("check_page", SCRIPT)
bp = load("build_page", SKILL / "scripts/build_page.py")
CHROME = cp.find_browser(None, os.environ)


def setUpModule():
    """Every run of a script in this module, in process or as a child, journals into a temporary directory, never the user's own."""
    feedback = tempfile.TemporaryDirectory(prefix="handover-feedback-")
    unittest.addModuleCleanup(feedback.cleanup)
    environment = mock.patch.dict(os.environ, {"HANDOVER_FEEDBACK_DIR": feedback.name})
    environment.start()
    unittest.addModuleCleanup(environment.stop)


def build(folder: Path, body: str, *args: str) -> Path:
    """The standalone page of `body`, built in `folder` with an empty configuration, so the strings are the defaults."""
    (folder / "config").mkdir(exist_ok=True)
    (folder / "body.html").write_text(body, encoding="utf-8")
    page = folder / "page.html"
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        code = bp.main(["--body", str(folder / "body.html"), "--out", str(page), "--standalone", *args],
                       {"XDG_CONFIG_HOME": str(folder / "config"), "HOME": str(folder)})
    if code != 0:
        raise AssertionError(f"build_page exit {code}: {err.getvalue()}")
    return page


def check(*args: str, env: dict | None = None) -> tuple[int, list[str], str]:
    """A run as a caller makes it, under -I: (exit code, stdout lines, stderr)."""
    done = subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8",
                          env=os.environ if env is None else env)
    return done.returncode, done.stdout.splitlines(), done.stderr


def fingerprint(path: Path) -> tuple[str, int]:
    return hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns


def figure_body(figure: str) -> str:
    return f'<h1>A figure</h1>\n<p data-say>The figure shows one thing.</p>\n<figure>\n{figure}\n<figcaption>One thing.</figcaption>\n</figure>\n'


def svg(content: str) -> str:
    return f'<div class="figscroll"><svg class="fig" viewBox="0 0 720 120" role="img">{content}</svg></div>'


@unittest.skipIf(CHROME is None, "no browser: set $CHROME or install Google Chrome, google-chrome, chromium or chromium-browser")
class Clean(unittest.TestCase):
    """The example page with its voice and its "Where to look", checked once with --shots."""

    @classmethod
    def setUpClass(cls):
        work = tempfile.TemporaryDirectory(prefix="check-page-clean-")
        cls.addClassCleanup(work.cleanup)
        folder = Path(work.name)
        (folder / "cues.json").write_text((FIXTURES / "cues.json").read_text(encoding="utf-8"), encoding="utf-8")
        cls.page = build(folder, EXAMPLE_BODY.read_text(encoding="utf-8"), "--cues", str(folder / "cues.json"), "--voice", "story.wav",
                         "--report", str(FIXTURES / "report.md"), "--root", str(FIXTURES / "repo"))
        cls.shots = folder / "shots"
        before = fingerprint(cls.page)
        cls.code, cls.out, cls.err = check(str(cls.page), "--shots", str(cls.shots))
        cls.unchanged = fingerprint(cls.page) == before

    def test_the_example_page_is_exit_0_with_no_finding(self):
        self.assertEqual((0, [f"{self.page}: 4 part(s), 0 finding(s), 8 picture(s) in {self.shots}"]), (self.code, self.out), self.err)

    def test_shots_writes_two_pictures_per_part_named_by_number_title_and_theme(self):
        self.assertEqual(EXAMPLE_PICTURES, sorted(path.name for path in self.shots.iterdir()))

    def test_every_picture_is_a_png_as_wide_as_the_window_and_at_most_4000_pixels_tall(self):
        sizes = {}
        for path in self.shots.iterdir():
            head = path.read_bytes()[:PNG_SIZE.stop]
            self.assertEqual(PNG_SIGNATURE, head[:len(PNG_SIGNATURE)], path.name)
            sizes[path.name] = struct.unpack(">II", head[PNG_SIZE])
        self.assertEqual({cp.WIDTH}, {width for width, _ in sizes.values()})
        self.assertTrue(all(0 < height <= cp.SHOT_HEIGHT_CAP for _, height in sizes.values()), sizes)

    def test_the_checked_page_file_is_unchanged(self):
        self.assertTrue(self.unchanged)


@unittest.skipIf(CHROME is None, "no browser: set $CHROME or install Google Chrome, google-chrome, chromium or chromium-browser")
class ExplanationBlocks(unittest.TestCase):
    """The explanation fixture, its pseudocode with lit lines and a link, its tables of questions, of a factor and of
    terms and its question, checked once with --shots: every block stays inside its frame."""

    @classmethod
    def setUpClass(cls):
        work = tempfile.TemporaryDirectory(prefix="check-page-explanation-")
        cls.addClassCleanup(work.cleanup)
        folder = Path(work.name)
        cls.page = build(folder, (FIXTURES / "explanation-body.html").read_text(encoding="utf-8"), "--explanation")
        cls.shots = folder / "shots"
        cls.code, cls.out, cls.err = check(str(cls.page), "--shots", str(cls.shots))

    def test_the_explanation_page_is_exit_0_with_no_finding(self):
        self.assertEqual((0, [f"{self.page}: 4 part(s), 0 finding(s), 8 picture(s) in {self.shots}"]), (self.code, self.out), self.err)


@unittest.skipIf(CHROME is None, "no browser: set $CHROME or install Google Chrome, google-chrome, chromium or chromium-browser")
class Findings(unittest.TestCase):
    """Four pages, each with one kind of defect, each checked once."""
    WIDE_LABEL = "a label far too wide for its small box"
    FAR_LABEL = "a label past the right edge"
    PAGES = {
        "wide": figure_body(svg(f'<g><rect class="box" x="340" y="30" width="80" height="48"/>'
                                f'<text x="380" y="59" text-anchor="middle">{WIDE_LABEL}</text></g>')),
        "far": figure_body(svg(f'<text x="690" y="20">{FAR_LABEL}</text>')),
        "frames": figure_body('<div class="figscroll"><table style="min-width: 1400px"><tr><td>a very wide table</td></tr></table></div>')
                  + '<figure><p style="width: 1400px">a paragraph wider than its figure</p></figure>\n',
        "throws": figure_body(svg('<g><rect class="box" x="300" y="30" width="200" height="48"/><text x="400" y="59" text-anchor="middle">fits</text></g>')),
    }

    @classmethod
    def setUpClass(cls):
        work = tempfile.TemporaryDirectory(prefix="check-page-findings-")
        cls.addClassCleanup(work.cleanup)
        cls.seen, cls.pages = {}, {}
        for name, body in cls.PAGES.items():
            folder = Path(work.name) / name
            folder.mkdir()
            page = build(folder, body)
            if name == "throws":
                page.write_text(page.read_text(encoding="utf-8").replace("</body>", "<script>\nnull.missing;\n</script>\n</body>"), encoding="utf-8")
            before = fingerprint(page)
            cls.seen[name] = check(str(page))
            cls.pages[name] = (page, before == fingerprint(page))

    def findings(self, name):
        code, out, _ = self.seen[name]
        return code, out[:-1]

    def test_an_svg_label_wider_than_its_box_is_exit_1_with_a_figure_line(self):
        self.assertEqual((1, [f"check_page: figure: wider than its box: {self.WIDE_LABEL}"]), self.findings("wide"))

    def test_a_text_outside_the_viewbox_is_exit_1_with_a_figure_line(self):
        self.assertEqual((1, [f"check_page: figure: outside the viewBox: {self.FAR_LABEL}"]), self.findings("far"))

    def test_a_figure_that_scrolls_sideways_and_an_element_past_its_frame_are_figure_lines(self):
        self.assertEqual((1, ["check_page: figure: scrolls sideways: One thing.", "check_page: figure: past the frame: a paragraph wider than its figure"]),
                         self.findings("frames"))

    def test_a_page_whose_script_throws_is_exit_1_with_a_script_line_naming_the_line_of_the_page(self):
        page, _ = self.pages["throws"]
        line = page.read_text(encoding="utf-8").splitlines().index("null.missing;") + 1
        code, lines = self.findings("throws")
        self.assertEqual((1, 1), (code, len(lines)), lines)
        self.assertTrue(lines[0].startswith("check_page: script: ") and "missing" in lines[0], lines[0])
        self.assertTrue(lines[0].endswith(f"(line {line})"), lines[0])

    def test_the_checked_page_files_are_unchanged(self):
        self.assertEqual({name: True for name in self.PAGES}, {name: unchanged for name, (_, unchanged) in self.pages.items()})

    def test_the_closing_line_counts_the_parts_and_the_findings(self):
        page, _ = self.pages["frames"]
        self.assertEqual(f"{page}: 1 part(s), 2 finding(s), 0 picture(s)", self.seen["frames"][1][-1])


@unittest.skipIf(os.name != "posix", "the fake browser is started by its first line, as POSIX starts a script")
class FakeBrowser(unittest.TestCase):
    """check_page.py with fixtures/page/fake_browser.py as its browser: what it passes and how it reads the answers."""
    PROBE = {"errors": [], "figures": [], "parts": [{"title": "Opening", "top": 0, "bottom": 300},
                                                    {"title": "How it broke", "top": 300, "bottom": 5300}]}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.browser = self.dir / "fake-browser"
        self.browser.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} {shlex.quote(str(FIXTURES / 'fake_browser.py'))} \"$@\"\n", encoding="utf-8")
        self.browser.chmod(0o755)
        self.page = self.dir / "page.html"
        self.page.write_text("<!doctype html>\n<title>A page</title>\n<p>Text.</p>\n", encoding="utf-8")
        self.log = self.dir / "runs.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def run_fake(self, *args, probe=None, picture=False):
        env = {**os.environ, "FAKE_BROWSER_LOG": str(self.log)}
        if probe is not None:
            env["FAKE_BROWSER_PROBE"] = json.dumps(probe)
        if picture:
            env["FAKE_BROWSER_PICTURE"] = "1"
        return check(str(self.page), "--chrome", str(self.browser), *args, env=env)

    def runs(self):
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]

    def test_a_browser_that_leaves_no_measurement_is_exit_1_with_the_probe_line(self):
        self.assertEqual((1, ["check_page: probe: the page did not finish loading", f"{self.page}: 0 part(s), 1 finding(s), 0 picture(s)"]),
                         self.run_fake()[:2])

    def test_a_measurement_of_another_form_is_the_probe_line(self):
        code, out, _ = self.run_fake(probe={**self.PROBE, "errors": "not a list"})
        self.assertEqual((1, ["check_page: probe: the page did not finish loading"]), (code, out[:-1]))

    def test_errors_and_figures_of_the_measurement_print_one_line_each_and_a_long_text_is_cut(self):
        long_label = "ж" * 70
        probe = {**self.PROBE, "errors": ["Uncaught Error: boom\n  at the second line (line 12)"],
                 "figures": [{"rule": "outside the viewBox", "text": long_label}]}
        code, out, _ = self.run_fake(probe=probe)
        self.assertEqual((1, ["check_page: script: Uncaught Error: boom at the second line (line 12)",
                              f"check_page: figure: outside the viewBox: {'ж' * 59}…"]), (code, out[:-1]))

    def test_pictures_are_named_by_number_title_and_theme(self):
        code, out, err = self.run_fake("--shots", str(self.dir / "shots"), probe=self.PROBE, picture=True)
        self.assertEqual((0, [f"{self.page}: 2 part(s), 0 finding(s), 4 picture(s) in {self.dir / 'shots'}"]), (code, out), err)
        self.assertEqual(["01-opening-dark.png", "01-opening-light.png", "02-how-it-broke-dark.png", "02-how-it-broke-light.png"],
                         sorted(path.name for path in (self.dir / "shots").iterdir()))

    def test_a_picture_the_browser_did_not_write_is_a_shot_line_per_theme(self):
        code, out, _ = self.run_fake("--shots", str(self.dir / "shots"), probe=self.PROBE)
        self.assertEqual((1, ["check_page: shot: Opening (light)", "check_page: shot: Opening (dark)",
                              "check_page: shot: How it broke (light)", "check_page: shot: How it broke (dark)"]), (code, out[:-1]))

    def test_a_part_whose_heading_is_not_on_the_page_has_no_picture(self):
        probe = {**self.PROBE, "parts": [{"title": "Opening", "top": 0, "bottom": 300}, {"title": "Lost", "top": None, "bottom": 300}]}
        code, out, _ = self.run_fake("--shots", str(self.dir / "shots"), probe=probe, picture=True)
        self.assertEqual((1, ["check_page: shot: Lost (light)", "check_page: shot: Lost (dark)"]), (code, out[:-1]))
        self.assertEqual(2, len(self.runs()) - 1)

    def test_the_window_of_a_picture_is_as_tall_as_its_part_and_at_most_4000_pixels(self):
        self.run_fake("--shots", str(self.dir / "shots"), probe=self.PROBE, picture=True)
        sizes = [next(a for a in run if a.startswith("--window-size=")) for run in self.runs()]
        self.assertEqual([f"--window-size={cp.WIDTH},{cp.PROBE_HEIGHT}"] + [f"--window-size={cp.WIDTH},300"] * 2 + [f"--window-size={cp.WIDTH},4000"] * 2,
                         sizes)

    def test_the_width_option_sets_the_window_width(self):
        self.run_fake("--width", "900", probe=self.PROBE)
        self.assertIn(f"--window-size=900,{cp.PROBE_HEIGHT}", self.runs()[0])

    def test_each_run_gets_the_flags_and_no_address_but_its_copy_in_a_temporary_directory_removed_afterwards(self):
        self.run_fake("--shots", str(self.dir / "shots"), probe=self.PROBE, picture=True)
        runs = self.runs()
        for run in runs:
            profile = Path(next(a for a in run if a.startswith("--user-data-dir=")).split("=", 1)[1])
            copy = run[-1]
            self.assertEqual(list(cp.FLAGS), [a for a in run if a in cp.FLAGS])
            self.assertEqual([copy], [a for a in run if "://" in a])
            self.assertTrue(copy.startswith((profile.parent.as_uri() + "/")), (copy, profile))
            self.assertNotEqual(self.page.as_uri(), copy)
            self.assertFalse(profile.parent.exists())
        self.assertEqual(["--dump-dom"] + ["--screenshot"] * 4, [run[-2].split("=")[0] for run in runs])

    def test_the_checked_page_file_is_unchanged(self):
        before = fingerprint(self.page)
        self.run_fake("--shots", str(self.dir / "shots"), probe=self.PROBE, picture=True)
        self.assertEqual(before, fingerprint(self.page))

    def test_a_shots_directory_that_cannot_be_made_is_exit_2(self):
        (self.dir / "a-file").write_text("", encoding="utf-8")
        code, out, err = self.run_fake("--shots", str(self.dir / "a-file" / "shots"), probe=self.PROBE)
        self.assertEqual((2, []), (code, out))
        self.assertTrue(err.startswith("check_page: cannot write pictures into "), err)


class NoBrowser(unittest.TestCase):
    """The runs that find no browser or no page; they need neither."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.empty = self.dir / "empty"
        self.empty.mkdir()
        self.page = self.dir / "page.html"
        self.page.write_text("<title>A page</title>\n", encoding="utf-8")
        self.env = {"PATH": str(self.empty), "HOME": str(self.dir), "HANDOVER_FEEDBACK_DIR": os.environ["HANDOVER_FEEDBACK_DIR"]}

    def tearDown(self):
        self._tmp.cleanup()

    def test_a_named_browser_that_is_not_there_is_exit_3_and_the_page_is_not_checked(self):
        code, out, err = check(str(self.page), "--chrome", str(self.dir / "no-browser"), env=self.env)
        self.assertEqual((3, [], "check_page: no browser found: the page was not checked\n"), (code, out, err))

    def test_a_browser_named_by_the_variable_that_is_not_there_is_exit_3(self):
        code, _, err = check(str(self.page), env={**self.env, "CHROME": str(self.dir / "no-browser")})
        self.assertEqual((3, "check_page: no browser found: the page was not checked\n"), (code, err))

    def test_without_a_named_browser_the_search_finds_none_on_an_empty_machine(self):
        self.assertIsNone(cp.find_browser(None, {"PATH": str(self.empty)}, mac_app=self.dir / "absent"))

    @unittest.skipIf(os.name != "posix", "an executable file is marked by its mode on POSIX")
    def test_the_search_takes_the_option_then_the_variable_then_the_application_then_path(self):
        found = {name: self.empty / name for name in ("option", "variable", "application", "chromium")}
        for path in found.values():
            path.write_text("#!/bin/sh\n", encoding="utf-8")
            path.chmod(0o755)
        environ = {"PATH": str(self.empty), "CHROME": str(found["variable"])}
        cases = [
            (str(found["option"]), environ, found["application"], str(found["option"])),
            (None, environ, found["application"], str(found["variable"])),
            (None, {"PATH": str(self.empty)}, found["application"], str(found["application"])),
            (None, {"PATH": str(self.empty)}, self.dir / "absent", str(found["chromium"])),
            (None, {"PATH": str(self.empty), "CHROME": "chromium"}, self.dir / "absent", str(found["chromium"])),
        ]
        for named, env, application, expected in cases:
            self.assertEqual((named, expected), (named, cp.find_browser(named, env, mac_app=application)))

    def test_an_absent_page_is_exit_2(self):
        code, out, err = check(str(self.dir / "absent.html"), "--chrome", str(self.dir / "no-browser"), env=self.env)
        self.assertEqual((2, []), (code, out))
        self.assertTrue(err.startswith(f"check_page: cannot read the page {self.dir / 'absent.html'}: "), err)

    def test_a_page_that_is_not_utf8_is_exit_2(self):
        self.page.write_bytes("<title>Seite für Ä</title>".encode("latin-1"))
        code, _, err = check(str(self.page), env=self.env)
        self.assertEqual(2, code)
        self.assertTrue(err.startswith("check_page: cannot read the page "), err)

    def test_a_width_below_one_pixel_is_exit_2(self):
        code, _, err = check(str(self.page), "--width", "0", env=self.env)
        self.assertEqual(2, code)
        self.assertIn("0 is not a width in pixels", err)


class TheCopy(unittest.TestCase):
    """What the browser runs on: the page with the two scripts on lines it already has."""
    PAGE = "<!doctype html>\n<html>\n<head><title>T</title></head>\n<body>\n<p>one</p>\n<script>\nwork();\n</script>\n</body>\n</html>\n"

    def test_the_scripts_stand_before_and_after_the_page_and_every_line_keeps_its_number(self):
        copy = cp.with_scripts(self.PAGE, "BEFORE", "AFTER")
        self.assertEqual(self.PAGE.replace("<!doctype html>", '<!doctype html><meta charset="utf-8"><script>BEFORE</script>', 1)
                         .replace("</body>", "<script>AFTER</script></body>"), copy)
        self.assertEqual(self.PAGE.count("\n"), copy.count("\n"))

    def test_a_page_without_a_doctype_or_a_body_gets_a_doctype_and_the_scripts_at_its_ends(self):
        self.assertEqual('<!doctype html><meta charset="utf-8"><script>BEFORE</script><title>T</title>\n<main></main>\n<script>AFTER</script>',
                         cp.with_scripts("<title>T</title>\n<main></main>\n", "BEFORE", "AFTER"))

    def test_the_added_scripts_are_one_line_each(self):
        for script in (cp.collector("dark"), cp.measurer(), cp.one_line(cp.SHIFT)):
            self.assertNotIn("\n", script)
        self.assertIn('setAttribute("data-theme", "dark")', cp.collector("dark"))


class Names(unittest.TestCase):
    def test_the_slug_of_a_title(self):
        cases = [("How it broke", "how-it-broke"), ("Суть", "суть"), ("Step 2: the key's version", "step-2-the-key-s-version"),
                 ("", "part"), ("___", "part"), ("x" * 60, "x" * cp.SLUG_LENGTH)]
        self.assertEqual([expected for _, expected in cases], [cp.slug(title) for title, _ in cases])

    def test_a_text_is_cut_at_60_characters(self):
        self.assertEqual(["ж" * 60, "ж" * 59 + "…"], [cp.clip("ж" * 60), cp.clip("ж" * 61)])


if __name__ == "__main__":
    unittest.main()
