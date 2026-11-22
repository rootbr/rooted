---
title: Decompose single-shot artifact outputs when the target exceeds 232 tokens
rule_id: R-15
applies_to_target: [skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# Decompose single-shot artifact outputs when the target exceeds 232 tokens

## Thesis
Skills that demand one large generated artifact in a single response are fragile. When the canonical target length exceeds 232 tokens, decompose into bounded outputs or iterative edits.

## Rationale
Pass@1 falls gradually as the canonical target length grows, and above 232 tokens even GPT-4o, the top model, stays below 10%. Tracing the drop to attention-budget contention between maintaining the constraint set and generating long structured output simultaneously is house inference. Bounded outputs let the model re-read constraints between segments.

## Example
```
bad:  "Generate the full README in one response."
good: "Generate the README outline first. Then fill each section one at a time."
```

## Limits
Applies to instructions demanding a single large artifact in one response where the target plausibly exceeds 232 tokens; short bounded outputs are unaffected.

## Validator
Search the body for instructions of the form "produce a complete X", "write the full Y", "generate the entire Z" where X/Y/Z is plausibly > 232 tokens. Flag each one.

## Patch output
When a single-shot artifact instruction targets > 232 tokens, emit one patch (`rule_id: R-15`, `current` = single-shot instruction, `proposed` = decomposed instruction with bounded steps, severity medium). Set `needs_human: true` when the target length is hard to estimate.
