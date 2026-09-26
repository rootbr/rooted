---
title: Two beans do not depend on each other, and a constructor dependency that would close a cycle is removed by extracting the shared part rather than hidden by @Lazy or by allowing circular references
rule_id: MNT-35
domain: maintainability
triggers: ['@Lazy', 'allow-circular-references|allowCircularReferences|setAllowCircularReferences\(', '@(Service|Component|Repository|Controller|RestController|Configuration)\b', 'ApplicationContext\b.*getBean\(|ApplicationContextAware', '@PostConstruct']
scope: callers
check_kind: semantic
severity_default: minor
---

# Two beans do not depend on each other, and a constructor dependency that would close a cycle is removed by extracting the shared part rather than hidden by @Lazy or by allowing circular references

## Thesis
When the diff adds a collaborator to a managed bean, that collaborator does not itself depend, directly or through intermediates, on the bean being changed; where the two need each other, the shared responsibility is extracted into a third bean both depend on, the callback is inverted through an event or an interface, or the value is passed as a method argument. `@Lazy` on the parameter, setter injection for the sake of the cycle, `ApplicationContext.getBean` lookups, `spring.main.allow-circular-references=true` and `SpringApplication.setAllowCircularReferences(true)` hide the cycle rather than remove it.

## Rationale
With constructor injection the container cannot construct either bean first, so it refuses to start with `BeanCurrentlyInCreationException`; Spring Boot prohibits circular references by default and says to update the configuration to break the cycle. Any workaround forces one bean to be injected into the other before it is fully initialized — a chicken-and-egg state in which a method call during construction reaches a half-built object — and the two beans, being mutually dependent, can be understood, tested and reused only together. The extraction or inversion that breaks the cycle is also the design that gives each bean one direction of dependency.

## Example
```java
bad:  @Service class OrderService   { OrderService(InvoiceService invoices) { ... } }
      @Service class InvoiceService { InvoiceService(@Lazy OrderService orders) { ... } }
good: @Service class OrderService   { OrderService(InvoiceService invoices) { ... } }
      @Service class InvoiceService { InvoiceService(OrderLookup orders) { ... } }   // read-only port, implemented elsewhere
      // or: OrderService publishes OrderPlaced; InvoiceService listens
```

## Limits
A cycle that already exists at the base commit and that the diff does not extend is reported once as pre-existing, if at all. A `@Lazy` used for a documented startup-cost reason on a non-cyclic dependency is not this finding. A project that documents `allow-circular-references=true` as a transitional setting in the project context still gets the finding on a new cycle, at lower priority.

## Validator
On the triggered hunk take each collaborator added to a bean's constructor, field or setter. At callers scope open the collaborator's class and follow its own injected dependencies for the bean under change, two hops deep. Validator question: **does the added dependency's target depend, directly or transitively, on the bean that now depends on it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-35`, severity minor, `file`, `symbol`, `code` = the added constructor parameter or field quoted verbatim from the diff, `fix` = the extracted bean, the event, or the inverted interface, `rationale` naming the two beans and the reverse path).

## Source
Spring Framework reference, Dependencies → Dependency Injection → "Circular dependencies" — with constructor injection "The Spring IoC container detects this circular reference at runtime, and throws a BeanCurrentlyInCreationException"; "a circular dependency between bean A and bean B forces one of the beans to be injected into the other prior to being fully initialized itself (a classic chicken-and-egg scenario)". Spring Boot 2.6 Release Notes, "Circular References Prohibited by Default" — "Circular references between beans are now prohibited by default. If your application fails to start due to a BeanCurrentlyInCreationException you are strongly encouraged to update your configuration to break the dependency cycle"; `spring.main.allow-circular-references`, or the setter on `SpringApplication` and `SpringApplicationBuilder`, restores the old behaviour.
