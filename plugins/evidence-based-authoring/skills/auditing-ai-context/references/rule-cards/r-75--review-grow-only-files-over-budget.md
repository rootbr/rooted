---
title: A file recorded as over its tier budget must get a refactor review, not paraphrase compression
rule_id: R-75
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# A file recorded as over its tier budget must get a refactor review, not paraphrase compression

## Thesis
When the discovery inventory marks a file as over its tier budget, emit a maintenance patch proposing a structural refactor review. The proposal is to split sections, demote content to a colder tier, or drop unsourced bullets — not to paraphrase the prose shorter.

## Rationale
A file that only ever appends content will eventually outgrow its tier budget. The fix must be structural: in one case study, an LLM that fully rewrote the accumulated context shrank it from 18,282 to 122 tokens in a single step, and accuracy fell from 66.7 to 57.1, below the 63.7 baseline; that trimming words while keeping every section fails the same way is house inference. Removing or relocating whole sections preserves the surviving text intact.

## Example
```
bad:  rewrite every paragraph tighter to fit the 200-line cap
good: split the API schema into references/api.md; demote the changelog to a cold file
```

## Limits
Targets files the inventory has already flagged as over budget; a file within budget needs no patch. The remedy is refactoring, distinct from in-place size compression — this card never proposes paraphrasing the prose to fit.

## Validator
Compare the line and token counts recorded in the discovery inventory against the tier budget the inventory names for the file. If over, name 3 to 5 candidate sections for demotion or split. Validator question: which whole sections could move to a colder file or be cut, so the file fits its budget without rewriting surviving text?

## Patch output
When the inventory marks a file over budget, emit one patch (`rule_id: R-75`, location naming the file, `current` = line/token count, severity medium) proposing a refactor pass that lists 3 to 5 candidate sections for demotion or split.
