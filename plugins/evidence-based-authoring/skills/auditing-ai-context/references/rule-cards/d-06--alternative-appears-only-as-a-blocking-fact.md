---
title: An alternative appears only as the subject of a present-tense blocking fact, never as the foil of the decision
rule_id: D-06
applies_to_target: [doc, code, context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# An alternative appears only as the subject of a present-tense blocking fact, never as the foil of the decision

## Thesis
An alternative may be named where it is the subject of a present-tense fact about the environment that blocks it — "the built-in slider tracking is inert inside an open menu". It may not be named as the foil the decision is defined against — "manual tracking, not the built-in action", "we switched because the built-in action did not fire". Both forms mention the same alternative; only the first survives.

## Rationale
A blocking fact is true independently of the decision. A maintainer reaching for the obvious approach is stopped by it, and a reader who never saw the decision being taken can still check it against the environment today. A foil is true only relative to the choice: it parses only for someone who was in the discussion, tells everyone else that a comparison happened without telling them what governs it, and fails silently when the environment changes, because it names nothing re-testable. Rewriting the foil as its blocking fact keeps what prevents the regression and drops what only narrates the path taken.

## Example
```
bad:  # We track the drag manually instead of using the built-in slider action.
good: # Built-in slider tracking is inert inside an open menu — track the drag manually.
```

## Limits
Covers how an alternative is named, not whether it may be mentioned: the same alternative passes as a blocking fact and fails as a foil, so this is a rewrite test rather than a deletion test. A comparison between two live options the reader must themselves choose between is a present decision, not a foil. Where no environmental fact blocks the alternative and the sentence exists only to report that a comparison happened, nothing survives the rewrite and the sentence goes.

## Validator
Find each sentence naming an option the artifact does not use — search for "not", "instead of", "rather than", "unlike", "we switched", "we chose", and comparatives standing beside a named alternative. On a `doc`, `context-file`, `skill` or `agent-prompt` target scan the whole file. On a `code` target scan only the comment and doc-comment spans the static pre-pass extracts for that file's language; the surrounding source is not Markdown and is not prose. For each hit ask one binary question: **is the alternative the grammatical subject of a fact about the environment a reader could check today without knowing this decision was ever taken?** Yes → keep. No → flag.

## Patch output
When an alternative appears as the foil of the decision, emit one patch (`rule_id: D-06`, `location.section` + `line_hint`, `current` = the sentence, `proposed: null`, severity medium, `needs_human: true`) proposing the environmental fact that blocks the alternative, or the sentence's removal where no such fact exists. Which fact blocks it is domain knowledge a reader holding only this file does not have.

## Source
Verified hands-on experience — eval seed 8, `plugins/evidence-based-authoring/skills/auditing-ai-context/evals/seeds/seed8_negative_keep.swift`, the do-not-cut control: a blocking environment fact ("built-in tracking is inert inside a menu's event loop") and a main-thread guardrail both survive an artifact purge unchanged, while the same alternative stated as a foil does not.
