---
title: A retry waits with exponential backoff and random jitter, never a fixed or lockstep delay
rule_id: JAVA-148
domain: errors
step: [handle-errors]
applies_to: [java, service-boundary]
triggers: ['Thread[.]sleep\(', '@Retryable', 'RetryConfig', 'IntervalFunction', 'waitDuration\(', 'for \(int attempt', 'while \(attempt', 'retr(y|ies)', 'BackOff']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A retry waits with exponential backoff and random jitter, never a fixed or lockstep delay

## Thesis
The delay between retry attempts grows with the attempt number and includes a random component — `random(0, min(cap, base * 2^attempt))` or the library's exponential-random interval — so that clients that failed at the same moment do not all retry at the same moment; an immediate retry or a delay computed identically by every client is not a backoff.

## Rationale
When a dependency stalls, every caller that was in flight fails within the same short window. With no delay, all of them retry at once and the dependency receives the whole burst again while still degraded; with a deterministic delay, "backoff without jitter lets independent clients fall into step and produce periodic surges", each surge arriving as one spike. The retries then form a sustaining effect: the extra load keeps the dependency too slow to answer in time, which triggers more retries, and the system can stay degraded after the original trigger has passed. Randomizing the delay spreads the retries over the window so the dependency sees a smoothed load; growing the delay reduces the total number of attempts a long outage attracts. In a repository study of 113 production retry configurations, 31% retried with no delay and exactly one randomized its delay.

## Example
```java
bad:  for (int i = 0; i < 3; i++) {
          try { return call(); } catch (TransientException e) { Thread.sleep(1000L * (1L << i)); }
      }
good: long base = 100, cap = 20_000;
      for (int i = 0; i < 3; i++) {
          try { return call(); } catch (TransientException e) {
              Thread.sleep(ThreadLocalRandom.current().nextLong(0, Math.min(cap, base << i))); }
      }
```

## Limits
Applies to retries against a shared dependency: a network service, a database, a broker. A retry of a local optimistic-lock conflict on one row, or a single immediate re-read after a known race, needs no jitter. A library policy with a randomization factor — `IntervalFunction.ofExponentialRandomBackoff`, `@Retryable(jitter = ..., multiplier = ...)`, Spring's `ExponentialBackOff` with jitter — satisfies the rule; a retry delegated to a service mesh the project context names is out of scope.

## Validator
On the triggered hunk find each retry loop or retry policy and read how the delay is computed: none, a constant, a formula of the attempt number only, or a formula with a random term. Validator question: **do all clients that fail together retry after the same delay, or with no delay?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: JAVA-148`, severity major, `file`, `symbol`, `code` = the retry loop or policy quoted verbatim from the diff, `fix` = a delay drawn at random up to a capped exponential bound, `rationale` naming the synchronized burst the fixed delay produces).
