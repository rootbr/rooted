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
card exits 0 silently; unreadable input exits 0 with the reason on stderr, so a parser failure
never blocks a question; an unreadable lexicon is reported on stderr and the check runs on the
English words.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

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
    "The question is outside the card form. A card opens with the fact and its decisive number, "
    "states what the answer changes and why the decision was not taken by default (irreversible, "
    "costly, or known only to the addressee), and ends with its one question; every option's "
    "description carries the consequence and the cost of being wrong. Reformulate the card, or take "
    "the reversible decision by default and record it."
)


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


def main(argv: list[str] | None = None) -> int:
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
            return 0
        for p in found:
            print(p, file=sys.stderr)
        print(GUIDANCE, file=sys.stderr)
        return 2
    for p in found:
        print(p)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
