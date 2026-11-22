#!/usr/bin/env python3
"""Grade the retelling measurement: whether a cold reader who retells the steps catches a removed step
more often than one who answers the questions alone.

    grade_retelling.py PLANTS.json ITERATION_DIR

PLANTS.json names, per case, the intact first part of an explanation, the number of steps of its
mechanism and the variants, each a copy with one step taken out; paths are relative to PLANTS.json:
    {"cases": [{"case": "<name>", "report_intact": "<path>", "steps": <n>,
                "variants": [{"variant": "<name>", "report": "<path>", "removed": "<what was taken out>"}]}]}
"steps" is a positive integer; a case without it is malformed input. Beside PLANTS.json stand the
questions of the two arms: questions-retell.json, which must carry "retell", for the arm retell,
and questions.json, which must not, for the arm questions.

ITERATION_DIR holds the cold reader's answers per arm and round:
<arm>/round-<r>/<case>--intact/cold.json and <arm>/round-<r>/<case>--<variant>/cold.json, for the
arms retell and questions and every round-<r> directory, <r> from 1, that an arm holds. Each run is
checked by check_cold_read on its report and its arm's questions; in the arm retell the case's
steps are its --steps. A signal fires in a run:
  steps         arm retell: fewer steps stand than the case's steps, a step is unsupported, or the
                retelling is absent, which is when check_cold_read exits 1 on a retelling
  question <n>  arm questions: the question of that number has a verdict other than answered
The answers to the questions are no signal in the arm retell, and neither are the gaps a reader
lists: check_cold_read prints them and exits 0. They are counted apart, per arm retell the planted
and the intact runs whose answer lists a gap.
Outcomes, a planted run against the intact run of its case in the same arm and round:
  caught         a signal fires that does not fire in the intact run
  not separated  signals fire and each also fires in the intact run
  missed         no signal fires
  clean          an intact run where no signal fires
  false alarm    an intact run where a signal fires, with the signals named
  unusable       a run whose cold.json is absent or whose check exits 2; a planted run is also
                 unusable when the intact run of its case is

Prints one line per run with the signal that decided it, then per arm caught, not separated, missed
and unusable of planted and the false alarms of intact; planted and intact count every run of their
kind, the unusable ones included. Then the runs of the arm retell that list a gap, among its usable
planted and its usable intact runs. Then the caught share of each arm among its usable planted runs,
the difference of the two shares in percentage points and the one-sided Fisher exact p-value that
the arm retell catches more, the hypergeometric tail summed exactly; with an arm that has no usable
planted run the difference and the p-value are null. Writes the same to ITERATION_DIR/grading.json.
Exit: 0 graded; 2 PLANTS.json or a questions file beside it unreadable or malformed, ITERATION_DIR
not a directory, or an arm directory absent or without a round-<r> directory.
"""
from __future__ import annotations

import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import check_cold_read as cc  # noqa: E402

RETELL = "retell"
QUESTIONS = "questions"
ARMS = (RETELL, QUESTIONS)
QUESTIONS_FILE = {RETELL: "questions-retell.json", QUESTIONS: "questions.json"}
ROUND = re.compile(r"round-([1-9][0-9]*)")

CAUGHT = "caught"
NOT_SEPARATED = "not separated"
MISSED = "missed"
CLEAN = "clean"
FALSE_ALARM = "false alarm"
UNUSABLE = "unusable"
STEPS = "steps"


class GradingError(Exception):
    """PLANTS.json or a questions file beside it is unreadable or malformed, or ITERATION_DIR lacks an arm's rounds."""


def _json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        raise GradingError(f"cannot read {path}: {e}") from e


