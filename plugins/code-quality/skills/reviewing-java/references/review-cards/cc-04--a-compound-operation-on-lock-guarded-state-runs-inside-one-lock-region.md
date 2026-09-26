---
title: A compound operation on lock-guarded state runs inside one lock region, not across two
rule_id: CC-04
domain: concurrency
triggers: ['synchronized', '[.]lock\(\)', 'Collections[.]synchronized', 'Vector<', 'Hashtable<', 'StringBuffer', '[.]contains\(', '[.]isEmpty\(\)', '[.]size\(\)']
scope: file
check_kind: semantic
severity_default: major
---

# A compound operation on lock-guarded state runs inside one lock region, not across two

## Thesis
A check followed by an act, or a read followed by a dependent write, on lock-guarded state runs inside one `synchronized` block or `Lock` region that spans the whole operation. Two individually synchronized calls — two `synchronized` methods, two calls on a `Collections.synchronizedList`, a `Vector`, a `Hashtable` or a `StringBuffer` — are each atomic on their own and are not atomic together.

## Rationale
A lock region is released when its block exits; between the exit of the first region and the entry of the second, any other thread may take the lock and change the state the first region observed, so the second region acts on a stale premise. A stress test of a check-then-set on a `volatile` flag lets both threads pass the check and enter the section in 12.36% of samples; the same check and set inside one `synchronized` block never does. A synchronized collection wrapper synchronizes each method call on itself, so `contains` then `add` is two regions; the wrapper documents that every access must go through it and that traversal must be enclosed by the caller in `synchronized (list)` on the returned object.

## Example
```java
bad:  if (!members.contains(m)) members.add(m);   // members is a synchronizedList
      if (from.balance() >= amt) { from.withdraw(amt); to.deposit(amt); }
good: synchronized (members) { if (!members.contains(m)) members.add(m); }
      synchronized (lock) { if (from.balance() >= amt) { from.withdraw(amt); to.deposit(amt); } }
```

## Limits
Applies to state that other threads modify between the calls. Two calls on state confined to one thread, two calls whose second does not depend on the first's result, and one atomic call on a concurrent collection such as `putIfAbsent` or `computeIfAbsent` need no enclosing region. A tolerance stated in the project context — "duplicate membership accepted" — rejects the finding. The enclosing region locks the object the collection's own methods lock: the wrapper instance for a `Collections.synchronized*` view, the collection itself for a `Vector`.

## Validator
On the triggered hunk find each pair of calls on the same lock-guarded object or field where the second call's argument or execution depends on the first's result — `contains` then `add`, `get` then `put`, `size` then `get`, `isEmpty` then `remove`, a getter then a setter. Open the file: confirm the object is shared between threads and that no single `synchronized` or `Lock` region on the object's own lock encloses both calls. Validator question: **can another thread change this state between the first call and the second, so that the second acts on a stale premise?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-04`, severity major, `file`, `symbol`, `code` = both calls quoted verbatim from the diff, `fix` = one region on the object's own lock enclosing both, `rationale` naming the interleaving between the two regions).

## Source
`java.util.Collections#synchronizedList` Javadoc, Java SE 21 — "In order to guarantee serial access, it is critical that all access to the backing list is accomplished through the returned list"; "It is imperative that the user manually synchronize on the returned list when traversing it"; "Failure to follow this advice may result in non-deterministic behavior". jcstress sample `problems/racecondition/RaceCondition_02_CheckThenReact.java` — `Racy`: a check-then-set on a `volatile` flag, both actors enter the section in 12.36% of samples; `Sync`: the same under `synchronized (this)`, forbidden, zero samples. SEI CERT VNA03-J "Do not assume that a group of calls to independently atomic methods is atomic".
