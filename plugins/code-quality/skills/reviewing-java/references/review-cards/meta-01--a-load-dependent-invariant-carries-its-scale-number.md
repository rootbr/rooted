---
title: An invariant whose enforcement depends on load carries the scale number that makes it auditable
rule_id: META-01
domain: meta
triggers: ['^\s*\d+[.]\s+\*\*', '[Ii]nvariant', 'hot path', '(?i)latenc|throughput|allocat|heap|per (request|call|second)|p9[059]', '(?i)\b(large|small|heavy|cheap|expensive|fast|slow)\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# An invariant whose enforcement depends on load carries the scale number that makes it auditable

## Thesis
An invariant whose rule depends on traffic shape — an allocation, latency, throughput, memory, lock-hold or call-rate rule, or one that grades a construct as `large`, `slow` or `expensive` — states the number that fixes the bar: the rate at which the subject runs, the budget per operation, or the target the response is measured against, with a unit. Without it a diff that adds a 16-byte allocation and one that adds a 16-KiB buffer read as the same change, and a reviewer can neither pass nor fail either.

## Rationale
A quality-attribute rule is a scenario with a stimulus and a way to measure the response; the measure is what turns "avoid large objects" into a check with an answer. Adjectives of size, speed and cost — `large`, `significant`, `minimal`, `fast` — are unspecific by nature: they allow more than one reading, so the rule cannot be verified, only argued about. With the number in place the reviewer multiplies: a new 48-byte allocation inside a method that runs ~50 M times a day is ~2.4 GB a day of churn, and that product is compared against the invariant's budget line. Without it the same allocation is a matter of taste, and the rule is enforced differently by every reader.

## Example
```java
bad:  5. **No large objects on the heap**: Avoid large objects in the dispatcher.
         Violation: heap churn.
good: 5. **Dispatcher allocations stay under 256 bytes**: No single allocation inside
         `Dispatcher#onEvent` exceeds 256 bytes retained; the method runs ~50 M times
         a day, so every 256 bytes allocated per call is ~12.8 GB/day of churn.
         Violation: an allocation over 256 bytes inside `Dispatcher#onEvent`.
```

## Limits
Applies to an invariant whose check changes with load. A structural invariant — a dependency direction, a package boundary, a naming rule, an annotation requirement — is the same check at any traffic and needs no number. A domain term (`hot path`, `tenant`) is an undefined term, not a missing measure, and is out of scope here. A number stated once in a definitions or scale section of the same config and referenced by the invariant counts as present.

## Validator
Open the config at HEAD and take each numbered invariant the diff adds or changes. Decide whether its rule depends on load: it names allocation, latency, throughput, memory, lock hold time, a call or request rate, a hot path, or an adjective of size, speed or cost. For such an invariant, grep its text and the config's definitions or scale section for a number with a unit or a rate — `256 bytes`, `~50 M/day`, `p99 ≤ 5 ms`. Validator question: **does this load-dependent invariant leave the reviewer without a rate, budget or target against which an added line could be measured?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-01`, severity minor, `file` = the config path, `symbol` = `Inv <N>` for the invariant's number, `code` = the invariant line quoted verbatim from the diff, `fix` = the invariant rewritten with the rate, budget or target and its unit, `rationale` naming the measure the rule lacks and the comparison it would allow).

## Source
arXiv:2506.00150 §2 — a quality scenario "is characterized by stimuli to which an architecture (or system) must respond and a way to measure the quality-attribute response triggered by the stimuli". arXiv:1611.08847 §3.2 — the ISO/IEC/IEEE 29148 requirements language criteria, whose violation yields requirements "often difficult or even impossible to verify"; the smell "Ambiguous Adverbs and Adjectives": words "unspecific by nature, such as almost always, significant and minimal". The number-with-unit form is the card's operational reading of "a way to measure"; the sources state the measure requirement and the adjective defect.
