---
title: Long-running CPU-bound work runs on a platform pool sized to the available processors, not on virtual threads
rule_id: CC-30
domain: concurrency
triggers: ['newVirtualThreadPerTaskExecutor\(', 'ofVirtual\(', 'startVirtualThread\(', 'newThreadPerTaskExecutor\(', 'setVirtualThreads\(']
scope: file
check_kind: semantic
severity_default: minor
---

# Long-running CPU-bound work runs on a platform pool sized to the available processors, not on virtual threads

## Thesis
A task submitted to a virtual-thread executor spends most of its time blocked — on I/O, a lock, a queue — or finishes quickly. A computation that runs for a long stretch without blocking (encoding, compression, a large sort, a model evaluation) is submitted to a fixed pool of platform threads sized to `Runtime.getRuntime().availableProcessors()` or to a `ForkJoinPool`.

## Rationale
Virtual threads are user-mode threads scheduled by the runtime onto a small set of carrier platform threads; a carrier is handed from one virtual thread to another when the current one blocks in I/O or on a lock. A virtual thread that never blocks keeps its carrier for as long as it runs, so N long CPU-bound virtual threads occupy the N carriers and every other virtual thread in the process — including request handlers whose I/O has completed — waits for a carrier. Nothing is gained: the computation needs a core per thread either way, and a platform pool sized to the processor count gives it that without starving the I/O-bound work. The class documentation states the intended use directly: tasks that spend most of the time blocked, not long running CPU intensive operations.

## Example
```java
bad:  try (ExecutorService ex = Executors.newVirtualThreadPerTaskExecutor()) {
          for (Chunk c : chunks) ex.submit(() -> compress(c));      // minutes of CPU per task
      }
good: ExecutorService cpu = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
      for (Chunk c : chunks) cpu.submit(() -> compress(c));
```

## Limits
Applies to a task that is CPU-bound for a long stretch — the file shows a loop over large data, a codec, a cryptographic or numeric routine — submitted to a virtual-thread executor. A task that mixes short computation with I/O belongs on virtual threads. A short CPU task (parsing a request, building a response) is fine anywhere. A project context that documents the carrier pool as sized for the CPU work states a tolerance.

## Validator
On the triggered hunk find each task handed to a virtual-thread executor or started as a virtual thread. Open the file and read the task body and the methods it calls: does it block (a client call, a repository call, a stream read, a queue take, a lock) or does it compute for a long stretch without blocking? Validator question: **does this virtual thread run a long CPU-bound computation with no blocking point, so that it holds a carrier for its whole duration?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-30`, severity minor, `file`, `symbol`, `code` = the submission and the computation entry quoted verbatim from the diff, `fix` = a platform pool sized to the available processors, or a `ForkJoinPool`, for that task, `rationale` naming the carrier held for the whole duration and the I/O-bound tasks starved of carriers).

## Source
`java.lang.Thread` class Javadoc, Java SE 21, section "Virtual threads" — "Virtual threads are suitable for executing tasks that spend most of the time blocked, often waiting for I/O operations to complete. Virtual threads are not intended for long running CPU intensive operations"; "Virtual threads typically employ a small set of platform threads used as carrier threads. Locking and I/O operations are examples of operations where a carrier thread may be re-scheduled from one virtual thread to another".
