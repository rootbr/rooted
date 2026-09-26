---
title: A lock region contains no call that can block on I/O, a remote service, a queue or another thread's work
rule_id: CC-03
domain: concurrency
triggers: ['synchronized', '[.]lock\(\)', 'lockInterruptibly\(', 'tryLock\(', 'writeLock\(\)', 'readLock\(\)']
scope: file
check_kind: semantic
severity_default: major
---

# A lock region contains no call that can block on I/O, a remote service, a queue or another thread's work

## Thesis
Code that runs while holding a monitor or `Lock` performs no operation that can block for an unbounded time — no socket, file or database I/O, no HTTP or RPC call, no `BlockingQueue.put` or `take`, no `Future.get`, `CompletableFuture.join`, `Thread.sleep` or `await` on another thread's work. The region snapshots what the call needs, releases the lock, makes the call, and applies the result in a second short region.

## Rationale
A lock serializes every thread that needs it, so the time the holder spends blocked is added to the wait of every thread queued on the lock: a 30-second remote timeout becomes a 30-second stall for each of them. When the blocking call itself waits on a thread that needs this lock — a consumer that must take from the queue the holder is putting into, a task submitted to a pool whose workers all wait on the lock — no thread can proceed, and the result is a deadlock that no lock-ordering analysis shows because only one lock is involved. Sleeping with a lock held has the same effect with no I/O at all: the other threads wait for the sleep to end.

## Example
```java
bad:  synchronized (lock) { current = client.fetch(current.version()); }
good: Version v;
      synchronized (lock) { v = current.version(); }
      Config fresh = client.fetch(v);
      synchronized (lock) { if (current.version().equals(v)) current = fresh; }
```

## Limits
Applies to a region on a lock that other threads contend for. A `BlockingQueue.offer` or `poll` with a timeout, a `tryLock` with a timeout, or a `get` on a future whose task cannot need this lock and that carries a bounded timeout is a bounded wait the project context may tolerate when it states the bound. A lock whose purpose is to serialize the I/O itself — one writer to a file, a connection that is not thread-safe — holds the I/O by design; the finding then names other alien calls made in the same region, not the I/O. A short in-memory computation is not blocking.

## Validator
On the triggered hunk take each `synchronized` block or method and each `lock()`…`unlock()` region. Open the file and list every call made inside it, following calls into methods of the same file. Flag a call that reads or writes a socket, file or database, sends a request over the network, or calls `put`, `take`, `get`, `join`, `await`, `sleep` or `acquire` on another thread's progress. Validator question: **can any call inside this lock region wait for I/O, a remote service, or another thread's work?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-03`, severity major, `file`, `symbol`, `code` = the lock region's opening line and the blocking call quoted verbatim from the diff, `fix` = the call moved outside the region with a snapshot before it and a short apply region after it, `rationale` naming the wait every contender inherits and the single-lock deadlock the blocked call can form).

## Source
SEI CERT Oracle Coding Standard for Java, LCK09-J "Do not perform operations that can block while holding a lock". SpotBugs `SWL_SLEEP_WITH_LOCK_HELD` — calling `Thread.sleep()` with a lock held "may result in very poor performance and scalability, or a deadlock, since other threads may be waiting to acquire the lock" (CWE-667 Improper Locking).
