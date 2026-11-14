#!/usr/bin/env python3
"""Check a built page in a browser without a window: the errors of its scripts, the text that runs outside the frame
of its figure, and, with --shots, a picture of every part in the light and the dark theme.

    check_page.py PAGE.html [--shots DIR] [--chrome PATH] [--width 1180]

The browser is --chrome, else $CHROME, else the macOS application Google Chrome, else the first of
google-chrome, chromium and chromium-browser on PATH. A browser named by --chrome or $CHROME, as a
path or a name on PATH, is the one used, and when it is not an executable file the page is not
checked. Without a browser the script prints "check_page: no browser found: the page was not
checked" on stderr and exits 3.

PAGE.html is read as UTF-8 and never written. The script writes a copy of it into a temporary
directory with two scripts added on lines the page already has, so a line number in a script error
is the line of PAGE.html; a page without a doctype gets "<!doctype html>" in the copy, and every
copy declares UTF-8. The script added before the page's own sets the theme (data-theme on the root
element) and collects uncaught errors, unhandled promise rejections and console.error calls; the
script added after them measures the page after load and writes what it found into the document.
The browser runs once on that copy and dumps the document, from which the script reads:

  script: MESSAGE         an error, a rejection or a console.error call during load
  figure: RULE: TEXT      a text outside the frame of its figure, TEXT cut to 60 characters:
    outside the viewBox   an SVG text of an svg.fig whose box leaves the SVG's viewBox
    wider than its box    an SVG text whose anchor point lies inside a rect of the same g and
                          that is wider or taller than every such rect
    scrolls sideways      a .figscroll wider inside than outside at the checked width
    past the frame        an element of a figure, outside any .figscroll, whose right edge
                          passes the figure's
  probe: WHAT             the page did not finish loading within 120 seconds or left no
                          measurement, or the measurement failed

Every rule tolerates one pixel. An SVG text is measured lit, as it shows while its sentence is
spoken, which is never narrower than its resting form. The page is measured --width pixels wide.

--shots DIR, created when absent, receives two pictures of every part of the page's data, the
opening first: NN-SLUG-light.png and NN-SLUG-dark.png, NN the part's number in two digits, SLUG its
title in lower case with every run of characters other than letters and digits made one "-". For
each picture the browser runs once more, on a copy that sets the theme before the page's own script
runs, pins the page's sticky elements in their place and shifts the page up to the part's top, 16
pixels above its heading; the window is --width wide and as tall as the part, at most 4000 pixels.
A picture of the same name is replaced. A page without part data is one part, named by its title.
A part whose picture the browser did not write is the finding "shot: TITLE (THEME)".

Each run is BROWSER --headless=new --disable-gpu --hide-scrollbars --mute-audio --no-first-run
--no-default-browser-check --disable-extensions --disable-sync --disable-background-networking
--disable-component-update "--host-resolver-rules=MAP * ~NOTFOUND" --user-data-dir=TEMP/profile
--window-size=WIDTH,HEIGHT --virtual-time-budget=5000, then --dump-dom or --screenshot=FILE, then
the file address of the copy and no other address; the resolver rule leaves the browser no host
name to reach. The temporary directory, with the copies and the browser's profile, is removed on
exit. The script itself opens no network connection and uses the Python standard library alone.

Findings print on stdout, one per line, then one line with the numbers of parts, findings and
pictures. With the usage journal of feedback.py beside this script turned on, a run that exits 0, 1
or 3 adds one line of counts to that journal: the outcome (clean, findings, no_browser) and the
numbers of parts, findings and pictures.
Exit: 0 no finding; 1 a finding; 2 an unreadable page, an unusable option, or a --shots or temporary
directory that cannot be written; 3 no browser, or one that cannot be started, so the page was not
checked.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

WIDTH = 1180  # pixels: the default width of the window
PROBE_HEIGHT = 1000  # pixels: the window of the measuring run; the layout depends on the width alone
SHOT_HEIGHT_CAP = 4000  # pixels: the tallest picture of one part
TIMEOUT = 120  # seconds one browser run may take
VIRTUAL_TIME_BUDGET = 5000  # milliseconds of page time before the browser dumps the document or takes the picture
TEXT_CUT = 60  # characters of a figure's text a finding quotes
SLUG_LENGTH = 48  # characters of a part's title in the name of its picture
THEMES = ("light", "dark")
MAC_CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
CHROME_NAMES = ("google-chrome", "chromium", "chromium-browser")
FLAGS = ("--headless=new", "--disable-gpu", "--hide-scrollbars", "--mute-audio", "--no-first-run", "--no-default-browser-check",
         "--disable-extensions", "--disable-sync", "--disable-background-networking", "--disable-component-update",
         "--host-resolver-rules=MAP * ~NOTFOUND", f"--virtual-time-budget={VIRTUAL_TIME_BUDGET}")
NO_BROWSER = "check_page: no browser found: the page was not checked"
DOCTYPE = re.compile(r"\A\ufeff?\s*<!doctype\b[^>]*>", re.I)  # a byte order mark may precede it
BODY_END = re.compile(r"</body\s*>", re.I)
OUTPUT_ID = "check-page-out"  # the id of the element into which the measuring script writes what it found
OUTPUT = re.compile(f'<pre id="{OUTPUT_ID}">(.*?)</pre>', re.S)
SLUG_BREAK = re.compile(r"[\W_]+")

# The scripts added to the copy. Each is joined into one line, so they hold no "//" comment.
COLLECT = """
(function () {
  document.documentElement.setAttribute("data-theme", THEME);
  var errors = [];
  window.checkPageProbe = { errors: errors, stringify: JSON.stringify };
  window.addEventListener("error", function (e) {
    errors.push((e.message || String(e.error)) + (e.lineno ? " (line " + e.lineno + ")" : ""));
  });
  window.addEventListener("unhandledrejection", function (e) {
    var reason = e.reason;
    errors.push("unhandled rejection: " + (reason && reason.message ? reason.message : String(reason)));
  });
  var original = console.error;
  console.error = function () {
    errors.push("console.error: " + Array.prototype.map.call(arguments, String).join(" "));
    return original.apply(console, arguments);
  };
})();
"""
MEASURE = """
window.addEventListener("load", function () {
  var TOLERANCE = 1, HEADING_MARGIN = 16, SETTLE = 100;
  function all(root, selector) { return Array.prototype.slice.call(root.querySelectorAll(selector)); }
  function clean(text) { return (text || "").replace(/\\s+/g, " ").trim(); }
  function shown(box) { return box.width > 0 || box.height > 0; }
  function leaves(box, frame) {
    return box.left < frame.left - TOLERANCE || box.right > frame.right + TOLERANCE
      || box.top < frame.top - TOLERANCE || box.bottom > frame.bottom + TOLERANCE;
  }
  function caption(e) { var figure = e.closest("figure"), c = figure && figure.querySelector("figcaption"); return clean(c && c.textContent); }
  function viewBoxOf(svg) {
    var view = svg.viewBox && svg.viewBox.baseVal, matrix = svg.getScreenCTM();
    if (!view || !view.width || !view.height || !matrix) { return svg.getBoundingClientRect(); }
    var a = svg.createSVGPoint(), b = svg.createSVGPoint();
    a.x = view.x; a.y = view.y; b.x = view.x + view.width; b.y = view.y + view.height;
    a = a.matrixTransform(matrix); b = b.matrixTransform(matrix);
    return { left: Math.min(a.x, b.x), right: Math.max(a.x, b.x), top: Math.min(a.y, b.y), bottom: Math.max(a.y, b.y) };
  }
  function anchorOf(text) {
    var matrix = text.getScreenCTM(), xs = text.x.baseVal, ys = text.y.baseVal;
    if (!matrix || !text.ownerSVGElement) { return null; }
    var point = text.ownerSVGElement.createSVGPoint();
    point.x = xs.numberOfItems ? xs.getItem(0).value : 0;
    point.y = ys.numberOfItems ? ys.getItem(0).value : 0;
    return point.matrixTransform(matrix);
  }
  function holders(text) {
    var group = text.parentElement, point = anchorOf(text);
    if (!group || group.tagName.toLowerCase() !== "g" || !point) { return []; }
    return Array.prototype.filter.call(group.children, function (e) { return e.tagName.toLowerCase() === "rect"; })
      .map(function (rect) { return rect.getBoundingClientRect(); })
      .filter(function (b) { return shown(b) && point.x >= b.left && point.x <= b.right && point.y >= b.top && point.y <= b.bottom; });
  }
  function svgTexts(add) {
    all(document, "svg.fig [data-lit]").forEach(function (e) { e.classList.add("lit"); });
    all(document, "svg.fig").forEach(function (svg) {
      var frame = viewBoxOf(svg);
      all(svg, "text").forEach(function (text) {
        var box = text.getBoundingClientRect(), rects = holders(text);
        if (!shown(box)) { return; }
        if (leaves(box, frame)) { add("outside the viewBox", clean(text.textContent)); }
        var fits = rects.some(function (r) { return box.width <= r.width + TOLERANCE && box.height <= r.height + TOLERANCE; });
        if (rects.length && !fits) { add("wider than its box", clean(text.textContent)); }
      });
    });
  }
  function frames(add) {
    all(document, ".figscroll").forEach(function (s) {
      if (s.scrollWidth > s.clientWidth + TOLERANCE) { add("scrolls sideways", caption(s) || clean(s.textContent)); }
    });
    all(document, "figure").forEach(function (figure) {
      var edge = figure.getBoundingClientRect().right, past = [];
      all(figure, "*").forEach(function (e) {
        if (e.closest(".figscroll") || past.some(function (p) { return p.contains(e); })) { return; }
        var box = e.getBoundingClientRect();
        if (shown(box) && box.right > edge + TOLERANCE) { past.push(e); add("past the frame", clean(e.textContent) || caption(e)); }
      });
    });
  }
  function figureFindings() {
    var found = [];
    function add(rule, text) { found.push({ rule: rule, text: text }); }
    svgTexts(add);
    frames(add);
    return found;
  }
  function partBounds() {
    var height = document.documentElement.scrollHeight, data = document.getElementById("page-data"), parts = null;
    try { parts = JSON.parse(data.textContent).parts; } catch (e) { parts = null; }
    if (!Array.isArray(parts) || !parts.length) { return [{ title: document.title || "page", top: 0, bottom: height }]; }
    var tops = parts.map(function (part, i) {
      if (!i) { return 0; }
      var heading = document.querySelector('#article [data-lit~="' + part.paragraph + '.1"]');
      return heading ? Math.max(0, Math.round(heading.getBoundingClientRect().top + window.scrollY - HEADING_MARGIN)) : null;
    });
    return parts.map(function (part, i) {
      var later = tops.slice(i + 1).filter(function (t) { return t !== null && tops[i] !== null && t > tops[i]; });
      return { title: String(part.title || ""), top: tops[i], bottom: later.length ? later[0] : height };
    });
  }
  setTimeout(function () {
    var probe = window.checkPageProbe || { errors: [], stringify: JSON.stringify };
    var out = { errors: probe.errors, figures: [], parts: [] };
    try {
      out.figures = figureFindings();
      out.parts = partBounds();
    } catch (e) { out.measureError = String(e && e.message || e); }
    var pre = document.createElement("pre");
    pre.id = OUTPUT_ID;
    pre.textContent = probe.stringify(out);
    document.body.appendChild(pre);
  }, SETTLE);
});
"""
SHIFT = """
(function () {
  Array.prototype.forEach.call(document.querySelectorAll("body *"), function (e) {
    if (getComputedStyle(e).position !== "sticky") { return; }
    e.style.setProperty("position", "relative", "important");
    e.style.setProperty("inset", "auto", "important");
  });
  document.body.style.setProperty("transform", "translateY(" + (-TOP) + "px)", "important");
})();
"""


class InputError(Exception):
    """The page, an option or a directory the run needs cannot be used; the message names it."""


class BrowserError(Exception):
    """The browser found cannot be started; the message names it."""


@dataclass(frozen=True)
class Part:
    title: str
    top: int | None  # pixels from the top of the page; None when its heading is not on the page
    bottom: int


@dataclass(frozen=True)
class Probe:
    """What the measuring run wrote into the document."""
    errors: list[str]
    figures: list[tuple[str, str]]  # (rule, text)
    parts: list[Part]
    measure_error: str | None


@dataclass(frozen=True)
class Run:
    """One check: the browser, the temporary directory of the copies and the browser's profile, the page's text and the
    window's width in pixels."""
    browser: str
    work: Path
    page: str
    width: int


