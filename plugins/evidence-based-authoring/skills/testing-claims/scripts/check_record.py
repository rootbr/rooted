#!/usr/bin/env python3
"""Check the records that close the rule lines of provenance maps and lists of hypotheses.

    check_record.py [--root DIR] [--require] [--stats] [--changed [--base REV] | --staged] [FILE ...]

A record is the tail of a rule line from its field `kind` on. references/record-format.md states
the fields, the rules and what each finding code rejects; this docstring states how the script
reads the files and applies the codes.

Input. FILE is a Markdown file, relative to the current directory. With no FILE the script checks
every file under the root whose name matches `*provenance*.md` or `pending-evidence*.md`, passing
over directories named .git, tmp, trash, node_modules, worktrees and __pycache__ and those whose
name ends with -workspace. --root DIR is the repository root, the current directory by default:
the path of an `own` test resolves against it and must stay inside it, and every printed path is
relative to it.

A rule line matches `^- \\*\\*<id>\\*\\*`. The line is split on ` · ` (space, middle dot, space);
the record is the first segment that starts with `kind:` and every segment after it, and the
segments before it are free text the script does not read. A line without such a segment carries
no record.

An id is unique per directory: the checked files that lie in one directory form one group, and
every comparison of ids below stays inside a group.

Plain mode applies KIND, FIELD, STANDING, TEST, SUPPORT, OWN, FIT and DUP to every rule line that
carries a record. A claim takes every field of the claim row and of the standing table, whatever
its standing; a hypothesis, a supported claim and a law whose `test` holds an `own` test also
require `threshold` and `runs`. DUP reports a recorded line whose id stands on another rule line
of the same directory. The words `proved` and `proven` count in `standing` and `result` as whole
words, in any case. A rule line without a record is counted; under --require it is NORECORD.

The comparing modes set a current state against a base state:
  --changed [--base REV]  the working tree against the same paths at REV, HEAD by default
  --staged                the index (`git show :<path>`) against HEAD
--base without --changed, or with --staged, is wrong usage. With no FILE the checked set is the
union of the matching files of the working tree and of the base listing (`git ls-tree`, the same
directories passed over), so a deleted map is still checked. A path absent from the current
state (the working tree under --changed, the index under --staged) or from the base counts as
empty there; a FILE named on the command line must exist in the working tree. A rule line is
changed when its id stands on no rule line of its directory's base state or its text differs
from every base line of that id there. A changed line without a record is NORECORD, and every
recorded line still passes the plain-mode codes. The base state of PREDICTION and ERASED is the
union of the records of the checked files of one directory at the base, so an id may move from
that directory's list of hypotheses to its provenance map:
  PREDICTION  compares measure, against, scope, refuter and threshold after collapsing runs of
              white space; a field absent on both sides is equal; one equal base record of the
              id in the same directory suffices
  ERASED      a base record with the standing refuted or contested whose id stands on no rule
              line of its directory's current state; reported at the base path and base line

Output on stdout: one line per finding, `<path>:<line>: <CODE>: <message>`, ordered by path and
line; with --stats then three lines
    records by kind: claim <n>, decision <n>, definition <n>, norm <n>
    claims by standing: contested <n>, hypothesis <n>, law <n>, refuted <n>, supported <n>
    rule lines without a record: <n>
(a value outside the vocabulary is counted after these); and the last line `<n> error(s)`.
Every finding is an error.

Exit: 0 no error; 1 an error; 2 an unreadable or non-UTF-8 file, wrong usage, a root that is not
a directory, or a failed git command (outside a repository, an unknown REV), with the message
on stderr. --stats changes no exit status.

Privileges: reads the checked files and, in the comparing modes only, runs `git show`,
`git ls-tree` and `git rev-parse` in the root; writes nothing, opens no network connection, uses
the standard library alone.
"""
from __future__ import annotations

import argparse
import os
import posixpath
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

RULE_LINE = re.compile(r"^- \*\*(?P<id>[^*]+)\*\*")
SEPARATOR = " · "
KEY = re.compile(r"[a-z-]+")
MAP_PATTERNS = ("*provenance*.md", "pending-evidence*.md")
SKIPPED_DIRS = frozenset({".git", "tmp", "trash", "node_modules", "worktrees", "__pycache__"})
SKIPPED_DIR_SUFFIX = "-workspace"

