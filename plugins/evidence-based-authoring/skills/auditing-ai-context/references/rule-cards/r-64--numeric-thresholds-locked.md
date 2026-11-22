---
title: Numeric thresholds locked; constraint reconfiguration degrades more than rephrasing
rule_id: R-64
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# Numeric thresholds locked; constraint reconfiguration degrades more than rephrasing

## Thesis
Once a numeric threshold appears in a rule, every subsequent reference to the same threshold uses the same number.

## Rationale
Numeric edits ("at most 600" vs "610") can make many test cases fail, and constraint reconfiguration typically scores lower reliability than pure rephrasing does (90.4 against 88.7 for one frontier model), so a drifting threshold fractures the rule it governs; that the model treats the number as a hard constraint is house inference.

## Example
```
bad:  "Keep files ≤ 500 lines." … later … "Split anything over 600 lines."
good: "Keep files ≤ 500 lines." … later … "Split anything over 500 lines."
```

## Limits
Concerns repeated references to the same threshold; distinct thresholds that legitimately differ by referent are not in scope. The check is mechanical equality within a referent group, not a judgement about whether the chosen number is correct.

## Validator
Extract all numeric thresholds from the file and group them by referent. Within each group, every occurrence must match. If "≤ 500 lines" appears once and "≤ 600 lines" elsewhere for the same referent, flag the inconsistency and take the canonical mention as the source of truth.

## Patch output
When a threshold drifts across references to the same referent, emit one patch (`rule_id: R-64`, `location` set to the heading and line hint, `current` = the inconsistent number, severity medium) proposing the consistent number taken from the canonical mention.
