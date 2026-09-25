---
title: An error response body is a structured problem document with a stable machine-readable type or code, never an ad-hoc string or the exception's message alone
rule_id: REL-54
domain: reliability
triggers: ['@ExceptionHandler', '@ControllerAdvice', '@RestControllerAdvice', 'ProblemDetail', 'ResponseEntity[.]status\(', 'getMessage\(\)\)', 'ResponseStatusException', 'ErrorResponse']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# An error response body is a structured problem document with a stable machine-readable type or code, never an ad-hoc string or the exception's message alone

## Thesis
An `@ExceptionHandler`, a `@ControllerAdvice` or a handler's error path returns a `ProblemDetail` (the RFC 9457 `application/problem+json` shape: `type`, `title`, `status`, `detail`, `instance`, plus the project's stable `code` and field-level details) or the project's documented error schema; it does not return a bare `String`, a `Map` assembled per handler, or `e.getMessage()` as the body.

## Rationale
A client can act on an error only if it can recognize it: retry on one code, show a field message on another, escalate on a third. A body that is a free-text message or the exception's `getMessage()` changes with every refactor and every locale, so clients parse prose and break silently; a per-handler `Map` gives each endpoint its own shape. A problem document carries a `type` (or `code`) that names the error class independently of its wording, a `status` matching the response, and room for details such as the offending field. Spring's `ProblemDetail` and `ErrorResponse` render this shape from any handler and, with `spring.mvc.problemdetails.enabled`, for the framework's own exceptions too, so the whole API has one error schema.

## Example
```java
bad:  @ExceptionHandler(OrderNotFoundException.class)
      ResponseEntity<String> notFound(OrderNotFoundException e) { return ResponseEntity.status(404).body(e.getMessage()); }
good: @ExceptionHandler(OrderNotFoundException.class)
      ProblemDetail notFound(OrderNotFoundException e) {
          ProblemDetail p = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, "order " + e.id() + " not found");
          p.setType(URI.create("https://api.example.com/problems/order-not-found")); p.setProperty("code", "ORDER_NOT_FOUND"); return p; }
```

## Limits
A project context naming its own error schema (a `code`/`message`/`details` envelope) satisfies the rule when the handler uses it. A plain-text body for a health or diagnostic endpoint consumed by humans is out of scope. Internal exception details in the body — stack traces, SQL, paths — are a separate concern and not this finding.

## Validator
On the triggered hunk find each error response construction in an exception handler or handler error path and read its body type: `ProblemDetail`/`ErrorResponse`, the project's error type, or a `String`/`Map`/`getMessage()`. Validator question: **does this error response give the client no stable machine-readable identifier of the error?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-54`, severity suggestion, `file`, `symbol`, `code` = the error response construction quoted verbatim from the diff, `fix` = a `ProblemDetail` (or the project's error type) with a `type`/`code`, `rationale` naming the prose the client would otherwise parse).

## Source
Spring Framework reference, "Error Responses" (Web MVC) — "the Spring Framework supports the RFC 9457 specification"; `ProblemDetail` is "a representation for an RFC 9457 problem detail"; "You can return ProblemDetail or ErrorResponse from any @ExceptionHandler or from any @RequestMapping method to render an RFC 9457 response"; "The status property of ProblemDetail determines the HTTP status"; extension "properties" for non-standard fields. RFC 9457 "Problem Details for HTTP APIs" — the `type`, `title`, `status`, `detail`, `instance` members and `application/problem+json` (unfetched; cited as its provenance line anchors it).
