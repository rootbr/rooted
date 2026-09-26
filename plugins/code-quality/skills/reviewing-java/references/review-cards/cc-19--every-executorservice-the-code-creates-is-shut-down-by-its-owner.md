---
title: Every ExecutorService the code creates is shut down by its owner, and reassigning the field shuts down the previous one
rule_id: CC-19
domain: concurrency
triggers: ['Executors[.]new', 'new ThreadPoolExecutor\(', 'new ScheduledThreadPoolExecutor\(', 'new ForkJoinPool\(', 'ExecutorService\s+\w+', 'ScheduledExecutorService\s+\w+']
scope: file
check_kind: mechanical
severity_default: major
---

# Every ExecutorService the code creates is shut down by its owner, and reassigning the field shuts down the previous one

## Thesis
An `ExecutorService` the code constructs has one owner that calls `shutdown()` (followed by `awaitTermination`) or `close()` when the owner ends — a `@PreDestroy` or `DisposableBean.destroy` method on the bean that holds it, the `close()` of the `AutoCloseable` that holds it, or the end of a try-with-resources block for an executor scoped to one method — and a field that is reassigned to a new executor shuts down the executor it replaces.

## Rationale
The threads of a pool exist until the pool is explicitly shut down: the default thread factory creates non-daemon threads, so a live pool keeps the JVM alive after `main` returns, and a pool created by a bean the container discards, or by a field reassigned on reinitialization, keeps its threads, its queue and every queued task reachable for the life of the process. The interface's contract is that "an unused ExecutorService should be shut down to allow reclamation of its resources"; a pool is reclaimed without an explicit shutdown only when it is unreferenced and has no remaining threads, which a pool with core threads and no core-thread timeout never satisfies. `ExecutorService` is `AutoCloseable`: `close()` performs `shutdown()` and waits for termination, so a try-with-resources block is the form for an executor that lives inside one method.

## Example
```java
bad:  @Service class Indexer { private ExecutorService pool = Executors.newFixedThreadPool(4);
          void rebuild() { pool = Executors.newFixedThreadPool(4); } }   // old pool leaks, none shut down
good: @Service class Indexer { private final ExecutorService pool = Executors.newFixedThreadPool(4);
          @PreDestroy void stop() { pool.shutdown(); } }
      try (ExecutorService e = Executors.newVirtualThreadPerTaskExecutor()) { e.submit(task); }
```

## Limits
Applies to an executor the code constructs. A Spring `ThreadPoolTaskExecutor`, `ThreadPoolTaskScheduler` or `SimpleAsyncTaskExecutor` bean is shut down by Spring's lifecycle management and is not flagged; the same holds for a container-managed `ManagedExecutorService` and for `ForkJoinPool.commonPool()`. An executor injected from elsewhere belongs to its creator. A pool built with zero core threads and `allowCoreThreadTimeOut(true)` that the project context documents as self-reclaiming is a tolerance.

## Validator
On the triggered hunk find each construction of an executor and each assignment of an executor to a field. Open the file: locate the `shutdown()`, `shutdownNow()` or `close()` for that executor in a `@PreDestroy`, `destroy()` or `close()` method of the owner, or the try-with-resources that holds it; for a field reassignment, check that the previous value is shut down before or at the reassignment. Validator question: **is there an executor this code creates that no owner method, resource block or reassignment path shuts down?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-19`, severity major, `file`, `symbol`, `code` = the construction or reassignment quoted verbatim from the diff, `fix` = the owner's shutdown in `@PreDestroy` or `close()`, the try-with-resources, or the shutdown of the replaced executor, `rationale` naming the threads and queued tasks kept alive).

## Source
`java.util.concurrent.ExecutorService` Javadoc, Java SE 21 — "An unused ExecutorService should be shut down to allow reclamation of its resources"; usage example `try (ExecutorService e = Executors.newWorkStealingPool()) { … }`; `#close()` (since 19) — "Initiates an orderly shutdown ... This method waits until all tasks have completed execution and the executor has terminated". `Executors#newFixedThreadPool` — "The threads in the pool will exist until it is explicitly shutdown". `ThreadPoolExecutor` class Javadoc — "Creating new threads": the default factory creates threads with "non-daemon status"; "Reclamation": a pool "that is no longer referenced in a program AND has no remaining threads may be reclaimed (garbage collected) without being explicitly shutdown". Spring Framework reference, "Task Execution and Scheduling" — `ThreadPoolTaskExecutor` and `ThreadPoolTaskScheduler` provide "graceful shutdown through Spring's lifecycle management".
