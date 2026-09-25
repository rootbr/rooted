---
title: A Spring bean receives its required collaborators through its constructor into final fields, and @Autowired on a field or a setter for a required dependency is not used
rule_id: MNT-34
domain: maintainability
triggers: ['@Autowired', '@Inject\b', '@Resource\b', '@(Service|Component|Repository|Controller|RestController|Configuration)\b', '@Value\("']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Spring bean receives its required collaborators through its constructor into final fields, and @Autowired on a field or a setter for a required dependency is not used

## Thesis
A class managed by the Spring container declares its required dependencies as constructor parameters and stores them in `final` fields (a single constructor needs no `@Autowired`); `@Autowired`, `@Inject` or `@Resource` on a field, and a setter for a dependency the class cannot work without, are not used; setter injection remains for optional dependencies with a sensible default.

## Rationale
Constructor injection lets the component be an immutable object whose required dependencies cannot be `null`, returned to callers in a fully initialized state; a field-injected object can be constructed without its dependencies — in a test, by reflection, by a subclass — and fails later with a `NullPointerException` from inside a method. Field injection also ties instantiation to the container: a unit test must either boot Spring or use reflection to set private fields. A long constructor exposes what field injection concealed — a class with too many responsibilities.

## Example
```java
bad:  @Service class OrderService {
          @Autowired private OrderRepository repo;
          @Autowired private Clock clock; }
good: @Service class OrderService {
          private final OrderRepository repo; private final Clock clock;
          OrderService(OrderRepository repo, Clock clock) { this.repo = repo; this.clock = clock; } }
```

## Limits
A genuinely optional dependency with a default (`@Autowired(required = false)` on a setter, or an `Optional<T>`/`ObjectProvider<T>` constructor parameter) is the documented setter case. A `@Value` on a field is configuration rather than a collaborator and takes the constructor form when the class is otherwise constructor-injected. A test class using `@Autowired` fields under Spring's test support, and a Lombok `@RequiredArgsConstructor` on final fields, are correct forms. A configuration class's `@Bean` methods take their dependencies as method parameters.

## Validator
On the triggered hunk find each `@Autowired`, `@Inject` or `@Resource` on a field or on a setter of a required dependency, and each non-final field holding a collaborator in a component class. Open the file to confirm the class is a managed component and the dependency is required. Validator question: **does this bean receive a required collaborator other than through its constructor into a final field?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-34`, severity minor, `file`, `symbol`, `code` = the annotated field or setter quoted verbatim from the diff, `fix` = the constructor parameter and the `final` field, `rationale` naming the partially initialized object a test or subclass can create).

## Source
Spring Framework reference, Dependencies → Dependency Injection → Constructor-based or setter-based DI — "The Spring team generally advocates constructor injection, as it lets you implement application components as immutable objects and ensures that required dependencies are not null. Furthermore, constructor-injected components are always returned to the client (calling) code in a fully initialized state … Setter injection should primarily only be used for optional dependencies that can be assigned reasonable default values within the class"; "a large number of constructor arguments is a bad code smell". ArchUnit `GeneralCodingRules.NO_CLASSES_SHOULD_USE_FIELD_INJECTION` — the library rule that flags `@Autowired`, `@Inject` and `@Resource` on fields.
