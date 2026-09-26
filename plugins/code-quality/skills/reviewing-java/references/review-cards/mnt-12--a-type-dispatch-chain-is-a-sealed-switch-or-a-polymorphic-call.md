---
title: A chain of instanceof tests or a switch on a type tag is an exhaustive switch over a sealed hierarchy or a polymorphic call
rule_id: MNT-12
domain: maintainability
triggers: ['instanceof', 'getClass\(\)', 'switch\s*\(.*(kind|type|Kind|Type)', '\(\(\w+\)\s*\w+\)', 'default\s*(:|->)\s*throw', 'sealed |permits ']
scope: file
check_kind: semantic
severity_default: minor
---

# A chain of instanceof tests or a switch on a type tag is an exhaustive switch over a sealed hierarchy or a polymorphic call

## Thesis
Dispatch on the runtime type of a value — an `if (x instanceof A) … else if (x instanceof B)` chain, a `switch` on a `kind` or `type` field, a cast guarded by a type check — is written either as a method the types implement (each subtype carries its own branch) or, for a closed set of variants, as a `switch` with type patterns over a `sealed` interface, whose missing case is a compile error rather than a `default: throw`.

## Rationale
A type-test chain lives outside the types it tests, so adding a variant means finding every chain and adding a branch; a forgotten one surfaces at runtime in the `else` or `default`. With the variants declared as `sealed … permits A, B, C`, a pattern `switch` without `default` is checked for exhaustiveness: the compiler rejects a switch that does not cover all possible input values, so a new variant fails the build at every dispatch site until handled. A polymorphic method does the same through virtual dispatch, at the cost of putting the operation on the type.

## Example
```java
bad:  double area(Shape s) {
          if (s instanceof Circle) { return PI * ((Circle) s).r() * ((Circle) s).r(); }
          else if (s instanceof Square) { return ((Square) s).side() * ((Square) s).side(); }
          throw new IllegalArgumentException("unknown " + s); }
good: sealed interface Shape permits Circle, Square {}
      double area(Shape s) { return switch (s) { case Circle c -> PI * c.r() * c.r();
                                                  case Square q -> q.side() * q.side(); }; }
```

## Limits
A single `instanceof` used as a guard, an `equals` implementation, and dispatch over an open set the code does not own (`Object`, a library interface) are not flagged; there, pattern matching for `instanceof` replaces the cast. A `switch` over an enum with every constant covered and no `default` is already exhaustive. Code compiled below Java 21 (pattern `switch`) or below 17 (`sealed`) takes the polymorphic form; a JDK version in the project context sets which fix applies.

## Validator
On the triggered hunk find each chain of two or more type tests over the same value, each `switch` on a type-tag field, and each `default` that throws for an "unknown" case. Open the file to see whether the tested types are the project's own and whether the set is closed. Validator question: **does this code branch on a value's runtime type or type tag across a set the project owns, with the branches outside the types?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-12`, severity minor, `file`, `symbol`, `code` = the type-test chain or the tagged switch quoted verbatim from the diff, `fix` = the sealed interface with a pattern switch, or the method moved onto the types, `rationale` naming the variant a future change forgets).

## Source
JEP 409 "Sealed Classes" and JEP 441 "Pattern Matching for switch" — a `switch` over a sealed hierarchy with type patterns must be exhaustive and the compiler checks it; JLS §14.11.1.1 "Exhaustive Switch Blocks". OpenJDK `javac` `compiler.properties` (tag `jdk-21-ga`) — `compiler.err.not.exhaustive.statement`: "the switch statement does not cover all possible input values". Error Prone `PatternMatchingInstanceof` — pattern matching replaces an `instanceof` followed by a separate cast.
