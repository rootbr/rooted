---
title: A working file states the merged rule; a precedence that must hold is executed, never declared between peer rules
rule_id: S-03
applies_to_target: [context-file, skill, agent-prompt, doc]
check_kind: semantic
severity_default: medium
---

# A working file states the merged rule; a precedence that must hold is executed, never declared between peer rules

## Thesis
Where two rules in a file prescribe different actions for the same case, the file states one merged rule carrying the condition that separates them. A precedence between peer rules is not written as a resolution clause; a precedence that must hold is executed by the code that applies the rules.

## Rationale
An unresolved contradiction fails silently. Models detect a conflict inside a set of instructions well — the highest measured average F1 scores are 91.5% and 87.3% — yet they rarely notify the reader of the conflict or ask for clarification. One side is chosen, the answer looks plausible, and nothing in the output marks the arbitrary choice. Declaring an order does not repair this: compliance with a declared hierarchy spans 98.2% down to 20.5% across 37 models, and strengthening the wording fixes some failures while others persist at every strictness level. What compliance exists comes from training a model on the hierarchy rather than from a document announcing one, so a clause ranking two peer rules inside a file has nothing enforcing it.

## Example
```
bad:  "Book the cheapest flight." … "Book the direct flight." … "The earlier rule wins."
good: "Book the direct flight; take the cheapest one when no direct flight exists."
```

## Limits
The compliance range measures privilege between message roles rather than precedence between peer rules inside one document, so applying it here is an extrapolation — one running in the pessimistic direction, since role hierarchies are the case models are trained for and peer-rule precedence is not. A precedence recorded as guidance for whoever maintains the file, not as an instruction to be obeyed at runtime, is out of scope. Merging is the treatment for a genuine contradiction, not for two rules that merely sit near each other.

## Validator
Find pairs of rules that can both apply to one case and prescribe different actions. For each pair, check whether the file states a single rule with the condition that separates the cases, or leaves both standing behind a resolution clause ("the earlier wins", "in case of conflict", "unless stated otherwise"). Flag the resolution clause and the unmerged pair together. Validator question: does the file say what to do in the overlapping case, or only which rule wins it?

## Patch output
When auditing a file that leaves two conflicting peer rules standing behind a declared precedence, emit one patch (`rule_id: S-03`, `location` set to the heading and line hint, `current` = the clause plus the conflicting pair, severity medium) proposing the merged rule with its explicit condition. Judging whether two rules truly conflict, and what condition separates them, is a semantic call, so set `proposed: null` and `needs_human: true`.

## Source
ConInstruct 2511.14342 (conflict detection within instructions — highest average F1 91.5% and 87.3%; models rarely notify users of a detected conflict or request clarification); IH-Benchmark 2607.25987 (declared-hierarchy compliance spans 98.2%–20.5% across 37 models; stronger warnings fix some failures, others persist at every strictness level — measures role privilege, not peer-rule precedence, so the transfer is an extrapolation); Wallace 2404.13208 (hierarchy following is obtained by a training method, not by declaration).
