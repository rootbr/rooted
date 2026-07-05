---
title: Every facet is filled from the store's taxonomy, and a plane-1 folder must equal a taxonomy value
rule_id: C-A3
applies_to_target: [kb-card, kb-corpus]
check_kind: mechanical
severity_default: high
---

# Every facet is filled from the store's taxonomy, and a plane-1 folder must equal a taxonomy value

## Thesis
Fill every facet field with a value drawn from the store's controlled taxonomy. Where cards are foldered by their primary filter facet, the folder name must itself be a valid value of that facet.

## Rationale
Facets are the retrieval index: the loader returns cards by matching facet values. A value not in the taxonomy — a typo, a synonym, an invented label — matches no query and makes the card invisible to the consumer, no matter how good its body. A folder that disagrees with the facet it represents produces the same blindness.

## Example
```
rejected: phase: [desígn]        # not a taxonomy value — loader never matches it
accepted: phase: [design]        # exact taxonomy value
```

## Limits
Covers facet values against the taxonomy and folder-to-facet agreement only. Whether the chosen facet is the semantically best fit is a judgement left to review; this check decides only membership in the allowed set.

## Validator
For each facet field, check every value for exact membership in the store's taxonomy file; flag any value not present. Where cards are foldered by the primary facet, check that the folder name is itself a taxonomy value and matches the card's facet. Validator question: can the loader return this card for the value it claims?

## Patch output
When auditing a card carrying a facet value absent from the taxonomy or a folder that disagrees with its facet, emit one patch (`rule_id: C-A3`, `location.field` = the facet, severity high) proposing the nearest valid taxonomy value; set `needs_human: true` when no taxonomy value clearly fits.

## Source
KB card spec, identity/retrievability rules, group A (facets are the retrieval index — a wrong facet makes the card invisible).
