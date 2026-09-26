---
title: A task running in a bounded pool never waits for the result of another task submitted to the same pool
rule_id: CC-35
domain: concurrency
triggers: ['[.]submit\(', '[.]join\(\)', 'invokeAll\(', 'Future<', 'CountDownLatch', '[.]execute\(']
scope: callers
check_kind: semantic
severity_default: major
---

# A task running in a bounded pool never waits for the result of another task submitted to the same pool

## Thesis
Code that executes as a task of a fixed-size executor does not call `Future.get`, `CompletableFuture.join`, `invokeAll` or `CountDownLatch.await` on work that the same executor must run; dependent work goes to a different pool, or the dependency is expressed as a `thenCompose`/`thenCombine` stage that blocks no worker.

## Rationale
A fixed pool holds at most N active threads; a task submitted while all N are busy waits in the queue until a thread is available. When each of the N running tasks blocks waiting for a task still in that queue, no thread ever becomes available: the waited-for tasks cannot start because the waiters occupy every thread, and the waiters cannot finish because the waited-for tasks never start. This is a deadlock without any lock — a thread dump shows N threads parked in `get()` and a queue that never drains — and it appears only under load, when the pool is saturated; a lightly loaded pool lets the dependent tasks find a free thread and the code works. Two levels of dependency on one pool of size N need only N outer tasks to trigger it. The common fork-join pool compensates for tasks joining other fork-join tasks; a `ThreadPoolExecutor` compensates for nothing.

## Example
```java
bad:  Future<Page> render(Doc d) {
          return pool.submit(() -> assemble(d.parts().stream()
              .map(p -> await(pool.submit(() -> renderPart(p)))).toList()));    // waits on the same pool
      }
good: Future<Page> render(Doc d) {
          return pool.submit(() -> assemble(d.parts().stream()
              .map(p -> await(partPool.submit(() -> renderPart(p)))).toList()));  // dependents on their own pool
      }
```

## Limits
Applies to a bounded executor: `newFixedThreadPool`, a `ThreadPoolExecutor` with a maximum, a `newCachedThreadPool` wrapped by a cap, a `ForkJoinPool` running non-fork-join tasks. A virtual-thread-per-task executor has no bound and cannot self-deadlock this way. A wait with a timeout that fails cleanly converts the deadlock into an error, which the project context may accept. Fork-join tasks joining fork-join subtasks in a `ForkJoinPool` are the pool's designed use.

## Validator
On the triggered hunk find each blocking wait — `get`, `join`, `invokeAll`, `await` — and the executor that runs the awaited work. Open the callers of the enclosing method to learn which executor runs the waiting code: a task submitted to the same executor, a handler on a pool that also runs the awaited task. Validator question: **can the thread that blocks here and the task it waits for both need a thread from the same bounded pool?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-35`, severity major, `file`, `symbol`, `code` = the blocking wait and the submission of the awaited work quoted verbatim from the diff, `fix` = a separate pool for the dependent work or a non-blocking composition, `rationale` naming the saturated pool in which the waiters occupy every thread).

## Source
`java.util.concurrent.Executors#newFixedThreadPool` Javadoc, Java SE 21 — "At any point, at most nThreads threads will be active processing tasks. If additional tasks are submitted when all threads are active, they will wait in the queue until a thread is available"; `java.util.concurrent.ForkJoinPool` class Javadoc — the pool maintains active threads "even if some tasks are stalled waiting to join others", a compensation a `ThreadPoolExecutor` does not offer. SEI CERT Oracle Coding Standard for Java, TPS01-J "Do not execute interdependent tasks in a bounded thread pool" — unfetched.
