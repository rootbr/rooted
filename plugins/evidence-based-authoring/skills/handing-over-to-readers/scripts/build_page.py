#!/usr/bin/env python3
"""Build a report's page with voice from an article body: the story the voice reads, the page, and the page's text.

    build_page.py --body BODY.html [--out PAGE.html] [--story-out STORY.txt] [--text-out TEXT.md]
                  [--cues CUES.json] [--voice URL] [--report REPORT.md | --look LOOK.json] [--root DIR]
                  [--terms TERMS.json] [--refs REFS.json] [--editor-url URL]
                  [--title TITLE] [--id ID] [--strings FILE] [--template FILE] [--standalone]
                  [--explanation]

At least one of --out, --story-out and --text-out is given.

BODY.html is the article: HTML without scripts, and the one place each spoken sentence is written.
Its contract:
  data-say  (no value) on an element whose content is text alone: its sentences are shown there
      and spoken; the page wraps each in <span class="s" data-lit="P.S">.
  data-part="PHRASE"  on an h2: a part starts here; the voice says PHRASE first, and the heading
      is lit meanwhile. What precedes the first such h2 is the opening, part 1; an opening without
      a spoken sentence is no part, and the first data-part heading is then part 1.
  data-voice="SENTENCES"  on any other element: spoken at this place and shown by the element
      itself (an option block, a group of a figure), which is lit meanwhile.
  [@name]  before a sentence, in the text of a data-say element or in a data-part or data-voice
      value, names that sentence; the mark is neither shown nor spoken. A name is a letter, then
      letters, digits, "_" or "-".
  data-lit="@name ..."  on any element: the page lights it while one of the named sentences is
      spoken.
  data-nav="NAME"  on a figure or any other element: the short name under which the map of an
      explanation's page lists it.
  data-ref="KEY"  on any element outside a data-say element: names the entry KEY of the file of
      references; the page shows what the entry names in place (see --refs).
  <section class="decision" data-decision="KEY" data-title="TITLE">  holds two or more
      <div class="option" data-option="NAME">, at most one of them with data-mine="1" (the
      author's choice). The page adds the pick controls, the words fields and the copy bar.
  Figures: inline SVG of class "fig" or HTML inside <figure>, in the template's classes.
  The figures of an explanation: <figure class="pseudo"> holds the rule of the mechanism as
      pseudocode in a <pre>, one line a step; a line may be a <span data-lit="@name">, may hold
      a link to the part that unfolds it, and may end in an element of class "by" that names the
      method carrying the line out. <figure class="questions"> holds the table of the readers'
      questions, <figure class="quiz"> a question with its hidden answer, <figure class="factor">
      a table that runs one factor without it and with it, its cells class="good" or class="bad".
      A class attribute may list several classes. A figure of class terms, the table of terms,
      is an ordinary figure: it makes no body an explanation and may stand anywhere.
  Blocks: <div class="gist"> holds the gist of a part, the few sentences to keep, as paragraphs
      or a list, set apart by a rule at its side; <div class="steps"> holds <div class="step">
      blocks that stand side by side and stack in a narrow window.
  An internal link href="#ID" names an id of the body, or look-heading on a page with a
      "Where to look" section.

The voice speaks the text of data-say, data-part and data-voice in document order. Part P counts
from 1, sentence S from 1 within its part. A sentence ends where voice_cues.py ends one: the
builder takes its sentence_spans and paragraphs from beside this script. The text of each holder
ends a sentence, so no sentence runs from one holder into the next.

A body is an explanation when --explanation is given or when it holds a figure whose classes
include pseudo, questions or quiz; any other body is built as a report's. The first part of an
explanation runs from its first data-part heading to the next one or to the end of the body, and
gives the mechanism whole.

The builder refuses a body, one line per violation on stderr as BODY:LINE: MESSAGE, when it gives
data-say a value or names a sentence by number in data-lit (the form of sentence numbers written
by hand: each message names the new form); puts an element into a data-say element, leaves one
without text or unclosed; carries data-part on another element than an h2, data-voice on an h2,
an empty data-part or data-voice, or two of the three on one element; ends a holder's text without
a sentence mark; puts a [@name] mark anywhere but before a sentence's first word, gives it a
malformed name, or sets one name twice; names in data-lit a sentence no mark sets; links to an id
the page does not have; has a decision with fewer than two options, more than one data-mine="1",
no data-decision or data-title, or a data-decision used twice; or carries a <script> element or
an on... handler attribute. It refuses an explanation, besides, whose first part holds no figure
of class pseudo with a <pre> of two or more non-empty lines (at the first part's heading, at line 1
in a body without a data-part heading); whose figure of class questions opens before the second
data-part heading, anywhere in a body with one part or none (at that figure): the table of
questions follows the first part; or whose figure, unless of class quiz, has no data-nav or an
empty one (at that figure). With --terms it refuses each barred word the body's text holds (see
--terms). On a run that writes the page or reads --refs it refuses each data-ref whose KEY the
file of references lacks, and so every data-ref of a page built without --refs.

It warns, as BODY:LINE: warning: MESSAGE and without changing the exit code, about a spoken
sentence a voice may misread: one that starts with a lowercase letter, ends in a number before
its period, holds a decimal fraction, or holds a number with an ordinary space inside. It warns,
as REFS.json: warning: entry "KEY" is not used, about an entry of the file of references that no
data-ref names, on a built page and after the refusals of a refused one.

--story-out writes the story: one paragraph per part, an empty line between, the text
voice_cues.py reads. It needs no cues.

--cues CUES.json is the list voice_cues.py writes from that story: [{"paragraph", "sentence",
"text", "start", "end"}]. The cues must be the story's own, the same sentences in the same order
with the same text; else the body is refused at the first sentence that differs, to be voiced
again. The page takes the times from the cues and the text from the body. Without --cues the page
is silent: every sentence's cue starts and ends at 0, and --voice is absent or empty.

--terms TERMS.json is the list of terms: a JSON list of objects {"term": TEXT, "is": TEXT,
"code": TEXT, "not": [WORD, ...]}, "term" required. The builder searches the words the reader
sees or hears: the text of the body's elements outside a script, and the values of data-part,
data-voice, data-nav, alt, title and aria-label, each at the line where the attribute stands;
sentence marks are left out. A WORD of "not" found there as a whole word, in any case and with
any white space between the words of a phrase, refuses the body at its line as BODY:LINE:
"FOUND" stands for "TERM": write the term. A WORD that ends in "*" stands for every word that
starts with the text before it. Every occurrence of any term is passed over first, so a barred
word inside a term is no violation. "is" and "code" hold the term's meaning and its name in the code; the
builder reads them as texts. A file that is no JSON, names a key twice in one object, is no list
of objects, or holds an entry with a key outside these four, without a non-empty "term", or with
a "not" that is no list of words is unreadable input.

--refs REFS.json is the file of references: a JSON object keyed by the KEYs data-ref uses, each
value a code entry {"path": FILE, "fragment": TEXT, "lines": N} or a source entry {"title":
TEXT, "note": TEXT, "href": URL}, "lines" and "note" optional. A code entry is anchored as a look
fragment item is, at the one line of FILE under --root that holds TEXT, and the page keeps the
lines from three above that line to N below it, N 12 by default and from 1 to 60; an entry that
does not resolve so refuses the body as REFS.json: entry "KEY": MESSAGE, naming the lines found.
A source entry's "href" is an http: or https: address. Only the entries the body names are
resolved and reach the page. A file that is no JSON object, names a key twice in one object, or
holds a value that is neither kind of entry as written here is unreadable input.

--editor-url URL is a link template holding {path} and {line}, such as vscode://file{path}:{line}:
each code entry on the page then carries the link with its file's absolute path, percent-encoded,
and its line. It needs --standalone, --refs and --root, as the link carries a path of this machine.

The page's parts: one per part of the story, starting at its sentence P.1, titled by the text of
its data-part heading, the opening by the string "opening"; a heading without text gives "part"
and the part's number.

The page with --voice has a button at the end of each part's heading, the opening's in the h1, or
on a line of its own before an opening without one. The button speaks its part and the voice stops
where the next part starts, whose button then offers the next part. The button of the part being
spoken pauses and resumes it; another part's button moves the voice to that part. Once the reader
has started the voice, the Space key pauses and resumes it; before that, Space is the browser's.
A click on the text leaves the voice as it is. A page without --voice says that it has no audio.

Selecting text does nothing by itself: beside a selection in the article the page shows two
buttons, one copying the selected text and one opening a comment window on it, and a click on a
commented piece opens its comment again. The copied answer and the stored one carry the comments
after the decisions and the parts. A comment pauses a running voice and, when it was running,
resumes it from the start of that sentence; a words field pauses it when the cursor enters.

The page of an explanation carries a map: one group per part, listing the part's figures and its
other elements with data-nav by kind and name, a question without data-nav by its text; the
reader's place on the page is marked on it. From 840 pixels wide the map stands beside the text,
open unless the reader closed it; below that it lies over the text and opens at a button.

An element with data-ref whose entry reached the page shows a preview of it when focused, or
pointed at on a device that can point, and opens it in a panel on a click, Enter or Space: a
code entry's excerpt with its anchored line marked and, with --editor-url, the link into the
editor; a source entry's title, note and link. The panel stands at the right beside the text, and
pushes it, while the text column keeps at least 480 pixels next to the open map and the panel; in
a narrower window, and below 840 pixels, it lies over the text. The page settles this when the
panel opens, when the map opens or closes, and when the window is resized, and the reference the
reader opened keeps its place on the screen when the text moves.

"Where to look" is a section after the body, from one of two sources; with neither the page has
none. --report REPORT.md: the list under the heading that check_report.py's LOOK_HEADING matches,
with the headings of its lexicon file $XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json added
when that file exists, under that heading's text; a report without that heading is unreadable
input. An item whose first `path:line` or `path:line-end` code span names a file and lines under
--root shows the lines from three above to three below, the anchored ones marked; any other item
shows its text; without --root no anchor resolves. --look LOOK.json: a JSON list of objects,
{"what": WORDS, "path": FILE, "fragment": TEXT} or {"what": WORDS}, under the string "look". A
fragment item becomes the item WORDS: `FILE:LINE` `TEXT`, LINE being the one line of FILE under
--root that holds TEXT, and shows as a report's anchored item; it is refused, naming the item and
the lines found, without --root, when FILE is missing or outside it, or when TEXT stands on no
line or on more than one. A list that is not a JSON list of objects, an item without "what", or
an item with "path" and no "fragment" or the reverse is unreadable input.

--text-out writes the page's visible text, top to bottom: "#", "##" and "###" before an h1, an
h2, and an h3 or h4; a paragraph or a list item per line, "- " before an item, "+ " before an
li.plus; a table row as its cells joined by " | "; code in backticks and a pre between ``` lines;
a figcaption, each SVG text and a summary with the content of its details as lines; then the
heading and the items of "Where to look". Spoken text that is not shown (data-part and
data-voice values) stays out.

Strings: every word the page shows comes from one dictionary with English defaults (STRINGS).
--strings FILE overrides keys; without it, $XDG_CONFIG_HOME/handing-over-to-readers/page-strings.json
is read when it exists ($HOME/.config when the variable is unset or empty). A key of
RETIRED_STRINGS in that file is dropped with the line FILE: warning: key "KEY" is retired and
ignored; any other key outside STRINGS makes the file unreadable input.

The template's <!--TITLE--> takes the title (--title, else the body's first h1, else the id),
<!--BODY--> the expanded body and the "Where to look" section, and /*DATA*/ one JSON object:
{"cues", "parts", "strings", "voice", "id", "map", "refs"}, "map" true on an explanation and
"refs" the page data of each entry the body names, by KEY: {"kind": "code", "path", "line",
"excerpt": [[NUMBER, TEXT, ANCHORED], ...], "editor"?} or {"kind": "source", "title", "note",
"href"}. Every "<" in it is written as \\u003c. The output starts with <title> and carries no
html, head or body tag; --standalone wraps it in a complete document.

Reads the files named on the command line, voice_cues.py beside this script, check_report.py
beside it with --report, the two configuration files named above when they exist, and the files
under --root that the look list and the code entries anchor; writes the files of --out,
--story-out and --text-out and, with the usage journal of feedback.py turned on, one line of
counts to that journal on exit 0 or 1: built or refused, the numbers of sentences, parts,
decisions, look items and violations.
Exit: 0 written; 1 the body breaks its contract or the list of terms, the cues are not the
story's, or a look item or a code entry does not resolve; 2 unreadable input, template, strings,
terms or references, options that do not go together, or an output that cannot be written.
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import math
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from types import ModuleType
from typing import Callable, Collection, Mapping, final
from urllib.parse import quote, unquote, urlsplit

STRINGS = {
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
    "look": "Where to look",
    "knew": "I had it",
    "missed": "I did not",
    "returnTo": "Worth returning to:",
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
# Retired keys: words the page does not show that a user's strings file may hold. Each is dropped with a warning and the
# file builds; any other key outside STRINGS makes the file unreadable input.
RETIRED_STRINGS = frozenset(("now", "notPlaying", "jump", "hintPause", "hintNote", "hintNoteSpoken", "noteSpoken", "parts"))
HERE = Path(__file__).resolve().parent
STRINGS_FILE = Path("handing-over-to-readers") / "page-strings.json"
LEXICON_FILE = Path("handing-over-to-readers") / "lexicon.json"
TEMPLATE = HERE.parent / "assets" / "page-template.html"
MARKERS = ("<!--TITLE-->", "<!--BODY-->", "/*DATA*/")
PAGE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
VOID_TAGS = frozenset("area base br col embed hr img input link meta source track wbr".split())

# The body contract
SAY, PART, VOICE, LIT = "data-say", "data-part", "data-voice", "data-lit"
HOLDERS = (SAY, PART, VOICE)  # the attributes that hold spoken text
REWRITTEN = frozenset((PART, VOICE, LIT))  # what the page takes in another form
CUE_ID = re.compile(r"^\d+\.\d+$")
NAME = re.compile(r"[^\W\d_][\w-]*")  # a letter, then letters, digits, "_" or "-"
LEAD_MARK = re.compile(r"\[@([^\]]*)\]\s*")
MARK_START = "[@"
LOOK_TARGET = "look-heading"
EXCERPT = 60  # characters of a sentence a message quotes

# An explanation
PSEUDO, QUESTIONS, QUIZ = "pseudo", "questions", "quiz"
EXPLANATION_FIGURES = frozenset((PSEUDO, QUESTIONS, QUIZ))  # a figure of one of these classes makes the body an explanation
PSEUDO_LINES = 2  # the fewest non-empty lines of the pseudocode
FIRST_PART = "the first part of an explanation gives the mechanism whole, with its rule as pseudocode, one line a step"
NAV = "data-nav"  # the short name of a figure or a passage on the map of the page

# Text a voice misreads
LOWERCASE_START = re.compile(r"[\W_]*([^\W\d_])")
NUMBER_END = re.compile(r"(\S*\d)\.$")
DECIMAL = re.compile(r"\d+[.,]\d+")
SPACED_NUMBER = re.compile(r"\b\d{1,3}(?: \d{3})+\b")

# Where to look
FENCE = re.compile(r"^\s*(?:```|~~~)")
HEADING = re.compile(r"^\s*#{1,6}\s")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
CODE_SPAN = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)")
ANCHOR = re.compile(r"^(?P<path>[^\s`:*?\"<>|]+?):(?P<line>\d+)(?:-(?P<end>\d+))?$")
CONTEXT_LINES = 3
LINES_NAMED = 8  # a fragment found on more lines is reported by its first lines

# The list of terms
TERM_KEYS = ("term", "is", "code", "not")
WORD_STAR = "*"  # a barred word that ends in it stands for every word that starts with the text before it
MARK = re.compile(r"\[@[^\]]*\]")  # a sentence mark, wherever it stands: neither shown nor spoken
# The attributes whose values the reader hears or sees, searched for barred words beside the body's text
WORD_ATTRIBUTES = frozenset((PART, VOICE, NAV, "alt", "title", "aria-label"))

# References
REF = "data-ref"
CODE_KEYS, CODE_REQUIRED = frozenset(("path", "fragment", "lines")), frozenset(("path", "fragment"))
SOURCE_KEYS, SOURCE_REQUIRED = frozenset(("title", "note", "href")), frozenset(("title", "href"))
REF_LINES = 12  # lines of a code entry's excerpt below its line, by default
REF_LINES_MOST = 60
WEB_SCHEMES = frozenset(("http", "https"))

# The page's text
HEADING_MARKS = {"h1": "# ", "h2": "## ", "h3": "### ", "h4": "### "}
TEXT_BLOCKS = frozenset("address article aside blockquote dd details div dl dt figcaption figure footer form h1 h2 h3 h4 h5 h6 "
                        "header hr li main nav ol p section summary table tbody tfoot thead ul".split())
UNSHOWN = frozenset(("script", "style", "template"))


class InputError(Exception):
    """An input the build cannot use: exit 2."""


class LookMiss(Exception):
    """A look item whose fragment does not name one line of a file under --root: exit 1."""


# The body


@dataclass(eq=False)
class Element:
    """A start tag that holds spoken text or carries data-lit, with its place in the body."""
    tag: str
    line: int
    start: int  # offset of its "<" in the body
    end: int  # offset just past its start tag
    attrs: list[tuple[str, str | None]]  # as the parser read them: names in lower case, values decoded, None without a value
    closes_itself: bool = field(kw_only=True)
    say_text: list[str] = field(default_factory=list)  # data-say: the text inside, entities decoded
    close_start: int | None = None  # data-say: the offset of its end tag
    title: str = ""  # a data-part heading: its visible text

    @property
    def holders(self) -> dict[str, str | None]:
        """Its attributes of HOLDERS, in that order."""
        values = dict(self.attrs)
        return {name: values[name] for name in HOLDERS if name in values}

    @property
    def lit(self) -> list[str]:
        """The tokens of its data-lit."""
        return (dict(self.attrs).get(LIT) or "").split()

    @property
    def kind(self) -> str | None:
        """The holder attribute it carries, the first of HOLDERS when it carries more; None for data-lit alone."""
        return next(iter(self.holders), None)

    @property
    def spoken(self) -> str:
        """Its spoken text as written, the marks in place."""
        if self.kind == SAY:
            return "".join(self.say_text)
        return self.holders.get(self.kind) or ""


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
    depth: int
    part: Element | None  # the element of a data-part heading
    text: list[str] = field(default_factory=list)


@dataclass
class Figure:
    """A <figure> of the body with the tokens of its class attribute, its data-nav name, and the number of non-empty
    lines of each <pre> it holds."""
    classes: frozenset[str]
    nav: str  # the data-nav value with its white space collapsed; "" without one
    line: int
    start: int  # offset of its "<" in the body
    depth: int
    pre_line_counts: list[int] = field(default_factory=list)

    @property
    def holds_pseudocode(self) -> bool:
        """Whether it is of class pseudo and holds a <pre> of PSEUDO_LINES non-empty lines or more."""
        return PSEUDO in self.classes and max(self.pre_line_counts, default=0) >= PSEUDO_LINES


@dataclass
class Pre:
    """A <pre> being read: its depth and its text so far."""
    depth: int
    text: list[str] = field(default_factory=list)


@final  # its constructor runs the parser, which calls the handlers below
class BodyScan(HTMLParser):
    """Reads a body once and records, in document order, the elements that hold spoken text or carry data-lit; its
    decisions, its figures, its first h1, its ids, internal links and data-ref keys; whether it is an explanation; and
    the violations its markup shows by itself: a data-say element left open or holding an element, a script element, a
    handler attribute. `explanation` declares the body an explanation, as --explanation does."""

    def __init__(self, body: str, *, explanation: bool = False):
        super().__init__(convert_charrefs=True)
        self._declared_explanation = explanation
        self._line_starts = [0] + [match.end() for match in re.finditer("\n", body)]
        self._stack: list[str] = []
        self._pending: Element | None = None  # the data-say element whose text is being read
        self._decisions: list[Decision] = []
        self._headings: list[Heading] = []
        self._figures: list[Figure] = []  # the figures open at the place being read
        self._pre: Pre | None = None  # the outermost pre open at the place being read
        self.elements: list[Element] = []
        self.decisions: list[Decision] = []
        self.figures: list[Figure] = []
        self.h1: str | None = None
        self.ids: set[str] = set()
        self.links: list[tuple[str, int]] = []
        self.refs: list[tuple[str, int]] = []  # (data-ref key, line) in document order
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

    def _unclosed(self, say: Element, where: str) -> None:
        self.violations.append((say.line, f"<{say.tag} data-say> is not closed before {where}: write <{say.tag} data-say>its sentences</{say.tag}>"))
        self._pending = None

    def _element(self, tag: str, attrs: list[tuple[str, str | None]], line: int, *, closes_itself: bool) -> Element | None:
        if all(name not in HOLDERS and name != LIT for name, _ in attrs):
            return None
        start = self._offset()
        element = Element(tag, line, start, start + len(self.get_starttag_text() or ""), attrs, closes_itself=closes_itself)
        self.elements.append(element)
        return element

    def _start(self, tag: str, attrs: list[tuple[str, str | None]], *, closes_itself: bool) -> None:
        line = self.getpos()[0]
        if self._pending is not None:
            self.violations.append((self._pending.line, f"<{self._pending.tag} data-say> holds an element <{tag}>: data-say takes text alone"))
            self._pending = None
        values = dict(attrs)
        if tag == "script":
            self.violations.append((line, "a <script> element: the body carries no script, the page's script is the template's"))
        for name, _ in attrs:
            if name.startswith("on"):
                self.violations.append((line, f"a handler attribute {name}=: the body carries no script"))
        if values.get("id"):
            self.ids.add(values["id"])
        href = values.get("href") or ""
        if href.startswith("#") and len(href) > 1:
            self.links.append((unquote(href[1:]), line))
        element = self._element(tag, attrs, line, closes_itself=closes_itself)
        if "data-option" in values and self._decisions:
            self._decisions[-1].options += 1
            self._decisions[-1].mine += values.get("data-mine") == "1"
        figure = None
        if values.get(REF) is not None:
            self.refs.append((values[REF].strip(), line))
        if tag == "figure":
            figure = Figure(frozenset((values.get("class") or "").split()), " ".join((values.get(NAV) or "").split()), line, self._offset(),
                            len(self._stack) + 1)
            self.figures.append(figure)
        says = element is not None and element.kind == SAY
        if closes_itself or tag in VOID_TAGS:
            if says:
                self._unclosed(element, "its own start tag ends")
            return
        self._stack.append(tag)
        if says:
            self._pending = element
        if tag == "section" and "decision" in (values.get("class") or "").split():
            self._decisions.append(Decision(values.get("data-decision"), values.get("data-title"), line, len(self._stack)))
        if tag in ("h1", "h2"):
            part = element if element is not None and PART in element.holders else None
            self._headings.append(Heading(tag, len(self._stack), part))
        if figure is not None:
            self._figures.append(figure)
        if tag == "pre" and self._pre is None:
            self._pre = Pre(len(self._stack))

    def _pop(self) -> None:
        depth = len(self._stack)
        self._stack.pop()
        if self._decisions and self._decisions[-1].depth == depth:
            self.decisions.append(self._decisions.pop())
        if self._pre is not None and self._pre.depth == depth:
            lines = sum(1 for text in "".join(self._pre.text).splitlines() if text.strip())
            for figure in self._figures:
                figure.pre_line_counts.append(lines)
            self._pre = None
        if self._figures and self._figures[-1].depth == depth:
            self._figures.pop()
        if self._headings and self._headings[-1].depth == depth:
            heading = self._headings.pop()
            text = " ".join("".join(heading.text).split())
            if heading.part is not None:
                heading.part.title = text
            elif heading.tag == "h1" and self.h1 is None:
                self.h1 = text

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, closes_itself=False)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._start(tag, attrs, closes_itself=True)

    def handle_endtag(self, tag: str) -> None:
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

    def handle_data(self, data: str) -> None:
        if self._pending is not None:
            self._pending.say_text.append(data)
        for heading in self._headings:
            heading.text.append(data)
        if self._pre is not None:
            self._pre.text.append(data)

    @property
    def is_explanation(self) -> bool:
        """Whether the body was declared an explanation or one of its figures has a class that marks one."""
        return self._declared_explanation or any(figure.classes & EXPLANATION_FIGURES for figure in self.figures)


# The story


@dataclass(frozen=True)
class Splitter:
    """How the voice reads a story: the white space and the sentence bounds of voice_cues.py."""
    paragraphs: Callable[[str], list[str]]
    sentence_spans: Callable[[str], list[tuple[int, int]]]

    def normal(self, text: str) -> str:
        """The text on one line, its white space as the voice reads a paragraph's."""
        return " ".join(self.paragraphs(text))

    def sentences(self, text: str) -> list[str]:
        return [text[start:end] for start, end in self.sentence_spans(text)]

    def ends_sentence(self, text: str) -> bool:
        """Whether a word written after the text, as the next holder's text follows it in the story, starts a sentence."""
        return len(self.sentence_spans(text + " x")) > len(self.sentence_spans(text))


