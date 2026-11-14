#!/usr/bin/env python3
"""Grade a measurement of the cold read on reports with planted omissions.

    grade_cold_read.py PLANTS.json RUNS_DIR

PLANTS.json names, per case, the intact report, the questions and the variants, each a copy of
the report with one thing taken out; paths are relative to PLANTS.json:
    {"cases": [{"case": "<name>", "report_intact": "<path>", "questions": "<path>",
                "variants": [{"variant": "<name>", "report": "<path>", "removed": "<what was taken out>",
                              "expect": {"question": <n>, "terms": ["<keyword>", ...]}}]}]}
`expect` holds `question`, `terms` or both: the number, from 1, of the question the omission
should leave without an answer, and keywords of which one should occur in a kept unexplained
term. A variant without `expect`, an `expect` with neither key, a question number outside the
case's questions or an empty `terms` is malformed input.

RUNS_DIR holds the cold reader's answers per run: <case>--intact/cold.json and
<case>--<variant>/cold.json. Each run is checked by check_cold_read on its report and the case's
questions. A signal fires in a run:
  question <n>  the question of that number has a verdict other than answered
  terms         a keyword occurs, case ignored, in a kept unexplained term or its quote
Outcomes:
  caught         a variant where a signal of its expect fires and the same signal does not fire
                 in the intact run of its case
  not separated  a variant where a signal fires and each signal that fires also fires in the
                 intact run
  missed         a variant where no signal of its expect fires
  clean          an intact report whose check exits 0
  false alarm    an intact report whose check exits 1, with the questions not answered listed
  unusable       a run whose cold.json is absent or whose check exits 2; a variant is also
                 unusable when the intact run of its case is

Prints one line per run with the signal that decided it, then the summary: per variant name
across the cases caught, not separated and missed of planted; false alarms of intact reports;
unusable runs. Planted and intact count every run of their kind, the unusable ones included.
Writes the same to RUNS_DIR/grading.json.
Exit: 0 graded; 2 PLANTS.json or a questions file it names unreadable or malformed, or RUNS_DIR
not a directory.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import check_cold_read as cc  # noqa: E402

CAUGHT = "caught"
NOT_SEPARATED = "not separated"
MISSED = "missed"
CLEAN = "clean"
FALSE_ALARM = "false alarm"
UNUSABLE = "unusable"
TERMS = "terms"


class PlantsError(Exception):
    """PLANTS.json or a questions file it names cannot be read or does not have the documented shape."""


def _json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        raise PlantsError(f"cannot read {path}: {e}") from e


def _question_count(path: Path) -> int:
    questions = _json(path)
    questions = questions.get("questions") if isinstance(questions, dict) else None
    if not isinstance(questions, list):
        raise PlantsError(f"{path}: expected an object whose \"questions\" is a list")
    return len(questions)


def _expect(v: dict, count: int, where: str) -> dict:
    """The variant's expect, checked against the shape and the case's number of questions."""
    expect = v.get("expect")
    if not isinstance(expect, dict) or not ({"question", "terms"} & set(expect)):
        raise PlantsError(f"{where}: \"expect\" must be an object with \"question\", \"terms\" or both")
    out = {}
    if "question" in expect:
        n = expect["question"]
        if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= count:
            raise PlantsError(f"{where}: \"expect\".\"question\" is {n!r}, expected a number from 1 to {count}")
        out["question"] = n
    if "terms" in expect:
        terms = expect["terms"]
        if not isinstance(terms, list) or not terms or not all(isinstance(k, str) and k for k in terms):
            raise PlantsError(f"{where}: \"expect\".\"terms\" must be a non-empty list of non-empty strings")
        out["terms"] = terms
    return out


def load_plants(path: Path) -> list[dict]:
    """The cases of PLANTS.json with every path resolved against its directory; raises PlantsError."""
    data = _json(path)
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list):
        raise PlantsError(f"{path}: expected an object whose \"cases\" is a list")
    base = path.parent
    resolved = []
    for i, case in enumerate(cases, 1):
        where = f"{path}: case {i}"
        if not isinstance(case, dict) or not all(isinstance(case.get(k), str) for k in ("case", "report_intact", "questions")):
            raise PlantsError(f"{where}: expected the strings \"case\", \"report_intact\" and \"questions\"")
        variants = case.get("variants", [])
        if not isinstance(variants, list):
            raise PlantsError(f"{where}: \"variants\" is not a list")
        questions = base / case["questions"]
        count = _question_count(questions)
        out_variants = []
        for j, v in enumerate(variants, 1):
            vwhere = f"{where}, variant {j}"
            if not isinstance(v, dict) or not all(isinstance(v.get(k), str) for k in ("variant", "report")):
                raise PlantsError(f"{vwhere}: expected the strings \"variant\" and \"report\"")
            out_variants.append({"variant": v["variant"], "report": base / v["report"],
                                 "removed": str(v.get("removed", "")), "expect": _expect(v, count, vwhere)})
        resolved.append({"case": case["case"], "report_intact": base / case["report_intact"],
                         "questions": questions, "variants": out_variants})
    return resolved


def findings(result: dict) -> list[str]:
    """The lines of the check that flag something: every question not answered and every kept unexplained term."""
    lines = [cc.question_line(r) for r in result["questions"] if r["verdict"] != cc.ANSWERED]
    return lines + [cc.term_line("unexplained", t) for t in result["unexplained"]]


def fired(result: dict, expect: dict) -> dict[str, str]:
    """Each signal of expect that fires in the run's result, mapped to the evidence that fired it."""
    out = {}
    n = expect.get("question")
    if n is not None:
        row = result["questions"][n - 1]
        if row["verdict"] != cc.ANSWERED:
            out[f"question {n}"] = row["verdict"]
    keywords = [k.casefold() for k in expect.get("terms", [])]
    for t in result["unexplained"]:
        hit = next((k for k in keywords if k in t["term"].casefold()), None)
        if hit:
            out[TERMS] = f"{hit!r} in the kept term {t['term']!r}"
            break
        hit = next((k for k in keywords if k in t["quote"].casefold()), None)
        if hit:
            out[TERMS] = f"{hit!r} in the quote of the kept term {t['term']!r}"
            break
    return out


