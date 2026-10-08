---
title: A property leaves the generated inputs it receives unchanged and clones any input it needs to change
rule_id: TST-48
domain: tests
step: [implement, test]
applies_to: [tests]
triggers: ['[.](?:sort|reverse|splice|push|pop|shift|unshift|fill|copyWithin)\(|[.](?:append|extend|insert|remove|clear|setdefault)\(|\b(?:sort[.](?:Ints|Strings|Slice|Sort)|slices[.](?:Sort|Reverse))\(|\bCollections[.](?:sort|reverse|shuffle)\(|\bArrays[.]sort\(|[.](?:sort_(?:by|by_key|unstable)\w*|dedup\w*|truncate|retain|drain|swap|rotate_left|rotate_right)\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A property leaves the generated inputs it receives unchanged and clones any input it needs to change

## Thesis
A property predicate leaves unchanged every generated input the framework passed it, including the underlying data the argument refers to; when the predicate needs a changed version of an input, it clones the input first and changes the clone.

## Rationale
Changing an input in place might lead to bad shrinking and to a wrong display on error. A fuzzing engine states the requirement as a must: the fuzz function must not modify the underlying data of the arguments the engine provides. The same engine asks that no mutable input argument, or pointer to one, be retained between executions, as the memory backing it may be mutated during a subsequent invocation. Cloning an input before changing it is the documented way for a predicate to work on a changed value.

## Example
```rust
bad:  fn max_matches_oracle(input: &mut Vec<i32>) -> bool {
          let got = max_of(input);
          input.sort();
          got == input.last().copied()
      }
good: fn max_matches_oracle(input: &[i32]) -> bool {
          let mut sorted = input.to_vec();
          sorted.sort();
          max_of(input) == sorted.last().copied()
      }
```

## Limits
The rule covers the generated inputs the predicate received; a clone of an input, and any value the predicate builds itself, may be changed, but a shallow copy still shares every nested value the input holds by reference, so changing an element or field of such a value changes the input. Where the framework passes the predicate a clone that shares no mutable data with the copy it keeps for shrinking and for the failure report, changing the argument does not reach the kept copy. A value the framework generates for the predicate to act through, such as a per-run logger, changes through its documented use and is outside the rule.

## Validator
Grep the hunk for in-place mutators (sort, reverse, push, pop, insert, remove, clear, append, extend, fill, splice, retain, truncate) and for element or field assignment. Open each hit that sits inside a property predicate, the function or closure the framework calls with generated values, and trace the receiver back to its origin: a parameter of the predicate, an alias of one, or data reachable through one, as against a copy the predicate made (clone, slice copy, spread, copy constructor) or a value it built; a nested value that a shallow copy holds by reference, and any element or field reached through it, is still data reachable through the input. Skip an argument the framework hands over as a clone made for that call alone that shares no mutable data with the framework's copy, such as a plain value the predicate received by move. Validator question: **Does the property predicate change in place a generated input it received, or data reachable through it, instead of a copy it made first?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-48`, severity minor, `file`, `symbol`, `code` = the statement that changes the input in place, `fix` = the predicate cloning the input into a local, deep enough that the changed part shares nothing with the input, and changing the local, in the file's language, `rationale` = the input changed in place and the bad shrinking and wrong display on error it can lead to).

## Source
- fast-check documentation, Properties > Basic, warning "Beware of side effects" (dubzzz/fast-check main, website/docs/core-blocks/properties.md) (fetched): "The predicate function should not change the inputs it received. If it needs to, it has to clone them before going on. Impacting the inputs might led to bad shrinking and wrong display on error."
- Go standard library, package testing, doc comment of `(*F).Fuzz` (golang/go master, src/testing/fuzz.go) (fetched): "No mutable input arguments, or pointers to them, should be retained between executions of the fuzz function, as the memory backing them may be mutated during a subsequent invocation. ff must not modify the underlying data of the arguments provided by the fuzzing engine."
- quickcheck for Rust, `testable_fn!` in src/tester.rs (BurntSushi/quickcheck master) (fetched): "let ( $($name,)* ) = a.clone(); let mut r = safe(move || {self_($($name),*)}).result(g); if r.is_failure() { let mut a = a.shrink();" and, for a shrunk failure, "r_new.arguments = Some(debug_reprs(&[$($name),*]));" bound from the kept tuple.
- MDN Web Docs, Spread syntax (mdn/content main, files/en-us/web/javascript/reference/operators/spread_syntax/index.md) (fetched): "Spread syntax effectively goes one level deep while copying an array."
- OpenJDK, `java.util.ArrayList`, doc comment of `clone()` (openjdk/jdk master, src/java.base/share/classes/java/util/ArrayList.java) (fetched): "Returns a shallow copy of this {@code ArrayList} instance. (The elements themselves are not copied.)"
- fast-check documentation, Arbitraries > Others, `fc.context()` (dubzzz/fast-check main, website/docs/core-blocks/arbitraries/others.md) (fetched): "The produced value - let's call it ctx - can be used as a logger that will be specific to this run (and only this run)."
- Caveat: the explicit statements come from two frameworks' documentation, a TypeScript property-testing library and Go's fuzzing engine; no research paper states the rule.
