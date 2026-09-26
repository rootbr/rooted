---
title: The Future returned by submitting a task to an executor is observed — joined, checked or completed with a handler — so an exception in the task is not silently kept inside it
rule_id: REL-58
domain: reliability
triggers: ['[.]submit\(', 'invokeAll\(', 'schedule\(', 'scheduleAtFixedRate\(', 'scheduleWithFixedDelay\(', 'runAsync\(', 'supplyAsync\(', 'UncaughtExceptionHandler']
scope: file
check_kind: semantic
severity_default: major
---

# The Future returned by submitting a task to an executor is observed — joined, checked or completed with a handler — so an exception in the task is not silently kept inside it

## Thesis
Code that calls `submit`, `invokeAll`, `schedule*`, `runAsync` or `supplyAsync` keeps the returned `Future`/`CompletableFuture` and, on some path, calls `get`/`join`, checks `isDone` and the result, or attaches a completion handler that records failure; a task whose outcome nobody will read is passed to `execute` (so its exception reaches the thread's `UncaughtExceptionHandler`) or wrapped in a try/catch that reports inside the task.

## Rationale
A task submitted through `submit` is wrapped in a `FutureTask`, and such task objects "catch and maintain computational exceptions, and so they do not cause abrupt termination": the exception is stored in the future and surfaces only through `get`, as an `ExecutionException`. When the future is discarded, nothing is thrown anywhere, no handler runs, no log line appears — the task simply did not do its work, and a scheduled task that throws once stops being rescheduled without notice. Methods that return a future "generally indicate errors by returning a future that eventually fails. If you don't check the return value of these methods, you will never find out if they threw an exception". `execute` does not wrap the task, so an exception there reaches the uncaught-exception handler.

## Example
```java
bad:  executor.submit(() -> index.rebuild());                 // returned Future dropped; a throw is invisible
      scheduler.scheduleAtFixedRate(this::poll, 0, 5, SECONDS); // one throw cancels every later run silently
good: Future<?> f = executor.submit(() -> index.rebuild()); pending.add(f);   // joined and checked later
      scheduler.scheduleAtFixedRate(() -> { try { poll(); } catch (RuntimeException e) { log.error("poll failed", e); } }, 0, 5, SECONDS);
```

## Limits
A task that catches and reports every exception inside its own body has no unobserved failure. `execute` with an `UncaughtExceptionHandler` set on the pool's thread factory is a correct form. A future stored in a field or collection and joined elsewhere in the file is observed; open the file before flagging. A test that intentionally ignores a future may name the variable `unused`.

## Validator
On the triggered hunk find each `submit`, `invokeAll`, `schedule*`, `runAsync`, `supplyAsync` and follow the returned future: is it stored, joined, checked, or given a handler, in this file? Read the task body for its own catch-and-report. Validator question: **can this task throw with no code path that ever observes or reports the exception?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-58`, severity major, `file`, `symbol`, `code` = the submission quoted verbatim from the diff, `fix` = the future joined and checked, a completion handler, `execute` with an uncaught-exception handler, or a catch-and-report inside the task, `rationale` naming the exception the future keeps unseen).

## Source
`java.util.concurrent.ThreadPoolExecutor#afterExecute` Javadoc, Java SE 21 — "When actions are enclosed in tasks (such as FutureTask) either explicitly or via methods such as submit, these task objects catch and maintain computational exceptions, and so they do not cause abrupt termination, and the internal exceptions are not passed to this method". `java.util.concurrent.Future#get()` — `@throws ExecutionException if the computation threw an exception`. Error Prone `FutureReturnValueIgnored` — "Methods that return java.util.concurrent.Future and its subclasses generally indicate errors by returning a future that eventually fails. If you don't check the return value of these methods, you will never find out if they threw an exception". `java.lang.Thread.UncaughtExceptionHandler` — "Method invoked when the given thread terminates due to the given uncaught exception". `java.util.concurrent.ScheduledExecutorService#scheduleAtFixedRate` — when "an execution of the task throws an exception", "calling get on the returned future will throw ExecutionException, holding the exception as its cause" and "Subsequent executions are suppressed".
