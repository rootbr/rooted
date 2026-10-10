---
title: A test verifies only calls a double receives for their side effects, never a call it also stubs to return a value for the same arguments
rule_id: TST-09
domain: tests
step: [test]
applies_to: [tests]
triggers: ['\b(co)?([Vv]erify)\s*[({]|[.](should)[(]', '[.]assert_(called|any_call|has_calls|not_called|awaited|any_await|has_awaits|not_awaited)\w*[(]|[.](called|(call|await)_(count|args(_list)?)|mock_calls)\b', '[.]toHaveBeen(Last|Nth)?(Called)\w*[(]|[.]to(BeCalled)\w*[(]|\bassert[.](called)\w*[(]|[.]been[.](called)\w*|[.]called(Once|Twice|Thrice|With)\w*|[.](callCount)\b|[.]mock[.](calls)\b', '[.]Assert(Called|NumberOfCalls)[(]|[.][Tt]imes[(]|[.]Once[(][)]|[.]Received[(]']
scope: callers
check_kind: mechanical
severity_default: minor
---

# A test verifies only calls a double receives for their side effects, never a call it also stubs to return a value for the same arguments

## Thesis
Interaction verification in a test, a check that a double received a call with given arguments, is kept for calls made for their side effect, such as sending a message or saving a record, whose effect no return value and no state the test can read shows. A call made to obtain a value is stubbed to return that value and is not also verified: no check that a call happened targets a call that the same test, or the setup it runs, stubs to return a value with argument matching at least as narrow as the check's.

## Rationale
A stub exists to hand the code under test a value. When the code under test uses that value and the test asserts an outcome that the code under test reaches only with that value, a call that never happens, or happens with arguments the stub does not match, leaves the code under test without the stubbed value, and that assertion fails, often before any verification runs. In that case verifying that the stubbed call happened adds no failure the test lacks: it restates the stub. When the code under test does not use the value, the stub is unnecessary and goes, and the verification, which can be the test's only check that the call happened, stays. Where the code under test uses the value but no assertion shows an outcome reached only with it, the verification can be the only check that the call happened, and it checks that a query ran rather than what its answer changed; an assertion on such an outcome, with a stubbed value that no path skipping the call yields, takes its place. Stubbing modes that fail a test on a stub that is never used, or on a stubbed call made with other arguments, make the same check with no verification line at all. Where a verification defaults to exactly one call, the restatement also fails the test when a refactoring reads the value twice, a change no outcome shows. A call made for its side effect is different: it returns nothing to assert on, or nothing the code under test passes on, and its effect lies outside the code under test, so a double that records the call and an assertion on that record are how a unit test observes the behaviour. Mock assertions do this work in practice: across 4,652 test cases from 11 popular open-source projects written in one language and tested with one mocking framework they are applied mostly to calls that interact with external resources and to calls that show whether a code path was traversed, and they complement ordinary assertions by checking that side effects were produced, validating control flow and checking internal computation results.

## Example
```java
bad:  when(repo.find(id)).thenReturn(order);
      service.ship(id);
      verify(repo).find(id);
      verify(mailer).send(order);
good: when(repo.find(id)).thenReturn(order);
      service.ship(id);
      verify(mailer).send(order);
```

## Limits
- A check of how often or in what order a stubbed call happens, where that is what the test examines, is outside the rule: no call on a short-circuit path, one call behind a cache across repeated requests, a bound on retries. A returned value cannot show a count or an order, and checking which code path ran is a documented use of mock assertions.
- A call made for its side effect that also returns a value reporting whether the effect succeeded, such as a success flag, a count of changed records or a completed future, is outside the rule when the code under test checks that value: the stub keeps the code under test on its success path, a path that skips the call can end in the same outcome, and the verification is the only check that the effect happened.
- A stub that answers any arguments leaves the arguments the code under test computes unchecked; a check of those specific arguments tests a computed value and is outside the rule. Stubbing those specific arguments instead would move the check into the stub.
- A whole-double check that every declared stub or expectation was used, such as a strict stubbing mode or a check-all-expectations call at the end of a test, names no single call and is outside the rule. So is a count written on a stub declaration in a framework whose stubs require a fixed number of calls by default: there the count is part of declaring the stub. A count on a stub declaration is a verification only where the framework's default leaves the number of calls open.
- A documented project tolerance that names the dependency and the reason each of its calls is verified rejects the finding.

## Validator
Grep the added lines for a verification of a call on a double: a verify statement, a called, awaited, called-with or called-times assertion, a read of a call count, or a count written on an expectation. Open the file and find the test that holds each hit and the setup it runs, such as a before-each routine, a fixture or a helper that builds the double. Look there for a stub of the same method on the same double that returns a value: a fixed return value, a sequence of values, a resolved promise or future, an answer. Compare the arguments: the stub matches at least as narrowly as the check when it names the same values, or when the check tests no arguments or only any-value matchers. Skip the hit when no such stub exists; when the stubbed method is called for its side effect, such as sending, writing, saving, deleting or publishing, and the stubbed value only reports whether that effect succeeded; when the stub answers any arguments and the check tests specific ones; when the check tests zero calls, a bound, an order, or one call across repeated requests the test makes on purpose; when the hit is a whole-double check that every stub was used; and when the count sits on a stub declaration in a framework whose stubs require a fixed number of calls by default. Validator question: **Does the test verify that a call on a double happened, once or at least once, while the same test or its setup stubs that call to return a value with argument matching at least as narrow as the verification's?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-09`, severity minor, `file`, `symbol`, `code` = the verification line quoted verbatim from the diff, with the stub line of the same call it restates, `fix` = the test without that verification, with any check in the test that the double received no other calls set to ignore stubbed calls where that check counts them as unverified, plus an assertion on an outcome reached only with the stubbed value, choosing a stubbed value that no path skipping the call yields, where no assertion of the test observes one, or, where the code under test does not use the stubbed value, without the stub and with the verification kept, in the file's language, `rationale` = names the stubbed call and the assertion that fails when the call is missing or takes other arguments, the test's own or the one the fix adds).
