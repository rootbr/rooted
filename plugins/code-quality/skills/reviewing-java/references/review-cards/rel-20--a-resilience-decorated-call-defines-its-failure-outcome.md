---
title: A resilience-decorated call defines what the caller receives when the breaker is open or the retries are exhausted, and that outcome is never a silently swallowed failure
rule_id: REL-20
domain: reliability
triggers: ['withFallback\(', 'fallbackMethod', 'CallNotPermittedException', 'BulkheadFullException', '@CircuitBreaker', '@Retry\(', '@TimeLimiter', 'recover\(', 'onErrorResume\(', 'onErrorReturn\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A resilience-decorated call defines what the caller receives when the breaker is open or the retries are exhausted, and that outcome is never a silently swallowed failure

## Thesis
Where a call is wrapped in a circuit breaker, retry, time limiter or bulkhead, the code states the result of the protected path failing: a cached or default value the caller can use, a degraded response the caller can recognize, or a typed exception that propagates. A fallback that returns `null`, an empty collection, or a success-shaped value while discarding the failure is not an outcome.

## Rationale
A decorator converts a dependency failure into a fast rejection — `CallNotPermittedException` from an open breaker, `BulkheadFullException`, a `TimeoutException` — and something has to receive it. A fallback that returns a cached or approximate response keeps the caller working through the outage; a typed exception lets the caller decide. A fallback that maps every failure to `null` or an empty list hides the outage: downstream code proceeds as if the dependency had answered, data is written as absent, and no metric or log records that the breaker is open, so the degradation is discovered by users. The fallback path is also where a failure must keep its cause, since it is the last place the original exception is visible.

## Example
```java
bad:  Decorators.ofSupplier(() -> prices.fetch(id)).withCircuitBreaker(cb)
          .withFallback(e -> null).decorate();
good: Decorators.ofSupplier(() -> prices.fetch(id)).withCircuitBreaker(cb)
          .withFallback(List.of(CallNotPermittedException.class), e -> priceCache.lastKnown(id)
              .orElseThrow(() -> new PricingUnavailableException(id, e))).decorate();
```

## Limits
A decorated call with no fallback whose exception propagates to a caller that handles it is a defined outcome and is not flagged. A fallback returning an empty result is correct when the caller distinguishes it from a real answer and the failure is logged with its cause or counted in a metric in the same fallback. A fire-and-forget notification whose loss the project context accepts may swallow with a comment saying so.

## Validator
On the triggered hunk find each fallback lambda, `fallbackMethod`, `recover` or `onError*` handler attached to a decorated call and read what it returns and whether it records the exception. Flag a handler that returns `null`, an empty collection, `Optional.empty()` or a success value without logging, counting or wrapping the failure. Validator question: **does this fallback make a dependency failure indistinguishable from a successful answer while discarding the exception?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-20`, severity major, `file`, `symbol`, `code` = the fallback handler quoted verbatim from the diff, `fix` = a fallback that returns a recognizable degraded value or throws a typed exception carrying the cause, `rationale` naming the hidden outage).

## Source
arXiv:2512.16959 §VI.D — "Fallbacks (cached or approximate responses) maintain UX during partial outages"; §VI.A — retries "should be bounded, avoid non-idempotent operations, and be instrumented". Resilience4j `io.github.resilience4j.decorators.Decorators` Javadoc — composition `Fallback(Retry(CircuitBreaker(Supplier)))`, "Each Decorator makes its own determination whether an exception represents a failure". Google Java Style Guide §6.2 — "It is very rarely correct to do nothing in response to a caught exception".