@dataclass(frozen=True)
class Outcome:
    findings: list[str]
    parts: int
    pictures: int


# The browser


def find_browser(named: str | None, environ: Mapping[str, str], mac_app: Path = MAC_CHROME) -> str | None:
    """The browser to run: `named`, else $CHROME, as a path or a name on PATH; else the macOS application, else the first
    of CHROME_NAMES on PATH. None when a named browser is not executable or none is found."""
    search = environ.get("PATH", os.defpath)
    chosen = named or environ.get("CHROME")
    if chosen:
        return shutil.which(chosen, path=search)
    if mac_app.is_file() and os.access(mac_app, os.X_OK):
        return str(mac_app)
    for name in CHROME_NAMES:
        found = shutil.which(name, path=search)
        if found:
            return found
    return None


def run_browser(run: Run, copy: Path, height: int, action: str) -> str | None:
    """The browser's standard output from one run on `copy` in a window `height` pixels tall; None when the run did not
    end within TIMEOUT seconds."""
    command = [run.browser, *FLAGS, f"--user-data-dir={run.work / 'profile'}", f"--window-size={run.width},{height}", action, copy.as_uri()]
    try:
        done = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=TIMEOUT, check=False)
    except subprocess.TimeoutExpired:
        return None
    except OSError as e:
        raise BrowserError(f"cannot run the browser {run.browser}: {e}") from e
    return done.stdout


