---
title: Positive framing in body; negatives reserved for description triggers and safety
rule_id: R-61
applies_to_target: [context-file, skill, agent-prompt, doc, code, answer]
check_kind: semantic
severity_default: low
---

# Positive framing in body; negatives reserved for description triggers and safety

## Thesis
In the body, write what TO do, not what NOT to do. Negative phrasing is permitted in exactly two places: the frontmatter `description` for negative triggers ("NOT for Vue or Svelte" — improves routing precision), and safety or data-integrity rules ("Never commit without tests"). Everywhere else, use positive phrasing.

## Rationale
Frontier models interpret prohibitions hyper-literally: "ONLY" and "must NOT" constraints act as handcuffs, and the model curtails legitimate behavior in adjacent space to over-comply, including hyper-literal misreads of idioms. Positive phrasing is processed more reliably.

## Example
```
bad:  "Don't use H4 headings."
good: "Keep heading depth ≤ 3 (H1 → H3); split deeper structures into a new H2."
```

## Limits
A negative kept in the `description` to mark a non-trigger is in scope to keep, not convert. A safety or data-integrity prohibition is kept, but its ALL-CAPS marker still needs a one-sentence rationale. Only style, formatting, and edge-case prohibitions in the body are converted; reframe an edge-case prohibition as "When X, do Y instead of Z."

## Validator
Grep the body for `do not`, `don't`, `never`, `must not`, `shall not`, `avoid`, `refrain from`. For each hit, classify: a `description`-field non-trigger → keep; a safety or data-integrity rule → keep (confirm its capitalized marker carries a rationale); a style or formatting rule → convert to positive; an edge-case prohibition → reframe as a conditional. Flag every style-class negative in the body.

## Patch output
When auditing a body negative that is style- or edge-case-class, emit one patch (`rule_id: R-61`, `location` set to the heading and line hint, `current` = the negative phrasing, severity low) proposing the positive equivalent; set `needs_human: true` when the prohibition's class (safety vs style) is unclear.

## Source
Promptomatix §B.1.1 (positive phrasing processed more reliably); Khan 2510.22251 §5.3 (ONLY / must-NOT handcuff frontier models). Appendix guidance ships without its own empirical citations — treat as vendor-grade.
