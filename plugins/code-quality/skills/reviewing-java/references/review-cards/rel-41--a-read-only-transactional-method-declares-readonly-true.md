---
title: A transactional method that only reads declares @Transactional(readOnly = true)
rule_id: REL-41
domain: reliability
triggers: ['@Transactional', 'readOnly', 'findBy\w+\(', 'getResultList\(\)']
scope: file
check_kind: semantic
severity_default: minor
---

# A transactional method that only reads declares @Transactional(readOnly = true)

## Thesis
A `@Transactional` service or repository method whose body performs no insert, update, delete or entity mutation carries `readOnly = true`, so the persistence provider skips dirty checking and flushing, the JDBC driver receives the read-only hint, and a lazy connection proxy configured with a read-only data source serves the transaction from it.

## Rationale
With `readOnly = true` Spring sets the Hibernate flush mode to `MANUAL`, "which causes Hibernate to skip dirty checks (a noticeable improvement on large object trees)", and propagates the flag "as a hint to the underlying JDBC driver for performance optimizations"; a `LazyConnectionDataSourceProxy` given a read-only `DataSource` obtains the connection for "a Spring-managed transaction that has been marked as read-only" from that data source — a replica, when one is configured there. Without the flag, every loaded entity is snapshotted and compared at commit, a large read costs memory and time proportional to the object graph, and the read takes its connection from the primary. The flag is not a guard — a write inside a read-only transaction is not rejected by Spring — so it must be declared where the code knows it only reads.

## Example
```java
bad:  @Transactional
      public List<OrderView> recent(long customer) { return repo.findRecent(customer).stream().map(OrderView::of).toList(); }
good: @Transactional(readOnly = true)
      public List<OrderView> recent(long customer) { return repo.findRecent(customer).stream().map(OrderView::of).toList(); }
```

## Limits
A method that mutates a loaded entity, calls `save`, `persist`, `merge`, `delete`, a `@Modifying` query, or a service that writes is correctly read-write. A method on a class annotated `@Transactional(readOnly = true)` at the type level inherits the flag. Spring Data's `CrudRepository` read methods are already read-only. A project context stating no replica routing and small object graphs lowers the finding to a suggestion.

## Validator
On the triggered hunk find each `@Transactional` without `readOnly = true` and open the method body and its callees in the same file for a write: a repository save/delete, a `@Modifying` query, a setter on a managed entity, `persist`/`merge`/`remove`. Validator question: **does this transactional method only read, without declaring readOnly?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-41`, severity minor, `file`, `symbol`, `code` = the annotation and method signature quoted verbatim from the diff, `fix` = `@Transactional(readOnly = true)`, `rationale` naming the dirty check and flush the flag skips).

## Source
Spring Data JPA reference, "Transactionality" — "You can use transactions for read-only queries and mark them as such by setting the readOnly flag. Doing so does not, however, act as a check that you do not trigger a manipulating query ... The readOnly flag is instead propagated as a hint to the underlying JDBC driver for performance optimizations. Furthermore, Spring performs some optimizations on the underlying JPA provider. For example, when used with Hibernate, the flush mode is set to MANUAL when you configure a transaction as readOnly, which causes Hibernate to skip dirty checks (a noticeable improvement on large object trees)"; "For read operations, the transaction configuration readOnly flag is set to true". `org.springframework.jdbc.datasource.LazyConnectionDataSourceProxy#setReadOnlyDataSource` Javadoc (since 6.1.2) — "Specify a variant of the target DataSource to use for read-only transactions. If available, a Connection from such a read-only DataSource will be lazily obtained within a Spring-managed transaction that has been marked as read-only".
