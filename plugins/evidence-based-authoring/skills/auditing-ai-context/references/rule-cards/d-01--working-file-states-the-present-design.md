---
title: A working file states the present design; a sentence that only parses as a correction of an earlier state is deleted
rule_id: D-01
applies_to_target: [context-file, skill, agent-prompt, doc, code]
check_kind: semantic
severity_default: medium
---

# A working file states the present design; a sentence that only parses as a correction of an earlier state is deleted

## Thesis
A working file describes the design as it now stands. A sentence a reader can parse only by holding an earlier state in mind — "used to", "no longer", "previously", "instead of the old parser", or a date, version or ticket id attached to a line — states nothing about the present and is deleted.

## Rationale
Prose and the thing it describes drift apart as the normal case, not the exceptional one: across Java systems only, 13%–20% of code changes trigger any change to the class or method comment, so the description falls behind by default rather than by neglect. Most of over 3,000 surveyed repositories carry at least one documentation reference to a code element whose every source instance was deleted. A sentence written as a correction compounds this, because its truth depends on a state no current reader can see: nobody can check it, and every later edit must carry it forward. For an agent reader the cost is sharper — a superseded design carries exactly the authority the current rule carries, and a wrong statement reproduced at every step is one of the documented context-rot failure modes, while a single distractor measurably lowers retrieval accuracy.

## Example
```
bad:  # Timeout is now 30s (used to be 5s, see TICKET-412).
good: # Timeout is 30s — the upstream gateway drops idle sockets at 45s.
```

## Limits
Covers a sentence whose meaning depends on a prior state of the same artifact, including dates, version numbers and ticket ids attached to a line, a field, or a section. Files whose genre is history — commit messages, a changelog, release notes, a migration guide, a dedicated decision record — are never scrubbed. A marker word is a candidate, not a verdict: "now" and "was" have innocent present-tense uses, and the systematic error on this axis is over-flagging. Whether a self-standing present fact survives once the comparison is stripped, and so whether the sentence is replaced rather than removed, is a separate disposition.

## Validator
Take the temporal and contrast markers — previously, formerly, originally, in the past, historically, used to, no longer, not anymore, we now (contrastive only), instead of, replaced, switched from, migrated from, changed from, rewrote, deprecated, legacy, old-style, "doesn't suit us", plus two contrastive patterns: was / were with a contrasting "now" in the same sentence, and before either opening a sentence or paired with "now" in it — bare, it is the temporal-ordering sense ("close before flush"), which states nothing about a superseded design — from the Phase 0 inventory's marker fields where the static pre-pass has filled them, otherwise grep them directly; add dates, version numbers and ticket ids attached to a line, and a journal or change-log header at the top of a working file — "Modified by … on …", a running list of edits — whose every entry narrates a change. On a `doc`, `context-file`, `skill` or `agent-prompt` target scan the whole file. On a `code` target scan only the comment and doc-comment spans the static pre-pass extracts for that file's language — the rest of a source file is not Markdown, and its statements, identifiers and string literals are not prose. For each hit ask one binary question: **does a reader who has never seen any prior version of this file need an earlier state in mind to parse this sentence?** Yes → flag.

## Patch output
When a sentence parses only as a correction of an earlier state, emit one patch (`rule_id: D-01`, `location.section` + `line_hint`, `current` = the whole sentence, `proposed: null`, severity medium, `needs_human: true`) whose justification names which present fact, if any, survives once the comparison is stripped. Judging whether a marker is an artifact or an innocent present-tense use is a reading call, so the disposition goes to the author.

## Source
2212.01479 (documentation references to code elements whose every source instance was deleted; most of 3,000+ GitHub projects carry at least one at some point in their history). Wen 2019, ICPC §IV-A p. 6 supplies the co-evolution prevalence — 13%–20% of code changes trigger a class- or method-comment change — for Java systems only. Vishnyakova 2603.09619 §9 (context poisoning: a wrong statement reproduced at every step) with Hong 2025, Context Rot (a single distractor lowers accuracy; direction only, no percentage). Caveat: the rationale is maintenance cost, and no defect-rate claim is carried on this axis.