def load_cases(path: Path) -> list[dict]:
    """The cases of PLANTS.json with every path resolved against its directory; raises GradingError."""
    data = _json(path)
    cases = data.get("cases") if isinstance(data, dict) else None
    if not isinstance(cases, list):
        raise GradingError(f"{path}: expected an object whose \"cases\" is a list")
    base = path.parent
    resolved = []
    for i, case in enumerate(cases, 1):
        where = f"{path}: case {i}"
        if not isinstance(case, dict) or not all(isinstance(case.get(k), str) for k in ("case", "report_intact")):
            raise GradingError(f"{where}: expected the strings \"case\" and \"report_intact\"")
        steps = case.get("steps")
        if isinstance(steps, bool) or not isinstance(steps, int) or steps < 1:
            raise GradingError(f"{where}: \"steps\" is {steps!r}, expected a positive number of steps")
        variants = case.get("variants", [])
        if not isinstance(variants, list):
            raise GradingError(f"{where}: \"variants\" is not a list")
        out_variants = []
        for j, v in enumerate(variants, 1):
            if not isinstance(v, dict) or not all(isinstance(v.get(k), str) for k in ("variant", "report")):
                raise GradingError(f"{where}, variant {j}: expected the strings \"variant\" and \"report\"")
            out_variants.append({"variant": v["variant"], "report": base / v["report"], "removed": str(v.get("removed", ""))})
        resolved.append({"case": case["case"], "report_intact": base / case["report_intact"], "steps": steps,
                         "variants": out_variants})
    return resolved


def load_questions(base: Path) -> dict[str, Path]:
    """The questions file of each arm, beside PLANTS.json in `base`: the arm retell's carries a non-empty "retell", the
    arm questions' carries none; raises GradingError."""
    paths = {arm: base / name for arm, name in QUESTIONS_FILE.items()}
    for arm, path in paths.items():
        payload = _json(path)
        questions = payload.get("questions") if isinstance(payload, dict) else None
        if not isinstance(questions, list) or not all(isinstance(q, str) for q in questions):
            raise GradingError(f"{path}: expected an object whose \"questions\" is a list of strings")
        if arm == RETELL:
            retell = payload.get("retell")
            if not (isinstance(retell, str) and retell.strip()):
                raise GradingError(f"{path}: the arm {RETELL} needs \"retell\", a non-empty string")
        elif cc.asks_retelling(payload):
            raise GradingError(f"{path}: the arm {QUESTIONS} asks for no retelling, so \"retell\" must be absent")
    return paths


def find_rounds(arm_dir: Path) -> list[int]:
    """The numbers r of the round-<r> directories in `arm_dir`, ascending; raises GradingError when there is none."""
    try:
        names = [p.name for p in arm_dir.iterdir() if p.is_dir()] if arm_dir.is_dir() else []
    except OSError as e:
        raise GradingError(f"cannot list {arm_dir}: {e}") from e
    rounds = sorted(int(m.group(1)) for m in map(ROUND.fullmatch, names) if m)
    if not rounds:
        raise GradingError(f"no round-<r> directory in {arm_dir}")
    return rounds


def check_run(run_dir: Path, report: Path, questions: Path, steps: int | None) -> tuple[int | None, dict | None, str]:
    """(exit code, result, why unusable) of one run checked with --steps `steps`; the exit code is None when cold.json is
    absent."""
    cold = run_dir / "cold.json"
    if not cold.is_file():
        return None, None, f"no {cold}"
    try:
        result = cc.check_files(report, questions, cold, steps)
    except cc.InputError as e:
        return 2, None, "; ".join(e.defects)
    return cc.exit_code(result), result, ""


def signals(arm: str, result: dict) -> dict[str, str]:
    """Each signal of the arm that fires in a checked run, in a fixed order, mapped to the evidence that fired it."""
    if arm == QUESTIONS:
        return {f"question {r['n']}": r["verdict"] for r in result["questions"] if r["verdict"] != cc.ANSWERED}
    fired = {}
    standing, total, expected = result["steps_standing"], result["steps_total"], result["steps_expected"]
    if not total or standing < total or standing < expected:
        fired[STEPS] = f"{standing} of {total} steps stand, {expected} expected"
    return fired


def listed_gaps(arm: str, result: dict) -> list[str]:
    """The gaps the reader of a checked run lists; none in the arm questions, where no retelling is asked."""
    return list(result["gaps"]) if arm == RETELL else []


