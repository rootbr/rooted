---
title: Matching the elements of two collections that grow with the input builds a hashed index of one collection in a single pass, instead of comparing every pair in nested loops
rule_id: PRF-23
domain: performance
step: [implement, refactor]
applies_to: [universal]
triggers: ['signal:deep_nesting', '\b\w+[.](\w+)(\(\))?\s*(===?|!==?|[.]equals\(|[.]eq\()\s*\w+[.]\1\b']
scope: file
check_kind: semantic
severity_default: major
---

# Matching the elements of two collections that grow with the input builds a hashed index of one collection in a single pass, instead of comparing every pair in nested loops

## Thesis
When code matches the elements of two collections that both grow with the input on equality of a hashable key, it builds a hashed map or set of one collection, keyed by the matched field, in a single pass and probes it from one loop over the other, which costs O(n + m) on average, plus one step for each matching pair a join emits, instead of the O(n·m) of walking the second collection for every element of the first.

## Rationale
A membership test or search in an unindexed sequence walks it and costs O(n) in its length, so a loop over the n elements of one collection that searches the m elements of a second for an equal key costs O(n·m), reading the same second collection again on every outer iteration. The shape covers a join, an intersection, a difference, a deduplication and a grouping, each a search for elements with an equal key. In a hashed set or map, membership, insertion and lookup by key cost O(1) on average, so one pass that indexes the m elements and one loop that probes the index n times cost O(n + m), plus one step for each matching pair that a join emits, a count that is at most n·m and reaches it only when every element shares one key; a documented hashed difference against a collection that is not yet a set likewise costs time linear in the sum of the two sizes. One language specification leaves the exact bound open and requires only that its maps and sets provide, on average, access times sublinear in the number of elements, which still keeps the probing loop below O(n·m). The average assumes a hash function that disperses keys so that collisions are uncommon and a key that hashes and compares in O(1); when every key hashes to the same value, each O(1) operation takes O(n). Redundant traversal bugs in collection traversals are a prevalent class of asymptotic performance bugs: a static analysis of 1.6M lines of code found 92 instances, 72 never previously reported, with 5 false positives, and at an input size of 50,000 every program repaired by hand ran at least 2.45 times faster than the original. Loops whose iterations repeat partially similar memory-access patterns do repetitive work that is likely unnecessary and can be done faster; an oracle reporting such loops found 42 new bugs in six projects, of which developers fixed 10 and confirmed 6 more. Loops that produce a result only in their last iteration are often searches that check a sequence one element at a time until the right one is found, and they are often fixed by a data-structure change: in one browser, large inputs filled a list with tens of thousands of nodes and caused poor performance, and the patch replaced the list with a hash table.

## Example
```go
bad:  for _, l := range left {
          for _, r := range right {
              if l.Key == r.Key { out = append(out, l); break }
          }
      }
good: keys := make(map[string]struct{}, len(right))
      for _, r := range right { keys[r.Key] = struct{}{} }
      for _, l := range left {
          if _, ok := keys[l.Key]; ok { out = append(out, l) }
      }
```

## Limits
Whether a search loop is efficient depends on the workload: when either collection is bounded by the domain to a handful of elements, the nested loop is already linear in the other, and the rule does not apply. The documented average-case operations of a hashed map or set are membership, insertion and lookup of a key, so a match on a range, an ordering or a similarity comparison lies outside the rule. A key whose hash does not disperse its values, or whose hashing or comparison is not constant-time, does not get the average-case bound.

## Validator
Grep the hunk for a loop nested inside another loop, for an equality comparison whose two sides read the same field or key from elements of two collections, and for a membership test or linear search of a collection inside a loop. Open the file and name both collections; trace where each comes from to decide whether both grow with the input (request payloads, query results, file contents, stored records) or whether either is bounded by the domain to a handful (the values of an enumeration, a fixed configuration list). Confirm that the match is equality on a hashable key rather than a range, an ordering or a similarity comparison, and that neither collection is already a hashed map or set probed by key. Validator question: **Does a loop over one collection that grows with the input walk a second collection that grows with the input to find elements with an equal hashable key, with no hashed index built for the match?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-23`, severity major, `file`, `symbol`, `code` = the outer loop header, the inner loop or linear search and the key comparison, quoted verbatim from the diff, `fix` = a hashed map or set built from one collection in a single pass keyed by the matched field, mapping each key to the list of its elements when keys repeat, and one loop over the other collection that probes it, in the file's language, `rationale` = the two collections, why both grow with the input, and the change from O(n·m) to O(n + m) average-case cost plus the matched pairs emitted).
