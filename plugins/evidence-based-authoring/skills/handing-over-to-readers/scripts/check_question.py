#!/usr/bin/env python3
"""Check an AskUserQuestion call against the card form of the reading contract.

    check_question.py < hook-input.json         the PreToolUse payload (.tool_input.questions)
    check_question.py --questions FILE.json     a JSON array of questions, or an object with
                                                "questions", or a whole hook payload
    check_question.py --hook < hook-input.json  the plugin hook on AskUserQuestion

A question that reaches the operator is one that passed the filters of rules 3–7: it could not
be answered from the files, it changes the work, and it was not decided by default. The card
makes those three facts visible, and this check holds the card to its form. Per question:

  ONE       exactly one question mark, and it closes the text (rule 19)
  FACT      a statement stands before the question: the fact and what the answer changes (2, 11, 17)
  WHY-ASKED the text says why the decision was not taken by default: irreversible, costly, or
            known only to the addressee (rule 6)
  OPTIONS   every option carries a description that states its consequence (rule 18)
  IDENT     no run, workflow or agent identifier in the card (rule 14)

The words WHY-ASKED matches are English; a lexicon adds those of another language: `--lexicon
FILE`, or the file `$XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json` when it exists — a
JSON object with a section per script: {"check_question": {"WHY_ASKED": [...extra regex alternatives...]}}.

Output without --hook: one problem per line on stdout. Exit: 0 pass; 1 problems; 2 unreadable
input or lexicon.

With --hook the exit codes follow the PreToolUse protocol, which blocks the call on exit 2 and
shows stderr to the model: the problems and then GUIDANCE go to stderr with exit 2; a passing
card goes on to the gate below; unreadable input exits 0 with the reason on stderr, so a parser
failure never blocks a question; an unreadable lexicon is reported on stderr and the check runs
on the English words.

The gate, with --hook only, runs on a card that passed the form check and looks for earlier
answers that may cover it. It needs the payload's session_id and the project's ledger of answers;
records.py beside this script resolves the ledger file and matches each question of the card,
its whole text, as `records.py ledger find` does. The match goes sentence against sentence: the
best overlap of the units of a sentence of the card with those of a sentence of a record's
question, divided by the unit count of the smaller sentence. A card carries the card form's own
sentences (the fact, what the answer changes, why it is asked) before its question, so a
whole-text share of a long card in a short record stays low however close the question is, and
two whole cards share the form's wording however unrelated they are. The ids of the records
already shown in a session stand in $XDG_STATE_HOME/handing-over-to-readers/gate/<session_id>.json
($HOME/.local/state when the variable is unset or empty). When a record found for the card is not
among them, the gate adds every record found for the card to that file, prints GATE_GUIDANCE and
the records on stderr and exits 2; when every one was shown before, the card passes. So a record
returns a card once in a session, however the question is reworded. Without a session_id or a
ledger file the card passes; a failure of the gate itself (an unreadable ledger, an unwritable
state file) lets the card pass with one line on stderr. The gate writes that state file alone.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Mapping

WORDS: dict[str, list[str]] = {
    "WHY_ASKED": ["irreversib", "reversib", "by default", r"cost of (?:an |the )?error", "only you", "you alone"],
}
LEXICON_FILE = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "handing-over-to-readers" / "lexicon.json"


LEXICON_SECTIONS = ("check_report", "check_question")
LEXICON_SECTION = "check_question"


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
    """Compile the language-bound pattern from WORDS plus the lexicon's alternatives."""
    global WHY_ASKED
    words = {k: v + (extra or {}).get(k, []) for k, v in WORDS.items()}
    try:
        WHY_ASKED = re.compile("(" + "|".join(words["WHY_ASKED"]) + ")", re.IGNORECASE)
    except re.error as e:
        raise ValueError(f"lexicon alternative is not a valid regex: {e}") from e


def apply_lexicon(path: str | None) -> None:
    """Rebuild the pattern with the named lexicon, or with the default file when it exists."""
    build_patterns(read_lexicon(Path(path) if path else LEXICON_FILE, required=bool(path)))


build_patterns()
IDENT = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b|\bwf_[a-z0-9-]{6,}\b|\ba[0-9a-f]{16}\b|\btoolu_[A-Za-z0-9]{8,}\b",
    re.IGNORECASE,
)
SENTENCE_BREAK = re.compile(r"[.;:!]\s+\S")
TAIL = re.compile(r"[\s*)»\"'\]_]+$")
MIN_DESCRIPTION = 15
GUIDANCE = (
    "The question is outside the card form. A card opens in plain words with what the matter is and "
    "one concrete instance of it, then gives the fact and its decisive number, "
    "states what the answer changes and why the decision was not taken by default (irreversible, "
    "costly, or known only to the addressee), and ends with its one question; every option's "
    "description carries the consequence and the cost of being wrong. Reformulate the card, or take "
    "the reversible decision by default and record it."
)
GATE_GUIDANCE = (
    "An earlier answer may cover this question. If one of the records below answers it, apply that "
    "answer, do not ask, and record that you applied it (records.py ledger add --kind closure ...). "
    "If none does, send the same card again: it passes."
)
SESSION_UNSAFE = re.compile(r"[^A-Za-z0-9._-]")