def _record(arm: str, round_no: int, case: str, variant: dict | None, code: int | None) -> dict:
    name = "intact" if variant is None else variant["variant"]
    return {"run": f"{arm}/round-{round_no}/{case}--{name}", "arm": arm, "round": round_no, "case": case,
            "kind": "intact" if variant is None else "planted",
            "variant": None if variant is None else variant["variant"],
            "removed": None if variant is None else variant["removed"],
            "exit": code, "outcome": None, "signal": None, "detail": "", "signals": {}, "gaps": []}


def grade_intact(record: dict, checked: tuple[int | None, dict | None, str]) -> dict:
    """`record`, the intact run's record from _record, filled in from its check and returned."""
    _, result, why = checked
    if result is None:
        record.update(outcome=UNUSABLE, detail=why)
        return record
    fired = signals(record["arm"], result)
    record.update(signals=fired, gaps=listed_gaps(record["arm"], result), outcome=FALSE_ALARM if fired else CLEAN,
                  detail=" | ".join(f"{name}: {evidence}" for name, evidence in fired.items()))
    return record


def grade_planted(record: dict, checked: tuple[int | None, dict | None, str], intact: dict) -> dict:
    """`record`, the planted run's record from _record, filled in from its check against `intact`, the graded intact run
    of its case, arm and round, and returned."""
    _, result, why = checked
    if result is None:
        record.update(outcome=UNUSABLE, detail=why)
        return record
    record["gaps"] = listed_gaps(record["arm"], result)
    if intact["outcome"] == UNUSABLE:
        record.update(outcome=UNUSABLE, detail=f"the intact run is unusable: {intact['detail']}")
        return record
    own = signals(record["arm"], result)
    record["signals"] = own
    if not own:
        record.update(outcome=MISSED, detail="no signal fired")
        return record
    in_intact = intact["signals"]
    separated = [name for name in own if name not in in_intact]
    if separated:
        signal = separated[0]
        record.update(outcome=CAUGHT, signal=signal, detail=own[signal])
    else:
        signal = next(iter(own))
        record.update(outcome=NOT_SEPARATED, signal=signal,
                      detail=f"{own[signal]}; in the intact run too: {in_intact[signal]}")
    return record


def fisher_one_sided(caught_first: int, runs_first: int, caught_second: int, runs_second: int) -> float:
    """The one-sided Fisher exact p-value that the first arm catches more: the probability, under the hypergeometric law
    of the 2x2 table with its margins fixed, that the first arm catches `caught_first` or more."""
    caught = caught_first + caught_second
    total = runs_first + runs_second
    tail = sum(math.comb(caught, k) * math.comb(total - caught, runs_first - k)
               for k in range(caught_first, min(caught, runs_first) + 1))
    return tail / math.comb(total, runs_first)


def _caught_share(tally: dict) -> dict:
    """The caught runs of an arm's tally, its usable planted runs and their quotient, None without a usable run."""
    usable = tally["planted"] - tally["unusable"]
    return {"caught": tally["caught"], "usable": usable, "share": tally["caught"] / usable if usable else None}


def compare(arms: dict[str, dict]) -> dict:
    """The caught share of each arm among its usable planted runs, their difference in points and the p-value that the
    arm retell catches more; the difference and the p-value are None when an arm has no usable planted run."""
    shares = {arm: _caught_share(arms[arm]) for arm in ARMS}
    comparison = {"caught_share": shares, "difference_points": None, "p_one_sided": None}
    retell, questions = shares[RETELL], shares[QUESTIONS]
    if retell["usable"] and questions["usable"]:
        comparison["difference_points"] = 100 * (retell["share"] - questions["share"])
        comparison["p_one_sided"] = fisher_one_sided(retell["caught"], retell["usable"], questions["caught"], questions["usable"])
    return comparison


