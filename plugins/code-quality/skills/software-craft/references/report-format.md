# Report format

The two documents `scripts/render-reports.py` writes from `craft/verdicts.json` and `craft/plan.json`. Paths are relative to the repository under review.

### Document 1: Craft Review Report

Saved to the config's `review_output` (with `{TICKET_ID}` substituted) or `craft/craft-review-<task>.md`, where `<task>` is the ticket id, the branch, or `worktree` for an uncommitted diff. It holds confirmed, upgraded, modified and restored findings, plus downgraded findings at their new severity; findings an arbiter left `uncertain` sit in a separate section for the author. A build run adds the developer agent's report under "What was built".

```markdown
# <task> Craft Review

## Executive Summary
- Reviewed: <diff_ref> (<committed | worktree>) — N files (SIZE); languages: <language counts>
- Passes: N card jobs, M logic slices, K project invariants (fallback, if used)
- Findings: N (X major, Y minor, Z suggestion)
- Verification: N raw → M confirmed, D downgraded, K rejected, U flagged for the author
- Fix round: <F fixed, L left with their reason | none>
- Recommendation: Fix before merge / Merge with fixes / Merge

## What was built
(the developer agent's report: what changed by path:Symbol, cards applied, what was verified and how, what could not be verified, open questions)

## Major Findings

### <RULE>.<n>: <title>
- **Severity**: Major
- **Rule**: `<rule_id>` — <one-line source>
- **Location**: `path` · `symbol`
- **Code**: the flagged snippet, fenced in the file's language
- **Problem**: what is wrong and why it matters
- **Suggested fix**: corrected code in the file's language
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
# <task> — Rejection Report

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
