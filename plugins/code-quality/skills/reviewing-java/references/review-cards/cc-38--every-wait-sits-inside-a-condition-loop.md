---
title: Every wait() and Condition.await() sits inside a loop that re-tests the condition it waits for
rule_id: CC-38
domain: concurrency
triggers: ['\bwait\(', '[.]await\(', '[.]awaitNanos\(', '[.]awaitUninterruptibly\(', '[.]awaitUntil\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Every wait() and Condition.await() sits inside a loop that re-tests the condition it waits for

## Thesis
A call to `Object.wait` or to any `Condition.await*` variant is the body of a `while (!condition)` loop, or of an equivalent loop whose exit re-checks the predicate — never guarded by a single `if`, and never unconditional.

## Rationale
A waiting thread can wake without a notification: a spurious wakeup is permitted by both APIs as a concession to platform semantics. It also wakes when a `notifyAll` was meant for a different condition sharing the same monitor, and when the predicate became true and false again before it ran. In each case an `if (!ready) wait();` falls through with the condition false and the code proceeds on a state it was meant to wait out — a consumer takes from an empty buffer, a worker reads a result that is not there. A `while` loop re-tests the predicate after every wake-up and waits again, which makes the cause of the wake-up irrelevant. The timed variants need the loop as well, with the remaining time recomputed on each pass.

## Example
```java
bad:  synchronized (buf) { if (buf.isEmpty()) buf.wait(); return buf.remove(); }
good: synchronized (buf) { while (buf.isEmpty()) buf.wait(); return buf.remove(); }
```

## Limits
Applies to `Object.wait` and the `Condition.await` variants. `CountDownLatch.await`, `CyclicBarrier.await`, `Phaser.awaitAdvance` and `Semaphore.acquire` wait on a state the utility maintains and need no loop; a timed latch `await` needs its boolean result checked, which is a different matter. A `do { ... } while (!cond)` or a `for (;;) { if (cond) break; wait(); }` is a loop.

## Validator
On the triggered hunk take each `wait`/`await` call and look at the statement that encloses it: a `while` or `for` whose test re-reads the awaited condition passes; an `if`, or no guard, fails. Validator question: **can this wait return with the awaited condition still false and the code continue past it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-38`, severity major, `file`, `symbol`, `code` = the wait and its guard quoted verbatim from the diff, `fix` = the `while (!condition) wait();` form, `rationale` naming spurious wakeups and notifications meant for other conditions).

## Source
`java.lang.Object#wait(long, int)` Javadoc, Java SE 21 — "A thread can wake up without being notified, interrupted, or timing out, a so-called spurious wakeup ... applications must guard against it by testing for the condition that should have caused the thread to be awakened, and continuing to wait if the condition is not satisfied"; API note — "The recommended approach to waiting is to check the condition being awaited in a while loop around the call to wait". `java.util.concurrent.locks.Condition` Javadoc — "a Condition should always be waited upon in a loop, testing the state predicate that is being waited for". SpotBugs `WA_NOT_IN_LOOP` "Wait not in loop" (fetched from `spotbugs/etc/messages.xml`, `master`). SEI CERT THI03-J "Always invoke wait() and await() methods inside a loop" — unfetched.
