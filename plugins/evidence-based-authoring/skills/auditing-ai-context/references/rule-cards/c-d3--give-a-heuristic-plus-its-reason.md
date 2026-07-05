---
title: A card gives a heuristic plus its reason, avoiding both rigid step-lists and vague slogans
rule_id: C-D3
applies_to_target: [kb-card]
check_kind: semantic
severity_default: medium
---

# A card gives a heuristic plus its reason, avoiding both rigid step-lists and vague slogans

## Thesis
A card must pitch its guidance at the right altitude: a heuristic together with the reason it holds — neither a brittle hardcoded step-list nor a vague slogan. Unexplained emphasis, including bare ALL-CAPS directives with no rationale, is not allowed.

## Rationale
The useful altitude sits between brittle hardcoded logic, which breaks the moment the situation differs from the script, and vague guidance, which gives the consumer nothing concrete to act on. Stating why a rule holds — not only what to do — lets the model generalize the rule to cases the author did not enumerate; a slogan or a rigid list both fail to transfer.

## Example
```
rejected: ALWAYS SPLIT MEETINGS. (slogan, no reason)
accepted: Split meetings over ~90 minutes — attention and decision quality fall past that
          length, so two focused sessions outperform one long block.
```

## Limits
Covers the altitude and the presence of reasoning. It does not forbid a short procedure where the task genuinely is a fixed sequence, nor require lengthy justification for a self-evident point. The defect is guidance with no reason (a slogan) or guidance so rigid it cannot transfer (a brittle script).

## Validator
Read the guidance: is it a heuristic with its reason, or has it collapsed into a bare step-list or an unexplained slogan? Flag rigid hardcoded procedures, vague directives with no rationale, and unexplained ALL-CAPS. Validator question: could the consumer apply this to a case the card did not enumerate, because it knows why the rule holds?

## Patch output
When auditing a card pitched as a slogan or a brittle step-list, emit one patch (`rule_id: C-D3`, severity medium) proposing a heuristic-plus-reason rewrite. Judging the right altitude is semantic, so set `needs_human: true`.

## Source
KB card spec, consumer-applicability rules, group D; Anthropic (the right altitude between brittle logic and vague guidance); skill-authoring best practices (explain why, not only what — the model generalizes from reasons).
