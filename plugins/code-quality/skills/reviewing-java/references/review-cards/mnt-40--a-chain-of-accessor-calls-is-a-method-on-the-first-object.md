---
title: A chain of accessor calls that walks three or more objects is replaced by a method on the first object
rule_id: MNT-40
domain: maintainability
triggers: ['\w+([.]get\w+\(\)){2,}[.]\w+', '(\w+\(\)[.]){3,}\w+\(\)', 'get\w+\(\)[.]get\w+\(\)[.]get\w+\(\)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A chain of accessor calls that walks three or more objects is replaced by a method on the first object

## Thesis
A client does not navigate a chain of getters through several objects — `order.getCustomer().getAddress().getCity().getPostalCode()` — to reach a value; the first object exposes what the client needs (`order.shippingPostalCode()`), and each object in the chain talks to its own fields, its parameters, and objects it creates.

## Rationale
The chain binds the client to the shape of every object along the way: rename `Address`, make `city` optional, or move the postal code, and every client walking the chain changes; each intermediate object also has to expose its internals for the walk to work. A method on the first object hides the delegation, leaves the chain in one place, and gives the intermediate objects room to change. The rule's degree of trust is small: `this`, parameters, fields and locally created objects are friends, and the default trust radius already reports a call on the result of one getter on a parameter. This card draws its line one hop later on purpose — a single delegation such as `order.getCustomer().getName()` passes, and the walk is flagged from the second intermediate object on — so that the finding is kept for chains that bind the client to two or more intermediate types.

## Example
```java
bad:  String zip = order.getCustomer().getAddress().getCity().getPostalCode();
good: String zip = order.shippingPostalCode();
      // in Order: String shippingPostalCode() { return customer.postalCode(); }   // and so on down
```

## Limits
A fluent builder, a stream pipeline, a `StringBuilder` chain and other APIs that return `this` or a new pipeline stage are one object's interface, not a walk across objects. A chain over immutable value objects (a record of records) in a mapper or a test assertion is a lower-value finding. A tolerance in the project context ("navigation over the read model accepted in views") rejects it.

## Validator
On the triggered hunk find each expression that calls an accessor on the result of an accessor on the result of an accessor across three or more distinct objects. Exclude builders, streams and self-returning APIs. Validator question: **does this expression reach a value by walking through two or more intermediate objects' accessors?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-40`, severity minor, `file`, `symbol`, `code` = the chain quoted verbatim from the diff, `fix` = the method on the first object, `rationale` naming the intermediate types the client is now bound to).

## Source
PMD `LawOfDemeter` — "only talk to friends … It forbids fetching data from 'too far away', for some definition of distance, in order to reduce coupling between classes or objects of different levels of abstraction"; the degree of `this` is 0, of a parameter, a new object or a static variable 1, of a getter expression the degree of its receiver plus 1; `trustRadius` default 1 "corresponds to the original law of Demeter (you're only allowed one getter call on untrusted values)". Lieberherr, Holland, "Assuring Good Style for Object-Oriented Programs", IEEE Software 6(5), 1989, DOI 10.1109/52.35588 — the Law of Demeter. Caveat: the card's three-object threshold is one hop wider than the default `trustRadius` of 1, by design.
