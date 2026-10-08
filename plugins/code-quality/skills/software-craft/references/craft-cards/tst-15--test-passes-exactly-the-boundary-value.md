---
title: When the code under test compares an input with a boundary value, a test passes exactly that boundary value, not only values clearly on either side of it
rule_id: TST-15
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['signal:test_file', '\b(if|elif|while|when|return|assert\w*|require)\b[^;{]*[\w)\]]\s*(<=|>=|<|>)\s*-?(\d[\d_.]*|[A-Z][A-Z0-9_]+|[A-Za-z][a-z0-9]*[A-Z]\w*)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# When the code under test compares an input with a boundary value, a test passes exactly that boundary value, not only values clearly on either side of it

## Thesis
When the behaviour under test turns on a comparison of an input with a boundary, such as a threshold, a limit or the end of a range, its tests include a case whose input is the boundary value itself and whose assertion checks the result expected at that value, in addition to cases on each side.

## Rationale
Many faults tend to concentrate near the extreme values of an input's domain, which is why boundary-value analysis chooses test cases on or near the boundaries. Changing a strict comparison to its non-strict form, such as greater-than to greater-or-equal, changes the result for the boundary input only. Inputs clearly above and clearly below the boundary return identical results under both operators, so a suite that checks only them cannot tell the operators apart: the boundary-shift mutant survives, and the shifted comparison would reach production with no test catching it. At the boundary value the two operators return different results, and that difference is what kills the mutant. In the documented case a threshold of 5 tested only with the inputs 10 and 2 leaves one of its two comparison mutants alive, a mutation score of 50.0%; one added test that passes 5 raises the score to 100.0%.

## Example
```go
bad:  func tier(n int) int { if n > 5 { return 2 }; return 1 }
      func TestTier(t *testing.T) { if tier(10) <= tier(2) { t.Error("tier(10) <= tier(2)") } }
good: func TestTierAtBoundary(t *testing.T) {
          if got := tier(5); got != 1 { t.Errorf("tier(5) = %d, want 1", got) }
          if got := tier(4); got != 1 { t.Errorf("tier(4) = %d, want 1", got) }
          if got := tier(6); got != 2 { t.Errorf("tier(6) = %d, want 2", got) }
      }
```

## Limits
Inputs chosen outside the input domain, to test how the code processes unexpected or erroneous values, belong to robustness testing, an extension of boundary-value analysis that the rule does not require. When a mutation run reports the strict-to-non-strict mutant of the comparison as killed, the suite already tells the two operators apart and meets the rule; the rule targets a comparison whose mutant survives.

## Validator
Grep the hunk for a condition or return that compares a variable, or a value computed from one such as its length, with a numeric literal or a named constant through `<`, `<=`, `>` or `>=`, and note the enclosing routine. Derive the boundary input the operator implies: the input value at which the two sides of the comparison are equal. When the hunk is the routine, open the tests that call it; when the hunk is a test, open the routine it calls and read its comparisons. Trace each test input that reaches the comparison and look for one equal to the boundary input whose assertion fails when the comparison is switched between its strict and non-strict form, such as one that checks the exact result there. Leave unflagged a routine with no test reaching the comparison and a comparison inside a test's own assertion. Validator question: **Do the tests that reach the comparison lack a case that passes exactly the boundary value with an assertion that fails when the comparison is switched between its strict and non-strict form?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-15`, severity minor, `file`, `symbol`, `code` = the comparison line when the hunk holds the routine, or the test line that calls the routine when the hunk holds the test, quoted verbatim from the diff, `fix` = a test case that passes exactly the boundary value and asserts the result expected there, in the file's language, `rationale` = names the boundary value, the operator, and the test inputs on either side that return the same result whether the comparison is strict or not).

## Source
- SWEBOK V3.0, IEEE Computer Society, ch. 4 'Software Testing' §3.2.3 'Boundary-Value Analysis' (V4.0a: ch. 5 §3.1.2) — raw.githubusercontent.com/ligurio/swebok-v3/master/4_software_testing.md (fetched): "Test cases are chosen on or near the boundaries of the input domain of variables"; "many faults tend to concentrate near the extreme values of inputs"; "An extension of this technique is robustness testing, wherein test cases are also chosen outside the input domain of variables to test program robustness in processing unexpected or erroneous inputs."
- muttest mutation-testing package documentation, article 'Reading mutation results and strengthening tests', 'Example: Shipping Cost — Missing Boundary Value' — raw.githubusercontent.com/jakubsob/muttest/gh-pages/articles/interpreting-results.html (fetched): "A test suite that checks only “clearly above” and “clearly below” cases will let a boundary-shift mutant survive."; "It passes inputs of 10 and 2 kg"; "Changing weight_kg > 5 to weight_kg >= 5 only affects input weight_kg = 5 exactly. For inputs 10 and 2, the function returns identical results under both operators, so the test cannot tell the operators apart."; "In production, >= 5 instead of > 5 would route 5 kg shipments to the expensive tier and no test would catch the regression."; before the fix "KILLED 1 | SURVIVED 1 | NO COVERAGE 0 | ERRORS 0 | TOTAL 2 | SCORE 50.0%"; the fix keeps the 10-and-2 test and adds 'test_that("5kg falls into the lower-cost tier", { expect_equal(shipping_cost(5), 5.00) })'; "Add a test that passes the exact boundary value 5. With > 5, the condition is FALSE and the function returns 5.00. With >= 5, it is TRUE and returns 15.00. This difference kills the mutant."; after the fix "KILLED 2 | SURVIVED 0 | NO COVERAGE 0 | ERRORS 0 | TOTAL 2 | SCORE 100.0%"; "When a comparison mutant survives, find the boundary value implied by the operator and add a test that passes exactly that value."
- Caveat: the mutation example covers one strict-to-non-strict swap on one numeric threshold, and the standard states the technique and its rationale without a fault rate.
