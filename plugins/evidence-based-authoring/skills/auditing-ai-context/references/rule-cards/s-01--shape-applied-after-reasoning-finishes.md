---
title: The output's shape is applied after reasoning finishes, never as a constraint on it
rule_id: S-01
applies_to_target: [answer, doc, context-file, skill, agent-prompt]
check_kind: semantic
severity_default: high
---

# The output's shape is applied after reasoning finishes, never as a constraint on it

## Thesis
A shape constraint — an output schema, a length cap, a mandated opening, a fixed layout — governs the delivered artifact only. It is applied once the reasoning that produces the content has finished, and never binds that reasoning while it runs.

## Rationale
Shaping and reasoning draw on the same capacity, and the loss is measured. Against information-matched prose controls, over 4 models and 5 benchmarks with 0% parse failures, a schema imposed up front cost a small model 36.2 pp (p < 0.0001, largely truncation) and a mid-sized one 28.0 pp (p < 0.001, capacity competition rather than truncation). The strongest model in the set still lost 5.3 pp on a hard benchmark under JSON (96.2% → 91.0%), while a large model on an easier benchmark lost nothing (88.7 ± 4.0% under JSON against 89.3 ± 1.7% unconstrained). The penalty scales with schema complexity (McNemar p < 0.0001) and is not explained by prompt length. Reasoning freely and formatting afterwards recovers most of what was lost: 80–87% over a 3-run mean.

## Example
```
bad:  "Answer as one JSON line, verdict first." — the work happens inside the schema
good: work the problem out first, then cast the finished verdict into one JSON line
```

## Limits
Covers the ordering of shaping against reasoning, not which shape is right. The cost tracks spare capacity, so a constraint a large model absorbs can be expensive on a small one — the rule binds hardest wherever the cheapest model runs. A shape stated as a property of the finished artifact is in scope to keep; the defect is a shape that must be satisfied while the content is still being worked out.

## Validator
For each shape constraint — output schema, length cap, mandated opening, fixed layout — ask what it governs: the delivered artifact, or the work that produces it. Flag a constraint written so the producer must satisfy it from the first token, and any brevity or format rule that states no boundary between the artifact and the reasoning budget. Validator question: can the producer reason freely and shape afterwards, or does the shape bind the thinking?

## Patch output
When auditing text whose shape constraint binds the reasoning rather than the delivered artifact, emit one patch (`rule_id: S-01`, `location` set to the heading and line hint, `current` = the constraint as written, severity high) proposing that the constraint be scoped to the finished artifact. Judging what a constraint governs requires reading intent, so set `proposed: null` and `needs_human: true`.

## Source
Capacity, Not Format 2606.09410 (4 models × 5 benchmarks, 0% parse failures: −36.2 pp p < 0.0001; −28.0 pp p < 0.001; 96.2% → 91.0% under JSON; 88.7 ± 4.0 vs 89.3 ± 1.7 unaffected; penalty scales with schema complexity, McNemar p < 0.0001; delayed-structure recovery 80–87%); Tam 2408.02442 (significant decline in reasoning under format restrictions; stricter constraints degrade more — no figures in the abstract); Lanham 2307.13702 (step-by-step reasoning before answering improves performance).
