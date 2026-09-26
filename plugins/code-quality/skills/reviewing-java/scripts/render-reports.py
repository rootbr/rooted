#!/usr/bin/env python3
"""Render the two review reports from the workflow's verified findings.

Inputs:
  --verdicts review/verdicts.json   the workflow's `findings` array after Verify: each
                                    finding carries `verdict` and, for a rejected
                                    Critical or Major, a `ruling`
  --plan     review/plan.json       the inventory (diff, files, size) and the card index,
                                    whose paths supply each finding's one-line source
  --out      <path>                 the review report; the rejection report lands next to
                                    it with a `-rejections` suffix
  --title    <text>                 the report title (ticket id or branch)
  --passes   <text>                 one line naming the passes that ran (optional)
Writes exactly the two Markdown files; standard library only.

A finding reaches the review report when its verdict is confirmed, upgraded or
modified, or when a ruling restored it (`refuted`) or left it uncertain (flagged
for the author). A rejected or downgraded finding goes to the rejection report;
a downgraded finding also stays in the review report at its new severity when
that severity is still reported.
"""
import json
import os
import re
import sys

SEV_ORDER = {"critical": 0, "major": 1, "minor": 2, "suggestion": 3}


def source_line(card_path):
    """The first line of a card's ## Source block, as the one-line source pointer."""
    try:
        with open(card_path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError:
        return ""
    m = re.search(r"^## Source\n+(.+?)$", text, re.M)
    return m.group(1).strip() if m else ""


def final_severity(f):
    r = f.get("ruling") or {}
    v = f.get("verdict") or {}
    return (r.get("final_severity") or v.get("final_severity") or f.get("severity") or "minor").lower()


def disposition(f):
    """One of: report, flagged, rejected, downgraded."""
    r = f.get("ruling") or {}
    v = f.get("verdict") or {}
    verdict = (v.get("verdict") or "confirmed").lower()
    if r:
        ruling = (r.get("ruling") or "").lower()
        if ruling == "refuted":
            return "report"
        if ruling == "uncertain":
            return "flagged"
        return "rejected"
    if verdict == "rejected":
        return "rejected"
    if verdict == "downgraded":
        return "downgraded"
    return "report"


def body_of(f):
    c = (f.get("verdict") or {}).get("corrected_finding") or {}
    return {k: c.get(k) or f.get(k, "") for k in ("file", "symbol", "code", "problem", "fix", "rationale")}


def esc(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def render(findings, plan, title, passes):
    cards = {c["rule_id"]: c for c in plan.get("cards", [])}
    inv = plan.get("inventory", {})
    report, flagged, rejected, downgraded = [], [], [], []
    for f in findings:
        d = disposition(f)
        {"report": report, "flagged": flagged, "rejected": rejected, "downgraded": downgraded}[d].append(f)
    shown = report + [f for f in downgraded]
    shown.sort(key=lambda f: (SEV_ORDER.get(final_severity(f), 9), body_of(f)["file"]))
    counts = {s: sum(1 for f in shown if final_severity(f) == s) for s in SEV_ORDER}
    grave = [f for f in shown if final_severity(f) in ("critical", "major")]
    light = [f for f in shown if final_severity(f) in ("minor", "suggestion")]
    rec = "Block" if counts["critical"] else ("Merge with fixes" if counts["major"] else "Merge")

    out = [f"# {title} Review", "", "## Executive Summary",
           f"- Reviewed: `{inv.get('diff_ref', '?')}` — {inv.get('file_count', 0)} Java files ({inv.get('size_class') or 'n/a'}); "
           f"packages: {', '.join(sorted({f.get('package', '') for f in inv.get('files', [])} - {''})) or 'n/a'}",
           f"- Passes: {passes or default_passes(plan)}",
           f"- Findings: {len(shown)} ({counts['critical']} critical, {counts['major']} major, {counts['minor']} minor, {counts['suggestion']} suggestion)",
           f"- Verification: {len(findings)} raw findings → {len(report)} confirmed, {len(downgraded)} downgraded, {len(rejected)} rejected, {len(flagged)} flagged for the author",
           f"- Recommendation: {rec}", ""]

    out.append("## Critical & Major Findings")
    out.append("")
    if not grave:
        out.append("None.")
        out.append("")
    for f in grave:
        b = body_of(f)
        out += [f"### {f.get('id', f['rule_id'])}: {title_of(f, cards, plan)}",
                f"- **Severity**: {final_severity(f).capitalize()}" + (f" _(downgraded from {f.get('severity')})_" if f in downgraded else ""),
                f"- **Rule**: {rule_line(f, cards)}",
                f"- **Location**: `{b['file']}` · `{b['symbol']}`",
                "- **Code**:", "  ```java", indent(b["code"]), "  ```",
                f"- **Problem**: {b['problem']}",
                "- **Suggested fix**:", "  ```java", indent(b["fix"]), "  ```",
                f"- **Rationale**: {b['rationale']}"]
        note = (f.get("verdict") or {}).get("note")
        if note and (f.get("verdict") or {}).get("verdict") in ("modified", "upgraded", "downgraded"):
            out.append(f"- **Verifier note**: {note}")
        if f.get("also"):
            out.append(f"- **Also flagged by**: {', '.join(f['also'])}")
        out.append("")

    out += ["## Minor & Suggestions", "", "| # | Severity | Rule | Location | Finding | Suggested fix |", "|---|---|---|---|---|---|"]
    for f in light:
        b = body_of(f)
        out.append(f"| {f.get('id', f['rule_id'])} | {final_severity(f).capitalize()} | `{f['rule_id']}` | `{esc(b['file'])}` · `{esc(b['symbol'])}` | {esc(b['problem'])} | {esc(b['fix'])} |")
    if not light:
        out.append("| — | — | — | — | none | — |")
    out.append("")

    if flagged:
        out += ["## Needs the author's decision", "",
                "A skeptic rejected each of these, a second skeptic defended it, and the arbiter could not settle it from the evidence.", ""]
        for f in flagged:
            b = body_of(f)
            r = f.get("ruling") or {}
            out += [f"### {f.get('id', f['rule_id'])}: {title_of(f, cards, plan)}",
                    f"- **Severity**: {final_severity(f).capitalize()}",
                    f"- **Location**: `{b['file']}` · `{b['symbol']}`",
                    f"- **Problem**: {b['problem']}",
                    f"- **Rejection**: {(f.get('verdict') or {}).get('evidence', '')}",
                    f"- **Defense**: {(f.get('defense') or {}).get('evidence', '')}",
                    f"- **Arbiter**: {r.get('note', '')}", ""]

    rej = [f"# {title} — Rejection Report", "", "## Summary",
           f"- Raw findings submitted to verification: {len(findings)}",
           f"- Confirmed (in review report): {len(report)}",
           f"- Rejected: {len(rejected)}", f"- Downgraded: {len(downgraded)}",
           f"- Modified: {sum(1 for f in findings if (f.get('verdict') or {}).get('verdict') == 'modified')}",
           f"- Flagged for the author: {len(flagged)}", "", "## Rejected Findings", ""]
    if not rejected:
        rej.append("None.")
        rej.append("")
    for f in rejected:
        b = body_of(f)
        r = f.get("ruling") or {}
        rej += [f"### ~~{f.get('id', f['rule_id'])}: {title_of(f, cards, plan)}~~",
                f"- **Original severity**: {f.get('severity', '').capitalize()}",
                f"- **Rule**: `{f['rule_id']}`",
                f"- **Location**: `{b['file']}` · `{b['symbol']}`",
                f"- **Original finding**: {b['problem']}",
                "- **Verdict**: Rejected" + (" (upheld by the arbiter)" if r else ""),
                f"- **Evidence**: {(f.get('verdict') or {}).get('evidence', '')}"]
        if r:
            rej.append(f"- **Arbiter**: {r.get('evidence', '')} {r.get('note', '')}".rstrip())
        rej.append("")
    rej += ["## Downgraded Findings", ""]
    if not downgraded:
        rej.append("None.")
        rej.append("")
    for f in downgraded:
        v = f.get("verdict") or {}
        rej += [f"### {f.get('id', f['rule_id'])}: {title_of(f, cards, plan)} _({f.get('severity')} → {final_severity(f)})_",
                f"- **Original severity**: {f.get('severity', '').capitalize()}",
                f"- **Rule**: `{f['rule_id']}`",
                "- **Verdict**: Downgraded",
                f"- **Evidence**: {v.get('evidence', '')}", ""]
    return "\n".join(out), "\n".join(rej), out[2:9]


def default_passes(plan):
    return f"{len(plan.get('jobs', []))} card jobs and {len(plan.get('slices', []))} logic slices"


def title_of(f, cards, plan=None):
    c = cards.get(f["rule_id"])
    if c:
        return c["title"]
    for pc in ((plan or {}).get("project_cards") or {}).get("cards", []):
        if pc.get("rule_id") == f["rule_id"]:
            return pc.get("title", f["rule_id"])
    words = str(f.get("problem", "")).split()
    out = ""
    for w in words:
        if len(out) + len(w) + 1 > 72:
            return out + " …"
        out = (out + " " + w).strip()
    return out


def rule_line(f, cards):
    if f["rule_id"] in cards:
        return f"`{f['rule_id']}` — {source_line(cards[f['rule_id']]['path'])}"
    if f["rule_id"] == "LOGIC":
        return "`LOGIC` — logic and correctness pass (no card)"
    return f"`{f['rule_id']}` — project invariant from config.md"


def indent(code):
    return "\n".join("  " + l for l in str(code or "").split("\n"))


def main(argv):
    opts = {"verdicts": "review/verdicts.json", "plan": "review/plan.json", "out": None, "title": "Review", "passes": ""}
    i = 0
    while i < len(argv):
        k = argv[i][2:]
        if k not in opts:
            sys.exit(f"render-reports: unknown option {argv[i]}")
        opts[k] = argv[i + 1]
        i += 2
    if not opts["out"]:
        sys.exit("render-reports: --out is required")
    with open(opts["verdicts"], encoding="utf-8") as handle:
        data = json.load(handle)
    findings = data["findings"] if isinstance(data, dict) else data
    with open(opts["plan"], encoding="utf-8") as handle:
        plan = json.load(handle)
    report, rejections, summary = render(findings, plan, opts["title"], opts["passes"])
    root, ext = os.path.splitext(opts["out"])
    rej_path = f"{root}-rejections{ext or '.md'}"
    os.makedirs(os.path.dirname(os.path.abspath(opts["out"])), exist_ok=True)
    with open(opts["out"], "w", encoding="utf-8") as handle:
        handle.write(report + "\n")
    with open(rej_path, "w", encoding="utf-8") as handle:
        handle.write(rejections + "\n")
    print("\n".join(summary))
    print(f"\nReview report: {opts['out']}\nRejection report: {rej_path}")


if __name__ == "__main__":
    main(sys.argv[1:])
