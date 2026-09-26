---
title: A catch block handles the exception, logs it with the exception object, or rethrows it; it is never empty and never discards the failure
rule_id: REL-52
domain: reliability
triggers: ['catch \(', 'catch\(', 'ignored\)', '\(Exception e\) \{\s*\}', 'printStackTrace\(\)', 'log[.]\w+\("[^"]*"\);']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A catch block handles the exception, logs it with the exception object, or rethrows it; it is never empty and never discards the failure

## Thesis
Every `catch` block does one of three things: recovers by producing a defined result the caller can rely on, records the failure through the logging framework with the exception object passed as the last argument, or rethrows (wrapped or not); an empty block, a block holding only a comment, `printStackTrace()`, a log line without the exception, or a `return null` that hides the failure is not one of them, unless a comment explains why nothing is the correct response.

## Rationale
A swallowed exception turns a failure into silence: the caller continues with a partial result, data is written as if the step succeeded, a resource opened before the throw is never closed, and the incident is found by its consequences days later with no trace of the cause. "It is very rarely correct to do nothing in response to a caught exception" — the typical responses are to log it or rethrow it — and "when it truly is appropriate to take no action whatsoever in a catch block, the reason this is justified is explained in a comment". A log line without the exception object drops the stack trace and the cause chain, which is the only record of where the failure originated. In a study of 491 leak issues, bad exception handling was the second most common root cause, at 20% of all leaks and 32% of resource leaks — as one studied issue put it, "Programmer should handle the exception properly instead of swallowing it".

## Example
```java
bad:  try { publish(event); } catch (Exception e) { }
      try { publish(event); } catch (IOException e) { log.warn("publish failed"); }
good: try { publish(event); } catch (IOException e) { log.warn("publish of {} failed, queued for retry", event.id(), e); retryQueue.add(event); }
      try { publish(event); } catch (IOException e) { throw new PublishException(event.id(), e); }
```

## Limits
A catch that returns a documented default or fallback — parse failure to `Optional.empty()`, a missing optional resource to `null` — is a recovery when the caller handles the absent case and the comment or method contract says so. A test that asserts an exception is thrown may catch it and assert. `InterruptedException` handling — restore the interrupt or rethrow — is a separate rule. A catch whose only purpose is cleanup before rethrow is correct.

## Validator
On the triggered hunk find each `catch` and read its body. Flag an empty body, a body of comments only, `printStackTrace()`, a log call that does not pass the exception, or a `return`/default that hides the failure without a contract or comment naming the recovery. Validator question: **does this catch block let the failure vanish — no recovery the caller can rely on, no record with the exception, no rethrow?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-52`, severity major, `file`, `symbol`, `code` = the catch block quoted verbatim from the diff, `fix` = a log call with the exception as the last argument, a rethrow wrapping the cause, or a documented recovery, `rationale` naming the consequence the silence hides).

## Source
Google Java Style Guide §6.2 "Caught exceptions: not ignored" — "It is very rarely correct to do nothing in response to a caught exception. (Typical responses are to log it, or if it is considered 'impossible', rethrow it as an AssertionError.) When it truly is appropriate to take no action whatsoever in a catch block, the reason this is justified is explained in a comment" (fetched from `google/styleguide`, `javaguide.html`). SpotBugs `DE_MIGHT_IGNORE` — "In general, exceptions should be handled or reported in some way, or they should be thrown out of the method" (CWE-754). Error Prone `EmptyCatch`. arXiv:1810.00101 §4.4 — bad exception handling is the root cause of 20% of 491 leak issues and 32% of resource leaks. PMD `AvoidPrintStackTrace` (`category/java/bestpractices.xml`) — "Avoid printStackTrace(); use a logger call instead". SLF4J `org.slf4j.Logger#error(String, Throwable)` Javadoc — "Log an exception (throwable) at the ERROR level with an accompanying message"; class Javadoc — "logging statements can be parameterized in presence of an exception/throwable" (the exception object as the call's last argument).
