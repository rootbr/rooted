---
title: A skill body mixes all five instruction styles
rule_id: R-22
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# A skill body mixes all five instruction styles

## Thesis
Across the body, ensure the presence of all five instruction styles: descriptive ("Uses dependency injection pattern"), prescriptive ("Follow the validator-per-rule convention"), prohibitive ("Never commit without tests"), conditional ("If the file is hot-tier, apply the hot-tier caps"), and explanatory ("Avoid X because Y rots on edit").

## Rationale
A body that uses only prescriptive sentences cues the model to read everything as an order; mixing styles helps the model classify each rule's strictness and applicability. Conditional phrasing matters most — the model recovers conditional rules only 22.9% of the time when they are not made explicit, so a missing conditional style is the highest-priority gap.

## Example
```
bad:  every sentence prescriptive: "Do X. Do Y. Do Z."
good: "Uses X (descriptive). If hot-tier, apply caps (conditional)."
```

## Limits
Concerns the spread of styles across the body, not any single sentence. A short file may legitimately lean on fewer styles; the check targets monoculture across a substantial body. Categorizing a sentence by style is a reading judgement.

## Validator
Sample 10–15 rule sentences from the body and categorize each by style. If any of the five styles is missing or under 5% of the sample → flag and propose adding one or two sentences in the missing style. Treat an absent conditional style as the highest-priority gap.

## Patch output
When a style is missing or under-represented, emit one patch (`rule_id: R-22`, `location.section` = whole file, `current` = the style distribution, severity low) proposing one or two sentences in the missing style with example phrasings; set `needs_human: true` when phrasing the new rule needs domain knowledge.

## Source
Mohsenimofidi §4.2 (five instruction styles); Yang 2505.13360 §3.2 (conditional rules recovered only 22.9% of the time when not made explicit).
