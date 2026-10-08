---
title: Every test asserts, verifies or declares the failure it expects, and each of its assertions is complete and has two sides that can differ
rule_id: TST-24
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['@(Test|ParameterizedTest|RepeatedTest)\b|#\[(\w+::)*test\]|^\s*(async\s+)?def\s+test\w*\s*\(|^\s*func\s+Test\w*\s*\(\s*\w+\s+\*testing[.]T\s*\)|\b(it|test)([.](only|concurrent|each\(.*?\)))?\s*\(\s*[\x22\x27\x60]', '\b(assert\w*|require|expect|check\w*)([.]\w+)?\s*!?\(\s*(?:t\s*,\s*)?([A-Za-z_][\w.]*(?:\(\))?)\s*,\s*\3\s*[,)]|\b(assertThat|expect)\(\s*([A-Za-z_][\w.]*)\s*\)[.](\w+[.])*(isEqualTo|isSameAs|toBe|toEqual|toStrictEqual)\(\s*\5\s*\)|^\s*assert\s+([A-Za-z_][\w.\[\]]*)\s*(==|is)\s*\8\s*(,|#|$)', '^\s*(assertThat|assertWithMessage|expect)\((?:[^()]|\([^()]*\))*\)\s*;?\s*$|^\s*verify\(\s*\w+\s*\)\s*;\s*$|[.](to[A-Z]\w*|resolves|rejects)\s*;?\s*$']
scope: file
check_kind: semantic
severity_default: major
---

# Every test asserts, verifies or declares the failure it expects, and each of its assertions is complete and has two sides that can differ

## Thesis
Every test contains, in its body or in a helper it calls, at least one assertion, verification or declaration of the failure it expects. Each assertion is complete, reaching its matcher, verb or comparison rather than stopping at its subject, and its two sides can differ: it never compares a value with itself, and never two values whose outcome the source already fixes. Such an assertion can fail, which is what lets it detect when the code under test does not behave as expected.

## Rationale
A test case without an assertion ensures only that no exception is thrown; beyond basic runnability it ensures nothing about the behaviour of the code under test, and the runner shows it as passing whenever its statements raise no exception. An assertion that names its subject and calls no matcher, or a verification that names a collaborator and no call, actually checks nothing: the test passes whatever value the subject holds. An assertion whose expected and actual sides are the same expression, or two literals whose outcome the source already fixes, is always true or always false, and an assertion that fails or succeeds all the time does not achieve what assertions are meant for, detecting when code behaves as expected; an assertion comparing an object with itself is more likely a bug from carelessness. These defects are common: of 656 open-source Android apps with test files, 635 showed at least one test smell; test methods with no single assertion and no expected-exception declaration appeared in 47.09% of those 635 apps and in 34.38% of the test files, and assertions whose expected and actual parameters are the same in 12.91% of those apps and 3.87% of the files. Developers surveyed about such methods confirmed that the missing assertions were mistakes, and called the always-true or always-false assertions not needed, bad style and code that should probably be removed. The remedy is to assert on something that could fail.

## Example
```typescript
bad:  it('totals the order', () => {
        const total = sumOrder(order);
        expect(total).toEqual(total);
        expect(total > 0);
      });
good: it('totals the order', () => {
        expect(sumOrder(order)).toEqual(42);
      });
```

## Limits
In a test that validates an equals or hash method, comparing an object with itself is legitimate. A project's own assertion helper counts as an assertion, and an assertion subject that a helper returns is complete once the calling test applies the matcher to it. A test the framework skips, marked disabled or ignored, is not executed and stays outside the rule. Most surveyed developers favour having an assertion statement in a test method, with minor exceptions in edge cases. For always-true or always-false assertions, one respondent described a canary test written as a sanity test or for warming up, which can be removed after serving its purpose, and a few said the code is required for their tests to execute, possibly to support an extreme edge case. These respondents' edge cases are context, not exemptions: they name no condition a reviewer can check, and the Validator flags such a test.

