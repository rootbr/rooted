---
title: Prefer hot/warm inclusion over retrieval for content reused within a session
rule_id: R-18
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: low
---

# Prefer hot/warm inclusion over retrieval for content reused within a session

## Thesis
Prefer hot/warm inclusion for anything used within a session; reserve MCP / search retrieval for rarely-touched specs.

## Rationale
Long-context retention outperforms fact-extracted retrieval by 33–35 pp on two memory benchmarks (a third shows only a 7.3 pp gap). Retrieval pays off only at ~10+ reuses of ~100k-token content with caching.

## Example
```
bad:  "Retrieve the coding conventions from the vector store each turn."
good: "Keep the coding conventions in a cold-tier file referenced from SKILL.md."
```

## Limits
Content with truly low reuse and large volume (full API specs, schemas referenced ad hoc) belongs in cold tier or external retrieval — the rule favors inclusion only for content reused within typical sessions.

## Validator
When the file recommends "retrieve from <vector store>" or "look up in <RAG index>" for content reused within typical sessions, flag — propose moving the content into a cold-tier file referenced from SKILL.md.

## Patch output
When a retrieval-based instruction covers content reused in-session, emit one patch (`rule_id: R-18`, `current` = retrieval-based instruction, `proposed` = inclusion-based instruction, severity low). Set `needs_human: true` when the reuse frequency cannot be judged from the file.

## Source
Pollertlam 2603.04814 §4.1, Table 3 (long-context retention beats retrieval by 33–35 pp on LoCoMo/LongMemEval; PersonaMem v2 gap 7.3 pp); §4.3 (break-even ~10+ reuses of ~100k-token content with caching).
