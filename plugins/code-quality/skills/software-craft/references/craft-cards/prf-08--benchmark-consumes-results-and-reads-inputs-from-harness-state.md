---
title: A benchmark consumes the results of the code it measures and reads every input from mutable harness state, to limit dead-code elimination and constant folding of the measured work
rule_id: PRF-08
domain: performance
step: [test]
applies_to: [universal]
triggers: ['@Benchmark\b', '\bfunc\s+Benchmark\w*\s*\(', '(\bbench_function|\bbench_with_input|\bcriterion_group!|\bb[.]iter\w*\s*\(|#\[bench\])', '\b(timeit[.](timeit|repeat|Timer)|perf_counter(_ns)?|System[.]nanoTime|performance[.]now|Instant::now|time[.]Now|process[.]hrtime([.]bigint)?)\s*\(', '\bfor\b.*\bb[.]N\b', '\b(suite|bench)[.]add\s*\(']
scope: file
check_kind: semantic
severity_default: major
---

# A benchmark consumes the results of the code it measures and reads every input from mutable harness state, to limit dead-code elimination and constant folding of the measured work

## Thesis
A benchmark hands the result of the measured code to its harness, by returning it, passing it to the harness's sink or computing it inside the body of the harness's keep-alive loop construct, or, inside a loop over the iteration count the harness supplies, which keeps nothing alive, by passing each iteration's result to the harness's sink or the opaque identity wrapper, or, where the platform has neither, by storing or accumulating it into a sink the benchmark keeps, and reads every input the compiler could treat as a constant from mutable harness state or through an opaque identity wrapper applied inside any loop around the call.

## Rationale
An optimizing compiler can deduce that a computation whose result is never used is redundant, for instance once it has inlined the call, and eliminate it completely; the benchmark then measures how long it takes to do nothing, and partial dead-code elimination can yield results that look reasonable but still do not measure what was intended. When the result of the computation is the same no matter what, the compiler can fold it and move it outside the harness's loop; reading the inputs from mutable harness state prevents this, and wrapping them in an opaque identity tries to keep the compiler from optimizations that would be unrealistic in real-life use. Saving each result of a loop into one variable lets the compiler evaluate only the last call, and an input wrapped once outside a loop over a run-time iteration count leaves the call loop-invariant, so the compiler can hoist it and leave nothing to time. A static-analysis study of the benchmarks of 123 open-source systems, all written for one harness, found each of five bad practices with that harness prevalent, among them not using a returned computation (dead-code elimination) and a final primitive as benchmark input (constant folding), and its experiments found that bad practices often significantly impact the benchmark results.

## Example
```java
bad:  static final int X = 42;
      @Benchmark public void measure() { compute(X); }
good: @State(Scope.Thread) public static class Fixture { int x = 42; }
      @Benchmark public int measure(Fixture f) { return compute(f.x); }
```

## Limits
Inside the harness's keep-alive loop construct, arguments to and results from calls written in the loop body are kept alive and need no further sink; this holds only for statements syntactically between the loop's braces, with the loop condition written exactly as the harness specifies, and keeping a value alive blocks dead-code and dead-store elimination, not the folding of a call on literal inputs, so the input clause holds there too. A single result is returned; several results are either merged into one returned value, which suits a relatively heavyweight computation whose merging does not offset the results much, or each handed to the harness's sink. The opaque identity wrapper is best-effort, and the extent to which it blocks optimizations may vary with the platform and code-generation backend. In a benchmark whose result goes unused, a sub-nanosecond time is a clear red flag of dead-code elimination. The rule guards against an optimizing compiler; where the timed code runs on an implementation that executes every call it is given, a dropped call result or a literal argument to a call removes nothing from the timing and is no finding, while an operator expression on literals can still be folded there. Setup inside the timed region and a repetition loop the benchmark writes around the measured call are separate defects of a benchmark, outside this rule.

## Validator
Grep the hunk for a benchmark declaration, a harness registration or a timer call. Open each benchmark body the hunk adds or changes, and each interval between paired timer calls. Trace the measured call's result: returned, handed to the harness's sink or produced inside the body of the harness's keep-alive loop construct, or, inside a loop over the harness-supplied iteration count, passed to the harness's sink or the opaque identity wrapper each iteration, or, where the platform has neither, stored or accumulated into a sink the benchmark keeps; or instead dropped, or saved into one variable across the iterations of a loop. Trace each input of the measured call, inside a keep-alive loop body too, to mutable harness state, a distinct dataset element or an opaque identity wrapper applied inside any loop around the call, or to a literal, a final constant or a value wrapped once outside that loop. Validator question: **Does the benchmark drop the measured result, or feed the measured call an input the compiler can treat as a constant?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-08`, severity major, `file`, `symbol`, `code` = the benchmark line that drops the result or reads the constant input, `fix` = the benchmark returning or sinking the result and reading its inputs from mutable harness state or through the opaque identity wrapper inside the loop, in the file's language, `rationale` = which of dead-code elimination or constant folding the benchmark exposes its timing to).
