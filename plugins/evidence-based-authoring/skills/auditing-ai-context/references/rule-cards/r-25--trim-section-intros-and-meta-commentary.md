---
title: Section intros and meta-commentary are trimmed so a section opens on its rule
rule_id: R-25
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# Section intros and meta-commentary are trimmed so a section opens on its rule

## Thesis
A section starts with its rule, fact, or instruction — not with framing such as "In this section we will discuss X", "The following table summarizes Y", or "Note that Z is important".

## Rationale
Framing sentences are pure overhead: they spend tokens announcing structure instead of stating a rule, and the structure they announce is already visible from the heading and the content that follows.

## Example
```
bad:  "## Token Economy / The following bullets describe the rules…"
good: "## Token Economy / - Tables for lookup data."
```

## Limits
Targets the opening sentence of a section. A sentence that both frames and carries load-bearing content should be trimmed to its content, not deleted outright. Deciding whether an opening sentence states a rule or merely announces one is a reading judgement.

## Validator
Read the first sentence of each section: does it state a rule, fact, or instruction? If it announces what is to come or comments on the structure → flag.

## Patch output
When an opening sentence only frames or comments on structure, emit one patch (`rule_id: R-25`, `location.section` + `line_hint`, `current` = the intro sentence, severity low) deleting it so the first rule moves into first position; set `needs_human: true` when the sentence also carries content that must be preserved.

## Source
Chatlatanagulchai 2509.14744 (token-economy convention; framing sentences are overhead).
