#!/usr/bin/env python3
"""Check, for each citation of a provenance line, whether the words it quotes stand in its source.

    check_quotes.py [--cache DIR] [--json OUT] [--context N] [--timeout SECONDS] CITATIONS.json

The script settles the deterministic half of re-verifying a citation: whether the quoted words
occur in the cited source. Whether the passage supports the rule that cites it stays a reader's
judgement.

Input. CITATIONS.json is a UTF-8 JSON array of objects, each holding three non-empty strings:
  id      unique in the file, e.g. `M-3/2`
  source  an http:// or https:// URL, or the path of a local text or HTML file, relative to the
          current directory; a PDF or a Word document is converted to text beforehand
  quote   the quoted words; an ellipsis (`…`, `...` or `[...]`) splits them into fragments that
          must occur in the source in that order
Other keys of an object are not read. A source cited several times is read once per run.

Reading a source. A URL takes one GET with the User-Agent `Mozilla/5.0 (compatible; quote-check)`
and a timeout of --timeout seconds (30 by default) on connecting and on each read; a redirect to
an http or https URL is followed, one to any other scheme fails the GET. With --cache DIR the body
and its Content-Type are stored as DIR/<SHA-256 of the URL>.body and DIR/<SHA-256 of the URL>.json,
and a URL stored there opens no connection. A local path is read as a file with no Content-Type.
The body is decoded with the charset its Content-Type names, else as UTF-8 with replacement. HTML
becomes text through html.parser, with the contents of script and style dropped, entities
unescaped and every tag boundary read as a space: a body of type text/html or
application/xhtml+xml, or a body of a text/* type or with no Content-Type whose first character
after white space is `<`. Any other text/* body is taken as it is.

Matching. The source text and the quote are normalised alike: Unicode NFKC; curly quotation
marks, primes and guillemets to straight quotes; every dash (Unicode category Pd) and minus sign
to `-`; soft hyphens and zero-width characters removed; runs of white space to one space;
stripped. The fragments are searched in order, each search starting where the previous fragment
ended. Every fragment found exactly, or every fragment found when case is ignored, makes the
citation FOUND. Otherwise each fragment not found takes the window of the source most similar to
it (difflib.SequenceMatcher.ratio over the lowercased words): a similarity of 0.9 or more makes
the fragment NEAR, a lower one ABSENT, and the citation takes the worst status of its fragments
(FOUND < NEAR < ABSENT). The window search is bounded: each occurrence of a fragment word, the
rarest words first and 200,000 occurrences at most, votes for the window start that aligns it;
the ten starts with the most votes are scored, and the best window's ends move by up to three
words.
  UNREADABLE  the Content-Type is neither HTML nor text/*
  UNFETCHED   the GET failed (an HTTP status of 400 or more, a timeout, a refused connection, a
              body over 64 MiB) or the local file cannot be read

Output on stdout: one line per citation in the order of the file, `<id>: <STATUS>: <detail>`.
The detail of FOUND and NEAR is the context: the matched words with --context N characters of
the normalised source on each side (200 by default), windows of distant fragments joined by
` ... `; of ABSENT the best similarity; of UNREADABLE the Content-Type; of UNFETCHED the HTTP
status or the error. The last line is `<n> of <m> not found`. --json OUT writes an array of
objects {id, source, status, case_differs, ratio, source_words, context, content_type,
http_status, final_url, error}, status in lowercase; a field that does not apply is null:
case_differs is a boolean for FOUND; ratio is the lowest similarity among the fragments not found,
0 for a fragment none of whose words occurs in the rest of the source; source_words holds the
source's own words of the NEAR fragments.

Exit: 0 every citation FOUND; 1 at least one NEAR, ABSENT, UNREADABLE or UNFETCHED; 2 wrong usage,
an unreadable, non-UTF-8 or malformed CITATIONS.json, a duplicate id, or a cache directory or
--json file that cannot be written, with the message on stderr.

Privileges: reads the citations file and the local sources, opens HTTP and HTTPS connections to
the cited URLs alone and to the http or https URLs their redirects name, through the proxy the
environment configures if any, reads and writes the cache directory and writes the --json file.
A fetched body is data: it is never executed or imported, and it is written nowhere but the cache
directory, under a file name that is a hash. Standard library alone; runs under `python3 -I`.
"""
from __future__ import annotations

