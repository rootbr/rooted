---
title: Two fields written at high rate by different threads do not share a cache line, so they are annotated @Contended, padded through a superclass chain, or split into separate objects
rule_id: PF-01
domain: performance
triggers: ['volatile', 'Atomic(Long|Integer|Boolean|Reference)', 'AtomicLongArray', 'AtomicIntegerArray', 'Contended', 'VarHandle', 'compareAndSet\(', 'long\[\]', 'LongAdder']
scope: file
check_kind: semantic
severity_default: minor
---

# Two fields written at high rate by different threads do not share a cache line, so they are annotated @Contended, padded through a superclass chain, or split into separate objects

## Thesis
Two counters, flags, indices or other fields that different threads write at high rate — a producer's and a consumer's index, per-thread statistics slots in one object or one array — are separated by a cache line: annotated `@jdk.internal.vm.annotation.Contended` (run with `-XX:-RestrictContended` and the package exported), padded through a chain of superclasses, or moved into separate objects, so a write by one thread does not invalidate the line the other thread is working on.

## Rationale
A cache line (64 bytes on common x86-64 parts) is the unit of coherence: when a core writes a field, every other core's copy of the whole line is invalidated, and the next access there misses and re-fetches it. Two fields that different threads write, laid out within the same 64 bytes, force this ping-pong on every write although the threads share no data — false sharing. Declaration order does not fix the layout: the virtual machine reorders fields of the same width, so single padding fields can end up beside each other. `@Contended` makes the runtime isolate the field (or, on a class, the whole object) in its own contention group at the cost of space; a chain of superclasses each carrying padding fields survives reordering because a superclass's fields are usually laid out first, which the padding chain relies on; separate objects sit on separate lines. Each fix costs space, so it is warranted only where the fields are hot and written per thread.

## Example
```java
bad:  final class Counters { volatile long produced; volatile long consumed; }
      // producer thread writes produced, consumer thread writes consumed, both per message
good: final class Counters {
          @jdk.internal.vm.annotation.Contended volatile long produced;
          @jdk.internal.vm.annotation.Contended volatile long consumed;
      }
```

## Limits
Applies to fields that different threads write frequently (per event, per message). Fields read by many threads and written rarely, fields written by one thread only, and fields of an object confined to one thread take the plain layout. `LongAdder` and the other striped accumulators already pad their cells. `@Contended` outside the JDK needs `-XX:-RestrictContended` and `--add-exports java.base/jdk.internal.vm.annotation=ALL-UNNAMED`; a project that forbids internal APIs uses the superclass-padding form or separate objects. A tolerance stated in the project context — "throughput of this counter is not on the hot path" — rejects the finding.

## Validator
On the triggered hunk find fields written from more than one thread: `volatile` fields, atomics, `VarHandle` targets, ring-buffer indices, per-thread slots in one array. Open the file and pair them: two such fields declared in one class, or adjacent slots of one array, that different threads write at high rate. Confirm there is no `@Contended`, no padding chain and no split between them. Validator question: **do two hot fields written by different threads sit in one object or one array region without padding between them?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-01`, severity minor, `file`, `symbol`, `code` = the two field declarations quoted verbatim from the diff, `fix` = the `@Contended` annotations or the padded superclass chain, `rationale` naming the shared cache line and the write-invalidate ping-pong between the two threads).

## Source
`jdk.internal.vm.annotation.Contended` Javadoc, Java SE 21 — fields "expected to encounter memory contention, generally in the form of 'false sharing'" should "reside in locations isolated from those of other objects or fields"; "warranted only when the performance impact of this time/space tradeoff is intrinsically worthwhile; for example, in concurrent contexts in which each instance of the annotated class is often accessed by a different thread". JMH sample `openjdk/jmh`, `jmh-samples/.../JMHSample_22_FalseSharing.java` — "If two threads access (and possibly modify) the adjacent values in memory, chances are, they are modifying the values on the same cache line. This can yield significant (artificial) slowdowns"; padding by extra fields "is not versatile because JVMs can freely rearrange the field order, even of the same type"; the hierarchy trick uses "the fact that superclass fields are usually laid out first". JMH benchmark `ionutbalosin/jvm-performance-benchmarks`, `.../compiler/FalseSharingBenchmark.java` — baseline, `@Contended` and superclass-padding variants, run with `-XX:-RestrictContended`. JEP 142 (the annotation's origin) — not fetched from the authoring environment.
