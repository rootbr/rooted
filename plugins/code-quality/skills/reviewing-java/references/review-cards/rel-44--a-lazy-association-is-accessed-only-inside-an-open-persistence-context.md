---
title: A lazy association is accessed only while its persistence context is open, or is fetched by the query that loaded the entity
rule_id: REL-44
domain: reliability
triggers: ['@OneToMany', '@ManyToMany', 'FetchType[.]LAZY', '@Transactional\(readOnly', 'toDto\(', 'toResponse\(', 'getContent\(\)', 'ResponseEntity', '@GetMapping']
scope: file
check_kind: semantic
severity_default: major
---

# A lazy association is accessed only while its persistence context is open, or is fetched by the query that loaded the entity

## Thesis
An entity's lazy collection or lazy `@ManyToOne` is read — iterated, sized, mapped to a DTO, serialized — inside the transaction or persistence context that loaded the entity, or is fetched in the loading query (`JOIN FETCH`, entity graph) or replaced by a projection; it is not touched from a scheduled job, a message listener, an async task or another thread after the loading method returned, and not from a controller or a serializer when the web tier runs without the Open EntityManager in View interceptor (`spring.jpa.open-in-view=false`, or a project context that says so).

## Rationale
A lazy association is a proxy or an uninitialized collection that issues its select on first access, using the session that loaded its owner. Once that session is closed — the transactional method returned, the request thread moved on — the access throws `LazyInitializationException`, "an attempt to access unfetched data outside the context of an open stateful Session". With the Open EntityManager in View interceptor that Spring Boot registers by default for web applications the persistence context stays open through the controller and the view, so the code works in the web tier and fails from a scheduled job, a message listener or an async handler; the interceptor itself keeps a connection for the whole request, which is the cost of relying on it. With `spring.jpa.open-in-view=false` the context closes when the transactional method returns, and the controller-tier access fails the same way. Fetching the association in the query, or mapping to a DTO inside the transaction, removes the dependence on where the entity is later read.

## Example
```java
bad:  @Transactional(readOnly = true) Customer load(long id) { return repo.findById(id).orElseThrow(); }
      CustomerDto view(long id) { Customer c = svc.load(id); return CustomerDto.of(c, c.getOrders()); }  // outside
good: @Transactional(readOnly = true) CustomerDto view(long id) {
          Customer c = repo.findById(id).orElseThrow(); return CustomerDto.of(c, c.getOrders()); }
```

## Limits
An association fetched by the loading query, initialized with `Hibernate.initialize` inside the transaction, or mapped with `FetchType.EAGER` is initialized and may be read anywhere. A read from a controller or a serializer under the default interceptor — `spring.jpa.open-in-view` unset or `true`, and no project context saying the web tier runs without it — does not fail: it is reported at minor, with the connection the interceptor holds for the whole request as the reason. A read from a job, a listener or an async task is major under either setting, as is a controller-tier read under `spring.jpa.open-in-view=false`.

## Validator
On the triggered hunk find each read of a lazy association and trace the method it sits in: is it inside the transaction that loaded the owner, or in a caller, a serializer, a scheduled or async method? Open the entity mapping and the loading query for a fetch of that association. For a controller or serializer read, read the project context, and `application.properties`/`application.yml` when they are in the file set, for `spring.jpa.open-in-view`. Validator question: **is this lazy association read outside the transaction that loaded its owner, without having been fetched?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-44`, severity major — minor when the read sits in a controller or serializer under the default Open EntityManager in View interceptor — `file`, `symbol`, `code` = the association access quoted verbatim from the diff, `fix` = the access moved inside the transaction, or `join fetch`/an entity graph/a DTO projection in the loading query, `rationale` naming the closed session and the `LazyInitializationException`, or, under the interceptor, the connection it holds for the whole request).

## Source
Hibernate ORM `org.hibernate.LazyInitializationException` Javadoc — "Indicates an attempt to access unfetched data outside the context of an open stateful Session. For example, this exception occurs when an uninitialized proxy or collection is accessed after the session was closed". Spring Boot reference, "SQL Databases", "Open EntityManager in View" — Spring Boot "by default registers OpenEntityManagerInViewInterceptor to apply the 'Open EntityManager in View' pattern, to allow for lazy loading in web views. If you do not want this behavior, you should set spring.jpa.open-in-view to false in your application.properties". Hibernate ORM user guide, chapter "Fetching" — "The Hibernate recommendation is to statically mark all associations lazy and to use dynamic fetching strategies for eagerness". The connection the interceptor holds for the whole request is the card's own reading; the cited page states only that the interceptor keeps the persistence context open for the view.
