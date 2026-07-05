---
title: Pasted snippets of project code must be replaced with pointers
rule_id: R-74
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: low
---

# Pasted snippets of project code must be replaced with pointers

## Thesis
Minimal illustrative snippets are acceptable where a pointer would not teach the pattern. Pasted snippets of actual project code must be replaced with a pointer to the source, optionally with a brief inline summary.

## Rationale
Code examples appear in 17.68% of development-guideline sections in the wild, so snippets are common and expected. But a snippet of project code duplicates the source of truth: when the project changes, the pasted copy rots while the prose still presents it as current.

## Example
```
bad:  ```java\n public Order place(Cart c){ /* 30 lines of real handler */ }\n```
good: Order placement: see PlaceOrderHandler#handle (validates, then persists)
```

## Limits
Classify each fenced block: a generic or language-syntax illustration stays; project-specific code over 10 lines becomes a pointer; project-specific code of 10 lines or fewer that teaches a pattern becomes a pointer plus a one- or two-line summary. Generic illustrations are out of scope.

## Validator
For each fenced code block, decide its source: generic syntax illustration, or project-specific code. Flag every block that reproduces project code. Validator question: would this exact block change if the project were refactored? If yes, it duplicates the source of truth and should be a pointer.

## Patch output
When a fenced block reproduces project code, emit one patch (`rule_id: R-74`, location naming the section, severity low) replacing the block with a pointer (`see <Class>#<method>`) plus, for short pattern-teaching snippets, a one- or two-line description.

## Source
Santos §5 (code examples in 17.68% of Development Guidelines sections).
