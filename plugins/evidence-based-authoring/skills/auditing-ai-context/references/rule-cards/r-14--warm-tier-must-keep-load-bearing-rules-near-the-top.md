---
title: A warm-tier file must keep load-bearing rules near the top
rule_id: R-14
applies_to_target: [skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# A warm-tier file must keep load-bearing rules near the top

## Thesis
Place safety rules, routing triggers, MUSTs, and "before any other step" instructions in the first ~30% of a SKILL.md or agent file. The ~30% figure is a working heuristic; the measured direction is that, in a task of copying long input, a word is reproduced most accurately near the beginning, more so as input grows; needle retrieval showed no notable variation by position. Counter-intuitively, a needle is retrieved better from a shuffled haystack of filler than from a logically structured one; carrying that to reference material is house inference.

## Rationale
Two phenomena combine. Positional decay: later content is weighted less by attention. Prose flow: narrative tends to bury load-bearing rules behind context-setting paragraphs, pushing them past the high-accuracy zone at the top.

## Example
```
bad:  three intro paragraphs, then "MUST run the safety check first"
good: top "## Quick Rules" block: "MUST run the safety check first"
```

## Limits
The ~30% threshold is a working heuristic, not a measured cutoff; the measurements give a direction for copying input (earlier is better, more so with length), not a percentage, and none for retrieval.

## Validator
For each MUST / SHALL / safety rule, record its line position and compute `position_pct = line / total_lines`. Any load-bearing rule with `position_pct > 0.30` is a candidate to flag.

## Patch output
When a load-bearing rule sits past ~30% of the file, emit one patch (`rule_id: R-14`, `location.position_pct` set, severity medium) proposing to hoist it into a top-of-file Quick Rules block while keeping the canonical body in its current section.
