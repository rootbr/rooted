---
title: No two invariants demand states of one subject that cannot both hold
rule_id: META-07
domain: meta
triggers: ['^\s*\d+[.]\s+\*\*', '[Ii]nvariant', '\bmust\b', '\bnever\b', '(?i)\ball\b']
scope: file
check_kind: semantic
severity_default: minor
---

# No two invariants demand states of one subject that cannot both hold

## Thesis
For every subject two invariants both govern there is at least one implementation that satisfies both. Where two rules pull against each other — all mutations flush under one monitor, and no monitor is held across I/O, while the flush writes to disk — the config writes the tension as a resolved tradeoff in the text of one invariant: which rule holds on which path, and the mechanism that keeps the other. Two absolute rules that cannot both be satisfied are one finding on the pair.

## Rationale
Two requirements that cannot be satisfied at the same time stand in an inconsistency relation, and a specification in that state has no correct implementation: any diff violates one rule or the other, and a reviewer enforcing both flags every change, or picks a side the project never chose. Architecture evaluation names a tension between two qualities as a tradeoff to be decided by a stated criterion, so a config that leaves both rules standing has skipped that decision. Written into the invariant, the resolution names the lock the mutation takes, the executor the I/O moves to, the path on which each rule applies; the reviewer then has one rule per path instead of a contradiction per diff.

## Example
```java
bad:  4. **Mutations flush under one monitor**: All mutations flush through a single
         `synchronized` region. Violation: a flush outside the region.
      5. **No monitor across I/O**: No method holds a monitor across I/O.
         Violation: I/O inside a `synchronized` block.   (the flush writes to disk)
good: 4. **Snapshot mutations flush under the snapshot lock**: Mutations of the
         in-memory snapshot flush under `ReentrantLock#lock`; disk persistence runs on
         the persistence executor via `PersistenceAdapter`. Violation: a disk write
         inside the lock region.
```

## Limits
Applies to invariants over one subject whose forbidden states, taken together, exclude every implementation. Two rules that are hard to satisfy together but admit one design — a lock-free path and a bounded allocation — are a tension resolved by the code, not a contradiction. A pair the config already resolves (`Inv 5 applies outside the snapshot region`) is correct.

## Validator
Open the config at HEAD and take each numbered invariant the diff adds or changes. For each other invariant over the same subject — class, method, package, resource, lock — take the two `Violation:` clauses and ask whether an implementation exists that exhibits neither; use the definitions section to bound the subject. Where the config states which rule holds on which path, the pair is resolved. Validator question: **is there a subject for which satisfying this invariant necessarily produces another invariant's forbidden state?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-07`, severity minor, `file` = the config path, `symbol` = `Inv <N>` for the added invariant's number, `code` = the two invariant lines quoted verbatim, the added one from the diff, `fix` = one invariant rewritten with the path split or the mechanism that satisfies both, `rationale` naming the implementation that neither rule admits).

## Source
arXiv:2103.02255 §5.1.1, Definition 5.1 — "If two requirements Req1 and Req2 cannot be satisfied meanwhile, there is an inconsistency relation between them". arXiv:2506.00150 §2 — "the tradeoffs for each scenario reflect the tensions between two or more qualities, thus a criterion must be used to prioritize and select between several scenarios during the brainstorming sessions"; the paper's criterion selects between scenarios, and the remedy of resolving the tension in the text of one invariant is the card's reading of a tradeoff decided by a criterion.
