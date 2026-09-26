---
title: Nested lock acquisitions take their locks in one global order on every code path
rule_id: CC-06
domain: concurrency
triggers: ['synchronized\s*\(', '[.]lock\(\)', 'tryLock\(', 'writeLock\(\)', 'lockInterruptibly\(']
scope: callers
check_kind: semantic
severity_default: major
---

# Nested lock acquisitions take their locks in one global order on every code path

## Thesis
When a thread holds one lock and acquires a second — nested `synchronized` blocks, a `lock()` inside another `lock()` region, a call into a synchronized method from a synchronized method — every path in the codebase that acquires the same two locks acquires them in the same order. Where the two locks are instances chosen at run time, the order is derived from a stable key (an id, or `System.identityHashCode` with a tie-break lock), not from parameter position.

## Rationale
Two threads that each hold one of two locks and wait for the other never proceed: a thread holding A waits for B while a thread holding B waits for A. The wait has no timeout and throws nothing; the threads stay blocked until the process restarts. A single order removes the cycle: if every thread takes A before B, a thread holding B cannot be waiting for A. A stress test of three actors that each take two of three shared monitors names the deadlock — every actor holds one fork and waits for the other to drop, which is the outcome when all take the fork on one side first — and records no deadlock across 6.3 billion samples when the last actor takes its pair in the hierarchy's order. A comment stating the order is not enforcement; a sort by key before acquisition is.

## Example
```java
bad:  void transfer(Account from, Account to, long amt) {
          synchronized (from) { synchronized (to) { move(from, to, amt); } } }
good: void transfer(Account from, Account to, long amt) {
          Account a = from.id() < to.id() ? from : to, b = a == from ? to : from;
          synchronized (a) { synchronized (b) { move(from, to, amt); } } }
```

## Limits
Applies where a thread can hold two locks that another thread can also hold in the opposite order. A single lock, a second lock private to an object no other thread reaches, and a `tryLock` with a timeout on the inner lock that releases the outer lock on failure and retries are not cycles. Two instances with equal keys need a tie-break lock or a third ordering criterion before the nested acquisition.

## Validator
On the triggered hunk find each acquisition made while another lock is held: nested `synchronized`, `lock()` inside a lock region, a call to a `synchronized` method from inside a region. Name the two locks. Grep the repository for every other acquisition of either lock and read each site's enclosing region to see which lock it holds first. Validator question: **does any path acquire these two locks in the opposite order, or choose the order by parameter position when the locks are run-time instances?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-06`, severity major, `file`, `symbol`, `code` = the nested acquisition quoted verbatim from the diff, `fix` = the ordered acquisition by stable key, or the global order applied to the path that violates it, `rationale` naming the two paths whose orders differ and the cycle they form).

## Source
SEI CERT Oracle Coding Standard for Java, LCK07-J "Avoid deadlock by requesting and releasing locks in the same order". jcstress sample `problems/classic/Classic_01_DiningPhilosophers.java`, `ResourceHierarchy` — "The trivial deadlock in this problem is when every philosopher holds one fork, and waits for other fork to drop"; the resource-hierarchy solution "avoids the deadlock by asking the last philosopher to take the forks in the different order", no deadlock across 6,325,295,104 samples.
