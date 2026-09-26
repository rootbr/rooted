---
title: A hot loop keeps its counters, accumulators and element values as primitives, with no boxing or unboxing per iteration
rule_id: PF-15
domain: performance
triggers: ['for \(\s*(Integer|Long|Double|Float|Short|Byte|Character|Boolean) ', '\b(Integer|Long|Double|Float) \w+ = 0', 'List<(Integer|Long|Double)>', 'Map<\w+,\s*(Integer|Long|Double)>', '[.]boxed\(\)', 'Stream<(Integer|Long|Double)>']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A hot loop keeps its counters, accumulators and element values as primitives, with no boxing or unboxing per iteration

## Thesis
Inside a loop on a hot path, the loop variable, the accumulator and the arithmetic operate on `int`, `long` or `double`: a `Long sum`, a `for (Integer v : list)` over a boxed collection, a `map.put(k, map.get(k) + 1)` and a `Stream<Integer>` reduction each box or unbox on every iteration and are rewritten over primitives — a primitive local, a primitive array, `IntStream` or `LongStream`, or a `mapToInt`/`mapToLong` before the reduction.

## Rationale
A boxed `Integer` or `Long` outside the cache range −128..127 is a fresh heap object. `sum += v` with `Long sum` unboxes `sum`, adds, and boxes the result into a new `Long` each iteration; `for (Integer v : ints)` unboxes each element; `map.put(k, map.get(k) + 1)` unboxes and re-boxes per update. Thousands of iterations produce thousands of short-lived objects — allocation, young-generation pressure and cache misses that a primitive loop does not pay — and the compiler's escape analysis removes them only when the whole loop and its callees inline. The arithmetic itself becomes a call and a null check instead of one instruction.

## Example
```java
bad:  Long total = 0L;
      for (Long v : values) total += v;
good: long total = 0L;
      for (long v : valuesArray) total += v;   // or values.stream().mapToLong(Long::longValue).sum()
```

## Limits
Applies to loops on a hot path: per request, per message, over large collections. A loop over a handful of elements, boxing at an API boundary that requires objects (a generic collection parameter, a JSON model), and a value that must be nullable are out of scope. Replacing a large boxed collection by a primitive-specialized one is a separate concern; this rule covers the loop's own boxing.

## Validator
On the triggered hunk find each loop whose variable, accumulator or per-iteration arithmetic has a boxed type, and each stream pipeline that reduces a `Stream<Integer>`, `Stream<Long>` or `Stream<Double>` without `mapToInt`, `mapToLong` or `mapToDouble`. Validator question: **does this hot loop box or unbox a primitive on each iteration where a primitive type would serve?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-15`, severity minor, `file`, `symbol`, `code` = the loop header and the boxed accumulator quoted verbatim from the diff, `fix` = the primitive form, `rationale` naming the per-iteration allocation outside the boxing cache).

## Source
`java.lang.Integer#valueOf(int)` and `java.lang.Long#valueOf(long)` Javadoc, Java SE 21 — "This method will always cache values in the range -128 to 127, inclusive, and may cache other values outside of this range"; the constructor is avoided because `valueOf` "is likely to yield significantly better space and time performance by caching frequently requested values". JLS §5.1.7 boxing conversion (the compiler inserts `valueOf` for boxing and the unboxing calls for arithmetic on boxed operands) — not fetched from the authoring environment.
