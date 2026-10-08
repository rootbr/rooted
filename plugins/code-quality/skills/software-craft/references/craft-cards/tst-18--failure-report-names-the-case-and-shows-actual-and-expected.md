---
title: A failing test's report names the test and its case and shows the actual and the expected value, through the assertion's own output or through a message where that output shows only true or false
rule_id: TST-18
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['\bassert(True|False|That)\(\s*[^,()]*(==|!=|[.]equals\(|<=?|>=?|\bin\b|\bis\b)|\bexpect\([^)]*(===|!==|==|!=|<=?|>=?)[^)]*\)[.](not[.])?(toBe|toEqual|toStrictEqual)\(\s*(true|false)\s*\)|^\s*assert\s+.+\s(and|or)\s.+|\bassert!\s*\(\s*[^,;]*(==|!=|<|>)[^,;]*\)\s*;', '\b(it|test|describe)([.]each\(.*?\))?\s*\(\s*([\x22\x27\x60])\s*\3|\bt[.]Run\(\s*(fmt[.]Sprint\w*\(\s*[\x22\x60][^\x22\x60]*%d[\x22\x60]\s*,\s*\w+\s*\)|strconv[.]Itoa\(\s*\w+\s*\)|[\x22\x60]{2})|\bt[.](Error|Fatal)f?\(\s*[\x22\x60][^\x22\x60%]*[\x22\x60]\s*\)|\b(Errorf|Fatalf|fail|assert\w*|expect)\(.*(?i:case|test|row|index)\s*#?\s*(%d|\$?\{(i|j|k|n|idx|index)\})']
scope: file
check_kind: mechanical
severity_default: minor
---

# A failing test's report names the test and its case and shows the actual and the expected value, through the assertion's own output or through a message where that output shows only true or false

## Thesis
Every test and subtest carries a non-empty name that no sibling at the same level shares, and a table row is identified in its failure by its name or its inputs rather than by its index. A failing assertion reports the value the code produced and the expected value and, where the test's or row's name does not already state them, the inputs when they are short or, when they are large or opaque, a case name that describes what is being tested. An equality or comparison assertion whose framework prints both compared values on failure reports them without a hand-written message. An assertion whose failure output omits the compared values or the failing condition — a truth check over an equality or comparison, a composite and/or condition, or a check repeated in a loop whose report does not name the iteration — becomes the framework's comparing assertion, is split into one assertion per condition, runs as a subtest named by its inputs, or carries a message that states the produced value and the case. A hand-written message that prints a diff of both values states which side is which.

## Rationale
It should be possible to diagnose a failing test from its report without reading the test's source, which takes what caused the failure, the inputs, the actual result and the expected one. Where the framework does not print the operands, a truth-only assertion reports just that it failed and on which line and a composite condition does not indicate which part failed; a loop of raising assertions without a per-iteration subtest stops at the first failure and does not display the iteration's value. A dedicated equality assertion gives more readable tests and error messages than a truth check over the same comparison. A test that shares its name with another in the same suite makes it harder to know which one failed, an empty name is not informative, and a row reported by its index makes the reader count the table's entries to find the failing case.

## Example
```python
bad:  def test_parse(self):
          for i, (text, want) in enumerate(CASES):
              result = parse(text)
              self.assertTrue(result.ok and result.value == want, f"case {i}")
good: def test_parse(self):
          for text, want in CASES:
              with self.subTest(text=text):
                  result = parse(text)
                  self.assertTrue(result.ok, f"parse returned {result!r}")
                  self.assertEqual(result.value, want)
```

## Limits
Where the framework's own failure output shows the values of the compared subexpressions, or its equality assertion prints both arguments, the bare comparison already reports the values, and a message there is needed only to name a case that the test's or row's name leaves unnamed. The positions on messages divide on whether the assertion's own output already shows the compared values. Tool rules that require a message on every assertion, including the two-argument equality form that prints both values, ask for it to diagnose failures quickly and to document the tests, and a study of practitioners' perception counts undocumented assertions as a test smell; documentation of frameworks whose assertions print the compared values presents the custom message as an optional argument. This rule asks for a message only where the output shows neither the values nor the case and no comparing assertion or subtest supplies them, so a project that enforces a message on every assertion also satisfies it.

