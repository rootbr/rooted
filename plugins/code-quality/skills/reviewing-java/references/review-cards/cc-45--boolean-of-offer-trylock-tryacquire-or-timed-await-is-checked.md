---
title: The boolean returned by offer, tryLock, tryAcquire or a timed await decides the next step and is never discarded
rule_id: CC-45
domain: concurrency
triggers: ['[.]offer\(', '[.]offer(First|Last)\(', '[.]tryLock\(', '[.]tryAcquire\(', '[.]await\([^)]*,', '[.]awaitUntil\(', '[.]tryTransfer\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# The boolean returned by offer, tryLock, tryAcquire or a timed await decides the next step and is never discarded

## Thesis
A call whose contract is to return `false` instead of blocking or throwing — `BlockingQueue.offer` with or without a timeout, `Lock.tryLock`, `Semaphore.tryAcquire`, `CountDownLatch.await(timeout, unit)`, `Condition.await(time, unit)`, `Condition.awaitUntil(deadline)`, `TransferQueue.tryTransfer` — is the condition of an `if`, a loop or an assertion, and the `false` branch does something: rejects, retries, drops with a metric, fails the test.

## Rationale
These methods encode their failure in the return value: `offer` returns `false` when a bounded queue has no space, `tryLock` when the lock is held, `tryAcquire` when no permit is available, a timed `await` when the waiting time elapsed before the count reached zero or the condition was signalled. Discarding the value turns each failure into silence — a task offered to a full queue is dropped while the producer continues as if it were enqueued, a critical section runs without the lock it failed to take and the `unlock()` in `finally` throws `IllegalMonitorStateException`, a resource is used without a permit, and a test that waits on a latch with a timeout passes when the latch never counted down. A bounded queue gives back-pressure only through this value: a producer that ignores it has no back-pressure and loses work.

## Example
```java
bad:  queue.offer(job);                                   // full queue: job silently dropped
      done.await(5, TimeUnit.SECONDS); assertEquals(3, results.size());
good: if (!queue.offer(job)) reject(job);
      assertTrue(done.await(5, TimeUnit.SECONDS), "workers did not finish");
```

## Limits
Applies to the methods whose `false` means "not done". `add` and `put` throw or block and return nothing useful. An `offer` on a `PriorityBlockingQueue`, a `LinkedBlockingQueue` without capacity, a `DelayQueue` or a `ConcurrentLinkedQueue` is documented never to return `false`, so ignoring it there is harmless, and the queue is unbounded, which is its own concern. An `offer` whose result is discarded deliberately as load shedding is correct only when a comment or a metric on the drop shows the intent.

## Validator
On the triggered hunk find each such call and look at its statement: is the result assigned, tested, returned or asserted? A bare expression statement discards it. Validator question: **is the boolean of an offer, try-acquire or timed wait discarded, so that the failure case continues as if it had succeeded?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-45`, severity major, `file`, `symbol`, `code` = the call as a bare statement quoted verbatim from the diff, `fix` = the `if (!...)` with the rejection, retry or assertion, `rationale` naming what the `false` means for that call and what continues wrongly).

## Source
`java.util.concurrent.BlockingQueue#offer(E)` Javadoc, Java SE 21 — "returning true upon success and false if no space is currently available"; `#offer(E, long, TimeUnit)` — "false if the specified waiting time elapses before space is available"; `java.util.concurrent.CountDownLatch#await(long, TimeUnit)` — "true if the count reached zero and false if the waiting time elapsed before the count reached zero"; `java.util.concurrent.locks.Lock#tryLock` — "true if the lock was acquired and false otherwise", with the usage idiom that "doesn't try to unlock if the lock was not acquired"; `java.util.concurrent.Semaphore#tryAcquire(long, TimeUnit)` — "false if the waiting time elapsed before a permit was acquired"; `java.util.concurrent.locks.Condition#await(long, TimeUnit)` — "false if the waiting time detectably elapsed before return from the method, else true"; `Condition#awaitUntil(Date)` — "false if the deadline has elapsed upon return, else true".
