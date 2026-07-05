---
title: Cited claims must be entailed by their source
rule_id: R-56
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: high
---

# Cited claims must be entailed by their source

## Thesis
A citation is faithful only when the source entails the claim as written. Four drifts make a cited claim unfaithful even when the number survives: inversion (the source's direction reversed), stripped precondition (a model / benchmark / scaffold qualifier dropped so the result reads as general), refuted-as-recommendation (a position the source argues against stated as its advice), and flattened conditional ("when X, Y" becomes "always Y").

## Rationale
The four drifts are instances of intrinsic hallucination — content that misrepresents the source. Entailment by the source correlates with faithfulness far better than n-gram overlap, so a surviving number is not evidence of a faithful claim; only the source's actual statement is.

## Example
```
bad:  "Eval repetition (10×) is required for significance (Gao 2510.16786)."
      (source recommends 3–5 runs; 10× appears only in supplementary studies)
good: "Single-run evals are unstable; run 3–5 repetitions per task (Gao 2510.16786 §5.1)."
```

## Limits
Concerns faithfulness to the source, not number presence (a separate check) or locator stability. Entailment is a semantic judgement; when the source cannot be fetched during the audit, the check cannot be completed mechanically and must be escalated rather than resolved.

## Validator
For each cited claim, compare against the source's actual statement: (a) direction matches; (b) the qualifying population, model, or benchmark is carried into the claim; (c) what the file presents as the source's recommendation is one; (d) "always / never / required" in the file corresponds to an unconditional claim in the source. Validator question: would the source's authors accept this sentence as a summary of their finding, with its conditions intact?

## Patch output
When a cited claim drifts from its source, emit one patch (`rule_id: R-56`, `location.section` = heading, severity high) re-aligning the claim with the source and restoring the dropped condition; set `needs_human: true` when the source was not re-fetched during the audit, since entailment is a semantic check.

## Source
Maynez 2005.00661, ACL 2020 (entailment correlates with faithfulness far better than n-gram overlap; the four drifts are intrinsic hallucination).
