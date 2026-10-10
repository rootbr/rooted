---
title: A test checks an effect it can read as a returned value or as state, through the code under test or a usable real or fake implementation, by asserting that value or state and not only by verifying a call on a double
rule_id: TST-53
domain: tests
step: [test]
applies_to: [tests]
triggers: ['\b(td[.])?verify\(|[.]assert_(called|any_call|has_calls|awaited)\w*\(|[.]toHaveBeen(Last|Nth)?Called\w*\(|[.]toBeCalled\w*\(|\bsinon[.]assert[.]called\w*\(|[.]AssertCalled\(|[.]AssertExpectations\(|[.]Received\(|[.]EXPECT\(\)|\bexpect_\w+\(\)[.]times\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# A test checks an effect it can read as a returned value or as state, through the code under test or a usable real or fake implementation, by asserting that value or state and not only by verifying a call on a double

## Thesis
When an effect of the code under test can be read as a value it returns, as state it exposes through its own API, or as state in a dependency for which the test can use the real implementation or an existing fake, the test asserts that value or state rather than relying on a verified call on a double alone. A call verification is the check for an effect that only the call shows: a side effect on a dependency with no usable real implementation or fake, or the presence, absence or number of calls that shows which execution path ran.

## Rationale
A call verification asserts that the code under test has a side effect, as opposed to relying on what the dependency returns, and it is needed only when the depended-on function is invoked for that side effect. Calls to a mocking API that set up and check doubles change with the production code: in a manual analysis of a sample of more than 300 such changed calls in four software systems, 172 (51%) were induced by the production code, through changes to the production class API or to the internal implementation of the class, and 164 (49%) by improvements to the test code. Asserting every invocation on a double, as some test generators do, produces an excessive number of assertions and fragile tests. A function that returns a useful value without a side effect is easier to understand, test and maintain, and where a mocking library is used to let side-effect-heavy code proliferate, refactoring each dependency to return values is almost always the better design.

## Example
```typescript
bad:  const store = { get: jest.fn(), put: jest.fn() };
      new Counter(store).increment("k");
      expect(store.put).toHaveBeenCalledWith("k", 1);
good: const counter = new Counter(new MemoryStore());
      counter.increment("k");
      expect(counter.value("k")).toBe(1);
```

## Limits
Verifying the call is the check when the relevant data is neither returned by the code under test nor accessible through any getter of the code under test or of a usable real or fake implementation of the dependency, so that a test assertion cannot check it and the operation shows as an interaction with a dependency; a recording double serves where the routine under test returns nothing to make assertions on and the dependency it calls has no usable real implementation or existing fake whose state shows the effect. It is also the check for a call made only on some execution paths, where the presence, absence or number of calls shows the path taken, as in a retry that must download exactly twice. A verification kept in the same test beside an assertion on the returned value or readable state that shows the same effect is outside the rule: in 240 test cases that used both kinds of assertion, 782 of the 1,557 (50%) injected faults that mock assertions detected went undetected by the test assertions, and the two sets of detected faults had a Jaccard similarity of 32%. A call that the same test stubs for its return value is outside the rule as well, because when the stubbing is needed for the test to pass, a verification of the same invocation is redundant. The rule is contested. One side verifies an invocation only when there is no other way to assert that the code under test does what it should, and finds a suite with lots of verification calls worrisome. The other side treats interactions between objects as the most essential part of object-oriented programming and recommends mock assertions for program behaviours that traditional test assertions cannot observe. The condition both sides state separates the cases: whether the effect can be read without the call record, through a returned value or through state the test can reach.

## Validator
Grep the hunk for a call verification on a double: a verify call, an assert-called or have-been-called matcher, a received-call check or a call expectation. For each, open the test and the code under test at its callers and name the effect the verified call stands for. Look for a value the code under test returns, state it exposes through its own API, and a real implementation or an existing fake of the doubled dependency in the project, from which that effect could be read, and check whether the test asserts that value or state. Pass a verified call that the same test stubs for its return value, a call whose data is neither returned nor reachable through a getter or a usable real or fake implementation, and a check of the presence, absence or number of calls that shows the execution path. Validator question: **Does the test check an effect of the code under test only by verifying a call on a double, while that effect can be read as a returned value, through the code under test's own API, or from a real implementation or an existing fake of that dependency?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-53`, severity minor, `file`, `symbol`, `code` = the call verification quoted verbatim from the diff, `fix` = an assertion on the returned value or on the state read through the code under test or a real or fake dependency, in the file's language, `rationale` = the effect the verified call stands for and the value or state that shows it).
