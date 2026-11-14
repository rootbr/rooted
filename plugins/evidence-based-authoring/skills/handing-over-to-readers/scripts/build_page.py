#!/usr/bin/env python3
"""Build a report's page with voice from the page template, an article body and the voice's cues.

    build_page.py --body BODY.html --cues CUES.json --report REPORT.md --out PAGE.html
                  [--root DIR] [--voice URL] [--title TITLE] [--id ID] [--strings FILE]
                  [--template FILE] [--standalone]

BODY.html is the article: HTML without scripts. Its contract:
  data-say="P.S P.S ..."  on an empty element; the builder fills it with one
      <span class="s" data-lit="P.S">sentence</span> per id, the text taken from CUES.json.
  data-lit="P.S ..."  on any element; the page lights it while one of those sentences is spoken.
  <section class="decision" data-decision="KEY" data-title="TITLE">  holds two or more
      <div class="option" data-option="NAME">, at most one of them with data-mine="1" (the
      author's choice). The page adds the pick controls, the words fields and the copy bar.
  Figures: inline SVG of class "fig" or HTML inside <figure>, in the template's classes.

CUES.json is the list voice_cues.py writes: [{"paragraph", "sentence", "text", "start", "end"}].

The builder refuses a body, one line per violation on stderr, when it names a sentence the cues
do not have, leaves a spoken sentence on no element, puts content into a data-say element,
writes a sentence twice, has a decision with fewer than two options, more than one data-mine="1",
no data-decision or data-title, or a data-decision used twice, or carries a <script> element or
an on... handler attribute.

The player's parts: part N starts at cue N.1, titled by the h2 whose data-lit holds N.1, else
"opening" for part 1 and "part N" for the others (both from the strings).

"Where to look" comes from REPORT.md: the list under the heading that check_report.py's
LOOK_HEADING matches, with the headings of its lexicon file
$XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json added when that file exists; a report
without that heading is unreadable input. The list is appended after the body under that
heading's text. An item whose first
`path:line` or `path:line-end` code span names a file and lines under --root shows the lines
from three above to three below, the anchored ones marked; any other item shows its text. Without
--root no anchor resolves.

Strings: every word the page shows comes from one dictionary with English defaults (STRINGS).
--strings FILE overrides keys; without it, $XDG_CONFIG_HOME/handing-over-to-readers/page-strings.json
is read when it exists ($HOME/.config when the variable is unset or empty).

The template's <!--TITLE--> takes the title (--title, else the body's first h1, else the id),
<!--BODY--> the expanded body and the "Where to look" section, and /*DATA*/ one JSON object:
{"cues", "parts", "strings", "voice", "id"}, every "<" in it written as \\u003c. The output starts
with <title> and carries no html, head or body tag; --standalone wraps it in a complete document.

Reads the files named on the command line, the two configuration files named above when they
exist, and the anchored files under --root; writes PAGE.html.
Exit: 0 written; 1 the body breaks its contract; 2 unreadable input, template or strings.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Mapping

STRINGS = {
    "now": "now:",
    "notPlaying": "not playing",
    "jump": "Go to the spoken place",
    "opening": "Opening",
    "part": "Part",
    "noAudio": "This page has no audio: read it as a document.",
    "choose": "Choose",
    "chosen": "Chosen",
    "words": "Your words on this decision, typed or dictated",
    "partWords": "Your words on this part, typed or dictated",
    "takeMine": "Take all recommendations",
    "copy": "Copy the answer",
    "pick": "Pick an option or add your words.",
    "write": "Add your words to any part.",
    "picked": "Noted. Add your words or copy the answer.",
    "copied": "Copied: paste it into the chat.",
    "copyFailed": "The page could not copy: the answer is shown below, copy it yourself.",
    "saved": "The answer is saved on the page.",
}
STRINGS_FILE = Path("handing-over-to-readers") / "page-strings.json"
LEXICON_FILE = Path("handing-over-to-readers") / "lexicon.json"
TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "page-template.html"
MARKERS = ("<!--TITLE-->", "<!--BODY-->", "/*DATA*/")
CUE_ID = re.compile(r"^\d+\.\d+$")
PAGE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VOID_TAGS = frozenset("area base br col embed hr img input link meta source track wbr".split())
FENCE = re.compile(r"^\s*(?:```|~~~)")
HEADING = re.compile(r"^\s*#{1,6}\s")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
CODE_SPAN = re.compile(r"`([^`]+)`")
ANCHOR = re.compile(r"^(?P<path>[^\s`:*?\"<>|]+?):(?P<line>\d+)(?:-(?P<end>\d+))?$")
CONTEXT_LINES = 3


class InputError(Exception):
    """An input the build cannot use: exit 2."""


@dataclass
class Say:
    """A data-say element: its ids, where its start tag ends and its end tag begins."""
    tag: str
    ids: list[str]
    line: int
    open_end: int
    close_start: int | None = None
    has_content: bool = False


@dataclass
class Decision:
    key: str | None
    title: str | None
    line: int
    depth: int
    options: int = 0
    mine: int = 0


@dataclass
class Heading:
    tag: str
    ids: list[str]
    depth: int
    text: list[str] = field(default_factory=list)


class BodyScan(HTMLParser):
    """Reads a body once and records its data-say elements, its data-lit ids, its decisions, the
    text of its headings, and the script elements and handler attributes it must not carry."""

    def __init__(self, body: str):
        super().__init__(convert_charrefs=True)
        self._line_starts = [0] + [match.end() for match in re.finditer("\n", body)]
        self._stack: list[str] = []
        self._pending: Say | None = None
        self._decisions: list[Decision] = []
        self._headings: list[Heading] = []
        self.says: list[Say] = []
        self.lits: list[tuple[list[str], int]] = []
        self.decisions: list[Decision] = []
        self.h2: list[tuple[list[str], str]] = []
        self.h1: str | None = None
        self.violations: list[tuple[int, str]] = []
        self.feed(body)
        self.close()
        if self._pending is not None:
            self._unclosed(self._pending, "the end of the body")
        while self._stack:
            self._pop()

    def _offset(self) -> int:
        line, column = self.getpos()
        return self._line_starts[line - 1] + column

    def _unclosed(self, say: Say, where: str) -> None:
        self.violations.append((say.line, f"<{say.tag} data-say> is not closed before {where}: write <{say.tag} data-say=\"…\"></{say.tag}>"))
        self._pending = None

    def _content_in_pending(self) -> None:
        if self._pending is not None:
            self._pending.has_content = True
            self.violations.append((self._pending.line, f"<{self._pending.tag} data-say> holds content: leave it empty, the builder fills it from the cues"))
            self._pending = None

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], closes_itself: bool) -> None:
        self._content_in_pending()
        line = self.getpos()[0]
        values = dict(attrs)
        if tag == "script":
            self.violations.append((line, "a <script> element: the body carries no script, the page's script is the template's"))
        for name, _ in attrs:
            if name.startswith("on"):
                self.violations.append((line, f"a handler attribute {name}=: the body carries no script"))
        if values.get("data-lit") is not None:
            self.lits.append((values["data-lit"].split(), line))
        if values.get("data-say") is not None:
            say = Say(tag, values["data-say"].split(), line, self._offset() + len(self.get_starttag_text() or ""))
            self.says.append(say)
            if closes_itself or tag in VOID_TAGS:
                self._unclosed(say, "its own start tag ends")
            else:
                self._pending = say
        if "data-option" in values and self._decisions:
            self._decisions[-1].options += 1
            self._decisions[-1].mine += values.get("data-mine") == "1"
        if closes_itself or tag in VOID_TAGS:
            return
        self._stack.append(tag)
        if tag == "section" and "decision" in (values.get("class") or "").split():
            self._decisions.append(Decision(values.get("data-decision"), values.get("data-title"), line, len(self._stack)))
        if tag in ("h1", "h2"):
            self._headings.append(Heading(tag, (values.get("data-lit") or "").split(), len(self._stack)))

    def _pop(self) -> None:
        depth = len(self._stack)
        self._stack.pop()
        if self._decisions and self._decisions[-1].depth == depth:
            self.decisions.append(self._decisions.pop())
        if self._headings and self._headings[-1].depth == depth:
            heading = self._headings.pop()
            text = " ".join("".join(heading.text).split())
            if heading.tag == "h2":
                self.h2.append((heading.ids, text))
            elif self.h1 is None:
                self.h1 = text

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, closes_itself=False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, closes_itself=True)

    def handle_endtag(self, tag):
        if self._pending is not None:
            if tag == self._pending.tag:
                self._pending.close_start = self._offset()
                self._pending = None
            else:
                self._unclosed(self._pending, f"</{tag}>")
        if tag in self._stack:
            while self._stack and self._stack[-1] != tag:
                self._pop()
            self._pop()

    def handle_data(self, data):
        if data.strip():
            self._content_in_pending()
        for heading in self._headings:
            heading.text.append(data)


def read_cues(path: Path) -> list[dict]:
    """The cues as a list of {"paragraph", "sentence", "text", "start", "end"}, each id once."""
    try:
        cues = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise InputError(f"cannot read the cues {path}: {e}") from e
    if not isinstance(cues, list) or not cues:
        raise InputError(f"the cues {path} are not a non-empty JSON list")
    seen = set()
    for index, item in enumerate(cues, 1):
        well_formed = (isinstance(item, dict)
                       and all(isinstance(item.get(key), int) and item[key] >= 1 for key in ("paragraph", "sentence"))
                       and isinstance(item.get("text"), str)
                       and all(isinstance(item.get(key), (int, float)) for key in ("start", "end")))
        if not well_formed:
            raise InputError(f"the cues {path}: entry {index} lacks an integer paragraph and sentence, a text, a start and an end")
        cue_id = f"{item['paragraph']}.{item['sentence']}"
        if cue_id in seen:
            raise InputError(f"the cues {path}: sentence {cue_id} appears twice")
        seen.add(cue_id)
    return [{key: item[key] for key in ("paragraph", "sentence", "text", "start", "end")} for item in cues]


def cue_id(cue: dict) -> str:
    return f"{cue['paragraph']}.{cue['sentence']}"


def validate(scan: BodyScan, cues: list[dict]) -> list[tuple[int, str]]:
    """Every violation of the body contract as (body line, message); line 0 for one not tied to a line."""
    said = {cue_id(cue): cue for cue in cues}
    found = list(scan.violations)
    written: dict[str, int] = {}
    for say in scan.says:
        for name in say.ids:
            if name in written:
                found.append((say.line, f"sentence {name} is written twice (first on line {written[name]}): a sentence has one place on the page"))
            written.setdefault(name, say.line)
    named = [(say.ids, say.line, "data-say") for say in scan.says]
    named += [(ids, line, "data-lit") for ids, line in scan.lits]
    placed = set()
    for ids, line, attribute in named:
        for name in ids:
            placed.add(name)
            if name not in said:
                found.append((line, f"{attribute} names {name}, which the cues do not have"))
    for name, cue in said.items():
        if name not in placed:
            found.append((0, f"spoken sentence {name} lands on no element: {cue['text'][:60]!r}"))
    keys: dict[str, int] = {}
    for decision in scan.decisions:
        label = f"decision {decision.key!r}" if decision.key else "a decision"
        if not decision.key or not decision.title:
            found.append((decision.line, f"{label} lacks data-decision or data-title"))
        elif decision.key in keys:
            found.append((decision.line, f"decision key {decision.key!r} is used twice (first on line {keys[decision.key]})"))
        keys.setdefault(decision.key or "", decision.line)
        if decision.options < 2:
            found.append((decision.line, f"{label} has {decision.options} option(s): a decision offers two or more data-option blocks"))
        if decision.mine > 1:
            found.append((decision.line, f"{label} marks {decision.mine} options data-mine=\"1\": the author's choice is one option"))
    return sorted(found)


def expand(body: str, scan: BodyScan, cues: list[dict]) -> str:
    """The body with every data-say element filled with its sentences."""
    text = {cue_id(cue): cue["text"] for cue in cues}
    pieces, done = [], 0
    for say in sorted(scan.says, key=lambda item: item.open_end):
        spans = " ".join(f'<span class="s" data-lit="{name}">{html.escape(text[name], quote=False)}</span>' for name in say.ids)
        pieces += [body[done:say.open_end], spans]
        done = say.close_start
    pieces.append(body[done:])
    return "".join(pieces)


def derive_parts(cues: list[dict], scan: BodyScan, strings: Mapping[str, str]) -> list[dict]:
    """One part per paragraph, starting at its first sentence and titled by the h2 that lights it."""
    titles: dict[str, str] = {}
    for ids, text in scan.h2:
        for name in ids:
            titles.setdefault(name, text)
    first: dict[int, dict] = {}
    for cue in cues:
        first.setdefault(cue["paragraph"], cue)
    parts = []
    for number, cue in sorted(first.items()):
        start = f"{number}.1"
        fallback = strings["opening"] if number == 1 else f"{strings['part']} {number}"
        parts.append({"paragraph": number, "cue": cue_id(cue), "start": cue["start"], "title": titles.get(start) or fallback})
    return parts


def load_look_heading(config: Path):
    """LOOK_HEADING of check_report.py beside this script, loaded by its path, with the headings of
    the lexicon file in `config` added when that file exists, as check_report.py itself adds them."""
    path = Path(__file__).resolve().with_name("check_report.py")
    lexicon = config / LEXICON_FILE
    try:
        spec = importlib.util.spec_from_file_location("handover_check_report", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module  # its dataclasses resolve their own module by name
        spec.loader.exec_module(module)
        if lexicon.is_file() and hasattr(module, "apply_lexicon"):
            module.apply_lexicon(str(lexicon))
        return module.LOOK_HEADING
    except Exception as e:  # an isolation point: any failure of the neighbour script or its lexicon is one input error here
        raise InputError(f"cannot take LOOK_HEADING from {path} (lexicon {lexicon}): {e}") from e


def look_items(report: str, look_heading) -> tuple[str, list[str]]:
    """The heading text of "Where to look" and the text of each item of the list under it."""
    lines = report.splitlines()
    fenced, start = False, None
    for index, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
        elif not fenced and look_heading.match(line):
            start = index
            break
    if start is None:
        raise InputError("the report has no \"Where to look\" heading")
    heading = lines[start].strip().lstrip("#").strip().strip("*").rstrip(":").strip("*").strip()
    items: list[str] = []
    for line in lines[start + 1:]:
        if HEADING.match(line):
            break
        if LIST_ITEM.match(line):
            items.append(LIST_ITEM.sub("", line, count=1).strip())
        elif items and line.strip() and line[:1].isspace():
            items[-1] += " " + line.strip()
    return heading, items


def inline_html(text: str) -> str:
    """Markdown text with its code spans as <code>, everything else escaped."""
    parts = CODE_SPAN.split(text)
    return "".join(f"<code>{html.escape(part)}</code>" if index % 2 else html.escape(part) for index, part in enumerate(parts))


def anchored_lines(item: str, root: Path | None) -> list[tuple[int, str, bool]] | None:
    """(number, text, anchored) for the lines around the item's first resolving anchor, or None."""
    if root is None:
        return None
    for span in CODE_SPAN.findall(item):
        match = ANCHOR.match(span.strip())
        if not match:
            continue
        target = (root / match["path"]).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            return None
        try:
            lines = target.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return None
        first, last = int(match["line"]), int(match["end"] or match["line"])
        if not 1 <= first <= last <= len(lines):
            return None
        low, high = max(1, first - CONTEXT_LINES), min(len(lines), last + CONTEXT_LINES)
        return [(number, lines[number - 1], first <= number <= last) for number in range(low, high + 1)]
    return None


