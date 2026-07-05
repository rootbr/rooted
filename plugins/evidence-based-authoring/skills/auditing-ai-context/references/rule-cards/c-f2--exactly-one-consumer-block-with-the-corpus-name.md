---
title: A card carries exactly one consumer block, under the corpus's single chosen name
rule_id: C-F2
applies_to_target: [kb-card]
check_kind: mechanical
severity_default: medium
---

# A card carries exactly one consumer block, under the corpus's single chosen name

## Thesis
A card must carry exactly one consumer block, headed with the single name the corpus has chosen for that block. There must never be a second consumer block, and never the same block under a different name within the corpus.

## Rationale
Corpus consistency requires one block per card and one name per corpus: every card's application section is found at the same heading, so a consumer or tool can locate it by name across the whole store. A second consumer block also signals that a second idea has crept in, and a divergent heading name defeats the uniform lookup the single name exists to provide.

## Example
```
rejected: a card with both "## Skill application" and a second "## Usage" block
accepted: a single "## Skill application" block (the corpus's one chosen name)
```

## Limits
Covers the count of consumer blocks and the consistency of their heading name within the corpus. The internal content of the block — whether it names the situation, the consumer, and the output field — is a separate concern. The corpus may pick any single name; this check enforces that one name is used and used once per card.

## Validator
Count the consumer blocks in the card and check each heading against the corpus's chosen consumer-block name: flag a card with zero or more than one such block, or one whose heading deviates from the agreed name. Validator question: is there exactly one consumer block, under the corpus's single name?

## Patch output
When auditing a card with a duplicate or misnamed consumer block, emit one patch (`rule_id: C-F2`, location of the offending block, severity medium) consolidating to one block under the corpus's name. Count and heading match are mechanically decidable, so no `needs_human` flag.

## Source
KB card spec, structural-consistency rules, group F (one block per card, one name per corpus).
