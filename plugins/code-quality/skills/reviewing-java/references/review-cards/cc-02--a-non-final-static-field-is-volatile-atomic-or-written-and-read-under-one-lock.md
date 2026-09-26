---
title: A static field that is not final is volatile, an atomic type, or written and read only inside one lock region
rule_id: CC-02
domain: concurrency
triggers: ['static\s+(?!final\b)(?!class\b)(?!interface\b)(?!void\b)(?!synchronized\b)[\w.<>\[\]?, ]+\s+\w+\s*[=;]', 'static volatile', 'static (int|long|boolean|String|Map|List|Set)\s', 'static \w+(<[^>]*>)? \w+;']
scope: file
check_kind: mechanical
severity_default: major
---

# A static field that is not final is volatile, an atomic type, or written and read only inside one lock region

## Thesis
A `static` field that is assigned after class initialization is `volatile`, an atomic type such as `AtomicInteger` or `AtomicReference`, or written and read only inside `synchronized` blocks or `Lock` regions on one lock. A plain mutable `static` is shared by every thread in the JVM and is read and written without a happens-before edge.

## Rationale
A static field has exactly one incarnation no matter how many instances of the class exist, so every thread that touches the class touches the same variable. A write to it from an instance method — a request handler, a task, a listener — is visible to another thread's read only if the write happens-before the read, and a plain field carries no such edge: readers may see a stale value indefinitely, and a compound update such as `++` can be lost between two writers. `volatile` gives each single read and write an edge; an atomic type adds an atomic read-modify-write; a lock region adds mutual exclusion for a compound update.

## Example
```java
bad:  private static int requests;
      void handle(Request r) { requests++; }
good: private static final AtomicInteger requests = new AtomicInteger();
      void handle(Request r) { requests.incrementAndGet(); }
```

## Limits
Applies to a static field written after the class is initialized. A `static final` field, a static assigned once in a static initializer and never again, a static written only from `main` or test set-up before any other thread starts, and a static that holds a thread-safe object (a `ConcurrentHashMap`, an `AtomicLong`, an immutable value) are not flagged. A tolerance stated in the project context — "the counter is a debug statistic; stale reads accepted" — rejects the finding.

## Validator
On the triggered hunk find each `static` field declaration without `final`, and each assignment to a static field. Open the file: check whether the field is `volatile` or of an atomic type, or whether every write and read of it sits inside a `synchronized` or `Lock` region on the same lock. Validator question: **is this static field written after class initialization without volatile, an atomic type, or one lock enclosing every access?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-02`, severity major, `file`, `symbol`, `code` = the static field declaration and the write quoted verbatim from the diff, `fix` = the `volatile` modifier, the atomic type, or the lock region, `rationale` naming the single JVM-wide incarnation of the field and the missing happens-before edge).

## Source
JLS §8.3.1.1 static Fields — "If a field is declared static, there exists exactly one incarnation of the field, no matter how many instances (possibly zero) of the class may eventually be created". `java.util.concurrent` package Javadoc, Java SE 21, "Memory Consistency Properties" — a write is visible to another thread's read only if it happens-before the read. SpotBugs `ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD` — a write to a static field from an instance method; SonarSource RSPEC-2696 "Instance methods should not write to static fields".
