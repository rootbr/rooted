---
title: Every term an invariant turns on is a concrete identifier or is defined once in the config
rule_id: META-04
domain: meta
triggers: ['^\s*\d+[.]\s+\*\*', '[Ii]nvariant', 'hot path', '(?i)steady state|cold start|tenant|critical path|core (path|loop)', '(?i)as usual|as agreed|the usual|convention|obvious|everyone knows']
scope: file
check_kind: mechanical
severity_default: minor
---

# Every term an invariant turns on is a concrete identifier or is defined once in the config

## Thesis
A word the enforcement of an invariant depends on — `hot path`, `tenant`, `steady state`, `the domain`, `the usual way` — is either a concrete identifier (a class, method, package, annotation, or a listed set of them) or defined exactly once in the config's definitions section and used with that one meaning by every invariant. An invariant that defers to unwritten knowledge — `as agreed`, `the team convention`, `obviously` — is the same defect with the whole rule as the undefined term.

## Rationale
Subjective language is a word whose semantics is not objectively defined; an open-ended term offers a choice of possibilities to whoever reads it; a rule built on either is difficult or impossible to verify and allows more than one interpretation. For a reviewer that is fatal: two readers of "the hot path must not block" bound the hot path differently, so one flags a change the other passes, and the author can answer either with a third reading. A term pinned to identifiers — `Dispatcher#onEvent`, `RequestLoop#tick` — or to one definition the config owns has one reading, and two invariants that use it cannot silently mean different things. A rule that lives only in what "everyone knows" cannot be cited in a finding at all, so for the reviewer it does not exist until it is written.

## Example
```java
bad:  3. **The hot path never blocks**: Code on the hot path must not block.
         Violation: blocking on the hot path.
good: 3. **Hot-path methods never block**: `Dispatcher#onEvent` and `RequestLoop#tick`
         (the hot-path list under Definitions) call no `Thread.sleep`, `Object.wait`,
         `LockSupport.park` or `Future.get` without a timeout. Violation: any of
         those calls inside the two methods.
```

## Limits
Applies to a term the rule's scope or test depends on. An adjective of size, speed or cost — `large`, `slow`, `expensive` — is a missing measure, not an undefined term, and is out of scope here. A term defined once under a definitions heading of the same config counts as defined wherever it is used; a term two invariants define differently is a finding on the later one. Ordinary Java and framework vocabulary — `monitor`, `executor`, `entity`, `repository`, `controller` — needs no definition. A noun that names what the subject's own identifiers hold or return (`balance` for `Totals#transfer`, `repository` for a class annotated `@Repository`) is resolved by the identifier and needs no definition.

## Validator
Open the config at HEAD and take each numbered invariant the diff adds or changes. List the terms its subject and its `Violation:` clause depend on that are not Java identifiers, package patterns, ordinary Java or framework vocabulary, or nouns the subject's own identifiers resolve. For each, grep the config for a definition — a definitions section, a list of members, an inline identifier list — and check that no other invariant defines it differently. Treat a rule whose content is deferred to unwritten agreement as a term without a definition. Validator question: **does this invariant depend on a term that the config defines nowhere, or defines differently elsewhere?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-04`, severity minor, `file` = the config path, `symbol` = `Inv <N>` for the invariant's number, `code` = the invariant line quoted verbatim from the diff, `fix` = the invariant with the term replaced by identifiers or by a reference to its one definition, `rationale` naming the term and the two readings it admits).

## Source
arXiv:1611.08847 §3.2 — smells derived from the ISO/IEC/IEEE 29148 requirements language criteria, whose violation results "in requirements that are often difficult or even impossible to verify or may allow for multiple interpretations"; "Subjective Language refers to words of which the semantics is not objectively defined"; "Open-ended, non-verifiable terms are hard to verify as they offer a choice of possibilities". ISO/IEC/IEEE 29148:2011, requirements language criteria — quoted through the paper (its p. 12 anchor); the standard itself was not fetched from the authoring environment.
