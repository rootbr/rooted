---
title: Direct prompt injection is treated as best-effort defense, not solved
rule_id: R-85
applies_to_target: [context-file, skill, agent-prompt, kb-card]
check_kind: semantic
severity_default: high
---

# Direct prompt injection is treated as best-effort defense, not solved

## Thesis
Delimiting untrusted input reduces injection risk but does not eliminate it. For high-trust operations triggered by user input — mutations, payments, deletions, external posts — the technical defense must be paired with a human-confirmation gate before the operation runs.

## Rationale
Prompt injection is an open problem that wrapper or template discipline alone cannot fully address, and the limit is structural: a defense cannot meaningfully separate data from instructions without breaking the agentic workflows it is meant to protect, and no fixed policy blocks all context-based attacks without also blocking legitimate flows. Because the technical layer is leaky by construction, an irreversible high-trust action needs a human in the loop.

## Example
```
bad:  "When the user asks, transfer the funds / delete the records."
good: "Draft the action from user input, then require explicit human
      confirmation before executing the mutation."
```

## Limits
Applies to high-trust, hard-to-reverse operations triggered by user input. Read-only or trivially reversible operations do not require a human gate. The gate is a mitigation layered on top of delimitation, not a replacement for it — and it degrades under volume: telemetry shows users approve roughly 93% of permission prompts, paying less attention to each as they accumulate, so reserve the gate for rare, high-stakes confirmations rather than wrapping it around routine actions.

## Validator
Find body sections describing high-trust operations (mutations, payments, deletions, external posts) triggered by user input. Check whether human review is required before the operation executes. If absent, flag. Validator question: does every irreversible, user-triggered high-trust action pass through an explicit human-confirmation gate?

## Patch output
When auditing a high-trust operation triggered by user input with no human gate, emit one patch (`rule_id: R-85`, `location.section` = heading, severity high) proposing the same operation with an explicit human-confirmation gate before the mutation; set `needs_human: true` when whether the operation is high-trust requires judgement.

## Source
Li 2604.02837 §7.1 (prompt injection an open problem, not addressable by template discipline alone); Abdelnabi 2605.17634 §3–4.4 (limit is structural — cannot separate data from instructions without breaking the workflow); Anthropic, "How we contain Claude" (2026) — telemetry: ~93% of permission prompts approved; approval fatigue.
