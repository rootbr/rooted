---
title: A unit whose contract states a result has a property that checks that result and not only properties that check the call raises no error
rule_id: TST-43
domain: tests
step: [design, test, review]
applies_to: [tests]
triggers: ['@given\(', '\bfc[.](?:assert|property|asyncProperty)\(', '\bproptest!|#\[proptest\]', '\bf[.]Fuzz\(', '@(?:Property|ForAll)\b', '\bquick[.]Check\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A unit whose contract states a result has a property that checks that result and not only properties that check the call raises no error

## Thesis
A unit whose contract promises a result has, among its property-based tests, at least one property that checks the returned result on generated inputs, beside any property that only calls the unit on inputs of the right shape and checks that the call completes without an uncaught exception, panic or failed assertion.

## Rationale
A property that calls the unit on generated inputs of the right shape and checks only that it does not crash is simpler than a correctness property, easy to write and a natural first one: it tries to provoke catastrophic failures such as assertion failures and uncaught exceptions, helps rule out worst-case scenarios, and can find crashes surprisingly often. In general it provides less confidence in code quality than a logical specification, because logical errors can remain in code that does not crash. In a documented date-parser walkthrough, the no-crash property first finds a panic on a non-ASCII input, and once that is fixed it and a property that every well-formed date string parses both pass; a third property starts from a generated date, formats it, parses it back and compares, and it fails with the minimal input year 0, month 10, day 1, which parses back with month 0. Of the three, only the property that checks the parsed result catches the wrong month.

## Example
```rust
bad:  proptest! { #[test] fn never_panics(s in "\\PC*") { decode(&s); } }
good: proptest! {
          #[test] fn never_panics(s in "\\PC*") { decode(&s); }
          #[test] fn decodes_back(v in any::<u32>()) {
              prop_assert_eq!(decode(&encode(v)), Some(v));
          }
      }
```

## Limits
A no-crash property is itself a documented property, for instance a type-checker, linter, formatter or compiler that does not crash when called on syntactically valid code; the rule keeps it and adds a result-checking property beside it, as the walkthrough keeps its no-crash property and goes on to test more properties. A no-crash specification is identical to one often used for fuzzing and the line between the two techniques is blurry; the rule follows the interview study in treating it as a property where a property-based testing tool drives it against a small unit of software. The confidence comparison is the general judgement of a study of 30 in-depth interviews with experienced users at one financial technology company, in which 7 of 30 participants used such properties; it is not a measurement of defects found.

## Validator
Grep the hunk for the property declarations the triggers name. For each property the hunk adds or changes, open its body and find the call to the unit under test. Open the unit's signature and documentation: a return value, an output parameter or a documented output is a contract that states a result. Trace the returned value through the body: a property that discards it, binds it to an unused name, or checks only that the call returned a success value rather than an error, leaving the value itself unchecked, checks only that no error occurred. Search the same test file, then the repository's other test files that call the same unit, for another property that calls it and asserts on its result, such as an equality, an inverse that brings back the input, an invariant, or a comparison with a model. Validator question: **Does the hunk hold a property that checks only that a call to a result-promising unit completes without an error, while no property in that test file or another test file of the repository checks that unit's result?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-43`, severity minor, `file`, `symbol`, `code` = the property's call to the unit, quoted verbatim from the diff, `fix` = a property in the file's language that checks the returned value, such as an inverse that brings back the input, an invariant or a comparison with a model, added beside the no-crash property, `rationale` = names the result the unit's contract promises and that code which does not crash can still return a wrong one).

## Source
- DOI 10.1145/3597503.3639581, §4.3 "Catastrophic Failure Properties (7/30)" (fetched, author-hosted PDF): "Rather than write logical specifications, some participants used PBT to try to provoke catastrophic failures such as assertion failures and uncaught exceptions. In general, these kinds of properties provide less confidence in code quality (there can still be logical errors, even if the code does not crash), but they help to rule out worst-case scenarios and they are easy to write."; "These kinds of specifications are identical to the ones often used for fuzzing; the line between the techniques is blurry, but since the participants were using PBT tools—including complex generators—and testing small units of software, we still consider this relevant"; "30 in-depth interviews with experienced users of PBT at Jane Street, a financial technology company"; §3.1 Population: "We recruited 31 participants and carried out 30 interviews (one was a joint interview)"; Table 1: "Pair interview; coded as one participant".
- proptest book, book/src/proptest/getting-started.md, parse_date walkthrough (fetched): "But before correctness, there's actually an even simpler property to test: _The function should not crash._ Let's start there."; "thread 'main' panicked at 'Test failed: byte index 4 is not a char boundary; it is inside 'ௗ' (bytes 2..5) of `aAௗ0㌀0`"; "// NEW: Ignore non-ASCII strings so we don't need to deal with Unicode."; "The tests pass now! But we know there are still more problems, so let's test more properties."; "The new test passes, so let's move on to something else."; "The final property we want to check is that the dates are actually parsed _correctly_."; "we start from the expected output, generate the string, and check that it gets parsed back"; "(left: `(0, 10, 1)`, right: `(0, 0, 1)`) ... minimal failing input: y = 0, m = 10, d = 1".
- Hypothesis tutorial, hypothesis/docs/tutorial/introduction.rst, "When to use Hypothesis and property-based testing" (fetched): "Simply call your code with random inputs (of the correct shape) from Hypothesis! You might be surprised how often this finds crashes."; "A type-checker, linter, formatter, or compiler does not crash when called on syntactically valid code."
- Caveat: the confidence comparison is a judgement drawn from interviews at one company, not a measurement; the walkthrough is one worked example.