@dataclass(frozen=True)
class Spoken:
    """A sentence of one holder: its text without the mark, and the name the mark gave it."""
    text: str
    name: str | None


def sentence_id(part: int, number: int) -> str:
    """The id P.S by which the cues, the page and its script name a sentence."""
    return f"{part}.{number}"


@dataclass
class Sentence:
    part: int
    number: int
    text: str
    name: str | None
    holder: Element

    @property
    def id(self) -> str:
        return sentence_id(self.part, self.number)


def excerpt(text: str) -> str:
    return text if len(text) <= EXCERPT else text[:EXCERPT - 1] + "…"


def read_holder(element: Element, splitter: Splitter) -> tuple[list[Spoken], list[str]]:
    """The holder's sentences in order, and what is wrong with its text, its marks and its end, one message each."""
    text = splitter.normal(element.spoken)
    if not text:
        return [], [f"<{element.tag} {element.kind}> holds no text: write the sentences it says"]
    sentences, problems = [], []
    for piece in splitter.sentences(text):
        said, name = piece, None
        mark = LEAD_MARK.match(piece)
        if mark:
            said, name = piece[mark.end():], mark.group(1)
            if not NAME.fullmatch(name):
                problems.append(f"the mark {mark.group().strip()} holds no name: a name is a letter, then letters, digits, '_' or '-'")
                name = None
        if MARK_START in said:
            problems.append(f"the sentence {excerpt(said)!r} holds a mark after its start: write [@name] before the sentence's first word")
        if not said:
            problems.append(f"the mark {piece.strip()} stands before no sentence")
            continue
        sentences.append(Spoken(said, name))
    if sentences and not splitter.ends_sentence(sentences[-1].text):
        problems.append(f"<{element.tag} {element.kind}> ends without a sentence mark (. ! ? …): "
                        f"its last sentence {excerpt(sentences[-1].text)!r} would run into the next one when voiced")
    return sentences, problems


