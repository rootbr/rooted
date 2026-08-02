---
title: A load-bearing uncertainty is stated in the first person; an empty softener is cut
rule_id: S-07
applies_to_target: [answer, doc]
check_kind: semantic
severity_default: medium
---

# A load-bearing uncertainty is stated in the first person; an empty softener is cut

## Thesis
Where a claim rests on something the writer has not verified, say so in the first person. A softener with no real uncertainty behind it is cut.

## Rationale
The precise wording carries the effect. In a pre-registered experiment with 404 participants answering questions with and without access to a system's responses, first-person uncertainty ("I'm not sure, but…") lowered participants' confidence in the system and their tendency to agree with it while raising their own accuracy, an increase attributed to reduced — though not eliminated — overreliance on incorrect answers. The same uncertainty expressed from a general perspective ("It's not clear, but…") produced similar effects that were weaker and not statistically significant. So the operative rule is not "hedge" but "hedge in the first person". An empty softener names no uncertainty the reader can act on and only adds length, and length raises the reader's confidence without raising accuracy.

## Example
```
bad:  "It seems the boiler maybe needs servicing."
good: "I have not opened the casing — from the noise, the boiler needs servicing."
```

## Limits
Both halves hold together: cutting a genuine epistemic marker or a scope qualifier falsely changes the certainty or the reach of a claim, and only a softener with nothing behind it is the target. The experiment put medical questions to lay participants, so transfer to an expert reader in a technical domain is an extrapolation.

## Validator
For each hedge, ask what uncertainty stands behind it. Where a real one does, require the first-person form ("I have not verified", "I did not test") and flag the impersonal alternative ("it is not clear", "it may be that", "arguably"). Where none does, flag the hedge for removal. Flag a scope qualifier removed alongside the softeners. Validator question: does this hedge name something the writer actually does not know, and does it say who does not know it?

## Patch output
When auditing text whose uncertainty is expressed impersonally, or that carries a softener with no uncertainty behind it, emit one patch (`rule_id: S-07`, `location` set to the heading and line hint, `current` = the hedge, severity medium) proposing the first-person restatement or the removal. Telling a load-bearing uncertainty from an empty softener is a semantic call, so set `proposed: null` and `needs_human: true`.

## Source
Kim 2405.00623 (FAccT 2024) — pre-registered human-subject experiment, N = 404: first-person expressions decrease participants' confidence in the system and their tendency to agree with it while increasing participants' accuracy, through reduced overreliance on incorrect answers; effects for uncertainty expressed from a general perspective are weaker and not statistically significant. Steyvers 2401.13835, *Nature Machine Intelligence* (users show increased confidence with longer explanations even where the extra length does not improve accuracy). Caveat: medical questions, lay participants — transfer to an expert technical reader is an extrapolation.
