---
title: A loop that adds elements one at a time and needs them in order sorts once after the loop or keeps them in a heap or ordered tree, instead of re-sorting, inserting into a sorted array or scanning for the extreme on every iteration
rule_id: PRF-18
domain: performance
step: [implement]
applies_to: [universal]
triggers: ['[.]sort\(|\bsorted\(|[.]sort_\w+\(|\b(Arrays|Collections)[.]sort\(|[.]toSorted\(', '\bsort[.](Slice|SliceStable|Sort|Stable|Strings|Ints|Float64s)\(|\bslices[.]Sort\w*\(', '\binsort\w*\(|\bbisect\w*\(|\bbinarySearch\(|[.]binary_search\w*\(|[.]partition_point\(|\bslices[.]BinarySearch\w*\(|\bsort[.]Search\w*\(|[.]splice\(.*,\s*0\s*,', '\b(min|max)\(|[.](min|max)\(|\bslices[.](Min|Max)\w*\(']
scope: file
check_kind: semantic
severity_default: minor
---

# A loop that adds elements one at a time and needs them in order sorts once after the loop or keeps them in a heap or ordered tree, instead of re-sorting, inserting into a sorted array or scanning for the extreme on every iteration

## Thesis
When a loop adds elements to a collection one at a time and the collection grows with the input, the loop gets its order from one sort after the loop if it reads the order only at the end, from a binary heap if each iteration needs only the smallest or largest element, or from a balanced ordered tree if each iteration needs the elements in key order or a range of them, so each addition costs O(log n) or less instead of the O(n) or more that re-sorting, sorted-array insertion or a minimum or maximum scan costs on every iteration.

## Rationale
A library sort costs O(n log n) in the worst case, and even an adaptive sort spends O(n) comparisons on input that is already sorted, so re-sorting after each of n additions costs at least O(n) per pass and at least O(n²) over the loop. Inserting into a sorted array costs O(n) per insertion, because the logarithmic search step is dominated by the linear time insertion step, so n insertions cost O(n²). Scanning for the minimum or maximum costs O(n) per scan, and one scan per iteration costs O(n²) over the loop. Sorting once after the loop costs O(n log n). A binary heap pushes an element and pops its minimum in O(log n) each and builds itself from n collected elements in O(n); it fits a loop that only ever processes the biggest or most important element at any given time. A balanced ordered tree keeps its keys sorted, inserts in guaranteed O(log n), and reports the smallest or largest key and a range of entries on demand. Either structure brings n additions to O(n log n), the class of a single sort.

## Example
```go
bad:  for _, x := range xs {
          out = append(out, x)
          slices.Sort(out)
      }
good: for _, x := range xs {
          out = append(out, x)
      }
      slices.Sort(out)
```

## Limits
A sort placed after the loop, for an order read only at the end, is the form the rule asks for and is not a finding. A collection the domain bounds to a handful of elements is outside the rule: its per-pass cost does not grow with the input, and the documented gain of sorted insertion over frequent re-sorting is stated for long lists of items with expensive comparison operations. Sorted insertion that finds its position by binary search can be an improvement over frequent re-sorting, yet each insertion still costs O(n) because of the linear insertion step, so it stays a finding when the collection grows with the input. A heap gives only its smallest or largest element cheaply; a loop that needs key order or a range of entries on each iteration takes the ordered tree.


Where the code after the loop reads only the smallest or largest element, or the first or last few, of what the loop collected, one scan or a bounded heap replaces the sort after the loop.
## Validator
Grep the hunk for a sort call, a sorted-insertion or binary-search call, and a minimum or maximum call. For each hit, open the file and find the innermost enclosing loop; check whether the same loop adds elements to the collection that the call sorts, inserts into or scans. Trace where the added elements come from: a loop over an input, a request stream or a growing work list makes the collection grow with the input, while a literal, a fixed set of cases or a constant bound keeps it to a handful. A sort placed after the loop is the cheap form and is not a hit. Validator question: **Does a loop whose collection grows with the input add elements to it one at a time and, on every iteration, re-sort it, insert into it as a sorted array, or scan it for its minimum or maximum?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-18`, severity minor, `file`, `symbol`, `code` = the loop header and the per-iteration sort, sorted insertion or minimum or maximum scan, quoted verbatim from the diff, `fix` = the sort moved after the loop, or the collection replaced by a binary heap or ordered tree, the standard library's where the language has one, in the file's language, `rationale` = the per-iteration cost class of the flagged step against O(n log n) for one sort or O(log n) per heap or tree operation, and the input that makes the collection grow).

## Source
- Python documentation, `bisect` module, introduction and Performance Notes, python/cpython main Doc/library/bisect.rst (fetched): "This module provides support for maintaining a list in sorted order without having to sort the list after each insertion. For long lists of items with expensive comparison operations, this can be an improvement over linear searches or frequent resorting." · "The insort() functions are O(n) because the logarithmic search step is dominated by the linear time insertion step."
- Python documentation, Time complexity of operations on built-in types, list table and note [4], python/cpython main Doc/builtins/time-complexity.rst (fetched): "Sort (l.sort()) [4] — O(n log n)" · "min(l), max(l) — O(n)" · "[4] This is the worst case scenario. Sorting is adaptive and input that is already sorted or reverse-sorted takes only O(n) comparisons."
- Python documentation, `heapq` module, paragraph after nsmallest, python/cpython main Doc/library/heapq.rst (fetched): "Also, when n==1, it is more efficient to use the built-in min() and max() functions. If repeated usage of these functions is required, consider turning the iterable into an actual heap."
- Go standard library, package container/heap, Init, Push and Pop, golang/go master src/container/heap/heap.go (fetched): "The complexity is O(n) where n = h.Len()." · "Push pushes the element x onto the heap. The complexity is O(log n) where n = h.Len()." · "Pop removes and returns the minimum element (according to Less) from the heap. The complexity is O(log n) where n = h.Len()."
- Go standard library, package sort, Sort, golang/go master src/sort/sort.go (fetched): "It makes one call to data.Len to determine n and O(n*log(n)) calls to data.Less and data.Swap."
- OpenJDK 21, java.util.PriorityQueue class comment, openjdk/jdk jdk-21-ga (fetched): "this implementation provides O(log(n)) time for the enqueuing and dequeuing methods (offer, poll, remove() and add)"
- OpenJDK 21, java.util.TreeMap class comment, openjdk/jdk jdk-21-ga (fetched): "A Red-Black tree based NavigableMap implementation. The map is sorted according to the natural ordering of its keys ... This implementation provides guaranteed log(n) time cost for the containsKey, get, put and remove operations."
- Rust standard library, module std::collections, "Use a BTreeMap when", "Use a BinaryHeap when" and "Cost of Collection Operations", rust-lang/rust master library/std/src/collections/mod.rs (fetched): "You want a map sorted by its keys. You want to be able to get a range of entries on-demand. You're interested in what the smallest or largest key-value pair is." · "You want to store a bunch of elements, but only ever want to process the "biggest" or "most important" one at any given time. You want a priority queue." · cost table, insert(i): Vec "O(n-i)*", BTreeMap "O(log(n))".
- Python documentation, heapq module (python/cpython main, `Doc/library/heapq.rst`), `nsmallest`: "Equivalent to: ``sorted(iterable, key=key)[:n]``."; after it: "The latter two functions perform best for smaller values of *n*. For larger values, it is more efficient to use the :func:`sorted` function. Also, when ``n==1``, it is more efficient to use the built-in :func:`min` and :func:`max` functions." (fetched)
- Caveat: the libraries document per-operation costs; the whole-loop totals are those costs multiplied by the loop's n additions.
