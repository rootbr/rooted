---
title: An invariant is an obligation stated with must or the plain indicative, never a should, prefer or try to
rule_id: META-05
domain: meta
triggers: ['^\s*\d+[.]\s+\*\*', '\bshould\b', '\bprefer', '\btry to\b', '(?i)where possible|as far as possible|if possible|ideally|avoid\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# An invariant is an obligation stated with must or the plain indicative, never a should, prefer or try to

## Thesis
The rule clause of an invariant binds: `must`, `must not`, `never`, `no … may`, or the plain indicative (`X calls no Y`). `should`, `prefer`, `try to`, `avoid where possible`, `as far as possible` mark a recommendation, and a reviewer cannot fail a diff on a recommendation; such text is rewritten as an obligation with its enforcement named, or moved out of the invariant list into a notes section where it binds nothing.

## Rationale
In the vocabulary of requirement levels, `must` means the definition is an absolute requirement, while `should` means there may exist valid reasons in particular circumstances to ignore the item once its implications are weighed. A finding raised against a `should` is therefore always answerable — "this is one of the circumstances" — and the author, not the rule, decides each time. A loophole phrase — `as far as possible` — says the requirement is fulfilled only to an imprecisely defined extent, which leaves room for subjective misinterpretation when the change is accepted. Either the rule is enforced and reads as an obligation, or it is advice and stays out of the list a finder cites.

## Example
```java
bad:  9. **Controllers avoid JPA**: Controllers should avoid direct JPA access.
         Violation: JPA in a controller.
good: 9. **Web adapters never touch persistence**: No class in `..adapter.in.web..`
         depends on a class in `..adapter.out.persistence..`. Violation: an import
         of `..adapter.out.persistence..` from `..adapter.in.web..`. Enforced by
         ArchUnit rule `WebAdapterDoesNotDependOnPersistence`.
```

## Limits
Applies to the rule clause of a numbered invariant. A `should` in a tolerances, notes or rationale section of the config, outside the invariant list, is not a finding. `avoid` followed by a concrete construct and no qualifier (`avoid String.format in onEvent`) reads as a prohibition and is tolerated; `avoid where possible` is not.

## Validator
Open the config at HEAD and take each numbered invariant the diff adds or changes. In its rule clause — the text before `Violation:` — grep for `should`, `prefer`, `try to`, `where possible`, `as far as possible`, `if possible`, `ideally`. Confirm the line sits in the invariant list, not in a notes or tolerances section. Validator question: **is this invariant's rule clause a recommendation a diff cannot be failed on?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-05`, severity minor, `file` = the config path, `symbol` = `Inv <N>` for the invariant's number, `code` = the invariant line quoted verbatim from the diff, `fix` = the invariant rewritten as an obligation with its enforcement, or the line moved under a notes heading, `rationale` naming that a recommendation admits a valid reason to ignore it in each case).

## Source
RFC 2119 §1 and §3 — MUST: "the definition is an absolute requirement of the specification"; SHOULD: "there may exist valid reasons in particular circumstances to ignore a particular item, but the full implications must be understood and carefully weighed before choosing a different course" (text verified against a mirrored copy; the RFC defines the capitalised keywords for specifications, and the card applies the same levels to a project's lowercase rule text). arXiv:1611.08847 §3.2 — the smell "Loopholes": "phrases that express that the following requirement must be fulfilled only to a certain, imprecisely defined extent", example "As far as possible, inputs are checked for plausibility"; §1 — such phrasing "leaves room for subjective (mis-)interpretation".
