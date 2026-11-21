#!/usr/bin/env python3
"""Settle the reviewers' readings of a trace list into a keep or a rewrite for every candidate.

    check_trace.py --list LIST.json [--root DIR] [--min-readings N] [--json OUT.json] READING.json [READING.json ...]

LIST.json is the output of trace_list.py. A reading is one reviewer's verdicts on the whole list:
{"verdicts": [...]}, or a JSON array of such objects whose verdict lists are concatenated. A
verdict carries id, verdict (rewrite, licensed or plain) and reason, with target and quote for
licensed and question for plain; a reviewer names a target on every verdict, and the check asks
for it where it reads it. A reading keeps a candidate only by a valid licensed or plain verdict,
and a candidate is kept when every reading keeps it.

A licensed verdict is valid when its normalised quote is at least 12 characters long, occurs in
the candidate's document, has an occurrence that ends at or before the candidate sentence starts
and overlaps no candidate that is itself to be rewritten, and shares a word of four letters or
more with the target. The candidates of a document are settled in its order, so a quote taken from
an earlier candidate holds exactly when that candidate is kept. The document is the listed file
read under --root (default: the current directory) and taken as the normalised texts of its prose
units joined by single spaces.

Codes, each as a finding line `<CODE>: reading <n>: <id>: <message>`:
  MISSING    the reading has no verdict for the candidate; the outcome is rewrite
  SHAPE      a verdict outside rewrite, licensed and plain, licensed without a target, or
             plain without a question; the outcome is rewrite
  QUOTE      licensed whose quote fails one of the four conditions; the outcome is rewrite
  DUPLICATE  a second verdict for one id in a reading; the first counts
  UNKNOWN    a verdict for an id the list does not hold; it has no effect

Reads LIST.json, the readings and every file the list names, whose sha256 must still equal the
list's. Prints one line per candidate in list order, then the findings, then the summary line
`N candidates: K kept, R to rewrite; readings: M`; writes the same content as JSON to --json when
given. Uses the Python standard library alone and opens no network connection.

Exit status: 0 no candidate is to be rewritten; 1 at least one is; 2 wrong usage, unreadable
input, a document changed since the list was built, or fewer readings than --min-readings.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trace_list import normalise, same_word, sha256_text, units  # noqa: E402

VERDICTS = ("rewrite", "licensed", "plain")
CANDIDATE_KEYS = ("id", "file", "line", "sentence")
MIN_QUOTE = 12
MIN_WORD = 4
WORD = re.compile(r"[^\W\d_]+")
SHOWN = 60


class InputError(Exception):
    """Input the script cannot judge; the message goes to standard error and the exit status is 2."""


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        raise InputError(f"cannot read {path}: {error}") from error
    except ValueError as error:
        raise InputError(f"{path} is not JSON: {error}") from error


def reading_verdicts(payload, name):
    """The verdicts of one reading: an object's list, or the concatenated lists of an array of objects."""
    objects = payload if isinstance(payload, list) else [payload]
    verdicts = []
    for obj in objects:
        if not isinstance(obj, dict) or not isinstance(obj.get("verdicts"), list):
            raise InputError(f'{name} is not a reading: {{"verdicts": [...]}} or an array of such objects')
        verdicts += obj["verdicts"]
    return verdicts


def listed(listing, name):
    """({file: sha256}, [candidate]) of a trace list."""
    try:
        files = {entry["file"]: entry["sha256"] for entry in listing["files"]}
        candidates = list(listing["candidates"])
    except (KeyError, TypeError) as error:
        raise InputError(f"{name} is not a trace list: no {error}") from error
    for candidate in candidates:
        if not isinstance(candidate, dict) or not all(key in candidate for key in CANDIDATE_KEYS):
            raise InputError(f"{name} is not a trace list: a candidate without {', '.join(CANDIDATE_KEYS)}")
    ids = Counter(candidate["id"] for candidate in candidates)
    repeated = [id_ for id_, count in ids.items() if count > 1]
    if repeated:
        raise InputError(f"{name} is not a trace list: candidate id {repeated[0]} is repeated")
    for candidate in candidates:
        if candidate["file"] not in files:
            raise InputError(f"{name} is not a trace list: {candidate['id']} names {candidate['file']}, "
                             "which `files` does not list")
    return files, candidates


class Document:
    """A listed file as the quote check sees it: the normalised unit texts joined by single spaces."""

    def __init__(self, text):
        self.units, pieces, at = [], [], 0
        for unit in units(text):
            piece = normalise(unit["text"])
            self.units.append((unit["line"], piece, at, at + len(piece)))
            pieces.append(piece)
            at += len(piece) + 1
        self.text = " ".join(pieces)

    def span(self, candidate):
        """(start, end) of the candidate sentence in the joined text, or None when it is no unit here."""
        sentence = normalise(candidate["sentence"])
        for line, piece, start, end in self.units:
            if line == candidate["line"] and piece == sentence:
                return start, end
        return None


