#!/usr/bin/env python3
"""Carry the records, texts and hypotheses of workers' result files into a provenance map and its list of hypotheses.

    apply_records.py --map MAP.md --hypotheses LIST.md [--replace] [--corrections OUT.md] [--dry-run] RESULT.json [RESULT.json ...]

The script is the one writer of the map and the list, so a batch can be applied, checked and
applied again: a second run of the same results with the same options changes nothing.

Input. RESULT.json is a UTF-8 JSON object {"rules": [...], "unopened": [...]}. `unopened` is an
array of strings, each a source the worker could not open and why. Each rule is an object of
  id           a non-empty string with no `*`, no line break and no white space at either end;
               an id stands once in the result files of one run
  record       a string: the record that closes the rule's line in MAP.md
  text         a string: what stands on the rule's line in MAP.md between the closing `**` of its
               id and the ` · ` that opens its record, or the end of the line when the line
               carries no record, as it shall stand; read under --replace alone
  hypotheses   an array of strings: the hypothesis lines the record rests on
  sources      an array of objects with the strings `source` and `seen`: what the worker opened
               and how it saw it
  corrections  an array of objects with the strings `where`, `says` and `source_says`: where our
               text says what, and what the source says
  notes        a string: what a maintainer has to know beside the record, empty when nothing
A rule carries record, text or both, and every other key of the list. Other keys are not read; an
object that repeats a name is malformed. MAP.md and LIST.md are UTF-8 Markdown files. A rule line
opens `- **<id>**` (references/record-format.md § Lines and files); it carries a record when a
segment after one of its ` · ` separators opens `kind:`, as scripts/check_record.py reads a
record, and the record runs from the first such segment to the end of the line. A line break is
any character str.splitlines breaks at.

Applying. The rules are taken in the order of the result files and of their rules, and each is
applied whole or not at all. Its outcome in MAP.md:
  MISSING   no rule line of MAP.md has its id; its hypothesis lines are not read
  BAD       two or more rule lines have its id, and its hypothesis lines are not read; or its line
            carries no record and its record does not open with `kind: `, holds a line break, or
            comes with a BAD hypothesis line
  KEPT      its line already carries a record and stays as it is, or the rule carries no record
  RECORDED  its line gets ` · ` and the record appended
Then, for a rule whose id stands on one rule line, the outcome of each of its hypothesis lines in
LIST.md, the line's id being the text between its opening `- **` and the next `**`:
  BAD       the line does not open `- **<id>** · ` or holds a line break; a line with no id is
            named by the rule's id
  KEPT      a rule line of LIST.md, or a line this run appends before it, has its id
  ADDED     the line is appended at the end of LIST.md, after one blank line when the file does
            not end with one

--replace makes the results the authority for the lines they name. A rule's outcome in MAP.md is
MISSING, or BAD for an id on two or more rule lines, as above; otherwise its record's outcome is
  BAD       its record does not open with `kind: ` or holds a line break, or the line would take
            the record and the rule comes with a BAD text or hypothesis line
  KEPT      the rule carries no record, or the record in place equals the rule's
  REPLACED  the record in place gives way to the rule's
  RECORDED  the line carries no record and gets ` · ` and the rule's record appended
and, printed after it, the outcome of the rule's text:
  BAD       the text holds a line break or a segment that opens `kind:`
  REWORDED  the text differs from the text in place, which gives way to it
A text equal to the text in place gets no outcome. A line that, rewritten, would not read back
with the text and the record it was given (a text ending in ` ·` swallows the separator of the
record after it) is BAD for the text, or for the record when the rule carries no text. A
hypothesis line is BAD as
above, or when its id stands on two or more rule lines of LIST.md, or when it differs from the
line this run already writes for its id; KEPT when the line of its id, as the run leaves it so
far, equals it; REPLACED when the one rule line of LIST.md with its id differs and gives way to
it; and ADDED as above.

A rule with a BAD outcome writes nothing to either file; its text and its hypothesis lines get no
outcome but a BAD one. Every other byte of the two files stays as it was; a replaced line keeps
its line ending, and an appended line ends as the first line of LIST.md does, with CR LF or with
LF.

--corrections OUT.md writes a Markdown report. Each rule with a correction or a non-empty note
gets a heading `## <id>`, in the order of its rule line in MAP.md and, for ids MAP.md lacks,
after those in the order of the results; under it one bullet per correction with where, what
our text says and what the source says, then the note, then the sources with how each was seen.
The closing section `## Unopened sources` lists each unopened source of the result files once.

--dry-run prints the same outcomes and writes nothing.

Writing. The corrections report is written on every run without --dry-run, then LIST.md and then
MAP.md, each only when its text changed, so a recorded line never names a hypothesis that a failed
write kept out of LIST.md. Each file is written to a temporary file in its own directory, given
the mode of the file it replaces, and renamed over it.

Output on stdout: one line per outcome, `<CODE> <id>`, the outcomes in MAP.md first, a rule's
text after its record, and those in LIST.md after them, each in the order of the results; then
the line `<n> recorded, <n> replaced, <n> reworded, <n> kept, <n> added, <n> missing, <n> bad`.
Each MISSING and BAD outcome also prints its reason and its result file on stderr.

Exit: 0 no MISSING and no BAD outcome; 1 at least one; 2 wrong usage (MAP.md and LIST.md one
file, or OUT.md one of the input files), an unreadable or non-UTF-8 result file, MAP.md or
LIST.md, a malformed result file (a rule with neither record nor text among them), a rule id in
two result files or twice in one, or a file that cannot be written, with the message on stderr.
Every exit 2 but a failed write comes before any write; a failed write names the files already
written, and a second run completes the rest.

Privileges: reads the result files, MAP.md and LIST.md; writes MAP.md, LIST.md, the corrections
report and their temporary files; opens no network connection and runs no other program.
Standard library alone; runs under `python3 -I`.
"""
from __future__ import annotations