import argparse
import bisect
import dataclasses
import difflib
import email.message
import hashlib
import http.client
import json
import math
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

FOUND, NEAR, ABSENT, UNREADABLE, UNFETCHED = "found", "near", "absent", "unreadable", "unfetched"
MATCH_ORDER = (FOUND, NEAR, ABSENT)

USER_AGENT = "Mozilla/5.0 (compatible; quote-check)"
WEB_SCHEMES = ("http", "https")
MAX_BODY_BYTES = 64 * 1024 * 1024
HTML_TYPES = ("text/html", "application/xhtml+xml")
DROPPED_ELEMENTS = frozenset({"script", "style"})

NEAR_RATIO = 0.9
# The bounds of the window search: the word occurrences that vote for candidate starts, the
# candidates scored, and the words by which the best window's ends move.
VOTE_BUDGET = 200_000
SCORED_WINDOWS = 10
SHIFT_WORDS = 3

SINGLE_QUOTES = "‘’‚‛′‵‹›"
DOUBLE_QUOTES = "“”„‟″‶«»"
MINUS_SIGNS = "−⁒➖"
# Soft hyphen, Mongolian vowel separator, zero-width space, non-joiner and joiner, word joiner, byte order mark.
INVISIBLE = "\u00ad\u180e\u200b\u200c\u200d\u2060\ufeff"
WHITE_SPACE = re.compile(r"\s+")
ELLIPSIS = re.compile(r"\[\s*\.{3,}\s*\]|\.{3,}")
WORD = re.compile(r"\w+")


class InputError(Exception):
    """The run cannot go on: an unreadable or malformed citations file, or a cache or output file that cannot be written."""


class FetchError(Exception):
    """A GET that gave no body; http_status is the status of the response, None without one."""

    def __init__(self, message: str, http_status: int | None = None) -> None:
        super().__init__(message, http_status)
        self.message, self.http_status = message, http_status

    def __str__(self) -> str:
        return self.message


class Spelling(dict):
    """The translation table of normalise; a character outside the fixed entries is looked up once, by its category."""

    def __missing__(self, code: int) -> int | str:
        value = "-" if unicodedata.category(chr(code)) == "Pd" else code
        self[code] = value
        return value


SPELLING = Spelling({**{ord(c): "'" for c in SINGLE_QUOTES}, **{ord(c): '"' for c in DOUBLE_QUOTES},
                     **{ord(c): "-" for c in MINUS_SIGNS}, **{ord(c): None for c in INVISIBLE}})


def normalise(text: str) -> str:
    """The text as matching compares it; the source and the quote pass through the same steps."""
    text = unicodedata.normalize("NFKC", text).translate(SPELLING)
    return WHITE_SPACE.sub(" ", text).strip()


def fragments(quote: str) -> tuple[str, ...]:
    """The normalised parts of a quote between its ellipses, empty parts dropped."""
    parts = (part.strip() for part in ELLIPSIS.split(normalise(quote)))
    return tuple(part for part in parts if part)


@dataclass(frozen=True)
class Citation:
    id: str
    source: str
    quote: str
    fragments: tuple[str, ...]


@dataclass
class Result:
    """One citation's verdict; its fields, in this order, are the objects of the --json array."""
    id: str
    source: str
    status: str
    case_differs: bool | None = None
    ratio: float | None = None
    source_words: str | None = None
    context: str | None = None
    content_type: str | None = None
    http_status: int | None = None
    final_url: str | None = None
    error: str | None = None

    def detail(self) -> str:
        if self.status in (FOUND, NEAR):
            return self.context or ""
        if self.status == ABSENT:
            return f"no window of the source reaches {NEAR_RATIO}; the best similarity is {self.ratio:.3f}"
        return self.error or ""

    def __str__(self) -> str:
        return f"{self.id}: {self.status.upper()}: {self.detail()}"


@dataclass
class Fetched:
    body: bytes
    content_type: str | None
    http_status: int
    final_url: str


@dataclass
class Words:
    """The words of a source text: character offsets, lowercased forms and, per form, the word numbers holding it."""
    starts: list[int]
    ends: list[int]
    names: list[str]
    positions: dict[str, list[int]]