def load_document(root, name, sha256):
    path = Path(root) / name
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise InputError(f"cannot read {path}: {error}") from error
    if sha256_text(text) != sha256:
        raise InputError(f"{name}: the document changed since the list was built")
    return Document(text)


def occurrences(text, part):
    found, at = [], text.find(part)
    while at != -1:
        found.append(at)
        at = text.find(part, at + 1)
    return found


def long_words(text):
    return [word for word in WORD.findall(text) if len(word) >= MIN_WORD]


def shares_word(quote, target):
    return any(same_word(mine, other) for mine in long_words(quote) for other in long_words(target))


def quote_refusal(verdict, candidate, document, spans, rewritten):
    """The condition a licensed verdict fails, as a message, or None when its quote licenses the candidate.

    spans maps the id of every candidate of the document to its (start, end) in the joined text;
    rewritten holds the ids of the candidates before this one that are to be rewritten.
    """
    quote = verdict.get("quote")
    quote = normalise(quote) if isinstance(quote, str) else ""
    if len(quote) < MIN_QUOTE:
        return f"the quote is shorter than {MIN_QUOTE} characters"
    starts = occurrences(document.text, quote)
    if not starts:
        return f"the quote does not occur in {candidate['file']}"
    begin = spans[candidate["id"]][0]
    before = [start for start in starts if start + len(quote) <= begin]
    if not before:
        return "every occurrence of the quote ends after the candidate sentence starts"
    overlapped = [[id_ for id_ in rewritten if start < spans[id_][1] and spans[id_][0] < start + len(quote)]
                  for start in before]
    if all(overlapped):
        inside = sorted({id_ for ids in overlapped for id_ in ids})
        return ("every occurrence of the quote before the candidate lies in a candidate to rewrite: "
                + ", ".join(inside))
    if not shares_word(quote, verdict["target"]):
        return f"the quote shares no word of {MIN_WORD} letters or more with the target"
    return None


def settle(verdict, candidate, document, spans, rewritten):
    """(outcome, code, message) of one verdict on its candidate; the code is empty when nothing is refused."""
    kind = verdict.get("verdict")
    if kind not in VERDICTS:
        return "rewrite", "SHAPE", f"verdict {kind!r} is outside {', '.join(VERDICTS)}"
    if kind == "rewrite":
        return "rewrite", "", ""
    if kind == "plain":
        question = verdict.get("question")
        if not isinstance(question, str) or not question.strip():
            return "rewrite", "SHAPE", "plain without a question"
        return "keep", "", ""
    target = verdict.get("target")
    if not isinstance(target, str) or not target.strip():
        return "rewrite", "SHAPE", "licensed without a target"
    refusal = quote_refusal(verdict, candidate, document, spans, rewritten)
    return ("rewrite", "QUOTE", refusal) if refusal else ("keep", "", "")


def finding(code, reading, id_, message):
    return {"code": code, "reading": reading, "id": id_, "message": message}


