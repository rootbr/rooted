---
title: A read-modify-write on a shared field is an atomic operation, never a plain or volatile increment
rule_id: CC-09
domain: concurrency
triggers: ['\+\+', '--', '\+=', '-=', '\*=', '\|=', '&=', 'volatile']
scope: file
check_kind: semantic
severity_default: major
---

# A read-modify-write on a shared field is an atomic operation, never a plain or volatile increment

## Thesis
A field that several threads update with `++`, `--`, a compound assignment such as `+=`, or a read followed by a write of a value derived from it is updated through an atomic operation — `AtomicInteger`, `AtomicLong`, `LongAdder`, a `VarHandle` `getAndAdd`, or one lock enclosing the read and the write. Declaring the field `volatile` does not make the update atomic.

## Rationale
`counter++` is three operations — read, add, write — and two threads that interleave them both read the same value and both write the same result, so one increment is lost. `volatile` orders and publishes each single read and each single write; it joins no two of them, so a volatile increment loses updates exactly as a plain one does. A stress test of two threads each running `++v` once on a plain `int` observes the pair `(1, 1)` — both threads saw the same value — in about 10% of samples. The atomic classes update a single variable atomically; `incrementAndGet` and `getAndAdd` issue one read-modify-write with the memory effects of a volatile access.

## Example
```java
bad:  private volatile int hits;
      void record() { hits++; }
good: private final AtomicInteger hits = new AtomicInteger();
      void record() { hits.incrementAndGet(); }
```

## Limits
Applies to a field written by more than one thread: an instance field of a shared object, or a static field. A local variable, a field of a thread-confined object, and a field whose every write sits inside one `synchronized` block or `Lock` region on the same monitor take the plain form. A field that one thread writes and others only read needs `volatile`, not an atomic. A tolerance stated in the project context — "an approximate statistics counter; lost increments accepted" — rejects the finding. A counter incremented from many threads at high rate is better served by `LongAdder` than by an atomic, which is a performance note, not this finding.

## Validator
On the triggered hunk find each `++`, `--`, compound assignment, or read-then-write of a derived value whose target is a field, not a local. Open the file: confirm the field is reachable from more than one thread (a shared object's instance field, a static field, a field touched from a task, callback or request handler) and that no lock encloses every read-modify-write of it. Validator question: **can two threads execute this read-modify-write at the same time, so that one of the two updates is lost?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-09`, severity major, `file`, `symbol`, `code` = the field declaration and the update quoted verbatim from the diff, `fix` = the atomic type or the lock region, `rationale` naming the lost update and, where the field is `volatile`, that `volatile` orders single accesses only).

## Source
jcstress sample `openjdk/jcstress`, `jcstress-samples/.../samples/api/API_01_Simple.java` — two actors each run `++v` on an `int`; outcome `1, 1` "Both actors came up with the same value: atomicity failure" observed at 10.1% of samples. `java.util.concurrent.atomic.AtomicInteger#incrementAndGet` Javadoc, Java SE 21 — "Atomically increments the current value, with memory effects as specified by VarHandle.getAndAdd". SEI CERT Oracle Coding Standard for Java, VNA02-J "Ensure that compound operations on shared variables are atomic" — the `++`, `--` and compound-assignment operators always form compound operations.
