# Report format

The two documents `scripts/render-reports.py` writes from `review/verdicts.json` and `review/plan.json`. Paths are relative to the repository under review.

### Document 1: Review Report

Saved to the config's `review_output` (with `{TICKET_ID}` substituted) or `review/java-review-<branch>.md`. It holds confirmed, upgraded, modified and restored findings, plus downgraded findings at their new severity; findings an arbiter left `uncertain` sit in a separate section for the author.

```markdown
# <TICKET_ID or branch> Review

## Executive Summary
- Reviewed: <diff_ref> — N Java files (SIZE); packages
- Passes: N card jobs, M logic slices, K project invariants (fallback, if used)
- Findings: N (X critical, Y major, Z minor, W suggestion)
- Verification: N raw → M confirmed, D downgraded, K rejected, U flagged for the author
- Recommendation: Block / Merge with fixes / Merge

## Critical & Major Findings

### <RULE>.<n>: <title>
- **Severity**: Critical / Major
- **Rule**: `<rule_id>` — <one-line source>
- **Location**: `File.java` · `Class#method`
- **Code**: the flagged snippet
- **Problem**: what is wrong and why it matters
- **Suggested fix**: corrected code
- **Rationale**: the mechanism

## Minor & Suggestions

| # | Severity | Rule | Location | Finding | Suggested fix |
|---|---|---|---|---|---|

## Needs the author's decision
(only when an arbiter ruled uncertain: both sides' evidence)
```

### Document 2: Rejection Report

Saved next to the review report with the `-rejections` suffix. Contents: every finding rejected or downgraded during verification, with the evidence the skeptic opened; a rejection an arbiter upheld carries the arbiter's evidence too.

```markdown
# <TICKET_ID or branch> — Rejection Report

## Summary
- Raw findings submitted to verification: N
- Confirmed (in review report): M
- Rejected: K · Downgraded: D · Modified: X · Flagged for the author: U

## Rejected Findings

### ~~<RULE>.<n>: <title>~~
- **Original severity**, **Rule**, **Location**, **Original finding**
- **Verdict**: Rejected
- **Evidence**: what was opened — a comment, a git log line, a project-context sentence, surrounding code

## Downgraded Findings

### <RULE>.<n>: <title> _(<original> → <new>)_
- **Verdict**: Downgraded
- **Evidence**: why the severity was too high
```

