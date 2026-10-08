---
title: A map or a comprehension is used for the value it builds, and work done for its effects runs in a loop or a for-each
rule_id: DSN-59
domain: design
step: [implement, review]
applies_to: [functional]
triggers: ['^\s*(let\s+_\s*=\s*|_\s*=\s*|void\s+)?(list\(\s*)?([\w$][\w$.\[\]()]*[.])?map\(', '[.]map\(.*(console[.](log|warn|error)|println!|print\(|System[.]out[.]print|fmt[.]Print)', '[.]map\(.*(=>|->|\|)\s*\{\s*$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A map or a comprehension is used for the value it builds, and work done for its effects runs in a loop or a for-each

## Thesis
A map over a collection, an iterator or a stream, a map over an optional or a result value, and a list comprehension are each used for the value they build: the callback returns a value, and the code assigns, returns, passes on or reads the result. Work done for its effects — a write, a record, a print, a mutation — runs in a loop, in a for-each step at the end of a chain, or, for one optional or result value, in a conditional that unwraps it. The rule is broken by a transforming step left as a statement with its result discarded, explicitly or not; by one whose callback returns nothing; and by one whose result is consumed only to make its callback run, such as by counting it or by collecting it into a value no code reads.

## Rationale
A map builds a new collection, iterator, stream, optional or result from its callback's results, and a comprehension builds a new list; when that result is dropped, the step does its work for a value no code reads. Where the step is eager, the callback runs and the value it builds is wasted. Where the step is lazy, nothing traverses a discarded map, so its callback never executes and the effect it was written for does not happen. Consuming the pipeline does not always make the effect run: one stream library documents that, apart from its for-each terminal steps, the effects of a callback may not run when the library can skip that callback without changing the result, and that it may compute a count directly from the pipeline's source and then evaluate no intermediate step. The official documentation of three languages names the loop or the for-each as the form for work done for its effect. Compilers and linters report the transforming forms: a map statement over an iterator whose callable returns nothing, as almost always a mistake; a map over an optional or a result with such a callable, as clearer written as a conditional; an array callback with no return, as probably a mistake; and a comprehension left as a statement, as probably meant to be something else.

## Example
```rust
bad:  items.iter().map(|item| {
          ledger.record(item);
      });
      maybe_note.map(|note| println!("{note}"));
good: for item in &items {
          ledger.record(item);
      }
      if let Some(note) = maybe_note {
          println!("{note}");
      }
```

## Limits
A step whose callback returns a value that the code reads is outside the rule even when the callback also has an effect: one stream library documents a print for debugging inside a callback as usually harmless, and whether any other effect belongs inside a callback is judged by its own rule. A pipeline returned or handed to a caller is a used result. A method named map that builds no new collection, iterator, stream, optional or result is outside the rule.

## Validator
Grep the added lines for a statement that starts with a map call, a bare map function call or an explicit discard of either, for a comprehension standing alone as a statement, and for a map whose callback prints or opens a block body. For each hit, read the hunk around it and confirm that the step builds a new collection, iterator, stream, optional or result from its callback's results. Then check whether the code assigns, returns, passes on or reads that result; whether the callback returns a value; and, where a later step consumes the result, whether it only counts it or collects it into a value no code reads. Treat an assignment to an underscore binding or a void operator applied to the step as a discard. Skip a step whose callback returns a value that the code reads although the callback also prints for debugging. Validator question: **Does an added line use a map or a comprehension whose result is discarded, whose callback returns nothing, or whose result is consumed only to make its callback run?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-59`, severity minor, `file`, `symbol`, `code` = the map or comprehension statement quoted verbatim from the diff, `fix` = the same work as a loop, a for-each step at the end of the chain, or a conditional that unwraps the optional or result value, in the file's language, `rationale` = the effect the callback performs and whether the step builds a collection no code reads or, being lazy, never runs it).

## Source
- MDN Web Docs, `Array.prototype.map()` §Description (mdn/content `files/en-us/web/javascript/reference/global_objects/array/map/index.md`) — "It calls a provided `callbackFn` function once for each element in an array and constructs a new array from the results."; "Since `map` builds a new array, calling it without using the returned array is an anti-pattern; use `forEach` or `for...of` instead." (fetched)
- What's New In Python 3.0 §Views And Iterators Instead Of Lists (python/cpython `Doc/whatsnew/3.0.rst`) — "`map` and `filter` return iterators."; "Particularly tricky is `map` invoked for the side effects of the function; the correct transformation is to use a regular `for` loop (since creating a list would just be wasteful)."; Python tutorial §List Comprehensions (`Doc/tutorial/datastructures.rst`) — "List comprehensions provide a concise way to create lists." (fetched)
- Rust `core::iter::Iterator::map` (rust-lang/rust `library/core/src/iter/traits/iterator.rs`) — "`map()` transforms one iterator into another"; "as `map()` is lazy, it is best used when you're already working with other iterators. If you're doing some sort of looping for a side effect, it's considered more idiomatic to use `for` than `map()`."; "// it won't even execute, as it is lazy." (fetched)
- `java.util.stream` package documentation §Stream operations and pipelines, §Side-effects (openjdk/jdk `src/java.base/share/classes/java/util/stream/package-info.java`) — "Intermediate operations return a new stream. They are always lazy"; "Traversal of the pipeline source does not begin until the terminal operation of the pipeline is executed."; "With the exception of terminal operations `forEach` and `forEachOrdered`, side-effects of behavioral parameters may not always be executed when the stream implementation can optimize away the execution of behavioral parameters without affecting the result of the computation."; "side-effects such as using `println()` for debugging purposes are usually harmless"; `Stream.count` API note — "In such cases no source elements will be traversed and no intermediate operations will be evaluated." (fetched)
- rustc lint `map_unit_fn`, level Warn (rust-lang/rust `compiler/rustc_lint/src/map_unit_fn.rs`) — "The `map_unit_fn` lint checks for `Iterator::map` receive a callable that returns `()`."; "Mapping to `()` is almost always a mistake." (fetched)
- clippy `option_map_unit_fn` and `result_map_unit_fn`, group complexity, warn by default (rust-lang/rust-clippy `clippy_lints/src/map_unit_fn.rs`) — "Checks for usage of `option.map(f)` where f is a function or closure that returns the unit type `()`."; "Readability, this can be written more clearly with an if let statement" (fetched)
- ESLint `array-callback-return` (eslint/eslint `docs/src/rules/array-callback-return.md`) — "If we forget to write `return` statement in a callback of those, it's probably a mistake. If you don't want to use a return or don't need the returned results, consider using `.forEach` instead." (fetched)
- Pylint W0106 `expression-not-assigned`, enabled by default (pylint-dev/pylint `pylint/checkers/base/basic_checker.py`) — "Used when an expression that is not a function call is assigned to nothing. Probably something else was intended."; it reports a comprehension statement such as `[f(x) for x in xs]`, and not a bare call (fetched)
- Caveat: no source measures how often a discarded map hides a defect; the rule rests on official documentation and on compiler and linter rules, and the skipping of callbacks in a consumed pipeline is documented for one stream library.