import argparse
import contextlib
import enum
import json
import os
import re
import stat
import sys
import tempfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

RECORDED, REPLACED, REWORDED, KEPT, ADDED, MISSING, BAD = (
    "RECORDED", "REPLACED", "REWORDED", "KEPT", "ADDED", "MISSING", "BAD")
CODES = (RECORDED, REPLACED, REWORDED, KEPT, ADDED, MISSING, BAD)

RULE_LINE = re.compile(r"- \*\*(?P<id>[^*]+)\*\*")
HYPOTHESIS_LINE = re.compile(r"- \*\*(?P<id>[^*]+)\*\* · ")
SEPARATOR = " · "
RECORD_KEY = "kind:"
RECORD_OPENING = "kind: "
# The characters str.splitlines breaks a line at.
LINE_BREAK = re.compile(r"[\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029]")


class Mode(enum.Enum):
    """What a rule does to a line that already carries a record, a text or a hypothesis of its id."""
    FILL = "fill"        # it leaves the line as it stands and reads no text
    REPLACE = "replace"  # its record, text and hypothesis lines take the place of those in the files


class InputError(Exception):
    """The run cannot go on: an unreadable or malformed input, or a file that cannot be written."""


class RepeatedName(ValueError):
    """A JSON object of a result file names one key twice."""


@dataclass(frozen=True)
class Source:
    source: str
    seen: str


@dataclass(frozen=True)
class Correction:
    where: str
    says: str
    source_says: str


@dataclass(frozen=True)
class Rule:
    id: str
    record: str | None  # None for a rule that carries text alone
    text: str | None    # None for a rule that leaves its line's text as it stands
    hypotheses: tuple[str, ...]
    sources: tuple[Source, ...]
    corrections: tuple[Correction, ...]
    notes: str
    origin: Path  # the result file that holds the rule


@dataclass(frozen=True)
class Results:
    rules: tuple[Rule, ...]
    unopened: tuple[str, ...]


@dataclass(frozen=True)
class Outcome:
    """One outcome line; a MISSING or BAD outcome carries the reason stderr prints, naming its result file."""
    code: str
    id: str
    reason: str | None = None

    def __str__(self) -> str:
        return f"{self.code} {self.id}"


def failure(code: str, outcome_id: str, rule: Rule, reason: str) -> Outcome:
    return Outcome(code, outcome_id, f"{reason} ({rule.origin})")


# ---------------------------------------------------------------- the result files

