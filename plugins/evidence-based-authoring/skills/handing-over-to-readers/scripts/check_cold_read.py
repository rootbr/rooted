#!/usr/bin/env python3
"""Check a cold read of a report: count an answer only when the sentences it quotes stand in the report.

    check_cold_read.py --report REPORT.md --questions QUESTIONS.json --answers COLD.json [--json]

Before a report with a decision goes to its reader, a fresh agent that saw nothing of the work
reads the report alone and answers the reader's questions from it (the cold read). Its answers
are a model's output; this check holds each one to the report's own text.

QUESTIONS.json, written by the author from his registry, holds the questions and never his
answers: {"questions": ["What was the task?", "How did it end?", ...]}.

COLD.json, returned by the cold reader:
    {"answers": [{"question": "<a question of QUESTIONS.json, verbatim>",
                  "found": "yes" | "partly" | "no",
                  "answer": "<one sentence, from the text alone>",
                  "quotes": ["<a sentence copied from the report>"],
                  "missing": "<what the report would have to say; empty when found is yes>"}],
     "unexplained": [{"term": "<a thing the report uses without saying what it is>",
                      "quote": "<the sentence where it first appears>"}]}
"question" and "found" are required in an answer; "answer", "missing" (strings) and "quotes"
(a list of strings) default to empty; "unexplained" defaults to an empty list.

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

An unexplained term is kept when its quote stands in the report; one whose quote does not stand
is listed apart as dropped. Unexplained terms are advisory: kept or dropped, they are printed and
change no exit code.

Output, in the order of QUESTIONS.json, one line each:
    question <n>: <verdict>: <text>
where <text> is the cold answer for answered and unsupported, and what is missing for partly
and missing (the cold answer when the missing text is empty); then
    unexplained: <term>: "<quote>"     for each kept term
    dropped: <term>: "<quote>"         for each dropped term
and the summary line `<a> of <n> questions answered from the text, <k> unexplained term(s)`.
--json prints the same as one JSON object: "questions" (a list of {n, question, verdict,
answer, missing, quotes_found, quotes_absent}), "unexplained" and "dropped" (lists of {term,
quote}), "answered" and "total".

Exit, from the questions alone: 0 every question answered; 1 otherwise; 2 an unreadable or
malformed input file, a "found" outside the three values, an answer to a question that
QUESTIONS.json does not hold, two answers to one question, a question repeated in
QUESTIONS.json, or a question without an answer — one line per defect on stderr.

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


def _string_field(item: dict, key: str, where: str, defects: list[str], required: bool = False) -> None:
    if key not in item:
        if required:
            defects.append(f"{where}: no \"{key}\"")
    elif not isinstance(item[key], str):
        defects.append(f"{where}: \"{key}\" is not a string")


def validate(questions_payload, cold_payload) -> list[str]:
    """Every defect that makes the pair of payloads uncheckable, one line each; [] when they are well formed."""
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
    return defects


def verdict(found: str, any_quote_stands: bool) -> str:
    """The verdict of one question from the cold reader's "found" and whether one of its quotes stands."""
    if found == "no":
        return MISSING
    if not any_quote_stands:
        return UNSUPPORTED
    return ANSWERED if found == "yes" else PARTLY


def evaluate(report: str, questions_payload: dict, cold_payload: dict) -> dict:
    """The result object of --json; the payloads must have passed validate()."""
    haystack = normalise(report)
    by_question = {a["question"]: a for a in cold_payload["answers"]}
    rows = []
    for n, question in enumerate(questions_payload["questions"], 1):
        a = by_question[question]
        quotes = a.get("quotes", [])
        found = [q for q in quotes if stands(q, haystack)]
        absent = [q for q in quotes if q not in found]
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
    return {
        "questions": rows,
        "unexplained": kept,
        "dropped": dropped,
        "answered": sum(1 for r in rows if r["verdict"] == ANSWERED),
        "total": len(rows),
    }


def exit_code(result: dict) -> int:
    """0 when every question is answered, 1 otherwise; unexplained terms are advisory and decide nothing."""
    return 0 if result["answered"] == result["total"] else 1


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
    lines += [term_line("unexplained", t) for t in result["unexplained"]]
    lines += [term_line("dropped", t) for t in result["dropped"]]
    lines.append(f"{result['answered']} of {result['total']} questions answered from the text, "
                 f"{len(result['unexplained'])} unexplained term(s)")
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


def check_files(report: Path, questions: Path, answers: Path) -> dict:
    """The result object for three files; raises InputError when any of them is unreadable or malformed."""
    defects: list[str] = []
    report_text = _read_text(report, "report", defects)
    questions_payload = _read_json(questions, "questions", defects)
    cold_payload = _read_json(answers, "answers", defects)
    if defects:
        raise InputError(defects)
    defects = validate(questions_payload, cold_payload)
    if defects:
        raise InputError(defects)
    return evaluate(report_text, questions_payload, cold_payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--report", required=True, help="the report the cold reader read")
    parser.add_argument("--questions", required=True, help="JSON: {\"questions\": [...]}")
    parser.add_argument("--answers", required=True, help="JSON: the cold reader's answers")
    parser.add_argument("--json", action="store_true", help="print one JSON object instead of lines")
    args = parser.parse_args(argv)
    try:
        result = check_files(Path(args.report), Path(args.questions), Path(args.answers))
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
