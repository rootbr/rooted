---
title: A service's API responses and published events are contract types that model the domain, never its persistence entities or a mirror of its table schema
rule_id: ARCH-32
domain: architecture
step: [design, implement, review]
applies_to: [service-boundary, public-api]
triggers: ['\b(?:ResponseEntity|Mono|Flux|List|Optional|Page|Promise|IActionResult|ActionResult|Task)<\s*\w*(?:Entity|Record|Row)\s*>', '\b(?:publish|send|emit|produce)\w*\s*\([^)]*\b\w+(?:Entity|Record|Row)\b', '\breturn\s+(?:await\s+)?(?:\w+[.])?\w*(?:[Rr]epository|[Rr]epo|[Dd]ao)[.]\w+\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# A service's API responses and published events are contract types that model the domain, never its persistence entities or a mirror of its table schema

## Thesis
A service's API responses and the events it publishes are contract types that model the domain and serve as the contract between services. These types abstract away from implementation details and do not mirror the service's internal database schema, so a persistence entity is not returned or published as the payload, a data change event that follows the datastore representation being the one documented exception. Ideally such a contract changes only when functionality is added, not when code is refactored or the database schema changes, and it stays stable even when the complete service implementation, including its technology stack, is replaced.

## Rationale
The API should model the domain and serve as the contract between services, and an API that mirrors the internal database schema follows that schema, so it changes when the schema changes; the contract should ideally change only when functionality is added, not when code is refactored or the database schema changes. A database entity used as an event exposes internal service details and often fails to convey the correct business intent, which leads to tightly coupled and unclear integrations. Events are part of a service's interface to the outside world, equivalent in standing to its REST API, so the stability an API owes its consumers applies to the events it publishes as well. Abstraction from implementation aspects is the property the rule restores: the contract should stay stable even if the complete service implementation and its underlying technology stack are replaced. A data change event whose representation of an entity corresponds to the API representation keeps the number of published structures low, so consumers work with fewer representations and the service owners maintain less API surface; a service should publish only events that are interesting in the domain and abstract away from implementation or local details, with no need to reflect every change that happens within the system.

## Example
```java
bad:  @GetMapping("/orders/{id}") Optional<OrderEntity> get(@PathVariable String id) {
          return repository.findById(id); }
      void place(OrderEntity orderEntity) { events.publish(orderEntity); }
good: record OrderView(String id, String status, long totalCents) {}
      record OrderPlaced(String orderId, long totalCents) {}
      @GetMapping("/orders/{id}") OrderView get(@PathVariable String id) {
          OrderEntity e = repository.findById(id).orElseThrow();
          return new OrderView(e.getId(), e.getStatus(), e.getTotalCents()); }
      void place(OrderEntity o) { events.publish(new OrderPlaced(o.getId(), o.getTotalCents())); }
```

## Limits
A data change event may follow the datastore representation where the API resource representations are very different from the datastore representation but the physical data are easier to reliably process for data integration. The rule reaches the contract between services: the responses of an API that other services call and the events published for other consumers; a persistence type passed between layers inside one service is outside it. Evolving, versioning and deprecating a contract that already exists, and the delivery guarantees of the messaging that carries an event, are separate concerns the rule does not reach.

## Validator
Grep the hunk for a handler or publish call whose type or argument ends in Entity, Record or Row, for a handler that returns a repository or data-access lookup directly, and for an object-relational base class on a type a handler returns. Open the type's declaration and its usages at the callers: decide whether it is a persistence entity (a class or record mapped to a table) or a type that mirrors the table's schema, so that a schema change changes the type too, such as a type generated from the table; a separate contract type that a mapping at the boundary fills does not mirror the schema even where its fields match the table's columns. Trace whether that type crosses the service boundary as the response of an endpoint other services call or as the payload of a message published for other consumers. For an event, check whether it is a data change event that follows the datastore representation because the physical data are easier to reliably process for data integration, while the API resource representation is very different from the datastore representation. Validator question: **Does a persistence entity, or a type that mirrors the service's table schema, cross the service boundary as an API response or a published event payload, outside a data change event whose API resource representation is very different from the datastore representation and whose physical data are easier to reliably process for data integration?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-32`, severity minor, `file`, `symbol`, `code` = the handler signature or publish call that carries the persistence type, quoted verbatim from the diff, `fix` = a contract type that models the domain and the mapping from the entity to it at the boundary, in the file's language, `rationale` = the internal schema detail the contract exposes to other services and the storage change that would now change the contract).

## Source
- Azure Architecture Center, docs/microservices/design/api-design.md, § RESTful API design (fetched): "Avoid APIs that expose internal implementation details or mirror an internal database schema. The API should model the domain and serve as a contract between services. Ideally, you should only change the API when you add new functionality, not when you refactor code or change the database schema."
- Azure Architecture Center, docs/guide/architecture-styles/microservices.md, § Antipatterns for microservices (fetched): "Using database entities as events exposes internal service details and often fails to convey the correct business intent, which leads to tightly coupled and unclear integrations."
- Zalando RESTful API and Event Guidelines, chapters/design-principles.adoc, § API first (fetched): "clear separation of WHAT vs. HOW concerns, i.e. abstraction from implementation aspects — APIs should be stable even if we replace complete service implementation including its underlying technology stack"
- Zalando RESTful API and Event Guidelines, chapters/events.adoc, rule #205 "ensure that data change events match the APIs resources" (fetched): "A data change event's representation of an entity should correspond to the REST API representation. There's value in having the fewest number of published structures for a service. Consumers of the service will be working with fewer representations, and the service owners will have less API surface to maintain. In particular, you should only publish events that are interesting in the domain and abstract away from implementation or local details - there's no need to reflect every change that happens within your system." and the exception "Where the API resource representations are very different from the datastore representation, but the physical data are easier to reliably process for data integration."
- Zalando RESTful API and Event Guidelines, chapters/events.adoc, rule #194 "treat events as part of the service interface" (fetched): "Events are part of a service’s interface to the outside world equivalent in standing to a service’s REST API. Services publishing data for integration must treat their events as a first class design concern, just as they would an API."
- Caveat: all five sources are official design guidance, and the four that state the rule itself are phrased as recommendations ("Avoid", "Ideally", "should"); none reports a measurement.
