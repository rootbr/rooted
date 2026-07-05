---
title: Compress format, never meaning
rule_id: R-11
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# Compress format, never meaning

## Thesis
Tables, fragments, abbreviations, and merged bullets are safe compressions. Paraphrasing, summarizing, or bulk-deleting accumulated bullets is not. When in doubt, append-and-refine; never wholesale-rewrite.

## Rationale
A working playbook reduced from 18,282 to 122 tokens — paraphrased into "essentials" — dropped accuracy from 66.7% to 57.1%, below the uncompressed baseline. Each removed bullet was a load-bearing failure-mode reminder; the paraphrase looked tighter but had lost the operational specifics.

## Example
```
bad:  "Make sure to always use the appropriate tier in order to ensure
       efficient token utilization."
good: "Tier content by access frequency."
```

## Limits
Format-only transforms are safe: bullet → table cell, bullet → fragment, long word → short synonym, and merging two bullets that state one rule only when they are exact duplicates. Paraphrase rewrites of an accumulated playbook and bulk-deletion to hit a token target are not safe — refuse and propose tier demotion instead. Exact-duplicate detection is a separate check.

## Validator
For each proposed compression, classify it as format (safe) or meaning (unsafe). Safe: bullet → table cell, verbose phrase → fragment, long word → short synonym, exact-duplicate merge. Unsafe: paraphrase rewrite of accumulated bullets, bulk-delete to hit a token count. Flag any compression that removes propositional content rather than restating it.

## Patch output
When a verbose passage can be compressed in form, emit one patch (`rule_id: R-11`, `current` = verbose excerpt, `proposed` = format-compressed excerpt with the same propositional content, severity low). Set `needs_human: true` when it is unclear whether a bullet is load-bearing.

## Source
Zhang 2510.04618 §2.2, Fig 2 (ACE: 18,282 → 122 tokens, accuracy 66.7% → 57.1%, below baseline).
