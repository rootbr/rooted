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

## Source
- golang/perf `cmd/benchstat/main.go` package doc (fetched): "Each benchmark should be run at least 10 times to gather a statistically significant sample of results"; § Tips: "noise is evenly distributed across benchmark runs. The best way to do this is to interleave before and after runs"; "Pick a number of benchmark runs (at least 10, ideally 20) and stick to it"; "it is *expected* to show a difference 5% of the time even if there is no difference"; "if you rerun benchmarks looking for a change, benchstat will probably eventually say there is a change, even if there isn't, which creates a statistical bias"; "median for summaries, and the Mann-Whitney U-test for A/B comparisons"; "\"statistically significant\" is not the same as \"large\""; "Some benchmarks measure things that have no noise, such as the size of a binary produced by a compiler"; "show A/B comparisons even if there's only one before and after measurement".
- nodejs/node `doc/contributing/writing-and-running-benchmarks.md` (fetched): "--runs 30 number of samples"; "if there are no stars, then don't make any conclusions based on the _improvement_"; "when considering 20 benchmarks it's normal that one of them will show significance, when it shouldn't"; "in that case the risk is 1%. If three stars (`***`) is considered the risk is 0.1%. However this may require more runs"; "the same Welch's t-test"; `benchmark/compare.js` (fetched): "such both node versions are tested `runs` amount of times each".
- psf/pyperf `doc/run_benchmark.rst` (fetched): "Then pyperf spawns 20 worker processes"; "running the benchmark once to \"warmup\" the process, but this result is ignored in the final result"; "large enough to reduce the effect of random factors like randomized address space layer (ASLR)"; `doc/cli.rst` § compare_to: "Student's two-sample, two-tailed t-test".
- criterion-rs/criterion.rs `book/src/analysis.md` (fetched): "A single estimate is difficult to interpret, however, since it contains no context"; "Optimizations or regressions within (for example) +-1% are considered noise and ignored".
- llvm/llvm-project `llvm/docs/Benchmarking.md` (fetched): "Note that low noise is required, but not sufficient. It does not exclude measurement bias."; "Run the benchmark multiple times to be able to recognize noise."
- google/styleguide `go/decisions.md` § Receiver type (fetched): "profile both approaches with a realistic benchmark before deciding that one approach outperforms the other".
- python/cpython 3.13 `Doc/library/profile.rst` (fetched): "designed to provide an execution profile for a given program, not for benchmarking purposes"; `Doc/library/timeit.rst` (fetched): "can be affected by other programs running on the same machine"; "higher values in the result vector are typically not caused by variability in Python's speed, but by other processes interfering"; "the :func:`min` of the result is probably the only number you should be interested in.  After that, you should look at the entire vector"; "repeat the timing a few times and use the best time.  The :option:`-r` option is good for this; the default of 5 repetitions is probably enough in most cases".
- DOI 10.1145/2451116.2451141 (DOI from memory), abstract in ccurtsinger/stabilizer `README.md` (fetched): "A single binary constitutes just one sample from the space of program layouts, regardless of the number of runs."
- DOI 10.1145/1508244.1508275 (DOI from memory; quote relayed, https://sape.inf.usi.ch/publications/asplos09): "changing a seemingly innocuous aspect of an experimental setup can cause a systems researcher to draw wrong conclusions from an experiment".
- DOI 10.1145/1297027.1297033 (DOI from memory; quote relayed, https://dri.es/files/oopsla07-georges.pdf): "non-determinism at run-time that causes execution time to differ from run to run, stemming from sources like Just-In-Time (JIT) compilation ... thread scheduling, garbage collection, and various system effects".
- DOI 10.1145/3617651.3622985 (DOI unverified; quote relayed, https://stefan-marr.de/downloads/mplr23-burchell-et-al-dont-trust-your-profiler.pdf): "The average run time overhead is in the range of 1% to 5.4%". Caveat: this study and the run-to-run study measured Java profilers and Java programs.
