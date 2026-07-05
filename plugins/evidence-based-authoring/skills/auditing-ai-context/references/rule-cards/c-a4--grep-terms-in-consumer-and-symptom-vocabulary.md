---
title: Grep terms must carry the consumer's vocabulary and symptom phrasing, not only the source's terms
rule_id: C-A4
applies_to_target: [kb-card]
check_kind: semantic
severity_default: high
---

# Grep terms must carry the consumer's vocabulary and symptom phrasing, not only the source's terms

## Thesis
The grep fields (`defines`, `uses`, `tags`) must hold the exact terms an agent will search — phrased in the consumer's vocabulary, not only the source's. Beside the canonical term, carry 2–5 symptom terms: the common words a practitioner greps before knowing the canonical name. Symptom terms must be the everyday words of the situation, defensible without sight of any evaluation set — never echoes of specific test queries.

## Rationale
Full-text search is blind to vocabulary that appears only in the source; a card indexed solely in the author's terms is unreachable by a query phrased in the situation's words. The consumer needs a card most exactly when it does not yet know the card's canonical term. Over symptom-phrased queries, every miss traced to this gap — the card indexed in the author's terms, the query in the situation's words — and adding symptom terms to 24 cards lifted recall@5 from 0.63 to 0.80. Echoing specific test queries instead overfits to a benchmark rather than improving retrievability.

## Example
```
rejected: tags: [hypertension]                      # canonical term only
accepted: tags: [hypertension, high blood pressure] # canonical + symptom phrase
```

## Limits
Covers the retrieval vocabulary of the grep fields. The number of terms is a guide, not a hard count. A card whose canonical term is also the lay term needs no separate symptom phrase. Symptom terms that merely paraphrase a known evaluation query are out of scope here and are themselves a defect.

## Validator
Read the grep fields against the thesis: do they include the words a practitioner would search before learning the canonical term, or only the source's terminology? Flag a card whose terms are all author/source vocabulary with no everyday symptom phrasing. Validator question: would a consumer who knows the situation but not the canonical name still retrieve this card?

## Patch output
When auditing a card whose grep terms lack consumer-vocabulary or symptom phrasing, emit one patch (`rule_id: C-A4`, `location.field` = the grep field, severity high). This is a semantic judgement of which lay terms apply, so set `needs_human: true`.

## Source
KB card spec, identity/retrievability rules, group A (grep is blind to source-only vocabulary); Anthropic Contextual Retrieval (recall@5 0.63 → 0.80 after adding symptom terms to 24 cards).
