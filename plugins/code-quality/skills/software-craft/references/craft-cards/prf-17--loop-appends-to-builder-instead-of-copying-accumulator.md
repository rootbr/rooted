---
title: A loop builds a string or collection by appending to a builder, a growable array or a list joined once after the loop, not by copying the whole accumulated value on every iteration
rule_id: PRF-17
domain: performance
step: [implement]
applies_to: [universal]
triggers: ['\+=\s*(["''`]|f["'']|\w+\s*\+|str\(|\w+[.](toString|String|join|format)\b)|\b(s|str|out|result|res|text|html|line|buf|acc|output|msg|message)\s*\+=|\b(\w+)\s*=\s*\4\s*\+\s*\S', '\bsum\([^)]*,\s*\[\]\s*\)', '\[\s*[.]{3}\s*\w+\s*,|\{\s*[.]{3}\s*\w+\s*,', '[.]concat\(', '\bformat!\(\s*"\{\w*\}|\bfmt[.]Sprintf\(\s*"%[sv]']
scope: file
check_kind: semantic
severity_default: major
---

# A loop builds a string or collection by appending to a builder, a growable array or a list joined once after the loop, not by copying the whole accumulated value on every iteration

## Thesis
Where a concatenation creates a new value that copies the accumulated one, a loop, reduction or summation whose iteration count grows with its input builds its string or collection by appending each piece to a string builder, a buffer or a growable array and joining or converting once after the loop. The forms this replaces are addition of an immutable accumulated string or sequential formatting of an accumulated string into a new string, addition of an immutable sequence, a summation of lists that starts from an empty list, and an array or object accumulator spread or concatenated into a new one on each step.

## Rationale
Concatenating immutable sequences always results in a new object, so building up a sequence by repeated concatenation will have a quadratic runtime cost in the total sequence length; recopying the growing string in each iteration can lead to a cost quadratic in the number of iterations. A summation of lists creates a new list for each element, and spread syntax on an accumulator causes a time complexity of O(n^2) rather than O(n). A standard growable array is documented to add an element in amortized constant time, so adding n elements requires O(n) time, and a string builder, a buffer, or a list joined once after the loop has amortized-linear run-time complexity. In a published microbenchmark that appends one six-character word per iteration, concatenation took 377.08, 40221.49 and 5286840.53 µs/op for 1,000, 10,000 and 100,000 iterations, while a string builder took 10.25, 93.27 and 1019.91 µs/op. The rule restores a build cost linear in the size of the result.

## Example
```typescript
bad:  let result: Item[] = [];
      for (const row of rows) result = [...result, toItem(row)];
good: const result: Item[] = [];
      for (const row of rows) result.push(toItem(row));
```

## Limits
The separating condition is whether the step the loop repeats creates a new value that copies the accumulated one. For immutable strings and sequences, for sequentially concatenated or formatted strings, for a summation of lists and for a spread accumulator, the language documentation, style guides and tool rules state that it does, at quadratic cost. Out of scope is a string addition the language documents as consuming the left-hand string and re-using its buffer, growing it if necessary, which it does to avoid the O(n^2) running time of repeated concatenation. Out of scope too is string addition on an engine that builds the result as a pair of pointers to the two operand strings. A runtime whose implementation sometimes performs string addition in place stays in scope: that optimization is fragile, working only for some types and absent from implementations that don't use refcounting, so code should not rely on it, with performance-sensitive parts of the library using the join form to ensure linear time across implementations. A loop whose iteration count the domain fixes at a small constant is out of scope, since the cost the tool rules describe is quadratic in the number of iterations and a fixed count bounds it.

## Validator
Grep the hunk for a compound or repeated addition to the same variable (`x += piece`, `x = x + piece`), a formatting call that takes the accumulated string as an argument and is assigned back to it, a summation seeded with an empty list, a spread of a variable as the first element of an array or object literal, a concat call assigned back to its receiver, and an addition or concat call on a reduction callback's accumulator that the callback returns as the next accumulator. Open the file and confirm the statement sits inside a loop body or a reduction callback and that the variable is the accumulator carried across iterations. Trace the accumulator's type and the operation that rebuilds it: an immutable string or sequence, a string rebuilt by a formatting call, or an array or object rebuilt by spread or concatenation, is in scope; string addition the language documents as re-using the left operand's buffer, or string addition on an engine that builds the result as a pair of pointers to the operands, is out. Trace the loop's bound: a collection, stream or input whose size grows with the data is in scope; a count the domain fixes at a small constant is out. Validator question: **Does a loop, reduction or summation over input-sized data rebuild its accumulated string or collection as a new value that copies the accumulated contents on every iteration?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-17`, severity major, `file`, `symbol`, `code` = the accumulating statement and its loop or reduction header, verbatim from the diff, `fix` = the same loop appending each piece to a string builder, buffer or growable array and joining or converting once after it, in the file's language, `rationale` = the accumulator's type, the operation that copies it on each iteration and the input that bounds the iteration count).
