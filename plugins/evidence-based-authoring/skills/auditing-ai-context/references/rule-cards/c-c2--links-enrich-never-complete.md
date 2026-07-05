---
title: Links enrich a card but never complete it; the card must make sense with no link followed
rule_id: C-C2
applies_to_target: [kb-card]
check_kind: semantic
severity_default: medium
---

# Links enrich a card but never complete it; the card must make sense with no link followed

## Thesis
A card's links may add context, but the card must be fully intelligible and applicable without following any of them. No part of the thesis, rationale, or its application may depend on a linked card being read.

## Rationale
A card is retrieved in isolation; the consumer is never required to traverse a link to use it. If understanding the card requires opening a linked sibling, then the retrieved card alone is incomplete — the consumer that stops at it acts on a fragment. Links are an optional enrichment for when one card is not enough, not a continuation of the current one.

## Example
```
rejected: Apply the same 90-minute rule described in the linked card.
accepted: Split any meeting over 90 minutes; the linked card covers recurring-series cadence.
```

## Limits
Covers body-completeness against link dependence. It does not forbid links, nor require that every related idea be inlined — a card may point to siblings that bound or extend it. The line is whether the card's own claim stands without the link; enrichment is allowed, dependence is not.

## Validator
Read the body as if every link were unreachable: is the thesis still fully stated and applicable? Flag any card whose claim, rationale, or application is only completed by a linked sibling. Validator question: if no link is followed, does the consumer still have the whole idea?

## Patch output
When auditing a card whose body depends on a linked sibling, emit one patch (`rule_id: C-C2`, severity medium) proposing the missing content be inlined so the card stands alone. Judging whether the body is self-complete is a semantic call, so set `needs_human: true`.

## Source
KB card spec, self-containedness rules, group C (retrieved in isolation).
