---
title: An error response carries a generic message, never a stack trace, an internal exception message, SQL, a file path or a class name
rule_id: SEC-41
domain: security
triggers: ['@ExceptionHandler', '@ControllerAdvice', '@RestControllerAdvice', 'ErrorController', 'ErrorAttributeOptions', 'Include[.](STACK_TRACE|MESSAGE|EXCEPTION|BINDING_ERRORS)', '[.]getMessage\(\)', 'printStackTrace\(', 'getStackTrace\(', 'ResponseStatusException\(', 'ProblemDetail']
scope: file
check_kind: semantic
severity_default: major
---

# An error response carries a generic message, never a stack trace, an internal exception message, SQL, a file path or a class name

## Thesis
A response body, `ProblemDetail`, `ResponseStatusException` reason or error view built for a client carries a message the application composed for that client; it does not carry the message of an exception the application did not construct for the client, a stack trace, an exception class name, an SQL statement, a file path, a host name or a framework version, and an error-attributes bean does not include `STACK_TRACE`, `EXCEPTION` or an unfiltered `MESSAGE`.

## Rationale
An exception message written by a driver, a framework or the JDK names what failed in the implementation's terms: the query and table, the file that was not found, the class that could not be cast, the host that refused; a stack trace adds every class and line on the path. Scanners harvest these to map the application and choose attacks, and the same detail helps no legitimate client. A generic response gives the client what it can act on and leaves the detail where it belongs, in the server log written with the full exception; a correlation id (an MDC `traceId` or equivalent) inside the generic message is the recommended way to let support find that log entry.

## Example
```java
bad:  @ExceptionHandler(Exception.class)
      ResponseEntity<String> on(Exception e) {
          return ResponseEntity.status(500).body(e.getMessage() + "\n" + Arrays.toString(e.getStackTrace())); }
good: @ExceptionHandler(Exception.class)
      ProblemDetail on(Exception e) {
          log.error("unhandled request failure traceId={}", MDC.get("traceId"), e);
          return ProblemDetail.forStatusAndDetail(INTERNAL_SERVER_ERROR, "Request failed; ref " + MDC.get("traceId")); }
```

## Limits
Applies to responses sent to clients. The message of an exception the application throws for the client with client-safe text — a validation error naming the field, a `NotFoundException("order not found")` — is the application's own message and is not flagged. A development-profile handler that includes the trace, guarded by a profile the project context names, is a tolerance. Logging the full exception server-side is required, not a finding. `ProblemDetail` is the right vehicle; its `detail` is what the rule constrains.

## Validator
On the triggered hunk find each handler, error controller, error-attributes bean or `ResponseStatusException` that builds a client response. Trace what reaches the body: an `e.getMessage()`, `e.toString()`, `getStackTrace`, `printStackTrace(writer)` or `getCause()` of a caught exception the application did not construct, an `Include.STACK_TRACE`, `EXCEPTION` or `MESSAGE` option, or a string interpolating a query, a path or a host. Validator question: **does the client response carry internal detail from an exception, a query, a path or a stack?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-41`, severity major, `file`, `symbol`, `code` = the response-building line quoted verbatim from the diff, `fix` = a generic message with a correlation id and a server-side `log.error` carrying the exception, `rationale` naming the internal detail exposed and what a scanner learns from it).

## Source
OWASP ASVS 5.0 §16.5.1 — "a generic message is returned to the consumer when an unexpected or security-sensitive error occurs, ensuring no exposure of sensitive internal system data such as stack traces, queries, secret keys, and tokens". OWASP Error Handling Cheat Sheet — "a generic response is returned by the application but the error details are logged server side for investigation, and not returned to the user"; a 5xx response should "not provide any content as part of the response that would reveal implementation details"; the Spring `@RestControllerAdvice` example returning `ProblemDetail.forStatusAndDetail(INTERNAL_SERVER_ERROR, "An error occur, please retry")`. Spring Boot reference, "Servlet Web Applications → Error Handling" — the `/error` mapping and `ErrorController`/`ErrorAttributes` as the customisation points. CWE-209 — by id.
