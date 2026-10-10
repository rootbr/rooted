---
title: In a framework that counts discarded cases apart from passing ones, a property skips an unwanted generated input through the framework's discard call and never through an early return counted as a pass
rule_id: TST-46
domain: tests
step: [test]
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

Whether the property also reports a classification of the cases it accepts is outside this rule, which judges only how an unwanted input is skipped.

## Validator
Grep the hunk for a `return` that carries no verdict (bare, constant true, or the empty success value) inside a property body: the callback handed to a property runner, a function the framework runs as a property, or a fuzz target. Open the body and check whether the return sits behind a condition on a generated input and ahead of the assertions or the verdict. Identify the runner: one that offers a discard call and counts discarded cases apart from passing ones, in its case budget or against a discard limit, is in scope; a fuzz target budgeted by duration or by executions, or a runner with no discard call, is out of scope. A return that carries the verdict, or a guard already written as the framework's discard call or as a generator filter, is no finding. Validator question: **Does a property body, run by a framework that counts discarded cases apart from passing ones, return early on a generated input before its assertions run where the framework's discard call belongs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-46`, severity minor, `file`, `symbol`, `code` = the guard line that returns early, quoted verbatim from the diff, `fix` = the guard rewritten as the framework's discard call on the condition a checkable input meets, in the file's language, `rationale` = names that the early return is counted as a passing case although no assertion ran, so the case count overstates what was tested and the framework's discard count and discard limit never see the case).
