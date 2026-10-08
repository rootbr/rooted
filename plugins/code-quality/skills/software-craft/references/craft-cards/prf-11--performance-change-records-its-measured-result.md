---
title: A change made for speed states in its description the measured before-and-after result and the benchmark that produced it, and no comment, name or description claims a speed gain without such a measurement
rule_id: PRF-11
domain: performance
step: [document, review]
applies_to: [universal]
triggers: ['(?<![A-Za-z])[Ff]aster(?![a-z])|(?<=[a-z0-9])Faster(?![a-z])', '(?i)\b(faster|speed-?up|speeds?\s+up|perf(ormance)?\s+(improvement|win|gain|fix)|more\s+efficient|reduces?\s+(latency|allocations?|cpu|memory\s+use))\b', '(?i)(//|#|/\*|\*)\s*.*(\b\d+([.]\d+)?\s*(x|%)\s*(faster|slower|speed-?up)\b|\bfaster than\b|\bcheaper than\b|\bmore efficient than\b)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A change made for speed states in its description the measured before-and-after result and the benchmark that produced it, and no comment, name or description claims a speed gain without such a measurement

## Thesis
A change made for speed states in its description the measured before-and-after result, formatted by the project's benchmark-comparison tool where it has one, and includes or names the repeatable benchmark that reproduces that result; a comment that explains code by its speed, or the comment at a name that claims speed, states the measured gain or names that benchmark; and every claim of speed in a comment, a name or a change description rests on such a measurement.

## Rationale
Modern hardware and optimizers defy naive assumptions and even experts are regularly surprised, so a claim about performance needs a measurement behind it, and a comment that explains code by its speed is such a claim. A comparison tool reports each benchmark before and after a change, can show a measure of its spread such as a confidence interval or a standard deviation, and marks a difference it cannot distinguish from noise; a difference so marked has not been shown to be more than noise, and a statistically significant difference is not necessarily a large one. Optimizations do not always age gracefully, and faster yesterday might mean slower today: a micro-optimization comes with a repeatable benchmark to show its value, with the expectation that it is dropped once the optimizer no longer needs it. Optimizing often requires a more complex form, such as a buffer preallocated and reused; the commentary at it explains the rationale and identifies the care to be taken, the form tells a maintainer that the code is performance-critical, and the same complexity employed unnecessarily is a burden on those who read or change the code. The description carries the result itself, because a link to an external resource may not be visible to future readers.

## Example
```go
bad:  // Faster than allocating a buffer per call.
      var bufPool = sync.Pool{New: func() any { return new(bytes.Buffer) }}
good: // Pooled for speed: BenchmarkEncode 412 -> 268 ns/op, 3 -> 1 allocs/op
      // (benchstat, 10 runs each); drop the pool once the benchmark shows no gain.
      var bufPool = sync.Pool{New: func() any { return new(bytes.Buffer) }}
```

## Limits
The rule reaches a change that is made for speed or claims a speed effect; a change made for another purpose that claims no speed effect falls outside it. Code left in its clear, idiomatic form needs no comment about speed. The description may also link a fuller record, such as an issue or a design document, provided it carries enough context for a future reader who cannot open the link. How the benchmark is run (warm-up, repetitions, variation against a baseline) and low-latency tuning of memory layout, lock-free structures or the runtime lie outside this rule, which asks only that the measured result be recorded.

## Validator
Grep the hunk's added comments and identifiers for a speed claim: faster, speed up, more efficient, reduces latency, allocations or memory use, a figure such as 2x or 30% faster. For each hit, read the claiming comment, or the comment at the named code, for the measured before-and-after gain (two figures with units) or the name of the benchmark that shows it. Where the change description is in view, as in the review of one's own change, grep it too, including for a perf or optimize subject prefix, and read it for a before-and-after result (two sets of figures with units, or a comparison table) and for a benchmark the change includes or names. Count a comparison that marks the difference as indistinguishable from noise as showing no gain. Validator question: **Does an added comment or identifier claim a speed gain while that comment, or the comment at that identifier, neither states a measured before-and-after gain nor names the benchmark that shows it, or does a change description in view make a change for speed or claim a speed gain while lacking the measured before-and-after result, or lacking a benchmark the change includes or names?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-11`, severity minor, `file`, `symbol`, `code` = the claiming comment or name verbatim from the diff, or the claiming description line when the description is in view, `fix` = that comment or description rewritten in the file's language to name the benchmark that reproduces the claim, with a marked placeholder for each before-and-after figure that neither the diff nor the description states, never an invented figure, or with the unmeasured speed claim removed, `rationale` = that a claim about performance needs a measurement behind it and that a recorded benchmark shows whether the tuning still pays).

## Source
- golang/website `_content/doc/contribute.html`, §Commit messages: "Add any relevant information, such as benchmark data if the change affects performance. The benchstat tool is conventionally used to format benchmark data for change descriptions." (fetched)
- golang/perf `cmd/benchstat/main.go`, package documentation: "Typically, there should be two (or more) inputs files for before and after some change (or series of changes) to be measured."; "For each benchmark, benchstat computes the median and the confidence interval for the median."; "the \"~\" means benchstat did not detect a statistically significant difference between the two inputs"; "it's very likely the differences for this benchmark are simply due to random chance"; "\"statistically significant\" is not the same as \"large\"" (fetched)
- psf/pyperf `doc/cli.rst`, §pyperf compare_to: "Compare benchmark suites, use the first file as the reference"; "Mean +- std dev: [py36] 4.70 us +- 0.18 us -> [py38] 4.22 us +- 0.08 us: 1.11x faster"; the comparison table's cell "not significant" (fetched)
- google/eng-practices `review/developer/cl-descriptions.md`, §Body is Informative: "If relevant, include background information such as bug numbers, benchmark results, and links to design documents."; "If you include links to external resources consider that they may not be visible to future readers due to access restrictions or retention policies. Where possible include enough context for reviewers and future readers to understand the CL." (fetched)
- rust-lang/rust `library/core/src/hint.rs`, `assert_unchecked` §Usage: "Any use should come with a repeatable benchmark to show the value, with the expectation to drop it later should the optimizer get smarter and no longer need it." (fetched)
- abseil/abseil.github.io fast/9 'Optimizations past their prime': "Optimizations don't always age gracefully. Faster yesterday might mean slower today."; §Best practices: "Prefer writing clear, idiomatic code whenever possible."; "Include a microbenchmark with your change." (fetched)
- C++ Core Guidelines Per.6 'Don't make claims about performance without measurements': "Modern hardware and optimizers defy naive assumptions; even experts are regularly surprised." (fetched)
- google/styleguide `go/guide.md`, §Simplicity: "Ideally, there should be accompanying commentary that explains the rationale and identifies the care that should be taken. This often arises when optimizing code for performance; doing so often requires a more complex approach, like preallocating a buffer and reusing it throughout a goroutine lifetime."; "it should be a clue that the code in question is performance-critical"; "If employed unnecessarily, on the other hand, this complexity is a burden on those who need to read or change the code in the future." (fetched)
- Caveat: the benchmark-with-the-change fragments speak of micro-optimizations; the description fragments cover any change that affects performance, and comparison output names each benchmark it reports.
