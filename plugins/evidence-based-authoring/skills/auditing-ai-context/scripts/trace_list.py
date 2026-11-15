#!/usr/bin/env python3
"""List the sentences a change adds that may argue with the text it deleted.

    trace_list.py --old OLD --new NEW [--out LIST.json]
    trace_list.py --staged [--root DIR] [--exclude GLOB]... [--out LIST.json]
    trace_list.py --base REV [--head REV] [--root DIR] [--exclude GLOB]... [--out LIST.json]

The list holds the statements the change deleted and, as candidates, every added sentence that
carries a cue of denial, contrast or history. A candidate is a sentence to judge; the script
rules on none.

Reads the two files of pair mode, or Markdown files through `git diff` and `git show` (and from
disk in range mode without --head). Writes the list to --out, or to standard output. Uses the
Python standard library alone and opens no network connection.

Exit status: 0 the list was produced; 2 wrong usage, an unreadable file or a failed git command.
"""
import argparse
import difflib
import fnmatch
import hashlib
import json
import re
import subprocess
import sys

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
THEMATIC_BREAK = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
HTML_COMMENT = re.compile(r"^\s*<!--.*-->\s*$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
BLOCK_QUOTE = re.compile(r"^\s*>\s?")
FRONT_MATTER_KEY = re.compile(r"^[A-Za-z_-]+:")
BLOCK_SCALAR_MARK = re.compile(r"^[>|][+-]?$")
TABLE_RULE_CELL = re.compile(r"^[\s:\-]*$")
CODE_SPAN = re.compile(r"`[^`]*`")

# A stop with its closing marks, followed by whitespace; the group is the first character after it.
SENTENCE_STOP = re.compile(r"[.!?][\"'”’)*`]*(?=\s+(\S))")
SENTENCE_OPENERS = "\"'“‘([`*"
ABBREVIATION = re.compile(r"(?<![^\W\d_])(?:e\.g|i\.e|etc|vs|cf)\.$", re.I)
INITIAL = re.compile(r"(?<![^\W\d_])([^\W\d_])\.$")

DENIAL_WORDS = ("not", "no", "never", "neither", "nor", "none", "nothing", "nobody", "nowhere",
                "without", "cannot")
CONTRAST_PHRASES = ("instead", "rather than", "unlike", "as opposed to", "in place of",
                    "in contrast", "whereas")
HISTORY_PHRASES = ("no longer", "any longer", "anymore", "any more", "previously", "formerly",
                   "originally", "used to", "not yet", "so far", "for now", "currently", "legacy",
                   "deprecated", "the old", "the earlier", "the former", "the previous", "we now")
NOW_VERBS = ("uses", "use", "reads", "runs", "returns", "takes", "lives", "is", "are", "has",
             "have", "does", "do")
WORD_ENDINGS = ("s", "es", "d", "ed", "ing")


def _phrase_pattern(phrase):
    return re.compile(r"\b" + r"\s+".join(map(re.escape, phrase.split())) + r"\b", re.I)


CUE_PATTERNS = (
    [(word, _phrase_pattern(word)) for word in DENIAL_WORDS]
    + [("n't", re.compile(r"n['’]t\b", re.I))]
    + [(phrase, _phrase_pattern(phrase)) for phrase in CONTRAST_PHRASES + HISTORY_PHRASES]
    + [("now", re.compile(r"\bnow\s+(?:" + "|".join(NOW_VERBS) + r")\b", re.I))]
)


def normalise(text):
    """Text as compared everywhere: one space for a run of whitespace, plain quotes."""
    for fancy, plain in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"')):
        text = text.replace(fancy, plain)
    return " ".join(text.split())


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _front_matter(lines):
    """(index of the first body line, [(line number, text)] of the description)."""
    if not lines or lines[0].strip() != "---":
        return 0, []
    for close in range(1, len(lines)):
        if lines[close].strip() == "---":
            break
    else:
        return 0, []
    description, inside = [], False
    for index in range(1, close):
        line = lines[index]
        if FRONT_MATTER_KEY.match(line):
            inside = line.startswith("description:")
            value = line[len("description:"):].strip() if inside else ""
            if inside and value and not BLOCK_SCALAR_MARK.match(value):
                description.append((index + 1, value))
        elif inside and line.strip():
            description.append((index + 1, line.strip()))
    return close + 1, description


def _paragraphs(text):
    """Paragraphs of the prose as lists of (line number, text of that line's part)."""
    lines = text.split("\n")
    start, description = _front_matter(lines)
    if description:
        yield description
    paragraph, fence = [], None
    for index in range(start, len(lines)):
        number, line = index + 1, lines[index]
        opened = FENCE.match(line)
        if fence:
            if opened and opened.group(1) == fence:
                fence = None
            continue
        if opened:
            if paragraph:
                yield paragraph
                paragraph = []
            fence = opened.group(1)
            continue
        if not line.strip() or HEADING.match(line) or THEMATIC_BREAK.match(line) or HTML_COMMENT.match(line):
            if paragraph:
                yield paragraph
                paragraph = []
            continue
        if line.strip().startswith("|"):
            if paragraph:
                yield paragraph
                paragraph = []
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not all(TABLE_RULE_CELL.match(cell) for cell in cells):
                for cell in cells:
                    if cell:
                        yield [(number, cell)]
            continue
        line = BLOCK_QUOTE.sub("", line)
        item = LIST_ITEM.match(line)
        if item:
            if paragraph:
                yield paragraph
            paragraph = [(number, line[item.end():].strip())]
        else:
            paragraph.append((number, line.strip()))
    if paragraph:
        yield paragraph


def _ends_sentence(joined, stop):
    """Whether a SENTENCE_STOP match ends its sentence: a new one visibly starts after it and the
    stop closes neither an abbreviation nor a single capital letter."""
    following = stop.group(1)
    if not (following.isupper() or following.isdigit() or following in SENTENCE_OPENERS):
        return False
    before = joined[:stop.start() + 1]
    initial = INITIAL.search(before)
    return not ABBREVIATION.search(before) and not (initial and initial.group(1).isupper())


def _sentences(paragraph):
    """Units of one paragraph: dicts with line, end_line and text."""
    joined, line_at = "", []
    for number, part in paragraph:
        part = " ".join(part.split())
        if not part:
            continue
        if joined:
            joined += " "
            line_at.append(number)
        joined += part
        line_at.extend([number] * len(part))
    begin = 0
    cuts = [stop.end() for stop in SENTENCE_STOP.finditer(joined) if _ends_sentence(joined, stop)]
    for cut in cuts + [len(joined)]:
        chunk = joined[begin:cut]
        if chunk.strip():
            lead = len(chunk) - len(chunk.lstrip())
            yield {"line": line_at[begin + lead], "end_line": line_at[cut - 1], "text": chunk.strip()}
        begin = cut


def units(text):
    """The prose units of a Markdown text, in order."""
    return [unit for paragraph in _paragraphs(text) for unit in _sentences(paragraph)]


def cues(sentence):
    """The cues of denial, contrast and history in a sentence, each once, in order of occurrence."""
    bare = CODE_SPAN.sub(" ", sentence)
    found = sorted((match.start(), name) for name, pattern in CUE_PATTERNS
                   for match in [pattern.search(bare)] if match)
    return [name for _, name in found]


def _forms(word):
    forms = {word} | {word + ending for ending in WORD_ENDINGS}
    if word.endswith("e"):
        forms |= {word[:-1] + "ed", word[:-1] + "ing"}
    return forms


def same_word(left, right):
    """Whether two words are one word up to a plain ending."""
    left, right = left.lower(), right.lower()
    return left in _forms(right) or right in _forms(left)


def changed_lines(old_text, new_text):
    """(deleted line numbers of the old text, added line numbers of the new text), 1-based."""
    old_lines, new_lines = old_text.split("\n"), new_text.split("\n")
    deleted, added = set(), set()
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    for tag, old_from, old_to, new_from, new_to in matcher.get_opcodes():
        if tag in ("replace", "delete"):
            deleted.update(range(old_from + 1, old_to + 1))
        if tag in ("replace", "insert"):
            added.update(range(new_from + 1, new_to + 1))
    return deleted, added


def _touches(unit, numbers):
    return any(number in numbers for number in range(unit["line"], unit["end_line"] + 1))


def compare(old_name, old_text, new_name, new_text):
    """(deleted statements, candidates without ids) of one file's change."""
    deleted_lines, added_lines = changed_lines(old_text or "", new_text or "")
    deleted = [{"file": old_name, "line": unit["line"], "text": unit["text"]}
               for unit in units(old_text or "") if _touches(unit, deleted_lines)]
    candidates = []
    for unit in units(new_text or ""):
        found_cues = cues(unit["text"])
        if found_cues and _touches(unit, added_lines):
            candidates.append({"file": new_name, "line": unit["line"], "end_line": unit["end_line"],
                               "sentence": unit["text"], "cues": found_cues})
    return deleted, candidates


class UsageError(Exception):
    """Unreadable input or a failed git command; the message goes to standard error."""


def _read(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as error:
        raise UsageError(f"cannot read {path}: {error.strerror}") from error
    except UnicodeDecodeError as error:
        raise UsageError(f"cannot read {path}: not UTF-8 text") from error


def _git(root, *args):
    done = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise UsageError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def _changed_markdown(root, diff_args, excludes):
    """[(status letter, path)] of the changed Markdown files."""
    rows = []
    for line in _git(root, "diff", "--name-status", "--no-renames", *diff_args).splitlines():
        status, _, path = line.partition("\t")
        if path.endswith(".md") and not any(fnmatch.fnmatch(path, glob) for glob in excludes):
            rows.append((status[:1], path))
    return sorted(rows, key=lambda row: row[1])


def _pairs(args):
    """[(old name, old text, new name, new text or None)] of the change the arguments name."""
    if args.new is not None:
        return [(args.old, _read(args.old), args.new, _read(args.new))]
    if args.staged:
        base, diff_args = "HEAD", ["--cached"]
        new_of = lambda path: _git(args.root, "show", f":{path}")
    else:
        base, diff_args = args.base, [args.base] + ([args.head] if args.head else [])
        if args.head:
            new_of = lambda path: _git(args.root, "show", f"{args.head}:{path}")
        else:
            new_of = lambda path: _read(f"{args.root}/{path}")
    pairs = []
    for status, path in _changed_markdown(args.root, diff_args, args.exclude):
        old_text = "" if status == "A" else _git(args.root, "show", f"{base}:{path}")
        pairs.append((path, old_text, path, None if status == "D" else new_of(path)))
    return pairs


def build(args):
    files, deleted, candidates = [], [], []
    for old_name, old_text, new_name, new_text in _pairs(args):
        gone, found = compare(old_name, old_text, new_name, new_text)
        deleted += gone
        candidates += found
        if new_text is not None:
            files.append({"file": new_name, "sha256": sha256_text(new_text)})
    numbered = [{"id": f"c{number:03d}", **candidate} for number, candidate in enumerate(candidates, 1)]
    mode = "pair" if args.new is not None else "staged" if args.staged else "range"
    return {"version": 1, "mode": mode, "files": files, "deleted": deleted, "candidates": numbered}


def parse(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--old", help="pair mode: the text before the change")
    parser.add_argument("--new", help="pair mode: the text after the change")
    parser.add_argument("--staged", action="store_true", help="the index against HEAD")
    parser.add_argument("--base", help="range mode: the revision before the change")
    parser.add_argument("--head", help="range mode: the revision after it (default: the working tree)")
    parser.add_argument("--root", default=".", help="the repository directory (default: .)")
    parser.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                        help="leave out the paths that match (repeatable)")
    parser.add_argument("--out", metavar="LIST.json", help="write the list here")
    args = parser.parse_args(argv)
    modes = [args.new is not None or args.old is not None, args.staged, args.base is not None]
    if sum(modes) != 1:
        parser.error("name one change: --old with --new, or --staged, or --base")
    if (args.new is None) != (args.old is None):
        parser.error("pair mode takes both --old and --new")
    if args.head and not args.base:
        parser.error("--head goes with --base")
    return args


def main(argv=None):
    args = parse(argv)
    try:
        listing = build(args)
    except UsageError as error:
        print(f"trace_list: {error}", file=sys.stderr)
        return 2
    text = json.dumps(listing, ensure_ascii=False, indent=1) + "\n"
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as handle:
                handle.write(text)
        except OSError as error:
            print(f"trace_list: cannot write {args.out}: {error.strerror}", file=sys.stderr)
            return 2
        print(f"{len(listing['files'])} file(s), {len(listing['deleted'])} deleted statement(s), "
              f"{len(listing['candidates'])} candidate(s)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
