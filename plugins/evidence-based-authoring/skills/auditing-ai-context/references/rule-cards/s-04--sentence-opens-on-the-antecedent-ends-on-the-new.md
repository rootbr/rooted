---
title: A sentence opens on the antecedent the reader already holds and ends on the new element
rule_id: S-04
applies_to_target: [answer, doc]
check_kind: semantic
severity_default: low
---

# A sentence opens on the antecedent the reader already holds and ends on the new element

## Thesis
Inside a sentence, begin with the element the reader can already match to something held in memory, and place the new or emphasized element at the end.

## Rationale
A reader takes the given part of a sentence, searches memory for a matching antecedent, and attaches the new part to it. With no direct antecedent available, the reader has to build an inferential bridge first, and those extra steps cost time. Comprehension time was 835 ms with a direct antecedent against 1016 ms without — a 181 ms penalty (minF'(1,36) = 6.47, p < .025). The effect is not mere lexical repetition: a second experiment gave both conditions the repeated noun, and the gap survived at 137 ms (1031 ms against 1168 ms, minF'(1,23) = 15.7, p < .001).

## Example
```
bad:  We hired a plumber. A burst pipe under the sink is what he came for.
good: We hired a plumber. He came for a burst pipe under the sink.
```

## Limits
Governs order inside one sentence and says nothing about the order of paragraphs, sections, or a whole document — that is a different scale resting on different evidence. The measurements come from undergraduate readers on two-sentence pairs, timed as self-paced comprehension rather than as errors or retention, so transfer to an expert reading extended technical prose is an extrapolation. A sentence whose new element cannot move to the end without changing what it asserts keeps the order it has.

## Validator
For each sentence, identify the element recoverable from what precedes it and the element that is new. Flag a sentence that opens on the new element while the recoverable one arrives late, and a sentence whose emphasized element sits mid-way with given material trailing behind it. Validator question: does the sentence's first phrase attach to something the reader already holds, and does its last phrase carry what the reader does not?

## Patch output
When auditing prose whose sentence opens on new material or buries its emphasis mid-sentence, emit one patch (`rule_id: S-04`, `location` set to the heading and line hint, `current` = the sentence, severity low) proposing the given-first, new-last order. Deciding which element the reader already holds requires reading the surrounding text, so set `proposed: null` and `needs_human: true`.

## Source
Haviland & Clark 1974, *Journal of Verbal Learning and Verbal Behavior* 13:512–521, doi:10.1016/S0022-5371(74)80003-4 — Exp. I 835 vs 1016 ms (Δ181 ms, minF'(1,36) = 6.47, p < .025, n = 16); Exp. II with repetition controlled 1031 vs 1168 ms (Δ137 ms, minF'(1,23) = 15.7, p < .001, n = 10). Caveat: undergraduates, two-sentence pairs, comprehension-time measure — transfer to expert technical prose is an extrapolation.
