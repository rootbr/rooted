---
title: A term the voice mispronounces is registered in the pronunciation lexicon rather than transliterated forever
rule_id: S-10
applies_to_target: [answer]
check_kind: semantic
severity_default: low
---

# A term the voice mispronounces is registered in the pronunciation lexicon rather than transliterated forever

## Thesis
When a speech engine says a term wrongly, register the term in the pronunciation lexicon that drives the engine. Respelling it inside the spoken text is a stopgap that holds only until the entry exists.

## Rationale
A lexicon is the mechanism the standard defines for this case: a Recommendation of 14 October 2008 specifies "a mapping between words (or short phrases), their written representations, and their pronunciations suitable for use by an ASR engine or a TTS engine", carries several written forms for one lexeme through multiple grapheme elements, and is "intended to be the standard format of the documents referenced by the `<lexicon>` element of SSML". The two repairs differ in where the fix lands and how long it lasts. A respelling fixes one occurrence, has to be repeated at every future one, and leaves the reader looking at a word that is not the term. A lexicon entry fixes every occurrence from then on and leaves the written form intact.

## Example
```
bad:  every spoken line respells the product name so the voice pronounces it right
good: the name stays written as it is; one lexicon entry fixes how it is said
```

## Limits
Covers a term whose spoken form is wrong, not the choice of term. A respelling is the correct move while no entry exists — the defect is a respelling that has become the permanent arrangement. Spotting a respelled term is a plain text match; which term is registered, and with which pronunciation, is the judgement this card asks for.

## Validator
Find terms respelled to steer the voice rather than written in their normal form. For each, check whether a lexicon entry backs it. Flag a respelling that recurs across turns with no entry behind it, and name the term that should be registered. Validator question: is this respelling a stopgap on the way to a lexicon entry, or the arrangement that has been left in place?

## Patch output
When auditing an answer that respells a term for the voice with no lexicon entry behind it, emit one patch (`rule_id: S-10`, `location` set to the line hint, `current` = the respelled term, severity low) proposing the written form plus a lexicon entry for it. Choosing the pronunciation to register is a judgement the answer alone does not decide, so set `proposed: null` and `needs_human: true`.

## Source
W3C Pronunciation Lexicon Specification (PLS) Version 1.0, W3C Recommendation, 14 October 2008 (<https://www.w3.org/TR/pronunciation-lexicon/>) — a lexicon maps words and short phrases from their written representations to pronunciations usable by an ASR or TTS engine; multiple `<grapheme>` orthographies per lexeme; the standard format for documents referenced by SSML's `<lexicon>` element.
