---
title: One thesis per card; a second idea must be split into a linked pair
rule_id: C-B1
applies_to_target: [kb-card]
check_kind: semantic
severity_default: medium
---

# One thesis per card; a second idea must be split into a linked pair

## Thesis
A card carries exactly one thesis. When a second distinct idea accretes into the card, split it out into its own card and connect the two with a link rather than letting both share one file.

## Rationale
Atomicity is what makes a card reusable and linkable: a card that holds one idea and one idea only can be retrieved, cited, and composed wherever that single idea is needed. Two ideas in one file cannot be retrieved independently — a query for the second idea pulls in the first as noise, and neither can be linked to without dragging the other along.

## Example
```
rejected: one card stating both "split long meetings" and "circulate the agenda 24h ahead"
accepted: two cards — one per rule — linked to each other
```

## Limits
One idea does not mean a thin idea: the preconditions, trade-offs, and bounds that make the single thesis true belong with it and are not a second idea. The split applies only when a genuinely separable second claim has accreted — not to the supporting detail of the primary claim.

## Validator
Read the card for more than one independently-actable claim: could a consumer want one without the other, or cite one alone? If the card states two separable theses, flag it for splitting into a linked pair. Validator question: is there a single idea here, captured whole — or two ideas sharing a file?

## Patch output
When auditing a card carrying a second distinct thesis, emit one patch (`rule_id: C-B1`, severity medium) proposing the split into a linked pair. Deciding whether two claims are truly separable is a judgement, so set `needs_human: true`.

## Source
KB card spec, atomicity rules, group B; Zettelkasten / evergreen-notes principle (a note holds one idea only, capturing the entirety of that thing).