class SourceText:
    """A normalised source text; its word index is built on the first window search."""

    def __init__(self, text: str) -> None:
        self.text = text
        self._words: Words | None = None

    def words(self) -> Words:
        if self._words is None:
            words = Words([], [], [], defaultdict(list))
            for number, match in enumerate(WORD.finditer(self.text)):
                name = match.group().lower()
                words.starts.append(match.start())
                words.ends.append(match.end())
                words.names.append(name)
                words.positions[name].append(number)
            self._words = words
        return self._words


@dataclass
class Reading:
    """What reading one source gave: a text, or the status UNREADABLE or UNFETCHED with its error."""
    text: SourceText | None
    status: str | None = None
    error: str | None = None
    content_type: str | None = None
    http_status: int | None = None
    final_url: str | None = None


@dataclass
class Window:
    ratio: float
    start: int
    end: int


@dataclass
class Match:
    status: str
    case_differs: bool | None
    ratio: float | None
    spans: list[tuple[int, int]]
    near_spans: list[tuple[int, int]]


# ---------------------------------------------------------------- the citations file

def load_citations(path: Path) -> list[Citation]:
    try:
        data = json.loads(path.read_bytes().decode("utf-8-sig"))
    except OSError as error:
        raise InputError(f"cannot read {path}: {error}") from error
    except UnicodeDecodeError as error:
        raise InputError(f"{path} is not UTF-8: {error}") from error
    except json.JSONDecodeError as error:
        raise InputError(f"{path} is not JSON: {error}") from error
    except RecursionError as error:
        raise InputError(f"{path} nests its JSON deeper than the parser reads") from error
    if not isinstance(data, list):
        raise InputError(f"{path}: the top level is not an array")
    citations: list[Citation] = []
    first_item: dict[str, int] = {}
    for number, item in enumerate(data, 1):
        citation = parse_citation(item, f"{path}: item {number}")
        if citation.id in first_item:
            raise InputError(f"{path}: item {number}: id {citation.id!r} repeats the id of item {first_item[citation.id]}")
        first_item[citation.id] = number
        citations.append(citation)
    return citations


def parse_citation(item: object, where: str) -> Citation:
    if not isinstance(item, dict):
        raise InputError(f"{where} is not an object")
    values = {}
    for key in ("id", "source", "quote"):
        value = item.get(key)
        if not isinstance(value, str) or not value.strip():
            raise InputError(f"{where}: {key} is not a non-empty string")
        values[key] = value
    parts = fragments(values["quote"])
    if not parts:
        raise InputError(f"{where}: quote holds nothing beside ellipses")
    return Citation(values["id"], values["source"], values["quote"], parts)


# ---------------------------------------------------------------- reading a source

def http_opener() -> urllib.request.OpenerDirector:
    """An opener of http and https URLs alone: it holds no handler for file, ftp or data URLs, so no redirect reaches one."""
    opener = urllib.request.OpenerDirector()
    for handler in (urllib.request.ProxyHandler(), urllib.request.UnknownHandler(), urllib.request.HTTPHandler(),
                    urllib.request.HTTPSHandler(), urllib.request.HTTPDefaultErrorHandler(),
                    urllib.request.HTTPRedirectHandler(), urllib.request.HTTPErrorProcessor()):
        opener.add_handler(handler)
    return opener


def is_web_url(source: str) -> bool:
    return urllib.parse.urlsplit(source).scheme.lower() in WEB_SCHEMES


