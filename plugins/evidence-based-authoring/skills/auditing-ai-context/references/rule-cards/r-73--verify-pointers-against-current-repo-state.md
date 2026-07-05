---
title: Every pointer to an in-repo entity must be verified against the current repo state
rule_id: R-73
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# Every pointer to an in-repo entity must be verified against the current repo state

## Thesis
Verify every pointer to an in-repo entity — a method, file, package, or repo-relative path — against the current state of the repo. A pointer whose target no longer exists is stale and must be corrected or removed.

## Rationale
After a repo changes, references to renamed methods, deleted files, or removed packages rot silently: nothing in the prose signals that the target moved, so a reader follows the pointer to nothing and the instruction misleads.

## Example
```
bad:  "Retry logic: see RetryPolicy#shouldRetry"   # method was renamed to attemptRetry
good: "Retry logic: see RetryPolicy#attemptRetry"  # matches the current symbol
```

## Limits
Applies to pointers that name a concrete in-repo entity (`<Class>#<method>`, `<file>::<function>`, repo-relative path). Generic pattern placeholders and references to external sources are out of scope. The check searches the current repo for the named entity with the `Grep` / `Glob` tools (no shell needed) and so needs a checkout of the repo; without one it cannot run.

## Validator
Inventory the file's pointers to in-repo entities. For each symbol, search the repo with the `Grep` tool (`<symbol>` over `<repo-root>`, files-with-matches mode); use `Glob` for a path pointer. If there is no match, the target is absent in the current repo and the pointer is stale; flag it. Validator question: does this exact symbol or path still exist in the repo?

## Patch output
When a pointer's target is absent from the current repo, emit one patch (`rule_id: R-73`, location naming the section, `proposed: null`, severity medium, `needs_human: true`) so the author supplies the current name or deletes the rule — the sub-agent cannot infer the new target.

## Source
Verified hands-on experience maintaining instruction files whose in-repo pointers rot after renames and deletions.
