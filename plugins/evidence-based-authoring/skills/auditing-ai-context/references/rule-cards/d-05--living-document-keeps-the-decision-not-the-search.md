---
title: A living document keeps the decision and its determining reason; candidate catalogues, decidedness announcements and "alternatives considered" tables move to a dedicated record
rule_id: D-05
applies_to_target: [doc, context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# A living document keeps the decision and its determining reason; candidate catalogues, decidedness announcements and "alternatives considered" tables move to a dedicated record

## Thesis
A living document states the decision and the one reason that determines it. The material of the search that produced it — a catalogue of candidates kept for a hypothetical future need, an announcement that the decision was taken deliberately, a table of alternatives considered — moves to a dedicated decision record or goes. The decision and its determining reason are never removed; only what surrounds them relocates.

## Rationale
The search and the design have different readers. Someone reading the living document needs enough to arrive at the design and to not depart from it; the candidates weighed on the way answer a question nobody reading now is asking, and they go stale exactly as any other cached copy does. Where the record of that search lives is not a filing detail. Of five decision-record templates compared for comprehension, usability and ease of adoption, the concise one carrying no considered-alternatives section won the overall score. That is a ranking, not a demonstration that the section itself harms — the participants were students and no causal claim about that section was made. It is enough to stop a candidate catalogue from propagating into a document whose job is to describe the present; it is not a licence to delete the decision or the reason that produced it, which is why this rule relocates rather than deletes.

## Example
```
bad:  "We deliberately chose a TTL cache, not an LRU. Alternatives considered: LRU,
      LFU, no cache. Options if needed: a size cap."
good: "Entries expire after `ttl`, because a stale price is worse than a cache miss."
```

## Limits
Covers the search residue around a decision, never the decision, its determining reason, or a present-tense fact that stops a competent maintainer from plausibly departing from it — all three stay in place. Files whose genre is the record of a decision — a dedicated decision record, a changelog, release notes — are the destination, never the target. A named present risk with its remedy is a live obligation rather than a catalogue of options and stays. Residue is not evidence that a rework happened: a document written during the search inherits the search's vocabulary in its first draft.

## Validator
Take the deliberation markers — chosen, adopted, deliberately, consciously, intentionally, considered, rejected, alternative, "if needed", "in case", "options:", "requirement lifted / relaxed / dropped" — from the Phase 0 inventory's marker fields where the static pre-pass has filled them, otherwise grep them directly; add any table or list whose rows enumerate candidates. For each hit ask one binary question: **does a reader who was never in the discussion need this line to arrive at the design, or to avoid departing from it?** No → flag it and name the destination, a dedicated decision record or removal. Then confirm the decision and its determining reason still stand in the document once the proposed cut is applied; a patch that takes either of them out fails its own check.

## Patch output
When a document carries the search that produced its design, emit one patch (`rule_id: D-05`, `location.section` + `line_hint`, `current` = the catalogue, announcement, or table, `proposed: null`, severity medium, `needs_human: true`) naming both the destination and the decision-plus-reason sentence that must survive in place. Choosing between relocation and removal turns on whether a future need is real, which the author decides.

## Source
2604.27333, abstract (five decision-record templates compared by comprehension, usability and ease of adoption; the concise template carrying no considered-alternatives section is the overall-score winner). Caveat: undergraduate participants, a template ranking with no numbers in the abstract and no causal claim about the alternatives section — the finding licenses relocating a candidate catalogue, not deleting a rationale.
