---
title: No clause sits between a subject and its verb; an embedded clause is reordered left-to-right rather than shortened
rule_id: S-05
applies_to_target: [answer, doc, code]
check_kind: semantic
severity_default: low
---

# No clause sits between a subject and its verb; an embedded clause is reordered left-to-right rather than shortened

## Thesis
Keep a subject next to its verb. Where a clause has been embedded between them, move it out so the sentence runs left to right; shortening the sentence is not the repair.

## Rationale
Reading difficulty is indexed by the maximal number of incomplete syntactic dependencies the reader must hold open at one time, not by length: a worked series holds at most one open dependency in the easy case, three at the hard point of the next, and five in the third, and the third is the one judged most difficult to understand. The decisive demonstration keeps the words and the content identical and only fronts the clause so that it is no longer nested between the subject and the verb — the reordered sentence is easier. The mechanism also explains subject-verb adjacency directly: while the verb is still outstanding, the subject's dependency stays open and every intervening word is carried under it. Length is not an available substitute for this check — against reading ease measured by eye tracking, readability formulas, NLP-based methods, commercial systems and frontier language models are all poor predictors compared with the word properties psycholinguistics uses to predict reading times.

## Example
```
bad:  The invoice, which the supplier reissued after we queried the total, arrived.
good: The supplier reissued the invoice after we queried the total, and it arrived.
```

## Limits
Covers prose sentences, including those written inside comments and doc-comments, not the code beside them. The mechanism and its demonstration come from the incomplete-dependency account that the distance-based theory later refines, so the card carries neither integration-cost figures nor a nesting-depth threshold. No word count and no depth count decides the call — the question is how many dependencies stand open at the sentence's hardest point. A short embedded phrase the reader resolves immediately is not the target.

## Validator
For each sentence, check whether anything sits between the subject and its verb, and at the sentence's hardest point count the dependencies still open. Flag a sentence carrying material between subject and verb, and propose a reordering that moves the clause out rather than a cut. Validator question: does the reader carry an unresolved subject across intervening material before reaching the verb?

## Patch output
When auditing prose that embeds a clause between a subject and its verb, emit one patch (`rule_id: S-05`, `location` set to the heading and line hint, `current` = the sentence, severity low) proposing the left-to-right reordering. Judging where the peak of open dependencies falls, and which reordering preserves the claim, is a semantic call, so set `proposed: null` and `needs_human: true`.

## Source
Gibson 2000, *The Dependency Locality Theory: A Distance-Based Theory of Linguistic Complexity*, in *Image, Language, Brain* (MIT Press) pp. 95–126, §5.2 at pp. 97–98 — difficulty indexed by the maximal number of incomplete syntactic dependencies (1 / 3 / 5 across the worked series); the minimal pair, the same words reordered out of the nesting, is easier — <https://tedlab.mit.edu/tedlab_website/researchpapers/Gibson_2000_DLT.pdf>. Shubi 2502.11150 (readability formulas, NLP-based methods, commercial systems and frontier LLMs are all poor predictors of eye-tracked reading ease; holds across L1/L2, reading regimes, and text lengths).
