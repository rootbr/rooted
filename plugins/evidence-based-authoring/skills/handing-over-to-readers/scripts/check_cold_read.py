#!/usr/bin/env python3
"""Check a cold read of a report: count an answer only when the sentences it quotes stand in the report.

    check_cold_read.py --report REPORT.md --questions QUESTIONS.json --answers COLD.json
                       [--steps N] [--json]

Before a report with a decision goes to its reader, a fresh agent that saw nothing of the work
reads the report alone and answers the reader's questions from it (the cold read). Before the
whole page of an explanation is built, its first part is read cold alone, and the cold reader
also retells the mechanism step by step. Its answers and its steps are a model's output; this
check holds each one to the report's own text.

QUESTIONS.json, written by the author from his registry, holds the questions and never his
answers: {"questions": ["What was the task?", "How did it end?", ...], "retell": "<what to
retell>"}. "retell", a non-empty string, asks for a retelling; without it a retelling in
COLD.json is not read.

COLD.json, returned by the cold reader:
    {"answers": [{"question": "<a question of QUESTIONS.json, verbatim>",
                  "found": "yes" | "partly" | "no",
                  "answer": "<one sentence, from the text alone>",
                  "quotes": ["<a sentence copied from the report>"],
                  "missing": "<what the report would have to say; empty when found is yes>"}],
     "unexplained": [{"term": "<a thing the report uses without saying what it is>",
                      "quote": "<the sentence where it first appears>"}],
     "retelling": [{"step": "<one sentence>", "quotes": ["<a sentence of the report>"]}],
     "gaps": ["<what the report would have to say between two steps>"]}
"question" and "found" are required in an answer; "answer", "missing" (strings) and "quotes"
(a list of strings) default to empty; "unexplained" defaults to an empty list. When a retelling
is asked, "retelling" lists the steps in the report's order: "step" is a required non-empty
string, "quotes" (a list of strings) defaults to empty; "gaps" (a list of strings) defaults to
empty.

--steps N, a positive integer, is the number of steps of the author's own rule.

A quote stands when its normalised text occurs in the normalised report. Both sides are
normalised the same way: runs of white space become one space; curly quotes and apostrophes
become straight ones; dashes of every kind become a hyphen; the Markdown emphasis marks * and _
and backticks are dropped; case is ignored. A trailing period, question mark or ellipsis of the
quote is dropped as well. The report is searched whole, fenced blocks included. A quote that is
empty after normalisation never stands.

Verdict per question:
  answered     found is "yes" and at least one of its quotes stands in the report
  unsupported  found is "yes" or "partly" and none of its quotes stands (an answer that may
               come from the model's own knowledge)
  partly       found is "partly" with a quote that stands
  missing      found is "no"
A quote decides nothing by itself: the verdict needs "found" and a standing quote together.

Verdict per step of a retelling:
  stands       one of its quotes stands in the report
  unsupported  none of its quotes stands

An unexplained term is kept when its quote stands in the report; one whose quote does not stand
is listed apart as dropped. Unexplained terms and gaps are advisory: they are printed and change
no exit code.

Output, in the order of QUESTIONS.json, one line each:
    question <n>: <verdict>: <text>
where <text> is the cold answer for answered and unsupported, and what is missing for partly
and missing (the cold answer when the missing text is empty); then, when a retelling was asked,
    step <n>: <verdict>: <step>        for each step, in the retelling's order
    gap: <gap>                         for each gap
then
    unexplained: <term>: "<quote>"     for each kept term
    dropped: <term>: "<quote>"         for each dropped term
and the summary line `<a> of <n> questions answered from the text, <k> unexplained term(s)`,
which ends with `, <s> of <m> steps from the text` when a retelling was asked, and then with
`, <N> expected` when --steps N is given.
--json prints the same as one JSON object: "questions" (a list of {n, question, verdict,
answer, missing, quotes_found, quotes_absent}), "unexplained" and "dropped" (lists of {term,
quote}), "answered" and "total"; when a retelling was asked, also "retell", "steps" (a list of
{n, step, verdict, quotes_found, quotes_absent}), "gaps", "steps_standing", "steps_total" and
"steps_expected" (N, or null without --steps).

Exit: 0 every question answered and, when a retelling was asked, every step of a non-empty
retelling stands and, with --steps N, at least N steps stand; 1 otherwise; 2 an unreadable or
malformed input file, a "found" outside the three values, an answer to a question that
QUESTIONS.json does not hold, two answers to one question, a question repeated in
QUESTIONS.json, a question without an answer, or --steps without a "retell" — one line per
defect on stderr.

The script reads the three files named on its command line as UTF-8, never edits the report and
never judges its style, opens no network connection and uses the standard library alone. It
writes nothing but, with the usage journal of feedback.py turned on, one line of counts to that
journal on a run that checked: the number of questions, of each verdict and of the unexplained
and dropped terms.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ANSWERED = "answered"
UNSUPPORTED = "unsupported"
PARTLY = "partly"
MISSING = "missing"
STANDS = "stands"
FOUND_VALUES = ("yes", "partly", "no")

WHITE_SPACE = re.compile(r"\s+")
DROPPED_MARKS = str.maketrans("", "", "*_`")
# Single curly quotes, apostrophes and the prime; then their double forms.
QUOTE_MARKS = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u2032": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"', "\u2033": '"',
})
MINUS_SIGN = "\u2212"
TRAILING_MARK = re.compile("[\\s.?\u2026]+$")


class InputError(Exception):
    """The input files cannot be checked; `defects` holds one line per defect."""

    def __init__(self, defects: list[str]):
        super().__init__("; ".join(defects))
        self.defects = defects


def dash_to_hyphen(text: str) -> str:
    """Every dash punctuation character (Unicode category Pd) and the minus sign become '-'."""
    return "".join("-" if ch == MINUS_SIGN or unicodedata.category(ch) == "Pd" else ch for ch in text)


def normalise(text: str) -> str:
    """The form in which a quote and the report are compared; see the module docstring."""
    text = dash_to_hyphen(text.translate(QUOTE_MARKS)).translate(DROPPED_MARKS)
    return WHITE_SPACE.sub(" ", text).strip().casefold()


def normalise_quote(quote: str) -> str:
    """A quote's comparison form: normalised, then without its trailing period, question mark or ellipsis."""
    return TRAILING_MARK.sub("", normalise(quote))