def check(listing, readings, root, name="the list"):
    """The result object of the verdicts of every reading on the list's candidates.

    readings holds one list of verdicts per reading, in reading order. Raises InputError on a list
    that is not a trace list or a document that is unreadable or changed since the list was built.
    """
    files, candidates = listed(listing, name)
    documents = {file: load_document(root, file, sha) for file, sha in files.items()}
    spans = {file: {} for file in files}
    for candidate in candidates:
        span = documents[candidate["file"]].span(candidate)
        if span is None:
            raise InputError(f"{candidate['id']} is not a sentence of {candidate['file']} at line {candidate['line']}")
        spans[candidate["file"]][candidate["id"]] = span

    order = {candidate["id"]: index for index, candidate in enumerate(candidates)}
    outcomes = {candidate["id"]: [] for candidate in candidates}
    quotes = {candidate["id"]: [] for candidate in candidates}
    scanned, firsts = [], []
    for reading, verdicts in enumerate(readings, 1):
        first, found = {}, []
        for verdict in verdicts:
            id_ = verdict.get("id") if isinstance(verdict, dict) else None
            if not isinstance(id_, str):
                found.append(finding("SHAPE", reading, "", "a verdict that is not an object with an id"))
            elif id_ not in outcomes:
                found.append(finding("UNKNOWN", reading, id_, "the list holds no candidate with this id"))
            elif id_ in first:
                found.append(finding("DUPLICATE", reading, id_, "a second verdict for the id; the first counts"))
            else:
                first[id_] = verdict
        scanned.append(found)
        firsts.append(first)

    # A quote from an earlier candidate holds only when that candidate is kept, so each document's
    # candidates are settled over all readings in the order they stand in it.
    refused = [[] for _ in readings]
    rewritten = {file: set() for file in files}
    for candidate in sorted(candidates, key=lambda c: (c["file"], spans[c["file"]][c["id"]][0])):
        id_, file = candidate["id"], candidate["file"]
        for reading, first in enumerate(firsts, 1):
            verdict = first.get(id_)
            if verdict is None:
                outcome, code, message, given = "rewrite", "MISSING", "no verdict for the candidate", ""
            else:
                outcome, code, message = settle(verdict, candidate, documents[file], spans[file], rewritten[file])
                given = verdict.get("verdict") if isinstance(verdict.get("verdict"), str) else ""
                if outcome == "keep" and given == "licensed":
                    quotes[id_].append(normalise(verdict["quote"]))
            outcomes[id_].append({"reading": reading, "verdict": given, "outcome": outcome, "code": code})
            if code:
                refused[reading - 1].append(finding(code, reading, id_, message))
        if any(outcome["outcome"] != "keep" for outcome in outcomes[id_]):
            rewritten[file].add(id_)
    findings = [item for found, late in zip(scanned, refused)
                for item in found + sorted(late, key=lambda item: order[item["id"]])]

    entries = []
    for candidate in candidates:
        id_ = candidate["id"]
        kept = all(outcome["outcome"] == "keep" for outcome in outcomes[id_])
        entries.append({"id": id_, "file": candidate["file"], "line": candidate["line"],
                        "sentence": candidate["sentence"], "disposition": "keep" if kept else "rewrite",
                        "outcomes": outcomes[id_], "quotes": list(dict.fromkeys(quotes[id_])) if kept else []})
    return {"readings": len(readings), "candidates": entries, "findings": findings}


def shorten(sentence):
    if len(sentence) <= SHOWN:
        return sentence
    cut = sentence[:SHOWN].rsplit(" ", 1)[0]
    return f"{cut} …"


def candidate_line(entry):
    head = f"{entry['file']}:{entry['line']}: {entry['disposition'].upper()} {entry['id']}"
    if entry["disposition"] == "keep":
        tally = Counter(outcome["verdict"] for outcome in entry["outcomes"])
        kept = ", ".join(f"{verdict} ×{count}" for verdict, count in tally.items())
        quotes = "".join(f' quote: "{quote}"' for quote in entry["quotes"])
        return f"{head} [{kept}]{quotes}"
    marks = "; ".join(f"reading {o['reading']}: {o['code'] or o['verdict']}" for o in entry["outcomes"])
    return f"{head} [{marks}] {shorten(entry['sentence'])}"


def render(result):
    """The lines of standard output: the candidates, the findings, the summary."""
    lines = [candidate_line(entry) for entry in result["candidates"]]
    lines += [f"{item['code']}: reading {item['reading']}: {item['id']}: {item['message']}"
              for item in result["findings"]]
    kept = sum(entry["disposition"] == "keep" for entry in result["candidates"])
    total = len(result["candidates"])
    lines.append(f"{total} candidates: {kept} kept, {total - kept} to rewrite; readings: {result['readings']}")
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--list", required=True, metavar="LIST.json", help="the output of trace_list.py")
    parser.add_argument("--root", default=".", metavar="DIR", help="the directory the list's files are read under (default: .)")
    parser.add_argument("--min-readings", type=int, default=1, metavar="N",
                        help="the fewest reading files accepted (default: 1)")
    parser.add_argument("--json", metavar="OUT.json", help="write the result here as JSON")
    parser.add_argument("readings", nargs="*", metavar="READING.json", help="one reviewer's verdicts")
    args = parser.parse_args(argv)
    if len(args.readings) < args.min_readings:
        print(f"check_trace: {len(args.readings)} reading(s) given, --min-readings asks for {args.min_readings}",
              file=sys.stderr)
        return 2
    try:
        listing = read_json(args.list)
        readings = [reading_verdicts(read_json(path), path) for path in args.readings]
        result = check(listing, readings, args.root, args.list)
    except InputError as error:
        print(f"check_trace: {error}", file=sys.stderr)
        return 2
    if args.json:
        try:
            Path(args.json).write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        except OSError as error:
            print(f"check_trace: cannot write {args.json}: {error}", file=sys.stderr)
            return 2
    print("\n".join(render(result)))
    return 1 if any(entry["disposition"] == "rewrite" for entry in result["candidates"]) else 0


def utf8_streams():
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
