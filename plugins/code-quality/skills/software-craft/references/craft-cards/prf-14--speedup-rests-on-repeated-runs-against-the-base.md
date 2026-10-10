---
title: A reported speedup rests on repeated runs of the base and the changed version and is claimed only where it is distinguished from noise
rule_id: PRF-14
domain: performance
step: [test, review]
applies_to: [universal]
triggers: ['(?i)\b\d+([.]\d+)?\s*(ns|µs|us|ms|s)(/op)?\b.*\b(vs[.]?|versus|before|after|down from|up from|instead of)\b', '(?i)\b\d+([.]\d+)?\s*(x|%)\s*(faster|slower|speed-?up|improvement|regression)\b']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A reported speedup rests on repeated runs of the base and the changed version and is claimed only where it is distinguished from noise

## Thesis
A speedup or regression figure recorded with a change rests on a comparison of the base and the changed version on a realistic benchmark, each version run a number of times fixed in advance and at least 10, or at least 5 where the harness compares the best of its repeats and every repeat is shown, with before and after runs interleaved where the harness allows, and the figure is claimed only where the reported variation between runs or the harness's significance verdict distinguishes it from noise.

## Rationale
Execution time differs from run to run through just-in-time compilation, thread scheduling, garbage collection, randomized address-space layout and hashing, and other programs running on the same machine; a single estimate has no context, and the benchmark is run multiple times to be able to recognize that noise. The harnesses fix the count in advance: one asks for at least 10 runs per version, ideally 20, and to stick to that number; another defaults to 30 samples of each version; another spawns 20 worker processes and ignores each worker's warmup run. Interleaving before and after runs, rather than all before runs followed by all after runs, distributes the noise evenly across both versions. At the default 0.05 threshold a comparison is expected to show a difference 5% of the time when there is none, so rerunning until a difference appears creates a statistical bias, and among 20 benchmarks one normally shows significance when it should not; a 1% or 0.1% threshold lowers that risk and may require more runs. Where the comparison reports no significant difference, the improvement figure supports no conclusion, and one harness ignores changes within a configurable noise threshold such as ±1%. A profiler is built for an execution profile, not for benchmarking: a deterministic profiler in an interpreted runtime adds overhead to the interpreted code but not to the native functions it calls, so the native code would seem faster, and one empirical study measured average profiler run-time overhead of 1% to 5.4%.

## Example
```python
bad:  # parse_rows: 41 ms before, 29 ms after, 1.4x faster (one run each)
      start = time.perf_counter(); parse_rows(rows)
      print(time.perf_counter() - start)
good: # compare_to base.json changed.json, 20 worker processes per version:
      # Mean +- std dev: [base] 41.2 ms +- 0.9 ms -> [changed] 29.3 ms +- 0.7 ms: 1.41x faster
      runner = pyperf.Runner(processes=20)
      runner.bench_func("parse_rows", parse_rows, rows)
```

## Limits
A measure with no noise, such as the size of a binary a compiler produces, gains nothing from repeated measurements, and a single before and after measurement can be compared. Statistically significant is not the same as large: with enough low-noise data even a very small change is distinguished from noise and counted significant. Harnesses differ in the statistic: one compares medians with a Mann-Whitney U-test, others use a Welch's or Student's t-test, and one documents the minimum of the repeats as the number of interest, higher values typically being interference from other processes, and advises looking at the entire vector of repeats; that harness documents its default of 5 repetitions as probably enough in most cases, so a comparison of minima from at least 5 repetitions of each version that shows every repetition carries the run count and the variation this rule asks for, while the floor of 10 holds where a significance test or the spread between runs decides. Low noise is required but not sufficient, since it does not exclude measurement bias: a single binary is one sample from the space of program layouts regardless of the number of runs, and changing a seemingly innocuous aspect of the setup can lead to wrong conclusions; controlling for layout and setup bias lies beyond this rule.

## Validator
Grep the hunk, including code comments, commit or changelog text, documentation and benchmark result files, for a timing or speed figure tied to a change: a speedup or slowdown factor, a percentage improvement or regression, a before and after time. Open the hunk around each figure and trace what it rests on: runs of the base, runs of the changed version, the run count, and the variation between runs or the significance verdict that accompanies it. Skip a deterministic measure such as binary size. Validator question: **Does the hunk claim a speedup or regression from fewer than 10 runs per version (fewer than 5 repetitions where the best of every shown repetition is compared), from no base measurement, from profiler timings, or with neither the variation between runs nor a significance verdict that distinguishes it from noise?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-14`, severity minor, `file`, `symbol`, `code` = the line that states the speedup or regression figure, verbatim from the diff, `fix` = the claim restated as a comparison of repeated runs of the base and the changed version, interleaved where the harness allows, with the harness's variation or significance verdict, in the file's language, `rationale` = which support is missing: at least 10 runs per version (5 repetitions where minima are compared), a base measurement, a measurement other than profiler timings, or a variation or verdict that separates the change from noise).
