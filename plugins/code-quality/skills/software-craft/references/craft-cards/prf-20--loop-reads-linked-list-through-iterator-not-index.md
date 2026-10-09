---
title: A loop does not read a linked list or other sequential-access sequence by index or binary-search it, because every positional access walks the nodes, which makes an indexed pass quadratic and each binary search at least linear
rule_id: PRF-20
domain: performance
step: [design, implement, review]
applies_to: [universal]
triggers: ['\bLinkedList\b|\bcontainer/list\b|\blist[.]New\(\)|\bdeque\(', '[.]get\(\s*\w+\s*\)|[.]nth\(\s*\w+\s*\)|\bbinarySearch\(|\bbisect\w*\(']
scope: file
check_kind: semantic
severity_default: major
---

# A loop does not read a linked list or other sequential-access sequence by index or binary-search it, because every positional access walks the nodes, which makes an indexed pass quadratic and each binary search at least linear

## Thesis
A loop over a linked list, or over a sequence whose indexed access is documented as O(1) at the ends but O(n) in the middle, reads the elements through the sequence's iterator or from an array-backed copy with O(1) indexed access, and a binary search repeated on each iteration of a loop runs only over a sequence with near-constant-time positional access. On a linked list each access by index walks from the nearer end at O(min(i, n − i)), so a pass that reads every position by index produces quadratic behaviour, and a binary search over a large one pays at least a linear walk per search for its O(log n) element comparisons: O(n) link traversals when it steps through an iterator, up to O(n log n) when it indexes the midpoint on every probe. The rule holds for a large sequence; access at either end and a sequence the domain bounds to a few elements are outside it.

## Rationale
A linked list reaches position i by traversing from the beginning or the end, whichever is closer, so an indexed read costs O(min(i, n − i)) where an array-backed vector answers in O(1). Algorithms written for random-access lists can produce quadratic behaviour when applied to sequential-access lists, and the loop that calls `get(i)` for every i below n is the documented test between the two kinds: a list should declare itself random-access when that loop runs faster than the loop over its iterator. Some double-ended queues give O(1) indexed access at both ends but O(n) in the middle, and their documentation directs fast random access to the plain list instead. A binary search runs in log(n) time on a list with near-constant-time positional access; on a large sequential-access list even an iterator-based search performs O(n) link traversals for its O(log n) element comparisons, and a search that indexes the midpoint walks up to n/2 nodes on every probe, so a loop that searches such a list on each iteration pays at least a linear walk per search. Iteration is the path the library itself takes on such a list: its default sort obtains an array of all the elements, sorts the array and iterates over the list resetting each element, which avoids the n² log(n) of sorting a linked list in place. Static analysis flags a positional get on a linked-list field as an O(n) call, which could be expensive when the collection is large.

## Example
```java
bad:  List<Item> items = new LinkedList<>(source);
      for (int i = 0; i < items.size(); i++) {
          process(items.get(i));
      }
good: List<Item> items = new LinkedList<>(source);
      for (Item item : items) {
          process(item);
      }
```

## Limits
Access at either end costs O(1) on a linked list and on the double-ended queue alike and is outside the rule, and a single positional access outside a loop costs one O(min(i, n − i)) walk and is outside it too. A sequence the domain bounds to a few elements is outside the rule: the cost is a concern when the collection is large. A sequence documented as asymptotically linear in access time only when huge, and constant-time in practice, should generally be treated as random-access. Whether a linked list suits the workload at all, and whether the pass is hot enough to measure, lie outside this rule.

