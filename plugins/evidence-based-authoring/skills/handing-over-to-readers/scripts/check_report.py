#!/usr/bin/env python3
"""Check a report or a question list against the reading contract.

    check_report.py [--profile operator|client] [--root DIR] [--json] [--strict] [--lexicon FILE] FILE|-

Profile `operator` (default): a report to the operator of the session, who opens files and runs
commands himself. The report is a story in plain words closed by the list "Where to look".
Errors: no "Where to look" heading; a code span or an exit code in the story above that heading;
a `path:line` anchor whose file or line does not exist under --root, or whose fragment (the next
code span on the same line) is not on that line; a run, workflow or agent identifier in the text.
Warnings: an opening paragraph of fewer than three sentences; a story sentence of more than twenty
words; a story sentence with three or more numbers; a self-report in the story while no exit code
stands under "Where to look"; more than five lines under "Where to look"; more than 300 words of
prose outside fences and tables; an anchor without a fragment, or one whose fragment stands within
two lines of the anchor instead of on it.

Profile `client`: the list reaches an addressee who opens nothing of ours. Errors: a file path,
a section reference, a date or deadline, an effort estimate, a contract reference, an identifier
or hash; a list item without its one question mark at the end. Warnings: a sentence with three or
more numbers, two items on one topic. A section whose heading names the internal block is exempt.

Warnings exit 0 unless --strict. The headings and words the checks match are English. A lexicon
adds those of another language: `--lexicon FILE`, or the file
`$XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json` when it exists — a JSON object with one
section per script, each from a key of its WORDS to extra regex alternatives:
{"check_report": {"WHERE_TO_LOOK": ["Evidence"]}, "check_question": {...}}.

Output: one line per finding, `FILE:LINE: LEVEL CODE: message`, or a JSON array with --json.
Exit: 0 no error; 1 at least one error (or a warning under --strict); 2 unreadable input or
lexicon.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ERROR = "error"
WARNING = "warning"

FENCE = re.compile(r"^\s*(?:```|~~~)")
HEADING = re.compile(r"^#{1,6}\s+(.*)")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
TABLE_ROW = re.compile(r"^\s*\|")
CODE_SPAN = re.compile(r"`([^`]+)`")
ANCHOR = re.compile(r"^(?P<path>[^\s`:*?\"<>|]+?):(?P<line>\d+)(?:-(?P<end>\d+))?$")
NUMBER = re.compile(r"(?<![\w.,])\d+(?:[.,]\d+)?(?![\w])")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")

MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")
WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
WORDS: dict[str, list[str]] = {
    "WHERE_TO_LOOK": ["where to look"],
    "SECTION_INTERNAL": ["internal"],
    "EXIT_CODE": [r"exit\s*(?:code|\d)"],
    "SELF_REPORT": [r"tests? (?:pass|passed|passes|are green)", "works as expected", "ready to merge"],
    "SECTION_REF": ["section", r"sec\.", "chapter", "§"],
    "MONTHS": list(MONTHS),
    "DEADLINE_LEAD": ["by", "until", "deadline"],
    "DEADLINE_TARGET": [*WEEKDAYS, "end of", "next (?:week|month|quarter|sprint|release)"],
    "EFFORT_UNITS": ["h", "hrs?", "hours?", "man-days?", "person-days?", "days?", "weeks?"],
    "EFFORT_TAIL": ["of work"],
    "AS_AGREED": ["as agreed", "per the contract", "as discussed"],
}
LEXICON_FILE = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "handing-over-to-readers" / "lexicon.json"


LEXICON_SECTIONS = ("check_report", "check_question")
LEXICON_SECTION = "check_report"


def read_lexicon(path: Path, required: bool) -> dict[str, list[str]]:
    """This script's section of a lexicon file: extra alternatives per key of WORDS; a missing optional file is empty."""
    if not required and not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"{path}: {e}") from e
    if not isinstance(data, dict) or not set(data) <= set(LEXICON_SECTIONS):
        raise ValueError(f"{path}: expected an object with the sections {' and '.join(LEXICON_SECTIONS)}")
    section = data.get(LEXICON_SECTION, {})
    if not isinstance(section, dict) or not all(
        isinstance(k, str) and isinstance(v, list) and all(isinstance(s, str) for s in v) for k, v in section.items()
    ):
        raise ValueError(f"{path}: {LEXICON_SECTION} must map a key to a list of strings")
    unknown = sorted(set(section) - set(WORDS))
    if unknown:
        raise ValueError(f"{path}: unknown keys {', '.join(unknown)} in {LEXICON_SECTION}; known: {', '.join(WORDS)}")
    return section


