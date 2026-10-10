---
title: A quantity that must be exact in decimal, such as an amount of money, is never held or computed in binary floating point, and its decimal value is built from a string or an integer rather than converted from a binary float
rule_id: CODE-84
domain: code
step: [design, implement]
applies_to: [universal]
triggers: ['(?i)\b(?:double|float|f32|f64|float32|float64|number)\b[^;=\n]*\b(?:price|amount|cost|total|balance|money|fee|tax|salary|payment|cents|dollars|euros|subtotal|refund|invoice)\w*', '(?i)\b(?:price|amount|cost|balance|fee|tax|salary|payment|total|subtotal|refund)\w*(?:\s*:\s*(?:float|number|f64|f32|float64|float32|double)|\s+(?:float|float32|float64|double|real))\b', '[.]toFixed\(\s*2\s*\)|\bround\([^)]*,\s*2\s*\)|\bnew\s+BigDecimal\(\s*-?\d+[.]\d+|\bDecimal\(\s*-?\d+[.]\d+\s*\)|\bDecimal[.]from_float\(']
scope: file
check_kind: semantic
severity_default: major
---

# A quantity that must be exact in decimal, such as an amount of money, is never held or computed in binary floating point, and its decimal value is built from a string or an integer rather than converted from a binary float

## Thesis
A quantity whose required precision is set by a fixed number of digits to the right of the decimal point, and whose sums, differences and equality tests must come out exact, such as a currency amount or an accounting total, is held and computed in a decimal type or as an integer count of a fixed smallest unit, and its decimal value is built from a string or an integer rather than from a binary float.

## Rationale
Binary floating point has no exact representation of 0.1, 1.1 or 2.2, so such a value is stored as the nearest representable binary value, and every floating-point operation can add a new rounding error. In binary floating point 1.1 + 2.2 displays as 3.3000000000000003, and 0.1 + 0.1 + 0.1 − 0.3 is 5.5511151231257827e-017 where decimal arithmetic gives exactly zero; the differences prevent reliable equality testing and accumulate, which is why decimal arithmetic is preferred where accounting has strict equality invariants. A decimal that a constructor converts exactly from the float 0.1 takes the float's exact binary value, 0.1000000000000000055511151231257827021181583404541015625, while a decimal built from the string "0.1" is exactly 0.1. Rounding a binary float to a fixed number of places can round the stored value rather than the written one: 2.55 rounded to one place can give 2.5, because the closest representable float is lower. An integer count of the smallest unit relies on every amount having the same fixed number of decimal places; that may not work across currencies, which differ in decimal places, nor where fractional parts of the smallest unit occur, as in stock trading and currency conversion, and there a decimal type, or whole units paired with an integer count of a finer unit such as 10⁻⁹ of the currency unit, holds the value. Automated detection cannot determine in the general case which code suffers from insufficient precision, so the check rests on what the value means.

## Example
```typescript
bad:  function orderTotal(lines: { qty: number, price: number }[]): number {
        let total: number = 0;
        for (const line of lines) total += line.price * line.qty;
        return Number(total.toFixed(2));
      }
good: function orderTotalCents(lines: { priceCents: bigint, qty: number }[]): bigint {
        let totalCents = 0n;
        for (const line of lines) totalCents += line.priceCents * BigInt(line.qty);
        return totalCents;
      }
```

## Limits
A value that need not be exact stays in binary floating point: on most machines its error is on the order of no more than 1 part in 2^53 per operation, more than adequate for most tasks, and the decimal type is meant for use cases that require exact decimal representation; values that need not be precise can be compared for equality within a range. A program whose recorded trade-off puts performance above accuracy, or minimal storage first, as for very large data sets where 4 bytes per value against 16 adds up, may hold decimal data in binary floating point; the documented speed difference goes unnoticed by all but the most calculation-intensive applications. A conversion that goes through the float's string form, or yields the shortest decimal that converts back to the same float, which for the float 0.1 is "0.1", builds the decimal from a string, and when that string equals the float literal's value, as "0.1" does for the literal 0.1, the decimal has the literal's value, so it is not flagged; a whole number larger than 2^53 can change in that conversion, as the float 2^62, exactly 4611686018427387904, converts to 4611686018427388000, and a float produced by arithmetic already carries the error, as the 5.5511151231257827e-017 above shows. Outside the rule: the choice between a decimal type and an integer unit, the rounding policy and cumulative error of a decimal computation, the allocation of a remainder when an amount is split, and equality between decimal values of different scale.

## Validator
Grep the hunk for a binary floating-point type on a variable, field, parameter, return value or column whose name or use denotes money or an accounting quantity (price, amount, cost, total, balance, fee, tax, payment, refund, invoice), for a decimal value constructed from a float literal or a float variable, and for a float rounded or formatted to two places. Open the file and trace the value: where it is parsed, stored, summed, compared for equality, rounded and emitted. Decide from that trace whether the quantity must be exact in decimal, because it is billed, booked, reconciled, compared for equality or summed into a total that must balance, or need not be exact under the Limits. Validator question: **Does the diff hold or compute a quantity that must be exact in decimal in a binary floating-point type, or build that quantity's decimal value directly from a binary float rather than from a string or an integer?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-84`, severity major, `file`, `symbol`, `code` = the declaration, field, column, arithmetic or conversion that holds the amount in binary floating point, quoted verbatim from the diff, `fix` = the same quantity in the file's decimal type or as an integer count of the smallest unit, with any decimal value built from a string or an integer, in the file's language, `rationale` = names the decimal value the binary float cannot hold exactly and the total, equality test or rounding that the error breaks).
