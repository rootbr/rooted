---
title: The minimum, the maximum or the few smallest or largest elements of a collection are taken with a linear scan or a bounded heap, not by sorting the whole collection and discarding the rest
rule_id: PRF-24
domain: performance
step: [implement]
applies_to: [universal]
triggers: ['\bsorted\(|[.](sort\w*|toSorted)\(|\bsort[.]\w+\(|\bslices[.]Sort\w*\(']
scope: file
check_kind: semantic
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
