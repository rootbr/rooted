---
title: A key or element of a hash- or comparison-based collection, ConcurrentHashMap and TreeMap included, is not mutated in a way that changes equals, hashCode or compareTo while it is in the collection
rule_id: PF-06
domain: performance
triggers: ['HashMap<', 'HashSet<', 'LinkedHashMap<', 'LinkedHashSet<', 'ConcurrentHashMap<', 'ConcurrentMap<', 'TreeMap<', 'TreeSet<', 'containsKey\(', 'hashCode\(\)', 'equals\(Object']
scope: callers
check_kind: semantic
severity_default: major
---

# A key or element of a hash- or comparison-based collection, ConcurrentHashMap and TreeMap included, is not mutated in a way that changes equals, hashCode or compareTo while it is in the collection

## Thesis
The fields that a key type's `equals`, `hashCode` or `compareTo` read stay unchanged for as long as the object is a key or element of any hash- or comparison-based collection, `ConcurrentHashMap` and `TreeMap` included: key types are immutable (a `record`, final fields), or the code removes the entry before mutating and re-inserts it afterwards. A `TreeMap` or `TreeSet` has the analogous hazard through `compareTo`, and the same check applies.

## Rationale
The map stores each key in the bucket its hash code selected at insertion. When a field that feeds `hashCode` changes afterwards, a later `get`, `containsKey` or `remove` computes the new code, looks in a different bucket and reports the key absent, while the entry remains reachable through iteration — the behavior of the map is unspecified from that point. The stale entry cannot be removed by key, so the map grows without bound, and a set may hold two elements that now compare equal. The rule binds every `Map` and `Set` implementation, `ConcurrentHashMap` among them, because it is the interface contract that leaves the behavior unspecified. A sorted map places each key by `compareTo` (or its comparator) instead of a hash code, and that ordering must be consistent with `equals` for the map contract to hold, so a key whose comparison fields change after insertion is likewise sought along a path that no longer leads to it. The defect passes every test that never mutates after insertion.

## Example
```java
bad:  Map<Endpoint, Conn> pool = new HashMap<>();
      pool.put(ep, conn);
      ep.setPort(newPort);          // hashCode changes; pool.get(ep) now misses
good: record Endpoint(String host, int port) {}                    // immutable key
      pool.remove(ep); pool.put(new Endpoint(ep.host(), newPort), conn);
```

## Limits
Applies to key types whose `equals`/`hashCode`, or `compareTo`, read mutable state. A key type with identity semantics (no `equals` override and no ordering), an immutable key type, and a mutation of fields that `equals`, `hashCode` and `compareTo` ignore are correct. An `IdentityHashMap` is unaffected.

## Validator
On the triggered hunk identify the key or element type of each hash- or comparison-based collection. Follow the type across the repository: does it override `equals`/`hashCode`, or implement `compareTo` (or get placed by a comparator), over fields that have setters or are non-final? Then look for a write to such a field on an object after it was put into the collection, in the same method or in a method the diff touches. Validator question: **can a field that this key's hashCode or compareTo reads change while the object is inside the map or set?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-06`, severity major, `file`, `symbol`, `code` = the insertion and the later mutation, or the mutable key field, quoted verbatim from the diff, `fix` = an immutable key type or remove-mutate-reinsert, `rationale` naming the bucket or tree path along which the entry becomes unreachable).

## Source
`java.util.Map` interface Javadoc, Java SE 21 — "Note: great care must be exercised if mutable objects are used as map keys. The behavior of a map is not specified if the value of an object is changed in a manner that affects equals comparisons while the object is a key in the map." `java.util.Set` interface Javadoc — the same note for set elements: "The behavior of a set is not specified if the value of an object is changed in a manner that affects equals comparisons while the object is an element in the set." `java.util.HashMap` class Javadoc — entries live in buckets selected by hash code, rebuilt on rehash. `java.util.TreeMap` class Javadoc — the ordering "must be consistent with equals if this sorted map is to correctly implement the Map interface", because "a sorted map performs all key comparisons using its compareTo (or compare) method". The `Map` and `Set` notes are on the interfaces and so bind `ConcurrentHashMap`; the `compareTo` analogue is stated for sorted maps through the consistency requirement, not as a note of its own.
