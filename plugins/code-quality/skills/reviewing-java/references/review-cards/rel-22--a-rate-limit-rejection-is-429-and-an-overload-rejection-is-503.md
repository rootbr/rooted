---
title: A request rejected for a client's rate limit answers 429 and a request rejected for temporary server overload answers 503
rule_id: REL-22
domain: reliability
triggers: ['TOO_MANY_REQUESTS', 'SERVICE_UNAVAILABLE', 'RateLimiter', '(?i)ratelimit', 'Bucket4j', 'tryAcquire\(', 'tryConsume\(', 'acquirePermission\(', 'RequestNotPermitted', 'BulkheadFullException', 'status\(429\)', 'status\(503\)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A request rejected for a client's rate limit answers 429 and a request rejected for temporary server overload answers 503

## Thesis
When a handler or filter refuses a request because the client exceeded its quota, it responds `429 Too Many Requests`; when it refuses because the server is temporarily unable to handle the request — a full bulkhead, a saturated pool, an overload guard — it responds `503 Service Unavailable`; neither condition is answered with 403, 400 or 500.

## Rationale
A rejected client decides what to do next from the status code. 429 is the code defined for a client that "has sent too many requests in a given amount of time": the client, not the server, must slow down. 503 "indicates that the server is currently unable to handle the request due to a temporary overload or scheduled maintenance, which will likely be alleviated after some delay": the request was valid and may be repeated later. A 403 or 400 for either condition tells the client its request is refused or malformed, so a correct client stops retrying a request that would succeed after a pause; a 500 reports a server fault and pages the on-call for a condition the limiter produced by design. The two codes name who must change behaviour, and clients and gateways branch on them.

## Example
```java
bad:  if (!limiter.tryAcquire(key)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
      catch (BulkheadFullException e) { return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build(); }
good: if (!limiter.tryAcquire(key)) return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).build();   // client quota
      try { return ResponseEntity.ok(bulkhead.executeSupplier(() -> svc.handle(key))); }
      catch (BulkheadFullException e) { return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).build(); }   // server overload
```

## Limits
`Retry-After` is optional on both codes: a 429 or 503 without it is not this finding, and a limiter that can state the wait may add the header in delay-seconds or HTTP-date form. A rejection issued by a gateway or mesh the project context names is out of scope. A 503 sent for a permanent condition is a different mismatch and not this finding.

## Validator
On the triggered hunk find each rejection path of a rate limiter, bulkhead or overload guard and read the status it sets and the condition that produced it: a per-client quota or a server-side capacity. Validator question: **is a throttled or overloaded request answered with a status other than 429 or 503?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-22`, severity minor, `file`, `symbol`, `code` = the rejection response quoted verbatim from the diff, `fix` = 429 for a client quota or 503 for server overload, `rationale` naming what the wrong status tells the client to do).

## Source
RFC 9110 "HTTP Semantics" §15.6.4 "503 Service Unavailable" — "indicates that the server is currently unable to handle the request due to a temporary overload or scheduled maintenance, which will likely be alleviated after some delay"; the server "MAY send a Retry-After header field to suggest an appropriate amount of time for the client to wait before retrying the request"; §10.2.3 "Retry-After" — `Retry-After = HTTP-date / delay-seconds` (fetched from the httpwg source `draft-ietf-httpbis-semantics-latest.xml`). RFC 6585 §4 "429 Too Many Requests" — the user "has sent too many requests in a given amount of time", and the response "MAY include a Retry-After header" (unfetched; cited as its provenance line anchors it). Both RFCs make `Retry-After` optional ("MAY"), so its absence is not a finding of this card.
