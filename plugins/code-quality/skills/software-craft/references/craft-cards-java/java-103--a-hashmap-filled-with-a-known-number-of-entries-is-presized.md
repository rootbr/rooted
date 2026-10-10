---
title: A HashMap or HashSet filled with a known number of entries is created with HashMap.newHashMap(n) or a capacity that holds them without rehashing
rule_id: JAVA-103
domain: performance
step: [implement]
applies_to: [java]
triggers: ['new HashMap<', 'new HashSet<', 'new LinkedHashMap<', 'new LinkedHashSet<', 'new HashMap\(', 'new HashSet\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A HashMap or HashSet filled with a known number of entries is created with HashMap.newHashMap(n) or a capacity that holds them without rehashing

## Thesis
When the number of entries a map or set will hold is known at construction — the size of a source collection, an array length, a fixed count — the map is created with `HashMap.newHashMap(n)` / `HashSet.newHashSet(n)` (Java 19 and later) or `new HashMap<>(capacity)` with `capacity` greater than `n / 0.75`, rather than default-sized and grown while filling.

## Rationale
A default `HashMap` starts with 16 buckets and a load factor of 0.75; when the entry count exceeds the product of the two, the table is rehashed — rebuilt with about twice the buckets — and every entry is re-inserted. Filling n entries into a default map rehashes on the way past 12, 24, 48, … entries, each pass copying the whole table. If the initial capacity is greater than the maximum number of entries divided by the load factor, no rehash operation ever occurs. `HashMap.newHashMap(n)` computes that capacity; the hand-written form is `n * 4 / 3 + 1`. Passing the raw count as the capacity is off by the load factor and may still rehash once.

## Example
```java
bad:  Map<String, User> byId = new HashMap<>();
      for (User u : users) byId.put(u.id(), u);
good: Map<String, User> byId = HashMap.newHashMap(users.size());
      for (User u : users) byId.put(u.id(), u);
```

## Limits
Applies when the count is known at the construction site and large enough to exceed the default threshold of 12 entries. A map whose final size is unknown, a map of a few entries, and one built by `Collectors.toMap` or `toSet` (whose map supplier the caller does not size) are out of scope. `ConcurrentHashMap(int)` sizes itself to accommodate that many elements and needs no adjustment.

## Validator
On the triggered hunk find each `new HashMap<>()`, `new HashSet<>()` (or the `Linked` variant) with no capacity or with the raw count as capacity. Look in the same hunk for the filling loop or bulk `put`/`add` and whether the count is available there (`.size()`, `.length`, a constant). Validator question: **is the entry count known at construction and larger than 12, while the map is built default-sized or with the raw count as its capacity?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-103`, severity minor, `file`, `symbol`, `code` = the constructor call quoted verbatim from the diff, `fix` = `HashMap.newHashMap(n)` or the load-factor-adjusted capacity, `rationale` naming the rehash passes avoided).