## Validator
Grep the hunk for a truth assertion whose argument is an equality, comparison, identity or membership test; an assertion over a condition joined by and/or; a failure report whose message is a constant string or names its case by an index; and a test, subtest or row name that is empty, built from a loop index, or repeated. Open the file to learn the framework's assertion forms and whether their failure output prints the compared values. Compare each new test or subtest name with its siblings at the same level, and trace each loop or table to whether its failure names the row by its name or its inputs. Validator question: **Would a failure of a test in this hunk leave out the produced value, the expected value, or the inputs or case description that the test's or row's name does not state, identify the test or row only by an empty name, a name a sibling shares or an index, or show the produced and expected values in a hand-written diff that does not say which side is which?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-18`, severity minor, `file`, `symbol`, `code` = the assertion, test name or row-naming expression quoted verbatim from the diff, `fix` = the comparing assertion, the split assertions, the subtest or row named by its inputs, or the message that states the produced value and the case, in the file's language, `rationale` = which of the produced value, the expected value or the case the failure report would omit, or that its diff does not say which side is which).

## Source
- google/styleguide go/decisions.md, 'Useful test failures', 'Identify the input', 'Identifying the row' (fetched): "It should be possible to diagnose a test's failure without reading the test's source. Tests should fail with helpful messages detailing: * What caused the failure * What inputs resulted in an error * The actual result * What was expected"; "In most tests, failure messages should include the function inputs if they are short. If the relevant properties of the inputs are not obvious (for example, because the inputs are large or opaque), you should name your test cases with a description of what's being tested and print the description as part of your error message"; "Whichever diff order you use in your failure messages, you should explicitly indicate it"; "Do not use the index of the test in the test table as a substitute for naming your tests or printing the inputs. Nobody wants to go through your test table and count the entries in order to figure out which test case is failing".
- rust-lang/book src/ch11-01-writing-tests.md (fetched): "When the assertions fail, these macros print their arguments using debug formatting"; "This result just indicates that the assertion failed and which line the assertion is on. A more useful failure message would print the value from the `greeting` function"; "add a custom message to be printed with the failure message as optional arguments".
- pytest-dev/pytest doc/en/how-to/assert.rst (fetched): "showing the values of the most common subexpressions including calls, attributes, comparisons, and binary and unary operators".
- python/cpython Doc/library/unittest.rst, 'Distinguishing test iterations using subtests' (fetched): "Without using a subtest, execution would stop after the first failure, and the error would be less easy to diagnose because the value of ``i`` wouldn't be displayed".
- SonarSource java:S5785 (fetched): "Testing equality or nullness with JUnit’s assertTrue() or assertFalse() should be simplified to the corresponding dedicated assertion"; eslint-plugin-jest prefer-equality-matcher (fetched): "more readable tests and error messages if an expectation fails".
- Ruff PT018 pytest-composite-assertion (fetched): "the failure message will not indicate which condition failed".
- eslint-plugin-jest no-identical-title and valid-title (fetched): "it is harder to know which one failed and thus harder to fix"; "An empty title is not informative".
- PMD UnitTestAssertionsShouldIncludeMessage (fetched): "use the three-argument version of `assertEquals()`, not the two-argument version"; SonarSource java:S2698 (fetched): "when either the tests fail and you need to quickly diagnose the problem, or when you need to maintain the tests and the assertion messages work as a sort of documentation".
- ICSME 2020, 'Pizza versus Pinsa: On the Perception and Measurability of Unit Test Code Quality', RQ2, author copy raw.githubusercontent.com/fpalomba/fpalomba.github.io/master/pdf/Conferencs/C56.pdf (fetched): "a survey study that involves 70 practitioners [...] rate 210 test cases"; "the presence of the Assertion Roulette smell, i.e., tests where assertions are not documented, negatively impacts test quality perception (OR = 0.13)".
- Caveat: the odds ratio measures perceived test quality, not defect detection; the other anchors are framework documentation and tool rules.
