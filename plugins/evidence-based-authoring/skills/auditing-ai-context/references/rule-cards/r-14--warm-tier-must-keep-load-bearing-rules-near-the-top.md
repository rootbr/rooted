---
title: A warm-tier file must keep load-bearing rules near the top
rule_id: R-14
applies_to_target: [skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# A warm-tier file must keep load-bearing rules near the top

## Thesis
Place safety rules, routing triggers, MUSTs, and "before any other step" instructions in the first ~30% of a SKILL.md or agent file. The ~30% figure is a working heuristic; the established direction is that retrieval accuracy is highest near the beginning of the input and decay compounds with input length. Counter-intuitively, shuffled or discrete content beats logically structured prose for reference material — structural coherence consistently hurts model performance.

## Rationale
Two phenomena combine. Positional decay: later content is weighted less by attention. Prose flow: narrative tends to bury load-bearing rules behind context-setting paragraphs, pushing them past the high-accuracy zone at the top.

## Example
```
bad:  three intro paragraphs, then "MUST run the safety check first"
good: top "## Quick Rules" block: "MUST run the safety check first"
```

## Limits
The ~30% threshold is a working heuristic, not a measured cutoff; the source reports the direction (earlier is better, decay compounds with length), not a percentage.

## Validator
For each MUST / SHALL / safety rule, record its line position and compute `position_pct = line / total_lines`. Any load-bearing rule with `position_pct > 0.30` is a candidate to flag.

## Patch output
When a load-bearing rule sits past ~30% of the file, emit one patch (`rule_id: R-14`, `location.position_pct` set, severity medium) proposing to hoist it into a top-of-file Quick Rules block while keeping the canonical body in its current section.

## Source
Hong 2025 (Context Rot): retrieval accuracy highest near input start, decay compounds with length; structural coherence hurts. Reports direction, not a percentage; ~30% is a working heuristic.
