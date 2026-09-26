---
title: A field that one thread writes and another reads is volatile, atomic, final, or accessed under one lock
rule_id: CC-01
domain: concurrency
triggers: ['new Thread\(', 'Runnable', 'submit\(', '@Async', '@Scheduled', 'CompletableFuture', 'volatile']
scope: file
check_kind: semantic
severity_default: major
---

# A field that one thread writes and another reads is volatile, atomic, final, or accessed under one lock

## Thesis
Every field that one thread writes and a different thread reads carries a happens-before edge from the write to the read: the field is `volatile`, an atomic type, `final` and assigned in the constructor, or every access to it sits inside a `synchronized` block or `Lock` region on the same lock. A plain field shared this way is a data race whatever the type of the value — an immutable object stored in a plain field is still published through a race.

## Rationale
The results of a write by one thread are guaranteed visible to a read by another thread only if the write happens-before the read. The constructs that form such an edge are `synchronized` (an unlock before a later lock of the same monitor), `volatile` (a write before a later read of the same field), `Thread.start` and `Thread.join`, and the `java.util.concurrent` classes, which extend the edges to task submission and completion. Without an edge the reader may see a stale value indefinitely, or see a later write before an earlier one: a stress test that writes `x = 1; y = 1` to plain fields while another thread reads `y` then `x` observes `y == 1, x == 0` in 0.09% of samples; with `y` declared `volatile` that outcome is forbidden and never observed. A `volatile` write publishes every write that precedes it in program order, so one `volatile` flag or reference carries a batch of plain writes, provided the reader reads the `volatile` first and the plain fields after.

## Example
```java
bad:  private boolean ready; private int value;
      void writer() { value = 42; ready = true; }
      void reader() { if (ready) use(value); }   // may use 0
good: private volatile boolean ready; private int value;
      void writer() { value = 42; ready = true; }
      void reader() { if (ready) use(value); }   // 42 guaranteed
```

## Limits
Applies to a field reachable from more than one thread: an instance field of an object handed to a task, callback, request handler or another thread, or a static field. A local, a field of a thread-confined object, and a field written only before the object is handed to another thread through `Thread.start`, an executor `submit`, a `volatile` store or a lock are not flagged. A tolerance stated in the project context — "benign race: one racy read of an idempotently constructed value with final fields, a stale value accepted" — rejects the finding when it names the outcome tolerated; "benign" without the outcome is not a tolerance.

## Validator
On the triggered hunk find each field the added lines write or read from a thread other than the one that created the object: inside a `Runnable`, `Callable` or lambda passed to `submit`, `execute` or a `CompletableFuture` stage, inside an `@Async` or `@Scheduled` method, or in a request handler on a singleton. Open the file: for each such field trace one happens-before chain from every write to every read — a `volatile` modifier, an atomic type, a `synchronized` or `Lock` region on one lock enclosing both, a `final` assigned in the constructor, or a `Thread.start`, `submit` or `join` that separates them. Validator question: **is there a write of this field and a read on another thread with no happens-before edge between them?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-01`, severity major, `file`, `symbol`, `code` = the field declaration and the racing write or read quoted verbatim from the diff, `fix` = the `volatile` modifier, the atomic type, or the lock region enclosing every access, `rationale` naming the missing happens-before edge and the stale or reordered read it permits).

## Source
`java.util.concurrent` package Javadoc, Java SE 21, "Memory Consistency Properties" — "The results of a write by one thread are guaranteed to be visible to a read by another thread only if the write operation happens-before the read operation", with the `synchronized`, `volatile`, `Thread.start` and `Thread.join` edges enumerated. jcstress sample `jmm/basic/BasicJMM_06_Causality.java` — `PlainReads` observes `1, 0` in 0.09% of samples; `VolatileGuard` forbids it, zero samples. JLS §17.4.5 happens-before order.
