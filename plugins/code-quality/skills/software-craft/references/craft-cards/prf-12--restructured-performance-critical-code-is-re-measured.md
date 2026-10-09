---
title: A change that restructures code marked as performance-critical, by a comment giving a performance reason or by a benchmark that covers it, re-runs a covering benchmark against the base version and records both results
rule_id: PRF-12
domain: performance
step: [refactor, review]
applies_to: [universal]
triggers: ['(?i)\b(refactor\w*|restructur\w*|simplif(y|ied|ies|ication)|clean\s*-?up|readability)\b', '(?i)(//|#|/\*|\*)\s*.*\b(perf(ormance)?[- ]critical|hot\s*(path|loop)|fast\s*path|tight\s+loop|for\s+(speed|performance))\b', '\b(def|fn|function)\s+\w+\s*[(<\[]|\bfunc\s+(\([^)]*\)\s*)?\w+\s*[(\[]|\b(public|protected|private|internal|static)\s+[\w<>\[\],.? ]+\s+\w+\s*\(']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A change that restructures code marked as performance-critical, by a comment giving a performance reason or by a benchmark that covers it, re-runs a covering benchmark against the base version and records both results

## Thesis
A change that restructures code marked as performance-critical, either by a comment that gives a performance reason for the code's complexity or by a benchmark that covers the code, runs that benchmark on the base version and on the changed version and records both results in the change description. Where only a comment marks the code, the change profiles both versions with a realistic benchmark. Restructuring here means a rewrite for readability or simplicity that splits or merges loops, extracts routines, replaces the tuned structure with a general one, or removes the optimization.

## Rationale
Complexity added for performance, such as a buffer preallocated and reused, should be a clue that the code is performance-critical, and that clue should influence the care taken in later changes; ideally an accompanying comment explains the rationale and identifies the care to take. A microbenchmark that covers the code helps verify the impact of performance improvements and can help prevent future performance regressions. When performance does matter, it is important to profile both approaches with a realistic benchmark before deciding that one outperforms the other. A before-and-after comparison typically takes one set of results before the change and one after; each benchmark should be run at least 10 times to gather a statistically significant sample, and the comparison reports whether there was a statistically significant difference. Benchmark data belongs in the change description when the change affects performance.

## Example
```rust
bad:  // perf-critical: one loop that stops at the first divisor
      // change: index loop rewritten as an iterator chain for readability
      fn admits(n: u64, ds: &[u64]) -> bool { ds.iter().all(|d| n % d != 0) }
good: // perf-critical: one loop that stops at the first divisor
      // change: index loop rewritten as an iterator chain for readability
      // change description: bench admits vs base, 10 runs each: 1.21 ms before, 1.20 ms after
      fn admits(n: u64, ds: &[u64]) -> bool { ds.iter().all(|d| n % d != 0) }
```

## Limits
The rule reaches only code that carries such a mark, and the mark is the condition that separates the two sides of a contested question. For marked code, complexity added for performance should be a clue that the code is performance-critical and should influence the care taken in later changes. For code without the mark, a performance consideration such as whether an argument is passed by value or by reference should not outweigh the readability and correctness of the code in most circumstances, performance-specific guidelines apply only to the hot path, and the code is restructured for readability without this step. A microbenchmark can have pitfalls that make it non-representative of full system performance; its before-and-after result checks the covered code, and the rule asks for no system-level measurement.


Whether the recorded results rest on enough runs and carry the variation between runs or a significance verdict lies outside this rule, which asks only that the covering benchmark run on both versions and that both results be recorded.
## Validator
Grep the hunk and the change description for restructuring words (refactor, simplify, clean up, readability), and grep the changed lines and the comments above them for a performance reason (performance-critical, hot path, fast path, for speed). A hunk that rewrites a routine's body dispatches the card through the routine's declaration, since the restructuring itself carries no such word. At scope callers, open the base version of each changed routine and read its comments for a performance reason, and look among the routine's usages across the repository for a benchmark that covers it. Where either mark exists and the change splits or merges its loops, extracts routines from it, replaces its tuned structure or removes its optimization, look in the change description and the diff for benchmark results taken on both the base and the changed version. Validator question: **Does the change restructure code that the base version marks as performance-critical, by a comment giving a performance reason or by a covering benchmark, with the benchmark result missing for the base version, the changed version, or both?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-12`, severity minor, `file`, `symbol`, `code` = the performance comment or the covering benchmark's name together with the restructured lines, quoted verbatim from the diff, `fix` = the covering benchmark, named or written in the file's language, run on the base and the changed version with both results added to the change description, `rationale` = names the performance mark, the restructuring and the missing comparison against the base version).

## Source
- Google Go Style Guide, go/guide.md §Simplicity (fetched): "When a maintainer sees this, it should be a clue that the code in question is performance-critical, and that should influence the care that is taken when making future changes"; "Ideally, there should be accompanying commentary that explains the rationale and identifies the care that should be taken. This often arises when optimizing code for performance; doing so often requires a more complex approach, like preallocating a buffer and reusing it".
- Abseil performance hints, fast/hints.md §Profiling tools and tips (fetched): "If you can, write a microbenchmark that covers the code you are improving. Microbenchmarks improve turnaround time when making performance improvements, help verify the impact of performance improvements, and can help prevent future performance regressions. However microbenchmarks can have pitfalls that make them non-representative of full system performance."
- Google Go Style Decisions, go/decisions.md §Receiver type, closing Note (fetched): "these considerations should not outweigh the readability and correctness of the code in most circumstances. When the performance does matter, it is important to profile both approaches with a realistic benchmark before deciding that one approach outperforms the other."
- Uber Go Style Guide, style.md §Performance (fetched): "Performance-specific guidelines apply only to the hot path."
- golang/perf cmd/benchstat, package documentation (fetched): "Typically, there should be two (or more) inputs files for before and after some change (or series of changes) to be measured. Each benchmark should be run at least 10 times to gather a statistically significant sample of results."; it "reports whether there was a statistically significant difference".
- Go contribution guide, golang/website _content/doc/contribute.html §Good commit messages, Main content (fetched): "Add any relevant information, such as benchmark data if the change affects performance. The benchstat tool is conventionally used to format benchmark data for change descriptions."
- Caveat: the evidence is project guidance from Go and C++ codebases, not a controlled study; the rule carries its condition, code marked as performance-critical, across languages.