def build_patterns(extra: dict[str, list[str]] | None = None) -> None:
    """Compile the language-bound patterns from WORDS plus the lexicon's alternatives.

    The patterns are module globals rebuilt in place, so a caller that imported one by name keeps
    the English pattern; read it from the module after apply_lexicon.
    """
    global LOOK_HEADING, SECTION_INTERNAL, EXIT_CODE, SELF_REPORT
    global CLIENT_SECTION_REF, CLIENT_DATE, CLIENT_DEADLINE, CLIENT_EFFORT, CLIENT_AS_AGREED
    words = {k: v + (extra or {}).get(k, []) for k, v in WORDS.items()}

    def alt(key: str) -> str:
        return "|".join(words[key])

    try:
        LOOK_HEADING = re.compile(rf"^\s*(?:#{{1,6}}\s+)?\**(?:{alt('WHERE_TO_LOOK')})\**:?\s*$", re.IGNORECASE)
        SECTION_INTERNAL = re.compile(rf"\b(?:{alt('SECTION_INTERNAL')})", re.IGNORECASE)
        EXIT_CODE = re.compile(alt("EXIT_CODE"), re.IGNORECASE)
        SELF_REPORT = re.compile(f"({alt('SELF_REPORT')})", re.IGNORECASE)
        CLIENT_SECTION_REF = re.compile(rf"(?:{alt('SECTION_REF')})\s*\d", re.IGNORECASE)
        CLIENT_DATE = re.compile(
            rf"\b\d{{1,2}}[./]\d{{1,2}}[./]\d{{2,4}}\b|\b\d{{4}}-\d{{2}}-\d{{2}}\b|\b\d{{1,2}}\s+(?:{alt('MONTHS')})\w*", re.IGNORECASE
        )
        CLIENT_DEADLINE = re.compile(rf"\b(?:{alt('DEADLINE_LEAD')})\s+(?:{alt('DEADLINE_TARGET')})\w*", re.IGNORECASE)
        CLIENT_EFFORT = re.compile(
            rf"\b\d+(?:[.,]\d+)?\s*(?:{alt('EFFORT_UNITS')})\b(?:\s+(?:{alt('EFFORT_TAIL')}))?", re.IGNORECASE
        )
        CLIENT_AS_AGREED = re.compile(rf"(?:{alt('AS_AGREED')})", re.IGNORECASE)
    except re.error as e:
        raise ValueError(f"lexicon alternative is not a valid regex: {e}") from e


def apply_lexicon(path: str | None) -> None:
    """Rebuild the patterns with the named lexicon, or with the default file when it exists."""
    build_patterns(read_lexicon(Path(path) if path else LEXICON_FILE, required=bool(path)))


build_patterns()

ID_PATTERNS = {
    "uuid": re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE),
    "workflow id": re.compile(r"\bwf_[a-z0-9-]{6,}\b"),
    "agent id": re.compile(r"\ba[0-9a-f]{16}\b"),
    "tool-use id": re.compile(r"\btoolu_[A-Za-z0-9]{8,}\b"),
}
CLIENT_HASH = re.compile(r"\b[0-9a-f]{7,40}\b")
CLIENT_PATH = re.compile(r"(?<![\w/])(?:[\w.-]+/)+[\w.-]+|\b[\w-]+\.(?:md|py|java|kt|ts|js|json|ya?ml|toml|xml|sh|sql|csv|gradle)\b")
QUESTION_TAIL = re.compile(r"[\s*)»\"'\]_]+$")

