---
title: Virtual threads are created one per task and never pooled, so no virtual-thread factory feeds a fixed or cached pool
rule_id: CC-29
domain: concurrency
triggers: ['ofVirtual\(', 'newFixedThreadPool\(', 'new ThreadPoolExecutor\(', 'newCachedThreadPool\(', 'newScheduledThreadPool\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Virtual threads are created one per task and never pooled, so no virtual-thread factory feeds a fixed or cached pool

## Thesis
A virtual thread runs one task and ends; work that needs many concurrent tasks uses `Executors.newVirtualThreadPerTaskExecutor()` or `Thread.ofVirtual().start(task)`. A `ThreadFactory` from `Thread.ofVirtual().factory()` is never handed to `newFixedThreadPool`, `newCachedThreadPool`, `newScheduledThreadPool` or a `ThreadPoolExecutor`, and no hand-written pool keeps virtual threads alive to reuse them.

## Rationale
A pool exists to amortize the cost of a platform thread — its creation and its stack — by keeping a bounded number alive and queueing tasks behind them. A virtual thread requires few resources, a single JVM supports millions, and the executor that creates one per task is documented as unbounded in the number of threads it creates, so there is nothing to amortize. Feeding virtual threads into a fixed pool caps concurrency at the pool size, reinstates the queue that the per-task model removes, and turns each pooled virtual thread into a long-lived worker parked in one blocking call after another: the throughput of the service returns to that of the platform pool it was meant to replace. Bounding concurrent access to a scarce downstream is the job of a `Semaphore` around the call, not of a pool of virtual threads.

## Example
```java
bad:  ExecutorService pool = Executors.newFixedThreadPool(200, Thread.ofVirtual().factory());
good: ExecutorService pool = Executors.newVirtualThreadPerTaskExecutor();
      // a downstream that must be bounded: a Semaphore around the call, not a smaller pool
```

## Limits
Applies to a virtual-thread factory given to a bounded or cached pool, and to a hand-rolled pool that reuses virtual threads. A `ThreadPoolExecutor` of platform threads is a different design and not this finding. `newThreadPerTaskExecutor(Thread.ofVirtual().factory())` is the per-task form spelled out. A `ScheduledExecutorService` of a few platform threads that hands each fired task to a virtual-thread executor is a correct pairing.

## Validator
On the triggered hunk find each pool constructor — `newFixedThreadPool`, `newCachedThreadPool`, `newScheduledThreadPool`, `new ThreadPoolExecutor` — and its `ThreadFactory` argument; find each `ofVirtual()` and where its threads or factory go. Validator question: **is a virtual-thread factory, or a set of started virtual threads, kept in a pool that reuses them across tasks?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-29`, severity minor, `file`, `symbol`, `code` = the pool constructor with the virtual factory quoted verbatim from the diff, `fix` = `newVirtualThreadPerTaskExecutor()`, with a `Semaphore` where downstream concurrency must be bounded, `rationale` naming the concurrency cap and the queue the pool reintroduces).

## Source
`java.util.concurrent.Executors#newVirtualThreadPerTaskExecutor` Javadoc, Java SE 21 — "Creates an Executor that starts a new virtual Thread for each task. The number of threads created by the Executor is unbounded"; `java.lang.Thread` class Javadoc, section "Virtual threads" — "Virtual threads will typically require few resources and a single Java virtual machine may support millions of virtual threads"; `Executors#newFixedThreadPool` — "At any point, at most nThreads threads will be active processing tasks. If additional tasks are submitted when all threads are active, they will wait in the queue until a thread is available". JEP 444 "Virtual Threads", section "Do not pool virtual threads" — unfetched.
