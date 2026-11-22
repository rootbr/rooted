#!/usr/bin/env python3
"""Keep a journal of counts of how the skill's scripts are used, and print a summary of it to paste into feedback.

    feedback.py status          the switch, the directory, the number of events and of days with use
    feedback.py on | off        turn the journal on or off
    feedback.py summary         print the summary of the journal
    feedback.py reset           delete the journal, keep the switch

The journal is off until the user turns it on, and nothing in it leaves the machine: the user
pastes the summary into the feedback form himself. The directory is $HANDOVER_FEEDBACK_DIR, else
$XDG_STATE_HOME/handing-over-to-readers ($HOME/.local/state when the variable is unset or empty).
feedback.json there is the switch: the journal is on only while that file holds {"journal": true};
absent, unreadable or anything else is off. journal.jsonl is the journal: one JSON object a line,
each appended with a single write, the file created with mode 0600.

The other scripts of the skill import this file and call record(event, **fields) once a run. With
the journal on, record appends {"day": "YYYY-MM-DD", "version": "<plugin version>", "event":
"<event>", ...fields}: the local date and no time of day; the version is the "version" of the
plugin's .claude-plugin/plugin.json, two directories above the skill, when it matches VERSION,
else "unknown". The schema is closed (SCHEMA): a field's value is a non-negative integer, a
boolean, a word of the set named for that field, or, for "codes", a mapping from a rule code
(CODE) to a positive integer, so no caller can write text into the journal. An event with an
unknown name, an unknown field or a value of another kind is dropped whole. record never raises
and prints nothing: with the journal off, outside the schema or on any failure it returns having
written nothing.

The summary is plain text built from the journal alone, with no date in it: the skill; the plugin
versions seen, the days with use and the number of events; one line per kind of use that
occurred; then what the journal holds, and the address of the feedback form, made from the
"repository" of the plugin's manifest. A journal line outside the schema is skipped.

Exit: 0 done; 2 the directory cannot be written (on, off, reset). The script reads the switch, the
journal and the plugin's manifest, writes only the switch and the journal, starts no program, opens
no network connection and uses the Python standard library alone.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Mapping

SKILL_NAME = "handing-over-to-readers"
DIR_VARIABLE = "HANDOVER_FEEDBACK_DIR"
SWITCH_FILE = "feedback.json"
JOURNAL_FILE = "journal.jsonl"
SKILL_DIR = Path(__file__).resolve().parent.parent
MANIFEST = SKILL_DIR.parent.parent / ".claude-plugin" / "plugin.json"
FORM_PATH = "/issues/new?template=handing-over-feedback.yml"
VERSION = re.compile(r"[0-9A-Za-z.+-]{1,24}")
CODE = re.compile(r"[A-Z][A-Z0-9-]{1,31}")
DAY = re.compile(r"\d{4}-\d{2}-\d{2}")
REPOSITORY = re.compile(r"[a-z][a-z0-9+.-]*://[^\s?#]+")
UNKNOWN_VERSION = "unknown"
TOP_CODES = 5

INTEGER = "integer"
BOOLEAN = "boolean"
CODES = "codes"
COLD_READ_COUNTS = ("questions", "answered", "partly", "unsupported", "missing", "unexplained", "dropped")
EXCHANGE_FORMS = ("text", "page")
EXCHANGE_OPENINGS = ("said-back", "accepted", "corrected", "none")
EXCHANGE_REPLIES = ("acted", "asked", "corrected")
# Each field is INTEGER, BOOLEAN, CODES or the tuple of the words it may hold; no field holds text.
SCHEMA: dict[str, dict[str, object]] = {
    "report": {"profile": ("operator", "client"), "errors": INTEGER, "warnings": INTEGER, "codes": CODES},
    "card": {"mode": ("hook", "file"), "outcome": ("passed", "form", "returned", "resent"),
             "questions": INTEGER, "candidates": INTEGER, "codes": CODES},
    "answer": {"count": INTEGER},
    "reader_find": {"found": BOOLEAN},
    "reader_add": {"holds": INTEGER, "lacks": INTEGER, "words": INTEGER, "barred": INTEGER,
                   "use": ("decide", "defend", "build", "know", "none"), "depth": ("mechanism", "change", "none"), "turns": INTEGER},
    "ledger_find": {"found": INTEGER},
    "ledger_add": {"kind": ("answer", "default", "closure")},
    "ledger_note": {},
    "ledger_supersede": {},
    "exchange_add": {"form": EXCHANGE_FORMS, "opening": EXCHANGE_OPENINGS, "reply": (*EXCHANGE_REPLIES, "none")},
    "exchange_note": {"reply": (*EXCHANGE_REPLIES, "none"), "asked": INTEGER},
    "cold_read": dict.fromkeys(COLD_READ_COUNTS, INTEGER),
    "page": {"outcome": ("built", "refused"), "sentences": INTEGER, "parts": INTEGER, "decisions": INTEGER,
             "look": INTEGER, "violations": INTEGER},
    "voice": {"backend": ("module", "command"), "outcome": ("written", "failed"), "sentences": INTEGER,
              "paragraphs": INTEGER, "seconds": INTEGER},
    "page_check": {"outcome": ("clean", "findings", "no_browser"), "parts": INTEGER, "findings": INTEGER, "shots": INTEGER},
}
HOLDS_LINE = "The journal holds counts and rule codes only: no text of a report or a question, no path and no name."


class SwitchError(Exception):
    """The directory of the journal cannot be written; the message names the file."""


# Files


def feedback_dir(environ: Mapping[str, str]) -> Path:
    """$HANDOVER_FEEDBACK_DIR, else the skill's directory under $XDG_STATE_HOME or $HOME/.local/state."""
    named = environ.get(DIR_VARIABLE)
    if named:
        return Path(named).expanduser()
    state = environ.get("XDG_STATE_HOME")
    home = Path(environ["HOME"]) if environ.get("HOME") else Path.home()
    return (Path(state) if state else home / ".local" / "state") / SKILL_NAME