KINDS = ("claim", "decision", "definition", "norm")
STANDINGS = ("contested", "hypothesis", "law", "refuted", "supported")
REQUIRED = {
    "decision": ("owner", "goal"),
    "definition": ("term",),
    "norm": ("issuer", "version", "locator"),
    "claim": ("standing", "measure", "against", "scope", "refuter"),
}
OPTIONAL = {
    "decision": ("hypothesis",),
    "definition": (),
    "norm": (),
    "claim": ("threshold", "runs", "test", "transfer"),
}
ADDED_BY_STANDING = {
    "hypothesis": (),
    "supported": ("test", "result", "bounds", "fit"),
    "law": ("test", "result", "bounds", "fit"),
    "contested": ("test", "result"),
    "refuted": ("test", "result", "bounds"),
}
ADDED_BY_OWN_TEST = ("threshold", "runs")
OWN_TEST_ADDS_TO = ("hypothesis", "supported", "law")
TWO_TESTS = ("law", "contested")
SUPPORTING = ("supported", "law")
TAKEN = {
    kind: frozenset({"kind", *REQUIRED[kind], *OPTIONAL[kind]}
                    | ({f for added in ADDED_BY_STANDING.values() for f in added} if kind == "claim" else set()))
    for kind in KINDS
}
KNOWN_KEYS = frozenset().union(*TAKEN.values())
FITS = ("direct", "transfer")
PROVED = re.compile(r"\b(?:proved|proven)\b", re.IGNORECASE)
PREDICTION_FIELDS = ("measure", "against", "scope", "refuter", "threshold")
ERASABLE = ("refuted", "contested")

OWN = "own"
FIRST_HAND = "first-hand"
RELAY = "relay"
OWN_TEST = re.compile(r"own (?P<path>\S(?:.*\S)?)")
EXTERNAL_TEST = re.compile(r"external (?P<locator>\S(?:.*\S)?) (?P<reading>first-hand|relay)")


class InputError(Exception):
    """The input cannot be checked: an unreadable file or a failed git command."""


@dataclass
class Record:
    fields: dict[str, str]
    defects: list[str]


@dataclass
class RuleLine:
    path: str
    line: int
    id: str
    text: str
    record: Record | None

    @property
    def key(self) -> tuple[str, str]:
        """The id within its directory: ids are unique per directory."""
        return posixpath.dirname(self.path), self.id


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.code}: {self.message}"


def parse_record(segments: list[str]) -> Record:
    """The fields of a record's segments, first value of each key; the FIELD defects of their form."""
    fields: dict[str, str] = {}
    defects: list[str] = []
    for segment in segments:
        key, colon, value = segment.partition(":")
        if not colon or not KEY.fullmatch(key):
            defects.append(f"segment {segment!r} is not `key: value` with a key of lowercase letters and hyphens")
            continue
        value = value.strip()
        if key in fields:
            defects.append(f"key {key} is written twice")
            continue
        fields[key] = value
        if key not in KNOWN_KEYS:
            defects.append(f"key {key} is outside the record format")
        elif not value and key != "kind":
            defects.append(f"{key} has an empty value")
    return Record(fields, defects)


def parse_rule_lines(path: str, text: str) -> list[RuleLine]:
    rules = []
    for number, raw in enumerate(text.splitlines(), 1):
        match = RULE_LINE.match(raw)
        if not match:
            continue
        line = raw.rstrip()
        segments = line.split(SEPARATOR)
        start = next((i for i, s in enumerate(segments) if s.startswith("kind:")), None)
        record = parse_record(segments[start:]) if start is not None else None
        rules.append(RuleLine(path, number, match["id"], line, record))
    return rules


def parse_tests(value: str) -> list[tuple[str | None, str]]:
    """Each test of a `test` value as (form, argument); the form is None for a test outside the three forms."""
    if not value:
        return []
    tests = []
    for item in value.split("; "):
        item = item.strip()
        own = OWN_TEST.fullmatch(item)
        external = EXTERNAL_TEST.fullmatch(item)
        if own:
            tests.append((OWN, own["path"]))
        elif external:
            tests.append((external["reading"], external["locator"]))
        else:
            tests.append((None, item))
    return tests


