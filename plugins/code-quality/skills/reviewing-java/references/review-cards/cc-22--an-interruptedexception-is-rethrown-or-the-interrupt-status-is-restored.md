---
title: An InterruptedException is rethrown or the interrupt status is restored with Thread.currentThread().interrupt() before the catch block ends
rule_id: CC-22
domain: concurrency
triggers: ['catch\s*\(\s*InterruptedException', 'catch\s*\(\s*(Exception|Throwable)\s', 'InterruptedException', 'Thread[.]sleep\(', '[.]await\(', '[.]join\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# An InterruptedException is rethrown or the interrupt status is restored with Thread.currentThread().interrupt() before the catch block ends

## Thesis
A `catch` of `InterruptedException` — or of `Exception` or `Throwable` around a block that calls `sleep`, `wait`, `join`, `await`, `take`, `put` or a future's `get` — either propagates the exception (the method declares `throws InterruptedException`) or calls `Thread.currentThread().interrupt()` and leaves the unit of work promptly. It does not log and continue, and it does not wrap the exception in a `RuntimeException` without re-asserting the status first.

## Rationale
Interruption is a request to stop, delivered as a flag: when the target thread is blocked in `sleep`, `wait` or `join`, "its interrupt status will be cleared and it will receive an InterruptedException". The clearing is the point: after the catch the flag is off, and every method further up the stack, and the pool that owns the thread, can no longer see that cancellation was requested. A caller that used `Future.cancel(true)`, an executor's `shutdownNow`, or a structured scope then observes a task that keeps running to completion. Restoring the status with `Thread.currentThread().interrupt()` gives the next blocking call up the stack its own `InterruptedException`; rethrowing does the same directly.

## Example
```java
bad:  try { Thread.sleep(backoff); } catch (InterruptedException e) { log.warn("interrupted"); }
good: try { Thread.sleep(backoff); }
      catch (InterruptedException e) { Thread.currentThread().interrupt(); return; }
```

## Limits
Applies to code that runs on a thread whose interruption means cancellation: pooled workers, tasks, request threads. A `catch` that rethrows, one that wraps the exception in another carrying the cause after re-asserting the status, and one that immediately ends the `run` method of a `Thread` subclass (the thread itself is finishing, so the status has no reader) are correct; a task's `run` on a pooled thread is not that case, because the worker continues with a cleared status. Code that owns the thread and documents that interruption is its own shutdown signal, consumed at that point, is a tolerance the project context may state.

## Validator
On the triggered hunk find each `catch (InterruptedException …)` and each `catch (Exception …)` or `catch (Throwable …)` whose `try` contains an interruptible call. Check that the block rethrows, or contains `Thread.currentThread().interrupt()` followed by an exit from the unit of work. Validator question: **does this catch block swallow the interruption, neither rethrowing nor restoring the interrupt status?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-22`, severity major, `file`, `symbol`, `code` = the catch block quoted verbatim from the diff, `fix` = the rethrow, or `Thread.currentThread().interrupt()` with the early exit, `rationale` naming the cleared status and the caller whose cancellation is lost).

## Source
`java.lang.Thread#interrupt` Javadoc, Java SE 21 — a thread blocked in `wait`, `join` or `sleep` has "its interrupt status ... cleared and it will receive an InterruptedException"; `Thread#sleep` — "The interrupted status of the current thread is cleared when this exception is thrown". `java.util.concurrent.ExecutorService` class Javadoc usage example — on `InterruptedException`, "Preserve interrupt status" with `Thread.currentThread().interrupt()`. Error Prone `InterruptedExceptionSwallowed` — "It is important for correctness and performance that thread interruption is handled properly". SonarSource RSPEC-2142 "InterruptedException and ThreadDeath should not be ignored".
