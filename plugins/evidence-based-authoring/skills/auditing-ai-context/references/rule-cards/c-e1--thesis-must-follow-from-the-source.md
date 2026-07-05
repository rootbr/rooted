---
title: The thesis must follow from its source, with no inversion, stripped precondition, refuted position, or flattened conditional
rule_id: C-E1
applies_to_target: [kb-card]
check_kind: semantic
severity_default: high
---

# The thesis must follow from its source, with no inversion, stripped precondition, refuted position, or flattened conditional

## Thesis
The thesis must be entailed by its source. Four drifts are forbidden: inverting the source's claim, dropping a precondition the source attached, stating as a recommendation a position the source refuted, and flattening a conditional ("X only when Y") into an absolute ("X").

## Rationale
Each of the four drifts is an intrinsic hallucination — content that misrepresents the very source the card claims to rest on, so the consumer acts on a claim its provenance does not support. Entailment by the source tracks faithfulness far better than surface word overlap: a card can reuse the source's vocabulary while reversing its meaning, so faithfulness is judged by whether the source logically supports the thesis, not by shared phrasing.

## Example
```
rejected: Long meetings improve decisions.            # inverts a source warning against them
accepted: Meetings over 90 minutes degrade decision quality, so split them.
```

## Limits
Covers fidelity of the thesis to what the source actually claims. It does not judge whether the source itself is correct, nor whether the thesis is well-formed or atomic. The defect is specifically a mismatch between the card's claim and the source's claim along one of the four drifts.

## Validator
Compare the thesis against the source for each drift: is the direction reversed, a stated precondition dropped, a refuted position presented as advice, or a conditional flattened to an absolute? Flag any mismatch. Validator question: does the source logically entail this thesis as stated, or has its meaning shifted?

## Patch output
When auditing a thesis that does not follow from its source, emit one patch (`rule_id: C-E1`, severity high) naming the drift and proposing a faithful restatement. Verifying entailment requires reading the source, so set `needs_human: true`.

## Source
KB card spec, faithfulness rules, group E; Maynez et al. ACL 2020 arXiv:2005.00661 (intrinsic hallucination; entailment correlates with faithfulness far better than n-gram overlap).
