---
title: A map read and written concurrently by many threads on a hot path is a ConcurrentHashMap, not a Collections.synchronizedMap wrapper or a Hashtable
rule_id: PF-10
domain: performance
triggers: ['synchronizedMap\(', 'synchronizedSet\(', 'Hashtable<', 'new Hashtable', 'Collections[.]synchronized']
scope: file
check_kind: mechanical
severity_default: minor
---

# A map read and written concurrently by many threads on a hot path is a ConcurrentHashMap, not a Collections.synchronizedMap wrapper or a Hashtable

## Thesis
A map shared by several threads and accessed on a hot path — a cache, a registry, a per-key counter table — is a `ConcurrentHashMap`; `Collections.synchronizedMap(new HashMap<>())` and `Hashtable` are replaced unless the code needs to hold one lock across a compound operation or an iteration.

## Rationale
The synchronized wrapper and `Hashtable` guard every operation with one monitor: a `get` on one key waits for a `put` on another, so under concurrent access the threads serialize on the single lock and the map's throughput is that of one thread plus the contention. `ConcurrentHashMap` supports full concurrency of retrievals and high expected concurrency for updates: `get` does not block and overlaps with updates, and updates on different bins proceed in parallel. Its atomic `compute`, `merge` and `putIfAbsent` cover the read-modify-write cases that otherwise need the wrapper's lock, and the platform recommends it in place of `Hashtable` where a thread-safe, highly concurrent map is wanted.

## Example
```java
bad:  private final Map<String, Session> sessions =
          Collections.synchronizedMap(new HashMap<>());
good: private final ConcurrentMap<String, Session> sessions = new ConcurrentHashMap<>();
```

## Limits
A map iterated under one lock while other threads may modify it, or updated by multi-key operations that must appear atomic, keeps the wrapper or an explicit lock. A map confined to one thread needs neither. `ConcurrentHashMap` permits no `null` key or value; code that stores `null` keeps the wrapper. Whether a plain `HashMap` shared between threads is safe at all is a thread-safety question this rule does not decide.

## Validator
On the triggered hunk find each `Collections.synchronizedMap` or `synchronizedSet` wrapper and each `Hashtable`. Open the file: confirm the map is shared (a field of a shared object, or static) and accessed per request or per event, and that no `synchronized (map)` block iterates it or groups several operations. Validator question: **do several threads read or update this map on a hot path through one monitor, with no compound operation that needs the single lock?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-10`, severity minor, `file`, `symbol`, `code` = the wrapper or `Hashtable` construction quoted verbatim from the diff, `fix` = `ConcurrentHashMap`, `rationale` naming the single monitor every operation takes).

## Source
`java.util.concurrent.ConcurrentHashMap` class Javadoc, Java SE 21 — "A hash table supporting full concurrency of retrievals and high expected concurrency for updates"; "Retrieval operations (including get) generally do not block, so may overlap with update operations". `java.util.Collections#synchronizedMap` Javadoc — "Returns a synchronized (thread-safe) map backed by the specified map. In order to guarantee serial access, it is critical that all access to the backing map is accomplished through the returned map"; in the JDK 21 source every method of the returned `SynchronizedMap` runs inside `synchronized (mutex)`. `java.util.Hashtable` class Javadoc — "If a thread-safe highly-concurrent implementation is desired, then it is recommended to use ConcurrentHashMap in place of Hashtable."
