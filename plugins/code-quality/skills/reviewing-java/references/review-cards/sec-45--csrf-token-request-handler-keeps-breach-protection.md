---
title: A CSRF token request handler keeps BREACH protection, so a plain CsrfTokenRequestAttributeHandler is installed only as a delegate
rule_id: SEC-45
domain: security
triggers: ['CsrfTokenRequestAttributeHandler', 'XorCsrfTokenRequestAttributeHandler', 'csrfTokenRequestHandler\(', 'CsrfTokenRequestHandler', 'CookieCsrfTokenRepository', 'csrf\(']
scope: file
check_kind: mechanical
severity_default: minor
---

# A CSRF token request handler keeps BREACH protection, so a plain CsrfTokenRequestAttributeHandler is installed only as a delegate

## Thesis
The `csrfTokenRequestHandler` in force is the default `XorCsrfTokenRequestAttributeHandler`, or a handler that delegates to it for resolving the token from a request; a `new CsrfTokenRequestAttributeHandler()` installed on its own, which is the documented opt-out of BREACH protection, is the defect unless the diff states the reason. A single-page-application setup uses the framework's SPA support or the documented delegating handler that renders the plain token and resolves through the Xor handler.

## Rationale
The Xor handler encodes randomness into the CSRF token value on each response, so the returned token changes every time a page reflects it; the plain handler renders the raw token and is the documented opt-out of that protection. The plain handler exists for the case where the masked value cannot be consumed — a JavaScript client that reads the token from a cookie — and the documented SPA configuration uses it only to hand the raw value to the client while the Xor handler still resolves incoming tokens.

## Example
```java
bad:  http.csrf(c -> c.csrfTokenRequestHandler(new CsrfTokenRequestAttributeHandler()));
good: http.csrf(c -> c.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
          .csrfTokenRequestHandler(new XorCsrfTokenRequestAttributeHandler()));
      // or, for a single-page application: http.csrf(c -> c.spa());
```

## Limits
Applies to a chain that serves browser pages or a single-page application. A chain with CSRF disabled for a documented bearer-token API has no handler. A response path without HTTP compression is not exposed to BREACH, and a project context stating that compression is off at every layer rejects the finding. A delegating handler that uses the plain handler for rendering and the Xor handler for `resolveCsrfTokenValue` is the documented single-page-application form on Spring Security 6.x; `csrf.spa()`, which configures the same thing, exists from Spring Security 7.0 and is not available on 6.x.

## Validator
On the triggered hunk find each `csrfTokenRequestHandler(...)` and the handler class it installs; open the file to see whether a delegating class routes resolution through the Xor handler. Validator question: **is a plain, non-Xor handler the one resolving tokens on this chain, with no stated reason?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-45`, severity minor, `file`, `symbol`, `code` = the handler installation quoted verbatim from the diff, `fix` = the Xor handler or the delegating SPA handler, `rationale` naming the unmasked token a compressed response reflects).

## Source
Spring Security reference, "Cross Site Request Forgery (CSRF) for Servlet Environments" — "By default, the XorCsrfTokenRequestAttributeHandler is used for providing BREACH protection of the CsrfToken. Spring Security also provides the CsrfTokenRequestAttributeHandler for opting out of BREACH protection"; "BREACH protection is provided by encoding randomness into the CSRF token value to ensure the returned CsrfToken changes on every request"; §Single-Page Applications configuration; `CsrfConfigurer#spa()` — `@since 7.0`. OWASP Cross-Site Request Forgery Prevention Cheat Sheet, "Synchronizer Token Pattern".
