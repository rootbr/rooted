---
title: Atomic does not mean short; keep the precondition, trade-off, and counter-example that make the thesis true
rule_id: C-B2
applies_to_target: [kb-card]
check_kind: semantic
severity_default: medium
---

# Atomic does not mean short; keep the precondition, trade-off, and counter-example that make the thesis true

## Thesis
A card being atomic does not mean it must be brief. Keep the precondition, the trade-off, and the counter-example that make the single thesis actually true — stripping them to shorten the card removes the qualifiers a consumer needs to apply it correctly.

## Rationale
Over-compression collapses accuracy. Bulk-rewriting an accumulated context into a short "essentials" summary dropped task accuracy from 66.7 to 57.1 — below the 63.7 no-context baseline — because each removed qualifier was a load-bearing condition. Minimal means the smallest set of high-signal tokens, which is not the same as the fewest tokens: a thesis shorn of its bounds reads cleaner but no longer holds.

## Example
```
rejected: Split long meetings.
accepted: Split any meeting over 90 minutes into two sessions — unless it is a single
          decision review, where one block preserves context.
```

## Limits
Covers under-specification from compression — a thesis missing the conditions that make it true. It does not license padding: detail that does not bound or qualify the single thesis is not protected and may itself be a second idea. The line is whether removing the text changes when the rule applies.

## Validator
Read the thesis and ask what conditions govern it: are the preconditions, trade-offs, and exceptions present, or has the card been compressed to a bare slogan that a consumer could misapply? Flag a thesis stripped of its load-bearing qualifiers. Validator question: can the consumer tell when this rule does and does not apply from what remains?

## Patch output
When auditing a card compressed below the qualifiers its thesis needs, emit one patch (`rule_id: C-B2`, severity medium) proposing restoration of the missing precondition, trade-off, or counter-example. Whether a qualifier is load-bearing is a judgement, so set `needs_human: true`.

## Source
KB card spec, atomicity rules, group B; ACE arXiv:2510.04618 (summary rewrite dropped accuracy 66.7 → 57.1, below the 63.7 no-context baseline); Anthropic (minimal does not necessarily mean short).
