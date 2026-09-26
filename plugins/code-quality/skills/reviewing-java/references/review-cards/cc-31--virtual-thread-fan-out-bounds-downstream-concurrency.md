---
title: A fan-out on virtual threads bounds its concurrent calls on a downstream with a Semaphore, because the per-task executor itself is unbounded
rule_id: CC-31
domain: concurrency
triggers: ['newVirtualThreadPerTaskExecutor\(', 'ofVirtual\(', 'startVirtualThread\(', 'newThreadPerTaskExecutor\(', 'new Semaphore\(', 'StructuredTaskScope']
scope: file
check_kind: semantic
severity_default: major
---

# A fan-out on virtual threads bounds its concurrent calls on a downstream with a Semaphore, because the per-task executor itself is unbounded

## Thesis
When a loop, a stream or a scope submits one virtual thread per element and each element calls a resource of finite capacity — a database, an HTTP peer, a connection pool, the common fork-join pool — the calls to that resource pass through a `Semaphore` sized to what the resource sustains, or through a client whose own pool bounds them; the number of in-flight calls is then a stated number, not the number of elements.

## Rationale
The virtual-thread-per-task executor creates as many threads as tasks it receives — it is documented as unbounded — and a virtual thread is cheap enough that ten thousand of them start in the time a platform pool would have queued them. The downstream is not: a database serves a connection pool of tens, an HTTP peer a few hundred sockets, and each call beyond that waits in the driver, times out, or is rejected, while the peer sees a burst a platform pool of fifty threads never produced. With platform threads the pool size was the accidental limit; on virtual threads the limit is gone and has to be written down. A `Semaphore` restricts the number of threads that access a resource to its permit count; acquiring before the call and releasing in `finally` makes the concurrency on that resource explicit and independent of how many tasks exist.

## Example
```java
bad:  try (ExecutorService ex = Executors.newVirtualThreadPerTaskExecutor()) {
          for (Id id : ids) ex.submit(() -> repo.load(id));           // 100k tasks against 20 connections
      }
good: Semaphore db = new Semaphore(20);
      for (Id id : ids) ex.submit(() -> { db.acquire(); try { return repo.load(id); } finally { db.release(); } });
```

## Limits
Applies when the number of submitted tasks is data-driven (a collection, a stream, a message batch) and each task calls a shared resource. A fixed small fan-out (three parallel lookups per request) is bounded by construction. A client that bounds its own concurrency — a connection pool that blocks on borrow, an HTTP client with a maximum-connections setting shown in the file or named in the project context — supplies the bound. The permit count is the author's number; the finding is the absence of any bound. A fan-out whose downstream is a remote dependency is a bulkhead question judged on its own.

## Validator
On the triggered hunk find the loop, stream or scope that submits per element to a virtual-thread executor. Open the file to identify what each task calls and whether that call is bounded: a `Semaphore` acquired around it, a pool with a documented maximum, a rate limiter. Validator question: **can the number of concurrent calls to one finite downstream grow with the input size, with nothing in the code bounding it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-31`, severity major, `file`, `symbol`, `code` = the submission loop and the downstream call quoted verbatim from the diff, `fix` = a `Semaphore` or bounded client around the call, acquired before and released in `finally`, `rationale` naming the unbounded executor and the downstream's capacity).

## Source
`java.util.concurrent.Executors#newVirtualThreadPerTaskExecutor` Javadoc, Java SE 21 — "The number of threads created by the Executor is unbounded"; `java.util.concurrent.Semaphore` class Javadoc — "Semaphores are often used to restrict the number of threads than can access some (physical or logical) resource", with the bounded-pool example. JEP 444 "Virtual Threads", section "Do not pool virtual threads" — a semaphore to limit concurrent access to a limited resource; unfetched.
