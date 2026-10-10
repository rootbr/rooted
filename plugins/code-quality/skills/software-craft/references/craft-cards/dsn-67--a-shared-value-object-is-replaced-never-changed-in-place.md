---
title: An object that stands for a value and is held by more than one component is never changed in place, and an update produces a new instance
rule_id: DSN-67
domain: design
step: [design, implement]
applies_to: [universal]
triggers: ['[.]([sS]et[A-Z]|set_)\w*\s*\(', '^\s*(?!this[.]|self[.])\w+[.]\w+\s*([+\-*/]?=)(?![=>])', '^\s*\w+([.]\w+){2,}\s*([+\-*/]?=)(?![=>])', '\b(Object[.]assign|setattr|__setattr__)\s*\(']
scope: callers
check_kind: semantic
severity_default: major
---

# An object that stands for a value and is held by more than one component is never changed in place, and an update produces a new instance

## Thesis
An object that stands for a value keeps its state once a component other than the one making a change holds a reference to it: an update creates a new instance, and the component making the update replaces its own reference with it, so every other holder keeps the value it read. A value, here, is an object that its holders use for the data it holds rather than as one particular thing, so that two instances holding equal data are interchangeable, such as a number, a date or a position, whether or not its type compares instances by that data. Such an object is immutable, or, where its type permits changes, it is treated as if it were immutable once it has been handed out. Changing an object that no other code references yet, such as one just created and not yet handed out, is outside the rule, and so is internal state whose changes no caller can ever observe.

## Rationale
Storing a reference in a second place does not copy the object: both holders refer to one object, and a change made through either is seen through every variable that refers to it. A holder that operates on the assumption that a value will never change may then no longer do what it was designed to do, and the cause of such a bug can be difficult to track down after the fact, especially when the other code changes the value only sometimes. Professional developers interviewed about language support for immutability stated that incorrect state mutations are a major source of bugs, for example an object thought to be immutable changed by some other object because references were reused instead of immutable copies. With an immutable object, every variable that refers to it always sees the same value, and an operation that transforms the value returns a new object, so only the variable that receives the result refers to the new value and every other holder keeps the old one. An object is immutable when its state cannot be observed to change after construction; it may keep internal mutable state, such as a lazily initialized field, as long as callers can never observe that state change. From a series of empirical studies, one research group concluded that immutability had positive effects on both security and usability.

## Example
```java
bad:  Money price = catalog.priceOf(sku);
      price.setAmount(price.amount().multiply(rate));
      cart.add(sku, price);
good: Money price = catalog.priceOf(sku).times(rate);
      cart.add(sku, price);
```

## Limits
The rule is contested, and whether a component other than the one making the change holds a reference to the object and can observe the change separates the cases (the Source entries marked condition). Changing an object just created is fine: no other code references it yet, so changing it cannot accidentally affect something that depends on it. Internal state that callers can never observe changing leaves the object immutable to them. The side that defends mutation (the entries marked mutation) holds that mutability can be very useful and can make code more convenient to write, and that whether to use it is up to the author and depends on what is clearest in the particular situation; one study found that professional programmers strongly preferred, and were more effective with, APIs that did not require constructor parameters. Setting the fields of an object after creating it and before handing it out is a change no other code can observe, so that style falls on the mutation side and outside this rule. An object that its holders track as one particular thing rather than use for the data it holds, such as an entity, is not a value, and the rule does not reach it. Where the type checker permits a change through a reference only while no other reference to the object exists, it rules out the defect wherever it enforces that restriction. Thread safety of shared objects is judged by its own rules.

## Validator
Grep the added lines for a setter call, an assignment or compound assignment to a field of an object other than the enclosing instance itself, and a call that copies properties onto an existing object or sets an attribute by name. For each changed object, read its type and decide whether it stands for a value: its equality and hash come from its fields rather than its identity, or it is a record-like holder of a number, a date, a position, an amount, an identifier or a configuration that its holders read as data. Skip an entity, an object that its holders track as one particular thing rather than use for the data it holds, and internal state, such as a lazily filled cache, that no caller can observe changing. Trace where the changed reference came from: an accessor or field of another object, a parameter, a registry, a cache, a constant or a default value, or a collection element; and check whether the routine stored it in another object or a collection, passed it on or returned it before the change. Skip an object the routine created itself and has not yet handed out. Search the repository for the other holders — the callers of the accessor that returned the object, the callers that passed it in, the field or collection that stores it — and read whether they keep it and read it after the change. Validator question: **Does an added line change in place an object that stands for a value while a component other than the one making the change holds a reference to it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-67`, severity major, `file`, `symbol`, `code` = the added line that changes the shared value in place, quoted verbatim from the diff, `fix` = the update written as a new instance derived from the old one — a method that returns a changed copy, a copy with one field replaced, or a new construction — assigned to the changing component's own reference, and, where the type permits changes, the type made immutable, in the file's language, `rationale` = which other component holds the same object and which of its readings the in-place change alters).
