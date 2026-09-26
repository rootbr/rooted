---
title: An object held in an AtomicReference is replaced through updateAndGet or compareAndSet, never mutated in place through get()
rule_id: CC-48
domain: concurrency
triggers: ['AtomicReference<', '[.]get\(\)[.]', 'updateAndGet\(', 'getAndUpdate\(', 'accumulateAndGet\(', 'compareAndSet\(']
scope: file
check_kind: mechanical
severity_default: major
---

# An object held in an AtomicReference is replaced through updateAndGet or compareAndSet, never mutated in place through get()

## Thesis
The object an `AtomicReference` holds is immutable, or treated as such: every change is a new object installed with `updateAndGet`, `accumulateAndGet` or a `compareAndSet` loop whose function builds the new object from the old. `ref.get().add(x)`, `ref.get().put(k, v)` and `ref.get().field = v` do not appear.

## Rationale
The atomic classes support lock-free thread-safe programming on single variables; the variable here is the reference, and what is atomic is reading, writing and comparing-and-swapping that reference. The object behind it receives nothing — a `List` reached through `get()` is a plain `ArrayList` mutated by every thread that calls `get()`, with the lost updates, corrupted structure and stale reads of any unsynchronized shared object. The usual reading, "it is in an atomic, so it is thread-safe", is exactly wrong for the contents. The `updateAndGet` family applies a function to the current value and installs the result atomically, re-applying the function on contention; when the function returns a fresh object built from the old one — a copied list with the element added, a record with one field changed — concurrent updates serialize on the compare-and-swap and none is lost. The function is documented as side-effect-free because it may run more than once.

## Example
```java
bad:  private final AtomicReference<List<String>> tags = new AtomicReference<>(new ArrayList<>());
      void tag(String t) { tags.get().add(t); }                               // plain ArrayList, no atomicity
good: private final AtomicReference<List<String>> tags = new AtomicReference<>(List.of());
      void tag(String t) { tags.updateAndGet(old -> { var n = new ArrayList<>(old); n.add(t); return List.copyOf(n); }); }
```

## Limits
Applies when the referenced object is mutable and shared through the reference. An `AtomicReference` to an immutable value — a `String`, a record, `List.of` — or to a thread-safe object such as a `ConcurrentHashMap`, whose own methods are the atomic unit, is fine to use through `get()`. A mutation under a lock that also guards every other access to the object, or a mutable object confined to one thread and published once through the reference, is correct. An update function that reads other shared state is a separate concern.

## Validator
On the triggered hunk find each `AtomicReference` and each `.get().` chain or field access on its value; open the file to see the value's type and whether it is mutable and mutated through the reference from more than one thread. Validator question: **is the object behind this reference mutated in place while other threads reach it through the same reference?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-48`, severity major, `file`, `symbol`, `code` = the `get()` mutation quoted verbatim from the diff, `fix` = the `updateAndGet` with a fresh object built from the old, or an immutable value type, `rationale` naming that the atomicity covers the reference, not the referent).

## Source
`java.util.concurrent.atomic` package Javadoc, Java SE 21 — "A small toolkit of classes that support lock-free thread-safe programming on single variables"; `java.util.concurrent.atomic.AtomicReference` class Javadoc — "An object reference that may be updated atomically"; `#updateAndGet` — "Atomically updates ... the current value with the results of applying the given function, returning the updated value. The function should be side-effect-free, since it may be re-applied when attempted updates fail due to contention among threads".
