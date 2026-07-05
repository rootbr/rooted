---
title: Identify the tier before applying any size rule; budget caps differ by tier
rule_id: R-10
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# Identify the tier before applying any size rule; budget caps differ by tier

## Thesis
Before applying any size rule, classify the file by tier. Hot-tier (`CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md`): ≤ 200 lines / ~2,000 tokens. Warm-tier (`SKILL.md`, per-task agents): ≤ 500 lines / ~5,000 tokens. Cold-tier (reference files, schemas): no hard cap, but each file > 100 lines MUST start with a table of contents because partial-read clients (`head -100`) only see the top.

## Rationale
Hot-tier files carrying conventions + architecture + project description showed −20.08% mean output tokens and −20.27% wall-clock. Ecosystem median SKILL.md is ~1.2k tokens (bundle ~1.8k) across 767k measured skills from a 2.01M-skill snapshot; 95% of 601 surveyed skills stay within the 500-line budget. Bigger is not better: measured Compact +19.0pp and Standard +21.5pp gains beat Detailed +14.5pp, while no-compression Comprehensive earns almost nothing (**+0.7pp**).

## Example
```
bad:  CLAUDE.md at 480 lines with full API schema inlined
good: CLAUDE.md ≤ 200 lines; schema moved to references/api.md
```

## Limits
Cold-tier files have no hard line cap; the only cold-tier obligation is a table of contents above 100 lines. The qualifying triple was the hot-tier study's inclusion criterion — partial triples were not measured.

## Validator
Inspect path and frontmatter. Path ends in `CLAUDE.md` / `AGENTS.md` / `copilot-instructions.md` → hot. Frontmatter has `name:` + `description:` and path matches `**/skills/<name>/SKILL.md` or `.claude/agents/<name>.md` → warm. Path under `references/`, `assets/`, `schemas/`, or referenced from a SKILL.md → cold. Then take the line and token counts from the Phase 0 inventory (`line_count`, `token_estimate`) and compare to the tier budget. Flag any tier over budget, or any cold file > 100 lines with no table of contents.

## Patch output
When a tier exceeds its budget, emit one patch (`rule_id: R-10`, `location.tier` set, `current` = line/token count, severity medium) proposing to move a specific section to a target file so the tier fits inside budget.

## Source
Lulla 2601.20404 (hot-tier triple, −20.08% tokens; Codex + gpt-5.2; triple was the inclusion criterion, partial triples untested). Li 2602.12670 v4 App. A.2 Fig. 7 (median ~1.2k tokens; 767k clones / 2.01M snapshot); Galster 2602.14690 §6.2 (95% within 500 lines); Li v4 §5.1.3 Finding 6 + App. F.2 Table 9 (Compact/Standard/Detailed/Comprehensive deltas).