def fetch(opener: urllib.request.OpenerDirector, url: str, timeout: float) -> Fetched:
    """One GET of an http or https URL; raises FetchError for every way it gives no body."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            content_type = response.headers.get("Content-Type")
            http_status, final_url = response.status, response.geturl()
    except urllib.error.HTTPError as error:
        error.close()
        raise FetchError(f"HTTP {error.code} {error.reason}", error.code) from error
    except urllib.error.URLError as error:
        raise FetchError(f"cannot fetch {url}: {error.reason}") from error
    except (OSError, http.client.HTTPException, ValueError) as error:
        raise FetchError(f"cannot fetch {url}: {error or type(error).__name__}") from error
    if len(body) > MAX_BODY_BYTES:
        raise FetchError(f"the body of {url} exceeds {MAX_BODY_BYTES // (1024 * 1024)} MiB", http_status)
    return Fetched(body, content_type, http_status, final_url)


class Cache:
    """Fetched bodies under DIR, each as <SHA-256 of the URL>.body beside its metadata in <SHA-256 of the URL>.json."""

    def __init__(self, directory: Path) -> None:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise InputError(f"cannot create the cache directory {directory}: {error}") from error
        self.directory = directory

    def paths(self, url: str) -> tuple[Path, Path]:
        key = hashlib.sha256(url.encode("utf-8")).hexdigest()
        return self.directory / f"{key}.body", self.directory / f"{key}.json"

    def get(self, url: str) -> Fetched | None:
        body_path, meta_path = self.paths(url)
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            body = body_path.read_bytes()
            content_type, http_status, final_url = meta["content_type"], meta["http_status"], meta["final_url"]
        except (OSError, ValueError, TypeError, KeyError):
            # A missing or damaged entry is a miss: the fetch that follows writes the entry anew.
            return None
        if not (isinstance(content_type, (str, type(None))) and isinstance(http_status, int) and isinstance(final_url, str)):
            return None
        return Fetched(body, content_type, http_status, final_url)

    def put(self, url: str, fetched: Fetched) -> None:
        body_path, meta_path = self.paths(url)
        meta = {"url": url, "content_type": fetched.content_type, "http_status": fetched.http_status,
                "final_url": fetched.final_url}
        try:
            # The body lands before its metadata, so a stored .json always has its whole .body beside it.
            write_atomic(body_path, fetched.body)
            write_atomic(meta_path, (json.dumps(meta, ensure_ascii=False) + "\n").encode("utf-8"))
        except OSError as error:
            raise InputError(f"cannot write the cache entry of {url} in {self.directory}: {error}") from error


def write_atomic(path: Path, data: bytes) -> None:
    part = path.with_name(path.name + ".part")
    part.write_bytes(data)
    part.replace(path)


class TextParser(HTMLParser):
    """The text of an HTML document: script and style contents dropped, a space at every tag boundary."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.dropped_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in DROPPED_ELEMENTS:
            self.dropped_depth += 1
        self.parts.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if tag in DROPPED_ELEMENTS and self.dropped_depth:
            self.dropped_depth -= 1
        self.parts.append(" ")

    def handle_data(self, data: str) -> None:
        if not self.dropped_depth:
            self.parts.append(data)


def html_text(markup: str) -> str:
    parser = TextParser()
    parser.feed(markup)
    parser.close()
    return "".join(parser.parts)


def parse_content_type(content_type: str | None) -> tuple[str | None, str | None]:
    """The lowercase media type and the charset a Content-Type value names; (None, None) for no value."""
    if not content_type:
        return None, None
    message = email.message.Message()
    message["Content-Type"] = content_type
    return message.get_content_type(), message.get_content_charset()


def decode(body: bytes, charset: str | None) -> str:
    try:
        return body.decode(charset or "utf-8", "replace")
    except LookupError:
        return body.decode("utf-8", "replace")


def body_text(body: bytes, content_type: str | None) -> str | None:
    """The text of a body, or None when its Content-Type is neither HTML nor text/*."""
    kind, charset = parse_content_type(content_type)
    textual = kind is None or kind.startswith("text/")
    if kind not in HTML_TYPES and not textual:
        return None
    text = decode(body, charset)
    if kind in HTML_TYPES or text.lstrip(" \t\r\n\f\ufeff").startswith("<"):
        return html_text(text)
    return text


class Sources:
    """Reads each cited source once per run, a URL through the cache when there is one."""

    def __init__(self, opener: urllib.request.OpenerDirector, timeout: float, cache: Cache | None) -> None:
        self.opener, self.timeout, self.cache = opener, timeout, cache
        self.readings: dict[str, Reading] = {}

    def read(self, source: str) -> Reading:
        if source not in self.readings:
            self.readings[source] = self.read_url(source) if is_web_url(source) else self.read_file(source)
        return self.readings[source]

    def read_file(self, source: str) -> Reading:
        try:
            body = Path(source).read_bytes()
        except OSError as error:
            return Reading(None, UNFETCHED, f"cannot read {source}: {error.strerror or error}")
        return reading_of(body, None)

    def read_url(self, url: str) -> Reading:
        fetched = self.cache.get(url) if self.cache else None
        if fetched is None:
            try:
                fetched = fetch(self.opener, url, self.timeout)
            except FetchError as error:
                return Reading(None, UNFETCHED, str(error), http_status=error.http_status)
            if self.cache:
                self.cache.put(url, fetched)
        return reading_of(fetched.body, fetched.content_type, http_status=fetched.http_status, final_url=fetched.final_url)


