---
title: An equality assertion puts the expected and the actual value in the positions its framework labels, or in the one order the rest of the file uses where the framework labels them neutrally
rule_id: TST-39
domain: tests
step: [test]
applies_to: [tests]
triggers: ['\bassert(Equals|NotEquals|Same|NotSame|ArrayEquals|IterableEquals|LinesMatch)\(\s*[a-z_]\w*([.]\w+)*(\([^()]*\))?\s*,\s*([\x22\x27]|-?\d|true\b|false\b|null\b|[A-Z][A-Z0-9_]+\b)|\b(assert|require)[.](Equal|EqualValues|Exactly|NotEqual)\(\s*t\s*,\s*[a-z_]\w*([.]\w+)*(\([^()]*\))?\s*,\s*([\x22\x60]|-?\d|true\b|false\b|nil\b)|\b(assertThat|expect)\(\s*([\x22\x27\x60]|-?\d+\b|true\b|false\b|null\b)|\bassert_(eq|ne)!\s*\(|\bassert(Equal|NotEqual|Is|IsNot)\s*\(', 'signal:test_file']
scope: file
check_kind: semantic
severity_default: minor
---

# An equality assertion puts the expected and the actual value in the positions its framework labels, or in the one order the rest of the file uses where the framework labels them neutrally

## Thesis
An equality or comparison assertion that takes an expected and an actual argument passes the hard-coded expected value in the position its framework labels expected and the value derived from the code under test in the position it labels actual. Where the framework labels its two positions neutrally, as left and right, every assertion in a file keeps one order, the one the file's other assertions already use.

## Rationale
Expected and actual passed in the wrong order do not alter the outcome of the test, which still succeeds or fails when it should, but the error message then contains misleading information: the value reported as expected is the one the code produced, and the hard-coded value is reported as what the code returned. Where the framework prints both arguments under neutral labels, the order in which the expected value and the produced value are given does not matter to the report, and a file that mixes both orders makes readers re-interpret each assertion and makes its failure messages harder to scan.

## Example
```java
bad:  assertEquals(cart.total(), 1150);
good: assertEquals(1150, cart.total());
```

## Limits
Argument order divides on whether the framework labels its positions. Under expected and actual labels a swapped pair leaves the outcome unchanged and makes the message misleading; under left and right labels either order prints both values under labels that stay true, since a swap only moves each value to the other side, and a tool rule for a neutrally labelled framework raises only when one file mixes both orders. A file whose assertions all use one order under neutral labels meets the rule whichever order that is. An assertion whose two arguments both derive from the code under test, or are both literals, has no expected position to misplace and is outside the rule; so is a hand-written failure message, whose diff direction is the report's own statement.

## Validator
Grep the hunk for equality, identity and comparison assertions that take two values. Open the file to learn whether the framework labels the two positions expected and actual or neutrally and, under neutral labels, which order the file's other assertions use. For each assertion in the hunk, identify the hard-coded expected value (a literal, a constant, or a value the test builds without calling the code under test) and the value derived from the code under test. Validator question: **Does an assertion in the hunk place the hard-coded expected value in the position its framework labels actual or the produced value in the position it labels expected, or, under neutral labels, put the two in the order opposite to the file's other assertions?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-39`, severity minor, `file`, `symbol`, `code` = the assertion quoted verbatim from the diff, `fix` = the assertion with its two arguments reordered, in the file's language, `rationale` = which value sits under which label and the misleading or inconsistent failure message that results).
