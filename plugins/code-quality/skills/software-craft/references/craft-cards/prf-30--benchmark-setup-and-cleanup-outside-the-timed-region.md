---
title: A benchmark runs its setup, fixtures and cleanup outside the timed region, in the harness's setup and teardown phases or behind a timer reset after setup and a timer stop before cleanup
rule_id: PRF-30
domain: performance
step: [test]
applies_to: [universal]
triggers: ['@Benchmark\b', '\bfunc\s+Benchmark\w*\s*\(', '(\bbench_function|\bbench_with_input|\bcriterion_group!|\bb[.]iter\w*\s*\(|#\[bench\])', '\b(timeit[.](timeit|repeat|Timer)|perf_counter(_ns)?|System[.]nanoTime|performance[.]now|Instant::now|time[.]Now|process[.]hrtime([.]bigint)?)\s*\(', '\bfor\b.*\bb[.]N\b', '\b(suite|bench)[.]add\s*\(']
scope: file
check_kind: semantic
severity_default: major
---

# A benchmark runs its setup, fixtures and cleanup outside the timed region, in the harness's setup and teardown phases or behind a timer reset after setup and a timer stop before cleanup

## Thesis
A benchmark runs setup, fixtures and cleanup outside the timed region: in the harness's setup and teardown phases, before or after the harness's keep-alive loop construct, or, around a loop over the iteration count the harness supplies, behind a timer reset after setup and a timer stop before cleanup.

## Rationale
Setup and cleanup left in the timed region are included in the overall time measurement and silently skew the result, while the harness excludes from the timing the setup and cleanup it runs in its setup and teardown phases or before and after its keep-alive loop construct; around a loop over the iteration count the harness supplies it can only time the entire benchmark function, so setup and cleanup there count unless the benchmark resets the timer after setup and stops it before cleanup. A static-analysis study of the benchmarks of 123 open-source systems, all written for one harness, found each of five bad practices with that harness prevalent, among them running fixture methods for each benchmark method invocation (harness overhead), and its experiments found that bad practices often significantly impact the benchmark results.

## Example
```go
bad:  func BenchmarkParse(b *testing.B) {
          doc := loadFixture()
          for i := 0; i < b.N; i++ { sink = parse(doc) }
      }
good: func BenchmarkParse(b *testing.B) {
          doc := loadFixture()
          for b.Loop() { parse(doc) }
      }
```

## Limits
Per-invocation work that should not count as payload belongs in the harness's per-invocation setup level, used with care, since its timestamping and synchronization might significantly offset the measurement, or between a timer stop and a timer start inside the harness's loop. A harness whose keep-alive loop construct starts the timer when the loop begins and stops it when the loop ends excludes the setup before and the cleanup after that loop with no timer call; a timing scaffold that takes a separate setup statement excludes that statement's execution time from the timed run. The rule holds on every implementation, optimizing or not, since timed setup adds to the measurement whatever the compiler does. Whether the measured result is consumed and whether the benchmark writes a repetition loop of its own are separate defects of a benchmark, outside this rule.

## Validator
Grep the hunk for a benchmark declaration, a harness registration or a timer call. Open each benchmark body the hunk adds or changes, and each interval between paired timer calls. Check whether data construction, fixture setup or cleanup runs inside the timed body or interval rather than in the harness's setup or teardown phase, before or after its keep-alive loop construct, or between a timer stop and a timer start; setup before, or cleanup after, a loop over the harness-supplied iteration count is inside the timed body unless a timer reset follows the setup and a timer stop precedes the cleanup. Validator question: **Does the benchmark time its own setup, fixture construction or cleanup?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-30`, severity major, `file`, `symbol`, `code` = the benchmark line that runs the setup or cleanup inside the timed region, `fix` = the setup moved to the harness's setup phase or before its keep-alive loop construct and the cleanup to its teardown phase or after that loop, or fenced by a timer reset and a timer stop, in the file's language, `rationale` = the setup or cleanup work the timing includes and the skew it adds).
