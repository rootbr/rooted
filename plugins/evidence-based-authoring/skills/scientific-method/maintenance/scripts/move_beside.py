#!/usr/bin/env python3
"""Move the published sources of every hypothesis from its field `test` to its field `beside`.

    move_beside.py [--root DIR] [--dry-run] [FILE ...]

A hypothesis awaits its test, so its `test` holds only a planned test of our own, and every
published source found for it stands in `beside` (references/record-format.md § Tests). This
script brings the lists of hypotheses and the provenance maps to that form. A second run moves
nothing.

Input. FILE is a UTF-8 Markdown file, relative to the current directory. With no FILE the script
takes every file under --root (the current directory by default) whose name matches
`*provenance*.md` or `pending-evidence*.md`, passing over the directories scripts/check_record.py
passes over. A rule line and its record are read as scripts/check_record.py reads them: the line
opens `- **<id>**`, is split on ` · `, and its record runs from the first segment that opens
`kind:` to the end of the line, the first value of each key counting.

Moving. A rule line is a candidate when its record is a claim with the standing hypothesis and
its `test` holds an entry of the form `external <locator> first-hand|abstract|relay`. A candidate
is LEFT as it stands, with the reason printed, when
  - it carries `fit` or `transfer`, which describe a test of the claim;
  - it carries `beside`, `beside-result` or `beside-bounds` already;
  - its `test` holds an entry in none of the four forms of a test;
  - a key among `test`, `result` and `bounds` is written twice.
Every other candidate is MOVED: the `external` entries of `test` go to `beside`, in their order,
and the `own` entries stay in `test`; `result` becomes `beside-result` and `bounds` becomes
`beside-bounds`, each whole and in its place, because a hypothesis has no result of a test of its
own: a result would have moved its standing. `beside` takes the place of `test` when no `own`
entry stays, and follows `test` when one does. `validity` stays where it stands: on a hypothesis
whose sources stand in `beside` it says what a source reports of its measure. Every other byte of a file stays as it was, line
endings included. A claim at any other standing is not read: which of its tests answers a
neighbouring question is a judgement, and the script makes none.

Output on stdout: one line per candidate, `<path>:<line>: MOVED <id>: <n> to beside[, <k> own
kept in test]` or `<path>:<line>: LEFT <id>: <reason>`; per file with a candidate the line
`<path>: <m> moved, <l> left; test entries <a> -> <b>, beside entries <c> -> <d>`, the entries
counted over every rule line of the file; and the last line `<m> moved, <l> left in <f> file(s)`.
Paths are relative to the root.

--dry-run prints the same lines and writes nothing.

Exit: 0 with no line left; 1 with a line left; 2 on wrong usage, a root that is not a directory, an
unreadable or non-UTF-8 file, or a file that cannot be written, with the message on stderr. Each
changed file is written through a renamed temporary file in its own directory, after every file
was read.

Privileges: reads the Markdown files; writes the files it changes and their temporary files; opens
no network connection and runs no other program. Standard library alone, with scripts/check_record.py
and apply_records.py of this skill; runs under `python3 -I`.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
# Under python3 -I no script directory is on the path, so both neighbours are put there by name.
sys.path[:0] = [str(SKILL / "scripts"), str(Path(__file__).resolve().parent)]
import check_record as cr  # noqa: E402
from apply_records import write_atomic  # noqa: E402

MOVED, LEFT = "MOVED", "LEFT"
EXTERNAL_READINGS = (cr.FIRST_HAND, cr.ABSTRACT, cr.RELAY)
TEST, RESULT, BOUNDS = "test", "result", "bounds"
BESIDE, BESIDE_RESULT, BESIDE_BOUNDS = "beside", "beside-result", "beside-bounds"
RENAMED = {RESULT: BESIDE_RESULT, BOUNDS: BESIDE_BOUNDS}
DESCRIBE_A_TEST = ("fit", "transfer")


class InputError(Exception):
    """The run cannot go on: wrong usage, an unreadable file or a file that cannot be written."""


@dataclass(frozen=True)
class Outcome:
    path: str
    line: int
    code: str
    id: str
    detail: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.code} {self.id}: {self.detail}"


@dataclass
class FileRun:
    path: str
    text: str
    moved_text: str = ""
    outcomes: list[Outcome] = field(default_factory=list)

    def entries(self, text: str, key: str) -> int:
        return sum(len(cr.parse_tests(rule.record.fields.get(key, "")))
                   for rule in cr.parse_rule_lines(self.path, text) if rule.record)

    def summary(self) -> str:
        moved = sum(o.code == MOVED for o in self.outcomes)
        left = len(self.outcomes) - moved
        return (f"{self.path}: {moved} moved, {left} left; "
                f"test entries {self.entries(self.text, TEST)} -> {self.entries(self.moved_text, TEST)}, "
                f"beside entries {self.entries(self.text, BESIDE)} -> {self.entries(self.moved_text, BESIDE)}")


def entry_items(value: str) -> list[str]:
    """The entries of a test value as written, split as scripts/check_record.py splits them."""
    return [item.strip() for item in value.split("; ")] if value else []


def record_start(segments: list[str]) -> int | None:
    return next((i for i, s in enumerate(segments) if s.startswith("kind:")), None)


def key_of(segment: str) -> str:
    return segment.partition(":")[0]


def move_line(line: str) -> tuple[str, str | None, str]:
    """The line after the move, and the outcome's code and detail; code None for a line that is no candidate."""
    segments = line.split(cr.SEPARATOR)
    start = record_start(segments)
    if start is None:
        return line, None, ""
    fields = cr.parse_record(segments[start:]).fields
    if fields.get("kind") != "claim" or fields.get("standing") != "hypothesis":
        return line, None, ""
    tests = cr.parse_tests(fields.get(TEST, ""))
    if not any(form in EXTERNAL_READINGS for form, _ in tests):
        return line, None, ""

    keys = [key_of(s) for s in segments[start:]]
    if carried := [k for k in DESCRIBE_A_TEST if k in fields]:
        fields_word = "a field that describes" if len(carried) == 1 else "fields that describe"
        return line, LEFT, f"carries {', '.join(carried)}, {fields_word} a test"
    if carried := [k for k in (BESIDE, BESIDE_RESULT, BESIDE_BOUNDS) if k in fields]:
        return line, LEFT, f"carries {', '.join(carried)} already"
    if any(form is None for form, _ in tests):
        return line, LEFT, "its test holds an entry outside the four forms"
    if twice := [k for k in (TEST, RESULT, BOUNDS) if keys.count(k) > 1]:
        return line, LEFT, f"writes {', '.join(twice)} twice"

    owns = [item for item, (form, _) in zip(entry_items(fields[TEST]), tests) if form == cr.OWN]
    externals = [item for item, (form, _) in zip(entry_items(fields[TEST]), tests) if form in EXTERNAL_READINGS]
    moved: list[str] = segments[:start]
    for segment in segments[start:]:
        key = key_of(segment)
        if key == TEST and owns:
            moved += [f"{TEST}: {'; '.join(owns)}", f"{BESIDE}: {'; '.join(externals)}"]
        elif key == TEST:
            moved.append(BESIDE + segment[len(key):])
        elif key in RENAMED:
            moved.append(RENAMED[key] + segment[len(key):])
        else:
            moved.append(segment)
    detail = f"{len(externals)} to beside" + (f", {len(owns)} own kept in test" if owns else "")
    return cr.SEPARATOR.join(moved), MOVED, detail


