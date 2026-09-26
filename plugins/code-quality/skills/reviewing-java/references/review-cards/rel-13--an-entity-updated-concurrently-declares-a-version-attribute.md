---
title: An entity that can be updated by concurrent transactions or merged from a detached state declares a @Version attribute
rule_id: REL-13
domain: reliability
triggers: ['@Entity', '@Version', '[.]merge\(', '[.]save\(', '@PutMapping', '@PatchMapping']
scope: file
check_kind: semantic
severity_default: major
---

# An entity that can be updated by concurrent transactions or merged from a detached state declares a @Version attribute

## Thesis
A JPA entity whose rows can be modified by two units of work at once — anything edited through a request handler, merged after a round trip to a client, or updated by a scheduled job alongside user traffic — carries a `@Version` field, so that the second write cannot silently replace the first.

## Rationale
Without a version, the persistence provider issues an unconditional `UPDATE`: the last transaction to commit wins and the changes of the intervening one are lost with no error, which is the lost-update anomaly. With a version attribute the provider "is required to perform optimistic locking automatically for every entity with a version": the update carries `WHERE version = ?`, an intervening commit makes it match zero rows, and the provider throws `OptimisticLockException` and marks the transaction for rollback, so the conflict becomes visible and can be retried or shown to the user. The merge or save site then handles that `OptimisticLockException` (under Spring, `ObjectOptimisticLockingFailureException`) by retrying or reporting the conflict; the handling is the consequence the version makes possible, not a substitute for it. The specification states that failure to use optimistic locking "often leads to inconsistent entity state, lost updates, and other anomalies".

## Example
```java
bad:  @Entity class Account { @Id Long id; BigDecimal balance; }
      void deposit(Long id, BigDecimal amt) { Account a = em.find(Account.class, id); a.balance = a.balance.add(amt); }
good: @Entity class Account { @Id Long id; @Version long version; BigDecimal balance; }
      void deposit(Long id, BigDecimal amt) { Account a = em.find(Account.class, id); a.balance = a.balance.add(amt); }
```

## Limits
Applies to entities updated in place. An append-only entity (events, audit rows), an entity updated only by one single-threaded process, or a row-level pessimistic lock (`LockModeType.PESSIMISTIC_WRITE`) around every update is correct without a version. A concurrent increment done as one atomic `UPDATE ... SET balance = balance + ?` statement does not lose updates and is out of scope. A project context that names last-writer-wins as acceptable for an entity rejects the finding for that entity.

## Validator
On the triggered hunk find each `@Entity` class added or modified, and each `merge`/`save` of an entity from a request handler or a job. Open the entity and check for a `@Version` attribute; check whether the update path uses a pessimistic lock or an atomic SQL update instead. Validator question: **can two units of work update the same row of this entity, and would the second commit overwrite the first without a version check?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-13`, severity major, `file`, `symbol`, `code` = the entity declaration or the merge/save call quoted verbatim from the diff, `fix` = a `@Version` attribute on the entity, `rationale` naming the lost update).

## Source
Jakarta Persistence specification, chapter "Entity Operations", section "Optimistic Locking" — "Optimistic lock verification ensures that an update of a given item is successful only when no intervening transaction has already updated the item, preventing the loss of updates"; "The persistence provider is required to perform optimistic locking automatically for every entity with a version"; on conflict the provider must "throw an OptimisticLockException and mark the current transaction for rollback"; "Applications are strongly encouraged to enable optimistic locking for every entity which may be concurrently accessed or which may be merged from a detached state. Failure to make use of optimistic locking often leads to inconsistent entity state, lost updates, and other anomalies". Hibernate ORM user guide, chapter "Locking", "Optimistic" and "Mapping optimistic locking".
