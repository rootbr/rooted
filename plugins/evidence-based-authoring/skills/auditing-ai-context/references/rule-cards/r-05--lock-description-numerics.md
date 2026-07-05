---
title: Numeric thresholds in the description are locked or pushed into the body
rule_id: R-05
applies_to_target: [skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# Numeric thresholds in the description are locked or pushed into the body

## Thesis
Numbers in a description (line / token counts, percent thresholds, version cutoffs) act as hard pivots for the router. Either keep each number exact across every use, or remove it from the description and let the body govern it.

## Rationale
Numeric edits ("at most 600" vs "610") cause widespread routing-reliability failures — more than pure rephrasing — because the model treats numbers as hard constraints rather than approximations. A description that says "≤ 500 lines" can fail to trigger on a cousin prompt that asks for 510.

## Example
```
bad:  desc "Use for files ≤ 600 lines."   body "Audit any agent file regardless of length."
good: desc "Use for agent context files of any length."
```

## Limits
Concerns numbers in the `description` only. A number that is a true hard limit and is consistent with the body may stay. Numbers inside the body, where they can be qualified, are out of scope here. The source measured numeric-edit fragility on instruction following generally — applying it to the `description` field specifically is an authoring extrapolation, not a measured result.

## Validator
Extract every numeric value from the description. For each: is it the real hard threshold or a rough guideline, and does it match the body? A description number that contradicts the body, or a soft guideline frozen as a hard number, is the footgun → flag.

## Patch output
When auditing the `description` of a skill or agent-prompt, emit one patch (`rule_id: R-05`, `location.field: description`, severity medium) removing the number or aligning it with the body; set `needs_human: true` when deciding whether the number is a true limit needs author intent.

## Source
Dong 2512.14754 §3.1 (numeric edits and constraint reconfiguration degrade reliability more than pure rephrasing).
