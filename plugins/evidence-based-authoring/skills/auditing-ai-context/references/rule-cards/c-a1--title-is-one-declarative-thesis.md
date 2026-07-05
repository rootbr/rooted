---
title: A card title is one complete declarative thesis, never a question or a bare topic
rule_id: C-A1
applies_to_target: [kb-card]
check_kind: mechanical
severity_default: high
---

# A card title is one complete declarative thesis, never a question or a bare topic

## Thesis
The `title` must be a single complete declarative claim — a proposition stated in full — not a question and not a bare topic label. A reader scanning a listing of titles decides from this one line alone whether to open the card.

## Rationale
Retrieval by index scan exposes only the title; the body is never seen until the card is opened. A bare topic ("Meeting hygiene") offers nothing to act on, and a question ("Should long meetings be split?") is undecidable from the index — both cause a relevant card to be skipped or an irrelevant one opened. A proposition is the unit that proposition-level indexing retrieves on.

## Example
```
rejected: Meeting hygiene                  # bare topic — no claim to act on
rejected: Should long meetings be split?   # question — undecidable from the index
accepted: Split any meeting longer than 90 minutes into two sessions with separate agendas
```

## Limits
Covers the title's grammatical form only — whether the thesis is faithful to its source, atomic, or checkable are separate concerns. A title that is a complete imperative clause ("Split any meeting longer than 90 minutes") is declarative in the operative sense and passes.

## Validator
Inspect the `title`: does it end as a question (interrogative form, trailing "?") or read as a noun phrase with no verb (a bare topic)? Either → flag. Test: read the title alone — does it assert something a consumer could act on, or merely name a subject?

## Patch output
When auditing a card whose title is a question or bare topic, emit one patch (`rule_id: C-A1`, `location.field: title`, severity high) rewriting it as one complete declarative proposition; set `needs_human: true` only when the intended claim cannot be recovered from the body.

## Source
KB card spec, identity/retrievability rules, group A (index scan shows only the title); Dense X Retrieval (Chen et al. EMNLP 2024) arXiv:2312.06648 (proposition-level retrieval).
