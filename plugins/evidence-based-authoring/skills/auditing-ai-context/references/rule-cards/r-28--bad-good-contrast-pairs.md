---
title: Normative rules are paired with a bad/good contrast example
rule_id: R-28
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# Normative rules are paired with a bad/good contrast example

## Thesis
Pair each normative rule (do this, not that) with a bad/good example.

## Rationale
Normative rules gain meaningfully from contrast pairs: without an example, edge cases are left to reader inference, and the reader must reconstruct the boundary the rule is drawing.

## Example
```
bad:  "Name by function." (no example)
good: "Name by function. bad: java-skill / good: reviewing-java"
```

## Limits
Targets normative rules (MUST / SHOULD). A rule that already has an adjacent bad/good pair needs no patch, and a self-evident rule may not need one. Deciding whether a rule is normative and whether it genuinely needs an example is a reading judgement.

## Validator
For each MUST or SHOULD rule, check whether at least one bad/good pair is adjacent. Long rules without examples are candidates for example-addition; rules that already carry examples do not need patches.

## Patch output
When a normative rule lacks an adjacent contrast example, emit one patch (`rule_id: R-28`, `location.section` + `line_hint`, `current` = the rule sentence, severity low) proposing an added pair (`bad: … / good: …`); set `needs_human: true` when constructing the example needs domain knowledge.

## Source
Chatlatanagulchai 2509.14744 (contrast-pair convention; normative rules gain from bad/good examples).
