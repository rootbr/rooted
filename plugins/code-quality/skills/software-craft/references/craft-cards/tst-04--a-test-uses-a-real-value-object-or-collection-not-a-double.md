---
title: A test uses a real instance of a value object, data class or standard collection rather than a double of it
rule_id: TST-04
domain: tests
step: [test]
applies_to: [tests]
triggers: ['(?i)(mock|spy|stub)\w*\s*[(<]|@(?:relaxed)?(?:mock|spy)\w*|(jest|vi)[.]fn\(|create_autospec\(|mock\w+::(?:new|default)\(|(?<![\w.])patch(?:[.]object)?\(|mock(?:er)?[.]patch\b|\b(?:instance_|class_|object_)?double\(|\bsubstitute[.]for<|\ba[.]fake<', '(?i)(mock|spy)\w*\(\s*(List|Map|Set|String|Integer|Long|Date|LocalDate|Instant|Optional|Duration|BigDecimal|UUID|dict|list|str)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# A test uses a real instance of a value object, data class or standard collection rather than a double of it

## Thesis
A test that needs a value object, a pure data class, or a standard data holder — a string, a number, a date or duration, an identifier, an optional, a list, a map or a set — constructs a real instance of it the way production code constructs it, and creates no mock, stub or spy of that type. A value, here, is a type whose instances are fixed by the data they hold and that reaches no store, service or I/O. Where construction is verbose, the test takes the instance from a builder with defaults for the fields it does not care about, a copy method that changes one field, or a named factory method in test code. That a value is painful to construct is not a reason to double it; it signals that the type or its construction may need refactoring.

## Rationale
A value's behaviour is fixed by the data passed to its constructor, so building it with the data the test needs yields exactly the instance the test needs; a double isolates nothing, because no slow or external collaborator stands behind a value. The double still costs: on a mock or a stub, every method the test did not stub answers with whatever the double supplies — a default such as null, zero, false or an empty collection, another double, or a failure — rather than what the real type computes from its data, so the code under test runs against an object without the type's own validation and derived results; a spy runs the real methods the test did not stub, yet each method it stubs answers with the test's value rather than the one the data determines; and on any double, each change to the type's accessors or invariants has to be mirrored in every test's stubbing. A double that returns a double that returns a double, down to something meaningful, hints at doubling a value or at a call chain that breaks the Law of Demeter. A value class left open to subclassing only because its code generator subclasses it is still logically final; that a mocking tool can subclass or proxy it is an accident of how it is generated. Practice agrees: in the test suites of four systems (a manually classified sample of 2,178 dependencies) standard-library types were almost never doubled, and 82% of 105 surveyed developers said they never or almost never double them; an interviewed developer gave the reason that such data holders are easy to instantiate with the desired value. When building a value takes many lines, a builder, a copy method or a named test factory lets each test state only the fields it depends on; the difficulty itself points at the type's design, not at a need for a double.

## Example
```java
bad:  Money price = mock(Money.class);
      when(price.amount()).thenReturn(new BigDecimal("9.99"));
      List<Item> items = mock(List.class);
      when(items.size()).thenReturn(1);
good: Money price = new Money(new BigDecimal("9.99"), "EUR");
      List<Item> items = List.of(new Item("sku-1", price));
```

## Limits
A domain class whose methods call collaborators or reach a store, a service or I/O, and a class that is costly to set up because of its dependencies, are not values, and whether to double them is outside this rule. A value derived from a type's own fields, such as arithmetic on an amount, keeps it a value; a domain class that carries complex business logic is not a value object, and whether to double it is outside this rule. A standard-library type that performs I/O — a file, a stream, a socket, a process — is not a data holder, and a test may double file access that is complex to set up. A double that replaces a source of the current time or of randomness — a clock, or the static now() or random-identifier factory of a date or identifier type — stands in for a nondeterministic dependency rather than a value, and is outside this rule. A tolerance the project context states for a named type — a third-party data type that tests cannot construct because it exposes no public constructor, factory or builder — rejects the finding.

## Validator
In the hunk, find each creation of a test double — a mock, stub, spy, fake, double or substitute factory call, a mock or spy annotation on a field, a mock-function or auto-spec factory, or a patch that replaces a name with a double — and read the type it doubles: the class literal, the generic argument, the spec argument, the patch target, or the annotated field's declared type. Recognise a standard-library string, number, date, duration, identifier, optional or collection type by its name; otherwise search the repository for the type's declaration and read it. A record, a data class, a struct or a generated value type whose members are fields, accessors, validation and values derived from those fields, with no dependency on a service, a store or I/O, is a value. Skip a domain class that carries complex business logic, a type whose methods call collaborators or perform I/O, a double that only replaces the static now() or random-identifier factory of a date or identifier type, and a type the project context names as not constructible in tests. Validator question: **does the test create a double of a value object, a pure data class or a standard-library data holder that it could construct for real?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-04`, severity minor, `file`, `symbol`, `code` = the line that creates the double and any line that stubs it, quoted verbatim from the diff, `fix` = the real construction of the value — its constructor or factory, a collection literal, or a builder or named test factory — in the file's language, `rationale` naming the value type and the stubbed answers a real instance gives by construction).