# The copy


def one_line(script: str) -> str:
    return " ".join(line.strip() for line in script.splitlines() if line.strip())


def collector(theme: str) -> str:
    return one_line(COLLECT.replace("THEME", json.dumps(theme)))


def measurer() -> str:
    return one_line(MEASURE.replace("OUTPUT_ID", json.dumps(OUTPUT_ID)))


def with_scripts(page: str, before: str, after: str) -> str:
    """The page with the script `before` ahead of all its own and `after` behind them, on lines the page already has, so
    every line of the page keeps its number; a page without a doctype gets one, and the copy declares UTF-8."""
    doctype = DOCTYPE.match(page)
    start = doctype.end() if doctype else 0
    head = (page[:start] if doctype else "<!doctype html>") + f'<meta charset="utf-8"><script>{before}</script>'
    rest = page[start:]
    ends = list(BODY_END.finditer(rest))
    cut = ends[-1].start() if ends else len(rest)
    return head + rest[:cut] + f"<script>{after}</script>" + rest[cut:]


def write_copy(path: Path, text: str) -> Path:
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as e:
        raise InputError(f"cannot write the copy of the page {path}: {e}") from e
    return path


# The measurement


def is_text_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def read_parts(entries: object) -> list[Part] | None:
    """The parts the probe wrote; None when they are not a list of {"title", "top", "bottom"}."""
    if not isinstance(entries, list):
        return None
    parts = []
    for entry in entries:
        top, bottom = (entry.get("top"), entry.get("bottom")) if isinstance(entry, dict) else (None, None)
        if not (isinstance(entry, dict) and isinstance(entry.get("title"), str) and isinstance(bottom, (int, float))
                and (top is None or isinstance(top, (int, float)))):
            return None
        parts.append(Part(entry["title"], None if top is None else int(top), int(bottom)))
    return parts


