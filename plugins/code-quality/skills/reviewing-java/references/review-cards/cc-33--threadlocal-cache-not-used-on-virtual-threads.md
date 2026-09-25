---
title: A ThreadLocal that caches a per-thread object is not used on virtual threads, where each of many short-lived threads would hold its own copy
rule_id: CC-33
domain: concurrency
triggers: ['ThreadLocal[.]withInitial\(', 'ThreadLocal<', 'ofVirtual\(', 'newVirtualThreadPerTaskExecutor\(']
scope: file
check_kind: semantic
severity_default: minor
---

# A ThreadLocal that caches a per-thread object is not used on virtual threads, where each of many short-lived threads would hold its own copy

## Thesis
A `ThreadLocal` whose purpose is to reuse an expensive object per thread — a `SimpleDateFormat`, a buffer, a parser, a `MessageDigest` — is not introduced or kept in code that runs on virtual threads; the object is shared when it is immutable (`DateTimeFormatter`), created per task when it is cheap, or borrowed from a bounded pool when it is neither.

## Rationale
A thread-local value lives as long as its thread: on a pool of ten platform threads the cache holds ten copies and amortizes well. A virtual thread is created per task and a JVM may run millions of them, so the same cache creates one copy per task — allocated on first use, never reused because the thread ends with the task, and retained until then. Heap use scales with the number of concurrent tasks instead of the number of carriers, and the cache saves nothing. A thread-local's lifetime is unbounded: it keeps its value after the method that set it completes unless explicitly removed, which on a short-lived thread means until the thread ends.

## Example
```java
bad:  static final ThreadLocal<SimpleDateFormat> FMT = ThreadLocal.withInitial(() -> new SimpleDateFormat("yyyy-MM-dd"));
      // on a virtual thread per request: FMT.get().format(d) allocates one formatter per request
good: static final DateTimeFormatter FMT = DateTimeFormatter.ISO_LOCAL_DATE;      // immutable, shared
```

## Limits
Applies to a `ThreadLocal` used as a per-thread cache in code that runs on virtual threads, which the file or the project context shows. Code on a bounded platform pool keeps the idiom. A `ThreadLocal` that carries request context rather than a cache is a context-propagation matter, not this finding. A library's own internal `ThreadLocal` the project cannot change is out of scope.

## Validator
On the triggered hunk find each `ThreadLocal` declaration or `withInitial`. Read what it holds and how it is used: a reusable object created in the initializer and read repeatedly is a cache. Confirm from the file or the project context that the code runs on virtual threads. Validator question: **does this thread-local cache an object per thread in code that runs one virtual thread per task?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-33`, severity minor, `file`, `symbol`, `code` = the `ThreadLocal` declaration quoted verbatim from the diff, `fix` = a shared immutable object, a per-task instance, or a bounded pool, `rationale` naming one copy per virtual thread and the retained heap).

## Source
`java.lang.Thread` class Javadoc, Java SE 21, section "Virtual threads" — "a single Java virtual machine may support millions of virtual threads"; `java.lang.ThreadLocal` class Javadoc — "each thread that accesses one (via its get or set method) has its own, independently initialized copy of the variable", and "Each thread holds an implicit reference to its copy of a thread-local variable as long as the thread is alive"; `java.lang.ScopedValue` Javadoc, Java SE 21 (preview API) — "A ThreadLocal has an unbounded lifetime and thus continues to have a value after a method completes, unless explicitly removed". JEP 444 "Virtual Threads", section "Thread-local variables" — a thread-local used to cache expensive objects, one copy per thread, does not pay off with millions of virtual threads; unfetched.