def is_on(directory: Path) -> bool:
    """True only while the switch file holds exactly {"journal": true}."""
    try:
        data = json.loads((directory / SWITCH_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and data.keys() == {"journal"} and data["journal"] is True


def write_switch(directory: Path, *, on: bool) -> None:
    """Replace the switch file in one rename; raises SwitchError when the directory cannot be written."""
    path = directory / SWITCH_FILE
    try:
        directory.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(dir=directory, prefix=f".{SWITCH_FILE}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps({"journal": on}) + "\n")
            os.replace(temporary, path)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(temporary)
            raise
    except OSError as e:
        raise SwitchError(f"cannot write {path}: {e}") from e


def read_manifest(path: Path) -> dict:
    """The plugin's manifest as a JSON object; an empty one when it cannot be read."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def plugin_version(manifest: Mapping[str, object]) -> str:
    version = manifest.get("version")
    return version if isinstance(version, str) and VERSION.fullmatch(version) else UNKNOWN_VERSION


def feedback_address(manifest: Mapping[str, object]) -> str | None:
    """The address of the feedback form in the manifest's repository; None without a usable repository."""
    repository = manifest.get("repository")
    if not isinstance(repository, str) or not REPOSITORY.fullmatch(repository.strip()):
        return None
    return repository.strip().rstrip("/") + FORM_PATH


# The schema


def is_count(value: object, least: int) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= least


def valid_value(kind: object, value: object) -> bool:
    if kind == INTEGER:
        return is_count(value, 0)
    if kind == BOOLEAN:
        return isinstance(value, bool)
    if kind == CODES:
        return isinstance(value, dict) and all(
            isinstance(code, str) and CODE.fullmatch(code) and is_count(count, 1) for code, count in value.items()
        )
    return isinstance(kind, tuple) and isinstance(value, str) and value in kind


def checked_fields(event: object, fields: Mapping[str, object]) -> dict | None:
    """The fields in the schema's order when the event and every field lie in the schema; None otherwise."""
    schema = SCHEMA.get(event) if isinstance(event, str) else None
    if schema is None or not all(name in schema and valid_value(schema[name], value) for name, value in fields.items()):
        return None
    checked = {name: fields[name] for name in schema if name in fields}
    if CODES in checked:
        checked[CODES] = dict(sorted(checked[CODES].items()))
    return checked


def event_line(event: str, fields: Mapping[str, object], version: str, day: str) -> str | None:
    """The journal line of one event, or None when the event lies outside the schema."""
    checked = checked_fields(event, fields)
    if checked is None:
        return None
    return json.dumps({"day": day, "version": version, "event": event, **checked}) + "\n"


def parse_event(line: str) -> dict | None:
    """A journal line as an event when it is one record() could have written; None otherwise."""
    try:
        data = json.loads(line)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    day, version, event = data.pop("day", None), data.pop("version", None), data.pop("event", None)
    if not (isinstance(day, str) and DAY.fullmatch(day)):
        return None
    if not (isinstance(version, str) and VERSION.fullmatch(version)):
        return None
    checked = checked_fields(event, data)
    return None if checked is None else {"day": day, "version": version, "event": event, **checked}


# The journal


def append_line(path: Path, line: str) -> None:
    """Append one line with a single write to a file opened for appending, created with mode 0600."""
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0)
    fd = os.open(path, flags, 0o600)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def append_event(directory: Path, manifest: Path, event: str, fields: Mapping[str, object]) -> None:
    if not is_on(directory):
        return
    line = event_line(event, fields, plugin_version(read_manifest(manifest)), datetime.date.today().isoformat())
    if line is not None:
        append_line(directory / JOURNAL_FILE, line)


def record(event: str, **fields: object) -> None:
    """Append one event to the journal when the user turned it on; never raises, prints nothing."""
    try:
        append_event(feedback_dir(os.environ), MANIFEST, event, fields)
    except Exception:  # noqa: BLE001 - an isolation point: no fault of the journal may change a run of the calling script
        return


def read_events(directory: Path) -> list[dict]:
    """The events of the journal in file order; an absent or unreadable journal holds none."""
    try:
        text = (directory / JOURNAL_FILE).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    return [event for event in (parse_event(line) for line in text.splitlines() if line.strip()) if event is not None]


# The summary


def tally(counter: Counter, order: tuple[str, ...]) -> str:
    """'word count, ...' in the given order, words with a zero count left out."""
    return ", ".join(f"{word} {counter[word]}" for word in order if counter[word])


def top_codes(events: list[dict]) -> str:
    codes: Counter = Counter()
    for event in events:
        codes.update(event.get(CODES, {}))
    return ", ".join(f"{code} {count}" for code, count in sorted(codes.items(), key=lambda pair: (-pair[1], pair[0]))[:TOP_CODES])


def report_line(by: dict[str, list[dict]]) -> str | None:
    reports = by.get("report", [])
    if not reports:
        return None
    profiles = tally(Counter(r.get("profile") for r in reports), SCHEMA["report"]["profile"])
    clean = sum(1 for r in reports if r.get("errors") == 0)
    codes = top_codes(reports)
    return (f"reports checked: {len(reports)}" + (f" ({profiles})" if profiles else "")
            + f"; {clean} without an error" + (f"; most frequent codes: {codes}" if codes else ""))


def card_line(by: dict[str, list[dict]]) -> str | None:
    cards = by.get("card", [])
    if not cards:
        return None
    outcomes = Counter(c.get("outcome") for c in cards)
    codes = top_codes([c for c in cards if c.get("outcome") == "form"])
    return (f"question cards: {outcomes['passed']} passed, {outcomes['form']} returned for the form"
            + (f" ({codes})" if codes else "")
            + f", {outcomes['returned']} returned with earlier answers, {outcomes['resent']} sent again after a return")


def answer_line(by: dict[str, list[dict]]) -> str | None:
    answers = by.get("answer", [])
    return f"answers recorded: {sum(a.get('count', 0) for a in answers)}" if answers else None


def reader_line(by: dict[str, list[dict]]) -> str | None:
    finds, intakes = by.get("reader_find", []), by.get("reader_add", [])
    if not finds and not intakes:
        return None
    known = sum(1 for f in finds if f.get("found") is True)
    line = f"reader lookups: {known} known, {len(finds) - known} unknown; intakes recorded: {len(intakes)}"
    turns = Counter(i.get("turns") for i in intakes)
    by_turns = [f"{turns[n]} after {n} card(s)" for n in sorted(n for n in turns if n is not None)]
    if turns[None]:
        by_turns.append(f"{turns[None]} without a count of cards")
    depths = tally(Counter(i.get("depth") for i in intakes), SCHEMA["reader_add"]["depth"])
    details = [part for part in (", ".join(by_turns), f"depth: {depths}" if depths else "") if part]
    return line + (f" ({'; '.join(details)})" if details else "")


def exchange_line(by: dict[str, list[dict]]) -> str | None:
    """The exchanges added with their openings, and the first replies set by an add or a note.

    A reply that a later note sets again is counted twice, since the journal counts events;
    records.py exchange count gives the counts of records.
    """
    adds, notes = by.get("exchange_add", []), by.get("exchange_note", [])
    if not adds and not notes:
        return None
    openings = Counter(a.get("opening") for a in adds)
    replies = Counter(e.get("reply") for e in adds + notes)
    return (f"exchanges recorded: {len(adds)}; "
            f"opening {', '.join(f'{word} {openings[word]}' for word in EXCHANGE_OPENINGS)}; "
            f"first reply {', '.join(f'{word} {replies[word]}' for word in EXCHANGE_REPLIES)}")


def ledger_line(by: dict[str, list[dict]]) -> str | None:
    finds, adds = by.get("ledger_find", []), by.get("ledger_add", [])
    if not finds and not adds:
        return None
    found = sum(1 for f in finds if f.get("found", 0) > 0)
    kinds = Counter(a.get("kind") for a in adds)
    return (f"ledger: {len(finds)} lookup(s), {found} found a record; "
            f"{kinds['closure']} closure(s), {kinds['default']} default decision(s)")


def cold_read_line(by: dict[str, list[dict]]) -> str | None:
    reads = by.get("cold_read", [])
    if not reads:
        return None
    complete = sum(1 for r in reads if "questions" in r and r.get("answered") == r["questions"])
    return f"cold reads: {complete} with every question answered, {len(reads) - complete} left a gap"


def page_line(by: dict[str, list[dict]]) -> str | None:
    pages, voices, checks = by.get("page", []), by.get("voice", []), by.get("page_check", [])
    if not pages and not voices and not checks:
        return None
    built = Counter(p.get("outcome") for p in pages)
    written = [v for v in voices if v.get("outcome") == "written"]
    backends = Counter(v.get("backend") for v in written)
    failed = len(voices) - len(written)
    seconds = sum(v.get("seconds", 0) for v in written)
    checked = Counter(c.get("outcome") for c in checks)
    return (f"pages: {built['built']} built, {built['refused']} refused; "
            f"voiced: {backends['module']} by module, {backends['command']} by command"
            + (f", {failed} failed" if failed else "") + f"; {seconds} seconds of audio"
            + (f"; checked in a browser: {checked['clean']} clean, {checked['findings']} with findings, "
               f"{checked['no_browser']} without a browser" if checks else ""))


SUMMARY_LINES = (report_line, card_line, answer_line, reader_line, exchange_line, ledger_line, cold_read_line, page_line)


def summary_lines(events: list[dict], manifest: Mapping[str, object]) -> list[str]:
    """The summary, one string per line; it holds no date."""
    address = feedback_address(manifest)
    closing = [HOLDS_LINE, f"Paste this summary into the feedback form: {address}" if address
               else "Paste this summary into the feedback form of the plugin's repository."]
    if not events:
        return [f"{SKILL_NAME}: the usage journal holds no event.", *closing]
    versions = sorted({e["version"] for e in events})
    days = len({e["day"] for e in events})
    by: dict[str, list[dict]] = {}
    for event in events:
        by.setdefault(event["event"], []).append(event)
    lines = [f"{SKILL_NAME}: usage summary",
             f"plugin version{'s' if len(versions) > 1 else ''} {', '.join(versions)}; {days} day(s) with use; {len(events)} event(s)"]
    lines += [line for line in (build(by) for build in SUMMARY_LINES) if line]
    return lines + closing


# Command line


def main(argv: list[str] | None = None, environ: Mapping[str, str] | None = None, manifest: Path = MANIFEST) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=("status", "on", "off", "summary", "reset"))
    args = parser.parse_args(argv)
    directory = feedback_dir(os.environ if environ is None else environ)
    journal = directory / JOURNAL_FILE
    try:
        if args.command == "status":
            events = read_events(directory)
            print(f"the usage journal is {'on' if is_on(directory) else 'off'}")
            print(f"directory: {directory}")
            print(f"{len(events)} event(s) on {len({e['day'] for e in events})} day(s) with use")
        elif args.command == "on":
            write_switch(directory, on=True)
            print(f"The usage journal is on: each run of the skill's scripts adds one line of counts and rule codes, no text, to {journal}.")
            print("feedback.py summary prints what it holds; feedback.py off stops it.")
        elif args.command == "off":
            write_switch(directory, on=False)
            print(f"The usage journal is off: the scripts add nothing to {journal}, which holds {len(read_events(directory))} event(s); feedback.py reset deletes them.")
        elif args.command == "summary":
            for line in summary_lines(read_events(directory), read_manifest(manifest)):
                print(line)
        else:
            count = len(read_events(directory))
            try:
                journal.unlink(missing_ok=True)
            except OSError as e:
                raise SwitchError(f"cannot delete {journal}: {e}") from e
            print(f"removed {count} event(s) from {journal}; the journal stays {'on' if is_on(directory) else 'off'}")
    except SwitchError as e:
        print(f"feedback.py: {e}", file=sys.stderr)
        return 2
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
