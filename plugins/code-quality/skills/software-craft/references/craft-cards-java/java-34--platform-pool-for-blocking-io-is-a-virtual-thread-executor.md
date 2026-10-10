---
title: On JDK 21 or later, a new pool of platform threads that serve blocking I/O is a candidate for a virtual-thread-per-task executor unless a reason to keep platform threads is stated
rule_id: JAVA-34
domain: concurrency
step: [design, implement]
applies_to: [java]
triggers: ['newFixedThreadPool\(', 'newCachedThreadPool\(', 'new ThreadPoolExecutor\(', 'newWorkStealingPool\(', 'ThreadPoolTaskExecutor', 'newScheduledThreadPool\(']
scope: file
check_kind: semantic
severity_default: suggestion
---

# On JDK 21 or later, a new pool of platform threads that serve blocking I/O is a candidate for a virtual-thread-per-task executor unless a reason to keep platform threads is stated

## Thesis
In a project on JDK 21 or later, a diff that introduces a fixed or cached pool of platform threads whose tasks spend their time blocked — HTTP calls, JDBC, message consumption, file I/O — is a candidate for `Executors.newVirtualThreadPerTaskExecutor()`, with a `Semaphore` where a downstream must be bounded, unless a reason to keep platform threads is stated.

## Rationale
A platform thread idle in a blocking call still holds its stack and costs a context switch on every wake-up, and the pool's size is the ceiling on concurrent I/O: at 200 threads, the 201st task waits in the queue while all 200 are parked on sockets. A virtual thread is the intended vehicle for tasks that spend most of their time blocked: it unmounts from its carrier while blocked, requires few resources, and a JVM supports millions of them, so throughput on I/O-bound work scales with the number of open connections rather than with a thread count chosen at deploy time. The sizing question — how many threads for this I/O — disappears together with its tuning; the remaining question, how many concurrent calls the downstream sustains, is answered by a `Semaphore` around the call. A platform pool remains right for CPU-bound work and for code that pins carriers on the project's JDK.

## Example
```java
bad:  ExecutorService io = Executors.newFixedThreadPool(200);
      for (Req r : reqs) io.submit(() -> client.send(r));
good: try (ExecutorService io = Executors.newVirtualThreadPerTaskExecutor()) {
          for (Req r : reqs) io.submit(() -> client.send(r));
      }
```

## Limits
Applies to a pool introduced or resized by the diff, in a project whose runtime is JDK 21 or later, whose tasks block. A project below JDK 21 keeps the platform pool. A pool for CPU-bound tasks, a pool that must be bounded because the tasks pin (native calls; `synchronized` around I/O on JDK 21–23), a scheduler's small pool of timer threads, and a pool the project context names as deliberately platform-based are not flagged. An existing pool merely touched by the diff is not reworked on this finding.

## Validator
On the triggered hunk find the pool creation and, in the file, what its tasks do: client calls, repository calls, stream reads and queue takes mark them I/O-bound. Confirm the project's JDK from the project context or the build shown in the diff. Validator question: **does the diff introduce a platform-thread pool for tasks that spend most of their time blocked, on a JDK 21 or later runtime, with no stated reason to keep platform threads?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-34`, severity suggestion, `file`, `symbol`, `code` = the pool creation quoted verbatim from the diff, `fix` = `newVirtualThreadPerTaskExecutor()` plus a `Semaphore` where a downstream needs a bound, `rationale` naming the thread-count ceiling on concurrent I/O).
