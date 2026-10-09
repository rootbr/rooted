---
title: The minimum, the maximum or the few smallest or largest elements of a collection are taken with a linear scan or a bounded heap, not by sorting the whole collection and discarding the rest
rule_id: PRF-24
domain: performance
step: [implement, review]
applies_to: [universal]
triggers: ['\bsorted\(|[.](sort\w*|toSorted)\(|\bsort[.]\w+\(|\bslices[.]Sort\w*\(']
scope: file
check_kind: mechanical
severity_default: minor
---

# The minimum, the maximum or the few smallest or largest elements of a collection are taken with a linear scan or a bounded heap, not by sorting the whole collection and discarding the rest

## Thesis
The minimum or the maximum of a collection is taken with one linear pass, and a small number k of its smallest or largest elements with a selection that keeps at most k elements in a heap, not by sorting the whole collection and reading only its first or last elements; for larger k, a full sort is the more efficient choice.

## Rationale
Taking the minimum or the maximum costs O(n): the operation iterates over the entire collection, in time proportional to its size, while sorting the collection costs O(n log n). Heap-based selection makes a single pass over the data while keeping the k most extreme values in a heap, so its memory is limited to k values. On random inputs with k = 100, one standard library's implementation of that selection measured 0.8% more comparisons than a plain minimum at 1,000,000 inputs and 231.7% more at 1,000 inputs. Heap-based selection performs best for smaller k; for larger k sorting is more efficient, and for k = 1 the minimum and maximum operations are more efficient than the selection. Against a sort that costs O(n log n) in the worst case, the scan costs O(n) and the selection of the k smallest or largest at most O(n log k), its worst case being input in reverse order, where every element enters the heap.

## Example
```rust
bad:  v.sort();
      let lowest = v[0];
good: let lowest = v.iter().min();
```

## Limits
The rule covers a sort whose result is read only for its minimum or maximum, or for its first or last k elements; a sort whose order the code goes on to use beyond the elements read is outside it. For larger k, sorting is more efficient than heap-based selection. Where the standard library has no heap or priority queue, a read of the first or last k elements is outside the rule. A heap holds its elements in no particular order, so where the code uses the order of the k elements, the fix returns them sorted, through a selection function that ends with that sort or by sorting the k elements after the selection. An in-place sort of a parameter, a field, or a value the code returns or passes on leaves a sorted collection that other code can read, and so does an in-place sort of a local that a later line of the function reads in order; both are outside the rule. The replacement can change behaviour: where several elements tie, the scan can return a different one of them than the sorted read did, and on an empty collection the replacement can raise a different error than the sorted read, or none at all, so code that handles the error the sorted read raises on an empty collection is updated with the fix.

## Validator
Grep the hunk for a sort call: a sorted copy, an in-place sort, a stream or array sort, a library sort routine. Open the hunk and, for an in-place sort, the enclosing function in the file, and trace every read of the sorted result after the call: a read of index zero or of the last index, a first or last accessor, a prefix or suffix slice, a take or limit. Check whether any later line iterates, searches, returns or outputs the sorted collection in order beyond the elements read; for an in-place sort, check whether the collection is a parameter, a field, or a value the enclosing function returns or passes on, and whether a later line of that function, inside or outside the hunk, reads it in order beyond the elements read; for a prefix or suffix, check whether the standard library of the file's language has a heap or priority queue, whether the length is a literal constant and, where the hunk shows the collection's size, whether the constant approaches that size. Validator question: **Does the hunk sort a whole collection and then read only its first or last element, or, where the standard library of the file's language has a heap or priority queue, only a prefix or suffix of literal constant length that the hunk does not show to approach the collection's size, with no use of the sorted order beyond the elements read and no in-place sort of a parameter, a field, a value the enclosing function returns or passes on, or a collection that a later line of that function reads in order?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-24`, severity minor, `file`, `symbol`, `code` = the sort call and the line that reads its first or last elements, quoted verbatim from the diff, `fix` = the same read written as one pass over the collection under the sort's own ordering (its key, its comparator or default comparison, and its direction), through a standard-library minimum or maximum that takes the collection itself or else a loop or reduction over it, or, for k elements, as the standard library's selection function or a heap of at most k elements built on its heap or priority queue, in the file's language, `rationale` = names the O(n) scan or single heap pass against the O(n log n) sort, and the tie-breaking and empty-collection behaviour to re-check).

## Source
- Python documentation, time complexity of built-in types (python/cpython main, `Doc/builtins/time-complexity.rst`), list table: "Sort (``l.sort()``) ... *O*\ (*n* log *n*)"; "``min(l)``, ``max(l)`` - *O*\ (*n*)"; footnote [4] to the sort row: "This is the worst case scenario. Sorting is adaptive and input that is already sorted or reverse-sorted takes only *O*\ (*n*) comparisons." (fetched)
- OpenJDK 21 Javadoc, `java.util.Collections.min(Collection)` (openjdk/jdk tag jdk-21-ga, `Collections.java`): "This method iterates over the entire collection, hence it requires time proportional to the size of the collection." (fetched)
- Python documentation, heapq module (python/cpython main, `Doc/library/heapq.rst`), `nsmallest`: "Equivalent to: ``sorted(iterable, key=key)[:n]``."; after it: "The latter two functions perform best for smaller values of *n*. For larger values, it is more efficient to use the :func:`sorted` function. Also, when ``n==1``, it is more efficient to use the built-in :func:`min` and :func:`max` functions." (fetched)
- CPython `Lib/heapq.py` (python/cpython main), "Algorithm notes for nlargest() and nsmallest()": "Make a single pass over the data while keeping the k most extreme values in a heap. Memory consumption is limited to keeping k values in a list."; measured for random inputs, k-extreme values 100, "% more than min()": "1,000,000 ... 0.8%", "1,000 ... 231.7%"; step 4 "final sort of the k most extreme values"; "In the worst case, the input data is reversed sorted so that every new element must be inserted in the heap: comparisons = 1.66 * k + log(k, 2) * (n - k)" (fetched)
- OpenJDK 21 Javadoc, `java.util.PriorityQueue` (openjdk/jdk tag jdk-21-ga, `PriorityQueue.java`), class documentation: "The Iterator provided in method iterator() and the Spliterator provided in method spliterator() are not guaranteed to traverse the elements of the priority queue in any particular order. If you need ordered traversal, consider using Arrays.sort(pq.toArray())." (fetched)
- Ruff rule FURB192 sorted-min-max (astral-sh/ruff main, `crates/ruff_linter/src/rules/refurb/rules/sorted_min_max.rs`): "Checks for uses of `sorted()` to retrieve the minimum or maximum value in a sequence."; "Using `sorted()` to compute the minimum or maximum value in a sequence is inefficient and less readable than using `min()` or `max()` directly."; "migrating to `min` or `max` can lead to a change in behavior, notably when breaking ties"; "The fix also changes which exception is raised for an empty sequence"; "Code that catches one specific exception type will need to be updated after the fix is applied." (fetched)
- Caveat: the costs are the documented costs of two standard libraries and one library's comparison counts on random inputs; no source gives the k at which a sort overtakes heap-based selection as a number.
