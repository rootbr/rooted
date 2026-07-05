---
title: A card's body blocks must be present and in the corpus's fixed order
rule_id: C-F1
applies_to_target: [kb-card]
check_kind: mechanical
severity_default: medium
---

# A card's body blocks must be present and in the corpus's fixed order

## Thesis
Every card must carry the corpus's fixed sequence of body blocks, present and in order — thesis, then rationale, then example, then the scope/limits block, then any terminology block, then the consumer block. A missing block or a reordered one breaks the uniform shape.

## Rationale
One schema across the whole corpus yields a predictable parse: a consumer or validator reading any card knows which block holds which kind of content and where the grep context for a term will sit. When blocks are missing or shuffled, that predictability is lost — the reader cannot rely on position to find the thesis, the scope, or the application, and mechanical checks that key off block order misfire.

## Example
```
rejected: Rationale appears before the Thesis; the limits block is omitted.
accepted: Thesis → Rationale → Example → Limits → [Terminology] → consumer block, in order.
```

## Limits
Covers the presence and ordering of the required blocks. The number and name of the consumer block specifically, the inner form of the example, and the content quality of each block are separate concerns. An optional block (such as terminology) may be absent when not needed; the required blocks may not.

## Validator
Parse the body headings into a sequence and compare against the corpus's required block list: flag any required block that is missing and any block out of the prescribed order. Validator question: does this card present the corpus's blocks, all present, in the fixed sequence?

## Patch output
When auditing a card with a missing or misordered body block, emit one patch (`rule_id: C-F1`, severity medium) proposing the corrected block set and order. Block presence and order are mechanically decidable, so no `needs_human` flag.

## Source
KB card spec, structural-consistency rules, group F (one schema across the corpus yields predictable parse and grep context).
