---
title: A CopyOnWriteArrayList holds a collection that is traversed far more often than it is mutated, because every mutation copies the whole array
rule_id: CC-40
domain: concurrency
triggers: ['CopyOnWriteArrayList', 'CopyOnWriteArraySet']
scope: file
check_kind: semantic
severity_default: minor
---

# A CopyOnWriteArrayList holds a collection that is traversed far more often than it is mutated, because every mutation copies the whole array

## Thesis
A `CopyOnWriteArrayList` or `CopyOnWriteArraySet` is chosen for a collection whose contents change rarely relative to how often it is iterated — listeners, handlers, a configuration list — and never as a thread-safe list for a log, a queue, a buffer or any collection that grows or churns per request; those take a bounded `BlockingQueue` or a lock around an `ArrayList`.

## Rationale
Every mutative operation — `add`, `set`, `remove`, `addAll` — makes a fresh copy of the whole underlying array: an `add` is O(n) in the current size and allocates n references, so n appends cost O(n²) copying and leave n discarded arrays for the collector. The class documentation calls this ordinarily too costly and reserves the structure for the case where traversal operations vastly outnumber mutations. What the copying buys is a traversal that needs no synchronization and cannot see interference: an iterator holds the array as of its creation, never throws `ConcurrentModificationException`, never reflects later changes, and refuses `remove`, `set` and `add` on itself with `UnsupportedOperationException`. A collection written per request and read once, or written and read at similar rates, pays the copying and gains nothing.

## Example
```java
bad:  private final List<Event> log = new CopyOnWriteArrayList<>();      // appended on every request
      void record(Event e) { log.add(e); }
good: private final BlockingQueue<Event> log = new ArrayBlockingQueue<>(10_000);
      void record(Event e) { if (!log.offer(e)) dropped.increment(); }        // dropped: a LongAdder
```

## Limits
Applies to a collection whose mutation rate, as the file shows it, is comparable to or above its traversal rate: appends in a request path, a loop that adds elements one by one, a periodic clear-and-refill. A listener or subscriber registry mutated at startup or on rare configuration changes is the intended use. A small list rebuilt occasionally is fine. A project-context statement of the write rate rejects the finding. An `addAll` or a single replacement of the contents copies once and is the cheapest way to change a read-mostly list.

## Validator
On the triggered hunk find the declaration or construction of the copy-on-write collection. Open the file and list the call sites that mutate it and those that iterate it; judge the rates from where they sit: a request handler, a loop, an initialization block, an event callback. Validator question: **is this copy-on-write collection mutated as often as, or more often than, it is traversed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-40`, severity minor, `file`, `symbol`, `code` = the declaration and the mutating call quoted verbatim from the diff, `fix` = a bounded `BlockingQueue` (`new ArrayBlockingQueue<>(cap)` or `new LinkedBlockingQueue<>(cap)`), `ConcurrentHashMap.newKeySet()` or a locked `ArrayList`, `rationale` naming the full-array copy per mutation).

## Source
`java.util.concurrent.CopyOnWriteArrayList` class Javadoc, Java SE 21 — "all mutative operations (add, set, and so on) are implemented by making a fresh copy of the underlying array. This is ordinarily too costly, but may be more efficient than alternatives when traversal operations vastly outnumber mutations, and is useful when you cannot or don't want to synchronize traversals, yet need to preclude interference among concurrent threads"; the snapshot iterator "will not reflect additions, removals, or changes to the list since the iterator was created. Element-changing operations on iterators themselves (remove, set, and add) are not supported. These methods throw UnsupportedOperationException".
