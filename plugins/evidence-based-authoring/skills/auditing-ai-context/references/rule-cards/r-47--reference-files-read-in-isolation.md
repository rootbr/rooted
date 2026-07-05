---
title: Reference files must read in isolation — no unnamed-document deixis, no completing cross-references
rule_id: R-47
applies_to_target: [skill]
check_kind: semantic
severity_default: medium
---

# Reference files must read in isolation — no unnamed-document deixis, no completing cross-references

## Thesis
A reference file is loaded alone by its consumer — one sub-agent reads one reference, and files two hops from SKILL.md get only partial reads. Two failure shapes break this. First, unnamed-document deixis: "the parent skill", "the skill itself", "as noted earlier", "you reported" — referents that resolve only inside the authoring context. Second, a completing cross-reference: a rule whose operative content (threshold, procedure, definition) lives only in a sibling file, so the rule cannot be applied without loading that file. A reference may *enrich* (name the sibling and carry enough content to act); it may not *complete*.

## Rationale
The consumer reads the file with no other document in context, so an unresolvable referent is dead weight and a completing reference silently disables its rule. Verified on a real skill's references: unnamed-document deixis ("the parent skill", "you reported") was found across multiple reference files, including one remnant of the authoring conversation that no consumer could resolve.

## Example
```
bad:  G-17 in the parent skill: conflict resolution is underdeveloped.
good: G-17 in ../SKILL.md: conflict resolution is underdeveloped.

bad:  When the file exceeds the budget, emit a maintenance patch.
good: When the Phase 0 inventory marks the file over its tier budget, emit a patch.
```

## Limits
A deference stub whose whole instruction is "defer; another group owns the patch" is complete in itself — the action is omission — and is not a violation. Deictic phrases inside fenced example blocks (demonstrating the violation, not committing it) are also out of scope.

## Validator
Grep for "the parent", "the skill itself", "as noted earlier", "as we saw", "see above", and second-person references to past events ("you reported", "you asked"). For each hit outside fenced blocks, name the document (`../SKILL.md §<section>`) or delete the clause. Then, for each rule that points at a sibling file, ask whether the rule can be applied with only this file in context; if the operative content is elsewhere, inline it or delegate the trigger to the Phase 0 inventory. Validator question: if this file is the only document in context, does every referent resolve and does every rule remain applicable?

## Patch output
When auditing a deictic phrase or a completing cross-reference, emit one patch (`rule_id: R-47`, location of the phrase, severity medium) proposing the named-document form or the inlined content; set `needs_human: true` when the operative content must be authored rather than merely renamed.

## Source
Anthropic, Skill authoring best practices (files two hops from SKILL.md get partial reads); verified on a real skill's own references.
