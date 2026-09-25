---
title: An unmodifiable copy or constant collection is List.copyOf, List.of, Set.copyOf or Map.copyOf, never Collections.unmodifiable* over a freshly allocated copy
rule_id: PF-08
domain: performance
triggers: ['unmodifiableList\(', 'unmodifiableSet\(', 'unmodifiableMap\(', 'unmodifiableCollection\(', 'Arrays[.]asList\(', 'new ArrayList<>\(List[.]of']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# An unmodifiable copy or constant collection is List.copyOf, List.of, Set.copyOf or Map.copyOf, never Collections.unmodifiable* over a freshly allocated copy

## Thesis
A method that hands out a defensive read-only copy calls `List.copyOf(src)` (or `Set.copyOf`, `Map.copyOf`); a small constant collection is `List.of(...)`, `Set.of(...)` or `Map.of(...)`. The two-step `Collections.unmodifiableList(new ArrayList<>(src))` and the mutable `new ArrayList<>(Arrays.asList(...))` for a fixed literal are replaced.

## Rationale
`Collections.unmodifiableList` returns a view: a wrapper object whose every query reads through to the backing list, so the two-step form allocates the backing `ArrayList` (its object and its element array) plus the wrapper, and each later `get` pays a delegation call. `List.copyOf` returns one unmodifiable list holding exactly the elements — for one or two elements an object with two fields, otherwise a single trimmed array — and when the source is already an unmodifiable list it generally returns it without copying. `List.of` builds the same compact representation directly. The saving is an object and an indirection per collection, and a whole allocation per call when the input is already immutable.

## Example
```java
bad:  return Collections.unmodifiableList(new ArrayList<>(items));
      static final List<String> CODES = new ArrayList<>(Arrays.asList("a", "b"));
good: return List.copyOf(items);
      static final List<String> CODES = List.of("a", "b");
```

## Limits
`List.of` and `List.copyOf` disallow `null` elements; a collection that must hold `null` keeps the wrapper form. `unmodifiableList(list)` over an existing list without a copy is a live view by design (changes to the source show through) and is not this pattern. `Set.copyOf` and `Map.copyOf` do not preserve the source's iteration order; an ordered read-only copy keeps `Collections.unmodifiableSet(new LinkedHashSet<>(src))`. A collection the receiver may mutate keeps a mutable copy.

## Validator
On the triggered hunk find each `Collections.unmodifiable*(new …(src))` and each mutable collection built from `Arrays.asList` or `List.of` for a fixed literal that is never mutated. Check the elements for `null` and the need for iteration order. Validator question: **does this code allocate a fresh mutable copy and then wrap it, or a mutable list for a constant, where a copyOf or of factory would give one compact unmodifiable object?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-08`, severity minor, `file`, `symbol`, `code` = the wrapper or literal construction quoted verbatim from the diff, `fix` = the `copyOf` or `of` call, `rationale` naming the extra wrapper object and the read-through indirection).

## Source
`java.util.Collections#unmodifiableList` Javadoc, Java SE 21 — "Returns an unmodifiable view of the specified list. Query operations on the returned list 'read through' to the specified list". `java.util.List#copyOf` Javadoc — "Returns an unmodifiable List containing the elements of the given Collection"; implementation note — "If the given Collection is an unmodifiable List, calling copyOf will generally not create a copy". `java.util.List` "Unmodifiable Lists" — "They disallow null elements"; in the JDK 21 source `List.of(e1)` and `List.of(e1, e2)` return a two-field `ImmutableCollections.List12`, larger forms a `ListN` over one array.
