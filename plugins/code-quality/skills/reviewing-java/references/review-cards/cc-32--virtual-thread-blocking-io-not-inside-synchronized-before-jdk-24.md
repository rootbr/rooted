---
title: On a runtime before JDK 24, a virtual thread performs blocking operations under a ReentrantLock, not inside a synchronized block that pins its carrier
rule_id: CC-32
domain: concurrency
triggers: ['synchronized', 'ofVirtual\(', 'newVirtualThreadPerTaskExecutor\(', 'startVirtualThread\(', 'setVirtualThreads\(']
scope: file
check_kind: semantic
severity_default: major
---

# On a runtime before JDK 24, a virtual thread performs blocking operations under a ReentrantLock, not inside a synchronized block that pins its carrier

## Thesis
In a project that runs on JDK 21, 22 or 23 and executes tasks on virtual threads, a region that performs a blocking operation — socket or file I/O, a JDBC call, `BlockingQueue.take`, `Object.wait` — is guarded by a `ReentrantLock` (or another `java.util.concurrent.locks.Lock`) rather than by `synchronized`; on JDK 24 or later either guard is acceptable.

## Rationale
A virtual thread unmounts from its carrier when it blocks, freeing the carrier for another virtual thread. On JDK 21 through 23 it cannot unmount while it holds a monitor: the continuation is pinned to the carrier — the runtime records a held monitor as one of its three pinning reasons, beside a native frame and a critical section — so a blocking call inside `synchronized` blocks the carrier itself. The carriers are a small set of platform threads; when as many virtual threads as there are carriers block inside `synchronized` regions, every other virtual thread waits for a carrier, including the one that would release the lock they wait on — a deadlock with no cycle in the lock graph. A `ReentrantLock` does not pin: a virtual thread parked on it unmounts. JDK 24 changed the monitor implementation so that a virtual thread holding or waiting for a monitor unmounts too; native methods and foreign-function calls still pin. The `jdk.VirtualThreadPinned` flight-recorder event, enabled by default with a 20 ms threshold, and the `jdk.tracePinnedThreads` property report pinning at run time.

## Example
```java
bad:  synchronized (this) { return socket.read(buf); }             // pins the carrier on JDK 21–23
good: lock.lock();
      try { return socket.read(buf); } finally { lock.unlock(); }
```

## Limits
Applies when the project's runtime is JDK 21–23 and the code runs on virtual threads: a `newVirtualThreadPerTaskExecutor`, `Thread.ofVirtual`, or a framework switch to virtual threads named in the project context. On JDK 24 or later `synchronized` around a blocking call no longer pins, and the finding is rejected. Code that runs on platform threads is unaffected. A `synchronized` region that holds the monitor for in-memory work — a counter, a map update — does not block and pins for no measurable time. A blocking call inside `synchronized` in a third-party library the project cannot change is reported as a note, not as a finding on the diff. A blocking call held under any lock, on any runtime, is a lock-scope concern judged on its own; the claim here is the carrier pinning that turns it into a carrier-exhaustion deadlock on JDK 21–23.

## Validator
On the triggered hunk find each `synchronized` method or block; read its body and the methods it calls in the file for a blocking operation. Establish from the file or the project context that the code runs on virtual threads and that the target JDK is below 24. Validator question: **on this project's JDK 21–23 runtime, does a virtual thread perform a blocking operation while holding a monitor?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-32`, severity major, `file`, `symbol`, `code` = the `synchronized` and the blocking call quoted verbatim from the diff, `fix` = the `ReentrantLock` guard, locked before the `try` and unlocked in `finally`, or the blocking call moved out of the monitor, `rationale` naming the pinned carrier and the carrier-exhaustion deadlock).

## Source
JEP 444 "Virtual Threads" (JDK 21), section "Pinning" — a virtual thread cannot be unmounted during a blocking operation inside a `synchronized` block or method, or during a native method or foreign function; guard long-held or blocking sections with `java.util.concurrent.locks.ReentrantLock` — unfetched. JEP 491 "Synchronize Virtual Threads without Pinning" (JDK 24) — unfetched. JDK 21 source at `jdk-21-ga`: `jdk.internal.vm.Continuation.Pinned` enumerates `NATIVE` ("Native frame on stack"), `MONITOR` ("Monitor held") and `CRITICAL_SECTION`; `jdk.jfr` `default.jfc` enables `jdk.VirtualThreadPinned` with a 20 ms threshold; `java.lang.VirtualThread` reads `jdk.tracePinnedThreads`. `java.lang.Thread` class Javadoc, Java SE 21 — carrier threads are "a small set of platform threads". The Rationale's sentence that carrier exhaustion also starves the virtual thread that would release the awaited lock — a deadlock with no cycle in the lock graph — rests on the unfetched JEP 491; the fetched JDK 21 source shows the pinning by a held monitor, not the deadlock.