def reading_of(body: bytes, content_type: str | None, http_status: int | None = None,
               final_url: str | None = None) -> Reading:
    """The normalised text of a body, or UNREADABLE when its Content-Type is neither HTML nor text/*."""
    fields = {"content_type": content_type, "http_status": http_status, "final_url": final_url}
    text = body_text(body, content_type)
    if text is None:
        return Reading(None, UNREADABLE, f"content type {parse_content_type(content_type)[0]} is neither HTML nor text", **fields)
    return Reading(SourceText(normalise(text)), **fields)


# ---------------------------------------------------------------- matching

def find_exact(text: str, fragment: str, start: int) -> tuple[int, int] | None:
    at = text.find(fragment, start)
    return (at, at + len(fragment)) if at >= 0 else None


def find_ignoring_case(text: str, fragment: str, start: int) -> tuple[int, int] | None:
    match = re.compile(re.escape(fragment), re.IGNORECASE).search(text, start)
    return match.span() if match else None


def find_in_order(text: str, parts: tuple[str, ...],
                  find: Callable[[str, str, int], tuple[int, int] | None]) -> list[tuple[int, int]] | None:
    """The span of each fragment, each searched from the end of the previous one; None when one is missing."""
    spans: list[tuple[int, int]] = []
    cursor = 0
    for part in parts:
        span = find(text, part, cursor)
        if span is None:
            return None
        spans.append(span)
        cursor = span[1]
    return spans


def candidate_starts(words: Words, names: list[str], first: int) -> list[int]:
    """The word numbers, from `first` on, where the most words of the fragment align with the source.

    Each occurrence of a fragment word votes for the start that would put it at its place in the
    fragment. Words are taken rarest first, and a word whose occurrences would pass VOTE_BUDGET is
    left out once another has voted, so the count stays bounded on a long page.
    """
    offsets: dict[str, list[int]] = defaultdict(list)
    for number, name in enumerate(names):
        offsets[name].append(number)
    later = {}
    for name in offsets:
        positions = words.positions.get(name, [])
        later[name] = positions[bisect.bisect_left(positions, first):]
    votes: Counter[int] = Counter()
    spent = 0
    for name in sorted((name for name in offsets if later[name]), key=lambda name: len(later[name]) * len(offsets[name])):
        cost = len(later[name]) * len(offsets[name])
        if votes and spent + cost > VOTE_BUDGET:
            break
        spent += cost
        for offset in offsets[name]:
            votes.update(number - offset for number in later[name])
    return sorted({max(first, begin) for begin, _ in votes.most_common(SCORED_WINDOWS)})


def best_window(source: SourceText, fragment: str, start: int) -> Window | None:
    """The window of the source from character `start` on most similar to the fragment; None when no word of it occurs there.

    Only the candidate starts are scored, each over as many words as the fragment holds; the best
    window's start and then its end move by up to SHIFT_WORDS words where that raises the ratio.
    """
    matches = list(WORD.finditer(fragment))
    words = source.words()
    first = bisect.bisect_left(words.starts, start)
    if not matches or first >= len(words.names):
        return None
    names = [match.group().lower() for match in matches]
    begins = candidate_starts(words, names, first)
    if not begins:
        return None
    last = len(words.names) - 1
    matcher = difflib.SequenceMatcher(None, autojunk=False)
    matcher.set_seq2(fragment[matches[0].start():matches[-1].end()].lower())

    def score(begin: int, end: int) -> float:
        matcher.set_seq1(source.text[words.starts[begin]:words.ends[end]].lower())
        return matcher.ratio()

    ratio, begin, end = max((score(b, min(b + len(names) - 1, last)), b, min(b + len(names) - 1, last)) for b in begins)
    for moved in range(max(first, begin - SHIFT_WORDS), min(end, begin + SHIFT_WORDS) + 1):
        moved_ratio = score(moved, end)
        if moved_ratio > ratio:
            ratio, begin = moved_ratio, moved
    for moved in range(max(begin, end - SHIFT_WORDS), min(last, end + SHIFT_WORDS) + 1):
        moved_ratio = score(begin, moved)
        if moved_ratio > ratio:
            ratio, end = moved_ratio, moved
    return Window(ratio, words.starts[begin], words.ends[end])


