---
title: A wait for a condition blocks on a latch, condition, future or park, never on a Thread.sleep polling loop
rule_id: PF-20
domain: performance
triggers: ['Thread[.]sleep\(', 'TimeUnit[.]\w+[.]sleep\(', 'while\s*\(\s*!\w+', 'parkNanos\(', 'onSpinWait\(\)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A wait for a condition blocks on a latch, condition, future or park, never on a Thread.sleep polling loop

## Thesis
Code that must proceed once another thread has done something — set a flag, produced a value, finished a task — waits on a synchronizer that the producer signals: `CountDownLatch.await`, `Condition.await`, `Future.get`, `CompletableFuture.join`, `BlockingQueue.take`, `LockSupport.park`. It does not loop on `Thread.sleep(1)` (or any small sleep) re-checking the condition.

## Rationale
`Thread.sleep` suspends the thread for the given milliseconds subject to the precision and accuracy of system timers and schedulers: the thread wakes no earlier, and how much later depends on the timer resolution, so a 1 ms poll both over-sleeps and wakes repeatedly to find nothing. Each wake-up is a context switch that consumes CPU and, in a pool, a worker. A synchronizer wakes the waiter when the event happens, so the latency is the signal itself; `parkNanos` accepts a nanosecond bound and returns on `unpark`, on interruption, when the time elapses or spuriously — callers re-check their condition — and `Thread.onSpinWait` is the form for a very short busy-wait on a `volatile` flag.

## Example
```java
bad:  while (!ready) Thread.sleep(1);
      use(result);
good: latch.await();               // the producer calls latch.countDown() after setting result
      use(result);
```

## Limits
A deliberate delay — a retry back-off, a rate limiter, a test's timing — is a correct use of `sleep`. A short spin on a `volatile` flag with `Thread.onSpinWait()` is correct where the wait is known to be microseconds. Code that must poll an external system with no notification (a file, a remote status) polls at a documented interval measured in seconds, not milliseconds. Whether the flag read is visible across threads is a memory-model concern outside this rule.

## Validator
On the triggered hunk find each `Thread.sleep` or `TimeUnit.sleep` inside a `while`, `do` or `for` whose condition re-reads state another thread sets. Validator question: **does this loop sleep and re-check a condition that a synchronizer could signal?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-20`, severity minor, `file`, `symbol`, `code` = the loop quoted verbatim from the diff, `fix` = the blocking wait on a latch, condition, future or queue, `rationale` naming the timer-bound over-sleep and the wake-ups that find nothing).

## Source
`java.lang.Thread#sleep(long)` Javadoc, Java SE 21 — "Causes the currently executing thread to sleep (temporarily cease execution) for the specified number of milliseconds, subject to the precision and accuracy of system timers and schedulers." `java.util.concurrent.locks.LockSupport#parkNanos(long)` — returns on `unpark`, on interrupt, when "The specified waiting time elapses", or spuriously; "Callers should re-check the conditions which caused the thread to park in the first place." `java.util.concurrent.CountDownLatch` class Javadoc — "The await methods block until the current count reaches zero due to invocations of the countDown method". `java.lang.Thread#onSpinWait` — the documented form for a loop that spins "until some flag is set outside of that method".
