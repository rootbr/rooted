---
title: REQUIRES_NEW is used from inside an active transaction only when the connection pool exceeds the number of concurrent threads
rule_id: REL-42
domain: reliability
triggers: ['REQUIRES_NEW', 'Propagation[.]REQUIRES_NEW', 'TransactionTemplate', 'PROPAGATION_REQUIRES_NEW']
scope: callers
check_kind: semantic
severity_default: major
---

# REQUIRES_NEW is used from inside an active transaction only when the connection pool exceeds the number of concurrent threads

## Thesis
A method with `Propagation.REQUIRES_NEW` that can be called while the caller's transaction is active — an audit write, a status update that must survive a rollback — is used only where the project's connection pool is sized above the number of threads that can hold an outer transaction at once.

## Rationale
`REQUIRES_NEW` "always uses an independent physical transaction for each affected transaction scope": the outer transaction's connection stays bound to the thread while the inner one takes a second connection from the pool. When N threads each hold an outer connection and wait for an inner one from a pool of N, none can be served, and the reference states the consequence — "This may lead to exhaustion of the connection pool and potentially to a deadlock if several threads have an active outer transaction and wait to acquire a new connection for their inner transaction ... Do not use PROPAGATION_REQUIRES_NEW unless your connection pool is appropriately sized, exceeding the number of concurrent threads by at least 1". The deadlock appears only at full load, which is when the pool is exactly consumed.

## Example
```java
bad:  @Transactional public void process(Item i) { work(i); audit.record(i); }   // audit.record is REQUIRES_NEW: two connections per thread, from a pool sized to the thread count
good: @Transactional public void process(Item i) { work(i); }
      // audit.record(i) called after commit from a TransactionSynchronization, or with REQUIRED
```

## Limits
A `REQUIRES_NEW` method called only from non-transactional callers starts one transaction and takes one connection; it is out of scope. A project context stating a pool size above the request-thread count plus the inner-transaction demand rejects the finding. Work that must commit independently can instead run after the outer commit (`TransactionSynchronization.afterCommit`) or on a separate pool the project context names.

## Validator
On the triggered hunk find each `REQUIRES_NEW` declaration or `TransactionTemplate` with that propagation and find its callers across the repository: are they `@Transactional`, or reached from a transactional method? Read the project context for pool size and thread count. Validator question: **can a thread holding an outer transaction's connection wait here for a second connection from a pool that all such threads can exhaust?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-42`, severity major, `file`, `symbol`, `code` = the propagation declaration and the transactional call site quoted verbatim from the diff, `fix` = `REQUIRED`, an after-commit synchronization, or a pool sized above the concurrent outer transactions, `rationale` naming the two connections per thread and the pool deadlock).

## Source
Spring Framework reference, "Transaction Propagation", "Understanding PROPAGATION_REQUIRES_NEW" — "always uses an independent physical transaction for each affected transaction scope, never participating in an existing transaction for an outer scope"; note — "The resources attached to the outer transaction will remain bound there while the inner transaction acquires its own resources such as a new database connection. This may lead to exhaustion of the connection pool and potentially to a deadlock if several threads have an active outer transaction and wait to acquire a new connection for their inner transaction, with the pool not being able to hand out any such inner connection anymore. Do not use PROPAGATION_REQUIRES_NEW unless your connection pool is appropriately sized, exceeding the number of concurrent threads by at least 1".
