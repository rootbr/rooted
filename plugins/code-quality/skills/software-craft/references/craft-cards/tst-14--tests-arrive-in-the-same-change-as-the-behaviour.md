---
title: A change that adds or changes production behaviour, a bug fix included, carries the new or updated tests for that behaviour in the same change unless it handles an emergency
rule_id: TST-14
domain: tests
step: [implement, test, review]
applies_to: [universal]
triggers: ['\b(if|elif|else|switch|match|case|when|for|foreach|while|loop|return|throw|raise)\b', '\b(def|fn|func|function)\s+\w+\s*[(<]|\b(public|protected|private|internal|static)\s+[\w<>\[\],.? ]+\s+\w+\s*\(', '(?i)\b(fix(es|ed)?|bug|regression|hotfix)\b', 'signal:added_file']
scope: callers
check_kind: semantic
severity_default: major
---

# A change that adds or changes production behaviour, a bug fix included, carries the new or updated tests for that behaviour in the same change unless it handles an emergency

## Thesis
In general, a change that adds or changes production logic, a bug fix included, carries in that same change the new or updated tests for the new behaviour, whichever of test and code was written first; the one exception is a change that handles an emergency.

## Rationale
Construction testing exists to reduce the gap between the time a fault is inserted into the code and the time it is detected, which reduces the cost of fixing it; its test cases are written after the code in some instances and may be created before it in others. Testing code during development can expose bugs that find their way in as changes are made. Proper tests in the change verify that it works as expected, and review asks for unit, integration or end-to-end tests as appropriate for the change. In case studies of four industrial teams that adopted test-driven development, in which the engineer cycles minute by minute between writing failing unit tests and writing the code that passes them, the pre-release defect density of the four products was between 40% and 90% lower than that of similar projects that did not use the practice, and the teams subjectively experienced a 15–35% increase in initial development time. In the one comparison group whose unit testing the study describes, unit testing followed as a post-coding activity and the process was not formal and not disciplined, so that comparison varies test order and testing discipline together.

## Example
```java
bad:  // bug fix for the fee limit; the change edits Account.java only
      public int fee(int amount) { return amount >= 100 ? 2 : 1; }
good: public int fee(int amount) { return amount >= 100 ? 2 : 1; }
      // the same change adds AccountTest.java
      @Test void feeAtLimitIsTwo() { assertEquals(2, new Account().fee(100)); }
```

## Limits
A pure refactoring, one not intended to change behaviour, lies outside this rule's question; review guidance still expects it to be covered by tests, ideally ones that already exist, otherwise ones the change adds. Independent test work may land first in a change of its own: new tests that validate code already submitted, refactoring of test code, and larger test framework code such as an integration test. A change that handles an emergency is exempt. The rule takes no side on whether the test or the code is written first, since either order puts the tests in the change; in a crossover replication with 21 graduate students, test-driven and test-last development showed no significant difference in testing effort (p = .27), external code quality (p = .82) or productivity (p = .83). Presence is the whole of this rule; review separately makes sure that the tests in the change are correct, sensible and useful.

## Validator
Grep the hunk for added or changed branches, returns, throws and routine signatures in production files, and the change description for fix, bug or regression. List the files of the change and pick out its tests: test files by the project's test directory and naming convention, and test functions or test modules kept inside production files, which count as tests, not as production routines. At scope callers, open each changed production routine and its callers, and trace from every added or modified test to the routines it calls. Pass the change when a test it adds or modifies reaches the changed behaviour, when it is a pure refactoring, when it adds or refactors only tests, or when its description says it handles an emergency. Validator question: **Does the change add or change production behaviour that no test added or modified in the same change exercises, while the change is neither a pure refactoring nor one that handles an emergency?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-14`, severity major, `file`, `symbol`, `code` = the added or changed production line that carries the new behaviour, verbatim from the diff, `fix` = a test in the file's language, added to the same change, that exercises the new or changed behaviour, `rationale` = names the behaviour the change adds or alters and states that no test in the change exercises it).