def stands(quote: str, report_normalised: str) -> bool:
    """True when the quote, non-empty after normalisation, occurs in the already normalised report."""
    needle = normalise_quote(quote)
    return bool(needle) and needle in report_normalised


def split_quotes(quotes: list[str], report_normalised: str) -> tuple[list[str], list[str]]:
    """The quotes that stand in the already normalised report and those that do not, each in their order."""
    found = [q for q in quotes if stands(q, report_normalised)]
    return found, [q for q in quotes if q not in found]


def _string_field(item: dict, key: str, where: str, defects: list[str], required: bool = False) -> None:
    if key not in item:
        if required:
            defects.append(f"{where}: no \"{key}\"")
    elif not isinstance(item[key], str):
        defects.append(f"{where}: \"{key}\" is not a string")


def asks_retelling(questions_payload: object) -> bool:
    """Whether QUESTIONS.json carries "retell"; its form is checked by validate()."""
    return isinstance(questions_payload, dict) and "retell" in questions_payload


def _retelling_defects(questions_payload: dict, cold_payload: object) -> list[str]:
    """Every defect of "retell" and of the retelling it asks for, one line each."""
    defects: list[str] = []
    retell = questions_payload["retell"]
    if not (isinstance(retell, str) and retell.strip()):
        defects.append("questions: \"retell\" is not a non-empty string")
    retelling = cold_payload.get("retelling", []) if isinstance(cold_payload, dict) else []
    if not isinstance(retelling, list):
        defects.append("answers: \"retelling\" is not a list")
        retelling = []
    for i, entry in enumerate(retelling, 1):
        where = f"answers: retelling step {i}"
        if not isinstance(entry, dict):
            defects.append(f"{where}: not an object")
            continue
        _string_field(entry, "step", where, defects, required=True)
        if isinstance(entry.get("step"), str) and not entry["step"].strip():
            defects.append(f"{where}: \"step\" is empty")
        quotes = entry.get("quotes", [])
        if not isinstance(quotes, list) or not all(isinstance(s, str) for s in quotes):
            defects.append(f"{where}: \"quotes\" is not a list of strings")
    gaps = cold_payload.get("gaps", []) if isinstance(cold_payload, dict) else []
    if not isinstance(gaps, list) or not all(isinstance(g, str) for g in gaps):
        defects.append("answers: \"gaps\" is not a list of strings")
    return defects


