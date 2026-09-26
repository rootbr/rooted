---
title: A synchronized block locks a private final field, never this, a Class literal, a reassignable field, or an interned constant
rule_id: CC-05
domain: concurrency
triggers: ['synchronized\s*\(', 'synchronized\s+(static\s+)?[\w<>\[\]]+\s+\w+\s*\(', 'Object\s+\w*[Ll]ock\b', '[.]class\s*\)', 'synchronized\s*\(\s*this\s*\)']
scope: file
check_kind: mechanical
severity_default: major
---

# A synchronized block locks a private final field, never this, a Class literal, a reassignable field, or an interned constant

## Thesis
The monitor a `synchronized` block takes is a `private final` field created for that purpose — `private final Object lock = new Object()` — or a `private final ReentrantLock`. It is not `this` or a `synchronized` method (the object's own monitor, which any holder of a reference can lock), not a `Class` literal (a JVM-wide monitor), not a field that can be reassigned, and not a `String` literal or boxed primitive (an object shared with unrelated code).

## Rationale
Locking on a field that is reassigned gives no mutual exclusion: two threads that read the field before and after the reassignment lock different objects and both enter the region. Locking on a field to guard updates of that same field fails the same way, because the lock is on the referenced object, not on the field. A monitor reachable from outside the class — `this`, the class object, a non-private field — lets unrelated code hold it: a caller that synchronizes on the object for its own purposes, or holds it indefinitely, blocks every method that uses the same monitor, and a subclass can take it for unrelated operations. Interned strings and cached boxed values are one object across the whole JVM, so two classes that lock on `"LOCK"` or on `Integer.valueOf(0)` serialize each other and can deadlock.

## Example
```java
bad:  private Object lock = new Object();   void reset() { lock = new Object(); }
      void add(int n) { synchronized (lock) { total += n; } }
      void bump() { synchronized ("LOCK") { count++; } }
good: private final Object lock = new Object();
      void add(int n) { synchronized (lock) { total += n; } }
      void bump() { synchronized (lock) { count++; } }
```

## Limits
Applies to a class whose instances are reachable from code the class does not control. A `synchronized` method or `synchronized (this)` in a class that is package-private or final and whose instances never leave the module is a tolerance the project context may state ("synchronized methods accepted in internal classes"); the reassignable-field and shared-constant cases have no tolerance. Locking on the wrapper returned by `Collections.synchronized*`, which the wrapper's own methods lock, is the documented form. Locking on a `java.util.concurrent` object such as an `AtomicInteger` does not stop its own methods from running and is flagged.

## Validator
On the triggered hunk take each `synchronized (expr)` and each `synchronized` method. Resolve `expr`: flag `this`, a class literal, a `String` literal or constant, a boxed primitive, and any field that is not both `private` and `final`; open the file to read the field's modifiers and to look for any method that assigns it. Validator question: **is the monitor anything other than a private final lock object or the class's documented internal lock?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-05`, severity major, `file`, `symbol`, `code` = the `synchronized` statement and the lock field's declaration quoted verbatim from the diff, `fix` = the private final lock field, `rationale` naming which failure applies: no exclusion after reassignment, an externally reachable monitor, or a JVM-wide shared constant). When the monitor is `this`, a `Class` literal or a `synchronized` method's own object — an exposure, not a lost exclusion — the finding is emitted at severity minor.

## Source
Error Prone `SynchronizeOnNonFinalField` — "Synchronizing on non-final fields is not safe: if the field is ever updated, different threads may end up locking on different objects". SpotBugs `ML_SYNC_ON_FIELD_TO_GUARD_CHANGING_THAT_FIELD` — "guarding a field gets a lock on the referenced object, not on the field"; `USO_UNSAFE_METHOD_SYNCHRONIZATION` and `USO_UNSAFE_OBJECT_SYNCHRONIZATION` — a monitor reachable outside the class can be held indefinitely by other code; `DL_SYNCHRONIZATION_ON_SHARED_CONSTANT` and `DL_SYNCHRONIZATION_ON_BOXED_PRIMITIVE` — interned strings and cached boxes are shared JVM-wide; `JLM_JSR166_UTILCONCURRENT_MONITORENTER` — a `java.util.concurrent` instance has "its own concurrency control mechanisms that are orthogonal to the synchronization provided by the Java keyword synchronized", so "synchronizing on an AtomicBoolean will not prevent other threads from modifying the AtomicBoolean". SEI CERT LCK00-J "Use private final lock objects to synchronize classes that may interact with untrusted code" and LCK01-J "Do not synchronize on objects that may be reused"; CWE-821, CWE-412.