def move_text(path: str, text: str) -> FileRun:
    """The file's text after the move, with one outcome per candidate line."""
    run = FileRun(path, text)
    pieces = []
    for number, raw in enumerate(text.splitlines(keepends=True), 1):
        ending = "\r\n" if raw.endswith("\r\n") else raw[-1:] if raw[-1:].splitlines() == [""] else ""
        body = raw[:len(raw) - len(ending)]
        match = cr.RULE_LINE.match(body)
        if match:
            # check_record.py reads a line without its trailing white space; the move keeps that white space.
            stripped = body.rstrip()
            new, code, detail = move_line(stripped)
            if code:
                run.outcomes.append(Outcome(path, number, code, match["id"], detail))
                body = new + body[len(stripped):]
        pieces.append(body + ending)
    run.moved_text = "".join(pieces)
    return run


def read(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise InputError(f"cannot read {path}: {error}") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=".", help="the repository root (default: the current directory)")
    parser.add_argument("--dry-run", action="store_true", help="print the outcomes and write nothing")
    parser.add_argument("files", nargs="*", metavar="FILE", help="Markdown files (default: every map under the root)")
    args = parser.parse_args(argv)
    root = Path(args.root).absolute()
    if not root.is_dir():
        print(f"root {args.root} is not a directory", file=sys.stderr)
        return 2
    paths = [Path(f).absolute() for f in args.files] or cr.discover(root)
    try:
        runs = [(path, move_text(cr.relative(root, path), read(path))) for path in paths]
        changed = [(path, run) for path, run in runs if run.moved_text != run.text]
        if not args.dry_run:
            for path, run in changed:
                try:
                    write_atomic(path, run.moved_text)
                except OSError as error:
                    raise InputError(f"cannot write {path}: {error.strerror or error}") from error
    except InputError as error:
        print(error, file=sys.stderr)
        return 2
    outcomes = [o for _, run in runs for o in run.outcomes]
    for _, run in runs:
        for outcome in run.outcomes:
            print(outcome)
        if run.outcomes:
            print(run.summary())
    moved = sum(o.code == MOVED for o in outcomes)
    left = len(outcomes) - moved
    print(f"{moved} moved, {left} left in {sum(1 for _, run in runs if run.outcomes)} file(s)")
    return 1 if left else 0


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
