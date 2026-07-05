---
title: Spell out conditionals; underspecified branches recover only 22.9%
rule_id: R-67
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# Spell out conditionals; underspecified branches recover only 22.9%

## Thesis
Spell out conditional branches and exception cases explicitly. Format defaults the model handles natively (length, casing, layout) MAY be omitted, but a conditional that implies an alternative path must name both branches.

## Rationale
Format defaults are inferred correctly 70.7% of the time when left unspecified, but conditional and edge-case rules are inferred correctly only 22.9% of the time. The model fills in formatting reliably and guesses branch logic poorly, so files should under-specify formats and over-specify conditionals.

## Example
```
bad:  "Usually return JSON."
good: "If the request sets Accept: application/json → return JSON; otherwise → return plain text."
```

## Limits
Targets implicit conditionals — prose that signals a branch ("usually X", "in most cases", "for typical inputs") without naming the alternative. Format defaults the model infers reliably are explicitly out of scope; spelling those out adds tokens without adding reliability.

## Validator
Find prose that implies a conditional ("usually", "in most cases", "for typical inputs", "normally") but does not name the alternative branch. For each, propose making the conditional explicit in the form "If X → do A; if Y → do B." The judgement of whether prose hides an unstated branch is the semantic call.

## Patch output
When prose implies a conditional without naming both branches, emit one patch (`rule_id: R-67`, `location` set to the heading and line hint, `current` = the implicit-conditional prose, severity medium) proposing the explicit conditional with both branches; set `needs_human: true` when the alternative branch's behavior is unknown.

## Source
Yang 2505.13360 §3.2 (format defaults inferred 70.7%; conditional / edge-case rules only 22.9%).
