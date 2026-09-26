---
title: A large collection of int or long values on a hot path is a primitive array or a primitive-specialized collection, not a Map, Set or List of boxed Integer or Long
rule_id: PF-09
domain: performance
triggers: ['Map<(Integer|Long|Short|Byte|Character),', 'Map<\w+,\s*(Integer|Long|Double|Float)>', 'Set<(Integer|Long|Short|Character)>', 'List<(Integer|Long|Double|Float)>', '(Integer|Long|Double)\[\]']
scope: file
check_kind: semantic
severity_default: minor
---

# A large collection of int or long values on a hot path is a primitive array or a primitive-specialized collection, not a Map, Set or List of boxed Integer or Long

## Thesis
A map, set or list that holds many `int`, `long` or `double` values on a per-request or per-event path stores them as primitives — an `int[]` or `long[]` indexed directly, a `BitSet`, or a primitive-specialized map or list from a library such as Eclipse Collections, fastutil or HPPC — rather than as `HashMap<Integer, …>`, `List<Long>` or `Set<Integer>`.

## Rationale
Every `Integer` or `Long` outside −128..127 is a separate heap object: boxing a key allocates it, and a `HashMap` then allocates a node that references the boxed key and the boxed value, so one int-to-int entry is three objects and their headers. A lookup boxes the probe, hashes it, walks a bucket and unboxes the result, and the value objects are scattered across the heap, so a scan of the collection chases pointers instead of reading one contiguous array. A primitive array or specialized map stores the values inline, in one contiguous block, with no boxing on either side of the call.

## Example
```java
bad:  Map<Integer, Integer> countByCode = new HashMap<>();
      for (int c : codes) countByCode.merge(c, 1, Integer::sum);
good: int[] countByCode = new int[MAX_CODE + 1];
      for (int c : codes) countByCode[c]++;
      // sparse or unbounded keys: a MutableIntIntMap or Int2IntOpenHashMap from a primitive-collection library
```

## Limits
Applies to collections that are large (thousands of entries or more) or touched per event on a hot path. A small map, a configuration table read at startup, a value that must be nullable, and an API that requires a `java.util` collection type at its boundary are out of scope. A project that admits no third-party collection library keeps the boxed form where a plain array cannot serve (sparse or negative keys), and the finding is downgraded to a note. Boxing of a loop-local variable or accumulator is a separate concern from the collection's element type.

## Validator
On the triggered hunk find each collection typed over a boxed primitive. Open the file to estimate its size (how it is filled, whether bounded by a request or a dataset) and whether it is read or written on a per-request, per-event or per-element path. Validator question: **does this collection hold many boxed primitives on a hot path where an array or a primitive-specialized collection could hold them inline?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-09`, severity minor, `file`, `symbol`, `code` = the collection declaration quoted verbatim from the diff, `fix` = the array or primitive-specialized collection, `rationale` naming the per-entry boxed objects and the pointer chase).

## Source
`java.lang.Integer#valueOf(int)` and `java.lang.Long#valueOf(long)` Javadoc, Java SE 21 — "This method will always cache values in the range -128 to 127, inclusive, and may cache other values outside of this range"; the cache is preferred to the constructor because it "is likely to yield significantly better space and time performance", so a value outside it is a fresh object. `java.util.HashMap` source, Java SE 21 — each mapping is a `Node` holding `hash`, `key`, `value` and `next`. JMH benchmarks `eclipse-collections/eclipse-collections`, `jmh-tests/.../jmh/IntListJMHTest.java` (boxed `List<Integer>` pipelines beside `IntArrayList`) and `IntIntMapTest.java` (`IntIntHashMap` get and put from 64 to 6.4 million entries) — the primitive forms and their harness; no figures are carried here.