def own_path_exists(root: Path, path: str) -> bool:
    """True when the path names an existing file or directory inside the root."""
    base = root.resolve()
    target = (base / path).resolve()
    return (target == base or base in target.parents) and target.exists()


def check_record(rule: RuleLine, root: Path) -> list[Finding]:
    """The plain-mode findings of one recorded rule line, DUP aside."""
    found: list[Finding] = []

    def add(code: str, message: str) -> None:
        found.append(Finding(rule.path, rule.line, code, message))

    fields = rule.record.fields
    for defect in rule.record.defects:
        add("FIELD", defect)
    kind = fields.get("kind", "")
    standing = fields.get("standing", "")
    tests = parse_tests(fields.get("test", ""))
    is_claim = kind == "claim"

    if not kind:
        add("KIND", "kind has no value")
    elif kind not in KINDS:
        add("KIND", f"kind {kind!r} is outside {', '.join(KINDS)}")
    else:
        for key in fields:
            if key in KNOWN_KEYS and key not in TAKEN[kind]:
                add("FIELD", f"kind {kind} does not take {key}")
        required = {key: f"kind {kind}" for key in REQUIRED[kind]}
        if is_claim:
            required |= {key: f"standing {standing}" for key in ADDED_BY_STANDING.get(standing, ())}
            if standing in OWN_TEST_ADDS_TO and any(form == OWN for form, _ in tests):
                required |= {key: f"standing {standing} with an own test" for key in ADDED_BY_OWN_TEST}
        for key, reason in required.items():
            if key not in fields:
                add("FIELD", f"{key} is required for {reason}")

    if standing and standing not in STANDINGS:
        add("STANDING", f"standing {standing!r} is outside {', '.join(STANDINGS)}")
    if PROVED.search(fields.get("result", "")):
        add("STANDING", "result says proved or proven; a test supports a claim and never proves it")

    for form, argument in tests:
        if form is None:
            add("TEST", f"test {argument!r} is not `own <path>`, `external <locator> first-hand` or `external <locator> relay`")
    if is_claim and standing in TWO_TESTS and tests and len(tests) < 2:
        add("TEST", f"standing {standing} takes two tests or more; the record names {len(tests)}")
    readable = [form for form, _ in tests if form is not None]
    if is_claim and standing in SUPPORTING and readable and not any(form in (OWN, FIRST_HAND) for form in readable):
        add("SUPPORT", f"standing {standing} rests on relay tests alone; it needs an own or first-hand test")
    for form, argument in tests:
        if form == OWN and not own_path_exists(root, argument):
            add("OWN", f"own test {argument} does not exist under the root")

    fit = fields.get("fit", "")
    if fit and fit not in FITS:
        add("FIT", f"fit {fit!r} is outside {', '.join(FITS)}")
    if fit == "transfer" and not fields.get("transfer"):
        add("FIT", "fit: transfer without transfer")
    return found


def duplicates(rules: list[RuleLine]) -> list[Finding]:
    """DUP at each recorded line whose id stands on another rule line of the same directory."""
    by_key: dict[tuple[str, str], list[RuleLine]] = defaultdict(list)
    for rule in rules:
        by_key[rule.key].append(rule)
    found = []
    for rule in rules:
        others = [f"{o.path}:{o.line}" for o in by_key[rule.key] if o is not rule]
        if rule.record and others:
            found.append(Finding(rule.path, rule.line, "DUP", f"id {rule.id} also stands on {', '.join(others)}"))
    return found


def prediction(fields: dict[str, str]) -> tuple[str | None, ...]:
    return tuple(" ".join(fields[key].split()) if key in fields else None for key in PREDICTION_FIELDS)