class Story:
    """The numbered story of a body without contract violations: its parts in speech order, each a list of sentences,
    with the data-part heading that starts it (None for the opening)."""

    def __init__(self, scan: BodyScan, splitter: Splitter):
        groups: list[tuple[Element | None, list[tuple[Spoken, Element]]]] = [(None, [])]
        for element in scan.elements:
            if element.kind is None:
                continue
            if element.kind == PART:
                groups.append((element, []))
            groups[-1][1].extend((spoken, element) for spoken in read_holder(element, splitter)[0])
        groups = [group for group in groups if group[1]]  # an opening without a spoken sentence is no part
        self.headings: list[Element | None] = [heading for heading, _ in groups]
        self.parts: list[list[Sentence]] = [
            [Sentence(part, number, spoken.text, spoken.name, element) for number, (spoken, element) in enumerate(said, 1)]
            for part, (_, said) in enumerate(groups, 1)]
        self._named = {sentence.name: sentence.id for sentence in self.sentences() if sentence.name}

    def sentences(self) -> list[Sentence]:
        return [sentence for part in self.parts for sentence in part]

    def paragraphs(self) -> list[str]:
        """One line per part, its sentences joined by one space: the paragraphs of the story file."""
        return [" ".join(sentence.text for sentence in part) for part in self.parts]

    def id_of(self, name: str) -> str:
        """The id P.S of the sentence a [@name] mark names; KeyError for a name no mark sets."""
        return self._named[name]


