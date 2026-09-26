---
title: A compareAndSet on a reference that can be recycled, or on a value that can repeat, carries a stamp or mark so an A-B-A change is detected
rule_id: CC-28
domain: concurrency
triggers: ['compareAndSet\(', 'weakCompareAndSet', 'compareAndExchange\(', 'AtomicReference<', 'AtomicStampedReference', 'AtomicMarkableReference']
scope: file
check_kind: semantic
severity_default: major
---

# A compareAndSet on a reference that can be recycled, or on a value that can repeat, carries a stamp or mark so an A-B-A change is detected

## Thesis
A CAS loop whose expected value can be observed again after intervening changes — a node taken from a pool and reinserted, a counter that wraps, a sequence that repeats, a reference to an object that is mutated and put back — compares a `(reference, stamp)` pair through `AtomicStampedReference` or a `(reference, mark)` pair through `AtomicMarkableReference`, or installs a fresh object on every change so that equality of reference implies no change.

## Rationale
`compareAndSet` decides by equality of the current value with the expected one; it cannot tell that the value went from A to B and back to A in between. A lock-free stack whose pop reads `top = N1` and prepares `CAS(top, N1, N1.next)` while another thread pops N1 and N2 and pushes N1 back with a different `next` succeeds and installs a stale successor: the structure is corrupted and nothing throws. The JDK's non-blocking collections avoid this by never reusing nodes — a removed node is left to the garbage collector, so the same reference cannot reappear with different contents, and no counted pointers are needed. The defect returns when code recycles nodes through a pool, keys a CAS on a small integer that wraps, or CASes a reference to a mutable object it later mutates in place. A stamp incremented on every modification makes `(A, n)` differ from `(A, n + 2)`, and the CAS fails as intended.

## Example
```java
bad:  Node old = top.get();                        // N1, later returned to the pool and re-pushed
      top.compareAndSet(old, old.next);            // succeeds although old.next is stale
good: int[] st = new int[1];
      Node old = top.get(st);
      top.compareAndSet(old, old.next, st[0], st[0] + 1);
```

## Limits
Applies to a CAS whose expected value can recur: recycled or pooled nodes, wrapping counters, sequence numbers, references to objects mutated in place. An `AtomicReference` CAS on immutable objects created fresh for every change is safe: a reference seen twice is the same unchanged object, and the collector keeps it from being reused while anyone holds it. An `AtomicInteger` CAS on a value that is monotonic over the object's life — a state machine with no backward transition, an id that never wraps — cannot see A-B-A. A CAS used as a one-shot latch (`false` to `true`) has no B.

## Validator
On the triggered hunk find each CAS loop and identify the expected value. Open the file and trace where that value comes from and whether it can be produced again after other threads changed the structure: a pool or free list, a reset or reuse path, a mutable object the loop CASes and later mutates, a counter that wraps or is decremented. Validator question: **can the expected value equal the current value while the state it stands for has changed in between?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-28`, severity major, `file`, `symbol`, `code` = the CAS and the origin of its expected value quoted verbatim from the diff, `fix` = `AtomicStampedReference` or `AtomicMarkableReference` with the stamp bumped on every change, or fresh immutable objects per change, `rationale` naming the recurrence path).

## Source
`java.util.concurrent.atomic` package Javadoc, Java SE 21 — `AtomicStampedReference` "associates an integer value with a reference. This may be used for example, to represent version numbers corresponding to series of updates"; `AtomicMarkableReference` "associates a single boolean with a reference ... this bit might be used inside a data structure to mean that the object being referenced has logically been deleted"; `AtomicStampedReference` class Javadoc — "maintains an object reference along with an integer 'stamp', that can be updated atomically". `java.util.concurrent.ConcurrentLinkedQueue` implementation note in the source at `jdk-21-ga` — "like most non-blocking algorithms in this package, this implementation relies on the fact that in garbage collected systems, there is no possibility of ABA problems due to recycled nodes, so there is no need to use 'counted pointers' or related techniques seen in versions used in non-GC'ed settings". Michael and Scott, "Simple, Fast, and Practical Non-Blocking and Blocking Concurrent Queue Algorithms", PODC 1996, DOI 10.1145/248052.248106 — modification counters against A-B-A; unfetched.
