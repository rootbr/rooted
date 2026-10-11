---
title: A pure refactoring leaves every existing test's expected results in place and removes or disables no test of code it keeps, changing what a test checks only to follow an interface the refactoring renamed or re-signed
rule_id: CHG-05
domain: change
step: [refactor, test, review]
applies_to: [tests]
triggers: ['signal:test_file', '\b(assert\w*!?|expect|require[.]\w+|should[.]\w+|t[.](Error|Errorf|Fatal|Fatalf))\s*\(|^\s*assert\s', '@(Disabled|Ignore)\b|\b(it|test|describe)[.](skip|todo)\(|\b(xit|xdescribe|xtest)\(|pytest[.]mark[.](skip|xfail)|\bt[.]Skip(Now|f)?\(|#\[ignore\]', '(?i)\b(want|expected|golden|snapshot)\w*\s*[:=]|[.]toMatch(Inline)?Snapshot\(']
scope: base-compare
check_kind: semantic
severity_default: major
---

# A pure refactoring leaves every existing test's expected results in place and removes or disables no test of code it keeps, changing what a test checks only to follow an interface the refactoring renamed or re-signed

## Thesis
In a change presented as a refactoring, every test that passed at the base and calls code the change keeps still runs and passes at the head with the same expected values, golden files and snapshots and an assertion no weaker than before; every edit the change makes to an existing test keeps what the test checks, and the test's calls into production code change only to follow an interface the change renamed or re-signed (such as a renamed routine, class or attribute, an added parameter, a changed return type). A test of a routine or class the change inlines into its callers or deletes leaves with it only when no caller of that code remains or a head test of a remaining caller exercises the cases it checked.

## Rationale
Refactoring aims at reorganizing a program without changing its behaviour, and the tests that already cover the code are what validate that the tested behaviour is unchanged before and after the refactoring. Regression testing makes that check by showing that the software still passes previously passed tests, so that its behaviour is unchanged by an incremental change except insofar as it should change. An expected value, golden file or snapshot edited in the same change, or a test deleted, skipped or weakened there, takes away the comparison with the behaviour before the change, so the passing suite no longer validates that the tested behaviour is unchanged. Refactoring operations differ in scope and so in their potential impact on test code: in a study of 615,196 test cases, the vast majority of refactoring operations did not or very seldom induced test breaks, renaming an attribute or a class had a higher chance of breaking test suites, and adding a parameter or changing a return type often required additional lines of change to fix the tests they broke. These kinds, which change a name or a signature that tests call, are where an edit to an existing test is to be expected.

## Example
```python
bad:  @pytest.mark.skip(reason="fails after refactor")
      def test_total_with_discount():
          assert total([2, 3], discount=1) == 4
      def test_total():
          expected = 6  # base: assert total([2, 3]) == 5
          assert order_total([2, 3]) == expected
good: def test_total_with_discount():
          assert order_total([2, 3], discount=1) == 4
      def test_total():
          assert order_total([2, 3]) == 5  # renamed call, same expectation
```

## Limits
Adding tests is within the rule: code that tests do not yet cover gets those tests in a change submitted before the refactoring, so that they validate the tested behaviour unchanged before and after it. A change that adds or changes logic, such as a feature or a bug fix, comes with new or updated tests for the new behaviour; the rule reaches a change presented as a refactoring, and one that needs an updated expected result has caused an effect on what that test observes and is reviewed as a behaviour change. Refactoring the test code itself, for example introducing helper functions, while every expected result and assertion stays is within the rule; as an independent test modification it can also go into a change of its own. Where the refactoring changed a return type, an expected value rewritten into the new type with the same content follows the interface; an expected value with different content does not. A test that calls a routine or class the refactoring inlines into its callers or deletes leaves with it when no caller of that code remains or a head test of a remaining caller exercises the cases it checked; a removal that leaves those cases with no head test takes behaviour the change keeps out of the suite.

## Validator
Read the change's title, description and production hunks, and continue only when the change is presented as a refactoring (a rename, extract, move, inline or restructuring, or a stated "no behaviour change"). Grep the test hunks for assertion lines, expected-value, golden and snapshot assignments, skip and disable markers, and removed test functions, and list the golden and snapshot files the diff rewrites. Open each touched test file at the base and at the head, pair every test that existed at the base with its head version, and for a base test with no head version check whether the production hunks inline or delete the routine or class it calls and, where a caller of that code remains, whether a head test of that caller exercises the cases the removed test checked. For each changed assertion, trace whether the edit only follows a production interface the same change renamed or re-signed (a new name, an added argument, the same content in a changed return type) or instead changes the expected content, weakens the comparison, or takes the test out of the run. Validator question: **Does a change presented as a refactoring delete, skip or disable a test of code the change keeps, remove a test of a routine or class it inlines or deletes while a caller of that code remains and no head test of that caller exercises the removed test's cases, or change an existing test's expected result or weaken its assertion beyond following an interface the change renamed or re-signed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-05`, severity major, `file`, `symbol`, `code` = the changed assertion, expected-value, golden or snapshot line, or the skip marker or removed test, quoted verbatim from the diff, `fix` = the test with its base expectation restored and only the renamed or re-signed call updated, or for a removed test of inlined code its cases checked through a remaining caller, in the file's language, `rationale` = the existing test whose check the change removed and that a refactoring keeps the tests that passed before passing with the same expectations).

## Source
- SWEBOK Guide V3.0, ch. 5 Software Maintenance §4.2 Reengineering (fetched): "Refactoring is a reengineering technique that aims at reorganizing a program without changing its behavior."
- SWEBOK Guide V3.0, ch. 4 Software Testing §2.2.5 Regression Testing, citing ISO/IEC/IEEE 24765 (fetched): "selective retesting of a system or component to verify that modifications have not caused unintended effects"; "In practice, the approach is to show that software still passes previously passed tests in a test suite ... the purpose of regression testing is to show that software behavior is unchanged by incremental changes to the software, except insofar as it should."
- google/eng-practices, review/developer/small-cls.md §"Keep related test code in the same CL" (fetched): "A CL that adds or changes logic should be accompanied by new or updated tests for the new behavior. Pure refactoring CLs (that aren't intended to change behavior) should also be covered by tests"; "submitting test CLs *before* submitting refactoring CLs can validate that the tested behavior is unchanged before and after the refactoring"; independent test modifications include "Refactoring the test code (e.g. introduce helper functions)."
- DOI 10.1109/ICSME52107.2021.00022, ICSME 2021, abstract (fetched): "many specific and diverse refactoring operations, which have different scopes and thus a different potential impact on both the production and the test code"; "a large-scale quantitative study complemented by a qualitative analysis involving 615,196 test cases"; "while the vast majority of refactoring operations do not or very seldom induce test breaks, some specific refactoring types (e.g., “RENAME Attribute” and “RENAME Class”) have a higher chance of breaking test suites. Meanwhile, “ADD Parameter” and “CHANGE Return Type” refactoring operations often require additional lines of changes to fix the test suite they break". Caveat: the study's replication package builds Java projects with Maven; the per-kind breakage figures come from that ecosystem, while the rule itself rests on the definition of refactoring and regression testing.
