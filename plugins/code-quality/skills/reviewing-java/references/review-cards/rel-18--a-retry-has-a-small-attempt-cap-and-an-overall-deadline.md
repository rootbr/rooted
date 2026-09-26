---
title: A retry stops after a small fixed number of attempts and within one overall deadline that covers every attempt
rule_id: REL-18
domain: reliability
triggers: ['while \(true\)', 'while \(!done\)', 'maxAttempts\(', 'maxRetries', '@Retryable', 'RetryConfig', 'for \(int attempt', 'retr(y|ies)', 'TimeLimiter']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A retry stops after a small fixed number of attempts and within one overall deadline that covers every attempt

## Thesis
A retry loop or policy names its maximum attempt count — three or four total attempts (the library defaults) is the common bound — and the caller's timeout or deadline spans the whole retried operation, so that the worst case is bounded by one number the code states; the attempt count does not grow with the failure rate, and retry layers are not stacked: a client-library retry inside an application retry multiplies the attempts across the layers.

## Rationale
Each extra attempt against a failing dependency adds its full load and its full timeout: with failure probability p and n retries a tier offers (1 − p^(n+1)) / (1 − p) times its base load, and the factor compounds across tiers, so three tiers retrying three times at a 50% failure rate can bound at 6.6× the normal traffic. An unbounded loop turns one outage into a permanent load source and a stuck caller; a cap of three attempts is what the major vendors advise, and the retry libraries default to three or four. The same product applies to retry layers inside one caller as to tiers of a call chain: a client library that retries three times, wrapped in an application retry of three, offers up to nine attempts. A per-attempt timeout alone does not bound the operation — three attempts of ten seconds are thirty — so the deadline the caller promises must enclose the retries. A policy whose cap rises under stress moves in the wrong direction.

## Example
```java
bad:  while (true) {
          try { return call(); } catch (TransientException e) { backoff(); }
      }
good: for (int attempt = 1; attempt <= 3; attempt++) {
          if (System.nanoTime() - start >= budgetNanos) throw new TimeoutException("retries exhausted");
          try { return call(); } catch (TransientException e) { backoff(attempt); }
      }
```

## Limits
A library policy with `maxAttempts` (Resilience4j, default 3) or `maxRetries` (Spring `@Retryable`, default 3) satisfies the count; a `TimeLimiter` or the caller's request timeout enclosing the decorated call satisfies the deadline. A retry budget enforced by a service mesh the project context names covers the cap. A polling loop that waits for a state change with a bounded wait and no repeated request to a failing dependency is not a retry.

## Validator
On the triggered hunk find each retry loop or policy. Check for an attempt bound, that the bound is a constant (not derived from the observed failure rate), and that a deadline or timeout encloses all attempts rather than one. Validator question: **can this operation keep retrying past a fixed small count, or past the deadline its caller expects?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-18`, severity major, `file`, `symbol`, `code` = the loop or policy quoted verbatim from the diff, `fix` = a constant attempt cap and an overall deadline check, `rationale` naming the load multiplication and the unbounded worst case).

## Source
arXiv:2608.25403 §III.B–C — RAF = (1 − p^(n+1)) / (1 − p) per tier; down a chain of tiers that each retry "the amplification compounds" to the product of the per-tier factors, (1.875)^3 ≈ 6.59 for three tiers at p = 0.5, n = 3 (the card reads a retry layer inside one caller as such a tier); §VIII.A — "Capping attempts at three pulls back the 43.8% that currently exceed five, which is what the major vendors advise". RFC 9110 §9.2.2 — "A client SHOULD NOT automatically retry a failed automatic retry" (fetched from the httpwg source of the document); caveat: the RFC allows an HTTP client one automatic retry, and the three-attempt bound is the vendors' and the libraries' (§VIII.A, `DEFAULT_MAX_ATTEMPTS`). Resilience4j `RetryConfig.DEFAULT_MAX_ATTEMPTS = 3`; Spring Framework reference, "Resilience Features" — `@Retryable` defaults to `maxRetries = 3`, "total attempts = 1 initial attempt + maxRetries attempts".
