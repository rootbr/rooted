---
title: A custom Collector's combiner is associative and merging with an empty container is an identity, so a parallel collect equals the sequential result
rule_id: CC-25
domain: concurrency
triggers: ['Collector[.]of\(', 'implements Collector<', 'combiner\(\)', 'BinaryOperator<', 'new Collector<']
scope: file
check_kind: semantic
severity_default: major
---

# A custom Collector's combiner is associative and merging with an empty container is an identity, so a parallel collect equals the sequential result

## Thesis
A collector built with `Collector.of` or by implementing `Collector` has a combiner that merges two partial containers into the same result the accumulator would have produced sequentially — every element of both arguments kept, no dependence on which argument came first beyond what the accumulator itself tolerates — and merging any partial result with a fresh container from the supplier leaves it equivalent.

## Rationale
A parallel `collect` splits the input, runs the accumulator on each split into its own container, then folds the containers with the combiner in an order the runtime chooses; a sequential run uses the accumulator alone. The stream library guarantees the two produce equivalent results only when the identity and associativity constraints hold. A combiner that returns its first argument unchanged, that ignores the second, that merges asymmetrically, or that returns a container missing some merged elements yields a different result per split — and the split depends on input size and worker count, so a test on a small input passes while production data loses part of every parallel result. The JDK collectors (`toList`, `toMap`, `groupingBy`, `joining`) satisfy the constraints; a hand-rolled one is checked by hand.

## Example
```java
bad:  Collector.of(() -> new long[2], (a, x) -> { a[0] += x; a[1]++; },
                   (a, b) -> a, a -> a[0] / (double) a[1]);
good: Collector.of(() -> new long[2], (a, x) -> { a[0] += x; a[1]++; },
                   (a, b) -> { a[0] += b[0]; a[1] += b[1]; return a; }, a -> a[0] / (double) a[1]);
```

## Limits
Applies to a collector a parallel pipeline may use: one applied to a parallel stream in the file, or one exposed as a reusable value. A collector used on a sequential stream alone never runs its combiner; the defect is latent until someone parallelizes the pipeline. A combiner that throws `UnsupportedOperationException` beside a comment restricting the collector to sequential use is a documented tolerance. A collector with the `CONCURRENT` characteristic accumulates into one container, and its combiner is trivially the identity.

## Validator
On the triggered hunk read the supplier, accumulator, combiner and finisher; open the file to see whether the collector is applied to a parallel stream or exposed as a reusable value. Check the combiner: it merges every element of both arguments, its correctness does not depend on which argument came first, and it returns the merged container. Check the identity: merging a partial result with `supplier.get()` changes nothing. Validator question: **can two ways of splitting the same input produce different results, because the combiner drops, reorders or asymmetrically merges elements, or treats an empty container as non-neutral?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-25`, severity major, `file`, `symbol`, `code` = the combiner quoted verbatim from the diff, `fix` = a combiner that merges both containers completely and symmetrically, `rationale` naming the split-dependent result).

## Source
`java.util.stream.Collector` Javadoc, Java SE 21 — "To ensure that sequential and parallel executions produce equivalent results, the collector functions must satisfy an identity and an associativity constraints"; the identity constraint: a partial result `a` "must be equivalent to `combiner.apply(a, supplier.get())`"; the associativity constraint: the unsplit result `finisher.apply(a1)` must be equivalent to the split result `finisher.apply(combiner.apply(a2, a3))`.
