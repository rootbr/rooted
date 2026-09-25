---
title: A loop that persists many entities flushes and clears the persistence context every batch and relies on JDBC batching, not one save per element
rule_id: REL-47
domain: reliability
triggers: ['for \(.*\)\s*\{?\s*\w*repo\w*[.]save\(', '[.]save\(', '[.]persist\(', 'saveAll\(', '[.]flush\(\)', '[.]clear\(\)', 'batch_size', 'jdbc[.]batch']
scope: file
check_kind: semantic
severity_default: major
---

# A loop that persists many entities flushes and clears the persistence context every batch and relies on JDBC batching, not one save per element

## Thesis
Code that inserts or updates a large or unbounded number of entities in one unit of work persists them in batches: it calls `flush()` and `clear()` regularly — every batch of `hibernate.jdbc.batch_size` entities, an integer between 10 and 50 — or uses a `StatelessSession`, so the first-level cache stays small and the statements are sent as JDBC batches; it does not call `repo.save(x)` per element with the whole set managed until commit.

## Rationale
Every persisted entity stays managed in the session until it is flushed and cleared: a loop over 100,000 rows keeps 100,000 managed instances plus their snapshots, and "if the maximum memory allocated to the JVM is rather low, this example could fail with an OutOfMemoryException". The transaction runs as long as the loop, and "long-running transactions can deplete a connection pool so other transactions don't get a chance to proceed". JDBC batching "is not enabled by default, so every insert statement requires a database round trip"; with `hibernate.jdbc.batch_size` set to an integer between 10 and 50, a flush sends the batch in one round trip, and clearing after the flush bounds the cache. An identity generator disables insert batching, so the id strategy is part of the check.

## Example
```java
bad:  for (Item i : items) repo.save(i);                       // items: an import of unknown size
good: int n = 0;
      for (Item i : items) {
          em.persist(i);
          if (++n % BATCH == 0) { em.flush(); em.clear(); }    // BATCH = hibernate.jdbc.batch_size, 10 to 50
      }
```

## Limits
A loop over a bounded handful of entities — a form with a few lines — is out of scope. `saveAll` on a small list is fine; on an unbounded one it still manages every entity until commit and is flagged the same way. A `StatelessSession` or a JDBC batch (`PreparedStatement.addBatch`) is the correct form. A project context stating that `hibernate.jdbc.batch_size` and `order_inserts` are configured satisfies the batching half; the flush-and-clear half remains.

## Validator
On the triggered hunk find each loop that persists or saves per element, or a `saveAll` of an unbounded collection. Open the file for the collection's origin and size, for periodic `flush`/`clear`, and for a stateless session or JDBC batch. Validator question: **can this loop hold an unbounded number of managed entities in one transaction, sending one statement per element?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-47`, severity major, `file`, `symbol`, `code` = the loop quoted verbatim from the diff, `fix` = `persist` with `flush()`/`clear()` every batch, or a `StatelessSession`, `rationale` naming the growing first-level cache and the long transaction).

## Source
Hibernate ORM user guide, chapter "Batching" — "Hibernate caches all the newly inserted Person instances in the session-level cache, so, when the transaction ends, 100 000 entities are managed by the persistence context. If the maximum memory allocated to the JVM is rather low, this example could fail with an OutOfMemoryException"; "long-running transactions can deplete a connection pool so other transactions don't get a chance to proceed"; "JDBC batching is not enabled by default, so every insert statement requires a database round trip. To enable JDBC batching, set the hibernate.jdbc.batch_size property to an integer between 10 and 50"; "Batch inserts" — "When you make new objects persistent, employ methods flush() and clear() to the session regularly, to control the size of the first-level cache"; "Hibernate disables insert batching at the JDBC level transparently if you use an identity identifier generator".
