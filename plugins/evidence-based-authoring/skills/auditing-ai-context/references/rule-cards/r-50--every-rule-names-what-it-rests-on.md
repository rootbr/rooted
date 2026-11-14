---
title: Every rule names what it rests on
rule_id: R-50
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# Every rule names what it rests on

## Thesis
Every prescription — rule, threshold, anti-pattern, recommended pattern — names its ground, and the ground is one of four. A claim that a technique works rests on a test that could have refuted it: a study that was opened (arxiv ID + section anchor), or a test of the project's own kept in its repository. A norm rests on its document: a technical standard (RFC number + §) or a vendor or framework doc (stable URL or doc-version). A decision rests on its owner's word and says whose it is. A definition fixes a term. A prescription that claims an effect and names no test must be cut or marked a hypothesis.

## Rationale
A citation is the address of a test, and the test is what supports the claim: a source that states a rule and reports no test adds a name to an opinion. A rule whose ground is named can be checked again when the model, the tool or the document changes, and a rule that is its owner's choice is read as a choice rather than as a finding. Under the bundling tax every retained rule must justify its slot.

## Example
```
bad:  "Always use 3-5 examples — too few under-trains, too many confuse." (an effect claimed, no test)
good: "Use 2–5 diverse examples; inconsistent label/format across examples
      cuts effectiveness up to 40% (Promptomatix 2507.14241 §B.2.1)."
```

## Limits
Covers whether each prescription names its ground. Whether the cited locator is structurally stable (anchor vs page/line) is a separate check and not flagged here, and so is whether the source entails the claim as worded. A rule may legitimately remain when it is marked a hypothesis rather than asserted as fact. A repository that keeps every ground on the rule's line of a provenance map, keyed by the rule's id and enforced by its layout check, satisfies the rule for its run-set files: the prescription names its ground through the map, and the audit opens the map's line instead of asking for an inline citation.

## Validator
For each rule sentence, look in the surrounding 5 lines for its ground. A test: `(Author <Year>)`, `(<Author> §<N>)`, `<arxiv-id> §<N>`, a path to a test or an eval in the repository, `Verified on <project>`. A norm: `RFC <N>`, a named standard or specification, a link to a stable doc. A decision: `house convention`, or an owner named. A definition of a term. Where the repository keeps provenance out of its runtime files, the ground stands on the rule's line in the repository's provenance map. Flag a sentence that claims an effect — `improves`, `reduces`, `works better`, a percentage — and names no test, and a sentence that names no ground at all. Does this prescription say what it rests on, and where it claims an effect, is there a test a reader could open or rerun?

## Patch output
When auditing a rule sentence that names no ground, emit one patch (`rule_id: R-50`, `location.section` = heading, severity medium) proposing the ground to name — a test, a norm, the owner's decision — or the rule marked a hypothesis / cut; set `needs_human: true` because the sub-agent cannot invent a test or speak for the owner — the patch is a request to supply the ground or accept removal.
