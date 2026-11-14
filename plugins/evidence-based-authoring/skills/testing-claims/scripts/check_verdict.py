#!/usr/bin/env python3
"""Check the independent reader's verdict on one record against where each of the seven rules applies.

    check_verdict.py VERDICT.json        (- reads standard input)

The reader answers the seven check questions of references/method.md about one record and
returns one JSON object. references/record-format.md § The reader's verdict states the object,
the table of where each rule applies and what this script rejects:

    {"id": "H-03", "kind": "claim", "standing": "hypothesis",
     "answers": [{"rule": 1, "verdict": "holds", "quote": "...", "missing": ""}, ...]}

`quote` and `missing` are strings and default to empty; a value of white space alone is empty.
On a claim as hypothesis rules 3, 4, 5 and 6 take any of the three verdicts.

Findings, one line each as `<CODE>: <message>`, then the line `<n> finding(s)`:
  SHAPE    not an object; id, kind or answers absent; a claim without standing; kind or standing
           outside the vocabulary; answers not a list, or an answer not an object; a rule outside
           1-7, a rule of 1-7 absent or given twice; a verdict outside holds, fails and
           not-applicable; a quote or missing that is not a string
  QUOTE    holds without a non-empty quote
  MISSING  fails without a non-empty missing
  APPLY    not-applicable where the rule applies; holds or fails where it is not applicable
  FAILS    fails on a rule that may take it; the message carries the rule number and its missing

Exit: 0 no finding, so every applicable rule holds; 1 a finding; 2 unreadable input, input that
is not JSON, or wrong usage, with the message on stderr.

Privileges: reads the one file or standard input as UTF-8 and writes only to the standard
streams; opens no network connection; uses the standard library alone.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

KINDS = ("claim", "decision", "definition", "norm")
STANDINGS = ("contested", "hypothesis", "law", "refuted", "supported")
VERDICTS = ("holds", "fails", "not-applicable")
RULES = tuple(range(1, 8))
APPLIES = "applies"
NOT_APPLICABLE = "not applicable"
EITHER = "either"
PLANNED_TEST_RULES = (3, 4, 5, 6)


def applicability(kind: str, standing, rule: int) -> str | None:
    """APPLIES, NOT_APPLICABLE or EITHER, by the table of record-format.md; None when the standing is unknown."""
    if rule == 1:
        return APPLIES
    if kind in ("decision", "definition"):
        return NOT_APPLICABLE
    if kind == "norm":
        return APPLIES if rule == 4 else NOT_APPLICABLE
    if rule not in PLANNED_TEST_RULES:
        return APPLIES
    if standing == "hypothesis":
        return EITHER
    return APPLIES if standing in STANDINGS else None


def subject(kind: str, standing) -> str:
    return f"a claim as {standing}" if kind == "claim" else f"a {kind}"


def text_field(answer: dict, key: str, label: str, found: list) -> str:
    value = answer.get(key, "")
    if isinstance(value, str):
        return value
    found.append(("SHAPE", f"{label}: {key} is not a string"))
    return ""


def check(verdict) -> list[tuple[str, str]]:
    """Every finding of one verdict object, as (code, message), in the order of its answers."""
    if not isinstance(verdict, dict):
        return [("SHAPE", "the verdict is not a JSON object")]
    found: list[tuple[str, str]] = []
    for key in ("id", "kind", "answers"):
        if key not in verdict:
            found.append(("SHAPE", f"no {key}"))
    kind = verdict.get("kind")
    standing = verdict.get("standing")
    kind_known = kind in KINDS
    if "kind" in verdict and not kind_known:
        found.append(("SHAPE", f"kind {kind!r} is outside {', '.join(KINDS)}"))
    if kind == "claim" and "standing" not in verdict:
        found.append(("SHAPE", "a claim without standing"))
    if "standing" in verdict and standing not in STANDINGS:
        found.append(("SHAPE", f"standing {standing!r} is outside {', '.join(STANDINGS)}"))

    answers = verdict.get("answers")
    if "answers" in verdict and not isinstance(answers, list):
        found.append(("SHAPE", "answers is not a list"))
    if not isinstance(answers, list):
        return found

    seen: Counter = Counter()
    for n, answer in enumerate(answers, 1):
        if not isinstance(answer, dict):
            found.append(("SHAPE", f"answer {n} is not an object"))
            continue
        rule = answer.get("rule")
        rule_known = isinstance(rule, int) and not isinstance(rule, bool) and rule in RULES
        if rule_known:
            seen[rule] += 1
            label = f"rule {rule}"
        else:
            found.append(("SHAPE", f"answer {n}: rule {rule!r} is not one of 1-7"))
            label = f"answer {n}"
        value = answer.get("verdict")
        if value not in VERDICTS:
            found.append(("SHAPE", f"{label}: verdict {value!r} is outside {', '.join(VERDICTS)}"))
            continue
        quote = text_field(answer, "quote", label, found)
        missing = text_field(answer, "missing", label, found)
        if value == "holds" and not quote.strip():
            found.append(("QUOTE", f"{label} holds without a quote"))
        if value == "fails" and not missing.strip():
            found.append(("MISSING", f"{label} fails without missing"))
        scope = applicability(kind, standing, rule) if rule_known and kind_known else None
        if scope == APPLIES and value == "not-applicable":
            found.append(("APPLY", f"rule {rule} applies to {subject(kind, standing)}; not-applicable is rejected"))
        elif scope == NOT_APPLICABLE and value != "not-applicable":
            found.append(("APPLY", f"rule {rule} does not apply to {subject(kind, standing)}; {value} is rejected"))
        elif value == "fails":
            found.append(("FAILS", f"{label} fails: {missing.strip()}"))
    for rule in RULES:
        if seen[rule] == 0:
            found.append(("SHAPE", f"rule {rule} has no answer"))
        elif seen[rule] > 1:
            found.append(("SHAPE", f"rule {rule} is answered {seen[rule]} times"))
    return found


def read_input(name: str) -> str:
    if name == "-":
        return sys.stdin.read()
    return Path(name).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("verdict", metavar="VERDICT.json", help="the reader's verdict; - reads standard input")
    args = parser.parse_args(argv)
    try:
        payload = json.loads(read_input(args.verdict))
    except (OSError, UnicodeDecodeError) as e:
        print(f"cannot read {args.verdict}: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"{args.verdict} is not JSON: {e}", file=sys.stderr)
        return 2
    findings = check(payload)
    for code, message in findings:
        print(f"{code}: {message}")
    print(f"{len(findings)} finding(s)")
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
