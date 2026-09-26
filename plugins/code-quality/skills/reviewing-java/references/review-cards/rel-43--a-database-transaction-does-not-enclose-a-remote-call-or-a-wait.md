---
title: A database transaction does not enclose a remote call, file transfer, message send or wait for a user
rule_id: REL-43
domain: reliability
triggers: ['@Transactional', 'TransactionTemplate', 'RestTemplate', 'RestClient', 'WebClient', 'HttpClient', '[.](postFor\w+|getFor\w+|exchange|retrieve)\(', 'kafkaTemplate', 'send\(', 'Thread[.]sleep\(', 'Files[.]copy\(', '[.]await\(', 'Future[.]get\(']
scope: file
check_kind: semantic
severity_default: major
---

# A database transaction does not enclose a remote call, file transfer, message send or wait for a user

## Thesis
The body of a `@Transactional` method, or the callback of a `TransactionTemplate`, performs the database work and returns; a call to another service, a message send, a large file operation, a sleep or a wait on a future happens before the transaction begins or after it commits, so the connection and the row locks are held only for the database work.

## Rationale
A transaction holds a pooled connection for its whole duration and, from the first write, row locks that block every other writer of those rows. A remote call inside it stretches that duration to the remote's latency and, when the remote stalls, to the remote timeout: the pool drains at one connection per stalled call and the locked rows block unrelated requests. The physical transaction "needs to be as short as possible", because "long-running database transactions prevent your application from scaling to a highly-concurrent load", and "long-running transactions can deplete a connection pool so other transactions don't get a chance to proceed".

## Example
```java
bad:  @Transactional public void place(Order o) { repo.save(o); payments.charge(o); notifier.send(o); }
good: public void place(Order o) { tx.executeWithoutResult(s -> repo.save(o));
          payments.charge(o); notifier.send(o); }   // or an after-commit synchronization / outbox
```

## Limits
A transaction that must span a remote resource under a distributed transaction manager (XA) the project context names is out of scope. A short, bounded remote lookup needed to decide the write, with a timeout well under the pool's wait, may stay inside when a comment names the trade-off. A message send registered through `TransactionSynchronization.afterCommit` or a transactional outbox is the correct form and is not flagged.

## Validator
On the triggered hunk find each transactional method or template callback and open the file to list what it calls: HTTP or gRPC clients, message producers, file transfers, sleeps, waits on futures or latches. Validator question: **does this transaction stay open across a call whose duration is set by another process or a user?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-43`, severity major, `file`, `symbol`, `code` = the transactional boundary and the enclosed call quoted verbatim from the diff, `fix` = the remote call moved outside the transaction or into an after-commit synchronization or outbox, `rationale` naming the connection and locks held for the remote's latency).

## Source
Hibernate ORM user guide, chapter "Transactions and concurrency control" — "To reduce lock contention in the database, the physical database transaction needs to be as short as possible. Long-running database transactions prevent your application from scaling to a highly-concurrent load. Do not hold a database transaction open during end-user-level work, but open it after the end-user-level work is finished"; chapter "Batching" — "long-running transactions can deplete a connection pool so other transactions don't get a chance to proceed".
