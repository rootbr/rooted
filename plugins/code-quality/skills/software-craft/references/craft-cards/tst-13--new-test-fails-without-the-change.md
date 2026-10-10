---
title: A test that a change adds for new or changed behaviour, including the regression test of a bug fix, fails against the code without the change on an assertion about that behaviour or on a crash the change removes, and passes with it
rule_id: TST-13
domain: tests
step: [implement, test]
applies_to: [tests]
triggers: ['signal:test_file', '@(Test|ParameterizedTest)\b|#\[(tokio::)?test\]|\bfunc\s+Test\w*\(|\bdef\s+test\w*\(|\b(it|test)\(\s*["''`]', '\b(assert\w*|assertThat|expect|require[.]\w+)\s*[(!]|\bt[.](Error|Errorf|Fatal|Fatalf)\(|[.]to(Be|Equal|StrictEqual|Throw)\w*\(', '(?i)\b(regression|reproduc\w*|issue\s*#?\d+|bug\s*#?\d+)\b|#\d{2,}\b']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A test that a change adds for new or changed behaviour, including the regression test of a bug fix, fails against the code without the change on an assertion about that behaviour or on a crash the change removes, and passes with it

## Thesis
Each test that a change adds or updates for new or changed behaviour, including the regression test of a bug fix, fails when run against the code without the change, on an assertion about that behaviour or on a crash the change removes, and passes with the change. The code without the change is the base version with every name the change declares present as a placeholder: a new routine returns an empty value, a new type, field, variant or constant is declared with no behaviour, and a routine whose signature the change alters keeps its base body under the new signature. A test that passes without the change, or that fails there only on a missing name, a compile error, or a crash the change does not remove, does not test the change. The rule holds in either order of writing: a test written first is run against a placeholder and seen failing for the expected reason before the code that makes it pass exists; a test written afterwards is seen failing by breaking the code on purpose; a reviewer asks whether the tests would fail when the code is broken.

## Rationale
Tests do not test themselves, and tests for tests are rarely written, so a person has to establish that a test is valid; watching it fail against the code without the change answers one part of that check, whether the test fails when the code is broken. A regression test that fails on the base version and passes after the fix catches the bug if it comes back, which helps prevent repeating the mistakes of the past; a test that passes on both versions detects nothing the change did. A failure from a missing routine, a compile error or a crash is not the expected reason, unless the change removes that crash, as a fix removes the bug's crash or a feature replaces the error the base raises on the new input: a placeholder that returns an empty value lets the test compile, run without crashing and fail because the empty result does not match the expected one. For code that already exists, changing it so that it no longer produces the tested result, as by flipping a comparison or dropping an argument from the output, shows the failing result and that the test catches the bug.

## Example
```rust
bad:  // regression test for the fix: parse trims surrounding spaces
      #[test]
      fn parses_padded_input() { assert_eq!(parse("7"), Ok(7)); }
good: // regression test for the fix: parse trims surrounding spaces
      #[test]
      fn parses_padded_input() { assert_eq!(parse(" 7 "), Ok(7)); }
```

## Limits
The order of writing is outside the rule: test-first is one of many ways to write software, review guidance asks that tests be added in the same change as the production code and prescribes no order, and a crossover replication with 21 graduate students found no significant difference between test-driven development and test-last in testing effort (p = .27), external code quality (p = .82) or productivity (p = .83). A change that refactors without changing behaviour keeps its tests passing before and after, so tests that only pin existing behaviour across such a change are outside the rule. A test that a behaviour-changing change adds to pin behaviour it leaves alone, such as an unpadded input beside a trimming fix, passes on the base by design and is outside the rule; a test is one for new or changed behaviour when its name, its comment or the change's description ties it to what the change adds or fixes. A change made in an emergency may ship without tests; the rule applies to the tests a change does add. A test of a new routine whose expected result is the placeholder's own empty value, such as a search that finds nothing, passes against the placeholder by construction and is outside the rule; the routine's other tests carry it. Assertion strength in general and the structure of a test are outside the rule; it asks only whether the test tells the change apart from the code before it.

## Validator
Grep the hunk for added or updated test routines and their assertions. Open the base version of the code under test at the card's scope, and for every name the change declares, take a placeholder as the base (a new routine returning an empty value; a new type, field, variant or constant declared with no behaviour) and skip a test whose expected result is that empty value; for a routine whose signature the change alters, take its base body under the new signature. For each added test that its name, its comment or the change's description ties to what the change adds or fixes, trace its inputs through the base code and evaluate each assertion: whether it holds there, whether the test fails earlier on a missing name, a compile error or a crash the change does not remove, or whether it fails on an assertion about the new or changed behaviour. For a bug fix, check that the regression test exercises the input that triggered the bug. Validator question: **Does a test that the change adds or updates for new or changed behaviour pass against the code without the change, or fail there only on a missing name, a compile error or a crash the change does not remove, rather than on an assertion about that behaviour?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-13`, severity major, `file`, `symbol`, `code` = the added test's assertion line quoted verbatim from the diff, `fix` = an assertion in the file's language on an input whose expected value the change alters, one the base code fails, `rationale` = the behaviour the change adds or fixes and why the base code passes the test or fails it before reaching the assertion).