def check_run(runs_dir: Path, name: str, report: Path, questions: Path) -> tuple[int | None, dict | None, str]:
    """(exit code, result, why unusable) of one run; the exit code is None when cold.json is absent."""
    cold = runs_dir / name / "cold.json"
    if not cold.is_file():
        return None, None, f"no {cold}"
    try:
        result = cc.check_files(report, questions, cold)
    except cc.InputError as e:
        return 2, None, "; ".join(e.defects)
    return cc.exit_code(result), result, ""


def _record(name: str, variant: dict | None, code: int | None) -> dict:
    return {"run": name, "kind": "intact" if variant is None else "planted",
            "variant": None if variant is None else variant["variant"],
            "removed": None if variant is None else variant["removed"],
            "exit": code, "outcome": None, "signal": None, "detail": "", "findings": []}


def grade_intact(name: str, checked: tuple[int | None, dict | None, str]) -> dict:
    """The graded record of an intact run."""
    code, result, why = checked
    record = _record(name, None, code)
    if result is None:
        record.update(outcome=UNUSABLE, detail=why)
        return record
    not_answered = [cc.question_line(r) for r in result["questions"] if r["verdict"] != cc.ANSWERED]
    record.update(findings=findings(result), outcome=FALSE_ALARM if code == 1 else CLEAN)
    if not_answered:
        record["detail"] = " | ".join(not_answered)
    return record


def grade_variant(name: str, variant: dict, checked: tuple[int | None, dict | None, str], intact: tuple[int | None, dict | None, str]) -> dict:
    """The graded record of a planted run, compared with the intact run of its case."""
    code, result, why = checked
    record = _record(name, variant, code)
    if result is None:
        record.update(outcome=UNUSABLE, detail=why)
        return record
    record["findings"] = findings(result)
    if intact[1] is None:
        record.update(outcome=UNUSABLE, detail=f"the intact run is unusable: {intact[2]}")
        return record
    own = fired(result, variant["expect"])
    if not own:
        record.update(outcome=MISSED, detail=f"no signal of {variant['expect']} fired")
        return record
    in_intact = fired(intact[1], variant["expect"])
    separated = [s for s in own if s not in in_intact]
    if separated:
        signal = separated[0]
        record.update(outcome=CAUGHT, signal=signal, detail=own[signal])
    else:
        signal = next(iter(own))
        record.update(outcome=NOT_SEPARATED, signal=signal,
                      detail=f"{own[signal]}; in the intact run too: {in_intact[signal]}")
    return record


def grade(cases: list[dict], runs_dir: Path) -> dict:
    """Every run graded, with the summary."""
    runs = []
    for case in cases:
        name = f"{case['case']}--intact"
        intact = check_run(runs_dir, name, case["report_intact"], case["questions"])
        runs.append(grade_intact(name, intact))
        for v in case["variants"]:
            name = f"{case['case']}--{v['variant']}"
            runs.append(grade_variant(name, v, check_run(runs_dir, name, v["report"], case["questions"]), intact))
    variants: dict[str, dict[str, int]] = {}
    for r in runs:
        if r["kind"] == "planted":
            tally = variants.setdefault(r["variant"], {"caught": 0, "not_separated": 0, "missed": 0, "planted": 0})
            tally["planted"] += 1
            key = {CAUGHT: "caught", NOT_SEPARATED: "not_separated", MISSED: "missed"}.get(r["outcome"])
            if key:
                tally[key] += 1
    intact_runs = [r for r in runs if r["kind"] == "intact"]
    summary = {
        "variants": variants,
        "false_alarms": sum(1 for r in intact_runs if r["outcome"] == FALSE_ALARM),
        "intact": len(intact_runs),
        "unusable": sum(1 for r in runs if r["outcome"] == UNUSABLE),
        "runs": len(runs),
    }
    return {"runs": runs, "summary": summary}


def render(grading: dict) -> list[str]:
    """The printed lines: one per run, then the summary."""
    lines = []
    for r in grading["runs"]:
        line = f"{r['run']}: {r['outcome']}"
        if r["signal"]:
            line += f": {r['signal']}"
        if r["detail"]:
            line += f": {r['detail']}"
        lines.append(line)
    s = grading["summary"]
    lines += [f"{name}: {t['caught']} caught, {t['not_separated']} not separated, {t['missed']} missed of {t['planted']} planted"
              for name, t in s["variants"].items()]
    lines.append(f"false alarms: {s['false_alarms']} of {s['intact']} intact")
    lines.append(f"unusable: {s['unusable']} of {s['runs']} runs")
    return lines


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: grade_cold_read.py PLANTS.json RUNS_DIR", file=sys.stderr)
        return 2
    plants, runs_dir = Path(args[0]), Path(args[1])
    if not runs_dir.is_dir():
        print(f"not a directory: {runs_dir}", file=sys.stderr)
        return 2
    try:
        cases = load_plants(plants)
    except PlantsError as e:
        print(e, file=sys.stderr)
        return 2
    grading = grade(cases, runs_dir)
    for line in render(grading):
        print(line)
    (runs_dir / "grading.json").write_text(json.dumps(grading, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    cc.utf8_streams()
    sys.exit(main())
