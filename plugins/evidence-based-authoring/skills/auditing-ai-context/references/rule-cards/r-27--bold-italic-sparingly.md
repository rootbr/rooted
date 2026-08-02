---
title: Bold and italic are reserved for critical warnings and first-term introductions
rule_id: R-27
applies_to_target: [context-file, skill, agent-prompt, doc, answer]
check_kind: semantic
severity_default: low
---

# Bold and italic are reserved for critical warnings and first-term introductions

## Thesis
Bold only critical warnings (safety, data integrity) and the first introduction of a term — nothing else.

## Rationale
Bold every fifth phrase and bold loses meaning: when emphasis is everywhere, it stops signalling importance anywhere.

## Example
```
bad:  "**Always** use **the** validator for **each** rule."
good: "Always use the validator for each rule."
```

## Limits
Covers emphasis density and target only. A high count is the trigger, but whether a given bolded phrase is a genuine safety warning or a first-term introduction — and so may stay — is a reading judgement.

## Validator
Count `**` occurrences per 100 lines. If there are more than 10 per 100 lines, the file is over-emphasizing. Sample the emphasized phrases: are they safety warnings or the first introduction of a defined term? If neither → propose unbolding.

## Patch output
When emphasis density exceeds 10 per 100 lines and a phrase is neither a warning nor a first-term introduction, emit one patch (`rule_id: R-27`, `location.section` + `line_hint`, `current` = the bolded phrase, severity low) proposing the unbolded equivalent; set `needs_human: true` when the phrase's status as a warning or term is unclear.

## Source
Chatlatanagulchai 2509.14744 (emphasis convention; bold is devalued past roughly 10 per 100 lines).
