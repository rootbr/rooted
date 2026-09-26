---
title: A list that is accessed by index, iterated on a hot path, or kept sorted is an ArrayList, never a LinkedList
rule_id: PF-02
domain: performance
triggers: ['new LinkedList<', 'LinkedList<', 'new LinkedList\(', 'import java[.]util[.]LinkedList', 'List<\w+> \w+ = new LinkedList']
scope: file
check_kind: mechanical
severity_default: minor
---

# A list that is accessed by index, iterated on a hot path, or kept sorted is an ArrayList, never a LinkedList

## Thesis
A `List` on a hot path is an `ArrayList` (or an array): indexed reads and writes run in constant time and the elements are contiguous in memory. A list that must stay sorted is an `ArrayList` sorted once after filling, not a `LinkedList` grown by positional insertion. A queue or stack is an `ArrayDeque`. A `LinkedList` remains only where its one advantage is used — constant-time insertion or removal at a position reached through a live `ListIterator` — or where a queue must hold `null` elements.

## Rationale
Every `LinkedList` operation that indexes into the list traverses from the nearer end, so `get(i)` inside a loop is quadratic and a sorted insertion by index walks the list before each insert. Each element lives in its own node object, so a traversal chases one pointer per element into a different heap location, each a potential cache miss, and each node carries the previous and next references besides the element. `ArrayList` keeps the elements in one array: `size`, `isEmpty`, `get`, `set`, `iterator` and `listIterator` run in constant time, `add` in amortized constant time, and sequential access walks memory linearly, which the hardware prefetches. `ArrayDeque` gives constant-time operations at both ends on an array and is documented as likely faster than `LinkedList` as a queue.

## Example
```java
bad:  List<Event> events = new LinkedList<>();
      for (int i = 0; i < events.size(); i++) handle(events.get(i));
good: List<Event> events = new ArrayList<>();
      for (int i = 0; i < events.size(); i++) handle(events.get(i));
```

## Limits
A `LinkedList` mutated through a `ListIterator` at the cursor position in a long list, a tiny list off the hot path, and a queue that must store `null` elements (which `ArrayDeque` prohibits) are out of scope. A project tolerance naming the collection as not performance-relevant rejects the finding.

## Validator
On the triggered hunk find each `LinkedList` construction or declaration. Open the file and check how it is used: `get(int)`, `set(int, E)`, `add(int, E)` or `remove(int)`, iteration on a per-request or per-message path, insertion kept in sorted order, or plain queue and stack operations. Flag unless every access is through a `ListIterator` at the cursor or the queue stores `null`. Validator question: **is this `LinkedList` indexed, iterated on a hot path, kept sorted by positional insertion, or used as a plain queue or stack?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-02`, severity minor, `file`, `symbol`, `code` = the `LinkedList` construction or declaration quoted verbatim from the diff, `fix` = the `ArrayList`, `ArrayDeque`, `TreeMap` or `TreeSet` form, `rationale` naming the per-index traversal and the per-node pointer chase).

## Source
`java.util.LinkedList` class Javadoc, Java SE 21 — "Operations that index into the list will traverse the list from the beginning or the end, whichever is closer to the specified index". `java.util.ArrayList` class Javadoc — "The size, isEmpty, get, set, iterator, and listIterator operations run in constant time. The add operation runs in amortized constant time... The constant factor is low compared to that for the LinkedList implementation". `java.util.ArrayDeque` class Javadoc — "Null elements are prohibited. This class is likely to be faster than Stack when used as a stack, and faster than LinkedList when used as a queue."
