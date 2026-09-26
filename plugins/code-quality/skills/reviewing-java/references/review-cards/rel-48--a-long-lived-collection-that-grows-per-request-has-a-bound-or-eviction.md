---
title: A long-lived collection that gains an entry per request, session or key has a bound or an eviction rule
rule_id: REL-48
domain: reliability
triggers: ['static .*(Map|List|Set|Cache)<', 'private final .*(Map|List|Set)<.*= new (Hash|Concurrent|Linked|Tree)', '\b[A-Z_]{3,}[.](put|add)\(', 'this[.]\w+[.](put|add)\(', 'computeIfAbsent\(', 'Caffeine', 'removeEldestEntry', 'maximumSize\(', 'expireAfter']
scope: file
check_kind: semantic
severity_default: major
---

# A long-lived collection that gains an entry per request, session or key has a bound or an eviction rule

## Thesis
A `Map`, `List` or `Set` held in a static field or in a singleton bean, to which code adds an entry keyed by a request, a user, a session, a message or any value the outside world supplies, also removes entries: a maximum size with eviction (`Caffeine.maximumSize`, `LinkedHashMap.removeEldestEntry`), a time-to-live, a removal at the end of the unit of work, or weak keys; a plain `HashMap` that only grows is not a cache.

## Rationale
A collection in a static field or a long-lived bean is reachable for the life of the process, and so is everything it references: the garbage collector cannot reclaim an entry that is still in the map, whatever the code's intent. Each request adds one entry, none removes it, the heap fills over hours or days, and the process dies of `OutOfMemoryError` after a run long enough that the tests never reproduce it. In a study of 491 leak issues in fifteen large Java projects, collection mismanagement — "Dead objects referenced by a collection" — was the most common root cause of memory leaks, at 39% of them, and "in particular when the collection is used as a static member. The reason is that the static fields are never garbage-collected". A bounded map deletes its eldest entry as new ones arrive, "maintaining a steady state".

## Example
```java
bad:  private static final Map<String, Session> SESSIONS = new ConcurrentHashMap<>();
      void open(String id) { SESSIONS.put(id, new Session(id)); }          // never removed
good: private final Cache<String, Session> sessions = Caffeine.newBuilder()
          .maximumSize(10_000).expireAfterAccess(Duration.ofMinutes(30)).build();
      void open(String id) { sessions.put(id, new Session(id)); }
```

## Limits
A collection populated once at startup from a bounded source (an enum, a configuration file, a reference table) and read thereafter is out of scope. A map whose entries are removed on a matching event in the same class — `close(id)` removing what `open(id)` put — is bounded by the protocol; open the file before flagging. A collection whose key space is bounded by construction (a small enum) is bounded. A project context naming a memory budget and a measured entry count within it rejects the finding.

## Validator
On the triggered hunk find each `put`, `add` or `computeIfAbsent` on a collection held in a static field or a singleton bean, whose key or element comes from a request, message, user or other external value. Open the file for a removal path, a size bound, an expiry, or weak references. Validator question: **can this collection grow with the number of requests or keys seen, with no bound or removal?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-48`, severity major, `file`, `symbol`, `code` = the collection declaration and the growing insertion quoted verbatim from the diff, `fix` = a bounded cache with a maximum size or expiry, or a removal on the matching event, `rationale` naming the entries the process can never reclaim).

## Source
arXiv:1810.00101 (Ghanavati, Costa, Seboek, Lo, Andrzejak, "Memory and Resource Leak Defects and their Repairs in Java Projects") §4.4 — "Collection mismanagement (collection) is the most common root cause for memory leaks (39% of the cases)"; "Leaks due to collection mismanagement can lead to severe memory waste, in particular when the collection is used as a static member. The reason is that the static fields are never garbage-collected"; Table 5 — "Dead objects referenced by a collection" 93 of 491 issues, "Over-sized cache or buffer" 14. `java.util.LinkedHashMap#removeEldestEntry` Javadoc, Java SE 21 — "This is useful if the map represents a cache: it allows the map to reduce memory consumption by deleting stale entries ... maintaining a steady state of 100 entries".
