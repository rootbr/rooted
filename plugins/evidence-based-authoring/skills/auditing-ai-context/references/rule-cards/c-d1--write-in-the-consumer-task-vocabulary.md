---
title: A card is written in the consumer's task vocabulary, shaped to its sub-task, not to the source's structure
rule_id: C-D1
applies_to_target: [kb-card]
check_kind: semantic
severity_default: medium
---

# A card is written in the consumer's task vocabulary, shaped to its sub-task, not to the source's structure

## Thesis
A card must be written in the vocabulary of the consumer's task and shaped to the sub-task it serves — not in the terms or the sequence of the material it was distilled from. The card serves a job to be done, not a syllabus to be reproduced.

## Rationale
The runtime consumer retrieves a card to act in a specific situation, phrased in the language of that situation. A card that mirrors the source's structure and terminology forces the consumer to translate from explanatory prose into actionable terms at the moment of use — and the card may not even be retrieved, since its language matches the source's framing rather than the task's.

## Example
```
rejected: The chapter introduces, then defines, the concept of meeting duration.
accepted: When a meeting is scheduled for over 90 minutes, split it into two sessions.
```

## Limits
Covers orientation toward the consumer's task and language. It does not forbid technical vocabulary the consumer itself uses, nor demand that every card be a bare instruction. The line is whether the card is framed for the job at hand or for retelling the source.

## Validator
Read the card and ask whose frame it speaks in: the consumer doing the task, or the source explaining the topic? Flag a card organized as exposition — definitions before use, source ordering, source terminology — rather than around the consumer's situation. Validator question: does this read as something to act on, or as a passage to study?

## Patch output
When auditing a card written in the source's frame rather than the consumer's, emit one patch (`rule_id: C-D1`, severity medium) proposing a rewrite into the consumer's task vocabulary and sub-task framing. Judging the consumer-fit requires knowing the job, so set `needs_human: true`.

## Source
KB card spec, consumer-applicability rules, group D (the card serves a job, not a syllabus).
