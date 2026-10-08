---
title: In a framework that counts discarded cases apart from passing ones, a property skips an unwanted generated input through the framework's discard call and never through an early return counted as a pass
rule_id: TST-46
domain: tests
step: [implement, test, review]
applies_to: [tests]
triggers: ['\breturn(?:\s+(?:true|True|None|Ok\(\(\)\)))?\s*;?\s*\}?\s*$']
scope: file
check_kind: mechanical
severity_default: minor
---

# In a framework that counts discarded cases apart from passing ones, a property skips an unwanted generated input through the framework's discard call and never through an early return counted as a pass

## Thesis
In a property-based testing framework that counts discarded cases apart from passing ones, a property body that meets a generated input it cannot check rejects that input through the framework's discard call, an assumption or precondition that the framework records as a discarded case, so that every case counted as passing is one in which the assertions ran.

## Rationale
The discard call tells the framework that the case was filtered out, and the framework leaves it out of its count of passing cases, the count it runs to where its budget is a number of passing cases. An early return is counted as a passing case even though the assertions did not run. When many generated inputs take the early return, the property can end up testing the code less than expected, because those cases are discarded without the framework knowing it. Cases discarded through the framework reach its guards: a count of discarded cases in the report, and a discard limit that gives up or fails the run when too many cases are filtered out (one documented default allows ten discarded cases per passing case); a case that returns early reaches neither. The discard call is still generation followed by dropping, and careless use can severely skew the distribution of tested inputs, so a generator option that yields only valid values, then a filter on the generator, comes first where it can express the condition, and the discard call covers the relationships a generator filter cannot express.

## Example
```typescript
bad:  fc.assert(fc.property(fc.integer(), fc.integer(), (lo, hi) => {
        if (lo > hi) return true;
        const m = midpoint(lo, hi);
        return lo <= m && m <= hi;
      }));
good: fc.assert(fc.property(fc.integer(), fc.integer(), (lo, hi) => {
        fc.pre(lo <= hi);
        const m = midpoint(lo, hi);
        return lo <= m && m <= hi;
      }));
```

## Limits
A filter attached to the generator satisfies the rule: the generator drops the value and draws another before the property body runs, so every case counted as passing still runs its assertions. A return that delivers the predicate's verdict after the check ran is the property's result, not a skip: true is a pass and false a failure. The rule holds where the framework counts discarded cases apart from passing ones, whether its budget is a number of passing cases or a number of tries with a cap on the ratio of tried to checked runs; a runner with no discard call is outside it. A fuzz engine whose budget is a duration or a number of executions of the fuzz target, and which by default runs forever if no failure occurs, documents returning early and calling its skip as alternatives for an input the target cannot check; the rule does not reach such a fuzz target.

## Validator
Grep the hunk for a `return` that carries no verdict (bare, constant true, or the empty success value) inside a property body: the callback handed to a property runner, a function the framework runs as a property, or a fuzz target. Open the body and check whether the return sits behind a condition on a generated input and ahead of the assertions or the verdict. Identify the runner: one that offers a discard call and counts discarded cases apart from passing ones, in its case budget or against a discard limit, is in scope; a fuzz target budgeted by duration or by executions, or a runner with no discard call, is out of scope. A return that carries the verdict, or a guard already written as the framework's discard call or as a generator filter, is no finding. Validator question: **Does a property body, run by a framework that counts discarded cases apart from passing ones, return early on a generated input before its assertions run where the framework's discard call belongs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-46`, severity minor, `file`, `symbol`, `code` = the guard line that returns early, quoted verbatim from the diff, `fix` = the guard rewritten as the framework's discard call on the condition a checkable input meets, in the file's language, `rationale` = names that the early return is counted as a passing case although no assertion ran, so the case count overstates what was tested and the framework's discard count and discard limit never see the case).

## Source
- HypothesisWorks/hypothesis master, hypothesis/docs/tutorial/adapting-strategies.rst, "assume vs early-returning" (fetched): "With |assume|, Hypothesis knows that a test case has been filtered out, and will not count it towards the |max_examples| limit. In contrast, early-returns are counted as a passing test, even though the assertions didn't run!"; "this could end up testing your code less than you expect, because many test cases get discarded without Hypothesis knowing about it"; "assume vs .filter": "Where possible, you should use |.filter|." and "For more complex relationships that can't be expressed with |.filter|, use |assume|."
- HypothesisWorks/hypothesis master, hypothesis/src/hypothesis/_settings.py (fetched): max_examples "Once this many satisfying |test cases| have been considered without finding any failing test case, Hypothesis will stop looking."; filter_too_much "Check for when the test is filtering out too many test cases, either through use of |assume| or |.filter|".
- nick8325/quickcheck master, src/Test/QuickCheck/Property.hs, (==>) (fetched): "The resulting property holds if the first argument is 'False' (in which case the test case is discarded)"; "using implication carelessly can severely skew test case distribution". src/Test/QuickCheck/Test.hs (fetched): maxSuccess "Maximum number of successful tests before succeeding"; maxDiscardRatio "Maximum number of discarded tests per successful test before giving up", `maxDiscardRatio = 10`; numDiscarded "Number of tests skipped".
- dubzzz/fast-check main, packages/fast-check/src/check/runner/configuration/Parameters.ts (fetched): numRuns "Number of runs before success: 100 by default"; maxSkipsPerRun "Runner will consider a run to have failed if it skipped maxSkips+1 times before having generated numRuns valid entries." website/docs/core-blocks/properties.md (fetched): "via `fc.pre` or `.filter`"; "they both consist into generating values and then dropping them"; "whenever feasible it's recommended to prefer relying on options directly providing by the arbitraries rather than filtering them"; "return crop(label, maxLength) === label; // true is success, false is failure".
- proptest-rs/proptest main, proptest/src/test_runner/config.rs (fetched): cases "The number of successful test cases that must execute for the test as a whole to pass."; max_global_rejects "The maximum number of combined inputs that may be rejected before the test as a whole aborts."
- jqwik-team/jqwik main, api/src/main/java/net/jqwik/api/Property.java (fetched): "They are executed (tried) several times, either until they fail or until the configured number of {@code tries()} has been reached."; maxDiscardRatio "The maximum ratio of tried versus actually checked property runs in case you are using Assumptions. If the ratio is exceeded jqwik will report this property as a failure."
- dubzzz/fast-check main, packages/fast-check/src/check/arbitrary/definition/Arbitrary.ts, FilterArbitrary.generate (fetched): a `while (true)` loop draws from the underlying arbitrary until the refinement holds; hypothesis/docs/tutorial/adapting-strategies.rst (fetched): "Calling |.filter| on a strategy creates a new strategy with that filter applied at generation-time."
- golang/website master, _content/doc/tutorial/fuzz.md (fetched): "Rather than returning, you can also call `t.Skip()` to stop the execution of that fuzz input."; "The default is to run forever if no failures occur". golang/go master, src/cmd/go/internal/test/test.go, -fuzztime (fetched): "Run enough iterations of the fuzz target during fuzzing to take t"; "The special syntax Nx means to run the fuzz target N times".
- Caveat: one framework's documentation states outright that an early return is counted as a pass; for the others the rule rests on their documented split between passing and discarded cases.
