---
title: A quantified claim must keep its number
rule_id: C-E3
applies_to_target: [kb-card]
check_kind: mechanical
severity_default: high
---

# A quantified claim must keep its number

## Thesis
When a claim is quantified in its source, the card must keep the number. Replacing the measured value with a qualitative gesture — "improves results", "much faster" — strips the load-bearing part of the claim.

## Rationale
The number is what makes a quantified claim falsifiable and weighable. "Cuts the failure rate" and "cuts the failure rate by 35%" are not equivalent: the first is an unfalsifiable gesture a consumer cannot act on with confidence or compare against alternatives, while the second states an effect that can be checked and traded off. De-quantifying discards exactly the information that gave the claim its force.

## Example
```
rejected: Splitting long meetings improves decision quality.
accepted: Splitting meetings over 90 minutes raises decision quality by 18% in trials.
```

## Limits
Applies to claims the source quantifies. A genuinely qualitative finding with no measured value in the source has no number to keep and is out of scope. Whether a retained number is faithful to the source's direction and conditions is a separate faithfulness concern.

## Validator
For each claim that asserts an effect, check whether a number is present where the source supplies one; flag a quantified claim reduced to a qualitative phrase. Validator question: did the source attach a measured value to this claim, and is that value still in the card?

## Patch output
When auditing a card whose quantified claim has been de-quantified, emit one patch (`rule_id: C-E3`, location of the claim, severity high) restoring the source's number. The presence or absence of the number is mechanically decidable, so no `needs_human` flag.

## Source
KB card spec, faithfulness rules, group E (a de-quantified claim is an unfalsifiable gesture).
