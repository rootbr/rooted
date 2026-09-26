---
title: A BlockingQueue between a producer and a consumer is constructed with a capacity bound
rule_id: CC-46
domain: concurrency
triggers: ['new LinkedBlockingQueue[<(]', 'new LinkedBlockingDeque[<(]']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A BlockingQueue between a producer and a consumer is constructed with a capacity bound

## Thesis
A queue that decouples a producer from a consumer — a `LinkedBlockingQueue`, `LinkedBlockingDeque` or `ArrayBlockingQueue` — is created with an explicit capacity, so that a producer that outruns the consumer blocks in `put` or sees `false` from `offer` instead of growing the queue without limit.

## Rationale
`new LinkedBlockingQueue<>()` has a capacity of `Integer.MAX_VALUE`: the optional capacity argument is the documented way to prevent excessive queue expansion, and without it the queue accepts every element until the heap is exhausted. A producer faster than its consumer — a burst of requests, a consumer stalled on a slow downstream, a consumer thread that died — then converts the rate mismatch into memory growth that ends in `OutOfMemoryError` for the whole process, usually hours later and far from the queue. A bounded queue converts the same mismatch into back-pressure at the producer: `put` blocks, `offer` returns `false`, and the producer's caller learns of the overload while the process is still healthy.

## Example
```java
bad:  private final BlockingQueue<Event> events = new LinkedBlockingQueue<>();
good: private final BlockingQueue<Event> events = new LinkedBlockingQueue<>(10_000);
      // producer: if (!events.offer(e)) metrics.dropped();   or   events.put(e) to block
```

## Limits
Applies to a queue that receives elements at a rate the consumer does not control. A queue handed to a `ThreadPoolExecutor` constructor is judged by the executor's saturation policy, not here. A queue filled once from a bounded source and drained — a batch of known size — or a queue whose producer is the consumer's own thread cannot grow without limit. The capacity value is the author's number, and it may come from configuration as long as the constructor receives one; the finding is the absence of any bound. A queue that is unbounded by design — `PriorityBlockingQueue`, `DelayQueue`, `LinkedTransferQueue`, `ConcurrentLinkedQueue` — takes no capacity argument and is judged by its producers on its own.

## Validator
On the triggered hunk find each `LinkedBlockingQueue` or `LinkedBlockingDeque` construction, check for a capacity argument, and confirm from the hunk that the queue is not handed to an executor constructor. Validator question: **can this producer–consumer queue grow with the producer's rate because its constructor received no capacity?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-46`, severity major, `file`, `symbol`, `code` = the construction without a capacity quoted verbatim from the diff, `fix` = the same constructor with a capacity and the producer's handling of a blocking `put` or a `false` from `offer`, `rationale` naming the `Integer.MAX_VALUE` default and the heap growth under a slow consumer).

## Source
`java.util.concurrent.LinkedBlockingQueue` class Javadoc, Java SE 21 — "The optional capacity bound constructor argument serves as a way to prevent excessive queue expansion. The capacity, if unspecified, is equal to Integer.MAX_VALUE"; `java.util.concurrent.PriorityBlockingQueue` — "An unbounded blocking queue ... While this queue is logically unbounded, attempted additions may fail due to resource exhaustion (causing OutOfMemoryError)"; `java.util.concurrent.BlockingQueue#offer` — "false if no space is currently available".