def load_neighbour(name: str, path: Path) -> ModuleType:
    """The script at `path` loaded as module `name`; any failure of the script propagates."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # its dataclasses resolve their own module by name
    spec.loader.exec_module(module)
    return module


def load_splitter() -> Splitter:
    """The sentence rule of voice_cues.py beside this script, loaded by its path."""
    path = HERE / "voice_cues.py"
    try:
        module = load_neighbour("handover_voice_cues", path)
        return Splitter(module.paragraphs, module.sentence_spans)
    except Exception as e:  # an isolation point: any failure of the neighbour script is one input error here
        raise InputError(f"cannot take the sentence rule from {path}: {e}") from e


def placement(element: Element) -> list[str]:
    """What is wrong with where the element's holder attributes stand, as written."""
    found = []
    holders = element.holders
    if len(holders) > 1:
        found.append(f"<{element.tag}> carries {' and '.join(holders)}: an element holds its spoken text one way")
    say = " ".join((holders.get(SAY) or "").split())
    if say:
        found.append(f'data-say="{say}" names sentences by number: write the sentences inside the element and leave data-say without a value')
    if PART in holders and element.tag != "h2":
        found.append(f'data-part on <{element.tag}>: a part starts at an <h2 data-part="…">')
    if VOICE in holders and element.tag == "h2":
        found.append("data-voice on <h2>: the h2 that starts a part takes data-part")
    return found


def lit_problems(tokens: list[str], names: Mapping[str, int]) -> list[str]:
    """What is wrong with the tokens of one data-lit, given the names the marks set."""
    found = []
    for token in tokens:
        if CUE_ID.match(token):
            found.append(f'data-lit names sentence {token} by its number: set a mark [@name] before that sentence and write data-lit="@name"')
        elif not token.startswith("@") or not NAME.fullmatch(token[1:]):
            found.append(f"data-lit holds {token!r}: name a sentence as @name, a letter, then letters, digits, '_' or '-'")
        elif token[1:] not in names:
            found.append(f"data-lit names @{token[1:]}, which no [@{token[1:]}] mark sets")
    return found


def decision_violations(decisions: list[Decision]) -> list[tuple[int, str]]:
    found = []
    keys: dict[str, int] = {}
    for decision in decisions:
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
    return found


def explanation_violations(scan: BodyScan) -> list[tuple[int, str]]:
    """What breaks an explanation, as (body line, message): a first part without its pseudocode, each table of questions
    that opens before the first part ends, and each figure other than a question without a name for the map."""
    found = []
    parts = [element for element in scan.elements if element.tag == "h2" and PART in element.holders]
    end = parts[1].start if len(parts) > 1 else math.inf  # the offset at which the first part ends
    if not parts:
        found.append((1, 'the body has no <h2 data-part>, so the explanation has no first part to hold <figure class="pseudo">: '
                         + FIRST_PART))
    elif not any(figure.holds_pseudocode and parts[0].start < figure.start < end for figure in scan.figures):
        found.append((parts[0].line, 'no <figure class="pseudo"> holding a <pre> of two or more lines stands in the first part: '
                                     + FIRST_PART))
    for figure in scan.figures:
        if QUESTIONS in figure.classes and figure.start < end:
            found.append((figure.line, f'<figure class="{QUESTIONS}"> opens before the first part ends: the table of questions follows the first part'))
        if QUIZ not in figure.classes and not figure.nav:
            found.append((figure.line, "<figure> has no data-nav: give the figure a short name for the map of the page"))
    return found


def validate(scan: BodyScan, splitter: Splitter, targets: set[str]) -> list[tuple[int, str]]:
    """Every violation of the body contract as (body line, message); `targets` are the ids the builder adds to the page."""
    found = list(scan.violations)
    if scan.is_explanation:
        found += explanation_violations(scan)
    names: dict[str, int] = {}
    for element in scan.elements:
        misplaced = placement(element)
        found += [(element.line, message) for message in misplaced]
        if element.kind is None or misplaced:
            continue
        sentences, problems = read_holder(element, splitter)
        found += [(element.line, message) for message in problems]
        for spoken in sentences:
            if spoken.name in names:
                found.append((element.line, f"the name @{spoken.name} is set twice (first on line {names[spoken.name]}): a name marks one sentence"))
            elif spoken.name:
                names[spoken.name] = element.line
    for element in scan.elements:
        found += [(element.line, message) for message in lit_problems(element.lit, names)]
    known = scan.ids | targets
    found += [(line, f'href="#{target}" names no id of the page') for target, line in scan.links if target not in known]
    found += decision_violations(scan.decisions)
    return sorted(found)


def sentence_count(scan: BodyScan, splitter: Splitter) -> int:
    """The number of sentences the body's holders say, whether or not the body keeps its contract."""
    return sum(len(read_holder(element, splitter)[0]) for element in scan.elements if element.kind is not None)


def misreadings(text: str) -> list[str]:
    """What a voice may misread in one sentence, one message each."""
    found = []
    first = LOWERCASE_START.match(text)
    if first and first.group(1).islower():
        found.append("starts with a lowercase letter: if an abbreviation's period ended the sentence before, write the abbreviation out")
    end = NUMBER_END.search(text)
    if end:
        found.append(f"ends in a number before its period ({end.group(1)}.): an ordinal such as '3.' may have cut the sentence there, "
                     "and a voice may read the number as an ordinal; end the sentence with a word")
    for number in DECIMAL.findall(text):
        found.append(f"holds the decimal fraction {number}: a voice may read its separator as another language does; write it in words")
    for number in SPACED_NUMBER.findall(text):
        found.append(f"holds the number {number!r} with an ordinary space inside: a voice may read two numbers; write it without the space or in words")
    return found


