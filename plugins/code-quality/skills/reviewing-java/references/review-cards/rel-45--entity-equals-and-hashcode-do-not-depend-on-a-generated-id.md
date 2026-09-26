---
title: An entity's equals and hashCode never depend on a generated identifier that is null until the entity is persisted
rule_id: REL-45
domain: reliability
triggers: ['@GeneratedValue', 'public boolean equals\(', 'public int hashCode\(', 'Objects[.]hash\(', '@EqualsAndHashCode', '@Data\b', 'Set<\w+> ']
scope: file
check_kind: semantic
severity_default: major
---

# An entity's equals and hashCode never depend on a generated identifier that is null until the entity is persisted

## Thesis
A JPA entity with `@GeneratedValue` implements `equals`/`hashCode` on a natural or business key, on an identifier assigned before the entity is added to any `Set`, or not at all (identity semantics); it does not derive them from the generated `@Id`, and it is not annotated with a code generator (`@Data`, `@EqualsAndHashCode`) that includes every field.

## Rationale
A `Set` requires that "the equals/hashCode value for an object should not change while the object is part of the Set". A generated identifier is `null` until the insert runs at flush or commit, so an entity added to a `HashSet` before persist hashes as a null-id object; after the flush its `hashCode` changes, the set can no longer find it, `contains` returns false, a second add creates a duplicate, and `remove` fails silently. The same holds for an all-fields `equals`: any mutation after insertion breaks the set. The failure depends on the order of `add` and `persist`, so it appears only on the code path that builds the graph before saving.

## Example
```java
bad:  @Entity class Book { @Id @GeneratedValue Long id; String isbn;
          @Override public int hashCode() { return Objects.hash(id); } ... }
good: @Entity class Book { @Id @GeneratedValue Long id; @NaturalId String isbn;
          @Override public int hashCode() { return Objects.hash(isbn); }
          @Override public boolean equals(Object o) { return o instanceof Book b && isbn.equals(b.isbn); } }
```

## Limits
An entity whose identifier is assigned by the application before any collection use (a UUID set in the constructor) may use the id. An entity never placed in a hash-based collection or compared across sessions, stated in a comment, may keep identity semantics without overriding. A `hashCode` returning a constant with an id-based `equals` is a documented compromise and is not flagged.

## Validator
On the triggered hunk find each entity `equals`/`hashCode` (or generator annotation) and read which fields it uses; open the file for the identifier's generation strategy and for `Set` fields or `Set` usages of the entity. Validator question: **can this entity's hash or equality change after it is placed in a set, because the fields used are assigned or mutated later?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-45`, severity major, `file`, `symbol`, `code` = the `equals`/`hashCode` or annotation quoted verbatim from the diff, `fix` = a natural-key implementation or identity semantics, `rationale` naming the hash that changes at flush).

## Source
Hibernate ORM user guide, chapter "Domain Model", "Implementing equals() and hashCode()" — the naive id-based implementation "still breaks when adding transient instance of Book to a set"; "Set says that the equals/hashCode value for an object should not change while the object is part of the Set. But that is exactly what happened here because the equals/hasCode are based on the (generated) id, which was not set until the Jakarta Persistence transaction is committed"; "Note that this is just a concern when using generated identifiers"; "The final approach is to use a 'better' equals/hashCode implementation, making use of a natural-id or business-key". `java.util.Set` class Javadoc, Java SE 21 — "Great care must be exercised if mutable objects are used as set elements. The behavior of a set is not specified if the value of an object is changed in a manner that affects equals comparisons while the object is an element in the set" (the all-fields `equals` clause).
