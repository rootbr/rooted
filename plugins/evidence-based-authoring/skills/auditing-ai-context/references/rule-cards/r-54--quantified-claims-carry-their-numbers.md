---
title: Quantified claims must carry their numbers
rule_id: R-54
applies_to_target: [context-file, skill, agent-prompt, doc, code, answer]
check_kind: mechanical
severity_default: low
---

# Quantified claims must carry their numbers

## Thesis
When a source supports a claim with a measured effect, the rule must preserve the number. "Improves accuracy" is not equivalent to "improves accuracy by 18.6pp" — the number is the load-bearing part of the citation.

## Rationale
Stripped numbers turn a falsifiable claim into a vague gesture. 5.9% of requirements regress by more than 20% over model updates when left unspecified — almost a 2× increase versus specified ones; a vague claim is the unspecified-requirement analog at the rule level.

## Example
```
bad:  "Reliable@10 testing catches failures."
good: "Reliable@10 testing exposes hidden failure modes — up to 61.8pp reliability
      drops measured vs single-prompt accuracy (Dong 2512.14754 §2.2)."
```

## Limits
Applies to claims whose source carries a measured number. A qualitative finding with no measured effect in the source has no number to restore and is out of scope. Whether the number is faithful to the source's direction and conditions is a separate entailment check.

## Validator
For each cited claim, check whether the source's number is present in the file. If the source supports the claim with a measured effect and the rule omits it, flag.

## Patch output
When a cited claim has been de-quantified, emit one patch (`rule_id: R-54`, `location.section` = heading, severity low) restoring the source's number to the claim. No `needs_human` flag — the number's presence or absence is mechanically decidable.

## Source
Yang 2505.13360 §3.3 (5.9% of unspecified requirements regress >20% over model updates, ~2× the specified rate).
