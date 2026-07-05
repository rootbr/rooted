---
title: ALL-CAPS prohibitions capped at three per file, each tied to safety or data integrity
rule_id: R-62
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# ALL-CAPS prohibitions capped at three per file, each tied to safety or data integrity

## Thesis
Count the ALL-CAPS markers (MUST, MUST NOT, SHALL, SHALL NOT, NEVER, ALWAYS, ONLY) in the body. The soft ceiling is 3 per file. Each remaining capitalized marker must pair with a one-sentence rationale, so the agent can judge edge cases rather than mimic edicts; a bare ALL-CAPS marker is a yellow flag.

## Rationale
Caps compound: each prohibition spreads the attention budget across constraint enforcement, and the marginal cost rises with every additional rule (the bundling tax). Reserve ALL-CAPS for safety, compliance, and data integrity, where the cost of mis-application is severe enough to justify the handcuff effect on model behavior.

## Example
```
bad:  MUST indent. NEVER commit binaries. MUST lint. MUST add tests. MUST update CHANGELOG.
good: Indent 2 spaces; tests cover new paths; update CHANGELOG. Linter MUST pass (blocks shared CI).
```

## Limits
The ceiling of 3 is a soft target on the body, not the `description`. Markers that are genuinely safety-, compliance-, or data-integrity-class may stay above a style downgrade, but even those need an adjacent rationale; only when the safety-class count itself exceeds 3 is the body over-strict. Style-class markers are always candidates for downgrade.

## Validator
Inventory every ALL-CAPS marker in the body. (1) Count them. (2) Classify each as safety, data-integrity, compliance, or style. (3) Any style-class marker → propose downgrading to SHOULD or to positive framing. (4) More than 3 in the safety class → flag the body as over-strict. (5) Any marker with no adjacent rationale → propose adding one or downgrading.

## Patch output
When the ALL-CAPS count exceeds the ceiling or a marker is unjustified, emit one patch (`rule_id: R-62`, `location` set to the heading and line hint, `current` = the marker rule, severity medium) proposing a downgrade to SHOULD, a positive rephrase, or an added rationale.

## Source
Anthropic skill-creator guidance (bare ALL-CAPS = yellow flag; pair with hoisted rationale); Yang 2505.13360 §3.4 (bundling tax — marginal cost rises per rule).
