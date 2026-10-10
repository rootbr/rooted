---
title: An assertion checks only a condition whose failure means a bug in the program, never a failure expected in normal operation such as invalid user input, a missing file or a refused request
rule_id: API-04
domain: interface
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['^\s*assert\b(?![!._])|\b(debug_)?assert(_eq|_ne)?!\s*\(|(?<![\w.])(console[.]assert|assert[.](ok|equal|strictEqual|notEqual|notStrictEqual|deepStrictEqual|match)|invariant)\s*\(']
scope: file
check_kind: semantic
severity_default: major
---

# An assertion checks only a condition whose failure means a bug in the program, never a failure expected in normal operation such as invalid user input, a missing file or a refused request

## Thesis
An assertion states a condition that holds unless the code itself is broken, such as a postcondition, an invariant of a type, an internal precondition of a non-public routine, or a branch that cannot be reached. A condition that can be false while the program works correctly is tested with ordinary control flow and reported as an error the caller can handle, rather than asserted: data from a user, a file, the network or another service that no earlier code has validated; a file that does not exist; a lookup that can come back empty; a remote status such as a rate limit. Which kind a condition is depends on where it is checked, not on the condition itself: the same check on outside data is ordinary control flow where the data arrives, and may be asserted past the point where earlier code has validated that data.

## Rationale
A failed assertion says that the code containing it is broken, so it is the wrong check for a failure that happens while the program works correctly. Assertions are normally compiled into the code during development and compiled out later so that they do not degrade performance: some runtimes drop every assertion when optimization is requested, a common practice in production environments; some leave assertions disabled until a flag enables them; some check the plain form in every build and offer a debug-only form that an optimized build does not execute. Where the assertion is dropped, the check on the outside data goes with it: projects that enforced interface constraints with assertions had protections removed this way, and a check that is not executed does not stop the program from continuing with the condition violated. Where the assertion runs, it reports the failure as a bug in the program instead of as an error that marks failure as an expected possibility the calling code must decide how to handle. Where a failed assertion stops the program, an attacker who can make the condition false can trigger an application exit or other behaviour more severe than necessary, and a bad server-side rollout can bring down the client. Proper handling of the failure as an error keeps servers operating instead of crashing after a non-fatal error, and proper reporting of it as an error makes it direct and to the point, sparing the programmer a large crash trace. Each assertion failure then reports a bug, to be triaged and fixed as one.

## Example
```python
bad:  port = find_open_port(minimum)
      assert port is not None, f"no open port from {minimum}"
      return port
good: port = find_open_port(minimum)
      if port is None:
          raise ConnectionError(f"no open port from {minimum}")
      return port
```

## Limits
Test code is outside the rule: a test assertion checks that the code under test meets its own specification and has almost nothing in common with an assertion in production code. An assertion on data from outside is in place past the point where earlier code has validated that data, since only a defect could then let a bad value through. A check that the caller of a public routine met the routine's documented requirements is a precondition, whose failure is a bug in the caller rather than an expected failure; whether an assertion may carry it, and how an expected failure is reported once it is tested, are judged by their own rules. In the rare case where a failure from outside cannot be recovered from safely, terminating the process is a last resort, done with a stop that is not an assertion so that the crash report is not triaged as a bug in the program.

## Validator
Grep the added lines for an assertion: an assert statement, an assert macro or its debug-only form, a console or module assertion call, an invariant helper. Set aside a hit in a test file or a test routine. For each remaining hit, open the file, name the asserted condition and trace each value in it to where it was produced: a local to the call or read that assigned it, a parameter to the callers in the file. Classify the condition. It is expected in normal operation when a value comes, with no validation on the traced path, from a user or a request, a file or the disk, the network or another service, or a remote status, or when it is the result of a lookup or a search that can come back empty or of an open or a read that can fail. It reveals a bug when it restates what the routine's own code, or validation earlier on the traced path, guarantees: a postcondition, an invariant of a type, an internal precondition of a non-public routine, an unreachable branch. Count an earlier validation only where the file shows it, not where a comment presumes it. Leave a check on a public routine's arguments that states a documented requirement of its callers to its own rule; a routine whose purpose is to read, parse or validate outside data places no such requirement on that data. Validator question: **Does an added assertion outside test code check a condition that can be false while the program works correctly — outside data that no earlier code on the traced path has validated, a missing file, a lookup that can come back empty or a remote status — instead of testing it with ordinary control flow and reporting an error?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: API-04`, severity major, `file`, `symbol`, `code` = the added assertion line quoted verbatim from the diff, `fix` = the same condition tested with ordinary control flow that raises or returns an error naming the failed condition and the offending value, in the file's language, `rationale` = where the asserted value comes from, why the condition can be false while the program works correctly, and what follows where assertions are disabled and where a failed one stops the program).
