---
title: Arithmetic whose overflow would corrupt a balance, a size or a count uses Math.addExact, multiplyExact or toIntExact, never a silently wrapping operator
rule_id: REL-04
domain: reliability
triggers: ['\bint\s+\w+\s*=\s*\w+\s*[+*]', '\blong\s+\w+\s*=\s*\w+\s*[+*]', '\(int\)\s*\(?\s*\w+', 'balance', 'capacity', 'total', '\* 1000\b']
scope: hunk
check_kind: semantic
severity_default: major
---

# Arithmetic whose overflow would corrupt a balance, a size or a count uses Math.addExact, multiplyExact or toIntExact, never a silently wrapping operator

## Thesis
An `int` or `long` addition, multiplication or narrowing cast whose result feeds a monetary amount, a quantity, an allocation size or an index is written with `Math.addExact`, `Math.subtractExact`, `Math.multiplyExact` or `Math.toIntExact`, so that an overflow throws `ArithmeticException` instead of producing a wrong value.

## Rationale
The `+`, `-` and `*` operators on `int` and `long` wrap on overflow: `Integer.MAX_VALUE + 1` is `Integer.MIN_VALUE`, and a cast `(int) longValue` keeps the low 32 bits. Nothing is thrown, so a balance goes negative, a computed capacity becomes a negative array size, or a duration in milliseconds is off by 2^32, and the wrong number is stored and propagated. An expression such as `1000 * 3600 * 24 * days` overflows in `int` before it is widened to `long`. The exact methods perform the same operation and throw `ArithmeticException` "if the result overflows an int" (or a long), which turns silent corruption into a visible failure at the site of the computation.

## Example
```java
bad:  int newBalance = balance + credit;
      long millis = 1000 * 3600 * 24 * days;
      int size = (int) count;
good: int newBalance = Math.addExact(balance, credit);
      long millis = 1000L * 3600 * 24 * days;
      int size = Math.toIntExact(count);
```

## Limits
Applies to values whose correctness matters: money, quantities, sizes, offsets, timestamps in milliseconds. A hash computation, a checksum, a random-number mix or a ring-buffer index that relies on wrap-around is correct with plain operators, and a comment saying so settles it. A loop counter bounded by a collection size, or arithmetic on values already proven to fit by a range check in the same method, needs no exact method. A project context that accepts wrap-around for a named statistic rejects the finding for that statistic.

## Validator
On the triggered hunk find each `+`, `-`, `*` on `int` or `long` operands and each `(int)` cast of a `long` whose result is assigned to, returned as, or compared against a balance, an amount, a count, a size, a capacity or a time value. Check whether the operands are bounded by a check in the same method, whether the expression is widened to `long` before the multiplication, and whether an exact method is used. Validator question: **can this expression overflow with inputs the method accepts, and would the wrapped result be stored or acted on as if correct?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-04`, severity major, `file`, `symbol`, `code` = the arithmetic expression quoted verbatim from the diff, `fix` = the same computation through `Math.addExact`, `multiplyExact`, `toIntExact` or a `long` widening before the operation, `rationale` naming the value that wraps and what it corrupts).

## Source
`java.lang.Math#addExact(int, int)`, `#multiplyExact`, `#toIntExact(long)` Javadoc, Java SE 21 — "Returns the sum of its arguments, throwing an exception if the result overflows an int"; `@throws ArithmeticException if the result overflows an int`; `toIntExact` — "throwing an exception if the value overflows an int". SEI CERT Oracle Coding Standard for Java, NUM00-J "Detect or prevent integer overflow". SpotBugs `ICAST_INTEGER_MULTIPLY_CAST_TO_LONG` — an `int` multiplication cast to `long` overflows before the widening.
