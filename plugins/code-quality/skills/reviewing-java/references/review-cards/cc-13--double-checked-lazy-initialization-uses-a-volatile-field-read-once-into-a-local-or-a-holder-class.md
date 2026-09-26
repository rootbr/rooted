---
title: Double-checked lazy initialization reads a volatile field once into a local, checks it twice, and assigns last, or uses a holder class
rule_id: CC-13
domain: concurrency
triggers: ['==\s*null', 'synchronized', 'getInstance\(', 'INSTANCE', '[Ll]azy']
scope: file
check_kind: mechanical
severity_default: major
---

# Double-checked lazy initialization reads a volatile field once into a local, checks it twice, and assigns last, or uses a holder class

## Thesis
A lazily initialized field that is read outside a lock and initialized inside one (the double-checked pattern) is declared `volatile`; the accessor reads the field once into a local, checks the local, takes the lock, re-reads and re-checks, assigns the fully constructed object as the last step, and returns the local. For a static field the holder-class idiom — a nested class whose `static final` field the class loader initializes on first use — needs no lock and no `volatile`; for a field that is not performance-critical a `synchronized` accessor is the plain form.

## Rationale
Without `volatile`, the write of the new object's reference to the field may become visible to another thread before the writes the constructor made to the object's fields: the first, unlocked check sees a non-null reference and the caller uses an object whose fields still hold their defaults. The `volatile` write orders the constructor's writes before the reference, and the `volatile` read on the other side acquires them. Reading the field into a local makes the value returned the value that was checked. The holder class is initialized on first access under the class-initialization lock, which the JVM makes safe without further synchronization.

## Example
```java
bad:  private static Registry instance;
      static Registry get() { if (instance == null) { synchronized (Registry.class) {
          if (instance == null) instance = new Registry(); } } return instance; }
good: private static class Holder { static final Registry INSTANCE = new Registry(); }
      static Registry get() { return Holder.INSTANCE; }
```

## Limits
Applies to a field read without a lock and written inside one. A field always accessed under the same lock, a `synchronized` accessor, a `static final` field, and a holder class are correct forms. An object all of whose fields are `final` and whose constructor does not leak `this` keeps its `final` fields intact through a plain-field publication; the `volatile` remains the reviewed form because a later non-final field breaks the exemption silently. A `computeIfAbsent` on a concurrent map, or a memoizing supplier that documents its own synchronization, is out of scope.

## Validator
On the triggered hunk find each `if (field == null)` outside a lock followed by a `synchronized` or `Lock` region that assigns the field. Open the file: check the field's declaration for `volatile`, check that the accessor reads the field into a local before the checks and returns the local, and that the assignment is the last statement of the initialization. Validator question: **is this double-checked field non-volatile, or read more than once outside the lock, or assigned before its object is fully constructed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-13`, severity major, `file`, `symbol`, `code` = the field declaration and the accessor quoted verbatim from the diff, `fix` = `volatile` with the single-read local, or the holder class, `rationale` naming the reference visible before the constructor's writes).

## Source
Error Prone `DoubleCheckedLocking` — "Using double-checked locking on mutable objects in non-volatile fields is not thread-safe"; "the compiler and JVM can re-order code from the object's constructor to occur after the object is written to the field"; its canonical correct form with `volatile` and a local, and the holder-class and synchronized-accessor alternatives. SpotBugs `DC_DOUBLECHECK` — "not correct according to the semantics of the Java memory model" (CWE-609 Double-Checked Locking). SEI CERT LCK10-J "Use a correct form of the double-checked locking idiom".
