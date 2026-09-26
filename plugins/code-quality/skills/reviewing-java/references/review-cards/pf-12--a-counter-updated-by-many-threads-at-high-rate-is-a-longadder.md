---
title: A statistics counter that many threads update at high rate is a LongAdder, not an AtomicLong or a compareAndSet loop
rule_id: PF-12
domain: performance
triggers: ['AtomicLong', 'AtomicInteger', 'incrementAndGet\(', 'getAndIncrement\(', 'addAndGet\(', 'getAndAdd\(', 'compareAndSet\(']
scope: file
check_kind: semantic
severity_default: minor
---

# A statistics counter that many threads update at high rate is a LongAdder, not an AtomicLong or a compareAndSet loop

## Thesis
A counter or sum that several threads increment on every request, message or event, and that is read only occasionally — metrics, statistics, throttling estimates — is a `LongAdder` (or a `LongAccumulator`); an `AtomicLong` with `incrementAndGet`, or a hand-written `get`/`compareAndSet` loop, is kept only where the exact value is needed at each update, as in a sequence generator or an admission decision.

## Rationale
An `AtomicLong` is one memory word; every update from every thread is a read-modify-write on the same cache line, so under contention the updates serialize on that line and each `compareAndSet` may fail and retry when another thread got there first. A `LongAdder` keeps a set of per-thread cells and sums them on read: under low contention it behaves like an `AtomicLong`, and under high contention its expected throughput is significantly higher, at the cost of more space and of a `sum()` that is a snapshot rather than an atomic read. A statistics counter tolerates that snapshot.

## Example
```java
bad:  private final AtomicLong requests = new AtomicLong();
      void onRequest() { requests.incrementAndGet(); }
good: private final LongAdder requests = new LongAdder();
      void onRequest() { requests.increment(); }
      long snapshot() { return requests.sum(); }
```

## Limits
A counter whose new value is used at the update site — an id generator, a permit count that gates admission, a compare-and-set that publishes state — needs an atomic, because `LongAdder.sum()` is not an atomic snapshot under concurrent updates. A counter updated by one thread, or rarely, gains nothing. A tolerance in the project context — "this metric is off the hot path" — rejects the finding. Whether the update is atomic at all is a separate, higher-priority concern.

## Validator
On the triggered hunk find each `AtomicLong`/`AtomicInteger` update or compare-and-set loop. Open the file: confirm the field is updated from a per-request or per-event path reachable by many threads, and that the return value of the update is discarded (nothing uses the incremented value at the update site). Validator question: **is this a many-thread, high-rate counter whose updated value nobody reads at the update site?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-12`, severity minor, `file`, `symbol`, `code` = the field and the update quoted verbatim from the diff, `fix` = `LongAdder` with `increment()` or `add()` and `sum()`, `rationale` naming the single contended word and the retry loop).

## Source
`java.util.concurrent.atomic.LongAdder` class Javadoc, Java SE 21 — "This class is usually preferable to AtomicLong when multiple threads update a common sum that is used for purposes such as collecting statistics, not for fine-grained synchronization control. Under low update contention, the two classes have similar characteristics. But under high contention, expected throughput of this class is significantly higher, at the expense of higher space consumption"; `#sum` — "The returned value is NOT an atomic snapshot; invocation in the absence of concurrent updates returns an accurate result, but concurrent updates that occur while the sum is being calculated might not be incorporated."
