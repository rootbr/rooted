---
title: A ReentrantReadWriteLock guards state that is read far more often than written; a write-heavy path uses a single lock
rule_id: CC-44
domain: concurrency
triggers: ['ReadWriteLock', 'readLock\(\)', 'writeLock\(\)']
scope: file
check_kind: semantic
severity_default: minor
---

# A ReentrantReadWriteLock guards state that is read far more often than written; a write-heavy path uses a single lock

## Thesis
A `ReentrantReadWriteLock` is introduced where the file shows many concurrent readers and rare writers of a large or expensive-to-traverse structure; where writes are frequent, or the guarded operation is short, a `ReentrantLock`, a `synchronized` block or a concurrent collection guards the same state at lower cost.

## Rationale
A read-write lock lets readers proceed in parallel and excludes them all while a writer holds the lock; its bookkeeping — reader counts, hold tracking, writer preference — costs more per acquisition than a plain lock. The cost pays for itself only when the collection is expected to be large, is accessed by more reader threads than writer threads, and its operations outweigh the synchronization overhead. With frequent writes the readers are excluded most of the time anyway and every acquisition pays the extra bookkeeping, so throughput falls below the plain lock's. With short operations — a `get` on a `HashMap` — the acquisition dominates and the parallel-read benefit is small. A `ConcurrentHashMap` covers the common read-mostly map with no lock at all.

## Example
```java
bad:  private final ReadWriteLock rw = new ReentrantReadWriteLock(false);
      void record(Sample s) { rw.writeLock().lock(); try { samples.add(s); } finally { rw.writeLock().unlock(); } }  // per request
      // readers: one report every few minutes
good: private final Object lock = new Object();
      void record(Sample s) { synchronized (lock) { samples.add(s); } }
```

## Limits
Applies to a read-write lock introduced or restructured by the diff. A structure read on every request and written on a reload, a rebuild, or an administrative action is the intended case. A lock whose contention profile the project context states — read-to-write ratio, size — is judged by that statement. An existing lock merely touched is not reworked on this finding. A `StampedLock` is a different structure with its own trade-off.

## Validator
On the triggered hunk find the read-write lock and, in the file, the call sites that take the write lock and the read lock; judge their rates from where they sit — request handlers, loops, schedulers, reload hooks — and the size or cost of the guarded operation. Validator question: **are writes to this state as frequent as reads, or the guarded operations short, so that the read-write lock's bookkeeping outweighs its parallel-read benefit?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-44`, severity minor, `file`, `symbol`, `code` = the lock declaration and the frequent write site quoted verbatim from the diff, `fix` = a `ReentrantLock`, a `synchronized` block or a concurrent collection, `rationale` naming the write frequency and the bookkeeping cost).

## Source
`java.util.concurrent.locks.ReentrantReadWriteLock` class Javadoc, Java SE 21 — "ReentrantReadWriteLocks can be used to improve concurrency in some uses of some kinds of Collections. This is typically worthwhile only when the collections are expected to be large, accessed by more reader threads than writer threads, and entail operations with overhead that outweighs synchronization overhead".
