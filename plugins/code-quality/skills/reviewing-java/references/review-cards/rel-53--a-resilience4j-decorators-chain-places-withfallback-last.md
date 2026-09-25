---
title: A Resilience4j Decorators chain places withFallback last
rule_id: REL-53
domain: reliability
triggers: ['Decorators[.]of', 'withCircuitBreaker\(', 'withRetry\(', 'withFallback\(', 'withBulkhead\(', 'withTimeLimiter\(', 'withRateLimiter\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A Resilience4j Decorators chain places withFallback last

## Thesis
In a `Decorators.of...()` chain the first `with*` call wraps the call itself and each later one wraps the previous, so `withFallback` is the last call and sees every other decorator's failure.

## Rationale
"Decorators are applied in the order of the builder chain": `withCircuitBreaker` then `withRetry` then `withFallback` produces `Fallback(Retry(CircuitBreaker(Supplier)))` — "the Supplier is called first, then its result is handled by the CircuitBreaker, then Retry and then Fallback". A fallback declared before a later decorator wraps only what precedes it: retry exhaustion, a `CallNotPermittedException`, a `BulkheadFullException` or a `TimeoutException` added after it bypass the fallback and reach the caller as raw exceptions. Each decorator "makes its own determination whether an exception represents a failure", so the order also sets what the breaker counts: with the breaker inside the retry (`withCircuitBreaker` first), every attempt is one call the breaker records, and "a single logical operation with multiple retries will be recorded as multiple failures by the CircuitBreaker, potentially opening the circuit too aggressively"; with the breaker outside (`withRetry` first), it records "only 1 failure per total attempt". Neither order is wrong on its own; an unstated one is a choice the next reader cannot check.

## Example
```java
bad:  Decorators.ofSupplier(call).withFallback(e -> cached()).withRetry(retry).withCircuitBreaker(cb).decorate();
good: Decorators.ofSupplier(call).withRetry(retry).withCircuitBreaker(cb)   // breaker outside: one failure per operation
          .withFallback(e -> cached()).decorate();
```

## Limits
A chain with a single decorator has no order. A fallback declared before a later decorator on purpose — meant only for the inner exception type, with the outer failures left to the caller — is correct with a comment naming the intent. The order of `withCircuitBreaker` and `withRetry` is a design choice this rule does not flag: with the retry outside, the breaker counts every attempt; with the breaker outside, one failure per operation; a comment on the chain or the project context names which count is meant. Annotation-based aspects (`@CircuitBreaker`, `@Retry` on a method) are ordered by the `circuitBreakerAspectOrder` and `retryAspectOrder` properties, not by a chain, and are out of scope.

## Validator
On the triggered hunk find each `Decorators` chain and list its `with*` calls in order. Validator question: **does the chain place `withFallback` before another decorator?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-53`, severity minor, `file`, `symbol`, `code` = the chain quoted verbatim from the diff, `fix` = `withFallback` moved to the end of the chain, or a comment naming which failure count the breaker is meant to see, `rationale` naming the decorator whose failures bypass the fallback, or the attempt count the breaker records under the unstated order).

## Source
Resilience4j `io.github.resilience4j.decorators.Decorators` Javadoc (`resilience4j-all`) — "Decorators are applied in the order of the builder chain. For example ... .withCircuitBreaker(...).withRetry(...).withFallback(...) ... This results in the following composition when executing the supplier: Fallback(Retry(CircuitBreaker(Supplier))). This means the Supplier is called first, then its result is handled by the CircuitBreaker, then Retry and then Fallback. Each Decorator makes its own determination whether an exception represents a failure". Resilience4j Spring Boot 3 README (`resilience4j-spring-boot3/README.adoc`), "Important Note on Aspect Order" — "a single logical operation with multiple retries will be recorded as multiple failures by the CircuitBreaker, potentially opening the circuit too aggressively. To ensure the CircuitBreaker wraps the entire Retry operation (recording only 1 failure per total attempt), explicitly configure the aspect order so that the CircuitBreaker has a higher priority"; the Javadoc's example order illustrates the mechanism and recommends nothing, and the README states the trade-off for the annotation form — reading it onto the chain form is the card's own.
