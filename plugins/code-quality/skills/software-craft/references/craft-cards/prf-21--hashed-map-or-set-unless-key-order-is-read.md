---
title: A map or set used only for lookups, insertions and removals by key is a hashed one, and a sorted map or set is chosen only where the code uses its key order
rule_id: PRF-21
domain: performance
step: [design, implement]
applies_to: [universal]
triggers: ['\bTree(Map|Set)\s*<|\bnew\s+Tree(Map|Set)\b|\bConcurrentSkipList(Map|Set)\b|\bBTree(Map|Set)\b|\bSorted(Dict|Set)\(|\b(btree|treemap)[.]New\w*(\[[^\]]*\])?\(']
scope: file
check_kind: semantic
severity_default: minor
---

# A map or set used only for lookups, insertions and removals by key is a hashed one, and a sorted map or set is chosen only where the code uses its key order

## Thesis
A map or set whose every use is a lookup, insertion, removal or membership test by key is a hashed map or set, which gives expected constant cost per operation, amortized for insertion, when the hash function disperses the keys; a sorted map or set, which pays a logarithmic cost on each operation that keeps or searches its order, is chosen where the code reads its key order: iteration sorted by key, a range of entries, the smallest or largest key, or the largest or smallest key below or above a value.

## Rationale
A hashed map's lookup, insertion and removal have expected O(1) cost, amortized for insertion, since an insertion that resizes the table takes O(n). The cost is expected, not guaranteed: two keys can produce the same hash and need extra computation to resolve, and many keys with the same hash slow down any hash table. A balanced tree map guarantees O(log n) for contains, get, put and remove, and in exchange keeps its keys sorted, returns a range of entries in O(log n), and finds the smallest and largest keys and the nearest key below or above a value. When the code needs a map with no extra functionality, the sorted map pays the logarithmic cost for an order the code never reads: a tree pays it on every operation, and a sorted map that stores its items in a hash table pays it on every insertion and removal. A collection implementation is a fixed choice of operation time, space use and synchronization, and using it in a manner inconsistent with that choice can cause significant performance degradation. A set is the map without values, and the same choice between the hashed and the ordered variant applies to it.

## Example
```python
bad:  index = SortedDict()
      for row in rows:
          index[row.key] = row
      found = index.get(wanted)
good: index = {}
      for row in rows:
          index[row.key] = row
      found = index.get(wanted)
```

## Limits
The ordered structure is correct where the code iterates in key order, takes a range, asks for the smallest or largest key or the nearest key below or above a value. It is correct where iteration order reaches output that must stay the same between runs and the hashed structure at hand guarantees no order, nor that its order stays constant over time, so that iterating it returns values in an undefined order. It is correct where the keys hash poorly, since many keys with the same hash slow down any hash table. It is correct where the ordered structure compares keys by a comparison of its own, such as a case-insensitive one, that treats as one key what the key's own equality and hash keep apart, since the ordered structure deems equal the keys its comparison deems equal. It is correct where code in other files can reach the structure, since the file does not show whether that code reads its key order. A structure shared between threads is replaced only by a hashed one with the same synchronization guarantee, since synchronization is part of the collection's fixed choice. The rule reaches the cost class of the two structures; whether the difference is measurable at the observed size is a profiling question outside it.

## Validator
Grep the hunk for the construction or declaration of an ordered map or set: a tree map or tree set, a B-tree map or set, a skip-list map or set, a sorted dictionary or sorted set. Open the file and list every use of that variable or field; a field or variable that code in other files can reach keeps the ordered structure, since its uses there are not listed. Count as a read of key order: iteration whose order can reach output, a returned sequence or a comparison; a range, head or tail view; first, last, smallest or largest key; floor, ceiling, lower, higher or any nearest-key search; passing or returning the structure through a type that promises sorted order. Count as by-key use: get, put, insert, contains, membership, remove, size, emptiness, and a pass whose result does not depend on order, such as a sum or a count. Check the key type and the comparison: a key without a hash function, one whose hash sends many keys to the same value, or an ordered structure built with a comparison of its own that treats as equal keys the key's own equality and hash keep apart keeps the ordered structure. Validator question: **Is the ordered map or set reachable only from this file, and is every use of it a lookup, insertion, removal, membership test or order-independent pass by key, with no read of its key order, no comparison of its own that treats as equal keys the key's equality keeps apart, and a key type that hashes well?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-21`, severity minor, `file`, `symbol`, `code` = the line that constructs or declares the ordered map or set, quoted verbatim from the diff, `fix` = the same declaration with the hashed map or set of the same interface and synchronization guarantee, in the file's language, `rationale` = names the by-key operations found that pay the sorted structure's logarithmic cost, against the expected constant cost of the hashed structure).

## Source
- Rust standard library, module `std::collections` documentation (rust-lang/rust master, library/std/src/collections/mod.rs): "Use a HashMap when: ... You want a map, with no extra functionality."; "Use a BTreeMap when: You want a map sorted by its keys. You want to be able to get a range of entries on-demand. You're interested in what the smallest or largest key-value pair is. You want to find the largest or smallest key that is smaller or larger than something."; "Use the Set variant of any of these Maps when: ... There is no meaningful value to associate with your keys."; cost table HashMap get O(1)~, insert O(1)~*, remove O(1)~, BTreeMap get, insert, remove and range O(log(n)); "Operations which have an amortized cost are suffixed with a *."; "Calling operations that add to a collection will occasionally require a collection to be resized - an extra operation that takes O(n) time."; "HashMap uses expected costs ... it is possible to generate a duplicate hash given some input key that will require extra computation to correct." (fetched)
- OpenJDK 21 `java.util.TreeMap` class documentation (openjdk/jdk jdk-21-ga): "A Red-Black tree based NavigableMap implementation ... guaranteed log(n) time cost for the containsKey, get, put and remove operations."; "a sorted map performs all key comparisons using its compareTo (or compare) method, so two keys that are deemed equal by this method are, from the standpoint of the sorted map, equal." (fetched)
- OpenJDK 21 `java.util.HashMap` class documentation (openjdk/jdk jdk-21-ga): "constant-time performance for the basic operations (get and put), assuming the hash function disperses the elements properly among the buckets"; "This class makes no guarantees as to the order of the map; in particular, it does not guarantee that the order will remain constant over time."; "using many keys with the same hashCode() is a sure way to slow down performance of any hash table." (fetched)
- OpenJDK 21 `java.util.concurrent.ConcurrentSkipListMap` class documentation (openjdk/jdk jdk-21-ga): "This class implements a concurrent variant of SkipLists providing expected average log(n) time cost for the containsKey, get, put and remove operations and their variants." (fetched)
- "Chameleon: Adaptive Selection of Collections", PLDI 2009, DOI 10.1145/1542476.1542522, abstract: "A collection implementation represents a fixed choice in the dimensions of operation time, space utilization, and synchronization. Using the collection in a manner not consistent with this fixed choice can cause significant performance degradation." (fetched)
- rust-clippy lint `ITER_OVER_HASH_TYPE` (restriction group): "Because hash types are unordered, when iterated through such as in a for loop, the values are returned in an undefined order." (fetched)
- Python `sortedcontainers` package, `SortedDict` class, `__setitem__` and `__delitem__` docstrings: "sorted dict inherits from dict to store items"; "Runtime complexity: O(log(n)) -- approximate." (fetched)
- Caveat: the research abstract concerns collection selection in general and reports a memory-footprint gain on a small set of benchmarks, not this substitution measured alone; the Example's sorted dictionary stores its items in a hash table, so its lookups are hashed, and pays an approximate logarithmic cost on insertion and removal.
