---
title: Every test asserts, verifies or declares the failure it expects, and each of its assertions is complete and has two sides that can differ
rule_id: TST-24
domain: tests
step: [test]
applies_to: [tests]
triggers: ['@(Test|ParameterizedTest|RepeatedTest)\b|#\[(\w+::)*test\]|^\s*(async\s+)?def\s+test\w*\s*\(|^\s*func\s+Test\w*\s*\(\s*\w+\s+\*testing[.]T\s*\)|\b(it|test)([.](only|concurrent|each\(.*?\)))?\s*\(\s*[\x22\x27\x60]', '\b(assert\w*|require|expect|check\w*)([.]\w+)?\s*!?\(\s*(?:t\s*,\s*)?([A-Za-z_][\w.]*(?:\(\))?)\s*,\s*\3\s*[,)]|\b(assertThat|expect)\(\s*([A-Za-z_][\w.]*)\s*\)[.](\w+[.])*(isEqualTo|isSameAs|toBe|toEqual|toStrictEqual)\(\s*\5\s*\)|^\s*assert\s+([A-Za-z_][\w.\[\]]*)\s*(==|is)\s*\8\s*(,|#|$)', '^\s*(assertThat|assertWithMessage|expect)\((?:[^()]|\([^()]*\))*\)\s*;?\s*$|^\s*verify\(\s*\w+\s*\)\s*;\s*$|[.](to[A-Z]\w*|resolves|rejects)\s*;?\s*$']
scope: callers
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
In a test that validates an equals or hash method, comparing an object with itself is legitimate. A project's own assertion helper counts as an assertion, and an assertion subject that a helper returns is complete once the calling test applies the matcher to it. A test the framework skips, marked disabled or ignored, is not executed and stays outside the rule. A property or fuzz target whose check is that the unit does not crash on generated inputs makes that check through the framework, which fails the case on an uncaught exception or panic, and is outside the rule as well. Most surveyed developers favour having an assertion statement in a test method, with minor exceptions in edge cases. For always-true or always-false assertions, one respondent described a canary test written as a sanity test or for warming up, which can be removed after serving its purpose, and a few said the code is required for their tests to execute, possibly to support an extreme edge case. These respondents' edge cases are context, not exemptions: they name no condition a reviewer can check, and the Validator flags such a test.

## Validator
Grep the hunk for added or changed test declarations and for assertion lines that compare an expression with itself or end at their subject. Open the file and, for each such test, trace its body and every helper it calls for an assertion, a verification or a declaration of the failure it expects; count a project helper that asserts as an assertion. For each assertion, check that it reaches a matcher, verb or comparison, in place or in the test that receives the subject a helper returns, and that its two sides can differ: not the same variable or object on both sides, and not two values the source already fixes; two separate calls that can return different values are different sides. Skip tests the framework skips, equality or hash tests that compare an object with itself, and a property or fuzz target whose check is that the call completes without an uncaught error. Validator question: **Does a test in the hunk lack any assertion, verification and expected-failure declaration, or hold an assertion that stops at its subject or compares two sides that cannot differ?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-24`, severity major, `file`, `symbol`, `code` = the test's declaration line together with the incomplete or self-comparing assertion, or the declaration line alone when the test has no assertion, `fix` = an assertion in the file's language that compares the value the code under test produced with an independent expected value, or a declaration of the expected failure, `rationale` = which defect applies, a missing assertion, an incomplete assertion or a comparison that cannot differ, and that the test therefore cannot detect a wrong result from the code under test).
