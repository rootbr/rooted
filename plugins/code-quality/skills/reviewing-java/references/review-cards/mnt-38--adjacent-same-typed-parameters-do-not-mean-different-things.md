---
title: A method does not take adjacent parameters of one primitive or String type that mean different things
rule_id: MNT-38
domain: maintainability
triggers: ['\((\s*(String|long|int|double|BigDecimal)\s+\w+\s*,\s*){2,}', 'String \w+, String \w+', '(long|int) \w+, (long|int) \w+', 'record \w+\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A method does not take adjacent parameters of one primitive or String type that mean different things

## Thesis
A method or constructor does not take two or more adjacent parameters of the same primitive or `String` type that carry different meanings — `(String from, String to, long cents, String currency)` — because a call that transposes two of them compiles and passes every type check. The remedy is one of three: a small value type per concept (a record such as `AccountNumber` or `Money`, whose canonical constructor validates it, so that passing `to` where `from` belongs no longer compiles), a parameter object that groups the related values, or a parameter-name comment at each call site (`/* from= */ a, /* to= */ b`) where a type is not warranted.

## Rationale
Positional arguments of one type cannot be told apart by the compiler, so a swapped pair compiles, passes every type check, and fails at run time on the first call that goes the wrong way; a static checker can only guess from name similarity that arguments were transposed, and a deliberate swap looks the same to it as an accidental one. A distinct type per concept moves the distinction into the signature and its validation into one constructor; a parameter object names the group and removes the positional list; a call-site comment makes the intended order visible to the reader and to the checker. The hazard is largest for identifiers, amounts, quantities with units, and codes.

## Example
```java
bad:  Transfer make(String fromAccount, String toAccount, long amountInCents, String currency)
      make(to, from, 1_000, "EUR");            // compiles; swaps the accounts
good: record AccountNumber(String value) { AccountNumber { if (!value.matches("\\d{9}")) throw new IllegalArgumentException(value); } }
      record Money(long cents, Currency currency) {}
      Transfer make(AccountNumber from, AccountNumber to, Money amount)
```

## Limits
Two parameters of one type that are interchangeable (`min`/`max` of a range, `x`/`y` of a point) or that a well-known API fixes (`substring(begin, end)`) are not this finding. A DTO mapped by a framework from JSON or a database row keeps primitive fields; the value type appears at the domain boundary. A no-wrapper policy for a hot path declared in the project context rules out the value type, and the parameter object or the call-site comment remains.

## Validator
On the triggered hunk find each declaration with two or more adjacent parameters of the same primitive or `String` type. Ask what each denotes; check whether a call site in the hunk passes them positionally without a parameter-name comment. Validator question: **would swapping two of these arguments compile while meaning something else?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-38`, severity minor, `file`, `symbol`, `code` = the declaration quoted verbatim from the diff, `fix` = the value types and the typed signature, a parameter object, or the call-site parameter-name comments, `rationale` naming the swap the compiler cannot see).

## Source
Error Prone `ArgumentSelectionDefectChecker` — "Arguments are in the wrong order or could be commented for clarity"; a permutation of same-typed arguments whose names better match the parameters "might indicate that they have been accidentally swapped", and for a deliberate mismatch "we suggest annotating the names with a comment to make the deliberate swap clear to future readers of the code", since "argument names annotated with a comment containing the parameter name will not generate a warning". PMD `ExcessiveParameterList` — "When parameters share similar datatypes, they become prone to mix-ups during refactoring or when calling the method with positional arguments"; among its alternatives, "Multiple Parameter Objects (grouping related parameters into dedicated classes)". `java.lang.Record` Javadoc, Java SE 21 — an explicit canonical constructor exists "to validate constructor arguments". Caveat: the sources state the hazard, the call-site comment and the parameter object; the value type as a remedy rests on the swap becoming a type error and on the record's validating constructor.