def lint(story: Story) -> list[tuple[int, str]]:
    """Warnings on spoken text a voice misreads, as (body line, message); they never refuse the body."""
    return [(sentence.holder.line, f"sentence {sentence.id} {message}") for sentence in story.sentences() for message in misreadings(sentence.text)]


# The cues


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
        if cue_id(item) in seen:
            raise InputError(f"the cues {path}: sentence {cue_id(item)} appears twice")
        seen.add(cue_id(item))
    return [{key: item[key] for key in ("paragraph", "sentence", "text", "start", "end")} for item in cues]


def cue_id(cue: dict) -> str:
    return sentence_id(cue["paragraph"], cue["sentence"])


def check_cues(cues: list[dict], story: Story) -> list[tuple[int, str]]:
    """The cues against the story: one violation at the first sentence where their ids or texts differ, else none."""
    sentences = story.sentences()
    again = "the cues are not this body's story; voice the story again (--story-out, then voice_cues.py)"
    for cue, sentence in zip(cues, sentences, strict=False):  # the counts are compared below
        if cue_id(cue) != sentence.id or cue["text"] != sentence.text:
            return [(sentence.holder.line, f"sentence {sentence.id} reads {sentence.text!r}, its cue {cue_id(cue)} reads {cue['text']!r}: {again}")]
    if len(cues) > len(sentences):
        extra = cues[len(sentences)]
        return [(0, f"cue {cue_id(extra)} {extra['text']!r} follows the body's last sentence: {again}")]
    if len(sentences) > len(cues):
        missing = sentences[len(cues)]
        return [(missing.holder.line, f"sentence {missing.id} {missing.text!r} has no cue: {again}")]
    return []


def page_cues(story: Story, cues: list[dict] | None) -> list[dict]:
    """The page's cues: the story's sentences at the times of the voice's cues, or at 0 on a silent page."""
    times = {cue_id(cue): (cue["start"], cue["end"]) for cue in cues or ()}
    return [{"paragraph": s.part, "sentence": s.number, "text": s.text, "start": times.get(s.id, (0.0, 0.0))[0], "end": times.get(s.id, (0.0, 0.0))[1]}
            for s in story.sentences()]


def derive_parts(story: Story, cues: list[dict], strings: Mapping[str, str]) -> list[dict]:
    """One part per paragraph of the story, starting at its first sentence and titled by the h2 that starts it."""
    start = {cue_id(cue): cue["start"] for cue in cues}
    parts = []
    for number, heading in enumerate(story.headings, 1):
        if heading is None:
            title = strings["opening"]
        else:
            title = heading.title or f"{strings['part']} {number}"
        first = sentence_id(number, 1)
        parts.append({"paragraph": number, "cue": first, "start": start[first], "title": title})
    return parts


# The page


def start_tag(element: Element, lit: list[str]) -> str:
    """The element's start tag rebuilt from its parsed attributes, without data-part, data-voice and data-lit, and lit
    by the ids `lit` when there are any. The names come in lower case, as an HTML parser reads them in any case."""
    pieces = [f"<{element.tag}"]
    for name, value in element.attrs:
        if name not in REWRITTEN:
            pieces.append(f" {name}" if value is None else f' {name}="{html.escape(value)}"')
    if lit:
        pieces.append(f' {LIT}="{" ".join(dict.fromkeys(lit))}"')
    pieces.append("/>" if element.closes_itself else ">")
    return "".join(pieces)


def expand(body: str, scan: BodyScan, story: Story) -> str:
    """The body in the page's form: each data-say element filled with one span per sentence, each data-part heading and
    data-voice element lit by its own sentences, each data-lit name turned into its sentence's id; the data-part and
    data-voice attributes and the marks stay out."""
    own: dict[Element, list[Sentence]] = {}
    for sentence in story.sentences():
        own.setdefault(sentence.holder, []).append(sentence)
    pieces, done = [], 0
    for element in scan.elements:
        said = own.get(element, [])
        named = [story.id_of(token[1:]) for token in element.lit]
        pieces.append(body[done:element.start])
        if element.kind == SAY:
            spans = " ".join(f'<span class="s" data-lit="{s.id}">{html.escape(s.text, quote=False)}</span>' for s in said)
            pieces += [start_tag(element, named) if element.lit else body[element.start:element.end], spans]
            done = element.close_start
        else:
            pieces.append(start_tag(element, [s.id for s in said] + named))
            done = element.end
    pieces.append(body[done:])
    return "".join(pieces)


# Where to look


@dataclass
class LookItem:
    """An item of "Where to look": its line in a report's Markdown, and the lines of the file it anchors, if any, as
    (number, text, anchored)."""
    text: str
    lines: list[tuple[int, str, bool]] | None


@dataclass
class Look:
    heading: str
    items: list[LookItem]
    misses: list[str]  # one message per item that does not resolve: the page is refused


def load_look_heading(config: Path) -> re.Pattern[str]:
    """LOOK_HEADING of check_report.py beside this script, loaded by its path, with the headings of
    the lexicon file in `config` added when that file exists, as check_report.py itself adds them."""
    path = HERE / "check_report.py"
    lexicon = config / LEXICON_FILE
    try:
        module = load_neighbour("handover_check_report", path)
        if lexicon.is_file() and hasattr(module, "apply_lexicon"):
            module.apply_lexicon(str(lexicon))
        return module.LOOK_HEADING
    except Exception as e:  # an isolation point: any failure of the neighbour script or its lexicon is one input error here
        raise InputError(f"cannot take LOOK_HEADING from {path} (lexicon {lexicon}): {e}") from e


def look_items(report: str, look_heading: re.Pattern[str]) -> tuple[str, list[str]]:
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


def code_text(span: re.Match[str]) -> str:
    """The content of a Markdown code span: one space on each side stripped when both are there."""
    content = span.group(2)
    if len(content) >= 2 and content[0] == content[-1] == " " and content.strip():
        return content[1:-1]
    return content


def code_span(text: str) -> str:
    """The text as one Markdown code span, its fence longer than any run of backticks inside it."""
    fence = "`" * (max((len(run) for run in re.findall(r"`+", text)), default=0) + 1)
    pad = " " if text.startswith("`") or text.endswith("`") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def inline_html(text: str) -> str:
    """Markdown text with its code spans as <code>, everything else escaped."""
    pieces, done = [], 0
    for span in CODE_SPAN.finditer(text):
        pieces += [html.escape(text[done:span.start()]), f"<code>{html.escape(code_text(span))}</code>"]
        done = span.end()
    pieces.append(html.escape(text[done:]))
    return "".join(pieces)


def context(lines: list[str], first: int, last: int) -> list[tuple[int, str, bool]]:
    """(number, text, anchored) for the lines first..last of a file and CONTEXT_LINES around them."""
    low, high = max(1, first - CONTEXT_LINES), min(len(lines), last + CONTEXT_LINES)
    return [(number, lines[number - 1], first <= number <= last) for number in range(low, high + 1)]


def lines_under(root: Path, path: str) -> list[str]:
    """The lines of the file `path` under `root`; LookMiss naming why there are none."""
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise LookMiss(f"{path} lies outside --root")
    if not target.is_file():
        raise LookMiss(f"{path} is no file under --root")
    try:
        return target.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as e:
        raise LookMiss(f"cannot read {path}: {e}") from e


def anchored_lines(item: str, root: Path | None) -> list[tuple[int, str, bool]] | None:
    """The lines around the item's first resolving anchor, or None."""
    if root is None:
        return None
    for span in CODE_SPAN.finditer(item):
        match = ANCHOR.match(code_text(span).strip())
        if not match:
            continue
        try:
            lines = lines_under(root, match["path"])
        except LookMiss:  # a report's item whose anchor does not resolve is shown as its text
            return None
        first, last = int(match["line"]), int(match["end"] or match["line"])
        if not 1 <= first <= last <= len(lines):
            return None
        return context(lines, first, last)
    return None


def read_look(path: Path) -> list[dict]:
    """The look list: a JSON list of objects, each with a "what", and with a "path" and a "fragment" both or neither."""
    text = read_text(path, "look list")
    try:
        entries = json.loads(text)
    except json.JSONDecodeError as e:
        raise InputError(f"cannot read the look list {path}: {e}") from e
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise InputError(f"the look list {path} is not a JSON list of objects")
    for index, entry in enumerate(entries, 1):
        for key in ("what", "path", "fragment"):
            if key in entry and not (isinstance(entry[key], str) and entry[key].strip()):
                raise InputError(f"the look list {path}: the {key!r} of item {index} is not a text")
        if "what" not in entry:
            raise InputError(f"the look list {path}: item {index} has no \"what\"")
        if ("path" in entry) != ("fragment" in entry):
            raise InputError(f"the look list {path}: item {index} has a \"path\" without a \"fragment\" or the reverse; give both or neither")
    return entries