def problems(questions: list[dict]) -> list[str]:
    out: list[str] = []
    for n, q in enumerate(questions, 1):
        text = (q.get("question") or q.get("title") or "").strip()
        options = q.get("options") or []
        label = f"question {n}"
        if not text:
            out.append(f"{label}: no question text")
            continue
        marks = text.count("?")
        if marks == 0:
            out.append(f"{label} ONE: no question mark; a message is not a question (rule 19)")
        elif marks > 1:
            out.append(f"{label} ONE: {marks} question marks; one topic, one question, at the end (rules 8, 19)")
        elif not TAIL.sub("", text).endswith("?"):
            out.append(f"{label} ONE: the question is not the last sentence (rule 19)")
        if not SENTENCE_BREAK.search(text):
            out.append(f"{label} FACT: no statement before the question; open with the fact and what the answer changes (rules 2, 11, 17)")
        haystack = " ".join([text] + [str(o.get("description") or "") for o in options])
        if not WHY_ASKED.search(haystack):
            out.append(f"{label} WHY-ASKED: say why this is not decided by default: irreversible, costly, or known only to the addressee (rule 6)")
        for o in options:
            desc = str(o.get("description") or "").strip()
            if len(desc) < MIN_DESCRIPTION:
                out.append(f"{label} OPTIONS: option «{o.get('label', '?')}» without a consequence in its description (rule 18)")
        if IDENT.search(haystack):
            out.append(f"{label} IDENT: run, workflow or agent identifier in the card (rule 14)")
    return out


def load(payload) -> list[dict]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        if "questions" in payload:
            return payload["questions"] or []
        tool_input = payload.get("tool_input") or {}
        return tool_input.get("questions") or []
    return []


def gate_state_file(session_id: str, environ: Mapping[str, str]) -> Path:
    state = environ.get("XDG_STATE_HOME")
    base = Path(state) if state else (Path(environ["HOME"]) if environ.get("HOME") else Path.home()) / ".local" / "state"
    return base / "handing-over-to-readers" / "gate" / f"{SESSION_UNSAFE.sub('_', session_id)}.json"


def read_shown(path: Path) -> set[str]:
    """The record ids already shown in the session; a missing file holds none."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return set()
    if not isinstance(data, dict) or not isinstance(data.get("shown"), list):
        raise ValueError(f"{path}: expected an object with a list \"shown\"")
    return {str(x) for x in data["shown"]}


def gate(payload, environ: Mapping[str, str]) -> int:
    """Return a card once per session when an earlier answer may cover it; 2 blocks, 0 passes."""
    session_id = payload.get("session_id") if isinstance(payload, dict) else None
    if not isinstance(session_id, str) or not session_id.strip():
        return 0
    # The gate is an isolation point: any fault of its own, a defect included, lets the card pass,
    # because a hook that blocks on its own failure would stop every question the agent asks.
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import records

        ledger = records.ledger_path(None, None, environ)
        if not ledger.is_file():
            return 0
        entries = records.read_records(ledger)
        found: dict[str, tuple[float, dict]] = {}
        for q in load(payload):
            text = (q.get("question") or q.get("title") or "").strip() if isinstance(q, dict) else ""
            if not records.units(text):
                continue
            for score, record in records.find(records.LEDGER, text, entries):
                if score > found.get(record["id"], (-1.0, None))[0]:
                    found[record["id"]] = (score, record)
        if not found:
            return 0
        state = gate_state_file(session_id, environ)
        shown = read_shown(state)
        if set(found) <= shown:
            return 0
        records.write_text_atomic(state, json.dumps({"shown": sorted(shown | set(found))}) + "\n")
    except Exception as e:  # noqa: BLE001 - the isolation point above
        print(f"the ledger gate let the card pass: {type(e).__name__}: {e}", file=sys.stderr)
        return 0
    print(GATE_GUIDANCE, file=sys.stderr)
    for score, record in sorted(found.values(), key=lambda pair: -pair[0]):
        print(records.found_line(records.LEDGER, score, record), file=sys.stderr)
    return 2


def main(argv: list[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--questions", help="JSON file; default: the hook payload on stdin")
    parser.add_argument("--hook", action="store_true", help="PreToolUse exit codes: 2 blocks, stderr reaches the model")
    parser.add_argument("--lexicon", help=f"lexicon JSON, section {LEXICON_SECTION}: extra alternatives per key of WORDS; default: {LEXICON_FILE} when it exists")
    args = parser.parse_args(argv)
    try:
        apply_lexicon(args.lexicon)
    except ValueError as e:
        print(f"cannot read the lexicon: {e}", file=sys.stderr)
        if not args.hook:
            return 2
    try:
        raw = open(args.questions, encoding="utf-8").read() if args.questions else sys.stdin.read()
        payload = json.loads(raw)
    except (OSError, ValueError) as e:
        print(f"unreadable input: {e}", file=sys.stderr)
        return 0 if args.hook else 2
    found = problems(load(payload))
    if args.hook:
        if not found:
            return gate(payload, os.environ if environ is None else environ)
        for p in found:
            print(p, file=sys.stderr)
        print(GUIDANCE, file=sys.stderr)
        return 2
    for p in found:
        print(p)
    return 1 if found else 0


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
