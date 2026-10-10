---
title: A Lock is acquired before the try block and released in its finally on every path
rule_id: JAVA-07
domain: concurrency
step: [implement, handle-errors]
applies_to: [java, exceptions]
triggers: ['[.]lock\(\)', 'lockInterruptibly\(', 'tryLock\(', '[.]unlock\(\)', 'writeLock\(\)', 'readLock\(\)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A Lock is acquired before the try block and released in its finally on every path

## Thesis
A `lock()`, `lockInterruptibly()` or successful `tryLock()` call stands immediately before a `try` block whose `finally` calls `unlock()` on the same lock; the acquisition is not inside the `try`, and no return, break or exception path leaves the region without passing through the `finally`.

## Rationale
An explicit lock is released only by `unlock()`; unlike a `synchronized` block, leaving the method by return or exception does not release it, and a lock left held blocks every later acquirer for good. `unlock()` in a `finally` runs on every exit — but only correctly if the lock was acquired: when `lock()` sits inside the `try` and the acquisition fails (an interrupted `lockInterruptibly`, a `tryLock` that returned false, an exception in an expression evaluated before it), the `finally` calls `unlock()` on a lock the thread does not hold, and `ReentrantLock.unlock` then throws `IllegalMonitorStateException`, replacing the original failure. Placing the acquisition before the `try` makes the `finally` cover exactly the held region.

## Example
```java
bad:  try { lock.lock(); apply(delta); } finally { lock.unlock(); }
      lock.lock(); apply(delta); lock.unlock();
good: lock.lock();
      try { apply(delta); } finally { lock.unlock(); }
```

## Limits
Applies to `java.util.concurrent.locks` locks and to `StampedLock` stamps. A `tryLock()` whose result is tested — `if (lock.tryLock()) { try { … } finally { lock.unlock(); } }` — is the correct form; the `finally` sits inside the branch that holds the lock. A lock acquired in one method and released in another (a hand-over-hand traversal, a lock held across a callback) is out of scope when the class documents the release path. `synchronized` blocks need no `finally`.

## Validator
On the triggered hunk find each `lock()`, `lockInterruptibly()` and `tryLock()` call and each `unlock()`. Check that the acquisition is the statement immediately before a `try`, that the `unlock()` on the same lock is in that `try`'s `finally`, and that no `unlock()` runs on a path where the acquisition may have failed or was not attempted. Validator question: **is there an exit path on which this lock stays held, or a path on which `unlock()` runs without the lock being held?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-07`, severity major, `file`, `symbol`, `code` = the acquisition and release lines quoted verbatim from the diff, `fix` = `lock()` before the `try` and `unlock()` in its `finally`, `rationale` naming the unreleased lock or the `IllegalMonitorStateException` on the failed-acquisition path).
