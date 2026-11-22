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


# An option of a client's question, written as a bullet of its own: "- A. Keep one connection".
OPTION_BULLET = re.compile(r"^(?:\*\*)?[A-Za-z][.)](?:\*\*)?\s")


def client_items(text):
    """The items of a client's list outside the internal block, each option bullet read as part of the item above it."""
    items = []
    for x in items_of(text):
        if x.section == "internal":
            continue
        if items and OPTION_BULLET.match(x.text):
            items[-1].text += " " + x.text
        else:
            items.append(x)
    return items


def grade_client(out: Path):
    q = out / "questions.md"
    i = out / "internal.md"
    qt = q.read_text(encoding="utf-8") if q.exists() else ""
    it = i.read_text(encoding="utf-8") if i.exists() else ""
    rc, last = run_check(["--profile", "client", str(q)]) if q.exists() else (2, "questions.md missing")
    items = client_items(qt)
    ends_ok = bool(items) and all(cr.strip_code(x.text).count("?") == 1 and cr.QUESTION_TAIL.sub("", cr.strip_code(x.text)).endswith("?") for x in items)
    body = qt.lower()
    def absent(pattern): return re.search(pattern, body, re.IGNORECASE) is None
    # The client reads "channel" in his own words: a line, a link, a connection.
    channel_items = [x for x in items if re.search(r"\bchannel\b|second (network )?(line|link|connection)", x.text, re.IGNORECASE)]
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


def story_facts(out: Path, fixture: str):
    """What every report eval checks about the story form: (text of the story, the six graded pairs after the check's exit)."""
    r = out / "report.md"
    text = r.read_text(encoding="utf-8") if r.exists() else ""
    lines = text.splitlines()
    # The task names the fixture as fixtures/<name>, so a report anchors its lines from the fixture or from the directory above the fixtures.
    roots = [FIXTURES / fixture, FIXTURES.parent]
    root = min(roots, key=lambda candidate: sum(1 for f in cr.check_anchors(lines, candidate) if f.level == cr.ERROR))
    rc, last = run_check(["--profile", "operator", "--root", str(root), str(r)]) if r.exists() else (2, "report.md missing")
    codes = [f.code for f in cr.check(text, "operator", root)] if text else ["WHERE-TO-LOOK"]
    look = next((i for i, line in enumerate(lines) if cr.LOOK_HEADING.match(line)), len(lines))
    prose, headings, blocks, block = [], [], [], None
    for line in lines[:look]:
        if cr.FENCE.match(line):
            if block is None:
                block = []
            else:
                blocks.append(block)
                block = None
        elif block is not None:
            block.append(line)
        elif cr.HEADING.match(line):
            headings.append(cr.HEADING.match(line).group(1).strip())
        elif line.strip():
            prose.append(line.strip())
    story = cr.strip_code(" ".join(prose))
    sentences = cr.opening_sentences(lines) if text else 0
    anchor_findings = cr.check_anchors(lines, root)
    anchors = [span for line in lines for span in cr.CODE_SPAN.findall(line) if cr.ANCHOR.match(span)]
    anchor_errors = [f for f in anchor_findings if f.level == cr.ERROR]
    unproven = [f for f in anchor_findings if f.code == "ANCHOR-FRAGMENT"]
    asks_last = bool(prose) and cr.QUESTION_TAIL.sub("", cr.strip_code(prose[-1])).endswith("?")
    options = [b for b in blocks if any(l.startswith("+") for l in b) and any(l.startswith("-") for l in b)]
    short = [h for h in headings if 1 <= len(h.split()) <= 4]
    facts = [
        (rc == 0, f"exit {rc}: {last}"),
        (sentences >= cr.STORY_OPENING_SENTENCES, f"the opening has {sentences} sentence(s)"),
        (bool(text) and "STORY-SENTENCE" not in codes, f"{codes.count('STORY-SENTENCE')} line(s) with a sentence past {cr.STORY_SENTENCE_WORDS} words"),
        (len(anchors) >= 2 and not anchor_errors and len(unproven) < len(anchors), f"{len(anchors)} anchors, {len(anchor_errors)} errors, {len(unproven)} without their fragment on the line"),
        (story.count("?") == 1 and asks_last, f"{story.count('?')} question mark(s) in the story; the last prose line asks: {asks_last}"),
        (bool(options), f"{len(options)} fenced block(s) with a gain and a cost, of {len(blocks)} block(s)"),
        (len(headings) >= 2 and len(short) == len(headings), f"{len(headings)} heading(s) before the list, {len(short)} of one to four words"),
    ]
    return story, "\n".join(l for b in blocks for l in b), facts, codes


