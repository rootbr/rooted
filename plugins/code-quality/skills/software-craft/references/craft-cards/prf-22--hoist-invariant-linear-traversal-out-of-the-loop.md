---
title: A linear traversal whose result does not change between iterations runs once before the loop, not in the loop condition or once per iteration
rule_id: PRF-22
domain: performance
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['\bfor\s*\([^;]*;[^;]*\w\([^;]*;', '\bfor\s+[^;{(]*;[^;{]*\w\([^;{]*;', '\bObject[.](keys|values|entries)\([^)]*\)[.]length\b', '\b(sum|max|min|sorted|len\(\s*set)\(\s*\w+\s*\)|[.]stream\(\).*[.](count|max|min|sum)\(|[.]iter\(\).*[.](count|max|min|sum)\(', '\bwhile\b[^;{]*\w\(|\bfor\s+[^;{(=]*[<>][^;{]*\w\(', '[.](filter|reduce)\(|\bMath[.](max|min)\([.]{3}']
scope: file
check_kind: semantic
severity_default: major
---

# A linear traversal whose result does not change between iterations runs once before the loop, not in the loop condition or once per iteration

## Thesis
A call that traverses a whole collection or string (counting, summing, taking a minimum or maximum, collecting keys, or reading a size that is O(n) for its type), and whose input nothing changes while the loop runs, is computed once before the loop, so that a loop over n elements costs O(n), where repeating that traversal in the loop condition or on every iteration costs O(n^2).

## Rationale
A call in a loop condition or body runs on every iteration; when the data it traverses does not change, each iteration repeats what an earlier iteration already did, and n iterations of an O(n) traversal do O(n^2) work, while the loop reads as linear because the time complexity of a call on a collection is not always obvious from the call. Taking the minimum or maximum of a list and iterating a string or a map are O(n). Reading a size takes constant time for most collections, and where the element count is stored in the object, reading it need not count; for some collections, a concurrent linked queue among them, the size call is O(n), directly proportional to the number of elements. Loops whose iterations repeat similar memory-access patterns do work that is likely unnecessary and can be done faster; an oracle that reports such loops found 42 new bugs in six projects, of which developers fixed 10 and confirmed 6 more. Redundant traversals of collections form a prevalent class of asymptotic performance bugs: a static analysis found 92 instances in 1.6M lines of code, 72 of them new, with 5 false positives, and at an input size of 50,000 every repaired program ran at least 2.45 times faster than its original code. Memoization, which caches the earlier computation's result, and batching, which combines several iterations' work, are the typical fixes.

## Example
```typescript
bad:  for (let i = 0; i < Object.keys(registry).length; i++) {
        report(Object.keys(registry)[i], i);
      }
good: const keys = Object.keys(registry);
      for (let i = 0; i < keys.length; i++) {
        report(keys[i], i);
      }
```

## Limits
A size or length that its type stores, so that reading it counts nothing and costs O(1), as for most collections, stays in the loop condition. A collection that the loop, a function the loop calls or another thread adds to, removes from or reassigns while the loop runs can yield a different result on each iteration, so its traversal cannot be computed once before the loop, and that loop falls outside the rule. The cost of a traversal is proportional to the number of elements and can be expensive when the collection is large, so a collection the domain bounds to a handful of elements is outside the rule. A loop whose iteration count is fixed or bounded by the domain, such as one pass per output format, repeats the traversal a constant number of times, so its total stays linear and hoisting it is code tuning, outside this rule. Hoisting invariant work whose cost does not grow with the input is code tuning, and measuring whether a given loop matters is profiling; both are outside this rule.

## Validator
Grep the hunk for a loop header or loop body that calls something taking a whole collection or string as argument or receiver: a key, value or entry listing followed by its length; a sum, minimum, maximum, count, sort or set conversion of a collection; a stream or iterator pipeline ending in a count, sum, minimum or maximum; a helper that counts or filters its argument; or a size call on a linked or concurrent collection. Open the file and confirm the callee walks its whole input, by reading the helper's body or the type's documented cost, and that it is not a stored length read in O(1). Trace the traversed collection through the loop: confirm nothing adds to, removes from or reassigns it while the loop runs, whether a statement in the loop, a function the loop calls or another thread that shares it, and that the domain does not bound it to a handful of elements, such as a fixed enumeration or a short configuration list. Confirm the loop runs a number of times that grows with the input, such as once per element of this or another collection; a loop with a fixed or domain-bounded iteration count repeats the traversal a constant number of times and stays linear. Validator question: **Does a loop whose iteration count grows with the input call, in its condition or body, an O(n) traversal of a collection or string that nothing modifies while the loop runs, so that every iteration recomputes the same result?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-22`, severity major, `file`, `symbol`, `code` = the loop header or body line holding the traversing call, quoted verbatim from the diff, `fix` = the traversal assigned to a local before the loop, with the loop reading that local, in the file's language, `rationale` = the traversal's O(n) cost, that nothing changes the traversed collection while the loop runs, and the resulting O(n^2) total).

## Source
- Performance Diagnosis for Inefficient Loops, ICSE 2017, DOI 10.1109/ICSE.2017.41, §"Redundant loops" (fetched): "Cross-iteration Redundancy: one iteration repeats what was already done by an earlier iteration of the same loop"; "memoization and batching are the typical fix strategies"; "either caching the earlier computation results and skip some following iterations; or combining multiple iterations' work together".
- Toddler: Detecting Performance Problems via Similar Memory-Access Patterns, ICSE 2013, abstract, https://raw.githubusercontent.com/rtholmes/conf-data/master/data/2013ICSE.json (fetched): "code loops whose computation has repetitive and partially similar memory-access patterns across loop iterations. Such repetitive work is likely unnecessary and can be done faster ... we also found 42 new bugs in six Java projects ... developers so far fixed 10 bugs and confirmed 6 more as real bugs."
- Static Detection of Asymptotic Performance Bugs in Collection Traversals, PLDI 2015, DOI 10.1145/2737924.2737966, abstract (fetched): "a prevalent class of asymptotic performance bugs called redundant traversal bugs ... Across 1.6M lines of Java code, CLARITY finds 92 instances of redundant traversal bugs, including 72 that have never been previously reported, with just 5 false positives ... for an input size of 50,000, all repaired programs are at least 2.45 faster than their original code."
- SonarSource RSPEC S2250 "Collection methods with O(n) performance should be used carefully", "Why is this an issue?" (fetched): "The time complexity of method calls on collections is not always obvious. For instance, for most collections the size() method takes constant time, but the time required to execute ConcurrentLinkedQueue.size() is O(n) ... When the collection is large, this could therefore be an expensive operation."
- CPython documentation, "Time complexity of operations on built-in types" (fetched): list "min(l), max(l) — O(n)"; str and dict "Iteration — O(n)"; "Get length (len(l)) — O(1)"; note 5: "The number of elements is stored in the object, so len() does not need to count them."
- Caveat: the bug counts come from Java codebases, and the quoted abstract names redundant traversal bugs without defining them, so the card reads that class through the loop study's repeated-work definition.
