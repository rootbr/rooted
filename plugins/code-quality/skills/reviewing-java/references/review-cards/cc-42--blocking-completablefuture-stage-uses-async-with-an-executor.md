---
title: A CompletableFuture stage that blocks or needs a particular execution context uses the Async overload with an explicit executor
rule_id: CC-42
domain: concurrency
triggers: ['then(Apply|Accept|Compose|Run|Combine)(Async)?\(', 'whenComplete(Async)?\(', '[.]handle(Async)?\(', 'supplyAsync\(', 'runAsync\(', 'exceptionally\(']
scope: file
check_kind: semantic
severity_default: major
---

# A CompletableFuture stage that blocks or needs a particular execution context uses the Async overload with an explicit executor

## Thesis
A dependent stage whose function performs blocking work — a database or HTTP call, a file read, a lock wait, a `join` on another future — or that must run on a specific kind of thread is attached with `thenApplyAsync`, `thenComposeAsync`, `thenAcceptAsync`, `supplyAsync` and their kin, passing an executor the module owns; the non-async variant is reserved for short in-memory transformations, and the single-argument async variant, which runs on the common pool, for CPU-bound ones.

## Rationale
A non-async stage runs on whichever thread completes the previous stage — a network library's I/O thread, a database driver's callback thread, a timer thread — or, if that stage was already complete when the dependent was attached, on the thread attaching it. The choice is made at run time and differs from call to call, so a blocking function placed there blocks an I/O event loop on some executions and the caller on others; an event loop with one thread then stalls every connection it serves, and a lock held by the completing thread is held across the stage. The async variants without an executor run on the common fork-join pool, which does not compensate for blocked I/O and is shared by every parallel stream in the JVM. An explicit executor — a virtual-thread-per-task executor for blocking work, a bounded pool the module names — makes the thread that runs the stage a stated decision.

## Example
```java
bad:  client.fetchAsync(id).thenApply(r -> repo.save(r));                // JDBC on the client's I/O thread
      client.fetchAsync(id).thenApplyAsync(r -> repo.save(r));           // JDBC on the common pool
good: client.fetchAsync(id).thenApplyAsync(r -> repo.save(r), dbExecutor);
```

## Limits
Applies to a stage whose function blocks or needs a particular thread. A stage that transforms the value in memory — maps a DTO, logs, completes another future — runs correctly on any thread and takes the non-async form. A CPU-bound stage on the common pool is that pool's intended use. A chain whose every future is created and completed on the caller's own thread, as in a synchronous test, has no cross-thread issue. Where the project context names a default executor installed through `defaultExecutor()` on a `CompletableFuture` subclass, the single-argument async variant uses it.

## Validator
On the triggered hunk find each stage function; read it and the methods it calls in the file for a blocking call or a thread requirement. For a non-async stage, open the file to see what completes the previous future: a client callback, an executor, the same thread. For an async stage, check the executor argument. Validator question: **does this stage block or need a specific thread, while its executor is unstated — the completing thread or the common pool?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-42`, severity major, `file`, `symbol`, `code` = the stage call and its blocking body quoted verbatim from the diff, `fix` = the `*Async` overload with the module's executor, `rationale` naming the completing thread or common pool it would otherwise run on).

## Source
`java.util.concurrent.CompletableFuture` class Javadoc, Java SE 21 — "Actions supplied for dependent completions of non-async methods may be performed by the thread that completes the current CompletableFuture, or by any other caller of a completion method"; "All async methods without an explicit Executor argument are performed using the ForkJoinPool.commonPool() (unless it does not support a parallelism level of at least two, in which case, a new Thread is created to run each task)"; `java.util.concurrent.ForkJoinPool` class Javadoc — "no such adjustments are guaranteed in the face of blocked I/O or other unmanaged synchronization".
