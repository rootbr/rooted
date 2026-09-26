---
title: A hand-rolled array copy, array comparison, bit count or math primitive on a hot path is the JDK method the virtual machine intrinsifies
rule_id: PF-14
domain: performance
triggers: ['for \(int \w+ = 0; \w+ < \w+[.]length', '\[[^\]]+\] = \w+\[[^\]]+\]', '!= \w+\[\w+\]', '>>>?= 1\b', '\? \w+ : \w+;', 'Math[.](sqrt|abs|max|min)\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A hand-rolled array copy, array comparison, bit count or math primitive on a hot path is the JDK method the virtual machine intrinsifies

## Thesis
A loop that copies one array into another element by element is `System.arraycopy` or `Arrays.copyOf`/`copyOfRange`; a loop that compares two arrays element by element is `Arrays.equals` or `Arrays.mismatch`; a loop that counts or scans bits is `Integer.bitCount`, `numberOfLeadingZeros` or `numberOfTrailingZeros` (or the `Long` forms); an inline `(a < b) ? a : b`, sign test or square-root routine is `Math.min`, `Math.max`, `Math.abs` or `Math.sqrt`. The JDK method is chosen wherever it has the same contract.

## Rationale
These methods are annotated `@IntrinsicCandidate`: the HotSpot virtual machine may replace the annotated method with hand-written assembly or compiler IR — a compiler intrinsic — to improve performance. An intrinsified `arraycopy` becomes a vectorized memory move with the bounds and store checks hoisted out; `Arrays.equals` and `mismatch` compare a vector width of elements per instruction; `bitCount` and the leading- and trailing-zero methods become one processor instruction where the CPU offers it; `Math.sqrt` becomes a single floating-point instruction. A hand-written loop compiles to per-element loads, compares, bounds checks and branches, and the compiler's own vectorizer recognizes only some loop shapes. The intrinsic form is also the one the JDK keeps correct on every platform.

## Example
```java
bad:  for (int i = 0; i < n; i++) dst[i + off] = src[i];
      boolean same = true; for (int i = 0; i < a.length; i++) if (a[i] != b[i]) same = false;
      int bits = 0; for (int v = x; v != 0; v >>>= 1) bits += v & 1;
good: System.arraycopy(src, 0, dst, off, n);
      boolean same = Arrays.equals(a, b);
      int bits = Integer.bitCount(x);
```

## Limits
Applies to a loop whose only work is the copy, comparison, count or arithmetic the JDK method performs. A loop that transforms elements while copying, compares under a custom equivalence, or short-circuits with side effects has no drop-in intrinsic. An array `clone()` is an intrinsified form as well, through `Object.clone`; `Arrays.fill` is not. Intrinsification is "may, not guaranteed": on a platform without the instruction the JDK method still runs as Java and is no slower than the loop.

## Validator
On the triggered hunk find each loop over array indices whose body only copies elements, compares corresponding elements, accumulates the bits of one value, or computes a min, max, abs or square root by hand. Map it to the JDK method with the same contract. Validator question: **does this hot loop or expression re-implement a copy, compare, bit-count or math method that the JDK provides as an intrinsic candidate?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-14`, severity minor, `file`, `symbol`, `code` = the loop or expression quoted verbatim from the diff, `fix` = the JDK call, `rationale` naming the intrinsic that replaces it).

## Source
`jdk.internal.vm.annotation.IntrinsicCandidate` Javadoc, Java SE 21 — "an annotated method may be (but is not guaranteed to be) intrinsified by the HotSpot VM. A method is intrinsified if the HotSpot VM replaces the annotated method with hand-written assembly and/or hand-written compiler IR -- a compiler intrinsic -- to improve performance". In the `jdk-21-ga` source the annotation is carried by `System.arraycopy`, `Object.clone`, the `Class`-typed `Arrays.copyOf(U[], int, Class)` and `copyOfRange(U[], int, int, Class)` overloads (the primitive `copyOf` and `copyOfRange` overloads reach the intrinsic through `System.arraycopy` or `clone()`; no `Arrays.fill` overload carries it), `Arrays.equals(byte[], byte[]) and `equals(char[], char[])`, `jdk.internal.util.ArraysSupport.vectorizedMismatch` (behind `Arrays.equals` and `Arrays.mismatch` for the other element types), `Integer.bitCount`, `Integer.numberOfLeadingZeros`, `Integer.numberOfTrailingZeros`, `Math.abs`, `Math.min(int, int)`, `Math.max(int, int)`, `Math.sqrt`, `Math.log` and `Math.pow`, among others.
