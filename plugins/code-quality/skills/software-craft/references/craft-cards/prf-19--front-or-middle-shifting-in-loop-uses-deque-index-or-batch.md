---
title: A loop that removes or inserts elements one at a time at the front or middle of an array-backed sequence uses a deque, a moving start index or one batch operation, because each such call shifts every later element
rule_id: PRF-19
domain: performance
step: [implement]
applies_to: [universal]
triggers: ['[.](pop|remove)\(\s*0\s*\)|\bdel\s+\w+\[\s*0\s*\]|[.](insert|add|insert_str)\(\s*0\s*,|[.](shift|unshift)\(|[.]splice\(|\bslices[.](Delete|Insert)\(|\bappend\(\s*\[\][\w.*]+\{|[.]removeFirst\(\)|[.](pop|remove)\(\s*[a-z_]\w*\s*\)|\bdel\s+\w+\[\s*[a-z_]\w*\s*\]|[.](insert|add)\(\s*[a-z_]\w*\s*,|\b\w+\s*=\s*\w+\[\s*1\s*:\s*\]|[.]slice\(\s*1\s*\)|\bappend\(\s*\w+\[\s*:[^\]]*\]\s*,\s*\w+\[|\[\s*\w+\s*,\s*[.][.][.]\s*\w+\s*\]|\[\s*\w+\s*\][.]concat\(|=\s*\[\s*\w+\s*\]\s*\+\s*\w+|[.](deleteCharAt|delete)\(\s*0\s*[,)]']
scope: file
check_kind: semantic
severity_default: minor
---

# A loop that removes or inserts elements one at a time at the front or middle of an array-backed sequence uses a deque, a moving start index or one batch operation, because each such call shifts every later element

## Thesis
A loop whose iteration count grows with the input and that removes or inserts one element per iteration at the front or in the middle of an array-backed sequence (a growable array, list, slice, vector or growable string), by a call that shifts or copies the elements after that position, does that work through a double-ended queue, a start index that advances over the buffer, one batch operation (a single filtering pass, a single ranged delete, or a single pass that appends every element to a new sequence in order), or, when the order of the remaining elements need not be kept, a removal that moves the last element into the gap, which keeps the loop's total work linear in the sequence length.

## Rationale
Removing the element at position k of an array-backed sequence of size n shifts every later element one slot toward the front, moving n − k − 1 elements; inserting at position k shifts the elements from k onwards one slot toward the back, moving n − k elements. The worst case is position 0, where the whole rest of the sequence moves, and a position in the middle still costs O(n). A loop that drains n elements from the front this way moves (n − 1) + (n − 2) + … + 0 = n(n − 1)/2 elements, and a loop that builds n elements by inserting each at the front moves 0 + 1 + … + (n − 1), the same total: calling such an operation in a loop can result in quadratic behavior. A double-ended queue built on a growable ring buffer has O(1) amortized inserts and removals at both ends, so the same drain or prepend loop costs O(n) in total. A front deletion that advances the start of the buffer and leaves the remaining elements in place is amortized O(1), and a re-slice that shares its underlying array with the sliced operand copies nothing; a slice that returns a new sequence holding its own copy of the elements, as a list slice does, copies every remaining element on each call, so a loop that re-slices that way is as quadratic as the removal it replaces. Reading the element at an index takes constant time, so an index that advances one slot per iteration visits every element without moving any. Many removals collapse into one pass: a single ranged delete costs O(n − i) for a range starting at i, so one call deleting them all together is better than deleting one at a time, and an in-place filter visits each element exactly once and preserves the order of the kept elements. Many middle insertions collapse the same way, because appending n elements to the end of a growable array costs O(n) in total. When the order of the remaining elements need not be preserved, replacing the removed element with the last one removes in O(1).

## Example
```rust
bad:  let mut queue: Vec<Job> = pending;
      while !queue.is_empty() {
          let job = queue.remove(0);
          run(job);
      }
good: let mut queue: VecDeque<Job> = pending.into();
      while let Some(job) = queue.pop_front() {
          run(job);
      }
```

## Limits
Removal and insertion at the end of the sequence move nothing and are outside the rule. A structure whose front removal moves nothing is outside the rule: a double-ended queue, a re-slice that shares its underlying array, or a byte buffer whose front deletion advances the start of the buffer. A sequence whose length the domain bounds to a small constant is outside the rule, because each call then moves at most that many elements. A double-ended queue fixes only the two ends: insertion or removal at position i costs it O(min(i, n − i)), so a loop that edits the middle one element at a time takes one batch pass, which needs every position to be known before the pass. A loop whose next middle position is computed from the sequence as the earlier edits left it and lies an input-sized distance from the previous one (an elimination that counts an input-sized step around the remaining elements) has no deque, start-index or batch form among the standard collections and is outside this rule. Insertion that keeps a sequence in sorted order belongs to the choice of an ordered structure and is outside this rule.

## Validator
Grep the hunk for a removal or insertion at index 0 or at a computed position (`remove(0)`, `pop(0)`, `del x[0]`, `insert(0, …)`), a `shift`, `unshift` or `splice` call, a positional delete or insert helper, a prepend that builds a new sequence from one element plus the old one, a re-slice that drops the first element (`x = x[1:]`, `x.slice(1)`), and `removeFirst()`. Open the file and resolve each hit's receiver: an array-backed sequence, or a structure whose front operation moves nothing (a double-ended queue or ring buffer, a re-slice that shares its underlying array, a byte buffer that advances its start); a slice that copies the remaining elements into a new sequence, as a list slice does, is a removal that copies them all, while a slice that returns a view onto the same buffer moves nothing. Trace the enclosing loop or recursion: check that its iteration count grows with the input, that the call runs once per iteration, and that the position is the front or the middle rather than the end; check whether the domain bounds the sequence to a small constant; for a middle position, check whether one pass over the sequence could collect the positions, or each is computed from the sequence as the earlier edits left it and lies an input-sized distance from the previous one. Validator question: **Does a loop whose iteration count grows with the input remove or insert one element per iteration at the front, or in the middle at positions that one pass could collect or that move a bounded step per iteration, of an array-backed sequence, by a call that shifts or copies every element after that position, on a sequence the domain does not bound to a small constant?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-19`, severity minor, `file`, `symbol`, `code` = the removal or insertion call and the loop header that repeats it, verbatim from the diff, `fix` = the loop rewritten over a double-ended queue, an advancing start index, one batch operation or, where order need not be kept, a removal that moves the last element into the gap, in the file's language, `rationale` = the position of the call, the O(n − k) elements after the position that each call shifts or copies, and the quadratic total over the loop).
