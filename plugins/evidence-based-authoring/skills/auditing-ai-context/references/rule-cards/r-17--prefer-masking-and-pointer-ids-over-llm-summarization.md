---
title: For large tool outputs, prefer masking and pointer-IDs over LLM summarization
rule_id: R-17
applies_to_target: [skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# For large tool outputs, prefer masking and pointer-IDs over LLM summarization

## Thesis
For skills whose tools return large outputs, favor masking and pointer-IDs over LLM summarization. Three mechanisms compare: masking stale observations (cuts instance cost 9.8–57.1% at a solve rate from 1.0 pp below to 5.0 pp above summarization's, no overhead), LLM summarization (cuts 0.0–55.4%, but adds a 0.65–7.20% summary pass), and pointer-IDs that return a handle the agent dereferences (~7× measured, ~16,900× estimated against a baseline that would overflow the window, no overhead).

## Rationale
Runtime tool outputs consume ~84% of agent tokens. The structural mechanisms cut that cost without a summary pass, and masking does so at a solve rate close to a semantic rewrite's, though in one of five configurations it lowered the solve rate significantly.

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
