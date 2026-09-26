---
title: A field that another thread may write is read once into a local before it is tested and used, never tested and then re-read
rule_id: CC-49
domain: concurrency
triggers: ['\(\s*(?:this[.])?(\w+)\s*[!=]=\s*null\b[^;{]*\b\1\b', 'while\s*\(\s*!?\s*(?:this[.])?\w+\s*\)\s*[{;]', 'getOpaque\(', 'getAcquire\(', '\bvolatile\b']
scope: file
check_kind: semantic
severity_default: major
---

# A field that another thread may write is read once into a local before it is tested and used, never tested and then re-read

## Thesis
A method that tests a field another thread can write and then acts on it — `if (handler != null) handler.handle(e)`, `while (!done) { }` — copies the field into a local once and tests and uses the local. The local is the fix whether the field is `volatile` or plain; a plain field that is shared additionally needs its visibility guarantee, which is judged on its own.

## Rationale
Two reads of one field in a method are two independent loads. For a `volatile` field the writes are seen in one order, but a write can land between the two reads: the test sees a listener, the use sees `null`, and the method throws `NullPointerException` on the path the test excluded. For a plain field the memory model does not even keep the order: without synchronization the order of independent reads is undefined, including reads of the same variable, so the second read may return the older value after the first returned the newer. A stress test reading one plain `int` twice while another thread wrote it observed the pair (newer, older) in 6,376 of about 210 million samples, an outcome forbidden once the field was `volatile` or read with opaque access. A compiler may also hoist a plain-field read out of a loop, so a spin on a plain field can miss the write entirely. One read into a local gives the test and the use the same value whatever the field's declaration, and the copy costs nothing; the double-checked idiom's fast path reads its field once into a local.

## Example
```java
bad:  if (listener != null) listener.onEvent(e);            // two reads: the second may return null
good: Listener l = listener;
      if (l != null) l.onEvent(e);
```

## Limits
Applies to a field another thread can write between the reads: a settable listener, a flag, a swappable configuration. A lazily initialized field is judged by the double-checked idiom on its own. A field confined to one thread, a `final` field, or a field read under the same lock that guards its writes has no race, and a second read there is a style matter. The local copy does not make a plain shared field visible across threads; that guarantee comes from `volatile`, an atomic type or a lock and is a separate matter. A spin loop on a plain field is flagged for the hoisting hazard even where a missed update would be harmless.

## Validator
On the triggered hunk find each field read twice in one method — a null or state test followed by a use, a loop condition on the field — and determine from the file whether another thread can write the field: a setter, an assignment from a callback or scheduler, no `final`, no enclosing lock covering both reads. Validator question: **can the field's value change, or be observed out of order, between the test and the use because the method reads it twice instead of once into a local?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-49`, severity major, `file`, `symbol`, `code` = the test and the use, or the loop, quoted verbatim from the diff, `fix` = the single read into a local that is then tested and used, `rationale` naming the second read that can differ from the first and, for a plain field, the (newer, older) pair the memory model permits).

## Source
jcstress `jcstress-samples/.../jmm/basic/BasicJMM_05_Coherence.java` (fetched, `master`) — `SameRead`: "in absence of synchronization, the order of independent reads is undefined. That includes reads of the *same* variable!"; outcome `1, 0` "First read seen racy value early, and the second one did not" observed 6,376 times in the recorded run; `SameVolatileRead` and `SameOpaqueRead`: coherence "mandates that the writes to the same variable to be observed in a total order ... Java volatile assumes this property", `1, 0` forbidden and not observed. jcstress `primitives/singletons/Singleton_05_DCL.java` — the fast path reads the field once into a local ("T t = instance; if (t != null) return t;"). SpotBugs `SP_SPIN_ON_FIELD` (fetched from `spotbugs/etc/messages.xml`, `master`) — "The compiler may legally hoist the read out of the loop, turning the code into an infinite loop".
