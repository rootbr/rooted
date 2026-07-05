---
title: Cross-file duplication must be consolidated once in AGENTS.md and referenced from siblings
rule_id: R-71
applies_to_target: [context-file]
check_kind: mechanical
severity_default: medium
---

# Cross-file duplication must be consolidated once in AGENTS.md and referenced from siblings

## Thesis
When `CLAUDE.md`, `AGENTS.md`, and `copilot-instructions.md` coexist in one repo, each shared convention must be written once in `AGENTS.md` and referenced from the others, not copied verbatim into each.

## Rationale
In a 2,853-repo sample, 301 outgoing `CLAUDE.md` → `AGENTS.md` references were observed: `AGENTS.md` receives the most incoming references and is the empirically dominant shared baseline. Duplicating a rule across files multiplies the surfaces that drift out of sync on the next edit.

## Example
```
bad:  same commit-message convention pasted in CLAUDE.md and copilot-instructions.md
good: convention written once in AGENTS.md#commits; others say `see AGENTS.md#commits`
```

## Limits
Applies only inside a repo that holds more than one AI-context file; a lone context file has no sibling to consolidate into. The check needs the discovery inventory's cross-file comparison to identify content that is repeated verbatim across files.

## Validator
Request the discovery inventory's cross-file comparison. For each rule appearing verbatim in two or more of the coexisting context files, flag the copies outside `AGENTS.md`. Validator question: is this content already stated in `AGENTS.md`, so the local copy could become a reference?

## Patch output
When the same content appears in two or more context files, emit one patch (`rule_id: R-71`, location naming the current file and the duplicate-in file, severity medium) proposing to keep the canonical version in `AGENTS.md` and replace the duplicates with `see AGENTS.md#<anchor>`.

## Source
Galster 2602.14690 §6.1 (301 outgoing CLAUDE.md → AGENTS.md references; AGENTS.md is the dominant incoming-reference baseline).
