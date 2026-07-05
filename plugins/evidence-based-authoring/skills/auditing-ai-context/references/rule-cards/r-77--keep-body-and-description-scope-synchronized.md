---
title: Body scope and description scope must stay synchronized across commits
rule_id: R-77
applies_to_target: [skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# Body scope and description scope must stay synchronized across commits

## Thesis
On every body edit that changes scope — a new tool, new file access, a new external call — the description must be updated in the same commit. When the body gained a capability across recent commits but the description did not change, scope drift is likely.

## Rationale
An unspecified requirement regresses more than 20% over a model update almost twice as often as a specified one. A description that does not advertise a capability the body now has is exactly such an unspecified requirement: the capability is undeclared, so nothing pins it across model updates.

## Example
```
bad:  commit adds a network-fetch step to the body; description still says "local only"
good: same commit updates the description to advertise the external fetch
```

## Limits
Detects drift only where git history is available; without it the check cannot run. It flags body capability growth unmatched by a description change — not every body edit, since wording changes that do not alter scope are out of scope.

## Validator
Compare the body against the description: enumerate every capability the body exercises (tool invocation, file write, network or external call) and verify the description advertises each. If the body uses a capability the description omits, flag. Verifying that body and description changed in the *same commit* needs `git log` (git history), which the read-only auditor lacks — treat that as an optional manual follow-up. Validator question: does the description advertise every tool, file access, and external call the body now uses?

## Patch output
When the body gained a capability the description does not advertise, emit one patch (`rule_id: R-77`, location naming the file and commit range, severity medium, `needs_human: true`) proposing description text that advertises the new capability — the author confirms scope rather than the sub-agent silently rewriting the description.

## Source
Yang §3.3 (unspecified requirements regress > 20% over model updates ~2× as often as specified ones).
