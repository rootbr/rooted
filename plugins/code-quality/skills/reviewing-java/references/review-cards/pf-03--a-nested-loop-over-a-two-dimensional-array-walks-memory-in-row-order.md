---
title: A nested loop over a two-dimensional array or a flat buffer walks memory in row order, with the last index varying fastest
rule_id: PF-03
domain: performance
triggers: ['\]\[', '\[\]\[\]', 'new \w+\[\w+\]\[\w+\]', '\* (width|cols|columns|stride|rowLength|pitch)\b', 'ByteBuffer']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A nested loop over a two-dimensional array or a flat buffer walks memory in row order, with the last index varying fastest

## Thesis
A loop nest that touches every element of `a[i][j]` — or of a flat array addressed as `a[i * width + j]` — keeps `i` in the outer loop and `j` in the inner loop, so consecutive iterations touch consecutive memory. A nest written with the first index varying fastest (`a[j][i]` with `i` in the outer loop) is interchanged.

## Rationale
A Java two-dimensional array is an array of arrays: `a[i]` is a separate heap object holding `a[i][0..n-1]` contiguously, and `a[i+1]` is another object elsewhere. With the last index varying fastest the inner loop walks one row linearly, each 64-byte cache line fetched serves the next several elements, and the hardware prefetcher stays ahead of the loop. With the first index varying fastest each inner iteration jumps to a different row object, so every access can miss the cache and the row reference is reloaded on each step. A JMH comparison of the two orders over a 2048 × 2048 `int[][]` is the reference measurement; the same holds for a flat buffer indexed as `i * width + j`.

## Example
```java
bad:  for (int i = 0; i < n; i++)
          for (int j = 0; j < n; j++) grid[j][i] = f(i, j);   // jumps to a new row each step
good: for (int j = 0; j < n; j++)
          for (int i = 0; i < n; i++) grid[j][i] = f(i, j);   // walks one row
```

## Limits
Applies to nests that traverse a whole array or a large region on a hot path. A nest whose inner loop is short (a handful of columns) or that runs once at startup is out of scope. An algorithm that must traverse by column (a transpose, a column reduction) either tiles the traversal or stores the data transposed; the finding then names the layout, not the loop order. A tolerance in the project context — "matrix sizes stay under a few kilobytes" — rejects the finding.

## Validator
On the triggered hunk find each two-level (or deeper) loop nest indexing an array of arrays or a flat buffer with an `i * width + j` style expression. Match the index that the inner loop varies against the position it occupies: the inner variable must be the last subscript, or the term not multiplied by the row width. Validator question: **does the inner loop vary the first subscript, or the multiplied term, so that consecutive iterations touch different rows?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-03`, severity minor, `file`, `symbol`, `code` = the loop headers and the indexed access quoted verbatim from the diff, `fix` = the interchanged nest, `rationale` naming the per-iteration row jump and the cache miss it causes).

## Source
JMH benchmark `ionutbalosin/jvm-performance-benchmarks`, `.../compiler/LoopInterchangeBenchmark.java` — `initial_loop` (`lA[j][i]` with `i` outer) against `manual_loop_interchange` (`j` outer) over a 2048 × 2048 `int[][]`; its note: interchange "is often done to ensure that the elements of a multi-dimensional array are accessed in the order in which they are present in memory, improving locality of reference". JLS §10.2 and §15.10.2 — a multidimensional array is an array whose components are arrays, each a separately created object — not fetched from the authoring environment.
