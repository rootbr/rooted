---
title: A call to a remote dependency runs behind a circuit breaker that fails fast while the dependency is down
rule_id: REL-16
domain: reliability
triggers: ['(?i)restTemplate|restClient|webClient', 'HttpClient', 'httpClient[.]send\(', 'getForObject\(', 'getForEntity\(', '[.]exchange\(', '[.]retrieve\(\)', 'newCall\(', 'ManagedChannel', 'FeignClient', '@CircuitBreaker', 'CircuitBreaker[.]of', 'Retry[.]of', '@Retryable']
scope: file
check_kind: semantic
severity_default: minor
---

# A call to a remote dependency runs behind a circuit breaker that fails fast while the dependency is down

## Thesis
A synchronous call out of the process — HTTP, gRPC, a message broker, a remote cache — is decorated with a circuit breaker (`@CircuitBreaker`, `CircuitBreaker.decorateSupplier`, a Spring Cloud `CircuitBreakerFactory`, or the project's equivalent), one instance per dependency, so that after the dependency's failure rate crosses the threshold further calls are rejected at once instead of each waiting for its own timeout.

## Rationale
When a dependency is down, every call to it still costs the caller a thread, a connection and a full timeout before failing, and retries multiply that cost; the caller's own capacity is spent on requests that cannot succeed, and its callers degrade in turn. A circuit breaker counts the outcomes of the calls it decorates; when the failure rate reaches the configured threshold it opens and "all access to the backend is rejected for a (configurable) time duration", then admits a limited number of probe calls in the half-open state and closes when they succeed. The rejection is immediate and cheap, so the caller stays responsive and the dependency is spared load while it recovers. In a simulated five-tier chain under correlated failure, plain retries reduced the success rate from 55.4% to 41.5% and amplified load by 1.34×, while retries behind a breaker held amplification at 1.00× and the success rate at the no-retry baseline.

## Example
```java
bad:  Quote q = restClient.get().uri("/quote/{id}", id).retrieve().body(Quote.class);
good: CircuitBreaker cb = registry.circuitBreaker("quoteService");
      Quote q = cb.executeSupplier(() ->
          restClient.get().uri("/quote/{id}", id).retrieve().body(Quote.class));
```

## Limits
Applies to calls that leave the process to a dependency that can fail independently. A call to the application's own database through the connection pool, a local cache, or a call inside a batch job whose failure stops the job are out of scope. A breaker applied centrally — a Feign or gateway configuration, a service mesh policy, or a decorated client bean the project context names — covers every call through that client; open the client's definition before flagging a use. A breaker shared across unrelated dependencies is a separate concern and not this finding.

## Validator
On the triggered hunk find each remote call. Open the file and the client's definition: check for a `@CircuitBreaker` annotation on the calling method, a `CircuitBreaker` decoration around the call, a breaker configured on the client bean or in a mesh or gateway the project context names. Validator question: **does this remote call reach the dependency unconditionally, with nothing that stops calling it while it is failing?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-16`, severity minor, `file`, `symbol`, `code` = the remote call quoted verbatim from the diff, `fix` = the call decorated with a per-dependency circuit breaker, `rationale` naming the timeout cost each call pays while the dependency is down).

## Source
arXiv:2512.16959 (systematic review of microservice recovery patterns) §VI.B — "Circuit breakers protect services from cascading failures by tripping after repeated errors and later probing recovery in a half-open state"; mini simulation — bounded retries with a circuit breaker gave a 3% error rate against 6% for jittered backoff and 17% for backoff without jitter. arXiv:2608.25403 §VII — the circuit-breaker strategy held the retry amplification factor at 1.00 and the success rate within a point of no retries, where standard retry fell to 41.5%. Resilience4j `io.github.resilience4j.circuitbreaker.CircuitBreaker` Javadoc — the state changes from CLOSED to OPEN "when the failure rate is greater than or equal to a (configurable) threshold. Then, all access to the backend is rejected for a (configurable) time duration"; README "The Golden Rule" — one instance per protected remote service.
