---
title: Optional.of wraps a value proven non-null, and a value that may be null is wrapped with Optional.ofNullable
rule_id: MNT-18
domain: maintainability
triggers: ['Optional[.]of\(', 'Optional[.]ofNullable\(']
scope: file
check_kind: semantic
severity_default: major
---

# Optional.of wraps a value proven non-null, and a value that may be null is wrapped with Optional.ofNullable

## Thesis
`Optional.of(x)` is called only where `x` cannot be `null` — a literal, a fresh object, a value already checked; a value that may be `null` — a map lookup, a getter of a nullable field, a nullable parameter, a JDBC column, a JSON property — is wrapped with `Optional.ofNullable(x)`, which yields an empty `Optional` for `null`.

## Rationale
`Optional.of` throws `NullPointerException` for a `null` argument, so wrapping a nullable value with it turns the absence the `Optional` was meant to represent into the crash it was meant to prevent, at the wrap site rather than at the use site, while the code reads as if the case were handled. `ofNullable` is the factory that maps `null` to empty; the choice between the two is a statement about the argument, and the wrong statement is a latent NPE on the path where the value is missing.

## Example
```java
bad:  return Optional.of(cache.get(key));            // get returns null when absent
      return Optional.of(user.getMiddleName());      // nullable field
good: return Optional.ofNullable(cache.get(key));
      return Optional.ofNullable(user.getMiddleName());
```

## Limits
`Optional.of(new X())`, `Optional.of("literal")`, and `Optional.of(x)` after a `null` check or `Objects.requireNonNull(x)` are correct. An argument of a primitive-wrapping or non-null-annotated type in a `@NullMarked` scope is proven non-null by the checker. Where the project context states that a `null` argument is a programming error to fail fast on, `of` is the intended assertion.

## Validator
On the triggered hunk find each `Optional.of(expr)`. Open the file and trace `expr`: a `Map.get`, a getter or field that can hold `null`, a parameter without a non-null guarantee, a method whose Javadoc or annotation says nullable. Validator question: **can the argument to this `Optional.of` be `null` on some path?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-18`, severity major, `file`, `symbol`, `code` = the `Optional.of` call quoted verbatim from the diff, `fix` = `Optional.ofNullable`, `rationale` naming the path on which the argument is `null`).

## Source
`java.util.Optional#of(T)` Javadoc, Java SE 21 — "Returns an Optional describing the given non-null value … @throws NullPointerException if value is null"; `#ofNullable(T)` — "Returns an Optional describing the given value, if non-null, otherwise returns an empty Optional".
