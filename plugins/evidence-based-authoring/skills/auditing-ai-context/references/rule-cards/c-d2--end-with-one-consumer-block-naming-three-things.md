---
title: A card ends with exactly one consumer block naming the sub-task, the consumer, and the output field
rule_id: C-D2
applies_to_target: [kb-card]
check_kind: semantic
severity_default: medium
---

# A card ends with exactly one consumer block naming the sub-task, the consumer, and the output field

## Thesis
A card must end with exactly one consumer block that names three things: the sub-task — the precise situation where the card applies; the downstream consumer — which agent, skill, or tool acts on it; and the output — the concrete field or structure that consumer populates. This block is the bridge from a fact to its use.

## Rationale
Without this bridge a card is a passive fact: true, retrievable, but with no stated point of application. Naming the situation, the actor, and the artifact field tells the consumer when the card applies, who acts on it, and where the result goes — turning a proposition into something operable. A card that carries two such blocks is signalling that a second idea has accreted and should be split.

## Example
```
rejected: (card ends after the rationale, with no statement of use)
accepted: When scheduling a recurring meeting, the planning agent sets the agenda[] field
          to two sessions if duration exceeds 90 minutes.
```

## Limits
Covers presence and content of the single consumer block. The block's exact name and the prohibition on a second block under a different name are a separate structural matter. A card may state its application tersely; what it may not do is omit the situation, the actor, or the output field.

## Validator
Check that the card ends with one consumer block naming all three: the sub-task, the consumer, and the output field. Flag a card missing the block, missing one of the three elements, or carrying a second such block. Validator question: does the card say when it applies, who acts on it, and where the result is written?

## Patch output
When auditing a card whose consumer block is absent or incomplete, emit one patch (`rule_id: C-D2`, severity medium) proposing a block that names the sub-task, the consumer, and the output field. Identifying the correct three requires knowing the pipeline, so set `needs_human: true`.

## Source
KB card spec, consumer-applicability rules, group D (without this bridge the card is a passive fact; with it the consumer knows when, who, and where).
