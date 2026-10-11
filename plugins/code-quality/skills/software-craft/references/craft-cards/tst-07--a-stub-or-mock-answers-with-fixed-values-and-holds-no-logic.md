---
title: A stub or mock defined in a test answers with fixed values and does not re-implement the logic of the dependency it replaces
rule_id: TST-07
domain: tests
step: [test]
applies_to: [tests]
triggers: ['[.]thenAnswer\(|\bdoAnswer\(|\bwillAnswer\(|[.]mockImplementation\w*\(|[.]callsFake\(', '\bside_effect\s*=\s*(lambda\b|\w+)|\b(setattr|patch|patch[.]object)\(.*\blambda\b', '[.]DoAndReturn\(|[.]Run(AndReturn)?\(\s*func\b|[.]Return\(\s*func\b|[.]return(ing|_once)\(\s*(move\s*)?\|', '\b(jest|vi)[.]fn\(\s*(async\s*)?(\(|\w+\s*=>|function\b)', '(?i)\b(class|struct|type|impl)\s+\w*(stub|mock)']
scope: file
check_kind: semantic
severity_default: minor
---

# A stub or mock defined in a test answers with fixed values and does not re-implement the logic of the dependency it replaces

## Thesis
A stub or mock defined in a test answers with fixed values that the test writes out where it uses them: a return value, a sequence of values for successive calls, a fixed error, or one fixed answer for each specific argument value the test matches. Where the double's answer is given as a function, the body returns, throws or passes on such fixed values, or hands an argument back unchanged, and it selects among fixed answers, if at all, by exact argument value. It does not branch on a property or pattern of its arguments, parse them or calculate from them to choose a result, which would recreate the behaviour of the component the double replaces.

## Rationale
Logic inside a double is code that no test checks. It restates part of the replaced component's behaviour inside the test, so a pass or a failure may come from the double's logic and not from the code under test: the test exercises its own infrastructure rather than its target. The reader, too, has to run the double's branches in their head to learn what the code under test received. Fixed values injected right before they are used keep every answer visible at the point of use and keep the double's behaviour obvious, which is the property the rule restores. An urge to add real behaviour to a double, such as a double that must interpret an incoming message or parse its input to decide what to return, usually signals a misplaced responsibility: the interpretation belongs to the code under test or to a collaborator with tests of its own. Recording the arguments a double receives, and choosing among fixed answers by exact argument value, are not logic in this sense: they select values the test wrote out rather than compute new ones.

## Example
```go
bad:  pricer.EXPECT().Price(gomock.Any()).AnyTimes().DoAndReturn(func(sku string) int {
          if strings.HasPrefix(sku, "SALE-") { return 80 }
          return 100
      })
good: pricer.EXPECT().Price("SALE-1").Return(80).AnyTimes()
      pricer.EXPECT().Price("STD-1").Return(100).AnyTimes()
```

## Limits
- An answer function whose body is a fixed answer fits the rule: it returns a constant or the receiver of a chained call, throws a fixed error, passes fixed values to a callback the caller supplied, or hands an argument back unchanged. Some calls need the function form, such as a result delivered through a callback or a different fixed answer on each successive call, and the rule allows it.
- Selecting among fixed answers by exact argument value, through the framework's argument matching, an equality test or a small table the test writes out, is argument matching in function form, not logic.
- A fake, a working lightweight implementation of the whole interface that keeps state across calls (an in-memory store written once and shared by many tests), is a different kind of double: its logic is its purpose, and it is outside this rule. A record of the calls a double received, kept for the test to inspect, is not such state.
- An expected value computed inside an assertion is outside this rule, which reads the double only.
- A documented project tolerance that names the double and the reason its answers must be computed rejects the finding.

## Validator
Find in the hunk each double whose answer is given as a function: an answer, implementation or callback function passed to a double's setup, an inline function patched in place of a real one, or a method of a hand-written stub or mock type. Open the file and read each such function body and each method of the stub or mock type. Mark a body that branches on a property or pattern of its arguments (a prefix, a range, a field, a type), parses or transforms them, or calculates from them to choose its result; pass a body that returns a constant, a value from a fixed sequence, the receiver or an argument unchanged, throws a fixed error, passes fixed values to a supplied callback, records its arguments, or selects a fixed answer by exact argument value. Classify a hand-written type that implements the whole interface with state kept across calls, other than a record of the calls it received, as a fake and skip it. Validator question: **Does a stub or mock defined in this test compute its answer from its arguments, by branching on a property or pattern of them, parsing them or calculating from them, and so recreate behaviour of the component it replaces?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-07`, severity minor, `file`, `symbol`, `code` = the double's setup line and the branching, parsing or calculating statement of its answer function, quoted verbatim from the diff, `fix` = the double rewritten to answer with fixed values, a per-call sequence or one fixed answer per matched argument value, allowing each call the test makes as many times as the original double allowed it, in the file's language, `rationale` = names the logic the double computes, the behaviour of the replaced component it recreates, and that no test checks that logic).

## Source
- Jest documentation, "Mock Functions" § Mock Return Values, of code in a functional continuation-passing style: "Code written in this style helps avoid the need for complicated stubs that recreate the behavior of the real component they're standing in for, in favor of injecting values directly into the test right before they're used"; of a mock function configured on any dependent component: "try to avoid the temptation to implement logic inside of any function that's not directly being tested." § Mock Implementations: "there are cases where it's useful to go beyond the ability to specify return values and full-on replace the implementation of a mock function" (fetched)
- Mockito `Mockito` class Javadoc § 11 Stubbing with callbacks: "We recommend simply stubbing with thenReturn() or thenThrow(), which should be enough to test/test-drive any clean and simple code." (fetched)
- Mockito project wiki, "How to write good tests" § Avoid coding a tautology: "Generally speaking one does not want to duplicate the logic between tests and code." (fetched)
- DOI 10.1145/1028664.1028765, § 4.6 Don't add behaviour: "Mock objects are still stubs and should not add any additional complexity to the test environment, their behaviour should be obvious"; "an urge to start adding real behaviour to a mock object is usually a symptom of misplaced responsibilities"; "This introduces a risk of testing the test infrastructure rather than the target code"; its example sets one expectation per key: `.method("retrieve").with(eq(KEY1)) .willReturn(VALUE1)` (fetched from the authors' version, jmock-developers/jmock-website `content/oopsla2004.pdf`; the DOI relayed)
- Caveat: the evidence is framework documentation and one experience report; no study measures the cost of logic inside doubles, and the wiki item states the principle for test code in general.