def locate(path: str, fragment: str, root: Path | None) -> tuple[list[str], int]:
    """The lines of the file `path` under `root` and the number of the one line that holds the fragment; LookMiss when
    there is no such file or not exactly one such line."""
    if root is None:
        raise LookMiss("a fragment item needs --root")
    lines = lines_under(root, path)
    found = [number for number, line in enumerate(lines, 1) if fragment in line]
    if not found:
        raise LookMiss(f"{fragment!r} stands on no line of {path}")
    if len(found) > 1:
        named = ", ".join(map(str, found[:LINES_NAMED])) + (", …" if len(found) > LINES_NAMED else "")
        raise LookMiss(f"{fragment!r} stands on lines {named} of {path}: lengthen it so it names one line")
    return lines, found[0]


def resolve_look(entries: list[dict], root: Path | None) -> tuple[list[LookItem], list[str]]:
    """Each item of a look list as an item of "Where to look", a fragment item anchored at the one line of its file under
    `root` that holds the fragment; and one message per fragment item that does not resolve so."""
    items, misses = [], []
    for index, entry in enumerate(entries, 1):
        if "path" not in entry:
            items.append(LookItem(entry["what"], None))
            continue
        path, fragment = entry["path"], entry["fragment"]
        try:
            lines, number = locate(path, fragment, root)
        except LookMiss as miss:
            misses.append(f"item {index} ({excerpt(' '.join(entry['what'].split()))}): {miss}")
            continue
        text = f"{entry['what']}: {code_span(f'{path}:{number}')} {code_span(fragment)}"
        items.append(LookItem(text, context(lines, number, number)))
    return items, misses


def look_section(look: Look) -> str:
    entries = []
    for item in look.items:
        if item.lines is None:
            entries.append(f'  <li class="look-item">{inline_html(item.text)}</li>')
            continue
        width = len(str(item.lines[-1][0]))
        rows = []
        for number, text, anchored in item.lines:
            row = f'<span class="ln">{number:>{width}}</span>  {html.escape(text)}'
            rows.append(f'<span class="hit">{row}</span>' if anchored else row)
        entries.append(f'  <li class="look-item"><details><summary>{inline_html(item.text)}</summary>'
                       f'<pre class="src">{chr(10).join(rows)}</pre></details></li>')
    return (f'<section class="look" aria-labelledby="{LOOK_TARGET}">\n<h2 id="{LOOK_TARGET}">{html.escape(look.heading)}</h2>\n'
            f'<ul class="look-list">\n' + "\n".join(entries) + "\n</ul>\n</section>")


def read_json(path: Path, what: str) -> object:
    """The JSON value of the file; InputError when it cannot be read, is no JSON, or an object in it names a key twice."""
    text = read_text(path, what)
    try:
        return json.loads(text, object_pairs_hook=unique_keys)
    except ValueError as e:  # json.JSONDecodeError and the repeated key of unique_keys
        raise InputError(f"cannot read the {what} {path}: {e}") from e


def unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """A JSON object's pairs as a dict; ValueError naming a key that appears twice, which json.loads would keep once."""
    seen: dict[str, object] = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f'the key "{key}" appears twice in one object')
        seen[key] = value
    return seen


# The list of terms


@dataclass(frozen=True)
class Term:
    """A line of the list of terms: the term as written and the words the text must not use for it."""
    term: str
    barred: tuple[str, ...]


def read_terms(path: Path) -> list[Term]:
    """The list of terms: a JSON list of objects {"term", "is", "code", "not"}, "term" a non-empty text, "is" and "code"
    texts, "not" a list of words, each holding text before a closing WORD_STAR; InputError naming the entry otherwise."""
    entries = read_json(path, "list of terms")
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise InputError(f"the list of terms {path} is not a JSON list of objects")
    terms = []
    for index, entry in enumerate(entries, 1):
        unknown = sorted(set(entry) - set(TERM_KEYS))
        if unknown:
            raise InputError(f"the list of terms {path}: entry {index} holds unknown key(s) {', '.join(unknown)}; known: {', '.join(TERM_KEYS)}")
        if not (isinstance(entry.get("term"), str) and entry["term"].strip()):
            raise InputError(f'the list of terms {path}: entry {index} has no non-empty "term"')
        for key in ("is", "code"):
            if key in entry and not isinstance(entry[key], str):
                raise InputError(f'the list of terms {path}: the "{key}" of entry {index} is not a text')
        barred = entry.get("not", [])
        if not isinstance(barred, list) or not all(isinstance(word, str) and word.removesuffix(WORD_STAR).strip() for word in barred):
            raise InputError(f'the list of terms {path}: the "not" of entry {index} is not a list of words, '
                             f'each with text before a closing "{WORD_STAR}"')
        terms.append(Term(" ".join(entry["term"].split()), tuple(" ".join(word.split()) for word in barred)))
    return terms


def phrase_pattern(text: str, *, prefix: bool = False) -> str:
    """A regular expression for the words of `text` as whole words, any white space between them; with `prefix`, its
    last word may run on."""
    words = r"\s+".join(re.escape(word) for word in text.split())
    return rf"(?<!\w){words}" + (r"\w*" if prefix else r"(?!\w)")


def barred_pattern(word: str) -> re.Pattern[str]:
    """A barred word as a case-insensitive pattern: a whole word, or every word that starts with it when it ends in WORD_STAR."""
    starred = word.endswith(WORD_STAR)
    return re.compile(phrase_pattern(word.removesuffix(WORD_STAR), prefix=starred), re.IGNORECASE)


@final  # its constructor runs the parser, which calls the handlers below
class BodyText(HTMLParser):
    """Reads a body's own text as (line, text) pieces in document order: each text node outside a <script>, and the value
    of each attribute of WORD_ATTRIBUTES at the line where the attribute stands."""

    def __init__(self, body: str):
        super().__init__(convert_charrefs=True)
        self.pieces: list[tuple[int, str]] = []
        self._in_script = 0
        self.feed(body)
        self.close()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "script":
            self._in_script += 1
        line, raw = self.getpos()[0], (self.get_starttag_text() or "").lower()
        for name, value in attrs:
            if name in WORD_ATTRIBUTES and value:
                at = re.search(rf"(?<=\s){re.escape(name)}\s*=", raw)  # the attribute itself, not data-title for title
                self.pieces.append((line + raw.count("\n", 0, at.start() if at else 0), value))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag == "script":
            self._in_script -= 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_script:
            self._in_script -= 1

    def handle_data(self, data: str) -> None:
        if not self._in_script:
            self.pieces.append((self.getpos()[0], data))


def blank(match: re.Match[str]) -> str:
    """The matched text with every character but a line break made a space, so offsets and line numbers stay."""
    return re.sub(r"[^\n]", " ", match.group())


def term_violations(body: str, terms: list[Term]) -> list[tuple[int, str]]:
    """Each barred word the body's own text holds, as (body line, message). The text is read as BodyText reads it, its
    sentence marks and every occurrence of every term masked first, so a barred word inside a term is passed."""
    if not terms:
        return []
    longest_first = sorted((term.term for term in terms), key=len, reverse=True)
    masks = re.compile("|".join(phrase_pattern(text) for text in longest_first), re.IGNORECASE)
    barred = [(term, barred_pattern(word)) for term in terms for word in term.barred]
    found = []
    for line, text in BodyText(body).pieces:
        masked = masks.sub(blank, MARK.sub(blank, text))
        for term, pattern in barred:
            for hit in pattern.finditer(masked):
                found.append((line + masked.count("\n", 0, hit.start()),
                              f'"{" ".join(hit.group().split())}" stands for "{term.term}": write the term'))
    return found


# References


