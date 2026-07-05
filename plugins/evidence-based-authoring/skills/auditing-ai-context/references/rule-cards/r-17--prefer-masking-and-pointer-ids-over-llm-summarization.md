---
title: For large tool outputs, prefer masking and pointer-IDs over LLM summarization
rule_id: R-17
applies_to_target: [skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# For large tool outputs, prefer masking and pointer-IDs over LLM summarization

## Thesis
For skills whose tools return large outputs, favor masking and pointer-IDs over LLM summarization. Three structural mechanisms beat semantic rewrites: masking stale observations (cuts 50.9–57.1%, no overhead), LLM summarization (cuts 41.5–55.4%, but adds a 0.65–7.20% summary pass), and pointer-IDs that return a handle the agent dereferences (~7× measured, ~16,900× estimated against a baseline that would overflow the window, no overhead).

## Rationale
Runtime tool outputs consume ~84% of agent tokens. The structural mechanisms cut that cost without a summary pass and without the accuracy risk of a semantic rewrite.

## Example
```
bad:  "Summarize the tool output, then continue."
good: "Return a handle/path to the output; read it on demand."
```

## Limits
Applies to skills whose tools return large blobs or that generate heavy intermediate output. A skill with only small tool outputs is out of scope.

## Validator
For skills whose tools return large blobs: if the tool inlines the blob → propose returning a handle/path read on demand. If the skill instructs the model to "summarize the output" → flag and propose masking-by-recency or pointer-ID. If the skill itself generates heavy intermediate output (research sweeps, long tool chains) → propose `context: fork` in frontmatter so the skill runs in an isolated context window and only its result returns to the main thread.

## Patch output
When an observation-handling instruction relies on summarization or inlines a large blob, emit one patch (`rule_id: R-17`, `current` = observation-handling instruction, `proposed` = masking or pointer-ID instruction, severity low). Set `needs_human: true` when the right mechanism depends on tool behavior the auditor cannot see.

## Source
Lindenbauer 2508.21433 §1 (tool outputs ~84% of agent tokens); Bulle Labate 2511.22729 §3.1–3.2 (masking 50.9–57.1%; summarization 41.5–55.4% + 0.65–7.20% pass; pointer-ID ~7× measured / ~16,900× estimated).