def validate(questions_payload: object, cold_payload: object, required_steps: int | None = None) -> list[str]:
    """Every defect that makes the pair of payloads uncheckable with --steps `required_steps`, one line each; [] when
    they are well formed. The retelling is read only when QUESTIONS.json asks for one."""
    defects: list[str] = []
    questions = questions_payload.get("questions") if isinstance(questions_payload, dict) else None
    questions_ok = isinstance(questions, list) and all(isinstance(q, str) for q in questions)
    if not questions_ok:
        defects.append("questions: expected an object whose \"questions\" is a list of strings")
        questions = []
    seen: set[str] = set()
    for n, q in enumerate(questions, 1):
        if q in seen:
            defects.append(f"questions: question {n} repeats an earlier question: {q}")
        seen.add(q)

    answers = cold_payload.get("answers") if isinstance(cold_payload, dict) else None
    if not isinstance(answers, list):
        defects.append("answers: expected an object whose \"answers\" is a list")
        answers = []
    answered: set[str] = set()
    for i, a in enumerate(answers, 1):
        where = f"answers: answer {i}"
        if not isinstance(a, dict):
            defects.append(f"{where}: not an object")
            continue
        _string_field(a, "question", where, defects, required=True)
        for key in ("answer", "missing"):
            _string_field(a, key, where, defects)
        if "found" not in a:
            defects.append(f"{where}: no \"found\"")
        elif a["found"] not in FOUND_VALUES:
            defects.append(f"{where}: \"found\" is {a['found']!r}, expected one of {', '.join(FOUND_VALUES)}")
        quotes = a.get("quotes", [])
        if not isinstance(quotes, list) or not all(isinstance(s, str) for s in quotes):
            defects.append(f"{where}: \"quotes\" is not a list of strings")
        question = a.get("question")
        if questions_ok and isinstance(question, str):
            if question not in seen:
                defects.append(f"{where}: answers a question that QUESTIONS.json does not hold: {question}")
            elif question in answered:
                defects.append(f"{where}: a second answer to the question: {question}")
            answered.add(question)
    for n, q in enumerate(questions, 1):
        if q not in answered:
            defects.append(f"answers: question {n} has no answer: {q}")

    unexplained = cold_payload.get("unexplained", []) if isinstance(cold_payload, dict) else []
    if not isinstance(unexplained, list):
        defects.append("answers: \"unexplained\" is not a list")
        unexplained = []
    for i, u in enumerate(unexplained, 1):
        where = f"answers: unexplained term {i}"
        if not isinstance(u, dict):
            defects.append(f"{where}: not an object")
            continue
        _string_field(u, "term", where, defects, required=True)
        _string_field(u, "quote", where, defects, required=True)

    if asks_retelling(questions_payload):
        defects += _retelling_defects(questions_payload, cold_payload)
    elif required_steps is not None:
        defects.append("--steps: QUESTIONS.json holds no \"retell\", so no retelling is asked")
    return defects


def verdict(found: str, any_quote_stands: bool) -> str:
    """The verdict of one question from the cold reader's "found" and whether one of its quotes stands."""
    if found == "no":
        return MISSING
    if not any_quote_stands:
        return UNSUPPORTED
    return ANSWERED if found == "yes" else PARTLY


def evaluate(report: str, questions_payload: dict, cold_payload: dict, required_steps: int | None = None) -> dict:
    """The result object of --json for --steps `required_steps`; the payloads must have passed validate()."""
    haystack = normalise(report)
    by_question = {a["question"]: a for a in cold_payload["answers"]}
    rows = []
    for n, question in enumerate(questions_payload["questions"], 1):
        a = by_question[question]
        found, absent = split_quotes(a.get("quotes", []), haystack)
        rows.append({
            "n": n,
            "question": question,
            "verdict": verdict(a["found"], bool(found)),
            "answer": a.get("answer", ""),
            "missing": a.get("missing", ""),
            "quotes_found": found,
            "quotes_absent": absent,
        })
    kept, dropped = [], []
    for u in cold_payload.get("unexplained", []):
        term = {"term": u["term"], "quote": u["quote"]}
        (kept if stands(u["quote"], haystack) else dropped).append(term)
    result = {
        "questions": rows,
        "unexplained": kept,
        "dropped": dropped,
        "answered": sum(1 for r in rows if r["verdict"] == ANSWERED),
        "total": len(rows),
    }
    if asks_retelling(questions_payload):
        result.update(retelling_fields(questions_payload["retell"], cold_payload, haystack, required_steps))
    return result


def retelling_fields(retell: str, cold_payload: dict, report_normalised: str, required_steps: int | None) -> dict:
    """The fields of the result object that a retelling adds, each step held to the already normalised report, with
    `required_steps` as "steps_expected"."""
    steps = []
    for n, entry in enumerate(cold_payload.get("retelling", []), 1):
        found, absent = split_quotes(entry.get("quotes", []), report_normalised)
        steps.append({"n": n, "step": entry["step"], "verdict": STANDS if found else UNSUPPORTED,
                      "quotes_found": found, "quotes_absent": absent})
    return {
        "retell": retell,
        "steps": steps,
        "gaps": list(cold_payload.get("gaps", [])),
        "steps_standing": sum(1 for s in steps if s["verdict"] == STANDS),
        "steps_total": len(steps),
        "steps_expected": required_steps,
    }


