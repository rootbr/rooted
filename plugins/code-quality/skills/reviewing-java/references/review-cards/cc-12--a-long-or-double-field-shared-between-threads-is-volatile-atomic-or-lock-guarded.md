---
title: A long or double field shared between threads is volatile, an AtomicLong, or accessed only under one lock
rule_id: CC-12
domain: concurrency
triggers: ['\blong\s+\w+\s*[=;]', '\bdouble\s+\w+\s*[=;]', 'volatile (long|double)', 'AtomicLong', '(long|double)\[\]']
scope: file
check_kind: mechanical
severity_default: major
---

# A long or double field shared between threads is volatile, an AtomicLong, or accessed only under one lock

## Thesis
A `long` or `double` field that one thread writes and another reads is declared `volatile`, replaced by an `AtomicLong` (a `double` through `doubleToLongBits`, or a `DoubleAdder` for sums), or read and written only inside one lock region. A plain `long` or `double` may be read half-written.

## Rationale
The language permits a write to a non-volatile `long` or `double` to be performed as two separate 32-bit writes, and a read that runs between them returns a value that was never written: a stress test in which one thread writes `0xFFFFFFFF_FFFFFFFFL` to a plain `long` while another reads it observes `-4294967296` and `4294967295` on a 32-bit x86 VM, values neither the writer nor the initial state ever held; the same test on a `volatile long` forbids them and observes none. Reads and writes of `int`, `boolean`, references and the other primitives happen in full even under a race, which is why the two 64-bit types are the exception a reviewer has to know. `volatile` restores single-access atomicity and adds the happens-before edge; it does not make `+=` or `++` atomic, which is what `AtomicLong` is for.

## Example
```java
bad:  private long lastSeen;
      void touch(long now) { lastSeen = now; }      // writer thread
      long lastSeen() { return lastSeen; }          // reader thread may see a torn value
good: private volatile long lastSeen;               // touch() and lastSeen() unchanged
```

## Limits
Applies to a field of type `long` or `double`, or an element of a `long[]` or `double[]`, that is written by one thread and read by another. A local, a field of a thread-confined object, a field written once before publication, and a field whose every access sits inside one lock region are not flagged. A project context that states the deployment runs 64-bit JVMs only, and accepts that a single-step access there is the behavior of those JVMs rather than a guarantee of the language, may record that as a tolerance for the tearing; the field still needs the happens-before edge for visibility, so the finding stands on that ground unless the context covers it too.

## Validator
On the triggered hunk find each `long` or `double` field declaration and each write to one. Open the file: confirm the field is reachable from more than one thread and check for `volatile`, an atomic type, or one lock enclosing every read and write. Validator question: **is this 64-bit field written by one thread and read by another without volatile, an atomic type, or one lock around every access?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-12`, severity major, `file`, `symbol`, `code` = the field declaration and the write quoted verbatim from the diff, `fix` = the `volatile` modifier, the `AtomicLong`, or the lock region, `rationale` naming the torn read the language permits and the visibility edge the fix adds).

## Source
JLS §17.7 "Non-atomic Treatment of double and long" — a single write to a non-volatile `long` or `double` may be treated as two separate 32-bit writes; writes and reads of `volatile` `long` and `double` values are always atomic. jcstress sample `jmm/basic/BasicJMM_02_AccessAtomicity.java` — `Longs`: torn values `-4294967296` (0.08%) and `4294967295` observed on x86_32; `VolatileLongs`: other outcomes forbidden, none observed; `Integers`: tearing forbidden for `int`.
