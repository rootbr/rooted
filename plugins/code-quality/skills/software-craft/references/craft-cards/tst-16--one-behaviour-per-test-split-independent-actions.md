---
title: A test checks one behaviour, making as many assertions as that behaviour's outcome needs, and an independent second behaviour with assertions on its own outcome is a separate test
rule_id: TST-16
domain: tests
step: [test]
applies_to: [tests]
triggers: ['(?i)^\s*(async\s+)?(def|fn)\s+\w*_and_\w*\s*\(', '^\s*(public\s+|protected\s+|private\s+)?(void|fun|func|fn)\s+\w*[a-z0-9]And[A-Z]\w*\s*\(', '\b(it|test)\s*\(\s*[\x22\x27\x60][^\x22\x27\x60]*\band\b[^\x22\x27\x60]*[\x22\x27\x60]', '\bt[.]Run\(\s*[\x22\x60][^\x22\x60]*(_and_|\band\b)[^\x22\x60]*[\x22\x60]', 'signal:long_routine']
scope: file
check_kind: semantic
severity_default: minor
---

# A test checks one behaviour, making as many assertions as that behaviour's outcome needs, and an independent second behaviour with assertions on its own outcome is a separate test

## Thesis
A test sets up the data or state it needs, runs one action on the code under test and asserts that the action's results are what it expects. Several assertions on that one outcome, such as one check for each of several properties of one returned value, can stay in the same test, so the number of assertions is proportioned to what the outcome needs. When a test also runs a second action on the code under test that does not depend on the first and either calls other code or needs other checking logic, and asserts on that action's own outcome, it checks a second behaviour and is split into one test per behaviour. The same call checked by the same logic on several inputs is one behaviour with several cases and stays in one test, as rows of a table or one after another. A count of assertions, or of production methods a test calls, is a sign to inspect; the split follows the independent actions that call other code or need other checking logic.

## Rationale
A common good practice is to write tests that target only one logical concept and can fail for only one reason. Many assertions mark a complex test whose correctness is harder to verify, and as more assertions are made there is a possible tendency for the test to mix multiple objectives. Across 221 releases of ten software systems and more than a million test cases, tests with smells were more change- and defect-prone, and production code was more defect-prone when tested by smelly tests. Test methods exercising more methods of the tested object, and test methods containing several assertions with no explanation, were more change- and defect-prone than test methods with other smells; the second measure also covers several unexplained assertions on one outcome, and the study explains that such tests test more than required, checking several methods of the tested object or holding several assertions that check different behaviour, which makes them intrinsically more complex to understand and likely leads developers to be more prone to introduce faults. The study measures the association of test smells with software quality. In 199 participant evaluations of 10 test cases, too many assertions correlated with a decrease of perceived quality, and the study suggests that the number of assertions in a unit test should be proportioned to its purpose.

## Example
```rust
bad:  #[test]
      fn split_returns_parts_and_rejects_missing_sign() {
          let (k, v) = split("a=b").unwrap(); assert_eq!(k, "a"); assert_eq!(v, "b");
          assert!(split("ab").is_none());
      }
good: #[test]
      fn split_returns_both_parts() { let (k, v) = split("a=b").unwrap(); assert_eq!(k, "a"); assert_eq!(v, "b"); }
      #[test]
      fn split_rejects_missing_sign() { assert!(split("ab").is_none()); }
```

## Limits
Comparing several different properties of one function's output takes one check per property within one test, and a test that keeps going after a failed check prints all of the failed checks in a single run. Calls that set up the data or state the action needs form the test's setup step, distinct from the action it runs. Many test cases tested with similar logic, such as rows of expected output for given input, form one table-driven test; cases that need different checking logic, such as exact output for valid input and an error for invalid input, are appropriately written as separate tests, and a simple extra case such as basic error checking that adds no conditionalized flow to the table's loop body is permissible in the existing test.

The rule is contested. One position counts assertions: a static-analysis rule with a default maximum of one assertion asks to consider breaking the test scenario into multiple, shorter test scenarios and documents the maximum as customizable to suit a project's needs, while other rules flag above 5 or above 25 assertions by default. A second position counts production methods: a detector flags a test method that invokes several methods of the production object, and the change- and defect-proneness measured for such tests is explained as their checking several methods and testing more than required. What separates the cases is whether the assertions check one behaviour, that is one action's outcome or the same call checked by the same logic on several inputs, or check independent actions that call other code or need other checking logic. Several assertions on one action's outcome can belong in one test: one rule's text grants that it might make sense to have more than one assertion to test one concept, and a style guide asks for a separate check for each of several properties of a function's output. A second, independent action on other code or with other checking logic is split off: one counting rule names the tendency to mix multiple objectives, another asks to consider breaking the scenario into shorter scenarios, and the study that measured several unexplained assertions explains them as several assertions checking different behaviour. A project that configures an assertion maximum keeps it as its documented tolerance.

## Validator
Grep the hunk for test names that join two clauses with "and" and for long test bodies. Open the test at file scope and read its whole body. Group the calls on the code under test into actions: a call whose result or state a later call depends on is setup for that later call. A call that only reads the result an action returned or the state it left, such as an accessor on the returned value, belongs to the assertion on that action's outcome; it is neither setup nor a separate action. A named subtest or nested test case is its own test. For each assertion, trace which action's result it reads. Count the same call checked by the same assertion logic on several inputs as one action, whether the cases are rows of a table under one shared loop body or written one after another. Validator question: **Does the test run two or more actions on the code under test that do not depend on each other, each followed by assertions on its own outcome?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-16`, severity minor, `file`, `symbol`, `code` = the test's signature line and the first line of the second independent action with its assertion, `fix` = the two tests, each named for its one behaviour and holding one action with the assertions on its outcome, in the file's language, `rationale` = the two independent actions and the outcome each group of assertions checks).
