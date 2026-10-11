---
title: An array or buffer whose capacity the code grows by hand enlarges it in proportion to its current size, not by a fixed number of elements, when its final size grows with the input
rule_id: PRF-25
domain: performance
step: [implement]
applies_to: [universal]
triggers: ['\brealloc\s*\(.*\+\s*(\d+|[A-Z][A-Z0-9_]*)\b', '\b\w*([cC]ap|[cC]apacity|[aA]lloc\w*|[bB]uf_?[sS]ize|[mM]ax_?[sS]ize)\s*(\+=|=\s*\w+\s*\+)\s*(\d+|[A-Z][A-Z0-9_]*)\b', '\bnew\s+Vector\s*(<[^>]*>)?\s*\(\s*[^,()]+,\s*[^,()]+\)', '[.]reserve_exact\s*\(|[.]reserve\s*\(\s*\w+[.]size\(\)\s*\+', '\b(Arrays[.]copyOf|Array[.]Resize)\s*\(.*[.][lL]ength\s*\+\s*(\d+|[A-Z][A-Z0-9_]*)\b|\bmake\(\s*\[\].*\b(len|cap)\(\w+\)\s*\+\s*(\d+|[A-Z][A-Z0-9_]*)\s*\)', '\bnew\s+\w+(\s*<[^>]*>)?\s*[\[(]\s*[\w.]+[.](length|Length|byteLength)\s*\+\s*(\d+|[A-Z][A-Z0-9_]*)\s*[\])]']
scope: file
check_kind: semantic
severity_default: minor
---

# An array or buffer whose capacity the code grows by hand enlarges it in proportion to its current size, not by a fixed number of elements, when its final size grows with the input

## Thesis
Where code itself decides how an array's or buffer's capacity grows (by reallocating or copying it into a larger block, by configuring a growable array with a fixed capacity increment, or by reserving exactly the room for the next few elements before an append) and the number of appends grows with the input, each growth enlarges the capacity in proportion to its current size, multiplying it by a factor greater than 1. Any factor greater than 1 meets the rule, and the factor may change as the size grows so long as it never falls below one constant greater than 1; a growth that adds a fixed number of elements, whose factor falls towards 1 as the capacity grows, does not.

## Rationale
A growth that moves the elements into a larger array copies the whole current array, so each growth costs time in proportion to the elements it holds. Growing at a constant factor avoids quadratic growth performance, and any factor greater than 1 gives amortized constant-time append towards an unbounded number of appends. The over-allocation can be mild: one eighth of the new size plus a few slots, giving capacities 0, 4, 8, 16, 24, 32, 40, 52, 64, 76, is enough for linear-time amortized behaviour over a long sequence of appends even when the system's reallocation performs poorly. The factor trades reallocation against memory: a factor that is too small (say 1.1) causes frequent reallocation, and one that is too large (say 3 or 4) consumes much more memory than needed. Factors in use differ (doubling for small arrays moving towards 1.25 for large ones, growth by half the capacity, over-allocation by an eighth), so the rule fixes none. An exact reservation does not deliberately over-allocate to avoid frequent allocations, so one repeated before appends grows the capacity by the fixed count it reserves, apart from any extra space the allocator gives.

## Example
```go
bad:  if len(buf) == cap(buf) {
          grown := make([]int, len(buf), cap(buf)+64)
          copy(grown, buf)
          buf = grown
      }
good: if len(buf) == cap(buf) {
          grown := make([]int, len(buf), max(2*cap(buf), 64))
          copy(grown, buf)
          buf = grown
      }
```

## Limits
A library growable array left to its own growth policy is outside the rule: several standard growable arrays promise amortized constant-time append at the end, and two of them leave the growth policy unspecified beyond that. A capacity reserved once to a known final size is outside the rule: an exact reservation fits where no further insertions are expected, and where they are expected the over-allocating reservation is the one to prefer. The amortized bound concerns a long sequence of appends, so a buffer whose element count the domain bounds to a few growths is outside the rule. Proportional over-allocation keeps linear-time amortized appends where the reallocation performs poorly, so a fixed-step reallocation is flagged as well. A copy of a whole immutable value made on every append is a separate defect that this rule does not reach, and the rule fixes no growth factor.

## Validator
Grep the hunk for a new capacity computed as the old length or capacity plus a constant (a reallocation, a copy into a new array, a new array or slice sized from the old one plus a number), for a growable array constructed with a positive capacity increment, and for an exact reservation of a few more elements. Open the file and trace where that growth runs: inside a loop or an append routine reached once per element over data whose size grows with the input, rather than once to a known final size or a few times within a bound the domain sets. Confirm that the increment is a fixed count, not a multiple or fraction of the current capacity, and that the array is not a library growable array left to its own policy. Validator question: **Does a capacity growth reached repeatedly while input-sized data is appended enlarge the capacity by a fixed number of elements, not by a factor greater than 1?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-25`, severity minor, `file`, `symbol`, `code` = the line that computes the new capacity as the old one plus a constant, or that configures the fixed increment or the exact reservation, `fix` = the same growth computing the new capacity as the current capacity times a constant factor greater than 1, or the library growable array's own append, in the file's language, `rationale` = the fixed step, the loop whose appends grow with the input, and the quadratic copying that follows).

## Source
- CPython `Objects/listobject.c` (python/cpython main), `py_list_resize`: "This over-allocates proportional to the list size, making room for additional growth. The over-allocation is mild, but is enough to give linear-time amortized behavior over a long sequence of appends() in the presence of a poorly-performing system realloc()." / "The growth pattern is: 0, 4, 8, 16, 24, 32, 40, 52, 64, 76, ..." / `new_allocated = ((size_t)newsize + (newsize >> 3) + 6) & ~(size_t)3;` (fetched)
- folly `folly/docs/FBVector.md` (facebook/folly main), §Memory Handling: "grows exponentially (at a constant factor) in order to avoid quadratic growth performance. ... Any factor greater than 1 ensures O(1) amortized append complexity towards infinity. But a factor that's too small (say, 1.1) causes frequent vector reallocation, and one that's too large (say, 3 or 4) forces the vector to consume much more memory than needed." (fetched)
- OpenJDK `java/util/Vector.java` (openjdk/jdk tag jdk-21-ga), field `capacityIncrement` and `grow(int)`: "If the capacity increment is less than or equal to zero, the capacity of the vector is doubled each time it needs to grow." / `capacityIncrement > 0 ? capacityIncrement : oldCapacity` ... `return elementData = Arrays.copyOf(elementData, newCapacity);` (fetched)
- OpenJDK `java/util/ArrayList.java` (openjdk/jdk tag jdk-21-ga), class Javadoc and `grow(int)`: "The details of the growth policy are not specified beyond the fact that adding an element has constant amortized time cost." / `oldCapacity >> 1 /* preferred growth */` (fetched)
- Rust `library/alloc/src/vec/mod.rs` (rust-lang/rust master), `Vec` Guarantees and `Vec::reserve_exact`: "Whatever strategy is used will of course guarantee O(1) amortized push." / "Unlike reserve, this will not deliberately over-allocate to speculatively avoid frequent allocations. ... Note that the allocator may give the collection more space than it requests. ... Prefer reserve if future insertions are expected." (fetched)
- ISO/IEC 14882 working draft (cplusplus/draft main, `source/containers.tex`), [vector.overview]/1: "a sequence container that supports (amortized) constant time insert and erase operations at the end" (fetched)
- Go runtime `src/runtime/slice.go` (golang/go master), `nextslicecap`: "Transition from growing 2x for small slices to growing 1.25x for large slices." (fetched)
