---
title: A lambda in a parallel stream pipeline touches no shared mutable state
rule_id: CC-24
domain: concurrency
triggers: ['parallelStream\(', '[.]parallel\(\)', '[.]forEach\(', '[.]peek\(', '[.]map\(']
scope: file
check_kind: semantic
severity_default: major
---

# A lambda in a parallel stream pipeline touches no shared mutable state

## Thesis
A behavioral parameter passed to `map`, `filter`, `forEach`, `peek` or any other operation of a pipeline that runs in parallel reads no state another thread may change and writes nothing outside the element it receives; an accumulation is expressed as `collect`, `reduce` or `toList`.

## Rationale
The functions handed to a stream execute on whichever thread the pipeline chooses; for a parallel pipeline these are workers of the common fork-join pool, and no guarantee exists as to which thread processes a given element nor as to the visibility of a function's side effects to other threads. A function that adds to an `ArrayList`, increments a counter or writes a field therefore runs concurrently from several threads without synchronization — a data race that yields incorrect results — and a function whose result depends on state that changes during the pipeline makes the result vary from run to run with thread scheduling. Synchronizing that state removes the race but serializes the workers, which undoes the parallelism. A monitor is owned by the thread that entered it: an enclosing `synchronized` block belongs to the caller of the terminal operation, and the workers executing the lambdas hold nothing, so it protects none of the accesses inside them. A reduction — `toList()`, `collect(...)`, `reduce`, `sum` — accumulates per-thread partial results and merges them, which needs no shared state.

## Example
```java
bad:  List<String> hits = new ArrayList<>();
      synchronized (lock) { items.parallelStream().filter(this::matches).forEach(hits::add); }
good: List<String> hits = items.parallelStream().filter(this::matches).toList();
```

## Limits
Applies to a pipeline that is parallel: `parallelStream()`, `.parallel()`, or a stream received from a caller under a parallel contract. A sequential pipeline runs its functions on the calling thread, where an accumulating lambda is a style matter, not a race. A lambda that writes to a concurrent collection or a `LongAdder` is free of the race but keeps the contention; it is flagged only when a reduction expresses the same result. A `forEach` whose side effect is a thread-safe sink such as a logger, or a `ConcurrentHashMap` `merge` that the project accepts, is correct. A collector with the `CONCURRENT` characteristic accumulates into one shared container by design. A `synchronized` block or lock held by the thread that invokes the terminal operation covers none of the pipeline's work, which runs on pool threads that do not own the monitor: an enclosing lock is not synchronization inside the function and does not reject the finding.

## Validator
On the triggered hunk locate each pipeline and decide whether it is parallel: the hunk, or the file, shows `parallelStream()`, `.parallel()`, or a stream passed in with a parallel contract. For each lambda or method reference in it, list what it reads and writes beyond its own argument: a captured local collection, a field, a counter, a map. Open the file to confirm that no reduction replaces the accumulation and that any `synchronized` block or lock around the pipeline is the caller's, not the workers'. Validator question: **does a function in a parallel pipeline read or write state that another worker can read or write during the same pipeline, without synchronization inside the function itself?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-24`, severity major, `file`, `symbol`, `code` = the parallel call and the offending lambda quoted verbatim from the diff, `fix` = the reduction (`toList`, `collect`, `reduce`) that replaces the accumulation, or the lambda made stateless, `rationale` naming the data race on the shared state and, where a lock encloses the pipeline, that the worker threads do not hold it).

## Source
`java.util.stream` package Javadoc, Java SE 21, sections "Non-interference", "Stateless behaviors" and "Side-effects" — behavioral parameters "must be non-interfering, and in most cases must be stateless"; "if you do not synchronize access to that state, you have a data race and therefore your code is broken, but if you do synchronize access to that state, you risk having contention undermine the parallelism you are seeking to benefit from"; no guarantees as to "the visibility of those side-effects to other threads" or "in what thread any behavioral parameter is executed for a given element"; the `forEach(results::add)` example replaced by `toList()`. `java.lang.Object#notify` Javadoc — a monitor is owned by one thread at a time; JLS §17.1 — unfetched.