def read_probe(dumped: str) -> Probe | None:
    """What the measuring script wrote into the dumped document; None when it wrote nothing of that form."""
    found = OUTPUT.search(dumped)
    if not found:
        return None
    try:
        data = json.loads(html.unescape(found.group(1)))
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    figures, parts, measure_error = data.get("figures"), read_parts(data.get("parts")), data.get("measureError")
    usable_figures = isinstance(figures, list) and all(isinstance(f, dict) and is_text_list([f.get("rule"), f.get("text")]) for f in figures)
    if not (is_text_list(data.get("errors")) and usable_figures and parts is not None and (measure_error is None or isinstance(measure_error, str))):
        return None
    return Probe(data["errors"], [(f["rule"], f["text"]) for f in figures], parts, measure_error)


def probe(run: Run) -> Probe | None:
    """The page measured after load in the light theme; None when the browser left no measurement."""
    copy = write_copy(run.work / "probe.html", with_scripts(run.page, collector("light"), measurer()))
    dumped = run_browser(run, copy, PROBE_HEIGHT, "--dump-dom")
    return None if dumped is None else read_probe(dumped)


def clip(text: str) -> str:
    return text if len(text) <= TEXT_CUT else text[:TEXT_CUT - 1] + "…"


def probe_findings(result: Probe) -> list[str]:
    findings = [f"script: {' '.join(message.split())}" for message in result.errors]
    findings += [f"figure: {rule}: {clip(text)}" for rule, text in result.figures]
    if result.measure_error is not None:
        findings.append(f"probe: the page could not be measured: {' '.join(result.measure_error.split())}")
    return findings


# The pictures


def slug(title: str) -> str:
    return SLUG_BREAK.sub("-", title.lower()).strip("-")[:SLUG_LENGTH].rstrip("-") or "part"


