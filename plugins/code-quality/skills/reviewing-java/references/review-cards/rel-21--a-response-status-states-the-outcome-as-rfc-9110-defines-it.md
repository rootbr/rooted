---
title: A response status code carries the meaning RFC 9110 gives it, so a failure is never sent as 2xx and a client error never as 5xx
rule_id: REL-21
domain: reliability
triggers: ['ResponseEntity[.]ok\(', 'HttpStatus[.]', '@ResponseStatus', 'ResponseEntity[.]status\(', '@ExceptionHandler', '@PostMapping', 'ResponseEntity[.]', 'setStatus\(']
scope: file
check_kind: semantic
severity_default: major
---

# A response status code carries the meaning RFC 9110 gives it, so a failure is never sent as 2xx and a client error never as 5xx

## Thesis
A handler or exception handler chooses the status class from the outcome: 2xx only when the request "was successfully received, understood, and accepted"; 201 with a `Location` header when a resource was created; 4xx (400, 404, 409, 422) when "the client seems to have erred"; 5xx when the server failed. An error body under a 200, a validation failure under a 500, or a missing resource under a 200 with an empty body contradicts the code.

## Rationale
Clients, proxies and caches act on the status class before they read the body: a 200 is retried by no one and may be cached, so an error inside it is treated as a result and stored; a 500 for malformed input tells the client to retry a request that can never succeed and pages the server's on-call for the client's mistake; a 200 with no body for a missing resource makes "absent" indistinguishable from "empty". The standard defines each class and code by the condition it reports and asks the server to explain 4xx and 5xx conditions in the body, so a client can branch on the class alone.

## Example
```java
bad:  @ExceptionHandler(ValidationException.class)
      ResponseEntity<ErrorBody> invalid(ValidationException e) { return ResponseEntity.ok(ErrorBody.of(e)); }
      @PostMapping ResponseEntity<Order> create(@RequestBody Req r) { return ResponseEntity.ok(svc.create(r)); }
good: @ExceptionHandler(ValidationException.class)
      ResponseEntity<ErrorBody> invalid(ValidationException e) { return ResponseEntity.unprocessableEntity().body(ErrorBody.of(e)); }
      @PostMapping ResponseEntity<Order> create(@RequestBody Req r) {
          Order o = svc.create(r); return ResponseEntity.created(URI.create("/orders/" + o.id())).body(o); }
```

## Limits
A `POST` that performs an action without creating a resource returns 200 or 202, not 201. A batch endpoint that reports per-item failures inside a 200 body is a documented protocol and is not flagged when the project context names it. A 404 versus 204 for a repeated `DELETE` is a choice the standard allows either way. Status codes translated by a gateway the project context names are out of scope.

## Validator
On the triggered hunk find each response construction and each exception handler. Trace what condition produces it: a created resource, an absent resource, invalid input, a conflict, an unexpected server failure. Compare the condition with the status class and, for 201, check for a `Location` header. Validator question: **does any response here report an outcome with a status whose defined meaning contradicts it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-21`, severity major, `file`, `symbol`, `code` = the response construction quoted verbatim from the diff, `fix` = the status matching the outcome (with `Location` for a creation), `rationale` naming how a client or cache misreads the wrong class).

## Source
RFC 9110 "HTTP Semantics" §15.3 — the 2xx class "indicates that the client's request was successfully received, understood, and accepted"; §15.3.2 — 201 "has resulted in one or more new resources being created. The primary resource created by the request is identified by either a Location header field in the response or, if no Location header field is received, by the target URI"; §15.5 — 4xx "indicates that the client seems to have erred", and the server SHOULD send "a representation containing an explanation of the error situation"; §15.6 — 5xx "indicates that the server is aware that it has erred or is incapable of performing the requested method"; §15.5.20 — 422 for content that is syntactically correct but cannot be processed; §15.5.10 — 409 for a conflict with the current state (fetched from the httpwg source `draft-ietf-httpbis-semantics-latest.xml`).
