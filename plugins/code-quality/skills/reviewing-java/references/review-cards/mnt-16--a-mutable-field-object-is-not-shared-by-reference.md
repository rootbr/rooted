---
title: A mutable object held in a field is neither returned nor stored by reference across the class boundary
rule_id: MNT-16
domain: maintainability
triggers: ['return (this[.])?\w*(list|items|map|set|entries|values|children|elements|array|bytes|data|date|calendar)\w*;', 'this[.]\w+ = \w+;', 'copyOf\(|unmodifiable\w*\(|[.]clone\(\)', 'public [\w<>\[\], ?]+\s+get\w*\(\)']
scope: file
check_kind: mechanical
severity_default: minor
---

# A mutable object held in a field is neither returned nor stored by reference across the class boundary

## Thesis
A getter does not return the reference of a mutable object stored in a field — a `List`, `Map`, `Set`, array, `Date`, `StringBuilder`, or a mutable value — and a constructor or setter does not store a mutable argument's reference into a field; the method returns an unmodifiable copy or view (`List.copyOf`, `Collections.unmodifiableList`, `clone()` for an array) and the constructor stores a copy, so the class alone controls its state.

## Rationale
The reference handed out is the same object the class keeps, so `order.getItems().clear()` empties the order behind every invariant its methods enforce, and a caller that keeps mutating the list it passed to the constructor changes the object after construction; none of it shows in the class's own code. A copy on the way out and on the way in makes the field's contents change only through the class's methods. `List.copyOf` returns an unmodifiable list that does not reflect later modification of the source; the copy is shallow, so elements that are themselves mutable remain a further exposure.

## Example
```java
bad:  private final List<LineItem> items;
      public List<LineItem> getItems() { return items; }
      public Order(List<LineItem> items) { this.items = items; }
good: public List<LineItem> getItems() { return List.copyOf(items); }
      public Order(List<LineItem> items) { this.items = List.copyOf(items); }
```

## Limits
A field already holding an immutable object (`List.of`, a record, a `String`) is exposed safely by reference. A class that documents itself as a mutable view or a builder returns its internals by design. A package-private accessor used by one collaborator in the same package is a lower-value finding. Copying a large collection on a hot path is a performance question the project context may settle with a documented unmodifiable view instead.

## Validator
On the triggered hunk find each `return` of a field holding a mutable type and each assignment of a constructor or setter parameter of a mutable type into a field. Open the file to confirm the field's type is mutable and no copy or unmodifiable wrapper intervenes. Validator question: **can a caller mutate this object's state through the reference this method hands out or accepts, bypassing the class's methods?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-16`, severity minor, `file`, `symbol`, `code` = the return or the assignment quoted verbatim from the diff, `fix` = the `copyOf` or unmodifiable form, `rationale` naming the mutation path around the class).

## Source
SpotBugs `EI_EXPOSE_REP` — "Returning a reference to a mutable object value stored in one of the object's fields exposes the internal representation of the object … Returning a new copy of the object is better approach in many situations"; `EI_EXPOSE_REP2` — "This code stores a reference to an externally mutable object into the internal representation of the object … Storing a copy of the object is better approach"; both cite CWE-374. `java.util.List#copyOf` Javadoc, Java SE 21 — "Returns an unmodifiable List containing the elements of the given Collection … If the given Collection is subsequently modified, the returned List will not reflect such modifications".
