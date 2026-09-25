---
title: The first element of a collection, array, iterator or split string is read only after the code has established that one exists
rule_id: REL-33
domain: reliability
triggers: ['[.]get\(0\)', 'iterator\(\)[.]next\(\)', '[.]getFirst\(\)', 'split\(.*\)\[', '\[0\]']
scope: hunk
check_kind: mechanical
severity_default: major
---

# The first element of a collection, array, iterator or split string is read only after the code has established that one exists

## Thesis
A `list.get(0)`, `array[0]`, `iterator().next()`, `getFirst()` or `split(...)[0]` on a value that can be empty is guarded by an `isEmpty()`, `hasNext()`, `size()` or `length` check on the same value, replaced by a lookup that returns a default or throws a named exception when nothing is there, or documented with the reason the value cannot be empty.

## Rationale
Each of these accessors throws on an empty input — `IndexOutOfBoundsException` from `get(0)` and `[0]`, `NoSuchElementException` from `next()` — with a message that names neither the data nor the reason it was expected. Query results, split strings, parsed headers and filtered lists are empty under conditions the tests never produce: a deleted row, a header absent from one client, a filter that matches nothing. The failure then surfaces as a 500 far from its cause. A guard turns the empty case into a defined outcome — a 404, a default, a domain exception — at the place that knows what empty means.

## Example
```java
bad:  Order latest = repo.findByCustomer(id).get(0);
      String host = header.split(":")[0];
good: List<Order> orders = repo.findByCustomer(id);
      if (orders.isEmpty()) throw new OrderNotFoundException(id);
      Order latest = orders.get(0);
      String host = header.indexOf(':') < 0 ? header : header.substring(0, header.indexOf(':'));
```

## Limits
A read inside a block guarded by `!isEmpty()`, `hasNext()`, `size() > 0` or a `length` check on the same value is correct. A collection or array built in the same method with at least one element is out of scope. A first-element read on a value that a method documents as never empty is out of scope.

## Validator
On the triggered hunk find each first-element read and look upward in the same method for a guard on the same value, or for a construction that guarantees an element. Validator question: **can this value be empty on some input, with the read throwing an unnamed exception?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-33`, severity major, `file`, `symbol`, `code` = the read quoted verbatim from the diff, `fix` = the guard, or a lookup that returns a default or throws a named exception when the value is empty, `rationale` naming the input that makes the value empty).

## Source
`java.util.List#get(int)` Javadoc, Java SE 21 — `@throws IndexOutOfBoundsException if the index is out of range (index < 0 || index >= size())`; `java.util.Iterator#next()` — `@throws NoSuchElementException if the iteration has no more elements`.
