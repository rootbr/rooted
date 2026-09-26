---
title: UPPER_SNAKE_CASE names only a static final field whose contents are deeply immutable, and a mutable static final is lowerCamelCase
rule_id: MNT-04
domain: maintainability
triggers: ['static final [\w<>\[\], ?]+\s+[A-Z][A-Z0-9_]+\s*=\s*new ', 'static final [\w<>\[\], ?]+\s+[A-Z][A-Z0-9_]+\s*=\s*\{', 'static final (Logger|Log|Map|List|Set|Collection|Queue|Deque|StringBuilder|Date|Calendar|Random|AtomicInteger|AtomicLong)\b', 'static final [\w<>\[\], ?]+\s+[a-z]\w*\s*=\s*(\d|"|true|false|null|[A-Z]\w*[.]of\()']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# UPPER_SNAKE_CASE names only a static final field whose contents are deeply immutable, and a mutable static final is lowerCamelCase

## Thesis
A `static final` field is named in `UPPER_SNAKE_CASE` only when its contents are deeply immutable and its methods have no detectable side effects — a primitive, a `String`, an immutable value, `List.of(...)`; a `static final` whose observable state can change — a `new ArrayList<>()`, a `new HashMap<>()`, a non-empty array, a `Logger` — is named in `lowerCamelCase`, and an immutable constant is not left in `lowerCamelCase`.

## Rationale
The all-caps name promises the reader that the value cannot change, so code that reads it is written without defensive copies and without synchronization. A mutable collection or array behind such a name is shared mutable static state wearing the badge of a constant: a later `NAMES.add(x)` reads as a mistake but compiles. Naming the field in `lowerCamelCase` keeps the promise honest; intending never to mutate the object is not enough.

## Example
```java
bad:  static final Set<String> ROLES = new HashSet<>();
      static final String[] HEADERS = {"id", "name"};
      static final int maxRetries = 3;
good: static final Set<String> ROLES = Set.of("admin", "user");
      static final List<String> HEADERS = List.of("id", "name");
      static final int MAX_RETRIES = 3;
```

## Limits
A `static final` empty array (`static final Foo[] EMPTY = {}`) is a constant — nothing in it can change. A `static final` `Logger` is named `logger` or `log`. A style declared in the project context that names every `static final` in caps rejects the finding. Whether the static mutable collection should exist at all is a separate concern.

## Validator
On the triggered hunk take each added `static final` field. Decide whether its initializer produces a deeply immutable value (primitive, `String`, enum constant, `List.of`/`Set.of`/`Map.of`, an immutable value class) or a mutable one (a `new` collection, a non-empty array, a builder, a logger, a `Random`, an atomic). Validator question: **is the field's case shape the opposite of its mutability — caps on a mutable object, or lowerCamelCase on an immutable constant?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-04`, severity suggestion, `file`, `symbol`, `code` = the field declaration quoted verbatim from the diff, `fix` = the renamed field, or an immutable initializer that earns the caps name, `rationale` naming the false promise of immutability).

## Source
Google Java Style Guide §5.2.4 "Constant names" — "Constants are static final fields whose contents are deeply immutable and whose methods have no detectable side effects … If any of the instance's observable state can change, it is not a constant. Merely intending to never mutate the object is not enough"; listed non-constants include `static final Set<String> mutableCollection = new HashSet<String>()`, `static final Logger logger` and `static final String[] nonEmptyArray`; `static final SomeMutableType[] EMPTY_ARRAY = {}` is a constant.
