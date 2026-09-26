---
title: After shutdown, the return value of awaitTermination is checked and a false result escalates to shutdownNow
rule_id: CC-20
domain: concurrency
triggers: ['awaitTermination\(', 'shutdown\(\)', 'shutdownNow\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# After shutdown, the return value of awaitTermination is checked and a false result escalates to shutdownNow

## Thesis
A `shutdown()` is followed by `awaitTermination(timeout, unit)` whose boolean result is tested: `false` means the timeout elapsed with tasks still running, and the code then calls `shutdownNow()`, waits again, and reports an executor that still did not terminate. An `awaitTermination` whose result is discarded, or a `shutdown()` with no wait, lets the caller proceed as if the tasks had finished.

## Rationale
`shutdown()` only stops the executor from accepting new tasks; previously submitted tasks continue to execute. `awaitTermination` blocks until the tasks complete, the timeout elapses, or the thread is interrupted, and returns `true` if the executor terminated and `false` if the timeout elapsed first — the only signal the caller gets that work is still running while it releases the resources those tasks use. `shutdownNow()` interrupts the running tasks and returns the tasks that never started, which is the material for the log line; a task that ignores the interrupt may never terminate, which the second wait detects. The interface's own two-phase example is the shape: shutdown, await, on `false` shutdownNow and await again, and re-interrupt the current thread if the wait itself was interrupted.

## Example
```java
bad:  pool.shutdown();
      pool.awaitTermination(30, TimeUnit.SECONDS);   // result ignored
good: pool.shutdown();
      try {
          if (!pool.awaitTermination(30, TimeUnit.SECONDS)) {
              List<Runnable> dropped = pool.shutdownNow();
              if (!pool.awaitTermination(10, TimeUnit.SECONDS)) log.error("pool did not terminate; {} dropped", dropped.size());
          }
      } catch (InterruptedException e) { pool.shutdownNow(); Thread.currentThread().interrupt(); }
```

## Limits
Applies to a shutdown the code performs itself. `ExecutorService.close()` performs both phases internally and needs no check. A `shutdown()` in a `@PreDestroy` where the container's own shutdown timeout is the bound and the project context says the tasks are safe to abandon is a tolerance; a test helper that shuts down a pool whose tasks are known to have completed may state the same.

## Validator
On the triggered hunk find each `shutdown()` and each `awaitTermination(...)`. Check that `awaitTermination` follows the `shutdown()`, that its result is tested, and that the `false` branch calls `shutdownNow()` and reports. Validator question: **does this shutdown proceed without testing whether awaitTermination returned false?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-20`, severity minor, `file`, `symbol`, `code` = the shutdown lines quoted verbatim from the diff, `fix` = the two-phase form with the tested result, `rationale` naming the tasks that may still be running when the caller proceeds).

## Source
`java.util.concurrent.ExecutorService#awaitTermination` Javadoc, Java SE 21 — "Blocks until all tasks have completed execution after a shutdown request, or the timeout occurs, or the current thread is interrupted, whichever happens first"; returns "true if this executor terminated and false if the timeout elapsed before termination". `ExecutorService` class Javadoc usage example `shutdownAndAwaitTermination` — `shutdown()`, then on `!awaitTermination` a `shutdownNow()` and a second wait, with `Thread.currentThread().interrupt()` on `InterruptedException`. `ThreadPoolExecutor#shutdownNow` — "interrupts tasks via Thread.interrupt; any task that fails to respond to interrupts may never terminate".