def predictions(current: list[RuleLine], base: list[RuleLine], base_name: str) -> list[Finding]:
    """PREDICTION for each claim with an own test and a standing past hypothesis whose prediction the base lacks."""
    base_records: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for rule in base:
        if rule.record:
            base_records[rule.key].append(rule.record.fields)
    found = []
    for rule in current:
        if not rule.record:
            continue
        fields = rule.record.fields
        standing = fields.get("standing", "")
        if fields.get("kind") != "claim" or not standing or standing == "hypothesis":
            continue
        if not any(form == OWN for form, _ in parse_tests(fields.get("test", ""))):
            continue
        earlier = base_records.get(rule.key, [])
        if any(prediction(b) == prediction(fields) for b in earlier):
            continue
        if not earlier:
            message = (f"{rule.id} has no record in {posixpath.dirname(rule.path) or '.'} at {base_name}; "
                       "the hypothesis with its prediction is committed first")
        else:
            now, then = prediction(fields), prediction(earlier[0])
            changed = [key for key, a, b in zip(PREDICTION_FIELDS, now, then) if a != b]
            message = f"{rule.id} differs from its record at {base_name} in {', '.join(changed)}"
        found.append(Finding(rule.path, rule.line, "PREDICTION", message))
    return found


def erasures(current: list[RuleLine], base: list[RuleLine], base_name: str) -> list[Finding]:
    """ERASED at the base position of each refuted or contested record whose id is gone from its directory."""
    present = {rule.key for rule in current}
    found = []
    for rule in base:
        standing = rule.record.fields.get("standing") if rule.record else None
        if standing in ERASABLE and rule.key not in present:
            found.append(Finding(rule.path, rule.line, "ERASED",
                                 f"{rule.id}, {standing} at {base_name}, has no rule line; the record of a test that went against stays"))
    return found


def changed_lines(current: list[RuleLine], base: list[RuleLine]) -> list[RuleLine]:
    base_texts: dict[tuple[str, str], set[str]] = defaultdict(set)
    for rule in base:
        base_texts[rule.key].add(rule.text)
    return [rule for rule in current if rule.text not in base_texts.get(rule.key, ())]


def check(current: list[RuleLine], root: Path, require: bool = False,
          base: list[RuleLine] | None = None, base_name: str = "HEAD") -> list[Finding]:
    """Every finding over the rule lines of the checked files; base is None in plain mode."""
    found: list[Finding] = []
    for rule in current:
        if rule.record:
            found += check_record(rule, root)
    found += duplicates(current)
    unrecorded = [rule for rule in current if not rule.record]
    if base is not None:
        changed = {(rule.path, rule.line) for rule in changed_lines(current, base)}
        required = [rule for rule in unrecorded if require or (rule.path, rule.line) in changed]
    else:
        required = unrecorded if require else []
    found += [Finding(r.path, r.line, "NORECORD",
                      "a changed rule line without a record" if base is not None and not require else "a rule line without a record")
              for r in required]
    if base is not None:
        found += predictions(current, base, base_name)
        found += erasures(current, base, base_name)
    return sorted(found)


def skipped_dir(name: str) -> bool:
    return name in SKIPPED_DIRS or name.endswith(SKIPPED_DIR_SUFFIX)


def is_map(name: str) -> bool:
    return any(fnmatchcase(name, pattern) for pattern in MAP_PATTERNS)


def discover(root: Path) -> list[Path]:
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not skipped_dir(d))
        found += [Path(dirpath) / name for name in sorted(filenames) if is_map(name)]
    return found


def base_maps(root: Path, base_name: str) -> list[str]:
    """The root-relative paths of the maps at the base revision, the skipped directories passed over."""
    args = ("ls-tree", "-r", "-z", "--name-only", base_name)
    run = git(root, *args)
    if run.returncode != 0:
        raise git_failure(args, run)
    found = []
    for rel in run.stdout.decode("utf-8", "surrogateescape").split("\0"):
        parts = rel.split("/")
        if rel and is_map(parts[-1]) and not any(skipped_dir(d) for d in parts[:-1]):
            found.append(rel)
    return found


def relative(root: Path, path: Path) -> str:
    return Path(os.path.relpath(path, root)).as_posix()


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise InputError(f"cannot read {path}: {e}") from e


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["git", "--no-pager", "-C", str(root), *args], capture_output=True)
    except OSError as e:
        raise InputError(f"cannot run git: {e}") from e


def git_failure(args: tuple[str, ...], run: subprocess.CompletedProcess) -> InputError:
    detail = run.stderr.decode("utf-8", "replace").strip()
    return InputError(f"git {' '.join(args)} failed: {detail}" if detail else f"git {' '.join(args)} failed")


