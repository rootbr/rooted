---
title: A map keyed by an enum type is an EnumMap and a set of enum constants is an EnumSet, never a HashMap, HashSet, TreeMap or TreeSet
rule_id: PF-07
domain: performance
triggers: ['new HashMap<', 'new HashSet<', 'new LinkedHashMap<', 'new TreeMap<', 'new TreeSet<']
scope: file
check_kind: mechanical
severity_default: minor
---

# A map keyed by an enum type is an EnumMap and a set of enum constants is an EnumSet, never a HashMap, HashSet, TreeMap or TreeSet

## Thesis
A `Map` whose key type is an `enum` is created as `new EnumMap<>(Kind.class)`; a `Set` of enum constants is created through `EnumSet.noneOf`, `of`, `allOf` or `copyOf`. A `HashMap`, `HashSet`, `TreeMap` or `TreeSet` over an enum key is replaced by these forms.

## Rationale
An `EnumMap` is represented internally as an array indexed by the constant's ordinal: a lookup is one array read with no hashing, no bucket, no node object and no `equals` call, and iteration follows declaration order. An `EnumSet` is a bit vector: membership, union and intersection are word operations, and bulk operations against another enum set run on whole words. A `HashMap` over the same keys allocates a node per entry, hashes on every access and walks a bucket; a `TreeMap` compares on every step. Both enum forms are documented as extremely compact and efficient.

## Example
```java
bad:  Map<Level, Handler> handlers = new HashMap<>();
      Set<Level> enabled = new HashSet<>();
good: Map<Level, Handler> handlers = new EnumMap<>(Level.class);
      Set<Level> enabled = EnumSet.noneOf(Level.class);
```

## Limits
Applies when the key or element type is an enum. An `EnumMap` permits no `null` key; code that stores a `null` key keeps a `HashMap` and says why. A map written concurrently by several threads uses `ConcurrentHashMap` or wraps the `EnumMap` in `Collections.synchronizedMap`; this rule does not choose between them. An immutable literal built with `Map.of` or `Set.of` is out of scope. An `ordinal()`-indexed array is the same representation and is not flagged.

## Validator
On the triggered hunk find each `HashMap`, `HashSet`, `LinkedHashMap`, `TreeMap` or `TreeSet` construction. Open the file to resolve the key or element type and confirm it is an `enum`. Validator question: **is this map keyed, or this set typed, by an enum while using a hash or tree representation?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-07`, severity minor, `file`, `symbol`, `code` = the construction quoted verbatim from the diff, `fix` = the `EnumMap` or `EnumSet` form, `rationale` naming the array-by-ordinal or bit-vector representation).

## Source
`java.util.EnumMap` class Javadoc, Java SE 21 — "Enum maps are represented internally as arrays. This representation is extremely compact and efficient"; "Null keys are not permitted." `java.util.EnumSet` class Javadoc — "Enum sets are represented internally as bit vectors. This representation is extremely compact and efficient... Even bulk operations (such as containsAll and retainAll) should run very quickly if their argument is also an enum set."
