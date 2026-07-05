---
title: The thesis must be a single checkable claim
rule_id: C-B3
applies_to_target: [kb-card]
check_kind: semantic
severity_default: medium
---

# The thesis must be a single checkable claim

## Thesis
The card's thesis must be a single claim that can be checked — stated so that a reviewer or downstream verifier can decide whether it holds against its source. A vague aspiration or an unfalsifiable generality is not a thesis.

## Rationale
Checkability is the foundation for everything done to the card afterward: faithfulness review compares the thesis to its source, and downstream verification tests whether the consumer applied it correctly. Neither is possible if the claim cannot be pinned to a definite assertion — an uncheckable thesis cannot be confirmed, refuted, or verified in use.

## Example
```
rejected: Meetings should be run well.
accepted: A meeting longer than 90 minutes is split into two sessions with separate agendas.
```

## Limits
Covers whether the thesis is a definite, checkable assertion. It does not judge whether that assertion is true — entailment against the source is a separate concern — nor whether more than one claim is present, which is a separate atomicity matter.

## Validator
Read the thesis: could a reviewer state a concrete condition under which it would be false? If the claim is too vague to confirm or refute against its source, flag it. Validator question: is this one definite assertion a verifier could test, or an aspiration with no checkable content?

## Patch output
When auditing a card whose thesis is not a single checkable claim, emit one patch (`rule_id: C-B3`, severity medium) proposing a sharpened, falsifiable restatement. Judging checkability requires reading the claim against its intent, so set `needs_human: true`.

## Source
KB card spec, atomicity rules, group B (foundation for faithfulness checking and downstream verification).
