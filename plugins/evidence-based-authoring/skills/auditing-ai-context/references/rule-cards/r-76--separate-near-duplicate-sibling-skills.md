---
title: Near-duplicate sibling skills must be consolidated or sharpened to restore routing separation
rule_id: R-76
applies_to_target: [skill]
check_kind: semantic
severity_default: medium
---

# Near-duplicate sibling skills must be consolidated or sharpened to restore routing separation

## Thesis
Audit sibling skills for semantic overlap. When two siblings cover nearly the same subject, action, and target, consolidate them or sharpen one name and description to create the separation a router needs.

## Rationale
Near-duplicate skills corrupt routing at the training-data level: in a set of 39,065 mined hard-negative pairs, about 10% were near-duplicates of the gold skill and had to be filtered to keep the router learnable. Semantic overlap between siblings erodes the separation a router depends on, so each steals the other's activations.

## Example
```
bad:  "review-java" and "java-code-review" — same subject, action, target
good: "reviewing-java" (PR diffs) vs "java-style-lint" (NOT for: logic review)
```

## Limits
Applies to sibling skills in the same plugin or marketplace, compared pairwise; it needs the discovery inventory's sibling descriptions. Skills that merely share a domain but differ in action or target are not duplicates and need no patch.

## Validator
For each pair (current skill, sibling), compute semantic similarity over the subject, action, and target the descriptions express. If overlap is at or above roughly 70%, flag the pair. Validator question: given only the two descriptions, could a router reliably pick the right one for a task?

## Patch output
When a sibling pair overlaps at or above the threshold, emit one patch (`rule_id: R-76`, location naming both skills, severity medium) proposing to sharpen the description (add a disambiguating term, add a NOT-for clause naming the sibling's domain) or to consolidate the two skills.

## Source
Zheng §4 (~10% of 39,065 mined hard-negative pairs were near-duplicates filtered to keep the router learnable).
