---
title: A function passed to compute, computeIfAbsent or merge never updates the same concurrent map
rule_id: CC-11
domain: concurrency
triggers: ['computeIfAbsent\(', 'computeIfPresent\(', '[.]compute\(', '[.]merge\(']
scope: file
check_kind: mechanical
severity_default: major
---

# A function passed to compute, computeIfAbsent or merge never updates the same concurrent map

## Thesis
The mapping or remapping function handed to `ConcurrentHashMap.compute`, `computeIfAbsent`, `computeIfPresent` or `merge` performs no update on the same map — no `put`, `remove`, `replace`, `clear` or nested `compute*` / `merge` on it, for any key — and stays short.

## Rationale
The map runs the function while holding the bin that owns the key, and other threads' updates to that bin block until the function returns. An update to the same map from inside the function is a recursive update: when the map detects it, the call fails with `IllegalStateException`; when it does not, the update waits on a bin the calling thread already holds and the call never completes. A long function stalls every other thread that needs the bin, so the function does the minimum and the map work happens before or after the call.

## Example
```java
bad:  totals.compute(to, (key, current) -> {
          totals.merge(from, -amount, Integer::sum);
          return (current == null ? 0 : current) + amount;
      });
good: totals.merge(from, -amount, Integer::sum);
      totals.merge(to, amount, Integer::sum);
```

## Limits
Applies to a `ConcurrentHashMap` or a `ConcurrentMap` whose implementation documents the same restriction. A `HashMap` passed through `Map.compute` on one thread holds no bin lock, so a nested call there is a different concern. A read of another key from inside the function — `get`, `containsKey` — takes no lock and throws nothing; it can return a stale or absent value, which is a design question for the author and not this finding. A function that updates a different map, or that uses values captured before the call, is correct.

## Validator
On the triggered hunk take each `compute`, `computeIfAbsent`, `computeIfPresent` or `merge` call on a concurrent map and read the function body it receives, whether a lambda, a method reference or a named class. Flag when the body calls an updating method — `put`, `putIfAbsent`, `remove`, `replace`, `clear`, `compute*`, `merge` — on the same map instance, or calls a method of the enclosing class that performs such an update; open the file to read the body of each enclosing-class method the function calls. Validator question: **does the function body update the map it was passed to?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-11`, severity major, `file`, `symbol`, `code` = the `compute*` or `merge` call with the offending line of its function quoted verbatim from the diff, `fix` = the nested update moved out of the function into a separate call before or after it, `rationale` naming the recursive update and the `IllegalStateException`).

## Source
`java.util.concurrent.ConcurrentHashMap#computeIfAbsent`, `#compute` Javadoc, Java SE 21 — "The mapping function must not modify this map during computation"; "Some attempted update operations on this map by other threads may be blocked while computation is in progress, so the computation should be short and simple"; throws `IllegalStateException` "if the computation detectably attempts a recursive update to this map that would otherwise never complete". `#merge` — the function "must not attempt to update any other mappings of this Map". Class Javadoc — "Retrieval operations (including get) generally do not block", which is why a read inside the function is outside the rule.
