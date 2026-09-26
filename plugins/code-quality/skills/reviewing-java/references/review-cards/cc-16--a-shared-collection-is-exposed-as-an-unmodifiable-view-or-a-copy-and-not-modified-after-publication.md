---
title: A collection field shared across threads is exposed as an unmodifiable view or a copy, and the backing collection is not modified after publication
rule_id: CC-16
domain: concurrency
triggers: ['(List|Set|Map|Collection|Deque)<[^>]*>\s+\w+\s*\(\s*\)', 'unmodifiable(List|Set|Map|Collection)\(', '(List|Set|Map)[.]copyOf\(', 'public (List|Set|Map|Collection)<', 'Collections[.]unmodifiable']
scope: file
check_kind: semantic
severity_default: major
---

# A collection field shared across threads is exposed as an unmodifiable view or a copy, and the backing collection is not modified after publication

## Thesis
When a collection the object holds is reachable from more than one thread, a method that gives callers access to it returns an unmodifiable view (`Collections.unmodifiableList`) or an unmodifiable copy (`List.copyOf`), never the mutable field itself; and a collection published across threads through an unmodifiable view is not modified afterwards by its owner, because the view reads through to the backing collection and every later change shows through it.

## Rationale
A getter that returns the field hands every caller a reference through which it can add, remove or iterate on any thread, bypassing whatever lock the owner uses: the owner's `synchronized` methods and the caller's unguarded `add` then race on one `ArrayList`. An unmodifiable view rejects modification through the view — attempts "result in an UnsupportedOperationException" — but query operations read through to the backing collection, so an owner that keeps mutating it publishes every mutation to every holder of the view, iterators included. A copy through `List.copyOf` is unaffected by later modification of the source, at the cost of one copy per call.

## Example
```java
bad:  public List<Item> items() { return items; }
      public List<Item> items() { return Collections.unmodifiableList(items); }
      public void add(Item i) { items.add(i); }   // shows through every view handed out
good: public List<Item> items() { synchronized (lock) { return List.copyOf(items); } }
      public void add(Item i) { synchronized (lock) { items.add(i); } }
```

## Limits
Applies to a collection reachable from more than one thread. A collection confined to one thread, a `CopyOnWriteArrayList` returned to readers (its iterators use a snapshot of the array taken when the iterator was created), a concurrent collection exposed by design, and a getter on an immutable object whose collection was copied in the constructor and is never modified are correct. An unmodifiable view is correct when the backing collection is populated before publication and never changed afterwards, which the file must show. A `Stream` returned instead of the collection is treated as the field.

## Validator
On the triggered hunk find each method that returns a collection field, and each `Collections.unmodifiable*` wrapping of a field. Open the file: confirm the field is shared between threads; for a returned field, flag; for an unmodifiable view, look for any modification of the backing collection after the view can have been handed out and flag when one exists. Validator question: **can a caller on another thread modify this collection through the reference, or observe the owner's later modifications through a view?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-16`, severity major, `file`, `symbol`, `code` = the accessor and, where present, the later modification quoted verbatim from the diff, `fix` = the copy under the owner's lock, or the view with the backing collection frozen after publication, `rationale` naming the unguarded mutation or the read-through).

## Source
`java.util.Collections#unmodifiableList` Javadoc, Java SE 21 — "Returns an unmodifiable view of the specified list. Query operations on the returned list 'read through' to the specified list, and attempts to modify the returned list ... result in an UnsupportedOperationException". `java.util.List#copyOf` Javadoc — "If the given Collection is subsequently modified, the returned List will not reflect such modifications". `java.util.concurrent.CopyOnWriteArrayList` class Javadoc — the "snapshot" style iterator "will not reflect additions, removals, or changes to the list since the iterator was created". SEI CERT OBJ05-J "Do not return references to private mutable class members".
