---
title: A constructor does not let this escape before it returns, through a listener registration, a thread start, or a hand-off to another object
rule_id: CC-15
domain: concurrency
triggers: ['\(this\)', '\(this,', ',\s*this\)', 'addListener\(', 'register\w*\(', 'new Thread\(']
scope: file
check_kind: mechanical
severity_default: major
---

# A constructor does not let this escape before it returns, through a listener registration, a thread start, or a hand-off to another object

## Thesis
Inside a constructor, `this` is not passed to another object, registered as a listener or callback, stored into a static or shared field, captured by a lambda or inner class that is published, or used to start a thread. Publication of the new object happens after the constructor returns — in a static factory method when the registration must accompany construction.

## Rationale
An object is completely initialized when its constructor finishes, and the initialization-safety guarantee of `final` fields holds only for a thread that can see the reference after that point. A reference that escapes mid-constructor lets another thread — the event source, the started thread — call methods on an object whose remaining fields, `final` or not, still hold `0`, `false` or `null`: a listener that reads a field the constructor assigns on its next line reads the default. Starting a thread in a constructor is the same escape with a guaranteed second thread, and the thread also runs before any subclass constructor body has executed.

## Example
```java
bad:  Listener(EventSource src) { src.register(this); this.limit = 42; }
good: private Listener() { this.limit = 42; }
      static Listener attach(EventSource src) {
          Listener l = new Listener(); src.register(l); return l; }
```

## Limits
Applies to a constructor whose `this` reaches code that can run on another thread or that reads the object's state before the constructor returns. Passing `this` to a helper that stores it in one of the object's own final fields (a builder, an inner component constructed with a back-reference) and does not publish it is confined and not flagged. A `super(...)` call is not an escape. The static factory with the registration after construction is the fix, not a `synchronized` constructor body.

## Validator
On the triggered hunk find each use of `this` inside a constructor as an argument, as a value stored elsewhere, as a capture in a lambda or anonymous class, or as the target of a `Thread.start` or executor submission. Open the file to see whether the callee stores or publishes the reference, or runs it on another thread. Validator question: **can another object or thread hold or use this reference before the constructor returns?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-15`, severity major, `file`, `symbol`, `code` = the escaping line and the fields assigned after it quoted verbatim from the diff, `fix` = the private constructor plus the static factory that publishes after construction, `rationale` naming the default-valued fields the early reader can observe).

## Source
SEI CERT Oracle Coding Standard for Java, TSM01-J "Do not let the this reference escape during object construction". JLS §17.5 — "An object is considered to be completely initialized when its constructor finishes. A thread that can only see a reference to an object after that object has been completely initialized is guaranteed to see the correctly initialized values for that object's final fields". SpotBugs `SC_START_IN_CTOR` — a thread started in a constructor "will be started before the subclass constructor is started". Error Prone `Immutable` — properly constructed means "the this reference does not escape the constructor".