def shoot(run: Run, top: int, height: int, theme: str, target: Path) -> bool:
    """Whether the browser wrote the picture `target`, `height` pixels tall, of the page shifted up by `top` pixels."""
    copy = write_copy(run.work / "shot.html", with_scripts(run.page, collector(theme), one_line(SHIFT.replace("TOP", str(top)))))
    try:
        target.unlink(missing_ok=True)
    except OSError as e:
        raise InputError(f"cannot replace the picture {target}: {e}") from e
    run_browser(run, copy, height, f"--screenshot={target}")
    return target.is_file() and target.stat().st_size > 0


def take_shots(run: Run, parts: list[Part], directory: Path) -> tuple[int, list[str]]:
    """The number of pictures written into `directory`, two per part, and a finding for each picture not written."""
    written, findings = 0, []
    for number, part in enumerate(parts, 1):
        height = max(1, min(part.bottom - (part.top or 0), SHOT_HEIGHT_CAP))
        for theme in THEMES:
            target = directory / f"{number:02d}-{slug(part.title)}-{theme}.png"
            if part.top is not None and shoot(run, part.top, height, theme, target):
                written += 1
            else:
                findings.append(f"shot: {part.title} ({theme})")
    return written, findings


def shots_dir(path: Path) -> Path:
    """The --shots directory as an absolute path, created when absent; InputError when a file cannot be written into it."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=path):
            pass
    except OSError as e:
        raise InputError(f"cannot write pictures into {path}: {e}") from e
    return path.resolve()


# The run


def check(run: Run, shots: Path | None) -> Outcome:
    """The findings on the page, its number of parts and the number of pictures written into `shots`."""
    result = probe(run)
    if result is None:
        return Outcome(["probe: the page did not finish loading"], 0, 0)
    findings = probe_findings(result)
    pictures = 0
    if shots is not None:
        pictures, missing = take_shots(run, result.parts, shots)
        findings += missing
    return Outcome(list(dict.fromkeys(findings)), len(result.parts), pictures)


def read_page(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise InputError(f"cannot read the page {path}: {e}") from e


def positive_width(value: str) -> int:
    width = int(value)
    if width < 1:
        raise argparse.ArgumentTypeError(f"{value} is not a width in pixels")
    return width


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("page", type=Path, help="the built page; it is read and never written")
    parser.add_argument("--shots", type=Path, help="directory for a picture of every part in the light and the dark theme")
    parser.add_argument("--chrome", help="the browser; else $CHROME, the macOS application, or google-chrome, chromium, chromium-browser on PATH")
    parser.add_argument("--width", type=positive_width, default=WIDTH, help=f"the window's width in pixels (default {WIDTH})")
    return parser.parse_args(argv)


def checked(browser: str, page: str, args: argparse.Namespace) -> Outcome:
    """The outcome of the check in a temporary directory that is removed afterwards; InputError when a directory the
    run writes cannot be used."""
    shots = shots_dir(args.shots) if args.shots is not None else None
    try:
        work = tempfile.TemporaryDirectory(prefix="check_page-", ignore_cleanup_errors=True)
    except OSError as e:
        raise InputError(f"cannot make a temporary directory: {e}") from e
    with work as folder:
        return check(Run(browser, Path(folder), page, args.width), shots)


def main(argv: list[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    args = parse_args(argv)
    try:
        page = read_page(args.page)
    except InputError as e:
        print(f"check_page: {e}", file=sys.stderr)
        return 2
    browser = find_browser(args.chrome, os.environ if environ is None else environ)
    if browser is None:
        print(NO_BROWSER, file=sys.stderr)
        journal("page_check", outcome="no_browser")
        return 3
    try:
        outcome = checked(browser, page, args)
    except InputError as e:
        print(f"check_page: {e}", file=sys.stderr)
        return 2
    except BrowserError as e:
        print(f"check_page: {e}: the page was not checked", file=sys.stderr)
        journal("page_check", outcome="no_browser")
        return 3
    for finding in outcome.findings:
        print(f"check_page: {finding}")
    where = f" in {args.shots}" if args.shots is not None else ""
    print(f"{args.page}: {outcome.parts} part(s), {len(outcome.findings)} finding(s), {outcome.pictures} picture(s){where}")
    journal("page_check", outcome="findings" if outcome.findings else "clean", parts=outcome.parts, findings=len(outcome.findings),
            shots=outcome.pictures)
    return 1 if outcome.findings else 0


def journal(event: str, **fields: object) -> None:
    """Add one line of counts to the usage journal of feedback.py beside this script, when the user turned it on."""
    try:
        here = str(Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        import feedback

        feedback.record(event, **fields)
    except Exception:  # noqa: BLE001 - an isolation point: a missing or broken feedback.py changes nothing in this run
        pass


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
