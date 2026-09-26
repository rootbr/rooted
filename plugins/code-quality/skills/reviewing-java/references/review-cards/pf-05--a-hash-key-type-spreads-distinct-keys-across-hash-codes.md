---
title: A type used as a hash key returns distinct hash codes for distinct keys, never a constant or a single low-cardinality field
rule_id: PF-05
domain: performance
triggers: ['int hashCode\(', 'Objects[.]hash\(', 'Objects[.]hashCode\(', 'hashCode\(\)']
scope: file
check_kind: semantic
severity_default: minor
---

# A type used as a hash key returns distinct hash codes for distinct keys, never a constant or a single low-cardinality field

## Thesis
A class whose instances serve as `HashMap` keys or `HashSet` elements overrides `hashCode` so that keys unequal under `equals` usually get different hash codes: it combines the fields `equals` compares, including at least one high-cardinality field, and it does not return a constant, a type tag, or a field with a handful of distinct values.

## Rationale
A hash table places each key in the bucket its hash code selects; keys that share a code share a bucket, and a lookup then compares the probe against every entry there. Distinct integer results for unequal objects are not required by the contract, but using many keys with the same hash code is a sure way to slow down any hash table: a constant `hashCode` turns every operation into a scan of the whole map. `HashMap` converts a bucket holding 8 or more entries into a red-black tree once the table has 64 or more buckets (below that it resizes instead), so with `Comparable` keys the degradation stops at logarithmic time; with other keys it stays linear in the bucket's length. The cost is invisible in a unit test with a few entries and appears as CPU time in `HashMap.get` and `putVal` under load.

## Example
```java
bad:  @Override public int hashCode() { return 42; }
      @Override public int hashCode() { return kind.ordinal(); }   // three kinds, many keys
good: @Override public int hashCode() { return Objects.hash(kind, id, region); }
      // or: record CacheKey(Kind kind, long id, String region) {}
```

## Limits
Applies to a type stored as a key or element in a hash-based collection on a hot path. A type never used as a hash key, a value type whose `equals` compares one field that is itself high-cardinality, and a type that keeps `Object`'s identity hash on purpose (identity semantics) are out of scope. A hash code that combines fields differently from `equals` is a defect of the `equals`/`hashCode` contract, which this rule does not adjudicate.

## Validator
On the triggered hunk read each `hashCode` override. Open the file to see the fields `equals` compares and check that `hashCode` derives from them with at least one high-cardinality field (an id, a name, a numeric key). Confirm the type is used as a map key or set element (a `HashMap<ThisType, …>`, `HashSet<ThisType>`, `Set.of` or `Map.of` with it). Validator question: **does this key type's hashCode collapse many unequal keys onto one value or a few values?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-05`, severity minor, `file`, `symbol`, `code` = the `hashCode` body quoted verbatim from the diff, `fix` = a hash over the fields `equals` uses, `rationale` naming the bucket collision and the linear or tree scan it forces).

## Source
`java.lang.Object#hashCode` Javadoc, Java SE 21 — "the programmer should be aware that producing distinct integer results for unequal objects may improve the performance of hash tables". `java.util.HashMap` class Javadoc — "Note that using many keys with the same hashCode() is a sure way to slow down performance of any hash table. To ameliorate impact, when keys are Comparable, this class may use comparison order among keys to help break ties"; implementation notes in the same source — `TREEIFY_THRESHOLD = 8` and `MIN_TREEIFY_CAPACITY = 64`: a bin is converted to a tree when it holds that many nodes and the table has at least that many buckets; `treeifyBin` resizes instead below that.