## Validator
Grep the hunk for a linked-list or double-ended-queue type or constructor, an indexed read `.get(<var>)` or `.nth(<var>)`, a subscript by a loop variable, and a binary-search call. Open the file and trace the receiver of each indexed read or search to its declared or constructed type; keep it when that type is a linked list or a sequence whose indexed access is documented as O(n) away from its ends. Check that the read sits inside a loop whose index varies across the sequence — a counted loop up to the size, or a hand-written binary search that reads the midpoint — or that the binary-search call runs on each iteration of an enclosing loop, and that the index is neither the first nor the last position. Drop the case when the sequence is bounded by construction to a few elements. Validator question: **Does a loop read a linked list or another sequence with O(n) indexed access away from its ends by a varying index, or binary-search such a sequence on each iteration, where the sequence is not bounded to a few elements?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-20`, severity major, `file`, `symbol`, `code` = the loop header and the indexed read or binary-search call quoted verbatim from the diff, `fix` = the loop rewritten over the sequence's iterator, or the data held in an array-backed list before the indexed pass, in the file's language, `rationale` = the sequence's type, the O(min(i, n − i)) cost of each positional access and the resulting cost, quadratic for a pass that reads every position by index and at least a linear walk per search for a binary search).

## Source
- OpenJDK 21 `java.util.RandomAccess` class documentation, openjdk/jdk tag jdk-21-ga, src/java.base/share/classes/java/util/RandomAccess.java (fetched): "The best algorithms for manipulating random access lists (such as ArrayList) can produce quadratic behavior when applied to sequential access lists (such as LinkedList)."; "a List implementation should implement this interface if, for typical instances of the class, this loop: for (int i=0, n=list.size(); i < n; i++) list.get(i); runs faster than this loop: for (Iterator i=list.iterator(); i.hasNext(); ) i.next();"; "some List implementations provide asymptotically linear access times if they get huge, but constant access times in practice."
- OpenJDK 21 `java.util.LinkedList` class documentation, same tag, LinkedList.java (fetched): "Operations that index into the list will traverse the list from the beginning or the end, whichever is closer to the specified index."
- OpenJDK 21 `Collections.binarySearch`, same tag, Collections.java (fetched): "This method runs in log(n) time for a "random access" list (which provides near-constant-time positional access). If the specified list does not implement the RandomAccess interface and is large, this method will do an iterator-based binary search that performs O(n) link traversals and O(log n) element comparisons."; implementation: `list instanceof RandomAccess || list.size()<BINARYSEARCH_THRESHOLD` with `BINARYSEARCH_THRESHOLD = 5000`; tuning comment on the list algorithms: "Often, the random access variant yields better performance on small sequential access lists. The tuning parameters below determine the cutoff point for what constitutes a "small" sequential access list for each algorithm. The values below were empirically determined to work well for LinkedList."; cutoffs for whole-list passes `COPY_THRESHOLD = 10`, `REPLACEALL_THRESHOLD = 11`, `REVERSE_THRESHOLD = 18`, `FILL_THRESHOLD = 25`.
- OpenJDK 21 `List.sort` @implSpec, same tag, List.java (fetched): "The default implementation obtains an array containing all elements in this list, sorts the array, and iterates over this list resetting each element from the corresponding position in the array. (This avoids the n² log(n) performance that would result from attempting to sort a linked list in place.)"
- Rust `std::collections` module documentation, "Cost of Collection Operations", rust-lang/rust master, library/std/src/collections/mod.rs (fetched): get(i) — "Vec O(1)", "LinkedList O(min(i, n-i))".
- Python `collections.deque` documentation, python/cpython main, Doc/library/collections.rst (fetched): "Indexed access is O(1) at both ends but slows to O(n) in the middle. For fast random access, use lists instead."
- CPython `bisect` module, python/cpython main, Modules/_bisectmodule.c (fetched): the search loop `while (lo < hi) { ... mid = ((size_t)lo + hi) / 2; ... // PySequence_GetItem, but we already checked the types. litem = sq_item(list, mid);`, which reads the midpoint by index on every probe; Lib/bisect.py, same branch (fetched), the same loop: `mid = (lo + hi) // 2` and `if a[mid] < x:`.
- SonarSource RSPEC S2250 "Collection methods with O(n) performance should be used carefully", SonarSource/sonar-java master, S2250.html (fetched): "When the collection is large, this could therefore be an expensive operation."; "This rule raises an issue when the following O(n) methods are called outside of constructors on class fields: ... LinkedList get contains".
- Caveat: the sources state the cost class of each operation and measure no workload, so the rule names the cost class and no speed-up figure.
