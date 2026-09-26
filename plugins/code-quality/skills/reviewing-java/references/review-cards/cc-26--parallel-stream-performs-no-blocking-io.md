---
title: A parallel stream pipeline performs no blocking I/O or long wait, because its workers are the common fork-join pool shared by the whole JVM
rule_id: CC-26
domain: concurrency
triggers: ['parallelStream\(', '[.]parallel\(\)', 'commonPool\(', 'ForkJoinPool', 'RecursiveTask', 'RecursiveAction']
scope: file
check_kind: semantic
severity_default: major
---

# A parallel stream pipeline performs no blocking I/O or long wait, because its workers are the common fork-join pool shared by the whole JVM

## Thesis
The functions of a parallel pipeline, and the tasks of a fork-join computation submitted to the common pool, are CPU-bound and short: no HTTP or database call, no file or socket read, no `Future.get`, `sleep` or lock wait inside them. A fan-out over I/O runs on a dedicated executor — a virtual-thread-per-task executor or a bounded pool the module owns — or in a `ForkJoinPool` constructed for it.

## Rationale
A parallel stream not submitted to a specific pool runs in the common pool, one static pool per JVM whose target parallelism is the number of available processors minus one. The pool compensates for tasks that block joining other fork-join tasks by adding workers; it makes no such adjustment for blocked I/O or other unmanaged synchronization. A worker blocked in a socket read is a worker removed from the pool for the duration: an I/O-bound parallel stream over n elements ties up as many workers as it can get, and every other parallel stream, async `CompletableFuture` stage and fork-join task in the JVM queues behind it. Fork-join tasks are documented as computational tasks that should not perform blocking I/O and should avoid `synchronized` and other blocking synchronization. On a two-processor container the common pool has a single worker, so one slow remote call inside a parallel stream serializes every parallel operation in the process.

## Example
```java
bad:  List<Quote> quotes = ids.parallelStream().map(client::fetchQuote).toList();
good: try (ExecutorService io = Executors.newVirtualThreadPerTaskExecutor()) {
          List<Future<Quote>> fs = ids.stream().map(id -> io.submit(() -> client.fetchQuote(id))).toList();
          quotes = fs.stream().map(this::await).toList();
      }
```

## Limits
Applies to a pipeline that is parallel and to a fork-join task run in the common pool. A sequential stream that calls a remote client is not this defect. A parallel stream started from inside a task of a dedicated `ForkJoinPool` runs in that pool, which the project sized for the work. A short computation — parsing, hashing, an in-memory lookup — is what the pool is for. A blocking call wrapped in `ForkJoinPool.ManagedBlocker` tells the pool to compensate and is the documented way to block inside it. A `join` on a fork-join subtask of the same pool — the `RecursiveTask` that forks its halves and joins them — is the wait the pool compensates for and is not this defect.

## Validator
On the triggered hunk find each parallel pipeline or fork-join task. Read every function it runs, following method references and called methods in the file, and list any call that blocks: a client or repository call, a `read`/`write` on a stream or channel, `Future.get`, a `join` on something other than a fork-join subtask of the same pool, `Thread.sleep`, `await`, a lock acquisition. Confirm the pipeline is not submitted to a dedicated pool. Validator question: **does work executed by the common pool block on I/O or on another thread for a duration the pool cannot compensate for?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-26`, severity major, `file`, `symbol`, `code` = the parallel call and the blocking call quoted verbatim from the diff, `fix` = the same fan-out on a dedicated executor, or the pipeline made sequential, `rationale` naming the common pool's fixed parallelism and the JVM-wide starvation).

## Source
`java.util.concurrent.ForkJoinPool` class Javadoc, Java SE 21 — "A static commonPool() is available and appropriate for most applications. The common pool is used by any ForkJoinTask that is not explicitly submitted to a specified pool"; the pool adds, suspends or resumes workers "even if some tasks are stalled waiting to join others. However, no such adjustments are guaranteed in the face of blocked I/O or other unmanaged synchronization. The nested ManagedBlocker interface enables extension of the kinds of synchronization accommodated"; the common pool's default parallelism is `availableProcessors() - 1`, floor 1 (static initialization in the source at `jdk-21-ga`). `java.util.concurrent.ForkJoinTask` class Javadoc — computations "should ideally avoid synchronized methods or blocks, and should minimize other blocking synchronization ... Subdividable tasks should also not perform blocking I/O". `java.util.stream` package Javadoc — no guarantee "in what thread any behavioral parameter is executed".
