---
title: A managed component receives its collaborators through its constructor and does not construct a service, repository or client with new
rule_id: MNT-14
domain: maintainability
triggers: ['new \w*(Service|Repository|Client|Gateway|Dao|DAO|Manager|Handler|Publisher|Producer|Consumer|Facade|Adapter|Provider)\s*\(', '= new \w+Impl\(', '@(Service|Component|Repository|Controller|RestController)\b', 'new RestTemplate\(\)|WebClient[.]create\(|HttpClient[.]newHttpClient\(']
scope: file
check_kind: mechanical
severity_default: minor
---

# A managed component receives its collaborators through its constructor and does not construct a service, repository or client with new

## Thesis
A class that is a managed component — a Spring `@Service`, `@Component`, `@Repository`, `@Controller` — or that holds business logic obtains the services, repositories, clients and gateways it uses as constructor parameters, and does not create them with `new` in its methods or field initializers; the collaborator's type is an interface or abstraction where a test would substitute it.

## Rationale
A collaborator constructed inside the class is bound at compile time to one implementation and one configuration: the class cannot be unit-tested without the real database, broker or HTTP endpoint behind it, cannot receive a pooled or configured instance from the container, and hides its dependency from anyone reading the constructor. Provided dependencies make the class's needs visible in one place and let a test pass a stub or mock; when the dependency is an interface the substitution costs nothing.

## Example
```java
bad:  @Service class OrderService {
          private final PaymentGateway gateway = new StripeGateway(apiKey);
          void pay(Order o) { new AuditRepository().record(o); gateway.charge(o); } }
good: @Service class OrderService {
          private final PaymentGateway gateway; private final AuditRepository audit;
          OrderService(PaymentGateway gateway, AuditRepository audit) { this.gateway = gateway; this.audit = audit; } }
```

## Limits
Value objects, DTOs, builders, collections, exceptions and other data are constructed freely; the rule concerns collaborators with behaviour and environment. A `@Configuration` `@Bean` method is exactly where `new` belongs. A cheap, stateless, unconfigured helper (`new ObjectMapper()` in a utility) is a lower-value finding. A class the project context marks as a plain library type outside the container is out of scope.

## Validator
On the triggered hunk find each `new` of a type whose name or package marks it as a collaborator (service, repository, client, gateway, adapter, producer) inside a class that is a managed component or holds business logic; open the file to confirm the class's role and that the collaborator is not already a constructor parameter. Validator question: **does this component construct a collaborator that a test would need to replace?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-14`, severity minor, `file`, `symbol`, `code` = the `new` expression quoted verbatim from the diff, `fix` = the constructor parameter and final field, `rationale` naming the concrete implementation the class is bound to and the test that cannot substitute it).

## Source
Spring Framework reference, The IoC Container → Dependencies → Dependency Injection — "Code is cleaner with the DI principle, and decoupling is more effective when objects are provided with their dependencies. The object does not look up its dependencies and does not know the location or class of the dependencies. As a result, your classes become easier to test, particularly when the dependencies are on interfaces or abstract base classes, which allow for stub or mock implementations to be used in unit tests".