def exit_code(result: dict) -> int:
    """0 when every question is answered and, when a retelling was asked, the retelling has steps, every one stands, and
    at least "steps_expected" of them stand; 1 otherwise. Unexplained terms and gaps are advisory and decide nothing."""
    if result["answered"] != result["total"]:
        return 1
    if "retell" in result:
        standing, total, expected = result["steps_standing"], result["steps_total"], result["steps_expected"]
        if not total or standing < total or (expected is not None and standing < expected):
            return 1
    return 0


def question_line(row: dict) -> str:
    text = row["answer"]
    if row["verdict"] in (PARTLY, MISSING) and row["missing"]:
        text = row["missing"]
    return f"question {row['n']}: {row['verdict']}: {text}"


def term_line(label: str, term: dict) -> str:
    return f"{label}: {term['term']}: \"{term['quote']}\""


def render(result: dict) -> list[str]:
    """The text output, one string per line."""
    lines = [question_line(r) for r in result["questions"]]
    summary = (f"{result['answered']} of {result['total']} questions answered from the text, "
               f"{len(result['unexplained'])} unexplained term(s)")
    if "retell" in result:
        lines += [f"step {s['n']}: {s['verdict']}: {s['step']}" for s in result["steps"]]
        lines += [f"gap: {gap}" for gap in result["gaps"]]
        summary += f", {result['steps_standing']} of {result['steps_total']} steps from the text"
        if result["steps_expected"] is not None:
            summary += f", {result['steps_expected']} expected"
    lines += [term_line("unexplained", t) for t in result["unexplained"]]
    lines += [term_line("dropped", t) for t in result["dropped"]]
    lines.append(summary)
    return lines


def _read_text(path: Path, label: str, defects: list[str]) -> str | None:
    """The file's UTF-8 text; None, with a defect appended, when it cannot be read."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        defects.append(f"{label}: cannot read {path}: {e}")
        return None


def _read_json(path: Path, label: str, defects: list[str]):
    """The file's parsed JSON; None, with a defect appended, when it cannot be read or parsed."""
    text = _read_text(path, label, defects)
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError as e:
        defects.append(f"{label}: {path} is not JSON: {e}")
        return None


def check_files(report: Path, questions: Path, answers: Path, required_steps: int | None = None) -> dict:
    """The result object for three files checked with --steps `required_steps`; raises InputError when any of them is
    unreadable or malformed, or when `required_steps` is given and QUESTIONS.json asks for no retelling."""
    defects: list[str] = []
    report_text = _read_text(report, "report", defects)
    questions_payload = _read_json(questions, "questions", defects)
    cold_payload = _read_json(answers, "answers", defects)
    if defects:
        raise InputError(defects)
    defects = validate(questions_payload, cold_payload, required_steps)
    if defects:
        raise InputError(defects)
    return evaluate(report_text, questions_payload, cold_payload, required_steps)


def step_count(value: str) -> int:
    count = int(value)
    if count < 1:
        raise argparse.ArgumentTypeError(f"{value} is not a positive number of steps")
    return count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--report", required=True, help="the report the cold reader read")
    parser.add_argument("--questions", required=True,
                        help="JSON: {\"questions\": [...]}, with \"retell\" when a retelling is asked")
    parser.add_argument("--answers", required=True, help="JSON: the cold reader's answers")
    parser.add_argument("--steps", type=step_count, metavar="N",
                        help="the number of steps of the author's own rule: fewer standing steps are exit 1; needs \"retell\"")
    parser.add_argument("--json", action="store_true", help="print one JSON object instead of lines")
    args = parser.parse_args(argv)
    try:
        result = check_files(Path(args.report), Path(args.questions), Path(args.answers), args.steps)
    except InputError as e:
        for defect in e.defects:
            print(defect, file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for line in render(result):
            print(line)
    verdicts = Counter(row["verdict"] for row in result["questions"])
    journal("cold_read", questions=result["total"], answered=verdicts[ANSWERED], partly=verdicts[PARTLY],
            unsupported=verdicts[UNSUPPORTED], missing=verdicts[MISSING],
            unexplained=len(result["unexplained"]), dropped=len(result["dropped"]))
    return exit_code(result)


def journal(event: str, **fields: object) -> None:
    """Add one line of counts to the usage journal of feedback.py beside this script, when the user turned it on."""
    try:
        here = str(Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        import feedback

        feedback.record(event, **fields)
    except Exception:  # noqa: BLE001 - an isolation point: a missing or broken feedback.py changes nothing in this run
        pass


def utf8_streams() -> None:
    """The standard streams carry UTF-8 on every platform; Python gives a pipe the system code page on Windows."""
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


if __name__ == "__main__":
    utf8_streams()
    sys.exit(main())
