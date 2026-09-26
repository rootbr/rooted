---
title: A task that a caller may cancel honors the interrupt, polling the interrupt status in CPU-bound loops and exiting promptly
rule_id: CC-23
domain: concurrency
triggers: ['cancel\(true\)', 'while\s*\(\s*true\s*\)', 'for\s*\(\s*;\s*;\s*\)', 'isInterrupted\(\)', 'Thread[.]interrupted\(\)', 'shutdownNow\(']
scope: file
check_kind: semantic
severity_default: major
---

# A task that a caller may cancel honors the interrupt, polling the interrupt status in CPU-bound loops and exiting promptly

## Thesis
A task submitted to an executor, a `Runnable` given to a `Thread`, or the body of a service loop that a caller can stop through `Future.cancel(true)`, `shutdownNow()` or `Thread.interrupt()` responds to the interrupt: a loop that makes no interruptible blocking call checks `Thread.currentThread().isInterrupted()` on each iteration and returns, and a loop that blocks does so in interruptible calls whose `InterruptedException` ends the task.

## Rationale
`Future.cancel(true)` only interrupts "the thread executing this task ... in an attempt to stop the task"; with `false`, "in-progress tasks are allowed to complete". The interrupt itself, when the thread is not blocked in an interruptible method, does nothing but set the thread's interrupt status. A loop that never reads the status runs to its own end, still mutating shared state and holding its resources while the caller has moved on, and an executor's `shutdownNow`, which interrupts its workers, cannot make the pool terminate: "any task that fails to respond to interrupts may never terminate". `Thread.interrupted()` reads and clears the status, so a check that uses it acts on `true` at once; `isInterrupted()` reads without clearing.

## Example
```java
bad:  Future<?> f = pool.submit(() -> { for (Item i : items) index(i); });
      f.cancel(true);                                    // the loop runs to the end
good: Future<?> f = pool.submit(() -> { for (Item i : items) {
          if (Thread.currentThread().isInterrupted()) return;
          index(i); } });
```

## Limits
Applies to a task whose caller cancels it or whose executor is shut down with `shutdownNow`. A short task that completes in bounded time, a loop whose every iteration makes an interruptible blocking call (`take`, `sleep`, `await`) and lets the exception end it, and a task cancelled through its own documented flag that every blocking call in it also observes are correct. A task that must finish its current unit before stopping checks the status between units, which is the form; a task the project context documents as non-cancellable is a tolerance.

## Validator
On the triggered hunk find each `cancel(true)` and `shutdownNow()`, and each long-running loop inside a task body. Open the file: for each cancellable task, trace its loop and confirm either an `isInterrupted()` or `interrupted()` check that exits, or an interruptible blocking call per iteration whose `InterruptedException` ends the task. Validator question: **can this task keep running after the interrupt because no iteration reads the status or blocks interruptibly?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-23`, severity major, `file`, `symbol`, `code` = the cancellation call or the loop header quoted verbatim from the diff, `fix` = the `isInterrupted()` check with an exit from the loop, `rationale` naming the interrupt status nothing reads).

## Source
`java.util.concurrent.Future#cancel` Javadoc, Java SE 21 — `mayInterruptIfRunning` "true if the thread executing this task should be interrupted (if the thread is known to the implementation); otherwise, in-progress tasks are allowed to complete". `java.lang.Thread#interrupt` — when the thread is not blocked in an interruptible method, "this thread's interrupt status will be set"; `Thread#interrupted` — "The interrupted status of the thread is cleared by this method". `ThreadPoolExecutor#shutdownNow` — "any task that fails to respond to interrupts may never terminate". `java.lang.InterruptedException` class Javadoc — the idiom `if (Thread.interrupted()) throw new InterruptedException();`.
