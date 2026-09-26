---
title: A check-then-act on a concurrent map is one atomic compute call, never a read followed by a put
rule_id: CC-08
domain: concurrency
triggers: ['containsKey\(', 'putIfAbsent\(', 'ConcurrentHashMap', 'ConcurrentMap', '[.]get\([^)]*\)\s*==\s*null', '[.]put\(', 'computeIfAbsent\(', '[.]merge\(']
scope: file
check_kind: semantic
severity_default: major
---

# A check-then-act on a concurrent map is one atomic compute call, never a read followed by a put

## Thesis
On a `ConcurrentMap`, a read whose result decides a subsequent write to the same key — `containsKey` then `put`, `get` returning `null` then `put`, `get` then `put` of a derived value — is written as one `computeIfAbsent`, `compute` or `merge` call, whose whole invocation is atomic.

## Rationale
A concurrent map guarantees atomicity per method call, not across two calls: retrievals do not block and overlap with updates, so between the read and the write a second thread can insert or replace the value, and the first thread's `put` then overwrites it. The lost update never shows in a single-threaded test. `computeIfAbsent`, `compute` and `merge` perform the entire method invocation atomically and invoke the function exactly once per invocation, returning the value that won when another thread got there first; `putIfAbsent` is atomic for the absent-then-insert case alone.

## Example
```java
bad:  if (!cache.containsKey(k)) cache.put(k, load(k));
      Integer n = counts.get(k); counts.put(k, n == null ? 1 : n + 1);
good: cache.computeIfAbsent(k, this::load);
      counts.merge(k, 1, Integer::sum);
```

## Limits
Applies to a map shared between threads: a field, or a local handed to another thread. A map confined to one thread, a map read and written under one lock that encloses both calls, and a map populated once before publication take the plain form. A tolerance stated in the project context — "duplicate load accepted, last writer wins" — rejects the finding. A function passed to `compute*` that updates the same map is a separate defect and not the fix here.

## Validator
On the triggered hunk find each read of a `ConcurrentMap` — `containsKey`, `get`, `getOrDefault` — whose result guards or feeds a `put`, `remove` or `replace` of the same key in the same method. Open the file to confirm the map is shared (a field, or a local passed to a thread, executor or callback) and that no lock or `synchronized` block encloses both calls. Validator question: **can a second thread write this key between the read and the write, and does the write then overwrite that thread's value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-08`, severity major, `file`, `symbol`, `code` = the read and the write quoted verbatim from the diff, `fix` = the single `computeIfAbsent`, `compute` or `merge` call, `rationale` naming the lost update).

## Source
`java.util.concurrent.ConcurrentHashMap#computeIfAbsent`, `#compute`, `#merge` Javadoc, Java SE 21 — "The entire method invocation is performed atomically. The supplied function is invoked exactly once per invocation of this method"; class Javadoc — "Retrieval operations (including get) generally do not block, so may overlap with update operations". `ConcurrentMap` class Javadoc — "A Map providing thread safety and atomicity guarantees", with `putIfAbsent` among the methods implementations override to keep them.
