#!/usr/bin/env python3
"""Grade every run of an iteration against the expectations of evals.json.

    grade.py <iteration-dir>

The eval directory eval-<id>-<name> names its eval; its runs sit in <config>/run-<n>/outputs/.

Writes <run-dir>/grading.json with expectations [{text, passed, evidence}] and a summary.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))
import check_report as cr  # noqa: E402
import check_question as cq  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
PY = sys.executable


def run_check(args):
    p = subprocess.run([PY, "-I", str(SKILL / "scripts" / "check_report.py"), *args], capture_output=True, text=True)
    return p.returncode, p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""


def items_of(text):
    return cr.list_items(text.splitlines())


def grade_client(out: Path):
    q = out / "questions.md"
    i = out / "internal.md"
    qt = q.read_text(encoding="utf-8") if q.exists() else ""
    it = i.read_text(encoding="utf-8") if i.exists() else ""
    rc, last = run_check(["--profile", "client", str(q)]) if q.exists() else (2, "questions.md missing")
    items = [x for x in items_of(qt) if x.section != "internal"]
    ends_ok = bool(items) and all(cr.strip_code(x.text).count("?") == 1 and cr.QUESTION_TAIL.sub("", cr.strip_code(x.text)).endswith("?") for x in items)
    body = qt.lower()
    def absent(pattern): return re.search(pattern, body, re.IGNORECASE) is None
    channel_items = [x for x in items if re.search(r"channel", x.text, re.IGNORECASE)]
    return [
        (rc == 0, f"exit {rc}: {last}"),
        (ends_ok, f"{len(items)} items; all end with one '?': {ends_ok}"),
        (absent(r"time ?zone|utc"), "no time-zone question" if absent(r"time ?zone|utc") else "time-zone question present"),
        (absent(r"version"), "no version question" if absent(r"version") else "version question present"),
        (absent(r"\bci\b|approv"), "CI/approval questions absent" if absent(r"\bci\b|approv") else "CI or approval question present"),
        (len(channel_items) == 1, f"{len(channel_items)} item(s) mention the channel"),
        (not any(re.search(r"\bts\b|timestamp", x.text, re.IGNORECASE) and "?" in x.text for x in items) and re.search(r"\bts\b|timestamp", it, re.IGNORECASE) is not None, f"ts asked as a question: {any(re.search(r'\\bts\\b|timestamp', x.text, re.IGNORECASE) and '?' in x.text for x in items)}; ts in internal: {re.search(r'\bts\b|timestamp', it, re.IGNORECASE) is not None}"),
        (re.search(r"closed|default|basis", it, re.IGNORECASE) is not None, "internal.md has closure/default/basis wording" if it else "internal.md missing"),
    ]


def grade_operator(out: Path):
    r = out / "report.md"
    rt = r.read_text(encoding="utf-8") if r.exists() else ""
    root = FIXTURES / "repo"
    rc, last = run_check(["--profile", "operator", "--root", str(root), str(r)]) if r.exists() else (2, "report.md missing")
    lines = rt.splitlines()
    head = [l.strip() for l, *_ in [(l,) for l in lines] if l.strip()][:15]
    labels = all(any(p.match(h) for h in head) for p in cr.FIRST_PAGE.values()) and any(cr.STATUS.match(h) for h in head)
    status_line = next((cr.STATUS.match(h).group("v") for h in head if cr.STATUS.match(h)), "")
    status_ok = re.match(r"(failed|findings)", status_line.lower()) is not None and "1" in status_line
    anchor_findings = cr.check_anchors(lines, root)
    anchors = [s for l in lines for s in cr.CODE_SPAN.findall(l) if cr.ANCHOR.match(s)]
    anchor_errors = [f for f in anchor_findings if f.level == cr.ERROR]
    fragment_warn = [f for f in anchor_findings if f.code == "ANCHOR-FRAGMENT"]
    anchors_ok = len(anchors) >= 2 and not anchor_errors and len(fragment_warn) < len(anchors)
    no_self = cr.SELF_REPORT.search(cr.strip_code(rt)) is None
    qitems = [x for x in items_of(rt) if x.section == "questions"]
    timeout_q = [x for x in qitems if re.search(r"250|400", x.text) and cr.strip_code(x.text).count("?") == 1 and cr.QUESTION_TAIL.sub("", cr.strip_code(x.text)).endswith("?")]
    not_done = re.search(r"jmh", rt, re.IGNORECASE) is not None and re.search(r"routing\.md|documentation", rt, re.IGNORECASE) is not None
    return [
        (rc == 0, f"exit {rc}: {last}"),
        (labels, f"first-page labels present: {labels}"),
        (status_ok, f"status line: {status_line!r}"),
        (anchors_ok, f"{len(anchors)} anchors, {len(anchor_errors)} errors, {len(fragment_warn)} fragment warnings"),
        (no_self, "no self-report phrase" if no_self else "self-report phrase present"),
        (len(timeout_q) == 1, f"{len(timeout_q)} question item(s) about 250/400 ending with one '?'"),
        (not_done, f"JMH and docs named as not done: {not_done}"),
    ]


def grade_question(out: Path):
    j = out / "question.json"
    m = out / "questions.md"
    mt = m.read_text(encoding="utf-8") if m.exists() else ""
    try:
        payload = json.loads(j.read_text(encoding="utf-8"))
        questions = cq.load(payload)
        problems = cq.problems(questions)
    except (OSError, ValueError) as e:
        questions, problems = [], [f"unreadable: {e}"]
    text = " ".join((q.get("question") or q.get("title") or "") for q in questions)
    about_legacy = re.search(r"legacy|table", text, re.IGNORECASE) is not None and re.search(r"limits\.yaml|resources", text, re.IGNORECASE) is None
    irreversible = re.search(r"irreversib", text + " " + " ".join(str(o.get("description", "")) for q in questions for o in (q.get("options") or [])), re.IGNORECASE) is not None
    default_rec = re.search(r"default", mt, re.IGNORECASE) is not None and "config/limits.yaml" in mt
    return [
        (not problems, "no problem" if not problems else "; ".join(problems)[:200]),
        (len(questions) == 1, f"{len(questions)} question(s)"),
        (about_legacy, f"question text: {text[:120]!r}"),
        (irreversible, f"irreversibility named: {irreversible}"),
        (default_rec, f"default with config/limits.yaml in questions.md: {default_rec}"),
        (mt.count("?") == 1, f"{mt.count('?')} question mark(s) in questions.md"),
    ]


GRADERS = {
    "client-question-list": grade_client,
    "operator-report-with-failing-build": grade_operator,
    "question-to-operator-with-default": grade_question,
}


def main():
    it = Path(sys.argv[1])
    evals = json.loads((Path(__file__).resolve().parent / "evals.json").read_text(encoding="utf-8"))
    expected = {e["name"]: e["expectations"] for e in evals["evals"]}
    for eval_dir in sorted(p for p in it.glob("eval-*") if p.is_dir()):
        name = eval_dir.name.split("-", 2)[2]
        for run_dir in sorted(p for cfg in eval_dir.iterdir() if cfg.is_dir() for p in cfg.glob("run-*")):
            out = run_dir / "outputs"
            results = GRADERS[name](out)
            expectations = [{"text": t, "passed": bool(ok), "evidence": ev} for t, (ok, ev) in zip(expected[name], results)]
            passed = sum(1 for e in expectations if e["passed"])
            grading = {"expectations": expectations, "summary": {"passed": passed, "failed": len(expectations) - passed, "total": len(expectations), "pass_rate": round(passed / len(expectations), 2)}}
            (run_dir / "grading.json").write_text(json.dumps(grading, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{eval_dir.name}/{run_dir.parent.name}/{run_dir.name}: {passed}/{len(expectations)}")


if __name__ == "__main__":
    main()