def summarise(runs: list[dict]) -> dict:
    """Per arm the outcomes of the planted runs and the false alarms of the intact runs, the usable runs of each kind
    that list a gap, then the comparison."""
    arms = {}
    for arm in ARMS:
        of_kind = {kind: [r for r in runs if r["arm"] == arm and r["kind"] == kind] for kind in ("planted", "intact")}
        planted = [r["outcome"] for r in of_kind["planted"]]
        intact = [r["outcome"] for r in of_kind["intact"]]
        outcomes = Counter(planted)
        usable = {kind: [r for r in rows if r["outcome"] != UNUSABLE] for kind, rows in of_kind.items()}
        arms[arm] = {"caught": outcomes[CAUGHT], "not_separated": outcomes[NOT_SEPARATED], "missed": outcomes[MISSED],
                     "unusable": outcomes[UNUSABLE], "planted": len(planted),
                     "false_alarms": intact.count(FALSE_ALARM), "intact": len(intact),
                     "gaps_planted": sum(1 for r in usable["planted"] if r["gaps"]), "usable_planted": len(usable["planted"]),
                     "gaps_intact": sum(1 for r in usable["intact"] if r["gaps"]), "usable_intact": len(usable["intact"])}
    return {"arms": arms, "comparison": compare(arms)}


def grade(cases: list[dict], questions: dict[str, Path], iteration: Path, rounds: dict[str, list[int]]) -> dict:
    """Every run of every arm and round graded, with the summary."""
    runs = []
    for arm in ARMS:
        for round_no in rounds[arm]:
            round_dir = iteration / arm / f"round-{round_no}"
            for case in cases:
                steps = case["steps"] if arm == RETELL else None
                checked = check_run(round_dir / f"{case['case']}--intact", case["report_intact"], questions[arm], steps)
                intact = grade_intact(_record(arm, round_no, case["case"], None, checked[0]), checked)
                runs.append(intact)
                for v in case["variants"]:
                    checked = check_run(round_dir / f"{case['case']}--{v['variant']}", v["report"], questions[arm], steps)
                    runs.append(grade_planted(_record(arm, round_no, case["case"], v, checked[0]), checked, intact))
    return {"runs": runs, "summary": summarise(runs)}


def _share(tally: dict) -> str:
    text = f"{tally['caught']} of {tally['usable']}"
    return text if tally["share"] is None else f"{text} ({100 * tally['share']:.1f} %)"


def render(grading: dict) -> list[str]:
    """The printed lines: one per run, then one per arm, then the comparison."""
    lines = []
    for r in grading["runs"]:
        line = f"{r['run']}: {r['outcome']}"
        if r["signal"]:
            line += f": {r['signal']}"
        if r["detail"]:
            line += f": {r['detail']}"
        lines.append(line)
    summary = grading["summary"]
    for arm, t in summary["arms"].items():
        lines.append(f"{arm}: {t['caught']} caught, {t['not_separated']} not separated, {t['missed']} missed, "
                     f"{t['unusable']} unusable of {t['planted']} planted; {t['false_alarms']} false alarms of {t['intact']} intact")
    r = summary["arms"][RETELL]
    lines.append(f"{RETELL}: a gap listed in {r['gaps_planted']} of {r['usable_planted']} usable planted "
                 f"and {r['gaps_intact']} of {r['usable_intact']} usable intact")
    comparison = summary["comparison"]
    shares = comparison["caught_share"]
    line = f"caught of usable planted: {RETELL} {_share(shares[RETELL])}, {QUESTIONS} {_share(shares[QUESTIONS])}"
    if comparison["p_one_sided"] is None:
        lines.append(f"{line}; no comparison: an arm has no usable planted run")
    else:
        lines.append(f"{line}; difference {comparison['difference_points']:.1f} points; "
                     f"one-sided Fisher exact p = {comparison['p_one_sided']:.3g}")
    return lines


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        print("usage: grade_retelling.py PLANTS.json ITERATION_DIR", file=sys.stderr)
        return 2
    plants, iteration = Path(args[0]), Path(args[1])
    if not iteration.is_dir():
        print(f"not a directory: {iteration}", file=sys.stderr)
        return 2
    try:
        cases = load_cases(plants)
        questions = load_questions(plants.parent)
        rounds = {arm: find_rounds(iteration / arm) for arm in ARMS}
    except GradingError as e:
        print(e, file=sys.stderr)
        return 2
    grading = grade(cases, questions, iteration, rounds)
    for line in render(grading):
        print(line)
    (iteration / "grading.json").write_text(json.dumps(grading, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    cc.utf8_streams()
    sys.exit(main())
