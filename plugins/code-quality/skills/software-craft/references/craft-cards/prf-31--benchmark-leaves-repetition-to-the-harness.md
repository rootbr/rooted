---
title: A benchmark leaves repetition to its harness, so the measured call sits in no loop the benchmark writes around it unless every iteration takes a distinct or wrapped input and hands its result to the harness's sink
rule_id: PRF-31
domain: performance
step: [test]
applies_to: [universal]
triggers: ['@Benchmark\b', '\bfunc\s+Benchmark\w*\s*\(', '(\bbench_function|\bbench_with_input|\bcriterion_group!|\bb[.]iter\w*\s*\(|#\[bench\])', '\b(timeit[.](timeit|repeat|Timer)|perf_counter(_ns)?|System[.]nanoTime|performance[.]now|Instant::now|time[.]Now|process[.]hrtime([.]bigint)?)\s*\(', '\bfor\b.*\bb[.]N\b', '\b(suite|bench)[.]add\s*\(']
scope: file
check_kind: semantic
severity_default: major
---

# A benchmark leaves repetition to its harness, so the measured call sits in no loop the benchmark writes around it unless every iteration takes a distinct or wrapped input and hands its result to the harness's sink

## Thesis
A benchmark leaves repetition to its harness: the measured call sits in no loop the benchmark writes around it unless every iteration takes a distinct dataset element or an input passed through the opaque identity wrapper inside the loop and hands its result to the harness's sink or the wrapper.

## Rationale
Looping inside the benchmark in the hope of minimizing the overhead of calling the measured method lets the optimizer merge the loop iterations: the loop is heavily unrolled and pipelined and the measured operation hoisted out of it, so the larger the repetition count, the lower the perceived cost, down to 1/20 ns per addition, well beyond what hardware can actually do. A loop the benchmark writes still measures every call in full when each iteration takes a distinct input and sinks its result, while saving each result into one variable lets the compiler evaluate only the last call, accumulating lets software pipelining merge otherwise distinct calls, and an input wrapped once outside the loop leaves the call loop-invariant, so the compiler can hoist it and leave nothing to time. A static-analysis study of the benchmarks of 123 open-source systems, all written for one harness, found each of five bad practices with that harness prevalent, among them using accumulation to consume values inside a loop (loop optimization), and its experiments found that bad practices often significantly impact the benchmark results.

## Example
```rust
bad:  b.iter(|| { for _ in 0..1000 { contains(&haystack, needle); } });
good: b.iter(|| contains(black_box(&haystack), black_box(needle)));
```

## Limits
A loop over the iteration count the harness supplies is the harness's own repetition protocol, and so is the harness's keep-alive loop construct; a benchmark uses one of them, not both, and neither is a loop the benchmark writes around the call. A loop inside the measured routine is part of the measured work; the rule reaches only the loop a benchmark writes around the measured call. A loop whose every iteration takes a distinct dataset element or a wrapped input and hands its result to the harness's sink or the wrapper is no finding, and a timing routine the harness asks to measure its own execution time repeats the call as the harness directs. The rule guards against an optimizing compiler; where the timed code runs on an implementation that executes every call it is given, a loop around the call removes nothing from the timing and is no finding. Whether the measured result is consumed and whether setup runs inside the timed region are separate defects of a benchmark, outside this rule.

## Validator
Grep the hunk for a benchmark declaration, a harness registration or a timer call. Open each benchmark body the hunk adds or changes, and each interval between paired timer calls. Check whether the benchmark wraps the measured call in a loop of its own, other than a loop over the harness-supplied iteration count or the harness's loop construct, whose iterations do not each take a distinct dataset element or a wrapped input and hand the result to the harness's sink or the wrapper. Validator question: **Does the benchmark repeat the measured call in a loop of its own without a distinct or wrapped input and a sunk result on every iteration?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-31`, severity major, `file`, `symbol`, `code` = the loop header the benchmark writes around the measured call, `fix` = the loop removed so that the harness repeats the call, or every iteration given a distinct or wrapped input and its result handed to the harness's sink, in the file's language, `rationale` = the merging, hoisting or last-call evaluation the loop exposes the timing to).
