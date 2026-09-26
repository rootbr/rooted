---
title: A retry fires only on a transient failure — a timeout, a connection reset, or a status such as 503, 502, 504, 429 or 408 — never on a 4xx client error or a permanent exception
rule_id: REL-50
domain: reliability
triggers: ['@Retryable', 'RetryConfig', 'retryExceptions\(', 'retryOnException\(', 'retryOnResult\(', 'catch \(Exception ', 'catch \(Throwable ', 'catch \(RuntimeException ', 'retr(y|ies)', 'ignoreExceptions\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A retry fires only on a transient failure — a timeout, a connection reset, or a status such as 503, 502, 504, 429 or 408 — never on a 4xx client error or a permanent exception

## Thesis
A retry loop or policy names the failures it retries: connect and read timeouts, connection resets, a status that names a passing condition — such as `503 Service Unavailable`, `502 Bad Gateway`, `504 Gateway Timeout`, `429 Too Many Requests` or `408 Request Timeout` — and the exception types that mean "try again"; it does not retry on `catch (Exception e)`, on a `400`, `401`, `403`, `404`, `409` or `422`, or on an exception that means the input or the state is wrong.

## Rationale
A 4xx status "indicates that the client seems to have erred": the same request will fail the same way, so each retry costs a round trip, delays the failure the caller must report, and — under an outage where a proxy returns 4xx for unrelated reasons — adds load to a struggling system for nothing. A `503` is "a temporary overload or scheduled maintenance, which will likely be alleviated after some delay", a `502` or `504` reports a gateway that "received an invalid response" or "did not receive a timely response" from the server behind it, a `408` says the server "did not receive a complete request message within the time that it was prepared to wait" and the client "MAY repeat that request", and a `429` asks the client to wait, so those are the responses worth a retry, after the delay `Retry-After` names. A catch-all retry also repeats `IllegalArgumentException`, a serialization failure, an authorization failure — none of which a second attempt cures — and hides the real error behind "retries exhausted".

## Example
```java
bad:  for (int i = 0; i < 3; i++) { try { return call(); } catch (Exception e) { backoff(i); } }
good: RetryConfig cfg = RetryConfig.custom()
          .retryExceptions(SocketTimeoutException.class, ConnectException.class, HttpServerErrorException.ServiceUnavailable.class)
          .ignoreExceptions(HttpClientErrorException.class).build();
```

## Limits
`408 Request Timeout` and `429`, and a `409` on an idempotent upsert that the project documents as retryable, may be retried. A retry predicate defined once in a shared configuration the project context names covers the policies that reference it. A retry of a local optimistic-lock conflict (`OptimisticLockException`) is a different, correct pattern.

## Validator
On the triggered hunk find each retry loop or policy and read what it retries on: the caught type in a loop, `retryExceptions`/`retryOnException`/`retryOnResult`/`ignoreExceptions` in a policy, `includes`/`excludes` on `@Retryable`. Validator question: **does this policy retry a failure that the same request will produce again — a 4xx other than 408/429, or a permanent exception?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-50`, severity minor, `file`, `symbol`, `code` = the retry predicate or catch clause quoted verbatim from the diff, `fix` = a predicate limited to timeouts, connection failures and passing statuses such as 503, 502, 504, 429 and 408, `rationale` naming the permanent failure the policy repeats).

## Source
RFC 9110 "HTTP Semantics" §15.5 — the 4xx class "indicates that the client seems to have erred"; §15.5.9 — 408 "indicates that the server did not receive a complete request message within the time that it was prepared to wait. If the client has an outstanding request in transit, it MAY repeat that request"; §15.6.3 — 502 "received an invalid response from an inbound server it accessed while attempting to fulfill the request"; §15.6.4 — 503 "indicates that the server is currently unable to handle the request due to a temporary overload or scheduled maintenance, which will likely be alleviated after some delay"; §15.6.5 — 504 "did not receive a timely response from an upstream server it needed to access in order to complete the request" (fetched from the httpwg source `draft-ietf-httpbis-semantics-latest.xml`). RFC 6585 §4 — 429 Too Many Requests (unfetched). arXiv:2608.25403 §III.A — a retry policy is "a predicate c determining which failures are retried at all"; §VII.C — retries that "could not have succeeded" consumed capacity that "yielded nothing". Resilience4j `RetryConfig` — `retryExceptions`, `ignoreExceptions`, `retryOnException`; Spring Framework reference, "Resilience Features" — `@Retryable(includes, excludes)`.
