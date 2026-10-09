---
title: Sorting, binary search, priority queues and ordered maps over data whose size grows with the input use the standard library's implementations rather than hand-written ones
rule_id: PRF-16
domain: performance
step: [implement]
applies_to: [universal]
triggers: ['\b([bB]ubble|[iI]nsertion|[sS]election|[qQ]uick|[mM]erge|[hH]eap|[sS]hell)_?[sS]ort\w*\s*\(|\b(class|struct|interface)\s+\w*(Heap|PriorityQueue|BST|BinaryTree|SearchTree|SortedList)\b|\btype\s+\w*(Heap|Tree)\s+struct\b', '\bmid\w*\s*:?=\s*\(?\s*\w+\s*\+\s*\w+\s*\)?\s*(/{1,2}\s*2|>{2,3}\s*1)|\bmid\w*\s*:?=\s*\w+\s*\+\s*\(+\s*\w+\s*-\s*\w+\s*\)|\b(left|right|child)\w*\s*:?=\s*2\s*\*\s*\w+\s*\+\s*[12]|\(\s*\w+\s*-\s*1\s*\)\s*(/{1,2}\s*2|>{2,3}\s*1)', '\[?\s*\w+\[[^\]\n]+\]\s*,\s*\w+\[[^\]\n]+\]\s*\]?\s*=\s*\[?\s*\w+\[[^\]\n]+\]\s*,\s*\w+\[[^\]\n]+\]|\b(tmp|temp)\s*:?=\s*\w+\[']
scope: file
check_kind: semantic
severity_default: major
---

# Sorting, binary search, priority queues and ordered maps over data whose size grows with the input use the standard library's implementations rather than hand-written ones

## Thesis
Where the data grows with the input, sorting it, binary-searching it, keeping it in priority order and keeping it as an ordered map are calls to the standard library's sort, binary search, heap and ordered tree map wherever the standard library provides the operation.

## Rationale
Several standard libraries document a cost class for these operations. Their sorts state O(n log(n)) performance on all data sets, O(n log(n)) in the worst case, or O(n log(n)) comparisons and swaps. One library's binary search runs in log(n) time on a random-access sorted sequence, and on a large sequence without near-constant-time positional access it performs O(n) link traversals. Insertion into a binary heap and removal of its top element are O(log(n)). An ordered tree map gives guaranteed log(n) time for lookup, insertion and removal. One library's cost table lists an array at O(n-i) for inserting or removing the element at position i, so priority order kept in a sorted array pays up to linear time per insertion where the binary heap pays O(log(n)). The same library's ordered-map documentation adds that a perfectly balanced binary search tree performs the theoretical minimum number of comparisons, yet storing every element in its own heap-allocated node makes every insertion allocate and every comparison a potential cache miss, which that library avoids by packing many elements into each node's contiguous array. A hand-written insertion sort stays quadratic in the expected and worst cases, and finding each position by binary search leaves its quadratic data movement unchanged; in one library's tests on random data that data-movement cost clearly hurt on runs of 256 elements, while below 64 elements the same library sorts the whole array by binary insertion sort, which is hard to beat given the overheads of anything fancier. A library binary search over a sequence that is not sorted, or with a comparator inconsistent with the sort order, returns a result one library calls undefined and another unspecified and meaningless, so the sort and the search share one ordering. Verification and maintenance work target the library implementation: formal verification of one standard library's main sort found a bug that crashes it and derived a bug-free version that does not compromise the performance, another library rewrote its sort to use pattern-defeating quicksort, faster for several common scenarios, and one library's documentation offered its binary search source as a working example whose boundary conditions are already right.

## Example
```python
bad:  def insertion_sort(items):
          for i in range(1, len(items)):
              lo, hi = 0, i
              while lo < hi:
                  mid = (lo + hi) // 2
                  if items[mid] > items[i]: hi = mid
                  else: lo = mid + 1
              for j in range(i, lo, -1):
                  items[j - 1], items[j] = items[j], items[j - 1]
good: items.sort()
```

## Limits
Data the domain bounds below 64 elements, the size under which one library's sort itself runs binary insertion sort over the whole array, falls outside the rule. Where equal elements must keep their order, the call is the library's stable sort, which keeps the original order of equal elements, since an unstable library sort may reorder them. A call to the library's binary search still needs a random-access sequence sorted by the same ordering it searches with, and the rule does not check that call's input. A platform whose standard library lacks the operation, a teaching exercise that implements the algorithm on purpose, and a specialised structure outside the standard library also fall outside it. The rule stops at the choice of implementation: whether the operation's cost matters at the observed size is a question for measurement, and novel algorithms, probabilistic or cache-oblivious structures and low-latency tuning lie beyond it.