def said(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


def grade_operator(out: Path):
    story, _, facts, codes = story_facts(out, "repo")
    # "Two of the three tests pass" beside the exit code of the run is a checked claim; the check script warns only where no exit code stands in the list.
    no_self = "SELF-REPORT" not in codes and not said(r"\ball (the )?tests pass|build (is green|passes|succeeds)", story)
    both = said(r"\b250\b", story) and said(r"\b400\b", story)
    not_done = said(r"jmh|benchmark|speed|performance|latency|measur\w+|slows?\b", story) and said(r"routing|documentation|docs\b", story)
    return facts + [
        (bool(story) and no_self, "no claim that the tests pass without their exit code" if no_self else "a claim that the tests pass"),
        (both, f"250 and 400 both named in the story: {both}"),
        (not_done, f"JMH and the documentation named as not done: {not_done}"),
    ]


def grade_retry(out: Path):
    story, pictures, facts, _ = story_facts(out, "retry")
    failing = said(r"payment", story) and said(r"\bfail|\bred\b|\bbroke", story)
    delays = all(said(rf"\b{n}\b", pictures) for n in (200, 400, 800))
    twice = said(r"twice|again|more than once|second time|duplicate|repeat", story) and said(r"payment", story)
    return facts + [
        (failing, f"the payments team's failing test and the red build named: {failing}"),
        (delays, f"200, 400 and 800 inside a fenced picture: {delays}"),
        (twice, f"a payment reaching the gateway more than once is said: {twice}"),
    ]


def grade_rename(out: Path):
    story, pictures, facts, _ = story_facts(out, "rename")
    both = story + " " + pictures
    values = said(r"\b3[ ,.]?000\b|\b3 ?s\b|three seconds", both) and said(r"\b10[ ,.]?000\b|\b10 ?s\b|ten seconds", both)
    theirs = said(r"operations|\bops\b", story) and said(r"not (touch|edit|chang)|did not|didn't|left|untouched|theirs", story)
    return facts + [
        (values, f"3000 ms and 10000 ms (or 3 s and 10 s) both named: {values}"),
        (theirs, f"the deployment file named as the operations team's and unedited: {theirs}"),
    ]


def grade_logformat(out: Path):
    story, _, facts, _ = story_facts(out, "logformat")
    silent = said(r"alert", story) and said(r"no longer|stops?|silent|does not match|doesn't match|not match|misses|miss\b|never fires|will not fire|won't fire", story)
    unverified = said(r"sample", story) or said(r"not (been )?(built|run|verif)|did not (build|run|verif)|could not (build|run)|cannot (build|run)|unverified", story)
    return facts + [
        (silent, f"the alert no longer matching error lines is said: {silent}"),
        (unverified, f"what was not verified is said: {unverified}"),
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
    told = re.search(r"default|decided (it |this |that )?myself|i decided|i chose|i put|goes into", mt, re.IGNORECASE) is not None
    default_rec = told and re.search(r"\bconfig\b", mt, re.IGNORECASE) is not None and re.search(r"because|since|already|other (three )?config", mt, re.IGNORECASE) is not None
    return [
        (not problems, "no problem" if not problems else "; ".join(problems)[:200]),
        (len(questions) == 1, f"{len(questions)} question(s)"),
        (about_legacy, f"question text: {text[:120]!r}"),
        (irreversible, f"irreversibility named: {irreversible}"),
        (default_rec, f"the config location told as decided, with its basis: {default_rec}"),
        (mt.count("?") == 1, f"{mt.count('?')} question mark(s) in questions.md"),
    ]


GRADERS = {
    "client-question-list": grade_client,
    "operator-report-with-failing-build": grade_operator,
    "question-to-operator-with-default": grade_question,
    "operator-report-retry-and-another-teams-test": grade_retry,
    "operator-report-rename-and-a-stale-override": grade_rename,
    "operator-report-upgrade-that-silences-an-alert": grade_logformat,
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
            assert len(results) == len(expected[name]), f"{name}: {len(results)} graded facts for {len(expected[name])} expectations"
            expectations = [{"text": t, "passed": bool(ok), "evidence": ev} for t, (ok, ev) in zip(expected[name], results)]
            passed = sum(1 for e in expectations if e["passed"])
            grading = {"expectations": expectations, "summary": {"passed": passed, "failed": len(expectations) - passed, "total": len(expectations), "pass_rate": round(passed / len(expectations), 2)}}
            (run_dir / "grading.json").write_text(json.dumps(grading, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"{eval_dir.name}/{run_dir.parent.name}/{run_dir.name}: {passed}/{len(expectations)}")


if __name__ == "__main__":
    main()