def look_section(heading: str, items: list[str], root: Path | None) -> str:
    entries = []
    for item in items:
        found = anchored_lines(item, root)
        if found is None:
            entries.append(f'  <li class="look-item">{inline_html(item)}</li>')
            continue
        width = len(str(found[-1][0]))
        rows = []
        for number, text, anchored in found:
            row = f'<span class="ln">{number:>{width}}</span>  {html.escape(text)}'
            rows.append(f'<span class="hit">{row}</span>' if anchored else row)
        entries.append(f'  <li class="look-item"><details><summary>{inline_html(item)}</summary>'
                       f'<pre class="src">{chr(10).join(rows)}</pre></details></li>')
    return (f'<section class="look" aria-labelledby="look-heading">\n<h2 id="look-heading">{html.escape(heading)}</h2>\n'
            f'<ul class="look-list">\n' + "\n".join(entries) + "\n</ul>\n</section>")


def config_dir(environ: Mapping[str, str]) -> Path:
    """$XDG_CONFIG_HOME, or $HOME/.config when the variable is unset or empty."""
    return Path(environ.get("XDG_CONFIG_HOME") or Path(environ.get("HOME") or Path.home()) / ".config")


def load_strings(path: Path | None, config: Path) -> dict[str, str]:
    """STRINGS overridden by the given file, or by the configuration file in `config` when it exists."""
    if path is None:
        path = config / STRINGS_FILE
        if not path.is_file():
            return dict(STRINGS)
    try:
        overrides = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise InputError(f"cannot read the strings {path}: {e}") from e
    if not isinstance(overrides, dict):
        raise InputError(f"the strings {path} are not a JSON object")
    unknown = sorted(set(overrides) - set(STRINGS))
    if unknown:
        raise InputError(f"the strings {path} hold unknown key(s) {', '.join(unknown)}; known: {', '.join(STRINGS)}")
    not_text = sorted(key for key, value in overrides.items() if not isinstance(value, str))
    if not_text:
        raise InputError(f"the strings {path}: the value of {', '.join(not_text)} is not a string")
    return {**STRINGS, **overrides}