def ref_entry_problem(entry: object) -> str | None:
    """What makes a value of the file of references neither a code entry {"path", "fragment", "lines"} nor a source
    entry {"title", "note", "href"}, as the rest of a message after the entry's key; None for a usable entry."""
    keys = set(entry) if isinstance(entry, dict) else None
    if keys is not None and CODE_REQUIRED <= keys <= CODE_KEYS:
        if not all(isinstance(entry[key], str) and entry[key].strip() for key in CODE_REQUIRED):
            return 'has a "path" or a "fragment" that is not a non-empty text'
        lines = entry.get("lines", REF_LINES)
        if isinstance(lines, bool) or not isinstance(lines, int) or not 1 <= lines <= REF_LINES_MOST:
            return f'has "lines" {lines!r}, not an integer from 1 to {REF_LINES_MOST}'
        return None
    if keys is not None and SOURCE_REQUIRED <= keys <= SOURCE_KEYS:
        if not (isinstance(entry["title"], str) and entry["title"].strip()) or not isinstance(entry.get("note", ""), str):
            return 'has a "title" that is not a non-empty text or a "note" that is not a text'
        href = entry["href"] if isinstance(entry["href"], str) else ""
        parts = urlsplit(href)
        if parts.scheme.lower() not in WEB_SCHEMES or not parts.netloc:
            return f'has "href" {entry["href"]!r}, not an http: or https: address'
        return None
    return 'is neither a code entry {"path", "fragment", "lines"} nor a source entry {"title", "note", "href"}'


def read_refs(path: Path) -> dict[str, dict]:
    """The file of references: a JSON object keyed by name, each value a code entry or a source entry; InputError naming
    the key of an entry that is neither."""
    entries = read_json(path, "references")
    if not isinstance(entries, dict):
        raise InputError(f"the references {path} are not a JSON object")
    for key, entry in entries.items():
        problem = ref_entry_problem(entry)
        if problem is not None:
            raise InputError(f'the references {path}: entry "{key}" {problem}')
    return entries


def unknown_refs(named: list[tuple[str, int]], entries: Mapping[str, dict]) -> list[tuple[int, str]]:
    """Each data-ref of the body, as (key, line), whose key `entries` lacks, as (body line, message)."""
    return [(line, f'data-ref="{key}" names no entry of the references') for key, line in named if key not in entries]


def editor_link(template: str, path: Path, line: int) -> str:
    """The editor URL template with {path} filled by the file's absolute path, percent-encoded, and {line} by the line."""
    return template.replace("{path}", quote(path.resolve().as_posix())).replace("{line}", str(line))


def resolve_refs(entries: Mapping[str, dict], used: Collection[str], root: Path | None,
                 editor_url: str | None) -> tuple[dict[str, dict], list[str]]:
    """The page data of each entry whose key is in `used`, and one message per code entry among them that does not
    resolve. A code entry is anchored at the one line of its file under `root` that holds its fragment, as a look item
    is, and keeps the lines from CONTEXT_LINES above that line to its "lines" below, each as [number, text, anchored];
    with `editor_url` it carries the link into the editor. A source entry passes as it is, its note "" when it has none."""
    refs: dict[str, dict] = {}
    misses = []
    for key, entry in entries.items():
        if key not in used:
            continue
        if "href" in entry:
            refs[key] = {"kind": "source", "title": entry["title"], "note": entry.get("note", ""), "href": entry["href"]}
            continue
        if root is None:
            misses.append(f'entry "{key}": a code entry needs --root')
            continue
        try:
            lines, number = locate(entry["path"], entry["fragment"], root)
        except LookMiss as miss:
            misses.append(f'entry "{key}": {miss}')
            continue
        last = min(len(lines), number + entry.get("lines", REF_LINES))
        shown = [[n, lines[n - 1], n == number] for n in range(max(1, number - CONTEXT_LINES), last + 1)]
        refs[key] = {"kind": "code", "path": entry["path"], "line": number, "excerpt": shown}
        if editor_url is not None:
            refs[key]["editor"] = editor_link(editor_url, root / entry["path"], number)
    return refs, misses


# The page's text


@final  # its constructor runs the parser, which calls the handlers below
class TextScan(HTMLParser):
    """Reads an expanded body into its visible text, one line per block."""

    def __init__(self, body: str):
        super().__init__(convert_charrefs=True)
        self.lines: list[str] = []
        self._line: list[str] = []
        self._mark = ""  # what the next line starts with: a heading's "#", a list item's "-" or "+"
        self._cells: list[list[str]] | None = None  # the cells of the table row being read
        self._pre: list[str] | None = None  # the text of the pre being read
        self._inside: Counter[str] = Counter()  # how deep the reader is in hidden content, an svg, an svg text
        self._stack: list[tuple[str, tuple[str, ...]]] = []  # each open tag with the scopes it opened
        self.feed(body)
        self.close()
        while self._stack:
            self._close(*self._stack.pop())
        self._flush()

    def _add(self, text: str) -> None:
        if self._cells is not None:
            if self._cells:
                self._cells[-1].append(text)
        else:
            self._line.append(text)

    def _flush(self) -> None:
        text = " ".join("".join(self._line).split())
        self._line = []
        if text:
            self.lines.append(self._mark + text)
            self._mark = ""

    def _open(self, tag: str, values: dict[str, str | None]) -> tuple[str, ...]:
        """Acts on a start tag; returns the scopes it opens, which its end tag closes."""
        if self._inside["hidden"] or tag in UNSHOWN or "hidden" in values:
            self._inside["hidden"] += 1
            return ("hidden",)
        if self._pre is not None:
            return ()
        if self._inside["svg"]:
            return self._open_in_svg(tag)
        if tag in ("svg", "pre", "tr"):
            return self._open_container(tag)
        if tag == "code":
            self._add("`")
            return ("code",)
        if self._cells is not None:
            return self._open_in_row(tag)
        return self._open_in_flow(tag, values)

    def _open_in_svg(self, tag: str) -> tuple[str, ...]:
        """Inside an svg only a text element shows, as a line of its own."""
        if tag != "text":
            return ()
        self._flush()
        self._inside["text"] += 1
        return ("text",)

    def _open_container(self, tag: str) -> tuple[str, ...]:
        """An svg, a pre or a table row: each gathers its own text until it closes."""
        self._flush()
        if tag == "svg":
            self._inside["svg"] += 1
        elif tag == "pre":
            self._pre = []
        else:
            self._cells = []
        return (tag,)

    def _open_in_row(self, tag: str) -> tuple[str, ...]:
        """Inside a table row a cell starts a cell, a line break is a space, and every other tag is inline."""
        if tag in ("td", "th"):
            self._cells.append([])
        elif tag == "br":
            self._add(" ")
        return ()

    def _open_in_flow(self, tag: str, values: dict[str, str | None]) -> tuple[str, ...]:
        if tag == "br":
            self._flush()
            return ()
        if tag not in TEXT_BLOCKS:
            return ()
        self._flush()
        if tag in HEADING_MARKS:
            self._mark = HEADING_MARKS[tag]
        elif tag == "li":
            self._mark = "+ " if "plus" in (values.get("class") or "").split() else "- "
        return ("block",)

    def _close(self, tag: str, scopes: tuple[str, ...]) -> None:
        for scope in scopes:
            if scope in ("hidden", "svg"):
                self._inside[scope] -= 1
            elif scope == "text":
                self._flush()
                self._inside["text"] -= 1
            elif scope == "pre":
                self.lines += ["```", *"".join(self._pre).strip("\n").splitlines(), "```"]
                self._pre = None
            elif scope == "tr":
                cells = [" ".join("".join(cell).split()) for cell in self._cells]
                self._cells = None
                if any(cells):
                    self.lines.append(" | ".join(cells))
            elif scope == "code":
                self._add("`")
            elif scope == "block":
                self._flush()
                if tag in HEADING_MARKS or tag == "li":
                    self._mark = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        scopes = self._open(tag, dict(attrs))
        if tag not in VOID_TAGS:
            self._stack.append((tag, scopes))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._close(tag, self._open(tag, dict(attrs)))

    def handle_endtag(self, tag: str) -> None:
        if all(open_tag != tag for open_tag, _ in self._stack):
            return
        while self._stack:
            open_tag, scopes = self._stack.pop()
            self._close(open_tag, scopes)
            if open_tag == tag:
                break

    def handle_data(self, data: str) -> None:
        if self._inside["hidden"] or (self._inside["svg"] and not self._inside["text"]):
            return
        if self._pre is not None:
            self._pre.append(data)
        else:
            self._add(data)


def page_text(article: str, look: Look | None) -> str:
    """The page's visible text top to bottom, for a reader who reads it cold: the expanded body, then "Where to look"."""
    lines = TextScan(article).lines
    if look is not None:
        lines += [f"## {look.heading}", *(f"- {item.text}" for item in look.items)]
    return "\n".join(lines) + "\n"


# The run


def config_dir(environ: Mapping[str, str]) -> Path:
    """$XDG_CONFIG_HOME, or $HOME/.config when the variable is unset or empty."""
    return Path(environ.get("XDG_CONFIG_HOME") or Path(environ.get("HOME") or Path.home()) / ".config")


