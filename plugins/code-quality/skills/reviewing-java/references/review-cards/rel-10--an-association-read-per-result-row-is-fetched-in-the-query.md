---
title: An association read for each row of a query result is fetched by that query, not lazily loaded one select per row
rule_id: REL-10
domain: reliability
triggers: ['getResultList\(\)', 'findAll\(', 'findBy\w+\(', 'for \(\w+ \w+ : ', '[.]forEach\(', '[.]stream\(\)[.]map\(', '@OneToMany', '@ManyToOne', 'JOIN FETCH', '@EntityGraph']
scope: file
check_kind: semantic
severity_default: minor
---

# An association read for each row of a query result is fetched by that query, not lazily loaded one select per row

## Thesis
When a loop or stream over the entities returned by one query touches an association of each entity — a collection's size, a child's field, a `@ManyToOne` target — the query fetches that association in the same statement (`JOIN FETCH`, an entity graph, `@BatchSize`, or a DTO projection that selects the needed columns), so the number of SQL statements does not grow with the number of rows.

## Rationale
A lazy association is loaded by a separate select when first accessed; an eager `@ManyToOne` omitted from a JPQL query is loaded by a secondary select per returned entity as well. A loop over N results that reads such an association therefore issues N further statements after the first — the N+1 pattern — and the cost is invisible in a test with three rows and dominant with three thousand, where each statement is a round trip holding the connection and the transaction open. Fetching the association in the query, or batching the loads with `@BatchSize`, replaces the N statements with one or a few; a DTO projection that selects only the columns the loop needs avoids loading the entities at all.

## Example
```java
bad:  List<Order> orders = em.createQuery("from Order", Order.class).getResultList();
      for (Order o : orders) total += o.getItems().size();     // one select per order
good: List<Order> orders = em.createQuery(
          "select distinct o from Order o join fetch o.items", Order.class).getResultList();
      for (Order o : orders) total += o.getItems().size();
```

## Limits
Applies to a result whose size is unbounded or larger than a handful of rows. A query with `setMaxResults(1)` or a lookup by identifier that reads one entity's association is one extra statement, not N. An association already covered by an `@EntityGraph` on the repository method, by a `@BatchSize` on the mapping, or by a second-level cache the project context names is fetched efficiently and is not flagged. A loop that reads only the entity's own columns is out of scope.

## Validator
On the triggered hunk find each loop or stream over a query result and list the association getters it calls on each element. Open the file and the entity mapping: check whether the query text carries `join fetch` for that association, whether the repository method declares an `@EntityGraph` naming it, whether the mapping declares `@BatchSize`, or whether the code selects a projection instead of entities. Validator question: **does this loop trigger one additional select per element for an association the query did not fetch?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-10`, severity minor, `file`, `symbol`, `code` = the query and the per-element association access quoted verbatim from the diff, `fix` = the query with `join fetch`, an `@EntityGraph`, a `@BatchSize` or a DTO projection, `rationale` naming the association and the statement count that scales with the rows).

## Source
Hibernate ORM user guide, chapter "Fetching" — the SELECT fetch strategy "is the strategy generally termed N+1"; "If you forget to JOIN FETCH all EAGER associations, Hibernate is going to issue a secondary select for each and every one of those which, in turn, can lead to N + 1 query issue"; "Batch fetching" — "Without @BatchSize, you'd run into a N + 1 query issue", and "most of the time, a DTO projection or a JOIN FETCH is a much better alternative"; "Dynamic fetching via Jakarta Persistence entity graph".