def data_json(data: dict) -> str:
    """The data block's JSON; "<" is escaped so no text in it can close the script element."""
    return json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")


def fill(template: str, title: str, body: str, data: dict) -> str:
    values = {"<!--TITLE-->": html.escape(title), "<!--BODY-->": body, "/*DATA*/": data_json(data)}
    return re.sub("|".join(re.escape(marker) for marker in MARKERS), lambda match: values[match.group()], template)


def standalone(page: str) -> str:
    """The page as a complete document: what precedes the first </style> goes into head."""
    head, mark, rest = page.partition("</style>")
    if not mark:
        head, rest = "", page
    return ('<!doctype html>\n<html>\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"{head}{mark}\n</head>\n<body>\n{rest.strip()}\n</body>\n</html>\n")


def read_text(path: Path, what: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise InputError(f"cannot read the {what} {path}: {e}") from e


def main(argv: list[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--body", type=Path, required=True)
    parser.add_argument("--cues", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--root", type=Path, help="directory the report's path:line anchors resolve under")
    parser.add_argument("--voice", default="", help="address of the audio; empty: the page has no player")
    parser.add_argument("--title")
    parser.add_argument("--id", default="report", help="name under which the page keeps the reader's answer")
    parser.add_argument("--strings", type=Path)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--standalone", action="store_true", help="write a complete HTML document")
    args = parser.parse_args(argv)
    try:
        if not PAGE_ID.match(args.id):
            raise InputError(f"--id {args.id!r}: use letters, digits, '.', '_' and '-'")
        if args.root is not None and not args.root.is_dir():
            raise InputError(f"--root {args.root} is not a directory")
        config = config_dir(os.environ if environ is None else environ)
        strings = load_strings(args.strings, config)
        cues = read_cues(args.cues)
        body = read_text(args.body, "body")
        template = read_text(args.template, "template")
        for marker in MARKERS:
            if template.count(marker) != 1:
                raise InputError(f"the template {args.template} holds {marker} {template.count(marker)} times, not once")
        heading, items = look_items(read_text(args.report, "report"), load_look_heading(config))
    except InputError as e:
        print(f"build_page: {e}", file=sys.stderr)
        return 2
    scan = BodyScan(body)
    violations = validate(scan, cues)
    if violations:
        for line, message in violations:
            print(f"{args.body}:{line}: {message}" if line else f"{args.body}: {message}", file=sys.stderr)
        return 1
    article = expand(body, scan, cues).rstrip() + "\n" + look_section(heading, items, args.root)
    data = {"cues": cues, "parts": derive_parts(cues, scan, strings), "strings": strings, "voice": args.voice, "id": args.id}
    page = fill(template, args.title or scan.h1 or args.id, article, data)
    try:
        args.out.write_text(standalone(page) if args.standalone else page, encoding="utf-8")
    except OSError as e:
        print(f"build_page: cannot write {args.out}: {e}", file=sys.stderr)
        return 2
    print(f"{len(cues)} sentences, {len(data['parts'])} parts, {len(scan.decisions)} decision(s), {len(items)} look item(s) -> {args.out}")
    return 0


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
