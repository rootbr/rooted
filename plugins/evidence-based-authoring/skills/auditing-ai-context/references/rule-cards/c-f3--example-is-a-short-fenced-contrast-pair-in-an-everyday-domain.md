---
title: The example is a fenced contrast pair of at most about three lines in an everyday domain
rule_id: C-F3
applies_to_target: [kb-card]
check_kind: mechanical
severity_default: medium
---

# The example is a fenced contrast pair of at most about three lines in an everyday domain

## Thesis
The example block must be a fenced contrast pair of at most about three lines — a rejected-versus-accepted or input-action-output pairing — set in an everyday domain. It must not be drawn from a niche specific to the card's author or their organization.

## Rationale
A fenced, short contrast pair is machine-parseable and uniform across the corpus, so every card's example is read the same way. An everyday domain parses for any consumer regardless of background, whereas a niche example specific to the author's project forces the reader to first decode an unfamiliar setting before the contrast lands — defeating the example's purpose of making the rule immediately concrete.

## Example
```
rejected: a 12-line excerpt from the author's internal billing pipeline
accepted: bad: "Meeting hygiene" / good: "Split meetings over 90 minutes into two sessions"
```

## Limits
Covers the example's form — fenced, contrast-paired, short, everyday-domain. It does not judge whether the example correctly illustrates the thesis, which is a content matter. The three-line bound is approximate; a marginally longer pair that stays parseable and everyday is tolerable, a niche or unfenced block is not.

## Validator
Check the example block: is it fenced, a two-sided contrast pair (rejected/accepted or input/action/output), within about three lines, and set in an everyday domain rather than an author- or organization-specific niche? Flag any example failing one of these. Validator question: would any consumer parse this contrast without first decoding a specialized setting?

## Patch output
When auditing a card whose example is unfenced, overlong, not a contrast pair, or drawn from a niche domain, emit one patch (`rule_id: C-F3`, location of the example, severity medium) proposing a short fenced everyday-domain contrast pair. The form is mechanically decidable; set `needs_human: true` only when a faithful everyday replacement requires domain knowledge.

## Source
KB card spec, structural-consistency rules, group F (machine-parseable and uniform; an everyday domain parses for any consumer).
