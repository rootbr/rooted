---
title: A card slug must match the title's thesis, and rewriting the thesis requires realigning slug or title
rule_id: C-A2
applies_to_target: [kb-card, kb-corpus]
check_kind: mechanical
severity_default: high
---

# A card slug must match the title's thesis, and rewriting the thesis requires realigning slug or title

## Thesis
The filename slug must derive from the title's central claim. If the thesis is rewritten so that the slug no longer reflects it, either the title or the slug must be realigned so the two stay consistent.

## Rationale
The slug is the stable key referenced by every link pointing at the card. When the title's claim drifts away from the slug, the key now names one idea while the card states another — navigation lands on a card that no longer matches the reference, and link integrity silently rots.

## Example
```
rejected: slug: split-long-meetings  +  title: Cap recurring meetings at one per week
accepted: slug: split-long-meetings  +  title: Split any meeting longer than 90 minutes
```

## Limits
Covers alignment between the slug and the current title only. Whether the title itself is a well-formed declarative thesis is a separate concern. Cosmetic slug differences that still encode the same claim (word order, stop-word omission) are tolerable; a slug encoding a different claim is not.

## Validator
Compare the slug's kebab tokens against the title's central claim: do the content words of the slug correspond to the subject and action of the title? If the slug encodes a claim the title no longer makes → flag. Validator question: would a reader following a link by this slug arrive at a card whose title states the expected idea?

## Patch output
When auditing a card whose slug and title encode different claims, emit one patch (`rule_id: C-A2`, `location.field: slug`, severity high) proposing a realigned slug or title; set `needs_human: true` when renaming the slug would require relinking references the sub-agent cannot see.

## Source
KB card spec, identity/retrievability rules, group A (the slug is the stable key in every link; drift breaks navigation).
