---
title: Cite a paper once with its full ID, then use short-form
rule_id: R-55
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: low
---

# Cite a paper once with its full ID, then use short-form

## Thesis
First mention of a source carries the full ID: `Author <Year> <arxiv-id> §<N>`. Every subsequent mention of the same source in the same file uses the short form: `<Author> §<N>` or `<arxiv-id> §<N>`.

## Rationale
Repeating the full citation devalues it and inflates length: each restatement spends tokens on bookkeeping the reader already has, and the full form's signal — "here is where to find this" — is diluted by repetition.

## Example
```
bad:  "... (Yang 2505.13360 §3.1) ... and again (Yang 2505.13360 §3.4)."
good: "... (Yang 2505.13360 §3.1) ... and again (Yang §3.4)."
```

## Limits
Concerns repeated mentions of one source within a single file. The first full mention is correct and is never flagged. Whether the locator itself is structurally stable is a separate check.

## Validator
Count occurrences per cited source. If any source appears with its full ID plus year more than once, propose shortening the second and later occurrences to `<Author> §<N>` or `<arxiv-id> §<N>`.

## Patch output
When a source's full ID + year recurs after its first mention, emit one patch (`rule_id: R-55`, `location.section` = heading, severity low) replacing the repeated full citation with its short form. No `needs_human` flag — occurrence counting is mechanical.

## Source
Convention; rationale is token economy (repeated full citation inflates length without adding locator value).
