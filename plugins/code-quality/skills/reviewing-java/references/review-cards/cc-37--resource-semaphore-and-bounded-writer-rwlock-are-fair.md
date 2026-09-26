---
title: A Semaphore that controls access to a resource, and a ReentrantReadWriteLock whose writers must complete in bounded time, are constructed fair
rule_id: CC-37
domain: concurrency
triggers: ['new Semaphore\(', 'new ReentrantReadWriteLock\(']
scope: file
check_kind: mechanical
severity_default: minor
---

# A Semaphore that controls access to a resource, and a ReentrantReadWriteLock whose writers must complete in bounded time, are constructed fair

## Thesis
A `Semaphore` whose permits gate access to a resource — a connection, a slot, a downstream call — is constructed with `true` as its fairness argument; so is a `ReentrantReadWriteLock` whose write path must complete within a bounded time on a read-heavy structure. The constructors without the boolean select non-fair mode, in which a continuously contended lock or semaphore may postpone a waiting thread indefinitely.

## Rationale
Under continuous contention a non-fair lock may indefinitely postpone one or more waiting threads — a read-write lock's order of entry to the read and write lock is unspecified, so a writer can wait behind a stream of arriving readers; a non-fair semaphore permits barging, so a newly arriving thread takes a permit ahead of one that has waited — while normally giving higher throughput than fair mode. Fair mode grants access in approximate arrival order at a throughput cost that can be large, and guarantees lack of starvation on the lock, though not of thread scheduling. A semaphore that controls access to a resource is initialized fair so that no thread is starved of the resource; a semaphore used for another kind of synchronization usually takes the throughput of non-fair ordering. A writer that must publish within a bound cannot rely on the non-fair read-write lock, whose contended waits have no bound.

## Example
```java
bad:  private final Semaphore connections = new Semaphore(20);                  // gates a resource; a waiter may starve
      private final ReentrantReadWriteLock rw = new ReentrantReadWriteLock();  // writers must publish within a bound
good: private final Semaphore connections = new Semaphore(20, true);
      private final ReentrantReadWriteLock rw = new ReentrantReadWriteLock(true);
```

## Limits
Applies to a `Semaphore` whose permits stand for a resource — the file shows `acquire` or `tryAcquire` around a resource use — and to a `ReentrantReadWriteLock` whose writers the file or the project context shows must complete within a bound. A semaphore used as a signal or a one-shot gate, and a read-write lock whose writers may wait — a reload that runs whenever readers pause — keep the non-fair default and its throughput. A `ReentrantLock` carries the same trade-off and no documented case that requires fair mode; it is not flagged. A comment or a project-context statement choosing throughput over bounded waiting rejects the finding. `synchronized` has no fairness argument and is out of scope.

## Validator
On the triggered hunk find each `new Semaphore(` and `new ReentrantReadWriteLock(` and check whether the constructor receives `true`. Open the file: for the semaphore, find its `acquire`/`tryAcquire` sites and what they guard — a resource use marks it as resource access; for the read-write lock, find the write-lock sites and whether the file or the project context requires them to complete within a bound. Validator question: **is a resource-access semaphore, or a read-write lock whose writers need bounded waiting, constructed without `true` as its fairness argument?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-37`, severity minor, `file`, `symbol`, `code` = the constructor call quoted verbatim from the diff, `fix` = the same call with `true` as the fairness argument, `rationale` naming the indefinite postponement the non-fair default permits and the throughput cost fair mode carries).

## Source
`java.util.concurrent.Semaphore` class Javadoc, Java SE 21 — when fairness is false, "barging is permitted"; "Generally, semaphores used to control resource access should be initialized as fair, to ensure that no thread is starved out from accessing a resource"; `java.util.concurrent.locks.ReentrantReadWriteLock` class Javadoc, "Non-fair mode (default)" — "the order of entry to the read and write lock is unspecified"; "A nonfair lock that is continuously contended may indefinitely postpone one or more reader or writer threads, but will normally have higher throughput than a fair lock"; `java.util.concurrent.locks.ReentrantLock` — programs using fair locks "may display lower overall throughput (i.e., are slower; often much slower) than those using the default setting, but have smaller variances in times to obtain locks and guarantee lack of starvation". None of these pages states that the fairness boolean must be passed explicitly; that convention is not carried.
