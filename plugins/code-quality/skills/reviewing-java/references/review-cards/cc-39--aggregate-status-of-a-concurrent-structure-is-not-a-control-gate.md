---
title: An aggregate status of a concurrent structure — size, isEmpty, containsValue, a LongAdder sum — is read for monitoring, never as a control-flow gate
rule_id: CC-39
domain: concurrency
triggers: ['[.]size\(\)\s*[<>=!]', '[.]isEmpty\(\)', '[.]containsValue\(', '[.]mappingCount\(', '[.]sum\(\)', 'ConcurrentHashMap', 'ConcurrentLinkedQueue']
scope: file
check_kind: mechanical
severity_default: major
---

# An aggregate status of a concurrent structure — size, isEmpty, containsValue, a LongAdder sum — is read for monitoring, never as a control-flow gate

## Thesis
On a `ConcurrentHashMap`, `ConcurrentLinkedQueue`, `ConcurrentSkipListMap` or other concurrent collection, and on a `LongAdder`, the result of `size()`, `isEmpty()`, `containsValue()`, `mappingCount()` or `sum()` is not the condition of a branch that then reads or writes the structure — no "put if the size is below the limit", no "take the first if not empty", no "initialize if empty". Capacity is enforced by a bounded structure or a `Semaphore`, emptiness by the `null` return of `poll` or `peek`, presence by the per-key operation.

## Rationale
These methods report a transient state: on a `ConcurrentHashMap` the aggregate status methods are documented as useful only when the map is not undergoing concurrent updates — adequate for monitoring or estimation, not for program control; on a `ConcurrentLinkedQueue` `size()` is an O(n) traversal whose result may be inaccurate if the queue changes meanwhile; a `LongAdder.sum()` is not an atomic snapshot and may miss updates in flight. Even an exact count is stale by the time the branch runs: between `size() < MAX` and `put`, other threads insert and the limit is exceeded; between `!isEmpty()` and `iterator().next()`, the last element is removed and `NoSuchElementException` follows; between `isEmpty()` and `initialize()`, another thread initializes too. The atomic per-element operations — `putIfAbsent`, `computeIfAbsent`, `poll`, `offer` on a bounded queue — decide and act in one step; a count that must drive a decision is kept in an `AtomicInteger` updated together with the structure, or the structure is replaced by a bounded one whose `offer` refuses the excess.

## Example
```java
bad:  if (cache.size() < MAX) cache.put(k, v);
      if (!queue.isEmpty()) handle(queue.iterator().next());
good: if (slots.tryAcquire()) cache.put(k, v);           // Semaphore(MAX), released on removal
      Job j = queue.poll(); if (j != null) handle(j);
```

## Limits
Applies to a concurrent structure under concurrent updates. A structure confined to one thread, populated once before publication, or read under the same lock that guards every write has exact aggregates. A `size()` logged, exported as a metric, or used to size a new collection is the intended use. `mappingCount()` is the right call for a report on a map that may hold more than `Integer.MAX_VALUE` entries; it is still an estimate.

## Validator
On the triggered hunk find each `size()`, `isEmpty()`, `containsValue()`, `mappingCount()` or `sum()` whose result is compared in an `if`, `while` or ternary, and check whether the branch then reads or writes the same structure. Open the file and confirm the structure is concurrent: a field of a concurrent type, or a local handed to threads. Validator question: **does a branch on an aggregate status of a concurrent structure then act on that structure as if the status still held?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-39`, severity major, `file`, `symbol`, `code` = the aggregate read and the branch quoted verbatim from the diff, `fix` = the atomic per-element operation, bounded structure or `Semaphore` that replaces the gate, `rationale` naming the window between the count and the action).

## Source
`java.util.concurrent.ConcurrentHashMap` class Javadoc, Java SE 21 — "the results of aggregate status methods including size, isEmpty, and containsValue are typically useful only when a map is not undergoing concurrent updates in other threads. Otherwise the results of these methods reflect transient states that may be adequate for monitoring or estimation purposes, but not for program control"; `#mappingCount` — "This method should be used instead of size because a ConcurrentHashMap may contain more mappings than can be represented as an int. The value returned is an estimate". `java.util.concurrent.ConcurrentLinkedQueue#size` — "NOT a constant-time operation ... requires an O(n) traversal. Additionally, if elements are added or removed during execution of this method, the returned result may be inaccurate. Thus, this method is typically not very useful in concurrent applications". `java.util.concurrent.atomic.LongAdder#sum` — "The returned value is NOT an atomic snapshot ... concurrent updates that occur while the sum is being calculated might not be incorporated".
