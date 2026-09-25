---
title: Calls to each remote dependency run under a concurrency limit dedicated to that dependency, so one slow downstream cannot take every thread
rule_id: REL-49
domain: reliability
triggers: ['Bulkhead[.]of', '@Bulkhead', 'ThreadPoolBulkhead', 'new Semaphore\(', 'Executors[.]newFixedThreadPool\(', '@Async', 'CompletableFuture[.]supplyAsync\(', 'RestTemplate', 'RestClient', 'WebClient', 'FeignClient']
scope: file
check_kind: semantic
severity_default: minor
---

# Calls to each remote dependency run under a concurrency limit dedicated to that dependency, so one slow downstream cannot take every thread

## Thesis
Calls out to a remote dependency are bounded in number by a bulkhead — a `Semaphore`, a Resilience4j `Bulkhead`, a dedicated thread pool — that belongs to that dependency alone, so that when it slows down at most that many caller threads or connections wait on it; two dependencies do not share one limit, and no dependency's calls run unbounded on the request-thread pool or the common `ForkJoinPool`.

## Rationale
When a dependency stalls, every call in flight to it holds a thread until its timeout; with no limit, a burst of requests that all touch the slow dependency occupies the whole request pool, and requests that do not need that dependency at all queue behind them — the caller is down because one of its many dependencies is slow. A bulkhead is "an entity limiting the amount of parallel operations" that "can be used to shed load, and, where it makes sense, limit resource use"; when it is full, "no additional operations will be permitted to execute until space is available", so the excess fails fast and the rest of the pool keeps serving. The limit must be per dependency: a shared bulkhead lets the slow dependency consume the permits the healthy one needed, which is the failure the pattern exists to isolate.

## Example
```java
bad:  Payment p = paymentClient.charge(req);                     // unbounded on the request pool
      Bulkhead shared = Bulkhead.ofDefaults("shared");           // one limit for payments and inventory
good: Bulkhead paymentBulkhead = Bulkhead.ofDefaults("paymentService");
      Payment p = paymentBulkhead.executeSupplier(() -> paymentClient.charge(req));
```

## Limits
Applies to synchronous calls that can stall. A client whose own connection pool per host is bounded and small (an HTTP client with `maxConnectionsPerRoute`) already limits concurrency to that host; the project context naming it rejects the finding. A limit enforced by a mesh or gateway the project context names is out of scope. Fire-and-forget calls on a bounded dedicated executor are correct.

## Validator
On the triggered hunk find each remote call and each bulkhead or pool definition. Open the file, and the client's configuration when it is in the file, else the project context: is the call bounded by a per-dependency semaphore, bulkhead, dedicated pool or per-host connection limit, or does it run on the shared request or common pool? Check that a bulkhead instance is not shared across dependencies. Validator question: **can a stall in this one dependency occupy threads that other requests need, because nothing bounds the concurrent calls to it alone?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-49`, severity minor, `file`, `symbol`, `code` = the remote call or the shared limit quoted verbatim from the diff, `fix` = a per-dependency bulkhead or pool around the call, `rationale` naming the request pool the stall would drain).

## Source
Resilience4j `io.github.resilience4j.bulkhead.Bulkhead` Javadoc — "A Bulkhead represent an entity limiting the amount of parallel operations ... can be used to shed load, and, where it makes sense, limit resource use (i.e. limit amount of threads/actors involved in a particular flow, etc). ... If the bulkhead is full, no additional operations will be permitted to execute until space is available"; Resilience4j README — "The Golden Rule: Create a unique instance (with a unique ID) for each protected remote service or backend you communicate with"; "Separate Bulkhead for each service ... DON'T" share one. arXiv:2512.16959 §VI.E — "Bulkheads isolate failure domains with separate pools/quotas to prevent cross-service collapse"; Table I — "Resource Exhaustion: CPU/memory leaks, thread starvation".