def match_fragments(source: SourceText, parts: tuple[str, ...]) -> Match:
    """The status of the fragments in the source, with the spans the context shows."""
    for find, case_differs in ((find_exact, False), (find_ignoring_case, True)):
        spans = find_in_order(source.text, parts, find)
        if spans is not None:
            return Match(FOUND, case_differs, None, spans, [])
    statuses: list[str] = []
    ratios: list[float] = []
    spans, near_spans = [], []
    cursor = 0
    for part in parts:
        span = find_ignoring_case(source.text, part, cursor)
        if span is not None:
            statuses.append(FOUND)
            spans.append(span)
            cursor = span[1]
            continue
        window = best_window(source, part, cursor)
        ratios.append(window.ratio if window else 0.0)
        if window and window.ratio >= NEAR_RATIO:
            statuses.append(NEAR)
            spans.append((window.start, window.end))
            near_spans.append((window.start, window.end))
            cursor = window.end
        else:
            statuses.append(ABSENT)
    return Match(max(statuses, key=MATCH_ORDER.index), None, round(min(ratios), 3), spans, near_spans)


def context(text: str, spans: list[tuple[int, int]], chars: int) -> str:
    """The spans with `chars` characters on each side; overlapping windows merge, the rest join with ` ... `."""
    windows: list[list[int]] = []
    for start, end in sorted(spans):
        low, high = max(0, start - chars), min(len(text), end + chars)
        if windows and low <= windows[-1][1]:
            windows[-1][1] = max(windows[-1][1], high)
        else:
            windows.append([low, high])
    return " ... ".join(text[low:high] for low, high in windows)


def check_citation(citation: Citation, reading: Reading, chars: int) -> Result:
    fields = {"content_type": reading.content_type, "http_status": reading.http_status,
              "final_url": reading.final_url, "error": reading.error}
    if reading.text is None:
        return Result(citation.id, citation.source, reading.status, **fields)
    text = reading.text.text
    found = match_fragments(reading.text, citation.fragments)
    near_words = " ... ".join(text[start:end] for start, end in found.near_spans) if found.near_spans else None
    shown = context(text, found.spans, chars) if found.status in (FOUND, NEAR) else None
    return Result(citation.id, citation.source, found.status, found.case_differs, found.ratio, near_words, shown, **fields)


# ---------------------------------------------------------------- command line

def non_negative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError(f"{value} is negative")
    return number


def positive_seconds(value: str) -> float:
    seconds = float(value)
    if not (math.isfinite(seconds) and seconds > 0):
        raise argparse.ArgumentTypeError(f"{value} is not a finite number of seconds above 0")
    return seconds


def write_json(path: Path, results: list[Result]) -> None:
    try:
        path.write_text(json.dumps([dataclasses.asdict(r) for r in results], ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    except OSError as error:
        raise InputError(f"cannot write {path}: {error}") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--cache", metavar="DIR", type=Path, help="store fetched bodies here and answer from them")
    parser.add_argument("--json", metavar="OUT", type=Path, help="write the results as a JSON array to OUT")
    parser.add_argument("--context", metavar="N", type=non_negative_int, default=200,
                        help="characters of context on each side of the matched words (default 200)")
    parser.add_argument("--timeout", metavar="SECONDS", type=positive_seconds, default=30.0,
                        help="the timeout of connecting and of each read of a GET (default 30)")
    parser.add_argument("citations", metavar="CITATIONS.json", type=Path, help="the JSON array of citations")
    args = parser.parse_args(argv)
    try:
        citations = load_citations(args.citations)
        sources = Sources(http_opener(), args.timeout, Cache(args.cache) if args.cache else None)
        results = [check_citation(c, sources.read(c.source), args.context) for c in citations]
    except InputError as error:
        print(error, file=sys.stderr)
        return 2
    for result in results:
        print(result)
    missed = sum(1 for result in results if result.status != FOUND)
    print(f"{missed} of {len(results)} not found")
    if args.json:
        try:
            write_json(args.json, results)
        except InputError as error:
            print(error, file=sys.stderr)
            return 2
    return 1 if missed else 0


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
