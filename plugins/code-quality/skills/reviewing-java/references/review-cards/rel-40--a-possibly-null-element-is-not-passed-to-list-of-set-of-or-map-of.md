---
title: A value that can be null is not passed to List.of, Set.of, Map.of or copyOf, which reject null elements
rule_id: REL-40
domain: reliability
triggers: ['List[.]of\(', 'Set[.]of\(', 'Map[.]of\(', 'Map[.]entry\(', 'List[.]copyOf\(', 'Set[.]copyOf\(', 'Map[.]copyOf\(', 'Stream[.]of\(', '[.]toList\(\)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A value that can be null is not passed to List.of, Set.of, Map.of or copyOf, which reject null elements

## Thesis
The arguments of `List.of`, `Set.of`, `Map.of`, `Map.entry`, `List.copyOf`, `Set.copyOf` and `Map.copyOf` are values that cannot be null: a field with a default, a literal, a checked parameter; a value that may be null — a getter on an optional property, a `Map.get` result, a nullable DTO field — is filtered or defaulted first, or the code builds an `ArrayList`/`HashMap`, which permit null.

## Rationale
The unmodifiable collections "disallow null elements. Attempts to create them with null elements result in NullPointerException". Code migrated from `Arrays.asList` or `new ArrayList<>(...)`, which accept null, keeps the same call shape and passes every test whose fixtures fill every field, then throws on the first record with an absent optional value — in a mapper, a serializer or a cache fill far from the null's origin. `Stream.toList()` permits null; `Collectors.toUnmodifiableList()` does not.

## Example
```java
bad:  List<String> parts = List.of(user.firstName(), user.middleName(), user.lastName());   // middle may be null
good: List<String> parts = Stream.of(user.firstName(), user.middleName(), user.lastName())
          .filter(Objects::nonNull).toList();
```

## Limits
Arguments that are literals, enum constants, non-null-annotated values, or values guarded in the same method are out of scope. A `copyOf` of a collection built from non-null sources is correct.

## Validator
On the triggered hunk find each null-rejecting factory call and read each argument's origin: an optional getter, a `Map.get`, a nullable field or parameter. Validator question: **can one of these arguments be null at runtime?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-40`, severity major, `file`, `symbol`, `code` = the factory call quoted verbatim from the diff, `fix` = a null filter or default before the factory, or a null-permitting collection, `rationale` naming the `NullPointerException` on an absent value).

## Source
`java.util.List` class Javadoc, Java SE 21, "Unmodifiable Lists" — "They disallow null elements. Attempts to create them with null elements result in NullPointerException"; `java.util.Set` and `java.util.Map` class Javadoc carry the same characteristic for `Set.of`, `Map.of`, `Map.entry` and `copyOf`; `java.util.stream.Stream#toList()` implSpec — the list is built "as if by" `Collections.unmodifiableList(new ArrayList<>(Arrays.asList(this.toArray())))`, which admits null; `java.util.stream.Collectors#toUnmodifiableList()` — "The returned Collector disallows null values and will throw NullPointerException if it is presented with a null value".
