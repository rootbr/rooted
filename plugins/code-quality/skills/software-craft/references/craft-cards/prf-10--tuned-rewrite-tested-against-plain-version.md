---
title: A routine rewritten for speed is covered, in the same change, by tests that compare its results with the plain implementation's or that the plain implementation already passed
rule_id: PRF-10
domain: performance
step: [test, refactor]
applies_to: [universal]
triggers: ['(?i)\b(def|fn|func|function|static|private|public|fun)\b.*\b\w*(naive|reference|slow|scalar|portable|fast|optimi[sz]ed|unrolled|simd|vectori[sz]ed)\w*\s*[(<]', '(?i)\b(REFERENCE_\w+|naive_?\w*|slow_?path|fast_?path)\b', '(?i)(//|#|/\*|\*)\s*.*\b(optimi[sz]ed|faster|for speed|for performance|hot\s*path)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A routine rewritten for speed is covered, in the same change, by tests that compare its results with the plain implementation's or that the plain implementation already passed

## Thesis
When a change replaces the plain implementation of a routine with one rewritten for speed — tuned loops, logic expressions or data transformations, bit-twiddling, intrinsics or vector code, inline assembly, or a rewrite in a lower-level language — the tuned routine is covered by tests when the change lands: tests in the change that check it is equivalent to the plain implementation kept as a reference routine, or tests that already covered the plain implementation and now run against the tuned one.

## Rationale
Code tuning is the modification of correct code so that it runs more efficiently, usually a small-scale change that affects a single class, a single routine or, more commonly, a few lines of code. Regressions can hide in sophisticated optimizations, which is why good coverage, through unit tests or any other technique, is highly recommended before such an optimization goes in. Keeping the plain implementation as a reference routine makes a unit test that the two implementations are equivalent easy to write, makes a microbenchmark easier to write, and makes it easier to revert to the reference code when, not if, the machine-dependent implementation outlives its usefulness. Complexity added because more performance is required may be justified, but it should come with documentation supplemented with tests and examples that demonstrate its correct usage, especially when there is both a simple and a complex way to use the code.

## Example
```typescript
bad:  // rewritten for speed: SWAR bit tricks replace the naive per-bit loop, and no test calls it
      export function popcountFast(x: number): number { ... }
good: export function popcountReference(x: number): number {
        let n = 0; for (; x; x >>>= 1) n += x & 1; return n; }
      // rewritten for speed: SWAR bit tricks; the reference above pins its results
      export function popcountFast(x: number): number { x -= (x >>> 1) & 0x55555555;
        x = (x & 0x33333333) + ((x >>> 2) & 0x33333333); return Math.imul((x + (x >>> 4)) & 0x0f0f0f0f, 0x01010101) >>> 24; }
      test("popcountFast matches the reference", () => {
        for (const x of [0, 1, 0xff, 0x80000000, 0xffffffff]) assert.equal(popcountFast(x), popcountReference(x)); });
```

## Limits
A separate reference routine is one way to pin the tuned routine's results, offered as something to consider; tests that already covered the plain implementation and now exercise the tuned one meet the rule without it. The rule reaches tuning at the code level, and leaves out the efficiency that architecture, detailed design decisions, and data-structure and algorithm selection determine.

## Validator
Grep the hunk for a speed-motivated rewrite: a comment naming optimization, speed or a hot path; a routine name carrying fast, naive, reference, scalar, unrolled, simd or vectorized; an unsafe block, platform intrinsics or a vector API; a routine body replaced by bit manipulation or unrolled loops beside a removed plain loop. Name the routine the rewrite changes. Open its callers at the card's scope, the test files in the change and the existing tests among them, and trace whether any test calls the tuned routine and either compares its result with a plain reference implementation or asserts results the plain implementation already produced. Validator question: **Does the change rewrite a routine for speed while no test, in the change or already present, exercises the tuned routine against the plain implementation's results?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-10`, severity minor, `file`, `symbol`, `code` = the tuned routine's signature line and the speed comment or construct as the diff shows them, `fix` = the plain implementation kept as a reference routine and a test that compares the tuned routine with it over sample inputs, in the file's language, `rationale` = names that the change modifies correct code for speed with no test to catch a regression hidden in the optimization).

## Source
- SWEBOK Guide V3.0, ch. 3 'Software Construction', §4.14 'Performance Analysis and Tuning' (fetched): "Code efficiency - determined by architecture, detailed design decisions, and data-structure and algorithm selection - influences an execution speed and size."; "Code tuning, which improves performance at the code level, is the practice of modifying correct code in ways that make it run more efficiently. Code tuning usually involves only small-scale changes that affect a single class, a single routine, or, more commonly, a few lines of code. A rich set of code tuning techniques is available, including those for tuning logic expressions, loops, data transformations, expressions, and routines. Using a low-level language is another common technique for improving some hot spots in a program."
- Abseil Performance Tip of the Week #9 'Optimizations past their prime', §'Best practices' (fetched): "a low-level performance optimization that requires fancy bit-twiddling, intrinsics code, or inline assembly"; "possibly using hwy to generate efficient and portable vector code"; "Keep the "naive" code you are replacing. If you are optimizing `ComputeFoo`, consider keeping the simple implementation in a `REFERENCE_ComputeFoo` function. This makes it easy to write a unit-test for the new implementation that ensures the two functions are equivalent; it makes it easier to write a microbenchmark; and it makes it easier to revert to the reference code when (not if) the machine-dependent implementation outlives its usefulness."
- Python Programming FAQ, 'My program is too slow. How do I speed it up?' (fetched): "It is highly recommended to have good code coverage (through unit testing or any other technique) before potentially introducing regressions hidden in sophisticated optimizations."
- Go Style Guide, §'Simplicity' (fetched): "When code needs complexity, the complexity should be added deliberately. This is typically necessary if additional performance is required [...] Complexity may be justified, but it should come with accompanying documentation [...] This should be supplemented with tests and examples that demonstrate its correct usage, especially if there is both a "simple" and a "complex" way to use the code."
- Caveat: the reference-routine practice is stated for machine-dependent low-level optimizations, the coverage recommendation for sophisticated optimizations in general; none of the sources measures how often tuned code without such tests regresses.
