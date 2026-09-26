---
title: A class whose instances are shared without synchronization declares every field final and exposes no mutable state
rule_id: CC-14
domain: concurrency
triggers: ['@Immutable', '[Ii]mmutable', 'record\s+\w+\s*\(', 'final class \w+', 'AtomicReference<', 'static final \w+(<[^>]*>)? \w+ = new']
scope: file
check_kind: semantic
severity_default: major
---

# A class whose instances are shared without synchronization declares every field final and exposes no mutable state

## Thesis
A class documented or annotated as immutable, or whose instances are handed between threads as values without a lock — a configuration snapshot, a cache entry, an event, a record — declares every field `final` and holds no reference to a mutable object that any method exposes or mutates after construction. Such an object can then be read from any thread without synchronization.

## Rationale
A `final` field carries initialization safety: a thread that sees a reference to the object after the constructor completes sees the constructor's write to that field, even when the reference itself arrived through a data race. A non-final field has no such guarantee: a stress test that publishes an object with four plain `int` fields through a plain field observes readers seeing partially constructed objects — some fields at their constructor values, others still `0` — on both x86_64 and AArch64; the same test with the four fields `final` observes only the default reference or the complete object. Finality of the reference is not finality of what it points to: a `final List` that a getter returns for the caller to mutate, or that a method appends to, is shared mutable state and needs its own synchronization.

## Example
```java
bad:  final class Settings { private Map<String, String> values;
          Settings(Map<String, String> v) { values = v; }
          Map<String, String> values() { return values; } }
good: final class Settings { private final Map<String, String> values;
          Settings(Map<String, String> v) { values = Map.copyOf(v); }
          Map<String, String> values() { return values; } }
```

## Limits
Applies to a class whose instances cross threads without a lock or `volatile` on every access. A class confined to one thread, a mutable entity always accessed under its owner's lock, and a class that documents itself as not thread-safe are not flagged. A lazily computed cache field inside an otherwise immutable class (a memoized hash) is a tolerance the project context may state when the computed value is idempotent and the field is written once. A `record` has `final` components by construction; a record whose component holds a mutable collection still needs the copy in its compact constructor.

## Validator
On the triggered hunk take the class that the annotation, name or shared reference marks as a value shared across threads. Open the file: list every field and flag one that is not `final`, and one whose type is a mutable collection or array that a method returns or modifies after construction. Validator question: **does this shared value class have a non-final field, or expose or mutate a mutable object it holds after construction?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-14`, severity major, `file`, `symbol`, `code` = the class header and the offending field or accessor quoted verbatim from the diff, `fix` = the `final` modifier and the copy or unmodifiable wrapper, `rationale` naming the partially constructed or externally mutated state another thread can observe).

## Source
jcstress sample `jmm/basic/BasicJMM_08_Finals.java` — `PlainInit`: "Seeing partially constructed object" observed on x86_64 and AArch64; `FinalInit`: "If we put them on all critical fields, then the only observed state is full object", other outcomes forbidden, none observed. Error Prone `Immutable` — the conservative definition of an immutable object: "All fields are final; All reference fields are of immutable type, or null; It is properly constructed (the this reference does not escape the constructor)". JLS §17.5 final field semantics.