def git_has(root: Path, spec: str) -> bool:
    """True when git resolves the spec; False when it names nothing."""
    args = ("rev-parse", "--verify", "--quiet", spec)
    run = git(root, *args)
    if run.returncode not in (0, 1):
        raise git_failure(args, run)
    return run.returncode == 0


def git_text(root: Path, spec: str) -> str:
    args = ("show", spec)
    run = git(root, *args)
    if run.returncode != 0:
        raise git_failure(args, run)
    try:
        return run.stdout.decode("utf-8")
    except UnicodeDecodeError as e:
        raise InputError(f"{spec} is not UTF-8: {e}") from e


def load(root: Path, paths: list[Path], mode: str, base_name: str,
         discovered: bool = False) -> tuple[list[RuleLine], list[RuleLine] | None]:
    """The rule lines of the current state and, in a comparing mode, of the base state.

    discovered: the paths come from discovery, so the base listing joins them and a path the
    working tree lacks counts as empty.
    """
    if mode == "plain":
        return [rule for path in paths for rule in parse_rule_lines(relative(root, path), read_file(path))], None
    args = ("rev-parse", "--show-toplevel")
    run = git(root, *args)
    if run.returncode != 0:
        raise git_failure(args, run)
    if not git_has(root, f"{base_name}^{{commit}}"):
        raise InputError(f"{base_name} is not a revision of the repository at {root}")
    if discovered:
        known = {relative(root, path) for path in paths}
        paths = paths + [root / rel for rel in base_maps(root, base_name) if rel not in known]
        paths.sort(key=lambda path: relative(root, path))
    current: list[RuleLine] = []
    base: list[RuleLine] = []
    for path in paths:
        rel = relative(root, path)
        if mode == "staged":
            text = git_text(root, f":./{rel}") if git_has(root, f":./{rel}") else ""
        elif discovered and not path.exists():
            text = ""
        else:
            text = read_file(path)
        current += parse_rule_lines(rel, text)
        spec = f"{base_name}:./{rel}"
        base += parse_rule_lines(rel, git_text(root, spec) if git_has(root, spec) else "")
    return current, base


def counts(counter: Counter, names: tuple[str, ...]) -> str:
    items = [(name, counter.get(name, 0)) for name in names]
    items += sorted((name or "(empty)", n) for name, n in counter.items() if name not in names)
    return ", ".join(f"{name} {n}" for name, n in items)


def stats(rules: list[RuleLine]) -> list[str]:
    records = [rule.record.fields for rule in rules if rule.record]
    kinds = Counter(fields.get("kind", "") for fields in records)
    standings = Counter(fields.get("standing", "") for fields in records if fields.get("kind") == "claim")
    return [
        f"records by kind: {counts(kinds, KINDS)}",
        f"claims by standing: {counts(standings, STANDINGS)}",
        f"rule lines without a record: {sum(1 for rule in rules if not rule.record)}",
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=".", help="the repository root (default: the current directory)")
    parser.add_argument("--require", action="store_true", help="every rule line must carry a record")
    parser.add_argument("--stats", action="store_true", help="print counts of records by kind and standing")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--changed", action="store_true", help="compare the working tree with --base")
    mode.add_argument("--staged", action="store_true", help="compare the index with HEAD")
    parser.add_argument("--base", metavar="REV", help="the base revision of --changed (default HEAD)")
    parser.add_argument("files", nargs="*", metavar="FILE", help="Markdown files to check (default: every map under the root)")
    args = parser.parse_args(argv)
    if args.base is not None and not args.changed:
        parser.error("--base takes --changed" + (", not --staged" if args.staged else ""))

    root = Path(args.root).absolute()
    if not root.is_dir():
        print(f"root {args.root} is not a directory", file=sys.stderr)
        return 2
    paths = [Path(f).absolute() for f in args.files] or discover(root)
    mode_name = "changed" if args.changed else "staged" if args.staged else "plain"
    base_name = args.base or "HEAD"
    try:
        current, base = load(root, paths, mode_name, base_name, discovered=not args.files)
    except InputError as e:
        print(e, file=sys.stderr)
        return 2
    findings = check(current, root, require=args.require, base=base, base_name=base_name)
    for finding in findings:
        print(finding)
    if args.stats:
        for line in stats(current):
            print(line)
    print(f"{len(findings)} error(s)")
    return 1 if findings else 0


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
