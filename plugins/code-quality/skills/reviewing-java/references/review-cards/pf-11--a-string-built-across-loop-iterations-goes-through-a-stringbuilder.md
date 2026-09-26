---
title: A string built across the iterations of a loop is accumulated in a StringBuilder, never by += on a String
rule_id: PF-11
domain: performance
triggers: ['\+= ', '\+=\s*"', 'String \w+ = ""', '[.]concat\(', 'StringBuilder']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A string built across the iterations of a loop is accumulated in a StringBuilder, never by += on a String

## Thesis
When a loop appends to a string on every iteration — `s += part`, `s = s + part`, `s = s.concat(part)` — the accumulator is a `StringBuilder`, sized when the final length is known, and `toString()` runs once after the loop. A single concatenation expression outside a loop is fine as `+`.

## Rationale
Strings are constant: their values cannot be changed after they are created, so each `s += part` builds a new `String` whose array holds a copy of everything accumulated so far plus the new part. Over n iterations that is n allocations and n copies of growing length — quadratic work and garbage for a linear task. A `StringBuilder` keeps one growable buffer: appends write into spare capacity and the buffer is reallocated only when it overflows, so the copying is amortized linear and one `String` is created at the end. The compiler's optimization of a single `+` expression does not extend across loop iterations.

## Example
```java
bad:  String csv = "";
      for (String v : values) csv += v + ",";
good: StringBuilder csv = new StringBuilder(values.size() * 8);
      for (String v : values) csv.append(v).append(',');
      String out = csv.toString();
```

## Limits
A loop of at most a few iterations off the hot path, and a `+` inside the loop whose result is consumed per iteration (a log line, a key) rather than accumulated, are out of scope. `String.join` and `Collectors.joining` are correct forms. A `StringBuffer` is a synchronized `StringBuilder` and is not needed in single-threaded code.

## Validator
On the triggered hunk find each `+=`, `s = s + …` or `concat` whose target is a `String` variable declared outside the enclosing `for`, `while` or `forEach` body and assigned inside it. Validator question: **does this loop grow a String accumulator by concatenation on each iteration?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-11`, severity minor, `file`, `symbol`, `code` = the accumulator declaration and the concatenation quoted verbatim from the diff, `fix` = the `StringBuilder` form with a single `toString()`, `rationale` naming the per-iteration copy of the whole accumulated string).

## Source
`java.lang.String` class Javadoc, Java SE 21 — "Strings are constant; their values cannot be changed after they are created. String buffers support mutable strings"; implementation note — the `+` operator is compiled through `StringBuilder` or `StringConcatFactory` per expression. `java.lang.StringBuilder` class Javadoc — "As long as the length of the character sequence contained in the string builder does not exceed the capacity, it is not necessary to allocate a new internal buffer. If the internal buffer overflows, it is automatically made larger." JLS §15.18.1 — the `String` object is newly created unless the expression is a constant expression — not fetched from the authoring environment. JMH benchmark `ionutbalosin/jvm-performance-benchmarks`, `.../api/string/StringConcatenationBenchmark.java` — `StringBuilder`, `StringBuffer`, `String.concat` and `+` on the same inputs.
