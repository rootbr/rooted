---
title: An executor that accepts production load bounds both its threads and its queue
rule_id: CC-21
domain: concurrency
triggers: ['newCachedThreadPool', 'newFixedThreadPool', 'new ThreadPoolExecutor\(', 'new LinkedBlockingQueue<[^>]*>\(\)', 'newSingleThreadExecutor', 'newScheduledThreadPool']
scope: hunk
check_kind: mechanical
severity_default: major
---

# An executor that accepts production load bounds both its threads and its queue

## Thesis
A thread pool that receives tasks at a rate the producer does not control — request handlers, listeners, a message consumer — is a `ThreadPoolExecutor` (or a Spring `ThreadPoolTaskExecutor`) with a finite `maximumPoolSize` and a bounded work queue (an `ArrayBlockingQueue`, or a `LinkedBlockingQueue` constructed with a capacity). `Executors.newCachedThreadPool()` bounds neither threads nor queue; `newFixedThreadPool`, `newSingleThreadExecutor` and `newScheduledThreadPool` bound the threads and queue without limit.

## Rationale
A cached pool "creates new threads as needed": with direct handoff and an unbounded maximum the pool "admits the possibility of unbounded thread growth when commands continue to arrive on average faster than they can be processed", and each platform thread holds a stack and an OS thread until memory or the OS limit ends the process. A fixed pool operates "off a shared unbounded queue" — a `LinkedBlockingQueue` whose default capacity is `Integer.MAX_VALUE` — which "admits the possibility of unbounded work queue growth" under the same condition, and the queued tasks hold their arguments until the heap runs out. A bounded queue with a finite maximum "helps prevent resource exhaustion"; when both bounds are hit the executor rejects, and its `RejectedExecutionHandler` decides the outcome: the default `AbortPolicy` throws a `RejectedExecutionException` to the submitter, `CallerRunsPolicy` runs the task on the submitting thread and so slows submission, `DiscardPolicy` drops the task silently.

## Example
```java
bad:  ExecutorService pool = Executors.newCachedThreadPool();
      ExecutorService pool = Executors.newFixedThreadPool(8);
good: ExecutorService pool = new ThreadPoolExecutor(8, 32, 60, TimeUnit.SECONDS,
          new ArrayBlockingQueue<>(1_000), new ThreadPoolExecutor.CallerRunsPolicy());
```

## Limits
Applies to a pool fed by a producer it does not throttle. A pool whose producer is itself bounded — a fixed set of scheduled jobs, a batch loop that waits for each result before submitting the next, a test — may use a factory method, and the project context may state that tolerance. `Executors.newVirtualThreadPerTaskExecutor()` creates an unbounded number of virtual threads by design and bounds the work through a `Semaphore` around the downstream resource, not through the executor. A Spring `ThreadPoolTaskExecutor` bean is configured through its `queueCapacity` and `maxPoolSize` properties; finite values there are the same check.

## Validator
On the triggered hunk find each executor construction. For a factory method, flag unless the surrounding code shows a bounded producer. For a `ThreadPoolExecutor` constructor, read the maximum and the queue argument (flag a `LinkedBlockingQueue` without capacity, or a `SynchronousQueue` with an `Integer.MAX_VALUE` maximum). Validator question: **can this pool grow its threads or its queue without bound when tasks arrive faster than they complete?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-21`, severity major, `file`, `symbol`, `code` = the construction quoted verbatim from the diff, `fix` = the `ThreadPoolExecutor` with a finite maximum and a bounded queue, `rationale` naming which resource grows without bound).

## Source
`java.util.concurrent.Executors` Javadoc, Java SE 21 — `#newCachedThreadPool` "Creates a thread pool that creates new threads as needed"; `#newFixedThreadPool` "Creates a thread pool that reuses a fixed number of threads operating off a shared unbounded queue". `ThreadPoolExecutor` class Javadoc, "Queuing" — direct handoffs admit "the possibility of unbounded thread growth when commands continue to arrive on average faster than they can be processed"; unbounded queues admit "the possibility of unbounded work queue growth" under the same condition; "A bounded queue ... helps prevent resource exhaustion when used with finite maximumPoolSizes"; "Rejected tasks" — the four predefined handlers, "In the default ThreadPoolExecutor.AbortPolicy, the handler throws a runtime RejectedExecutionException upon rejection". `LinkedBlockingQueue` class Javadoc — "The capacity, if unspecified, is equal to Integer.MAX_VALUE".
