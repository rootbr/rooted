---
title: An identifier encoding a superseded design is renamed to state present intent
rule_id: D-03
applies_to_target: [code, doc]
check_kind: semantic
severity_default: low
---

# An identifier encoding a superseded design is renamed to state present intent

## Thesis
A name that encodes a design no longer in the artifact — a version suffix, a `new` / `old` / `legacy` prefix, an `improved` / `refactored` / `temp` / `compat` / `shim` qualifier — is renamed to state what the thing does now, and every reference to the old name is renamed with it.

## Rationale
A name is read far more often than the declaration it sits on, and it is the one piece of prose a reader cannot skip. `parseConfigV2` asserts that a first parser exists somewhere and that choosing between the two matters; once it is the only parser, the suffix is a false claim the reader has to disprove by search, on every encounter. The old name also propagates outward: documentation keeps naming code elements after every source instance of them is gone, in most of over 3,000 surveyed repositories, and a rename left half-finished is one event that produces exactly that dangling reference.

## Example
```
bad:  export function parseConfigV2(raw) { … }   // the only parser in the project
good: export function parseConfig(raw) { … }     // every call site renamed with it
```

## Limits
Applies where the encoded design is genuinely gone. A version suffix separating two live things — two protocol revisions both in service, two schema generations both readable — names a real distinction and stays. A genuine shim bridging a real external constraint keeps its name, because the qualifier is a false claim only when nothing remains for it to contrast with. The rename's follow-through spans every reference in the repository, which a reader holding one file cannot enumerate.

## Validator
Take the identifier smells — `*V2` / `*V3`, `New*`, `Old*`, `Legacy*`, `*Improved`, `*Refactored`, `Temp*`, `*Compat`, `*Shim` — from the Phase 0 inventory where the static pre-pass has filled them, otherwise grep them directly. On a `code` target read the declarations and their call sites in the source itself, not only the comment spans the pre-pass extracts: an identifier is code, and the Markdown-shaped checks do not apply to the file around it. On a `doc` target read the identifiers named in prose and inside fenced examples. For each hit search the repository with `Grep` for the counterpart the name implies — the first version, the non-legacy twin, the pre-refactor original. Then ask one binary question: **does the thing this name contrasts with still exist in the repository?** No → flag the name.

## Patch output
When an identifier encodes a design that no longer exists, emit one patch (`rule_id: D-03`, `location.section` + `line_hint`, `current` = the identifier, `proposed: null`, severity low, `needs_human: true`) proposing a name that states present intent, and record in the justification that the rename must reach every reference — a repository-wide follow-up a single-file reader cannot complete.

## Source
Verified hands-on experience — eval seed 7, `plugins/evidence-based-authoring/skills/auditing-ai-context/evals/seeds/seed7_old_name.ts`: `parseConfigV2` becomes `parseConfig` with its call site updated, once it is the only parser in the file. 2212.01479 supplies the propagation half — most of 3,000+ GitHub projects carry at least one documentation reference to a code element whose every source instance was deleted.
