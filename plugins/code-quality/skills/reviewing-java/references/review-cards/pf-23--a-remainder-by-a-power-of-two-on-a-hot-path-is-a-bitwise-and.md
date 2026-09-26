---
title: A remainder by a power-of-two size on a hot path is a bitwise AND of a non-negative value, and a remainder by a runtime-variable divisor is restructured
rule_id: PF-23
domain: performance
triggers: ['\s%\s', '%=', 'floorMod\(', '& \(\w+ - 1\)', 'ringSize|capacity - 1|mask']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A remainder by a power-of-two size on a hot path is a bitwise AND of a non-negative value, and a remainder by a runtime-variable divisor is restructured

## Thesis
An index computation `x % size` on a per-element or per-message path — a hash-table bucket, a ring-buffer slot, a shard selector — uses a power-of-two `size` and computes `x & (size - 1)` on a value known to be non-negative, or on a hash whose masked residue is the intended index. A `%` whose divisor is neither a compile-time constant nor a power of two is restructured: a counter that wraps by comparison, a size rounded up to a power of two, or a precomputed multiplier.

## Rationale
Integer division and remainder run on the hardware divider: on current x86-64 parts the 32-bit `idiv` and `div` instructions have a latency of 26 cycles, against 3 cycles for a multiply and a single AND instruction for the masked form. When the divisor is a compile-time constant the just-in-time compiler already replaces the division by a multiply-and-shift sequence — and a remainder by a power-of-two constant, on a dividend known to be non-negative, by an AND — so no action is needed; when the divisor is a runtime value — a field, a parameter, a size read from configuration — the division executes on every evaluation. For a power-of-two divisor and a non-negative dividend, `x & (size - 1)` is the remainder in one instruction, which is the form the JDK's own hash table uses for its bucket index. The two forms are not interchangeable for negative dividends: Java's `%` yields a negative remainder (`-7 % 4 == -3`) while `-7 & 3 == 1`, so a replacement is shown correct for the dividend's range or the dividend is made non-negative first.

## Example
```java
bad:  int slot = seq % ring.length;               // ring.length a runtime value
      int bucket = key.hashCode() % table.length;  // negative for a negative hash code
good: int slot = (int) (seq & (ring.length - 1)); // ring.length kept a power of two, seq >= 0
      int bucket = key.hashCode() & (table.length - 1);   // non-negative index, as in the JDK
```

## Limits
A `%` with a compile-time constant divisor (a literal or a `static final` primitive) is already strength-reduced by the compiler and is not flagged. A `%` off the hot path — a formatting routine, a once-per-request computation — is not worth restructuring. The AND form requires the size to be a power of two; a size that is not (a shard count of 12) stays with `%` or `Math.floorMod` unless the design can round it up. A replacement on a possibly-negative value must be shown correct for that range.

## Validator
On the triggered hunk find each `%` or `%=` whose right operand is not a compile-time constant. Confirm the expression runs per element, per message or per iteration, and whether the divisor is (or can be made) a power of two and the dividend is non-negative or a hash whose masked residue is acceptable. Validator question: **does this hot path compute a remainder by a runtime-variable divisor where a power-of-two AND, or a restructured wrap, would serve?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-23`, severity minor, `file`, `symbol`, `code` = the `%` expression quoted verbatim from the diff, `fix` = the `& (size - 1)` form with its non-negative precondition, or the restructured counter, `rationale` naming the hardware division per evaluation).

## Source
Lemire, Kaser, Kurz, "Faster Remainder by Direct Computation", Software: Practice and Experience 49(6), 2019, arXiv:1902.01961 (read through alphaXiv's text of the paper) — division instructions on Skylake "have 26 cycles of latency for 32-bit registers", multiplication instructions "produce the full 128-bit product in three cycles"; compilers replace division by a constant with the Granlund-Montgomery multiply-shift; the power-of-two case "follows by inspection". HotSpot `src/hotspot/share/opto/divnode.cpp` (jdk-21-ga) — `transform_int_divide` and `transform_long_divide`, "Convert a division by constant divisor into an alternate Ideal graph", through `magic_int_divide_constants` ("converting a 32 bit divide by constant into a multiply/shift/add series"); `ModINode::Ideal` rewrites a remainder by a power-of-two constant into an `AndINode` with `pos_con - 1` when the dividend's type is non-negative. `java.util.HashMap` source, Java SE 21 — `tab[(n - 1) & hash]` as the bucket index. `lemire/fastmod` README — the same division-versus-multiply claim for constant divisors. JLS §15.17.3 — the remainder takes the sign of the dividend — not fetched from the authoring environment.
