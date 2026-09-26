---
title: A SecurityFilterChain keeps the default protective response headers, and any disable or relaxation of nosniff, frame options or HSTS is scoped and justified
rule_id: SEC-08
domain: security
triggers: ['headers\(', 'frameOptions\(', 'contentTypeOptions\(', 'defaultsDisabled\(', 'httpStrictTransportSecurity\(|hsts\(', 'X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A SecurityFilterChain keeps the default protective response headers, and any disable or relaxation of nosniff, frame options or HSTS is scoped and justified

## Thesis
The header set Spring Security writes by default — `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security` on HTTPS responses, no-store cache control — stays in force. A diff that calls `headers(h -> h.disable())`, `defaultsDisabled()`, `contentTypeOptions(c -> c.disable())`, `frameOptions(f -> f.disable())`, `frameOptions(f -> f.sameOrigin())` or `httpStrictTransportSecurity(h -> h.disable())` limits the change to the endpoints it is for through a `securityMatcher` and states why (an embedded widget, a database console in a non-production profile); a chain-wide disable is the defect, and a chain-wide `sameOrigin()` its lesser form. Where framing by a known origin is required, a CSP `frame-ancestors` directive on those responses is the replacement.

## Rationale
`nosniff` makes the browser honour the declared `Content-Type` instead of guessing, which is what stops an uploaded or reflected file from being executed as script or rendered as HTML. `X-Frame-Options: DENY` (or `frame-ancestors 'none'`) stops the page from being loaded in an attacker's iframe, the mechanism of clickjacking; `SAMEORIGIN` reopens it for every same-origin page and is an application-wide decision, not a single endpoint's. HSTS tells the browser to reach the host over HTTPS only for a year, closing the downgrade window on the first request. Turning the whole header set off to fix one page removes all of them from every response of the chain, and the loss shows in no test.

## Example
```java
bad:  http.headers(h -> h.disable());
      http.headers(h -> h.frameOptions(f -> f.disable()));
good: http.securityMatcher("/embed/**")
          .headers(h -> h.frameOptions(f -> f.disable())
              .contentSecurityPolicy(c -> c.policyDirectives("frame-ancestors https://partner.example")));
```

## Limits
Applies to a chain that serves browser responses. A chain scoped by `securityMatcher` to a non-browser API may disable headers that matter only for rendered content, and the diff shows the scope. A `frameOptions` change inside a chain limited to a development-only console, or one whose reason is written beside it and accepted in the project context, rejects the finding. A chain-wide `frameOptions(f -> f.sameOrigin())` still blocks cross-origin framing; it is reported at minor, as a relaxation whose reason is due, not at this card's severity. Adding headers (`referrerPolicy`, `permissionsPolicy`, a CSP) is never flagged. HSTS is written by Spring Security only on secure requests, so a missing HSTS header on a plain-HTTP test response is not this defect.

## Validator
On the triggered hunk find each `disable()`, `defaultsDisabled()` or `sameOrigin()` under `headers(...)`. Check whether the enclosing chain has a `securityMatcher` narrowing it, and whether a comment or method name states the reason. Validator question: **does the diff remove or relax nosniff, frame options or HSTS for responses a browser renders, without a scope and a stated reason?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-08`, severity major, `file`, `symbol`, `code` = the `headers(...)` call quoted verbatim from the diff, `fix` = the default kept, or the relaxation moved under a `securityMatcher` with `frame-ancestors` for the allowed origin, `rationale` naming the header removed and the attack it stopped).

## Source
Spring Security reference, "Security HTTP Response Headers" §Default Security Headers — the default set `Cache-Control: no-cache, no-store, max-age=0, must-revalidate`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security: max-age=31536000 ; includeSubDomains` (HTTPS requests only), `X-Frame-Options: DENY`; the servlet page's `headers.disable()`, `defaultsDisabled()`, `contentTypeOptions.disable()` and `frameOptions` forms. OWASP HTTP Security Response Headers Cheat Sheet — `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, HSTS. OWASP Clickjacking Defense Cheat Sheet. OWASP ASVS 5.0 requirements 3.4.1, 3.4.4, 3.4.6.
