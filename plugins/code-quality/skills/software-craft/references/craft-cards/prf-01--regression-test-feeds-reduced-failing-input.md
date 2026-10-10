---
title: When a failure reproduces under an automated test, the fix's regression test feeds the code the failing input reduced to what still triggers the failure, not the whole captured input
rule_id: PRF-01
domain: performance
step: [test]
applies_to: [tests]
triggers: ['(?i)\b(test_?data|fixtures?)\b[/\\]', '(?i)\b(captured|recorded|dump|crash|repro(duce|duction)?|regression)[-_ ]?\w*[.](json|xml|html?|txt|bin|csv|log|yaml|yml)\b', 'signal:test_file', 'signal:added_file']
scope: file
check_kind: semantic
severity_default: minor
---

# When a failure reproduces under an automated test, the fix's regression test feeds the code the failing input reduced to what still triggers the failure, not the whole captured input

## Thesis
When an automated test reproduces a failure, the regression test that lands with its fix feeds the code the failing input reduced until removing any single remaining part makes that failure disappear, in place of the whole captured file, payload, log or recorded sequence of user actions.

## Rationale
A bug report must be as specific as possible so that the context in which the program failed can be recreated, while a test case must be as simple as possible, because a minimal test case implies a most general context: it allows short problem descriptions and valuable problem insights, and it subsumes several current and future bug reports. Debugging guides isolate the problem by binary search on the assumption that the test is carried out by hand; with an automated test, the delta debugging reducer simplifies the input by successive testing and stops when removing any single input part would make the failure disappear. The reducer needs time quadratic in the number of input parts in general, and logarithmic time in the best case, where a single part causes the failure. In one case study a browser crashed after 95 user actions; automated reduction left 3 relevant actions and cut 896 lines of HTML to the single line that caused the failure, and the case study required 139 automated test runs, or 35 minutes on a 500 MHz PC. The reducer's test counts a run as failing only when it produces the failure the test was intended to capture; a run with indeterminate results is unresolved, and the reducer treats an unresolved run as it treats a passing one. One fuzzing engine attempts to minimize a failing input to the smallest possible and most human-readable value that still produces the error, and that input serves as the regression test once the bug has been fixed. By default, property-based testing frameworks try to reduce counterexamples so that the errors they report are easier to troubleshoot.

## Example
```go
bad:  func TestDecodeRegression(t *testing.T) {
          in, err := os.ReadFile("testdata/captured-session.json") // the whole capture
          if err != nil { t.Fatal(err) }
          if _, err := Decode(in); err != nil { t.Fatal(err) }
      }
good: func TestDecodeRegression(t *testing.T) {
          in := []byte(`{"items":[{"id":""}]}`) // removing any part loses the failure
          if _, err := Decode(in); err != nil { t.Fatal(err) }
      }
```

## Limits
Simplification, including binary search over code, configuration or inputs, was effective once a defect was reproducible and narrowed to a manageable region, and less suitable for timing-sensitive defects, production-only failures where changes were risky, or legacy systems where simplification could introduce new faults. An input that stays large after reduction meets the rule when removing any single part of it makes the failure disappear. A failing input that a fuzzing engine has minimized and written to its seed corpus serves as the regression test as it stands. When one input holds several independent failure-inducing parts, a reducer may report only the first failing subset; fix that failure first, then check for further similar failures. The rule judges which input the test feeds, not the test's assertions or structure.

## Validator
Grep the hunk for an added or changed test that reads a file under a test-data or fixture directory, or embeds a captured file, payload, log or recorded sequence of user actions. Open the test file and the fix it accompanies, trace the input the test feeds the code under test, and look for a sign of reduction: a small inline input, a reduced fixture, a comment or message naming the reduction, or an entry a fuzzing engine or property-based framework wrote after minimizing or shrinking it. Leave timing-sensitive and production-only failures unflagged. Validator question: **Does the regression test that lands with a fix feed the code a whole captured input with no sign that it was reduced to the part that still triggers the failure?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-01`, severity minor, `file`, `symbol`, `code` = the line that loads or embeds the captured input, `fix` = the test feeding the reduced input inline or from a reduced test-data file, in the file's language, `rationale` = that a minimal failing input gives a short problem description and subsumes current and future reports of the same failure).
