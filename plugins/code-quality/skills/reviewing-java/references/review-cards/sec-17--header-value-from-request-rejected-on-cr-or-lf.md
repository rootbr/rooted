---
title: A response header value built from request data is rejected when it contains a carriage return or line feed
rule_id: SEC-17
domain: security
triggers: ['setHeader\(|addHeader\(', 'sendRedirect\(', 'HttpHeaders', '[.]header\(|[.]headers\(', '"Location"|HttpHeaders[.]LOCATION', 'Set-Cookie|Content-Disposition|setContentType\(']
scope: file
check_kind: semantic
severity_default: major
---

# A response header value built from request data is rejected when it contains a carriage return or line feed

## Thesis
Before a value that originates in a request — a redirect target, a filename in `Content-Disposition`, a cookie value, a custom header echoing a parameter — is passed to `setHeader`, `addHeader`, `sendRedirect`, `HttpHeaders.set` or a `ResponseEntity` header, the code rejects it (or reduces it to an allowlisted form) if it contains `\r` or `\n`, checking the decoded value the header will carry rather than the URL-encoded form the request sent (`%0D`, `%0A`).

## Rationale
Headers are separated by CRLF on the wire, so a value that contains one ends the header early; what follows is read as further headers or, after a blank line, as the response body. That lets a request parameter add a `Set-Cookie`, inject a `Location`, or write a second response body — response splitting and header injection. A servlet container may strip or reject CR and LF in a header value, but the Servlet API does not specify it, the behaviour differs between containers, and it does not cover a value that reaches the wire by another route, so the check belongs in the code that builds the value. A redirect target is validated as a URL from an allowlist anyway; a filename is reduced to safe characters; a header echoing a parameter carries only the characters its purpose needs.

## Example
```java
bad:  response.setHeader("X-Requested-Page", req.getParameter("page"));
      response.sendRedirect(req.getParameter("next"));
good: String page = req.getParameter("page");
      if (page == null || page.indexOf('\r') >= 0 || page.indexOf('\n') >= 0) throw new IllegalArgumentException();
      response.setHeader("X-Requested-Page", page);
      response.sendRedirect(ALLOWED_NEXT.getOrDefault(req.getParameter("next"), "/"));
```

## Limits
Applies to a value from outside the code. A constant header, a value from configuration, or one already reduced to an allowlist (`[a-z0-9-]+`, an enum name, a numeric id) is not flagged. A value the framework encodes into a structured form (a `ResponseCookie` builder, `ContentDisposition.builder`) is correct where the builder validates its input. A log line containing CR or LF is a different sink.

## Validator
On the triggered hunk find each header-setting call with a non-constant value and trace the value to its origin in the file. Look for a CR/LF check or an allowlist reduction between origin and the call. Validator question: **can a request put a carriage return or line feed into a header this response writes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-17`, severity major, `file`, `symbol`, `code` = the header-setting call quoted verbatim from the diff, `fix` = the CR/LF rejection or the allowlist mapping before the call, `rationale` naming the header or body an injected line break can add).

## Source
RFC 9110 §5.5 "Field Values" — "Field values containing CR, LF, or NUL characters are invalid and dangerous, due to the varying ways that implementations might parse and interpret those characters; a recipient of CR, LF, or NUL within a field value MUST either reject the message or replace each of those characters with SP before further processing or forwarding of that message" (any field, request or response). CWE-113, Improper Neutralization of CRLF Sequences in HTTP Headers ('HTTP Response Splitting'). OWASP ASVS 5.0 requirement 4.2.4 — for HTTP/2 and HTTP/3 requests, header fields and values must not contain CR, LF or CRLF sequences, "to prevent header injection attacks" (stated for inbound requests; the response side of this card rests on RFC 9110 §5.5). `java.net.http.HttpRequest.Builder#header` Javadoc, Java SE 21 — throws "if the header name or value is not valid, see RFC 7230 section-3.2".
