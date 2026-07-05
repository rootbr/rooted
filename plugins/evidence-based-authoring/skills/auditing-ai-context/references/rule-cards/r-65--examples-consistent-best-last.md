---
title: Examples consistent in label and format; three excellent beats ten mediocre; place best last
rule_id: R-65
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: low
---

# Examples consistent in label and format; three excellent beats ten mediocre; place best last

## Thesis
Use 2–5 diverse examples; 3 excellent examples beat 10 mediocre ones. Place the most-relevant example last, and keep the label and format consistent across every example in a list.

## Rationale
Final examples carry 2–3× more influence on the model than earlier ones, so the most representative case belongs last. Inconsistent labels or formats across examples cut their effectiveness by up to 40%.

## Example
```
bad:  e.g. "fmt this", then bad:/good: pair, then the strongest case buried first
good: 3 bad:/good: pairs, identical labels, strongest case placed last
```

## Limits
The 2–3× influence and up-to-40% figures are vendor-grade guidance, not independently measured. The count band (2–5) and "best last" are heuristics on example lists; a single non-list illustration is not in scope.

## Validator
For each list of examples in the file: (1) count — if 1, propose adding one; if more than 5, propose pruning to the best 3–5; (2) check that all examples share one label/format (e.g. "bad:" / "good:") and standardize if not; (3) check that the most representative case appears last and reorder if not.

## Patch output
When an example list violates count, consistency, or ordering, emit one patch (`rule_id: R-65`, `location` set to the heading and line hint, `current` = the examples block, severity low) proposing the reordered, standardized, or pruned block.

## Source
Promptomatix §B.2.1 (final examples 2–3× influence; inconsistent label/format cuts effectiveness up to 40%). Appendix-B guidance ships without its own empirical citations — treat the figures as vendor-grade, not measured.
