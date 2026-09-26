---
title: A retry waits with exponential backoff and random jitter, never a fixed or lockstep delay
rule_id: REL-17
domain: reliability
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
When the validator answers yes, the finder emits one finding (`rule_id: REL-17`, severity major, `file`, `symbol`, `code` = the retry loop or policy quoted verbatim from the diff, `fix` = a delay drawn at random up to a capped exponential bound, `rationale` naming the synchronized burst the fixed delay produces).

## Source
arXiv:2608.25403 (Retry Amplification in Distributed Systems) §III.D — "Immediate retries concentrate into a spike, exponential backoff spreads that spike over time, and backoff without jitter lets independent clients fall into step and produce periodic surges"; §II — "randomizing the delay prevents clients from synchronizing into retry storms"; §IV.C, Table I — no backoff in 31.0% and verified jitter in 1 of 113 production configurations. arXiv:2510.03551 §1 — retries "may form a sustaining effect: the additional workload from retries prevents the system to respond to requests on time, thereby leading to further client-side retries". arXiv:2512.16959 mini simulation — exponential backoff without jitter: P99 2600 ms and a 17% error rate; backoff with jitter: P99 1400 ms and 6%. Spring Framework reference, "Resilience Features" — `@Retryable(delay, jitter, multiplier, maxDelay)`; Resilience4j `IntervalFunction.ofExponentialRandomBackoff`.
