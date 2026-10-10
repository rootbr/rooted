---
title: A reduce or fold is replaced by a named operation when one expresses it and by a plain loop when it mutates its accumulator or copies a growing one on each step
rule_id: DSN-58
domain: design
step: [implement, refactor]
applies_to: [functional]
triggers: ['\b(reduce|reduceRight|reducing|fold|rfold|try_fold|Reduce|Fold)(::)?(<.*>|\[[^\]]*\])?([.](call|apply))?\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A reduce or fold is replaced by a named operation when one expresses it and by a plain loop when it mutates its accumulator or copies a growing one on each step

## Thesis
A reduce or fold whose result an operation of the language or its standard library computes by name is written as that operation. Such operations include a sum, a product, a maximum, a count, a map over each element, a filter, a test whether any element or every element satisfies a predicate, the first matching element or its index, a flatten, a flat-map, a grouping by key, a join of strings and a de-duplication. A reduce or fold that no such operation expresses, and whose combining function mutates the accumulator it receives or copies on every step a whole accumulator that grows with the elements, such as an array, an object or a string each step adds to, is written as a loop that updates one accumulator in place.

## Rationale
A reduce or fold combines a sequence of elements into a single summary result by applying a combining function repeatedly. It is equivalent to a loop over the same elements, except that each step returns the new accumulator instead of mutating a variable. Because it is multipurpose, it can be difficult to understand, and a reader can take time to disentangle its combining function before seeing what it computes. Standard libraries ship specialized forms of it for common results, such as a sum, a maximum or a count. A fold that one of them computes is less readable than that more succinct form. A named search or predicate test also returns as soon as its result is certain, without visiting the rest of the elements; where the combining function or a lazy step that produces the sequence has a side effect, that early return changes what runs, and the named operation is then not equivalent to the fold. A combining function that mutates its accumulator drops the one difference between the fold and the loop, and the loop then states the same computation much more clearly. A combining function that copies the whole accumulator on every step, an array, an object or a string, can make the fold quadratic. Copying an object with one key per distinct element gives a worst case of O(N²) in the number of elements, and concatenating strings by reduction runs in O(n²) in the number of characters; such a quadratic cost has happened in real-world code. Updating one accumulator in place removes the copy, and once the accumulator is mutated, the loop is the clearer form.

## Example
```go
bad:  late := reduce(orders, false, func(seen bool, order Order) bool { return seen || order.Late() })
      counts := reduce(names, map[string]int{}, func(acc map[string]int, name string) map[string]int {
          acc[name]++
          return acc
      })
good: late := slices.ContainsFunc(orders, Order.Late)
      counts := map[string]int{}
      for _, name := range names {
          counts[name]++
      }
```

## Limits
The rule weighs reduce and fold calls, a generic helper of that shape included. An operation built to accumulate into a mutable result container, such as a collection or a string builder, mutates that container by design and is not a reduce whose accumulator is mutated. A combining function that returns a new fixed-size value, such as a pair or a small record spread from the previous one or updated field by field in a copy the function received by value, copies nothing that grows with the input, and the reduce documentation recommends copying over mutation there; the rule leaves that case to the contested one. A concatenation that moves the accumulator and appends to its buffer in place copies nothing and carries no quadratic cost.

Whether to keep a reduce or fold that no named operation expresses, and whose combining function neither mutates its accumulator nor copies one that grows with the elements, is contested; the rule does not flag it. On one side, an explicit loop is more readable 99 percent of the time and many uses of a reduce are clearer as loops; in almost every case a map, a filter or a loop can replace a reduce, and a lint rule that disallows reduce allows by default only simple arithmetic such as summing numbers. On the other side, summing an array, sequencing promises and piping functions are acceptable uses, and a reduction is preferred over a mutating accumulation loop as more abstract, since it operates on the sequence as a whole. That side also treats the fold as the general pattern from which a sum, a product, an any-true or all-true test and a map are each defined as a named function. Two conditions separate the cases the rule flags, and sources on both sides point the same way on each. Where a named operation computes the result, both sides name it as the better alternative to a reduce. Where the combining function mutates its accumulator, or copies one that grows with the elements, the documentation that lists the acceptable uses of reduce itself calls the loop much clearer, and the stream documentation moves the same accumulation into a mutable result container, which the rule does not flag.

Where a reduce or fold stays, documentation and names that say what the accumulator holds can help mitigate its readability cost. A project context that prefers higher-order functions over loops rejects the loop half of a finding, and one that forbids reduce outright decides the contested case.

## Validator
Grep the added lines of the hunk for a reduce or fold call: a method or function named reduce, reduceRight, fold, rfold or try_fold, a reducing collector, or a generic helper of that name. Read the call's initial value and its combining function in the hunk. First, name the operation of the file's language or standard library, if one exists, that computes the same result: a sum, a product, a maximum, a count, a map, a filter, an any or every test, a find or find-index, a flatten, a flat-map, a group-by, a join of strings or a de-duplication. Treat it as equivalent when it returns the same result for every input the call can receive; where the two differ only on an empty input, say so in the fix; where the combining function, or a lazy step that produces the sequence, has a side effect, an operation that stops at the first element that settles the result is not equivalent. Second, read whether the combining function mutates the accumulator it receives (an assignment to one of its elements or fields, an increment, an append, push, add, insert or set on it, where the accumulator is an object, collection or buffer passed from step to step; a fixed-size value the function received as its own copy, updated field by field and returned, is a new fixed-size value, not such a mutation) or builds on each step a new copy of an accumulator that grows with the elements (a spread or concatenation of an array or object that each step adds to, a string concatenated onto it where the concatenation allocates a new string); a new fixed-size value, such as a pair or a small record, is not such a copy. A concatenation that moves the accumulator and appends to its buffer in place is not such a copy. Skip an operation built to accumulate into a mutable container. Skip the loop half where the project context prefers higher-order functions over loops. Validator question: **Does this reduce or fold compute a result that an equivalent named operation of its language computes, or does its combining function mutate the accumulator it receives or copy on every step a whole accumulator that grows with the elements?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-58`, severity minor, `file`, `symbol`, `code` = the reduce or fold call quoted verbatim from the diff, `fix` = the call replaced by the named operation that computes the same result or, where none does, by a loop, or an operation built to accumulate into a mutable result container, that updates one accumulator in place, in the file's language, `rationale` = the named operation that states the result, or the mutation or per-step copy of the accumulator and the quadratic cost a copy carries).
