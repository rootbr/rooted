---
title: Cousin-prompt examples beat generic Alpaca-style examples
rule_id: R-66
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# Cousin-prompt examples beat generic Alpaca-style examples

## Thesis
When authoring trigger examples or eval prompts, use cousin-prompt variants — paraphrases of real user queries, with concrete detail — rather than abstract textbook-style prompts.

## Rationale
Cousin-augmented data lifts reliability by more than 45% over generic Alpaca-style examples; the generic examples actually decline reliability, so an abstract prompt is worse than no example, not merely weaker.

## Example
```
bad:  "Format this data."
good: "my boss sent an xlsx (downloads, 'Q4 sales final FINAL v2.xlsx'); add a profit-margin %
      column — revenue in col C, costs in col D i think"
```

## Limits
Concerns example user prompts and eval prompts — the realistic-query class — not the rule prose itself. The judgement of whether a prompt reads as a realistic user voice versus an abstract textbook stub is the semantic call.

## Validator
Examine the example user prompts in the file. Classify each as (a) realistic — concrete file paths, company names, casual phrasing, real-world mess — or (b) abstract textbook-style. For each abstract prompt, propose a cousin-prompt rewrite that adds realistic detail and a believable user voice.

## Patch output
When an example prompt is abstract, emit one patch (`rule_id: R-66`, `location` set to the heading and line hint, `current` = the abstract prompt, severity low) proposing a cousin-prompt rewrite with realistic detail; set `needs_human: true` when the realistic context to inject is unknown.

## Source
Dong 2512.14754 Fig 5 (cousin-augmented data lifts reliability >45%; generic Alpaca-style examples decline it).
