---
title: Bound history growth by summarizing or truncating past about 20 turns
rule_id: R-16
applies_to_target: [skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# Bound history growth by summarizing or truncating past about 20 turns

## Thesis
For skills that manage conversational state or store transcripts, prescribe summarization or window-based truncation rather than unbounded retention.

## Rationale
Transcripts grow O(T²) in tokens because each turn re-encodes prior turns. Past ~20 turns, stale context degrades accuracy; the exact threshold is provider-specific.

## Example
```
bad:  "Keep all prior turns in the prompt."
good: "Summarize turns older than the last 20; keep recent turns verbatim."
```

## Limits
The ~20-turn figure is provider-specific, not a universal cutoff. Applies only where a skill retains conversational state or transcripts; a skill that holds no history is out of scope.

## Validator
Grep for "transcript", "history", "all prior turns", "full conversation". For each usage: if it names an explicit summarization or truncation policy → keep; if it implies unbounded retention → flag.

## Patch output
When a skill implies unbounded history retention, emit one patch (`rule_id: R-16`, `current` = unbounded-history instruction, `proposed` = same instruction with an explicit window or summarization policy, severity medium).

## Source
Tokalator 2604.08290 §1, Eq. 1 (O(T²) growth; rot past ~20 turns, threshold provider-specific per §3.2.1, relaying Hong 2025); Gao & Peng 2510.16786 §1.