## Validator
Grep the hunk for a routine named after a sort, a type named after a heap or a search tree, a midpoint computed from two indices, a heap's child or parent index computed from a position, or an element swap through a temporary or a tuple. Open the file and read the routine: decide which operation it implements (sort, binary search, priority queue or ordered map), and trace where its data comes from, a request, a file, a query result or another collection sized by the input, as against a fixed set the domain bounds below 64 elements. Check that the standard library of the file's language provides the operation and that the file is not a teaching exercise or a specialised structure the library lacks. Validator question: **Does the file hand-write a sort, binary search, priority queue or ordered search tree over data whose size grows with the input, where the language's standard library provides that operation?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-16`, severity major, `file`, `symbol`, `code` = the hand-written routine's signature and its inner loop, midpoint or child-index line, `fix` = the call to the standard library's sort, binary search, heap or ordered map that replaces the routine, in the file's language, `rationale` = the operation, the hand-written routine's cost class against the library's documented one, and the input that sizes the data).

## Source
- OpenJDK 21 `java.util.Arrays.sort(int[])` @implNote, openjdk/jdk tag jdk-21-ga (fetched): "This algorithm offers O(n log(n)) performance on all data sets".
- OpenJDK 21 `java.util.Collections.binarySearch` (fetched): "If it is not sorted, the results are undefined." / "This method runs in log(n) time for a "random access" list ... performs O(n) link traversals and O(log n) element comparisons."
- OpenJDK 21 `java.util.PriorityQueue` implementation note (fetched): "O(log(n)) time for the enqueuing and dequeuing methods"; `java.util.TreeMap` class comment (fetched): "guaranteed log(n) time cost for the containsKey, get, put and remove operations."
- Rust `slice::sort_unstable` and `slice::binary_search_by`, rust-lang/rust master library/core/src/slice/mod.rs (fetched): "unstable (i.e., may reorder equal elements), in-place (i.e., does not allocate), and O(n * log(n)) worst-case" / "If the slice is not sorted or if the comparator function does not implement an order consistent with the sort order of the underlying slice, the returned result is unspecified and meaningless."
- Rust `collections::binary_heap` module doc and std `collections` cost table (fetched): "Insertion and popping the largest element have O(log(n)) time complexity." / BTreeMap get(i), insert(i), remove(i): "O(log(n))"; Vec insert(i) (amortized), remove(i): "O(n-i)".
- Rust `collections::btree::map` module doc, rust-lang/rust master library/alloc/src/collections/btree/map.rs (fetched): "a perfectly balanced BST performs the theoretical minimum number of comparisons necessary to find an element ... However, in practice the way this is done is very inefficient for modern computer architectures. In particular, every element is stored in its own individually heap-allocated node. This means that every single insertion triggers a heap-allocation, and every comparison is a potential cache-miss due to the indirection." / "A B-Tree instead makes each node contain B-1 to 2B-1 elements in a contiguous array."
- Go `sort.Sort`, `slices.BinarySearch`, `container/heap.Push`, golang/go master (fetched): "O(n*log(n)) calls to data.Less and data.Swap. The sort is not guaranteed to be stable." / `sort.Stable`: "keeping the original order of equal elements" / "The slice must be sorted in increasing order." / "The complexity is O(log n) where n = h.Len()."
- CPython Objects/listsort.txt with Objects/listobject.c, python/cpython main (fetched): "insertion sort remains quadratic (expected and worst cases) either way. Speeding the search doesn't reduce the quadratic data movement costs." / "If N < MAX_MINRUN, minrun is N. IOW, binary insertion sort is used for the whole array then; it's hard to beat that given the overheads of trying something fancier" / "#define MAX_MINRUN 64" / "testing on random data ... At 256 the data-movement cost in binary insertion sort clearly hurt".
- CPython 3.9 Doc/library/bisect.rst (fetched): "The source code may be most useful as a working example of the algorithm (the boundary conditions are already right!)."
- Go 1.19 release notes, golang/website _content/doc/go1.19.md (fetched): "The sorting algorithm has been rewritten to use pattern-defeating quicksort ... which is faster for several common scenarios."
- DOI 10.1007/978-3-319-21690-4_16 (CAV 2015), abstract (fetched): "the main sorting algorithm provided by the Java standard library ... we discovered a bug which causes the implementation to crash ... we derive a bug-free version that does not compromise the performance."
- Caveat: the cost classes are each library's documented contract; the evidence carries no measured comparison of library and hand-written routines in application code.
