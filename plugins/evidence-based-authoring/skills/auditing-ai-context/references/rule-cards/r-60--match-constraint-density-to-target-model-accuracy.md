---
title: Match constraint density to target-model accuracy
rule_id: R-60
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# Match constraint density to target-model accuracy

## Thesis
Set the number of hard constraints from the target model's measured accuracy on the task. When eval accuracy is below 90%, add hard constraints (Sculpting-style). At 90–95%, A/B test both densities — the outcome depends on the prompt class. Above 95%, keep prompts simple and goal-oriented and minimize prohibitions.

## Rationale
Hard constraints that raise a mid-tier model by +4 points can degrade a frontier model by ~2.4 points: the same constraint set helps below the accuracy ceiling and handcuffs above it. Implicit-rule inference also varies by model — one model recovers 44.7% of unstated requirements while another recovers only 24.5% — so a file tuned on a frontier model under-specifies for smaller models.

## Example
```
bad:  frontier-target skill loaded with 9 MUST/ONLY prohibitions
good: frontier-target skill: goal-oriented prose, prohibitions reserved for safety
```

## Limits
The numeric accuracy-to-density mapping rests on OpenAI-model measurements; transferring the thresholds to other model families is an extrapolation. The *direction* is vendor-confirmed for the Claude family: newer generations over-trigger on aggressive "CRITICAL: You MUST" language, and skills authored for prior models are often too prescriptive for the newest tier and can degrade output — but no numeric threshold is published. The check needs the target model's tier: if frontmatter pins `model: <id>`, audit constraint count against that tier; if no model is pinned, default to a broad target with moderate constraints and positive framing.

## Validator
Determine the target model from frontmatter (`model: <id>`) or treat as broad/unspecified. Count hard constraints and ALL-CAPS prohibition markers in the file. For a frontier-tier or unspecified-broad target carrying a dense prohibition set, flag the mismatch; for a low-accuracy target carrying almost no constraints, flag under-specification. The judgement of which tier the file is really aimed at is the semantic call.

## Patch output
When auditing constraint density against the declared or inferred model target, emit one patch (`rule_id: R-60`, `location` set to the heading or frontmatter plus the model target, `current` = constraint and ALL-CAPS counts, severity medium) proposing to reduce, increase, or rephrase constraints for the tier; set `needs_human: true` when the intended tier is ambiguous.

## Source
Khan 2510.22251 §4.2, §4.4 (+4 pts gpt-4o vs −2.4 pts GPT-5), §6.2.1, §6.3.2 (OpenAI-only; Claude-tier mapping is extrapolation); implicit-rule recovery 44.7% vs 24.5%. Anthropic, Claude prompting best practices + per-model guides (2026: dial back "CRITICAL: You MUST" trigger language on Opus 4.5+; "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality").
