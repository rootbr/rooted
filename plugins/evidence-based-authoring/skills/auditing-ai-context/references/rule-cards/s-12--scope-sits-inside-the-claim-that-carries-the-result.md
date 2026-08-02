---
title: A result's scope sits inside the claim that carries it, never in a trailing block of caveats
rule_id: S-12
applies_to_target: [answer, doc]
check_kind: semantic
severity_default: medium
---

# A result's scope sits inside the claim that carries it, never in a trailing block of caveats

## Thesis
The scope of a result is stated inside the claim that carries it — "the patch fixes the leak in the pooled client" — rather than propping a wider claim up with a trailing block of caveats. A separate caveat earns its place only where it states what that scope does not imply and what would change the reader's decision: an open finding of the same work, a blocking consequence, the cost of an error.

## Rationale
A caveat block appended after the result does not reach the reader. A two-arm parallel-group randomised controlled trial put 30 systematic-review abstracts to 300 participants, 150 per arm, each abstract assessed 5 times in each arm, allocation concealed by a computer-generated web-based procedure at a 1:1 ratio. One arm read the abstract with a standardized limitations section, the other without, and no interpretation outcome moved: confidence in the results 4.6 (SD 2.5) without against 4.4 (SD 2.3) with, mean difference 0.2 (95% CI −0.4 to 0.7), p = 0.5; confidence in the validity of the conclusions 4.1 (SD 2.5) against 4.0 (SD 2.3), difference 0.07 (95% CI −0.5 to 0.6), p = 0.8; benefit to patients 4.4 (SD 2.6) against 4.3 (SD 2.3), difference 0.1 (95% CI −0.4 to 0.7), p = 0.6. A qualifier carried by the claim itself does reach the reader: in a pre-registered experiment with 404 participants, an uncertainty stated inside the answer lowered agreement with the system and raised participants' own accuracy, through reduced overreliance on incorrect answers. Set side by side, the two results say the qualifier works where the claim is, and the trailing block is the position with no measured effect.

## Example
```
bad:  The heater is fixed. Caveat: only the upstairs unit was tested.
good: The upstairs heater is fixed; the downstairs one is untested.
```

## Limits
Covers a claim that delivers a result to a reader, and the caveats attached beneath it. The measurement is a null result: it shows that a trailing limitations block leaves the reader's confidence where it was, never that the block does harm. Its participants were reader-experts — corresponding authors of trials indexed in a medical database — whom the authors themselves call unrepresentative of all readers, and the material was systematic-review abstracts rather than a technical answer. The second experiment varied the person an uncertainty is stated in, not its position, so the claim about placement is an extrapolation from the two results standing side by side. Where a target's own schema fixes a separate scope block, that block belongs to the schema and is not a caveat to fold in.

## Validator
Read the sentence carrying the result, then each caveat beneath it. Ask which of two things the caveat does: narrow the result — the narrowing belongs inside the result's own sentence — or state something the narrowed scope does not imply that would change the reader's decision, which keeps it where it is. Flag a result stated wider than what was actually done whose narrowing sits below it, and flag a caveat that only restates a scope the claim already carries. Validator question: does the sentence that carries the result already say how far the result reaches?

## Patch output
When auditing a target whose result claim is wider than what was done, with the narrowing parked in a trailing caveat, emit one patch (`rule_id: S-12`, `location.section` + `line_hint`, `current` = the claim together with the caveat, severity medium) proposing the result restated with its scope inside it. Telling a caveat that narrows the claim from one that states a consequence the reader must act on is a reading call, so set `proposed: null` and `needs_human: true`.

## Source
Yavchitz, Ravaud, Hopewell, Baron & Boutron 2014, *BMC Medical Research Methodology* 14:123, doi:10.1186/1471-2288-14-123, PMC4247631 — <https://pmc.ncbi.nlm.nih.gov/articles/PMC4247631/>, Table 4 and the trial abstract: 300 participants, 30 abstracts, all three interpretation outcomes unchanged; "adding a limitations section in abstracts of systematic review may not affect expert-readers' interpretation of abstract results and conclusions". Read first-hand. Kim 2405.00623 (FAccT 2024), pre-registered, N = 404: an uncertainty stated inside the answer lowers agreement and raises participants' accuracy. Caveats: a null result, on reader-experts the authors call unrepresentative, on systematic-review abstracts; the second experiment measured the person of the qualifier and not its position, so the placement claim is an extrapolation.
