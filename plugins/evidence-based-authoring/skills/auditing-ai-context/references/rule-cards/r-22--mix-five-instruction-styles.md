---
title: A skill body mixes all five instruction styles
rule_id: R-22
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# A skill body mixes all five instruction styles

## Thesis
Across the body, ensure the presence of all five instruction styles: descriptive ("Uses dependency injection pattern"), prescriptive ("Follow the validator-per-rule convention"), prohibitive ("Never commit without tests"), explanatory ("Avoid X because Y rots on edit"), and conditional — a rule that holds only in some situations names them ("Apply the hot-tier caps to every hot-tier file"). The conditional style is judged by the situation a rule names, in whatever sentence form carries it: a qualifier ("every hot-tier file"), a relative clause or an if-clause.

## Rationale
A body that uses only prescriptive sentences cues the model to read everything as an order; mixing styles helps the model classify each rule's strictness and applicability. A situation left unnamed is guessed poorly: models meet only 22.9% of unstated conditional requirements more than 98% of the time, against 41.1% of unstated requirements overall. A plain instruction that names the situation was followed more often than an if-clause: compliance with one rule appended to a context file was 78.0% and 71.6% on two models when it was written as a plain instruction naming its situation ("every Python function you add or modify"), against 64.2% and 35.6% when the same situation opened the sentence as an if-clause.

## Example
```
bad:  every sentence prescriptive and none naming when it applies: "Do X. Do Y. Do Z."
good: "Uses X (descriptive). Apply the caps to every hot-tier file (prescriptive, its situation named)."
```

## Limits
Concerns the spread of styles across the body, not any single sentence. A short file may legitimately lean on fewer styles; the check targets monoculture across a substantial body. Categorizing a sentence by style is a reading judgement.

## Validator
Sample 10–15 rule sentences from the body and categorize each by style, counting a sentence as conditional, beside its other style, when it names the situation its rule applies in — by a qualifier, a relative clause or an if-clause alike. If any of the five styles is missing or under 5% of the sample → flag and propose adding one or two sentences in the missing style.

## Patch output
When a style is missing or under-represented, emit one patch (`rule_id: R-22`, `location.section` = whole file, `current` = the style distribution, severity low) proposing one or two sentences in the missing style with example phrasings; set `needs_human: true` when phrasing the new rule needs domain knowledge.
