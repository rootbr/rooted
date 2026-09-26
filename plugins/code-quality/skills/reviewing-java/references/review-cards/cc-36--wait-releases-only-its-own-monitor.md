---
title: A wait() or Condition.await() is called while the thread holds no lock other than the one it waits on
rule_id: CC-36
domain: concurrency
triggers: ['\bwait\(', '[.]await\(', 'synchronized', '[.]lock\(\)']
scope: file
check_kind: semantic
severity_default: major
---

# A wait() or Condition.await() is called while the thread holds no lock other than the one it waits on

## Thesis
A `wait()` on monitor B, or an `await()` on a `Condition` of lock B, is reached while the current thread holds B alone — not from inside a `synchronized` block or `Lock` region on some other object A that the notifying thread must also enter.

## Rationale
`wait` places the thread in the wait set of the object it is called on and relinquishes the synchronization claims on that object only; any other object the thread is synchronized on stays locked while it waits, and `await` likewise releases only the lock its `Condition` belongs to. If the thread holding outer lock A waits on inner monitor B, the thread that would notify B must first acquire A to reach the guarded region — and A is still held by the waiter. Neither thread progresses; the JVM's deadlock detector reports nothing because the waiter is in `WAITING`, not `BLOCKED` on a cycle, and the hang looks like a lost notification. The wait belongs on the outermost lock of the nesting, or the outer lock is released before the wait.

## Example
```java
bad:  synchronized (registry) {                                            // outer lock A
          synchronized (slot) { while (!slot.ready) slot.wait(); }        // releases slot only; registry stays held
      }
good: synchronized (slot) { while (!slot.ready) slot.wait(); }            // no other lock held
      synchronized (registry) { registry.assign(slot); }
```

## Limits
Applies when the waited-on monitor or lock differs from another lock the same thread holds at the call, including a lock taken by a caller of the method shown. A `wait` on the only monitor held, or an `await` on the `Condition` of the only lock held, is correct. A `CountDownLatch.await`, `CyclicBarrier.await` or `Semaphore.acquire` under a lock is a different blocking-under-lock concern and not this finding. A nested wait whose notifier provably never needs the outer lock is tolerable when the project context documents that ordering.

## Validator
On the triggered hunk find each `wait()` and `Condition.await()`; identify its monitor or lock. Open the file and walk outward through enclosing `synchronized` blocks, `lock()`/`unlock()` regions and the callers within the file to list every other lock held at that point; then find the code that notifies or signals and check whether it must acquire one of those locks first. Validator question: **is a different lock held across this wait, and does the code that would wake the waiter need that lock?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-36`, severity major, `file`, `symbol`, `code` = the wait and the enclosing lock acquisition quoted verbatim from the diff, `fix` = the wait moved to the outermost lock, or the outer lock released before waiting, or a `Condition` of the single governing lock, `rationale` naming the lock still held while waiting and the notifier that needs it).

## Source
`java.lang.Object#wait(long, int)` Javadoc, Java SE 21 — "This method causes the current thread ... to place itself in the wait set for this object and then to relinquish any and all synchronization claims on this object. Note that only the locks on this object are relinquished; any other objects on which the current thread may be synchronized remain locked while the thread waits"; `java.util.concurrent.locks.Condition#await` Javadoc — "The lock associated with this Condition is atomically released", that lock alone. SpotBugs `TLW_TWO_LOCK_WAIT` "Wait with two locks held" — "Performing a wait only releases the lock on the object being waited on, not any other locks" (fetched from `spotbugs/etc/messages.xml`, `master`; CWE-833).
