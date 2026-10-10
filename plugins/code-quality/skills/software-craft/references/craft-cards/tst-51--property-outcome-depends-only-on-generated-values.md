---
title: A property's pass or fail outcome depends only on the values the framework generates, with any randomness that reaches it drawn from the framework or from a source seeded for each generated case, and with shared, file or database state reset for each case
rule_id: TST-51
domain: tests
step: [test]
applies_to: [tests]
triggers: ['\b(?:Math[.]random|random[.](?:random|randint|choice|shuffle|uniform)|thread_rng|rand::random)\b|\brand[.](?:Intn|Int|Float64|Seed|NewSource)\(|\bnew\s+Random\(\s*\)|\b(?:time[.]Now|Date[.]now|System[.]currentTimeMillis|Instant[.]now|datetime[.]now)\(|^\s*global\s+\w+|\bstatic\s+mut\b']
scope: file
check_kind: semantic
severity_default: major
---

# A property's pass or fail outcome depends only on the values the framework generates, with any randomness that reaches it drawn from the framework or from a source seeded for each generated case, and with shared, file or database state reset for each case

## Thesis
A property or fuzz target is deterministic: run on the same generated input, it gives the same pass or fail outcome and asks the framework for the same sequence of draws. Randomness that reaches the outcome or the draws comes from the framework's own generators, from a source the framework seeds and restores for each generated case, or from a source the body seeds for each case with a constant or a generated value; a source seeded once for the run and shared across inputs carries its state from one input to the next even when its seed is fixed or reported. Its decisions rest on the generated input rather than on global state or on a dependency between generated inputs, and state it writes to shared variables, files or a database is reset between inputs, so that state ends with each call.

## Rationale
A property framework runs the test many times, and one framework's failure database relies on deterministic behaviour to work. A failing input that only flakily reproduces makes debugging substantially harder, and flakiness makes the framework's exploration of the test's behaviour space difficult or impossible; one framework therefore treats flakiness as a fatal error and raises an exception when it detects it, rather than a warning, and it asks for every global pseudo-random generator to be registered with it to prevent flaky tests, seeding each to zero and restoring its previous state around every test case. A fuzzing engine invokes the target in parallel across multiple workers and in nondeterministic order, which is why the target's state should not persist past the end of each call and its behaviour should not depend on global state; being deterministic lets the engine work efficiently and lets new failures and code coverage be easily reproduced. One runner whose random source is left unset seeds it from the current time in nanoseconds. A constant seed makes every run draw the same set of values, and a seed reported with a failed run can be passed back to the runner, making the error easy to reproduce. Beyond property tests, a test that non-deterministically passes or fails on a fixed environment is a serious problem for regression testing; in a study of flaky-test issues across five programming languages, 5 of 13 root causes cover 78.07% of the issues, with concurrency and async wait common causes in most of the languages.

## Example
```typescript
bad:  fc.assert(fc.property(fc.array(fc.integer()), (xs) => {
        const k = Math.floor(Math.random() * (xs.length + 1));
        return sum(rotate(xs, k)) === sum(xs);
      }));
good: fc.assert(fc.property(fc.array(fc.integer()), fc.nat(), (xs, k) => {
        return sum(rotate(xs, k % (xs.length + 1))) === sum(xs);
      }));
```

## Limits
Only what the framework observes needs to be deterministic, which is the sequence of draws and the pass or fail outcome, and for a coverage-guided fuzzing engine also the code coverage it records: randomness, threads or other nondeterminism inside the body are acceptable as long as they affect nothing the framework can see. Conceptually global state passes when the test replaces it with a value the framework generates and shares within one generated case, which brings that state under the framework's control and visibility. The known sources of flakiness form a non-exhaustive list: decisions based on global state, explicit dependencies between inputs, filesystem or database state that is not reset between inputs, and unmanaged randomness, which includes standard pseudo-random generators the framework does not seed for each generated case (one framework seeds its language's default generator to zero and restores it around every case), thread scheduling and network timing. The rule reaches tests that run a property or fuzz target over generated inputs.

## Validator
Grep the hunk for a random-number call outside the framework's generators, a clock read, or a module-level or static mutable variable. Open the file and find each property or fuzz target the hunk touches: the function the framework calls once per generated input. Trace every value that body reads to decide its outcome or to choose what to draw. A framework-generated argument or draw, a source the framework seeds and restores for each generated case, or a source the body seeds for each case with a constant or a generated value, passes. A default pseudo-random generator that the framework does not seed and restore for each generated case, a source seeded once for the run and shared across inputs even with a fixed or reported seed, the clock, a variable outside the body that earlier inputs wrote, a value carried from one generated input to the next, or a file, table or row the body writes that nothing resets before the next input, fails. Randomness or concurrency that touches neither the outcome, nor the draws, nor in a fuzz target the coverage the engine records, passes. Validator question: **Does a property or fuzz-target body let its pass or fail outcome, or the values it draws, depend on randomness that comes neither from the framework nor from a source seeded for that generated case, on global state, on an earlier generated input, or on shared, file or database state that persists from one generated input to the next?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-51`, severity major, `file`, `symbol`, `code` = the line in the property body that reads a random source not seeded for that case, the clock or the state that persists between generated inputs, `fix` = the property with that value drawn from the framework's generators or from a source seeded for each generated case, or with the state created or reset for each input, in the file's language, `rationale` = the failure replay and failure database that a nondeterministic outcome defeats).