def unique_names(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """The object_pairs_hook that keeps json.loads from taking the last of two values under one name."""
    obj: dict[str, object] = {}
    for name, value in pairs:
        if name in obj:
            raise RepeatedName(name)
        obj[name] = value
    return obj


def member(item: dict, key: str, kind: type, where: str) -> object:
    value = item.get(key)
    if not isinstance(value, kind):
        raise InputError(f"{where}: {key} is not {'a string' if kind is str else 'an array'}")
    return value


def optional_text(item: dict, key: str, where: str) -> str | None:
    """The string under `key`, None when the object has no such key."""
    return member(item, key, str, where) if key in item else None


def texts(item: object, keys: tuple[str, ...], where: str) -> list[str]:
    """The string values of `keys` in the object `item`."""
    if not isinstance(item, dict):
        raise InputError(f"{where} is not an object")
    return [member(item, key, str, where) for key in keys]


def string_items(values: list, where: str) -> tuple[str, ...]:
    for number, value in enumerate(values, 1):
        if not isinstance(value, str):
            raise InputError(f"{where} {number} is not a string")
    return tuple(values)


def is_rule_id(value: str) -> bool:
    return bool(value) and value == value.strip() and "*" not in value and not LINE_BREAK.search(value)


def parse_rule(item: object, where: str, origin: Path) -> Rule:
    if not isinstance(item, dict):
        raise InputError(f"{where} is not an object")
    rule_id = member(item, "id", str, where)
    if not is_rule_id(rule_id):
        raise InputError(f"{where}: id {rule_id!r} is empty, holds `*` or a line break, or has white space at an end")
    record, text = optional_text(item, "record", where), optional_text(item, "text", where)
    if record is None and text is None:
        raise InputError(f"{where}: the rule carries neither record nor text")
    sources = member(item, "sources", list, where)
    corrections = member(item, "corrections", list, where)
    return Rule(
        id=rule_id,
        record=record,
        text=text,
        hypotheses=string_items(member(item, "hypotheses", list, where), f"{where}: hypotheses item"),
        sources=tuple(Source(*texts(entry, ("source", "seen"), f"{where}: sources item {number}"))
                      for number, entry in enumerate(sources, 1)),
        corrections=tuple(Correction(*texts(entry, ("where", "says", "source_says"), f"{where}: corrections item {number}"))
                          for number, entry in enumerate(corrections, 1)),
        notes=member(item, "notes", str, where),
        origin=origin,
    )


def load_result(path: Path) -> Results:
    try:
        data = json.loads(path.read_bytes().decode("utf-8-sig"), object_pairs_hook=unique_names)
    except OSError as error:
        raise InputError(f"cannot read {path}: {error.strerror or error}") from error
    except UnicodeDecodeError as error:
        raise InputError(f"{path} is not UTF-8: {error}") from error
    except RepeatedName as error:
        raise InputError(f"{path}: an object names {error.args[0]!r} twice") from error
    except json.JSONDecodeError as error:
        raise InputError(f"{path} is not JSON: {error}") from error
    except RecursionError as error:
        raise InputError(f"{path} nests its JSON deeper than the parser reads") from error
    if not isinstance(data, dict):
        raise InputError(f"{path}: the top level is not an object")
    rules: list[Rule] = []
    first_rule: dict[str, int] = {}
    for number, item in enumerate(member(data, "rules", list, str(path)), 1):
        rule = parse_rule(item, f"{path}: rule {number}", path)
        if rule.id in first_rule:
            raise InputError(f"{path}: rule {number}: id {rule.id!r} repeats the id of rule {first_rule[rule.id]}")
        first_rule[rule.id] = number
        rules.append(rule)
    unopened = string_items(member(data, "unopened", list, str(path)), f"{path}: unopened item")
    return Results(tuple(rules), unopened)


def load_results(paths: Iterable[Path]) -> Results:
    """The rules of every result file in order and their unopened sources, each once."""
    rules: list[Rule] = []
    unopened: list[str] = []
    origin: dict[str, Path] = {}
    for path in paths:
        results = load_result(path)
        for rule in results.rules:
            if rule.id in origin:
                raise InputError(f"rule id {rule.id!r} stands in {origin[rule.id]} and in {path}")
            origin[rule.id] = path
        rules += results.rules
        unopened += results.unopened
    return Results(tuple(rules), tuple(dict.fromkeys(unopened)))


# ---------------------------------------------------------------- the Markdown files

def split_ending(line: str) -> tuple[str, str]:
    """A line split at LF into its content and the CR that ends it, empty when none does."""
    return (line[:-1], "\r") if line.endswith("\r") else (line, "")


def record_start(content: str) -> int | None:
    """The index of the ` · ` before the first segment that opens `kind:`, the separators taken as str.split takes them.

    None when no segment after a separator opens `kind:`, which is when the line carries no record.
    """
    position = content.find(SEPARATOR)
    while position != -1:
        if content.startswith(RECORD_KEY, position + len(SEPARATOR)):
            return position
        position = content.find(SEPARATOR, position + len(SEPARATOR))
    return None


@dataclass(frozen=True)
class RuleLine:
    """A rule line of MAP.md in its parts, which joined in order give the line back."""
    head: str           # the opening `- **<id>**`
    text: str           # what stands between the head and the ` · ` that opens the record
    record: str | None  # from the segment that opens `kind:` to the end of the content; None for no record
    ending: str         # the CR that ends the line, empty when none does

    @classmethod
    def read(cls, line: str) -> RuleLine:
        """The parts of `line`, a line that opens `- **<id>**`."""
        content, ending = split_ending(line)
        head = RULE_LINE.match(content)[0]
        start = record_start(content)
        if start is None:
            return cls(head, content[len(head):], None, ending)
        return cls(head, content[len(head):start], content[start + len(SEPARATOR):], ending)

    def __str__(self) -> str:
        record = "" if self.record is None else SEPARATOR + self.record
        return f"{self.head}{self.text}{record}{self.ending}"


class Markdown:
    """The text of a Markdown file and its lines split at LF, each keeping the CR that ends it."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.lines = text.split("\n")

    @classmethod
    def read(cls, path: Path) -> Markdown:
        try:
            return cls(path.read_bytes().decode("utf-8"))
        except OSError as error:
            raise InputError(f"cannot read {path}: {error.strerror or error}") from error
        except UnicodeDecodeError as error:
            raise InputError(f"{path} is not UTF-8: {error}") from error

    def rule_lines(self) -> dict[str, list[int]]:
        """The indices of the rule lines, by id."""
        found: dict[str, list[int]] = {}
        for index, line in enumerate(self.lines):
            match = RULE_LINE.match(split_ending(line)[0])
            if match:
                found.setdefault(match["id"], []).append(index)
        return found

    def newline(self) -> str:
        return "\r\n" if len(self.lines) > 1 and self.lines[0].endswith("\r") else "\n"

    def with_lines_appended(self, added: list[str]) -> str:
        """The text with each added line at its end, set apart by one blank line unless the text ends with one."""
        if not added:
            return self.text
        newline = self.newline()
        separator = ""
        if self.text:
            terminated = self.lines[-1] == ""
            last = self.lines[-2] if terminated else self.lines[-1]
            separator = ("" if terminated else newline) + (newline if last.strip() else "")
        return self.text + separator + "".join(line + newline for line in added)


# ---------------------------------------------------------------- applying

@dataclass(frozen=True)
class Applied:
    outcomes: tuple[Outcome, ...]
    map_text: str
    list_text: str


@dataclass(frozen=True)
class HypothesisLine:
    """A hypothesis line of a rule, the id that names it in the output, and its defect; None for a well-formed line."""
    text: str
    id: str
    defect: str | None


def record_defect(record: str) -> str | None:
    if not record.startswith(RECORD_OPENING):
        return f"the record does not open with `{RECORD_OPENING}`"
    if LINE_BREAK.search(record):
        return "the record holds a line break"
    return None


def hypothesis_line(text: str, rule_id: str) -> HypothesisLine:
    named = RULE_LINE.match(text)
    hypothesis_id = named["id"] if named else rule_id
    if LINE_BREAK.search(text):
        return HypothesisLine(text, hypothesis_id, "holds a line break")
    if not HYPOTHESIS_LINE.match(text):
        return HypothesisLine(text, hypothesis_id, f"does not open `- **<id>**{SEPARATOR}`")
    return HypothesisLine(text, hypothesis_id, None)


def line_numbers(indices: Iterable[int]) -> str:
    return ", ".join(str(index + 1) for index in indices)


def placement_outcome(rule: Rule, found: list[int]) -> Outcome:
    """The outcome of a rule whose id stands on no rule line of the map or on several."""
    if not found:
        return failure(MISSING, rule.id, rule, f"no rule line of the map opens `- **{rule.id}**`")
    return failure(BAD, rule.id, rule, f"the id stands on the rule lines {line_numbers(found)} of the map")


def record_outcome(rule: Rule, in_place: str | None) -> Outcome:
    """The outcome of a rule's record on the one rule line of its id, whose record is `in_place`, its text and hypotheses aside."""
    if in_place is not None or rule.record is None:
        return Outcome(KEPT, rule.id)
    defect = record_defect(rule.record)
    if defect:
        return failure(BAD, rule.id, rule, defect)
    return Outcome(RECORDED, rule.id)


def replacing_record_outcome(rule: Rule, in_place: str | None) -> Outcome:
    """The outcome of a rule's record under --replace on the one rule line of its id, whose record is `in_place`."""
    if rule.record is None:
        return Outcome(KEPT, rule.id)
    defect = record_defect(rule.record)
    if defect:
        return failure(BAD, rule.id, rule, defect)
    if in_place is None:
        return Outcome(RECORDED, rule.id)
    return Outcome(KEPT if in_place == rule.record else REPLACED, rule.id)


def text_defect(text: str) -> str | None:
    if LINE_BREAK.search(text):
        return "the text holds a line break"
    if any(segment.startswith(RECORD_KEY) for segment in text.split(SEPARATOR)):
        return f"the text holds a segment that opens `{RECORD_KEY}`"
    return None


def text_outcome(rule: Rule, in_place: str) -> Outcome | None:
    """The outcome of a rule's text under --replace on its line, whose text is `in_place`; None when the text stays."""
    if rule.text is None:
        return None
    defect = text_defect(rule.text)
    if defect:
        return failure(BAD, rule.id, rule, defect)
    return None if rule.text == in_place else Outcome(REWORDED, rule.id)


@dataclass(frozen=True)
class LineChange:
    """A rule line as a rule leaves it, the outcome of the rule's record and that of its text, None when the text stays."""
    line: RuleLine
    record: Outcome
    text: Outcome | None


def change_line(rule: Rule, line: RuleLine, mode: Mode) -> LineChange:
    """What the rule does to `line`, the one rule line of its id, its hypothesis lines aside."""
    if mode is Mode.FILL:
        record = record_outcome(rule, line.record)
        written = rule.record if record.code == RECORDED else line.record
        return LineChange(RuleLine(line.head, line.text, written, line.ending), record, None)
    record, text = replacing_record_outcome(rule, line.record), text_outcome(rule, line.text)
    changed = RuleLine(line.head, line.text if rule.text is None else rule.text,
                       rule.record if record.code in (RECORDED, REPLACED) else line.record, line.ending)
    text_code = None if text is None else text.code
    writes = BAD not in (record.code, text_code) and (record.code in (RECORDED, REPLACED) or text_code == REWORDED)
    # A text that ends in ` ·` would swallow the separator before the record, and a second run would
    # then find no record on the line; the line is written only when it reads back as it was built.
    if writes and RuleLine.read(str(changed)) != changed:
        unread = failure(BAD, rule.id, rule, "the rewritten line would not read back with this text and record")
        if rule.text is None:
            record = unread
        else:
            text = unread
    return LineChange(changed, record, text)


class HypothesisList:
    """LIST.md as the run rewrites it: its own lines, some replaced in place, then the lines the run appends."""

    def __init__(self, list_file: Markdown, mode: Mode) -> None:
        self.mode = mode
        self.lines = list(list_file.lines)
        self.positions = list_file.rule_lines()
        self.appended: dict[str, str] = {}  # the appended lines by id, in the order the run appends them
        self.written: set[str] = set()      # the ids whose line the run appended or replaced

    def line_of(self, hypothesis_id: str) -> str | None:
        """The first line of the id as the run leaves it so far, without its line ending; None when no line has the id."""
        if hypothesis_id in self.appended:
            return self.appended[hypothesis_id]
        found = self.positions.get(hypothesis_id)
        return split_ending(self.lines[found[0]])[0] if found else None

    def outcome(self, line: HypothesisLine, number: int, rule: Rule, planned: dict[str, str]) -> Outcome:
        """The outcome of a well-formed hypothesis line, the earlier lines of its rule being `planned`, by id."""
        current = planned[line.id] if line.id in planned else self.line_of(line.id)
        if current is None:
            return Outcome(ADDED, line.id)
        if self.mode is Mode.FILL:
            return Outcome(KEPT, line.id)
        found = self.positions.get(line.id, [])
        if len(found) > 1:
            return failure(BAD, line.id, rule, f"hypothesis line {number} of {rule.id} has an id that stands on "
                                               f"the rule lines {line_numbers(found)} of the list")
        if current == line.text:
            return Outcome(KEPT, line.id)
        if line.id in planned or line.id in self.written:
            return failure(BAD, line.id, rule, f"hypothesis line {number} of {rule.id} differs from the line "
                                               f"this run already writes for {line.id}")
        return Outcome(REPLACED, line.id)

    def place(self, rule: Rule) -> list[tuple[Outcome, HypothesisLine]]:
        """The outcome of each hypothesis line of the rule, in order; the list stays as it is until write()."""
        planned: dict[str, str] = {}
        placed: list[tuple[Outcome, HypothesisLine]] = []
        for number, line in enumerate((hypothesis_line(text, rule.id) for text in rule.hypotheses), 1):
            if line.defect:
                outcome = failure(BAD, line.id, rule, f"hypothesis line {number} of {rule.id} {line.defect}")
            else:
                outcome = self.outcome(line, number, rule, planned)
            if outcome.code in (ADDED, REPLACED):
                planned[line.id] = line.text
            placed.append((outcome, line))
        return placed

    def write(self, placed: Iterable[tuple[Outcome, HypothesisLine]]) -> None:
        """Appends each ADDED line and puts each REPLACED line in place of the line of its id, keeping that line's ending."""
        for outcome, line in placed:
            if outcome.code == ADDED:
                self.appended[line.id] = line.text
                self.written.add(line.id)
            elif outcome.code == REPLACED:
                index = self.positions[line.id][0]
                self.lines[index] = line.text + split_ending(self.lines[index])[1]
                self.written.add(line.id)

    def text(self) -> str:
        return Markdown("\n".join(self.lines)).with_lines_appended(list(self.appended.values()))


def apply(rules: Iterable[Rule], map_file: Markdown, list_file: Markdown, mode: Mode = Mode.FILL) -> Applied:
    """The outcomes in their printed order and the texts of the map and the list once the rules are applied."""
    positions = map_file.rule_lines()
    listed = HypothesisList(list_file, mode)
    map_lines = list(map_file.lines)
    map_outcomes: list[Outcome] = []
    list_outcomes: list[Outcome] = []
    for rule in rules:
        found = positions.get(rule.id, [])
        if len(found) != 1:
            map_outcomes.append(placement_outcome(rule, found))
            continue
        change = change_line(rule, RuleLine.read(map_lines[found[0]]), mode)
        record, text = change.record, change.text
        placed = listed.place(rule)
        bad_lines = [outcome for outcome, _ in placed if outcome.code == BAD]
        text_is_bad = text is not None and text.code == BAD
        blocker = "the text" if text_is_bad else "a hypothesis line" if bad_lines else None
        if blocker and record.code in (RECORDED, REPLACED):
            record = failure(BAD, rule.id, rule, f"{blocker} of the rule is BAD, so the record is not written")
        if blocker or record.code == BAD:
            map_outcomes += [record, text] if text_is_bad else [record]
            list_outcomes += bad_lines
            continue
        map_outcomes += [record] if text is None else [record, text]
        if record.code in (RECORDED, REPLACED) or text is not None:
            map_lines[found[0]] = str(change.line)
        listed.write(placed)
        list_outcomes += [outcome for outcome, _ in placed]
    return Applied(tuple(map_outcomes + list_outcomes), "\n".join(map_lines), listed.text())


# ---------------------------------------------------------------- the corrections report

def reported_rules(rules: Iterable[Rule], positions: dict[str, list[int]]) -> list[Rule]:
    """The rules with a correction or a note: by their rule line in the map, then those the map lacks, in their order."""
    reported = [rule for rule in rules if rule.corrections or rule.notes.strip()]
    in_map = sorted((rule for rule in reported if rule.id in positions), key=lambda rule: positions[rule.id][0])
    return in_map + [rule for rule in reported if rule.id not in positions]


def indented(text: str, depth: int) -> str:
    """The text with each line after its first indented by `depth` spaces, so it stays inside its list item."""
    return ("\n" + " " * depth).join(text.splitlines())


def corrections_report(rules: Iterable[Rule], unopened: Iterable[str]) -> str:
    parts = ["# Corrections and notes\n"]
    for rule in rules:
        parts.append(f"\n## {rule.id}\n")
        if rule.corrections:
            parts.append("\n")
        for correction in rule.corrections:
            parts.append(f"- Where: {indented(correction.where, 2)}\n"
                         f"  - Our text says: {indented(correction.says, 4)}\n"
                         f"  - The source says: {indented(correction.source_says, 4)}\n")
        if rule.notes.strip():
            parts.append(f"\nNote: {rule.notes.strip()}\n")
        if rule.sources:
            parts.append("\nSources:\n\n")
            parts += [f"- {indented(source.source, 2)} ({indented(source.seen, 2)})\n" for source in rule.sources]
    parts.append("\n## Unopened sources\n\n")
    listed = [f"- {indented(source, 2)}\n" for source in unopened]
    parts += listed or ["None.\n"]
    return "".join(parts)


# ---------------------------------------------------------------- writing

def new_file_mode() -> int:
    """The mode open() gives a new file: 0o666 less the process umask."""
    umask = os.umask(0)
    os.umask(umask)
    return 0o666 & ~umask


def write_atomic(path: Path, text: str) -> None:
    """Replaces the file at `path` by `text` through a renamed temporary file that keeps the file's mode."""
    try:
        mode = stat.S_IMODE(path.stat().st_mode)
    except FileNotFoundError:
        mode = new_file_mode()
    stream = tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", suffix=".part", delete=False)
    temporary = Path(stream.name)
    try:
        with stream:
            stream.write(text.encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        temporary.chmod(mode)
        temporary.replace(path)
    except BaseException:
        # The error that stopped the write is the one to report; a temporary file the unlink cannot remove
        # stays behind under a name that starts with a dot and ends with .part.
        with contextlib.suppress(OSError):
            temporary.unlink(missing_ok=True)
        raise


def write_all(writes: list[tuple[Path, str]]) -> None:
    written: list[str] = []
    for path, text in writes:
        try:
            write_atomic(path, text)
        except OSError as error:
            already = f"; already written: {', '.join(written)}" if written else ""
            raise InputError(f"cannot write {path}: {error.strerror or error}{already}") from error
        written.append(str(path))


# ---------------------------------------------------------------- command line

def same_file(first: Path, second: Path) -> bool:
    return first.resolve() == second.resolve()


def run(args: argparse.Namespace) -> Applied:
    """Reads the inputs, applies the results and, without --dry-run, writes the report, the list and the map."""
    results = load_results(args.results)
    map_file, list_file = Markdown.read(args.map), Markdown.read(args.hypotheses)
    applied = apply(results.rules, map_file, list_file, args.mode)
    if args.dry_run:
        return applied
    writes = []
    if args.corrections:
        rules = reported_rules(results.rules, map_file.rule_lines())
        writes.append((args.corrections, corrections_report(rules, results.unopened)))
    if applied.list_text != list_file.text:
        writes.append((args.hypotheses, applied.list_text))
    if applied.map_text != map_file.text:
        writes.append((args.map, applied.map_text))
    write_all(writes)
    return applied


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--map", metavar="MAP.md", type=Path, required=True,
                        help="the provenance map whose rule lines take the records")
    parser.add_argument("--hypotheses", metavar="LIST.md", type=Path, required=True,
                        help="the list of hypotheses that takes the hypothesis lines")
    parser.add_argument("--replace", dest="mode", action="store_const", const=Mode.REPLACE, default=Mode.FILL,
                        help="replace the records, texts and hypothesis lines the results name")
    parser.add_argument("--corrections", metavar="OUT.md", type=Path,
                        help="write the corrections, the notes and the unopened sources to OUT.md")
    parser.add_argument("--dry-run", action="store_true", help="print the outcomes and write nothing")
    parser.add_argument("results", metavar="RESULT.json", type=Path, nargs="+", help="the workers' result files")
    args = parser.parse_args(argv)
    if same_file(args.map, args.hypotheses):
        parser.error("--map and --hypotheses name one file")
    if args.corrections and any(same_file(args.corrections, p) for p in (args.map, args.hypotheses, *args.results)):
        parser.error("--corrections names one of the input files")
    try:
        applied = run(args)
    except InputError as error:
        print(error, file=sys.stderr)
        return 2
    for outcome in applied.outcomes:
        print(outcome)
        if outcome.reason:
            print(f"{outcome}: {outcome.reason}", file=sys.stderr)
    counts = {code: sum(outcome.code == code for outcome in applied.outcomes) for code in CODES}
    print(", ".join(f"{counts[code]} {code.lower()}" for code in CODES))
    return 1 if counts[MISSING] or counts[BAD] else 0


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
