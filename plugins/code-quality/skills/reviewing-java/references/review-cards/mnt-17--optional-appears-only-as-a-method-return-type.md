---
title: Optional appears only as a method return type, never as a field, a parameter or a collection element
rule_id: MNT-17
domain: maintainability
triggers: ['Optional<[^>]+>\s+\w+\s*[;=]', '\(\s*Optional<', ',\s*Optional<', '(List|Set|Map|Collection)<[^>]*Optional<', 'private (final )?Optional<']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Optional appears only as a method return type, never as a field, a parameter or a collection element

## Thesis
`Optional<T>` is declared as the return type of a method that may have no result; a field, a constructor or method parameter, a collection element and a map value are declared as `T`, with absence expressed by a nullable reference annotated `@Nullable`, an overload, or an empty collection.

## Rationale
The type exists to make "no result" explicit at a method boundary where returning `null` is likely to cause errors; a variable of that type is itself a reference that should never be `null`, so an `Optional` parameter turns two states (present, `null`) into three (present, empty, `null` Optional) and forces every caller to wrap and every callee to unwrap without adding information. As a field it is not serializable, adds an allocation per instance, and its emptiness is as invisible to the constructor's caller as `null` was. An overload or a `@Nullable` parameter says the same thing without the wrapper.

## Example
```java
bad:  private Optional<String> nickname;
      void rename(String name, Optional<String> nickname) { ... }
good: private @Nullable String nickname;
      void rename(String name) { ... }
      void rename(String name, String nickname) { ... }
      Optional<User> findByEmail(String email) { ... }
```

## Limits
A local variable holding a method's `Optional` result is fine. A private field that caches an `Optional` result verbatim for a documented reason is tolerated by a note in the project context. A generic type parameter bound such as `Function<T, Optional<R>>` describes a return and is not flagged. `OptionalInt`, `OptionalLong` and `OptionalDouble` follow the same rule.

## Validator
On the triggered hunk find each `Optional<…>` in a field declaration, a parameter list, or a collection or map type argument. Validator question: **is `Optional` used in a position other than a method's return type?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-17`, severity minor, `file`, `symbol`, `code` = the declaration quoted verbatim from the diff, `fix` = the `@Nullable` reference, the overload, or the plain element type, `rationale` naming the third state the wrapper adds).

## Source
`java.util.Optional` class Javadoc, Java SE 21, API note — "Optional is primarily intended for use as a method return type where there is a clear need to represent 'no result,' and where using null is likely to cause errors. A variable whose type is Optional should never itself be null; it should always point to an Optional instance". SonarSource `java:S3553` "Optional should not be used for parameters" — "With an Optional parameter, you go from having 2 possible inputs: null and not-null, to three: null, non-null-without-value, and non-null-with-value … overloading has long been available to convey that some parameters are optional" (rule text from the `sonar-java` 6.15.1 plugin resources).