## Validator
Grep the hunk for added or changed test declarations and for assertion lines that compare an expression with itself or end at their subject. Open the file and, for each such test, trace its body and every helper it calls for an assertion, a verification or a declaration of the failure it expects; count a project helper that asserts as an assertion. For each assertion, check that it reaches a matcher, verb or comparison, in place or in the test that receives the subject a helper returns, and that its two sides can differ: not the same variable or object on both sides, and not two values the source already fixes; two separate calls that can return different values are different sides. Skip tests the framework skips and equality or hash tests that compare an object with itself. Validator question: **Does a test in the hunk lack any assertion, verification and expected-failure declaration, or hold an assertion that stops at its subject or compares two sides that cannot differ?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-24`, severity major, `file`, `symbol`, `code` = the test's declaration line together with the incomplete or self-comparing assertion, or the declaration line alone when the test has no assertion, `fix` = an assertion in the file's language that compares the value the code under test produced with an independent expected value, or a declaration of the expected failure, `rationale` = which defect applies, a missing assertion, an incomplete assertion or a comparison that cannot differ, and that the test therefore cannot detect a wrong result from the code under test).

## Source
- SonarSource java:S2699 'Tests should include assertions' (fetched): "A test case without assertions ensures only that no exceptions are thrown. Beyond basic runnability, it ensures nothing about the behavior of the code under test."; "Tests annotated with @Disabled (JUnit 5) or @Ignore (JUnit 4) are excluded from this rule, as they are not executed by the test framework."; "as new or custom assertion frameworks may be used, the rule can be parametrized to define specific methods that will also be considered as assertions"
- PMD 7 java bestpractices UnitTestShouldIncludeAssert (fetched): "Unit tests should include at least one assertion."
- eslint-plugin-jest expect-expect (fetched): "This rule triggers when there is no call made to `expect` in a test, to prevent users from forgetting to add assertions."
- SonarSource java:S2970 'Assertions should be complete' (fetched): "In such cases, what is intended to be a test doesn’t actually verify anything"; "nothing is actually checked, the test passes whether \"result\" is true or false"; "Variable assignments and return statements are skipped to allow helper methods."
- eslint-plugin-jest valid-expect (fetched): "Ensure `expect()` is called with a single argument and there is an actual expectation made."
- SonarSource java:S5863 'Assertions should not compare an object to itself' (fetched): "Assertions comparing an object to itself are more likely to be bugs due to developer’s carelessness."; "In a unit test validating the equals(...) and hashCode() methods, it’s legitimate to compare an object to itself."
- SonarSource python:S5914 'Assertions should not fail or succeed unconditionally' (fetched): "Assertions are meant to detect when code behaves as expected. An assertion which fails or succeeds all the time does not achieve this."
- Pylint W1503 redundant-unittest-assert (fetched): "comparing two literals has an outcome that is already fixed by the source. The solution is to test something that could fail"
- testifylint useless-assert (fetched): "The checker guards against assertion of the same variable"
- tsDetect test smell catalog, tool paper DOI 10.1145/3368089.3417921 (catalog fetched): Redundant Assertion, "assertion statements that are either always true or always false", detected when "the expected and actual parameters are the same"; Unknown Test, "JUnit will show the test method as passing if the statements within the test method did not result in an exception", detected as "A test method that does not contain a single assertion statement and @Test(expected) annotation parameter."
- 'On the Distribution of Test Smells in Open Source Android Applications: An Exploratory Study', CASCON 2019 preprint, TestSmells.github.io assets/publications/CASCON2019_TechnicalPaper.pdf (fetched): data-collection table, "Apps containing test files 656"; §4.1, "Out of the 656 apps, which contained unit tests, only 21 apps (approximately 3%) did not exhibit any test smells" (the Table 3 app shares are of the remaining 635 apps: 47.09% = 299/635, 12.91% = 82/635); Table 3, "Unknown Test 47.09% 34.38%", "Redundant Assertion 12.91% 3.87%" (apps, files); survey, "The respondents confirmed that the missing assertions in their methods were mistakes"; "such code “is not needed”, ”bad style” and “should probably be removed”"; "a “canary test” [...] “as a sanity test, or for purposes of warming up”. These tests can be removed after serving their purpose"; "the code is required for their tests to execute (possibly to support an extreme edge case)"
- Rust official documentation, src/ch11-01-writing-tests.md, 'Checking for Panics with should_panic' (fetched): "The test passes if the code inside the function panics; the test fails if the code inside the function doesn’t panic."
- Caveat: the prevalence and survey figures come from JUnit tests in open-source Android apps; the tool rules each cover one framework family, and together with the Rust documentation they span JVM, Python, JavaScript and TypeScript, Go and Rust test code.
