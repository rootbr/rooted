---
title: Iteration, spliteration or streaming of a Collections.synchronizedXxx view runs inside a synchronized block on the view itself
rule_id: CC-47
domain: concurrency
triggers: ['synchronized(List|Map|Set|Collection|Sorted(Map|Set)|Navigable(Map|Set))\(', '[.]iterator\(\)', '[.]stream\(\)', '[.]spliterator\(\)', '[.]forEach\(']
scope: file
check_kind: mechanical
severity_default: major
---

# Iteration, spliteration or streaming of a Collections.synchronizedXxx view runs inside a synchronized block on the view itself

## Thesis
Every traversal of a collection wrapped by `Collections.synchronizedList`, `synchronizedMap`, `synchronizedSet` or their sorted and navigable variants — a for-each loop, `iterator()`, `spliterator()`, `stream()`, and for a map its `keySet()`, `values()` and `entrySet()` views — is enclosed in `synchronized (view) { ... }` on the wrapper object the factory returned, not on the backing collection and not on a sub-view.

## Rationale
The wrapper synchronizes each method call on itself, so `add`, `get` and `size` are individually safe. A traversal is many calls — `hasNext`, `next`, `hasNext` — with no lock held between them, and the backing collection is an ordinary `ArrayList` or `HashMap`: a concurrent `add` during the loop is a structural modification that the fail-fast iterator reports with `ConcurrentModificationException` when it notices and silently corrupts the traversal — a skipped or repeated element, a `null`, a half-resized table — when it does not. The documentation makes external synchronization on the returned object imperative for traversal via iterator, spliterator or stream and states that failure to follow it may result in non-deterministic behavior. The monitor must be the wrapper: the mutators lock the wrapper, so a block on the backing list or on a `subList` view excludes nothing.

## Example
```java
bad:  List<Job> jobs = Collections.synchronizedList(new ArrayList<>());
      for (Job j : jobs) run(j);                             // no lock between hasNext() and next()
good: synchronized (jobs) { for (Job j : jobs) run(j); }
      // or: List<Job> snap; synchronized (jobs) { snap = List.copyOf(jobs); } for (Job j : snap) run(j);
```

## Limits
Applies to the views returned by `Collections.synchronizedXxx` when they are shared between threads. A view confined to one thread needs no block. A traversal already inside a `synchronized (view)` block, or in a method whose every caller holds that monitor as the file shows, is correct. A copy taken under the monitor and traversed outside it is the pattern for long loops. `ConcurrentHashMap`, `CopyOnWriteArrayList` and the other `java.util.concurrent` collections have weakly consistent or snapshot iterators and need no block.

## Validator
On the triggered hunk find each traversal of a synchronized view — identify the collection's origin in the file as `Collections.synchronized...` — and check the enclosing statements for `synchronized (view)` on that same reference. Validator question: **is a synchronized view traversed outside a block on the view's own monitor?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-47`, severity major, `file`, `symbol`, `code` = the traversal quoted verbatim from the diff, `fix` = the `synchronized (view)` block around it, or a copy taken under the monitor, `rationale` naming the calls between which no lock is held and the fail-fast backing collection).

## Source
`java.util.Collections#synchronizedList` Javadoc, Java SE 21 — "It is imperative that the user manually synchronize on the returned list when traversing it via Iterator, Spliterator or Stream ... Failure to follow this advice may result in non-deterministic behavior"; `#synchronizedMap` — the same for the map's collection views, with the example synchronizing on the map rather than on the view; `#synchronizedSortedSet` — "synchronized (s) {  // Note: s, not s2!!!" for a sub-view.
