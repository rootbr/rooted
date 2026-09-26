---
title: A caught exception is either logged or rethrown, not both
rule_id: MNT-22
domain: maintainability
triggers: ['log\w*[.](error|warn|info|debug)\([^;]*\b\w+\);?\s*$', 'catch\s*\(', 'throw new \w+\([^)]*,\s*\w+\)', 'LOGGER[.]|logger[.]|log[.]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A caught exception is either logged or rethrown, not both

## Thesis
A `catch` block that rethrows the exception — as is, or wrapped in a new exception with the original as cause — does not also log it; the log line is written once, at the layer that handles the exception (the controller advice, the job runner, the message listener), and an intermediate layer adds its context to the wrapping exception's message instead.

## Rationale
Each layer that logs and rethrows produces one stack trace per layer for one failure, so the log carries the same exception three or four times, interleaved with other threads' output, and the reader must work out that they are one event; alerting counts them as several. Logging where the exception is handled records it exactly once with the whole cause chain, and the message of each wrapping exception carries what the intermediate layer knew — the order id, the endpoint — into that single record.

## Example
```java
bad:  catch (GatewayException e) {
          log.error("charge failed for order {}", orderId, e);
          throw new PaymentFailedException("charge failed", e); }
good: catch (GatewayException e) {
          throw new PaymentFailedException("charge failed for order " + orderId, e); }
      // the boundary handler logs PaymentFailedException once, with its cause chain
```

## Limits
A `catch` that logs and then handles — returns a fallback, retries, or discards for a documented reason — logs correctly. A debug-level trace at an intermediate layer, without the throwable, for a diagnostic purpose the project context documents is tolerated. A boundary with no further handler (a `main`, a thread's `run`) both logs and, if it terminates by rethrowing, may do so.

## Validator
On the triggered hunk find each `catch` block containing both a logger call at any level that passes the exception (or its message) and a `throw`. Validator question: **does this `catch` block log the exception and also rethrow it or a wrapper of it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-22`, severity minor, `file`, `symbol`, `code` = the log line and the throw quoted verbatim from the diff, `fix` = the throw alone with the context in its message, `rationale` naming the duplicate stack traces per layer).

## Source
SonarSource `java:S2139` "Exceptions should be either logged or rethrown but not both" — "you end up with miles-long logs that contain multiple instances of the same exception. In multi-threaded applications debugging this type of log can be particularly hellish because messages from other threads will be interwoven with the repetitions of the logged-and-thrown Exception. Instead, exceptions should be either logged or rethrown, not both" (rule text from the `sonar-java` 6.15.1 plugin resources).
