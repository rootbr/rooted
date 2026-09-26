---
title: An immutable data carrier with final fields set in the constructor and exposed by accessors is declared as a record
rule_id: MNT-15
domain: maintainability
triggers: ['private final \w[\w<>\[\], ?]*\s+\w+;', 'public \w[\w<>\[\], ?]*\s+get[A-Z]\w*\(\)\s*\{\s*return', 'public boolean equals\(Object', 'public int hashCode\(\)', '@Value\b|@Data\b|@AllArgsConstructor|@EqualsAndHashCode']
scope: file
check_kind: mechanical
severity_default: suggestion
---

# An immutable data carrier with final fields set in the constructor and exposed by accessors is declared as a record

## Thesis
A class whose purpose is to carry a fixed set of values — every field `private final`, assigned once in the constructor, each read by an accessor, with `equals`, `hashCode` and `toString` over all of them — is declared as a `record`, whose canonical constructor, accessors and the three `Object` methods the compiler supplies; validation and defensive copies go into a compact canonical constructor.

## Rationale
The hand-written form is fifty lines that say what one line says, and each of the three `Object` methods is a place where a field is forgotten when the next field is added. A record is by definition a shallowly immutable, transparent carrier for a fixed set of values: the fields, accessors, `equals`, `hashCode` and `toString` are derived from the components, so they cannot drift from the state, and the invariant that a copy built from the accessors equals the original holds for the compiler-derived members and must be preserved by an explicit one. The explicit canonical constructor remains for validating arguments, copying mutable components and normalizing.

## Example
```java
bad:  final class Money { private final long cents; private final Currency ccy;
          Money(long cents, Currency ccy) { this.cents = cents; this.ccy = ccy; }
          long getCents() { return cents; } Currency getCcy() { return ccy; }
          @Override public boolean equals(Object o) { ... } @Override public int hashCode() { ... } }
good: record Money(long cents, Currency ccy) {
          Money { Objects.requireNonNull(ccy); } }
```

## Limits
A class with mutable state, with identity semantics (a JPA entity), with fields outside its equality, that must extend another class, or that a framework requires to be a settable bean is not a record candidate. Code compiled below Java 16 has no records; a JDK version in the project context settles it. A Lombok `@Value` class serves the same purpose and is a lower-value finding unless the project is moving off Lombok.

## Validator
On the triggered hunk find each class that declares only `private final` fields set in one constructor plus accessors, or that hand-writes `equals`/`hashCode`/`toString` over all its fields. Open the file to confirm no mutable state, no superclass, and no framework constraint. Validator question: **is this class a fixed-set immutable value carrier that a record would express?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-15`, severity suggestion, `file`, `symbol`, `code` = the class header and one accessor or the `equals` quoted verbatim from the diff, `fix` = the record declaration with any compact constructor, `rationale` naming the drift risk in the hand-written members).

## Source
`java.lang.Record` class Javadoc, Java SE 21 — "A record class is a shallowly immutable, transparent carrier for a fixed set of values, called the record components"; the mandated canonical constructor, private final fields and public accessors; `equals`, `hashCode` and `toString` "derived from all of the component fields"; explicit declarations serve "to validate constructor arguments, perform defensive copies on mutable components, or normalize groups of components"; the invariant `new R(r.c1(), r.c2(), ..., r.cn())` equals `r`; JLS §8.10. JEP 395 "Records".