REPORT_WORDS = 300  # prose outside fences and tables; a house limit
LOOK_LINES = 5  # lines under "Where to look"; a house limit
STORY_OPENING_SENTENCES = 3  # the task, how it ended, the problem with its cause and what is needed take at least three
STORY_SENTENCE_WORDS = 20  # headroom over 16, the longest sentence of a narration read as clear; the written story of the same case, read as tangled, reaches 40


@dataclass(frozen=True)
class Finding:
    line: int
    level: str
    code: str
    message: str


@dataclass
class Item:
    line: int
    text: str
    section: str


def strip_code(text: str) -> str:
    return CODE_SPAN.sub(" ", text)


def section_kind(title: str) -> str:
    return "internal" if SECTION_INTERNAL.search(title) else "other"


def prose_lines(lines: list[str]):
    """Yield (index, line, section kind) outside fenced blocks."""
    fenced = False
    section = "other"
    for i, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        heading = HEADING.match(line)
        if heading:
            section = section_kind(heading.group(1))
            continue
        yield i, line, section


def list_items(lines: list[str]) -> list[Item]:
    """List items with their continuation lines joined, outside fenced blocks."""
    items: list[Item] = []
    current: Item | None = None
    for i, line, section in prose_lines(lines):
        if LIST_ITEM.match(line):
            current = Item(i + 1, LIST_ITEM.sub("", line).strip(), section)
            items.append(current)
        elif current is not None and line.strip() and line.startswith((" ", "\t")):
            current.text += " " + line.strip()
        else:
            current = None
    return items


def has_three_numbers(text: str) -> bool:
    return any(len(NUMBER.findall(sentence)) >= 3 for sentence in SENTENCE_END.split(text))


def opening_sentences(lines: list[str]) -> int:
    """Sentences of the first paragraph; a report that opens on a heading, a list, a table or a fence has none."""
    opening: list[str] = []
    for line in lines:
        if not line.strip():
            if opening:
                break
            continue
        if FENCE.match(line) or HEADING.match(line) or LIST_ITEM.match(line) or TABLE_ROW.match(line):
            break
        opening.append(line.strip())
    return len([part for part in SENTENCE_END.split(" ".join(opening)) if part])


def check_story(lines: list[str]) -> list[Finding]:
    """The story above "Where to look" in plain words, the list itself short and carrying the checks."""
    findings: list[Finding] = []
    fenced = False
    look_at: int | None = None
    look_lines = 0
    look_has_exit_code = False
    self_reports: list[int] = []
    for i, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        if fenced or not line.strip():
            continue
        if look_at is None and LOOK_HEADING.match(line):
            look_at = i
            continue
        if look_at is not None:
            look_lines += bool(LIST_ITEM.match(line))
            look_has_exit_code = look_has_exit_code or bool(EXIT_CODE.search(line))
            continue
        if TABLE_ROW.match(line):
            continue
        if CODE_SPAN.search(line) or EXIT_CODE.search(line):
            findings.append(Finding(i + 1, ERROR, "STORY-CODE", "a code span or an exit code inside the story: name the thing by its role, the anchor goes under Where to look"))
        if HEADING.match(line):
            continue
        if not LIST_ITEM.match(line):
            longest = max((len(sentence.split()) for sentence in SENTENCE_END.split(line.strip())), default=0)
            if longest > STORY_SENTENCE_WORDS:
                findings.append(Finding(i + 1, WARNING, "STORY-SENTENCE", f"a sentence of {longest} words in the story, past {STORY_SENTENCE_WORDS}: one claim per sentence, the way it is said aloud"))
        if has_three_numbers(line):
            findings.append(Finding(i + 1, WARNING, "NUMBERS", "three or more numbers in one sentence: one number per claim, the rest in a picture or a table (rule 17)"))
        if SELF_REPORT.search(line):
            self_reports.append(i)
    if not look_has_exit_code:
        for i in self_reports:
            findings.append(Finding(i + 1, WARNING, "SELF-REPORT", "self-report while no check with its exit code stands under Where to look: not evidence"))
    sentences = opening_sentences(lines)
    if sentences < STORY_OPENING_SENTENCES:
        findings.append(Finding(1, WARNING, "OPENING-SHORT", f"the opening paragraph has {sentences} sentence(s): give the task, how it ended, the problem with its cause and what is needed from the reader"))
    if look_at is None:
        findings.append(Finding(1, ERROR, "WHERE-TO-LOOK", "no Where to look list: the story's claims need their anchors and checks"))
    elif look_lines > LOOK_LINES:
        findings.append(Finding(look_at + 1, WARNING, "WHERE-TO-LOOK", f"{look_lines} lines under Where to look, past {LOOK_LINES}: keep the places the story turns on"))
    return findings


