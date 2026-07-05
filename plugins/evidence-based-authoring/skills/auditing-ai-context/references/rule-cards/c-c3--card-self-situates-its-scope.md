---
title: A card self-situates its scope through its applicability facet and a limits block
rule_id: C-C3
applies_to_target: [kb-card]
check_kind: semantic
severity_default: medium
---

# A card self-situates its scope through its applicability facet and a limits block

## Thesis
A card must state where it holds: the applicability facet plus a limits or counter-example block together fix the conditions under which the thesis applies and the conditions under which it does not. A card that asserts its claim with no stated scope invites misapplication.

## Rationale
Situating context is what lets a consumer judge whether a retrieved card fits the case at hand. Adding such context cuts the top-20 retrieval failure rate by 35% — 49% when combined with lexical matching, and 67% with reranking. Without it, a card retrieved for a superficially similar query is applied outside the situation it was written for, and the consumer has no signal to reject it.

## Example
```
rejected: Split long meetings into two sessions.
accepted: Split meetings over 90 minutes; applies_to recurring working sessions, not one-off
          decision reviews where a single block preserves context.
```

## Limits
Covers presence of self-situating scope — an applicability facet and a stated boundary. It does not judge whether the boundary is the empirically correct one, only that the card declares where it applies and where it stops rather than asserting a context-free absolute.

## Validator
Check that the card carries an applicability facet and a limits/counter-example block that name the conditions of use. Flag a card that states its thesis with no scope — no facet, no boundary. Validator question: does the card tell the consumer when it applies and when it does not, or leave that to be guessed?

## Patch output
When auditing a card with no self-situating scope, emit one patch (`rule_id: C-C3`, severity medium) proposing an applicability value and a limits boundary. Determining the correct scope requires judgement, so set `needs_human: true`.

## Source
KB card spec, self-containedness rules, group C; Anthropic Contextual Retrieval (situating context cuts top-20 retrieval failure 35%, 49% with lexical matching, 67% with reranking).
