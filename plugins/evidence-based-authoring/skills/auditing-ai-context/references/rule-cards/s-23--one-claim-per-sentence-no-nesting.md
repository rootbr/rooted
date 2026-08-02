---
title: A spoken span carries one claim per sentence and no nesting
rule_id: S-23
applies_to_target: [answer]
check_kind: semantic
severity_default: low
---

# A spoken span carries one claim per sentence and no nesting

## Thesis
Each sentence of a spoken span states one claim and embeds no clause inside another. A second claim starts a second sentence; a relative clause that would sit between a subject and its verb is reordered so the sentence runs left to right.

## Rationale
An embedded clause forces the listener to hold the opening of a sentence unresolved while a second structure runs to completion — and unlike a reader, a listener cannot go back for the subject he is still holding. Heard sentences carrying one centre-embedded relative clause were answered less accurately than the same content with the clause resolved left to right, and the gap widened at fast speech, where the listener sets no pace. One claim per sentence follows the same constraint on open dependencies and is applied as a house default: no measurement of claims per spoken sentence was located.

## Example
```
bad:  The invoice, which the office sent on Monday, is due next week.
good: The office sent the invoice on Monday. It is due next week.
```

## Limits
The measured material is heard six-word sentences with a single centre-embedded relative clause, so the direction transfers to spoken prose of arbitrary length while the size of the effect does not — this rule carries no number. It also does not rest on speech being harder than text: across 46 studies and N = 4,687, "the overall difference between reading and listening comprehension was not reliably different (g = 0.07, p = 0.23)", with reading ahead only where the reader sets the pace and where the question requires inference. The one-claim-per-sentence half has no located measurement of its own and stands as a house default.

## Validator
For each sentence of the span, take the dependencies left open at its midpoint — a subject still waiting for its verb across an intervening clause is the flag case — and count the independently assertable claims. Flag a sentence that separates a subject from its verb with a clause, and flag a sentence that asserts a second claim after the first is already complete. Validator question: can this sentence be heard once, left to right, with nothing held open?

## Patch output
When auditing a span whose sentence nests a clause or carries a second claim, emit one patch (`rule_id: S-23`, `location.section` + `line_hint`, severity low) proposing the split into left-to-right sentences. Where a sentence's claims divide is a reading call, so set `proposed: null` and `needs_human: true`.

## Source
Peelle, Troiani, Wingfield & Grossman 2010, *Cerebral Cortex* 20(4):773–782, PMC2837088 — 40 adults, twenty aged 19–27 and twenty aged 60–77, heard six-word sentences with a centre-embedded relative clause; object-relative sentences were answered less accurately than subject-relative, worsening at fast speech. Backs the nesting half only, and transfers no number to prose of other lengths. Clinton-Lisell 2022, *Review of Educational Research* 92(4):543–582, doi:10.3102/00346543211060871 — 46 studies, N = 4,687, listening against reading g = 0.07 (p = .23, n.s.); bounds the rule against a general claim that speech is harder. One claim per sentence is a house default with no located source.