def check_length(lines: list[str]) -> list[Finding]:
    """The report's prose, outside fenced blocks and tables, stays within one screen."""
    words = sum(len(line.split()) for _, line, _ in prose_lines(lines) if not TABLE_ROW.match(line))
    if words > REPORT_WORDS:
        return [Finding(1, WARNING, "LENGTH", f"{words} words of prose, past {REPORT_WORDS}: cut what answers no question of the reader")]
    return []


def check_anchors(lines: list[str], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for i, line, _ in prose_lines(lines):
        spans = [(m.start(), m.group(1)) for m in CODE_SPAN.finditer(line)]
        for k, (_, span) in enumerate(spans):
            a = ANCHOR.match(span)
            if not a or ("/" not in a.group("path") and "." not in a.group("path")):
                continue
            path = Path(a.group("path"))
            target = path if path.is_absolute() else root / path
            lineno = int(a.group("line"))
            if not target.is_file():
                findings.append(Finding(i + 1, ERROR, "ANCHOR", f"`{span}`: file not found under {root}"))
                continue
            try:
                target_lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError as e:
                findings.append(Finding(i + 1, ERROR, "ANCHOR", f"`{span}`: {e}"))
                continue
            if lineno < 1 or lineno > len(target_lines):
                findings.append(Finding(i + 1, ERROR, "ANCHOR", f"`{span}`: line out of range (file has {len(target_lines)} lines)"))
                continue
            fragment = spans[k + 1][1] if k + 1 < len(spans) and not ANCHOR.match(spans[k + 1][1]) else None
            if fragment is None:
                findings.append(Finding(i + 1, WARNING, "ANCHOR-FRAGMENT", f"`{span}`: no fragment beside the anchor, only the address is checkable"))
                continue
            needle = fragment.strip()
            if needle in target_lines[lineno - 1]:
                continue
            window = target_lines[max(0, lineno - 3): lineno + 2]
            if any(needle in w for w in window):
                findings.append(Finding(i + 1, WARNING, "ANCHOR-FRAGMENT", f"`{span}`: fragment found within two lines of the anchor, not on it"))
            else:
                findings.append(Finding(i + 1, ERROR, "ANCHOR-FRAGMENT", f"`{span}`: fragment `{needle}` is not on that line"))
    return findings


def check_questions(items: list[Item]) -> list[Finding]:
    findings: list[Finding] = []
    for item in items:
        if item.section == "internal":
            continue
        text = strip_code(item.text)
        marks = text.count("?")
        body = QUESTION_TAIL.sub("", text)
        if marks == 0:
            findings.append(Finding(item.line, ERROR, "QUESTION", "item without a question: a message goes to the registry or is dropped (rule 19)"))
        elif marks > 1:
            findings.append(Finding(item.line, ERROR, "QUESTION", f"item with {marks} questions; one topic, one question (rules 8, 19)"))
        elif not body.endswith("?"):
            findings.append(Finding(item.line, ERROR, "QUESTION", "the question is not the last sentence of the item (rule 19)"))
    return findings


def check_duplicates(items: list[Item]) -> list[Finding]:
    findings: list[Finding] = []
    scoped = [it for it in items if it.section != "internal"]

    def tokens(text: str) -> set[str]:
        return {w for w in re.findall(r"[^\W\d_]{4,}", strip_code(text).lower())}

    bags = [(it, tokens(it.text)) for it in scoped]
    for x in range(len(bags)):
        for y in range(x + 1, len(bags)):
            a, b = bags[x][1], bags[y][1]
            if not a or not b:
                continue
            jaccard = len(a & b) / len(a | b)
            if jaccard >= 0.5:
                findings.append(Finding(bags[y][0].line, WARNING, "DUPLICATE", f"shares {jaccard:.0%} of its words with the item at line {bags[x][0].line}: one topic lives in one item (rule 8)"))
    return findings


def check_identifiers(lines: list[str], profile: str) -> list[Finding]:
    findings: list[Finding] = []
    for i, line, _ in prose_lines(lines):
        for name, pattern in ID_PATTERNS.items():
            if pattern.search(line):
                findings.append(Finding(i + 1, ERROR, "IDENTIFIER", f"{name} in the text (rule 14)"))
        if profile == "client" and CLIENT_HASH.search(strip_code(line)):
            findings.append(Finding(i + 1, ERROR, "IDENTIFIER", "hash or identifier in a client text (rule 14)"))
    return findings


def check_client_prose(lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    checks = (
        ("PATH", CLIENT_PATH, "file path in a client text (rule 14)"),
        ("SECTION-REF", CLIENT_SECTION_REF, "reference to a document section (rule 14)"),
        ("DATE", CLIENT_DATE, "date in a client text (rule 15)"),
        ("DEADLINE", CLIENT_DEADLINE, "deadline in a client text: name the dependency in words (rule 15)"),
        ("EFFORT", CLIENT_EFFORT, "effort or duration estimate (rules 15, 16)"),
        ("AS-AGREED", CLIENT_AS_AGREED, "reference to the contract or a past agreement (rule 14)"),
    )
    for i, line, section in prose_lines(lines):
        if section == "internal":
            continue
        for code, pattern, message in checks:
            if pattern.search(line):
                findings.append(Finding(i + 1, ERROR, code, message))
    return findings


def check_client_numbers(lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for i, line, section in prose_lines(lines):
        if section == "internal" or TABLE_ROW.match(line) or not line.strip():
            continue
        if has_three_numbers(strip_code(line)):
            findings.append(Finding(i + 1, WARNING, "NUMBERS", "three or more numbers in one sentence: one number per claim, the rest in a table (rule 17)"))
    return findings


def check(text: str, profile: str = "operator", root: Path | str = ".") -> list[Finding]:
    lines = text.splitlines()
    findings = check_identifiers(lines, profile)
    if profile == "operator":
        findings += check_story(lines)
        findings += check_anchors(lines, Path(root))
        findings += check_length(lines)
    else:
        items = list_items(lines)
        findings += check_client_prose(lines)
        findings += check_questions(items)
        findings += check_duplicates(items)
        findings += check_client_numbers(lines)
    return sorted(findings, key=lambda f: (f.line, f.level != ERROR, f.code))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("file", help="markdown file, or - for stdin")
    parser.add_argument("--profile", choices=("operator", "client"), default="operator")
    parser.add_argument("--root", default=".", help="directory anchors resolve against")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true", help="a warning fails the check too")
    parser.add_argument("--lexicon", help=f"lexicon JSON, section {LEXICON_SECTION}: extra alternatives per key of WORDS; default: {LEXICON_FILE} when it exists")
    args = parser.parse_args(argv)
    try:
        apply_lexicon(args.lexicon)
    except ValueError as e:
        print(f"cannot read the lexicon: {e}", file=sys.stderr)
        return 2
    try:
        text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except OSError as e:
        print(f"cannot read {args.file}: {e}", file=sys.stderr)
        return 2
    findings = check(text, args.profile, args.root)
    name = args.file
    if args.json:
        print(json.dumps([asdict(f) for f in findings], ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(f"{name}:{f.line}: {f.level} {f.code}: {f.message}")
        errors = sum(1 for f in findings if f.level == ERROR)
        print(f"{errors} error(s), {len(findings) - errors} warning(s)")
    failed = any(f.level == ERROR or (args.strict and f.level == WARNING) for f in findings)
    return 1 if failed else 0


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
