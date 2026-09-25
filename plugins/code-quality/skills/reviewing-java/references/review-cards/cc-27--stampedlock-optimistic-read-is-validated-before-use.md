---
title: A StampedLock optimistic read validates its stamp before using the values it read
rule_id: CC-27
domain: concurrency
triggers: ['tryOptimisticRead\(', 'StampedLock', '[.]validate\(']
scope: hunk
check_kind: semantic
severity_default: major
---

# A StampedLock optimistic read validates its stamp before using the values it read

## Thesis
Every value read between `tryOptimisticRead()` and `validate(stamp)` is copied into a local and used only after `validate` returns true; when it returns false, the code re-reads under `readLock()` or retries.

## Rationale
`tryOptimisticRead` acquires nothing: it returns a stamp that records the lock's version. A writer may take the write lock at any point during the optimistic section, so the fields read there may come from before and after a write — a torn view of two states. `validate(stamp)` returns true only if the lock has not been exclusively acquired since the stamp was issued, and only then are the reads guaranteed to happen after the last write; otherwise there is no guarantee the reads obtained a consistent snapshot. Without a validate, or with the values used before it, the code computes on a mix of two states and nothing signals it. A side effect inside the section — a write, a call that publishes the values — has already happened when validation fails and cannot be retracted, and a method outside the class may itself take the lock, which is not reentrant.

## Example
```java
bad:  long s = lock.tryOptimisticRead();
      double d = Math.sqrt(x * x + y * y);              // fields used before validate
      if (!lock.validate(s)) { /* ignored */ }
      return d;
good: long s = lock.tryOptimisticRead();
      double cx = x, cy = y;
      if (!lock.validate(s)) { s = lock.readLock(); try { cx = x; cy = y; } finally { lock.unlockRead(s); } }
      return Math.sqrt(cx * cx + cy * cy);
```

## Limits
Applies to `tryOptimisticRead`. A `readLock()`/`unlockRead` pair needs no validate. An optimistic section that reads one field whose every value is self-consistent and validates before returning it is correct; the finding is use before validation, including a false branch that continues with the values instead of falling back. A section that calls `validate` repeatedly between reads is the documented alternative to a single validate at the end. The section is assumed to have the documented shape — field reads into locals, no write, no call outside the class; a section that performs a side effect is not repaired by validation, since the effect has happened before `validate` can fail, and lies outside this finding.

## Validator
On the triggered hunk find each `tryOptimisticRead()` and follow the code to the matching `validate(stamp)`. Between them, note each field read and the local it lands in. After: the locals are used only on the true branch, and the false branch re-reads under `readLock()` or loops; a false branch that continues with the values is a use before validation. Validator question: **is any value read optimistically used, written out or passed on before `validate` returned true for its stamp?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-27`, severity major, `file`, `symbol`, `code` = the optimistic section quoted verbatim from the diff, `fix` = the locals, the validate check and the read-lock fallback, `rationale` naming the torn view when a writer intervenes).

## Source
`java.util.concurrent.locks.StampedLock` class Javadoc, Java SE 21 — "Method tryOptimisticRead returns a non-zero stamp only if the lock is not currently held in write mode. Method validate returns true if the lock has not been acquired in write mode since obtaining a given stamp"; "Optimistic read sections should only read fields and hold them in local variables for later use after validation. Fields read while in optimistic read mode may be wildly inconsistent, so usage applies only when you are familiar enough with data representations to check consistency and/or repeatedly invoke method validate()"; the design "relies on ... the associated code sections being side-effect-free"; reads between `tryOptimisticRead` and `validate` are ordered after prior writes "only if a later validate returns true; otherwise there is no guarantee that the reads ... obtain a consistent snapshot"; the class's own `distanceFromOrigin` example.
