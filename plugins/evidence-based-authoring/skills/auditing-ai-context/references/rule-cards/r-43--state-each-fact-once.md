---
title: State each fact once; downstream sections must reference, not restate
rule_id: R-43
applies_to_target: [context-file, skill, agent-prompt, doc, code, answer]
check_kind: mechanical
severity_default: medium
---

# State each fact once; downstream sections must reference, not restate

## Thesis
A factual claim, threshold, citation, or instruction may appear once in the file. Subsequent sections that depend on it must link by section name, rule ID, or short tag rather than repeat the wording.

## Rationale
Duplication has three failure modes. First, drift: one copy is updated, the other rots into a contradiction. Second, a bundling tax: the same rule appearing twice consumes two slots in the model's attention budget, displacing distinct rules. Third, reader confusion: the reader cannot tell whether the second mention is reinforcement or a *different* rule.

## Example
```
bad:  Packing list: two litres of water per person.  …  Reminder: pack two litres of water per person.
good: Packing list: two litres of water per person.  …  Reminder: water as the packing list says.
```

## Limits
Two surface forms that share vocabulary but prescribe *different* actions are not duplicates — leave both and tighten the wording so the distinction is visible. The rule targets restated prescriptions, not coincidental word overlap. A block that declares itself a summary of the file's own sections — a "Quick rules" list at the top of a skill, a dispatch overview that says the card's facet decides — is one fact whose owner is the detailed section; the summary line is flagged only where it contradicts its section. A script declaration that R-82 requires — summary, inputs, outputs, privileges — may restate what a phase narrates about the same script; R-82 owns that copy.

## Validator
Build a near-duplicate inventory in two passes. First, exact-or-near-exact: sliding 6-gram match, flag pairs at Jaccard ≥ 0.85. Second, semantic duplicate: different surface form, same prescription, detected via shared subject plus verb plus threshold. For each duplicate pair pick the canonical copy: a Principles or Definitions copy beats a Checklist copy; a cited copy beats an uncited one; a more compressed copy beats a verbose one; otherwise the first occurrence wins. Validator question: are these two surface forms saying the same *prescriptive thing*? If yes, consolidate.

## Patch output
When auditing a duplicate of a fact already stated earlier in the file, emit one patch (`rule_id: R-43`, location of the duplicate instance, severity medium) replacing the duplicate with a reference to the canonical section or tag, and record the canonical location on the patch.

## Source
Yang 2505.13360 §3.4 (a duplicated rule consumes two attention slots, displacing distinct rules).
