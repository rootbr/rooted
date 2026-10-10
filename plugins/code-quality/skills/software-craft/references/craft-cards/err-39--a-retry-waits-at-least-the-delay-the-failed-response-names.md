---
title: A retry after a response that says how long to wait, such as Retry-After on a 429 or 503 or an RPC pushback, waits at least that long before the next attempt
rule_id: ERR-39
domain: errors
step: [implement, handle-errors]
applies_to: [service-boundary]
triggers: ['\b(413|429|503)\b', '(?i)too_?many_?requests|service_?unavailable|resource_?exhausted|\bthrottl|\bunavailable\b', '(?i)retr(y|ie[sd])|pushback|\battempt', '(?i)back[-_]?off']
scope: file
check_kind: semantic
severity_default: minor
---

# A retry after a response that says how long to wait, such as Retry-After on a 429 or 503 or an RPC pushback, waits at least that long before the next attempt

## Thesis
When code retries a failed call and the failure response names how long to wait — an HTTP Retry-After header on a 429, on a 503, or on a 413 whose condition is temporary, or an RPC pushback value — the next attempt waits at least that long, and a shorter computed backoff does not override it; the computed backoff sets the wait when the response names none. A pushback that says not to retry ends the retry. The attempt cap and the call's deadline still bound the retry: a call that has used up its attempts is not retried even when the server names a delay, and the call fails once its deadline passes, however many attempts remain.

## Rationale
The named wait is the server's own statement of how long the client ought to wait before its follow-up request. On a 503, which a server sends when it is unable to handle the request due to a temporary overload or scheduled maintenance that will likely be alleviated after some delay, it indicates how long the service is expected to be unavailable; on a 429 it tells a client that has sent too many requests in a given amount of time how long to wait before making a new request. A computed backoff is a function of the attempt number, so the attempt it schedules can fall before the named time, while the service is still expected to be unavailable, and a server receiving a very large number of requests from one party spends resources on every 429 it returns. The HTTP field gives the wait either as a number of seconds or as a date, so a parse that reads only one form misses the named wait whenever the server sends the other. A negative or unparseable RPC pushback value counts as the server asking the client not to retry at all.

## Example
```go
bad:  case http.StatusTooManyRequests, http.StatusServiceUnavailable: // 429, 503
          if err := sleepCtx(ctx, backoff(attempt)); err != nil {
              return nil, err
          }
good: case http.StatusTooManyRequests, http.StatusServiceUnavailable: // 429, 503
          wait := retryAfterOr(resp.Header.Get("Retry-After"), backoff(attempt))
          if err := sleepCtx(ctx, wait); err != nil {
              return nil, err
          }
```

## Limits
The rule governs the wait before a retry the code already makes; whether a failure is retried at all, how many attempts are allowed, and how the backoff is computed when no wait is named are judged by their own rules. Where the retry runs inside a client library that honors the named wait by default, the call site meets the wait clause unless it switches that behaviour off or overrides the library's wait, and the call's deadline still bounds that wait: where the library sleeps the named wait without regard to the deadline, the call site bounds it, for example by setting the library's cap on the named wait below the deadline. A client may cap the named wait at a threshold it considers reasonable and define what it does above it, since a misconfigured server or a malicious intermediary can send an excessive value; a documented cap of this kind, such as a library default of 21600 seconds, follows the rule.

## Validator
Grep the added lines for a 413, 429 or 503 status, a too-many-requests, service-unavailable, resource-exhausted or unavailable code, a throttling branch, a retry, attempt or pushback name, a Retry-After read, and a backoff computation. Open the file and find the retry path each hit belongs to: the loop, callback or handler that sends the same request again after a failed response. Trace the delay before the next attempt. Where the response can carry a Retry-After header or a pushback value, check that the delay is that named wait or longer, that the header is read in both its seconds and its date form, and that a pushback saying not to retry stops the loop; then check that the wait still ends with the failure when the call's deadline passes and that the attempt cap still counts the attempt. A retry delegated to a client library that honors the named wait by default is checked only against the call's deadline; a documented cap on the named wait and a path that does not retry are outside the rule. Validator question: **Does an added retry path, after a response that carries a Retry-After header or an RPC pushback, send the next attempt sooner than the named wait, retry after a pushback that says not to retry, or wait past the call's deadline or send an attempt beyond its attempt cap?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-39`, severity minor, `file`, `symbol`, `code` = the added line that sets or sleeps the delay before the next attempt, or the status check that starts the retry, verbatim from the diff, `fix` = the delay taken from the Retry-After header or the pushback value when the response carries one and from the computed backoff otherwise, the loop ended on a pushback that says not to retry, and the wait bounded by the call's deadline and attempt cap, in the file's language, `rationale` = the status or pushback the response carried, the wait it named, and whether the code retries sooner, retries against a do-not-retry pushback, or overruns the deadline or the attempt cap).
