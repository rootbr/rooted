---
title: A StampedLock is not reentrant, so code holding a stamp calls no method that acquires the same lock
rule_id: CC-43
domain: concurrency
triggers: ['StampedLock', 'writeLock\(\)', 'readLock\(\)', 'tryOptimisticRead\(', 'unlockWrite\(', 'unlockRead\(']
scope: file
check_kind: semantic
severity_default: major
---

# A StampedLock is not reentrant, so code holding a stamp calls no method that acquires the same lock

## Thesis
Between a `StampedLock` acquisition — `writeLock`, `readLock`, `tryWriteLock`, `tryReadLock` — and the matching unlock, the code calls no method, of the same class or of a callback, listener or overridable method, that acquires the same `StampedLock` in any mode; a mode change while holding a stamp goes through `tryConvertToWriteLock` or `tryConvertToReadLock`.

## Rationale
A `StampedLock` has no notion of ownership: a thread holding the write stamp that calls `readLock()` or `writeLock()` again on the same lock waits for a lock that it itself holds and never releases — a self-deadlock, with a thread dump showing one thread parked in the lock's acquire loop. `ReentrantLock` and `synchronized` count reentrant acquisitions per owning thread; `StampedLock` tracks modes and versions only, and its documentation restricts it to internal utilities whose locked bodies do not call unknown methods that may try to re-acquire locks. The failure needs one call path through a helper that "just takes the read lock" — a getter, a `toString`, a validator — reached from inside a write region.

## Example
```java
bad:  long s = sl.writeLock();
      try { total = recompute(); } finally { sl.unlockWrite(s); }       // recompute() calls size(), which takes readLock()
good: long s = sl.writeLock();
      try { total = recomputeUnlocked(); } finally { sl.unlockWrite(s); }   // no lock inside; size() stays for external callers
```

## Limits
Applies to the same `StampedLock` instance. Nested regions on different locks are a lock-ordering concern, not this finding. Passing a held stamp to another method that uses it for `validate` or `unlock` is permitted. A conversion — `tryConvertToWriteLock(stamp)` — is the documented way to change mode while holding a stamp.

## Validator
On the triggered hunk find each `StampedLock` region. Open the file and follow every call inside the region — same-class methods, callbacks, overridable methods — to any acquisition of the same lock field. Validator question: **can a thread that holds a stamp on this lock reach a second acquisition of the same lock before releasing the first?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-43`, severity major, `file`, `symbol`, `code` = the region and the nested acquisition quoted verbatim from the diff, `fix` = a lock-free variant of the callee used inside the region, the call moved outside the region, or a `tryConvertToWriteLock`, `rationale` naming the self-deadlock on a non-reentrant lock).

## Source
`java.util.concurrent.locks.StampedLock` class Javadoc, Java SE 21 — "StampedLocks are designed for use as internal utilities in the development of thread-safe components. Their use relies on knowledge of the internal properties of the data, objects, and methods they are protecting. They are not reentrant, so locked bodies should not call other unknown methods that may try to re-acquire locks (although you may pass a stamp to other methods that can use or convert it)"; "Unlike Semaphore or Lock implementations, StampedLocks have no notion of ownership"; `#tryConvertToWriteLock`, `#tryConvertToReadLock`.
