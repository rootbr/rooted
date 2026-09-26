---
title: Two fields that must change together are updated inside one lock region or replaced as one immutable snapshot
rule_id: CC-10
domain: concurrency
triggers: ['AtomicReference', 'volatile', 'synchronized', 'this[.]\w+\s*=', '[.]lock\(\)']
scope: file
check_kind: semantic
severity_default: major
---

# Two fields that must change together are updated inside one lock region or replaced as one immutable snapshot

## Thesis
When an invariant ties two or more fields — a lower and an upper bound, a value and its version, the coordinates of one point — every write that changes them and every read that uses more than one of them runs inside one `synchronized` or `Lock` region on the same lock; or the fields are gathered into one immutable object held in a `volatile` field or an `AtomicReference` and replaced as a whole, with `updateAndGet` when the new value derives from the old, and never mutated in place.

## Rationale
Making each field `volatile` or atomic on its own orders each single access, not the pair: a reader that runs between the two writes sees the new value of one field and the old value of the other, and the invariant the fields express is false at that instant. A stress test that writes `x = 1; y = 1` and reads `y` then `x` observes `y == 1, x == 0` in 0.09% of samples on plain fields. The two-dimensional point in the `StampedLock` documentation updates `x` and `y` under one write lock, and its readers validate their stamp after reading both before trusting the pair. Replacing an immutable snapshot through `AtomicReference.updateAndGet` gives readers either the old pair or the new pair and no mixture; the function may be re-applied on contention, which is why it is side-effect-free: it builds a new object and never mutates the one it received.

## Example
```java
bad:  private volatile int lo, hi;
      void set(int a, int b) { lo = a; hi = b; }     // reader may see lo = a with the old hi
good: record Range(int lo, int hi) {}
      private final AtomicReference<Range> range = new AtomicReference<>(new Range(0, 0));
      void set(int a, int b) { range.set(new Range(a, b)); }
```

## Limits
Applies to fields that a reader combines or that a writer must keep consistent. Two fields with no invariant between them, fields written only in the constructor, and fields whose every combined access already sits inside one region on the same lock are not flagged. A `StampedLock` optimistic read that validates the stamp after reading both fields is a correct read form. A tolerance stated in the project context — "the pair may be momentarily inconsistent; readers only display it" — rejects the finding.

## Validator
On the triggered hunk find each method that writes two or more fields of the same object in sequence, and each method that reads two fields and combines them. Open the file: decide whether the fields are shared between threads, whether one lock region encloses every combined write and read, or whether the pair lives in one immutable object replaced through a `volatile` field or an `AtomicReference`. Validator question: **can a reader observe the new value of one of these fields together with the old value of another?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-10`, severity major, `file`, `symbol`, `code` = the sequence of field writes or the combined read quoted verbatim from the diff, `fix` = one lock region around the whole update and read, or the immutable snapshot replaced through an `AtomicReference`, `rationale` naming the mixed old-and-new state a reader can observe).

## Source
`java.util.concurrent.locks.StampedLock` class Javadoc, Java SE 21 — the `Point` sample: `move` updates `x` and `y` under one `writeLock`; readers `validate` the stamp before using both. `java.util.concurrent.atomic.AtomicReference#updateAndGet` Javadoc — "Atomically updates ... the current value with the results of applying the given function"; "The function should be side-effect-free, since it may be re-applied when attempted updates fail due to contention among threads". jcstress sample `jmm/basic/BasicJMM_06_Causality.java`, `PlainReads` — `1, 0` (new `y`, old `x`) observed in 0.09% of samples.