def load_strings(path: Path | None, config: Path) -> dict[str, str]:
    """STRINGS overridden by the given file, or by the configuration file in `config` when it exists. A key of
    RETIRED_STRINGS in the file is dropped with one warning line on stderr; any other unknown key is an InputError."""
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
    for key in sorted(RETIRED_STRINGS.intersection(overrides)):
        print(f'{path}: warning: key "{key}" is retired and ignored', file=sys.stderr)
        del overrides[key]
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


@dataclass
class Inputs:
    """What one run reads, before the body is judged."""
    body: str
    splitter: Splitter
    strings: dict[str, str]
    template: str | None  # None when the run writes no page
    cues: list[dict] | None  # None for a silent page
    look: Look | None  # None for a page without "Where to look"
    terms: list[Term] = field(default_factory=list)  # empty without --terms
    refs: dict[str, dict] | None = None  # the entries of --refs; None without it


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--body", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="the page")
    parser.add_argument("--story-out", type=Path, help="the story the voice reads, one paragraph per part")
    parser.add_argument("--text-out", type=Path, help="the page's visible text")
    parser.add_argument("--cues", type=Path, help="the cues voice_cues.py wrote from the story; without them the page is silent")
    parser.add_argument("--voice", default="", help="address of the audio; empty: a silent page without the buttons that play its parts")
    parser.add_argument("--report", type=Path, help="the report whose \"Where to look\" list the page shows")
    parser.add_argument("--look", type=Path, help="a JSON list of look items the page shows as \"Where to look\"")
    parser.add_argument("--root", type=Path, help="directory the files of the look items and of the code references resolve under")
    parser.add_argument("--terms", type=Path, help="a JSON list of terms with the words the text must not use for each")
    parser.add_argument("--refs", type=Path, help="a JSON object of references, keyed by the names the body's data-ref attributes use")
    parser.add_argument("--editor-url", help="a URL template with {path} and {line} that opens a code reference in the editor; "
                                             "with --standalone, --refs and --root only")
    parser.add_argument("--title")
    parser.add_argument("--id", default="report", help="name under which the page keeps the reader's answer")
    parser.add_argument("--strings", type=Path)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--standalone", action="store_true", help="write a complete HTML document")
    parser.add_argument("--explanation", action="store_true",
                        help="check the body as an explanation, which a figure of class pseudo, questions or quiz also makes "
                             "it: its first part must hold the rule as pseudocode in <figure class=\"pseudo\">, a table of "
                             "questions must open after the first part, and every figure but a question needs a data-nav name")
    return parser.parse_args(argv)


def check_options(args: argparse.Namespace) -> None:
    """InputError for options that do not go together."""
    if args.out is None and args.story_out is None and args.text_out is None:
        raise InputError("give at least one of --out, --story-out and --text-out")
    if args.voice and args.cues is None:
        raise InputError("--voice needs --cues: a page without cues is silent")
    if args.report is not None and args.look is not None:
        raise InputError("give --report or --look, not both")
    if not PAGE_ID.match(args.id):
        raise InputError(f"--id {args.id!r}: use letters, digits, '.', '_' and '-'")
    if args.root is not None and not args.root.is_dir():
        raise InputError(f"--root {args.root} is not a directory")
    if args.editor_url is not None:
        if not args.standalone or args.refs is None or args.root is None:
            raise InputError("--editor-url needs --standalone, --refs and --root: the link carries a path of this machine")
        if "{path}" not in args.editor_url:
            raise InputError(f"--editor-url {args.editor_url!r} holds no {{path}}")


def read_look_section(args: argparse.Namespace, config: Path, strings: Mapping[str, str]) -> Look | None:
    if args.report is not None:
        heading, items = look_items(read_text(args.report, "report"), load_look_heading(config))
        return Look(heading, [LookItem(item, anchored_lines(item, args.root)) for item in items], [])
    if args.look is not None:
        items, misses = resolve_look(read_look(args.look), args.root)
        return Look(strings["look"], items, misses)
    return None


def read_inputs(args: argparse.Namespace, environ: Mapping[str, str]) -> Inputs:
    """Everything the run reads; InputError for what it cannot use."""
    check_options(args)
    config = config_dir(environ)
    strings = load_strings(args.strings, config) if args.out or args.text_out else dict(STRINGS)
    template = None
    if args.out is not None:
        template = read_text(args.template, "template")
        for marker in MARKERS:
            if template.count(marker) != 1:
                raise InputError(f"the template {args.template} holds {marker} {template.count(marker)} times, not once")
    cues = read_cues(args.cues) if args.cues is not None else None
    body = read_text(args.body, "body")
    terms = read_terms(args.terms) if args.terms is not None else []
    refs = read_refs(args.refs) if args.refs is not None else None
    return Inputs(body, load_splitter(), strings, template, cues, read_look_section(args, config, strings), terms, refs)


def body_violations(args: argparse.Namespace, inputs: Inputs, scan: BodyScan) -> list[tuple[int, str]]:
    """Every violation of the body, sorted by line: its contract, the barred words of the list of terms and, on a run that
    writes the page or reads --refs, each data-ref that names no entry of the references."""
    targets = {LOOK_TARGET} if inputs.look is not None or args.out is None else set()
    found = validate(scan, inputs.splitter, targets) + term_violations(inputs.body, inputs.terms)
    if args.out is not None or inputs.refs is not None:
        found += unknown_refs(scan.refs, inputs.refs or {})
    return sorted(found)


def render(args: argparse.Namespace, inputs: Inputs, scan: BodyScan, story: Story, refs: dict[str, dict]) -> list[tuple[Path, str]]:
    """Each output file the run writes, with its text; `refs` is the page data of the references the body names."""
    outputs = []
    if args.story_out is not None:
        outputs.append((args.story_out, "\n\n".join(story.paragraphs()) + "\n"))
    article = expand(inputs.body, scan, story).rstrip() + "\n"
    if args.text_out is not None:
        outputs.append((args.text_out, page_text(article, inputs.look)))
    if args.out is not None:
        cues = page_cues(story, inputs.cues)
        data = {"cues": cues, "parts": derive_parts(story, cues, inputs.strings), "strings": inputs.strings, "voice": args.voice, "id": args.id,
                "map": scan.is_explanation, "refs": refs}
        page = fill(inputs.template, args.title or scan.h1 or args.id, article + (look_section(inputs.look) if inputs.look else ""), data)
        outputs.append((args.out, standalone(page) if args.standalone else page))
    return outputs


def main(argv: list[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    args = parse_args(argv)
    try:
        inputs = read_inputs(args, os.environ if environ is None else environ)
    except InputError as e:
        print(f"build_page: {e}", file=sys.stderr)
        return 2
    scan = BodyScan(inputs.body, explanation=args.explanation)
    found = body_violations(args, inputs, scan)
    story = None if found else Story(scan, inputs.splitter)
    if story is not None and inputs.cues is not None:
        found = check_cues(inputs.cues, story)
    used = {key for key, _ in scan.refs}
    refs, ref_misses = resolve_refs(inputs.refs or {}, used, args.root, args.editor_url)
    look_count = len(inputs.look.items) + len(inputs.look.misses) if inputs.look else 0
    refusals = [f"{args.body}:{line}: {message}" if line else f"{args.body}: {message}" for line, message in found]
    refusals += [f"{args.look}: {miss}" for miss in inputs.look.misses] if inputs.look else []
    refusals += [f"{args.refs}: {miss}" for miss in ref_misses]
    unused = [f'{args.refs}: warning: entry "{key}" is not used' for key in inputs.refs or {} if key not in used]
    if refusals:
        print("\n".join(refusals + unused), file=sys.stderr)
        journal("page", outcome="refused", sentences=sentence_count(scan, inputs.splitter), decisions=len(scan.decisions),
                look=look_count, violations=len(refusals))
        return 1
    warnings = unused + [f"{args.body}:{line}: warning: {message}" for line, message in lint(story)]
    if warnings:
        print("\n".join(warnings), file=sys.stderr)
    outputs = render(args, inputs, scan, story, refs)
    for path, text in outputs:
        try:
            path.write_text(text, encoding="utf-8")
        except OSError as e:
            print(f"build_page: cannot write {path}: {e}", file=sys.stderr)
            return 2
    sentences = story.sentences()
    print(f"{len(sentences)} sentences, {len(story.parts)} parts, {len(scan.decisions)} decision(s), {look_count} look item(s) -> "
          + ", ".join(str(path) for path, _ in outputs))
    journal("page", outcome="built", sentences=len(sentences), parts=len(story.parts), decisions=len(scan.decisions), look=look_count, violations=0)
    return 0


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
