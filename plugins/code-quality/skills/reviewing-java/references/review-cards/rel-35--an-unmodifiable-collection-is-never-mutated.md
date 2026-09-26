---
title: A collection from List.of, Set.of, Map.of, copyOf, Collections.singletonList, emptyList or unmodifiable is never passed where it will be mutated
rule_id: REL-35
domain: reliability
triggers: ['List[.]of\(', 'Set[.]of\(', 'Map[.]of\(', '[.]copyOf\(', 'Collections[.]singletonList\(', 'Collections[.]emptyList\(', 'Collections[.]unmodifiable', '[.]toList\(\)', 'Arrays[.]asList\(']
scope: file
check_kind: semantic
severity_default: major
---

# A collection from List.of, Set.of, Map.of, copyOf, Collections.singletonList, emptyList or unmodifiable is never passed where it will be mutated

## Thesis
A collection created by `List.of`, `Set.of`, `Map.of`, `List.copyOf`, `Stream.toList()`, `Collections.singletonList`, `Collections.emptyList` or `Collections.unmodifiable*` is not the target of `add`, `remove`, `put`, `clear`, `sort` or `set`, in the same method or in a callee it is handed to; code that needs a mutable collection builds one (`new ArrayList<>(...)`).

## Rationale
These factories return unmodifiable instances: "Calling any mutator method on the List will always cause UnsupportedOperationException to be thrown". `Arrays.asList` is fixed-size — `set` works, `add` and `remove` throw. The exception is thrown at the mutation, which may be several calls away from the construction, in a helper that has always received an `ArrayList` before, so a refactor that switches a return value to `List.of` or `toList()` breaks a caller that appends to it, and the failure appears only on the code path that mutates.

## Example
```java
bad:  List<String> tags = defaults.isEmpty() ? List.of() : new ArrayList<>(defaults);
      tags.add(extra);                                       // throws when defaults is empty
good: List<String> tags = new ArrayList<>(defaults);
      tags.add(extra);
```

## Limits
A collection returned to a caller as unmodifiable by design is correct, and the caller copying it before mutation is correct. A `Collections.unmodifiableList` wrapper around a list the owner still mutates on one thread is the intended pattern. `Arrays.asList` followed only by `set` is correct.

## Validator
On the triggered hunk find each unmodifiable construction and follow the variable within the method and into callees in the same file. Flag a mutator call on it, or a hand-off to a method whose body or name mutates its parameter. Validator question: **does a mutator reach a collection that one of these factories produced?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-35`, severity major, `file`, `symbol`, `code` = the construction and the mutator quoted verbatim from the diff, `fix` = `new ArrayList<>(...)` (or `HashMap`/`HashSet`) where mutation is intended, `rationale` naming the `UnsupportedOperationException`).

## Source
`java.util.List` class Javadoc, Java SE 21, "Unmodifiable Lists" — "The List.of and List.copyOf static factory methods provide a convenient way to create unmodifiable lists ... They are unmodifiable. Elements cannot be added, removed, or replaced. Calling any mutator method on the List will always cause UnsupportedOperationException to be thrown"; `#add(E)` — `@throws UnsupportedOperationException if the add operation is not supported by this list`. `java.util.Arrays#asList` — "Returns a fixed-size list backed by the specified array". `java.util.stream.Stream#toList()` — "The returned List is unmodifiable; calls to any mutator method will always cause UnsupportedOperationException to be thrown"; `java.util.Collections#singletonList` — "Returns an immutable list containing only the specified object"; `#emptyList` — "Returns an empty list (immutable)".
