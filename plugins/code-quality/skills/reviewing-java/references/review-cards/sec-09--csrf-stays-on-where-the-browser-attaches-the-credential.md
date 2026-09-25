---
title: CSRF protection stays enabled on every filter chain whose credential the browser attaches by itself, and is disabled only for a chain whose credential is a header the browser never adds
rule_id: SEC-09
domain: security
triggers: ['csrf\(', 'AbstractHttpConfigurer::disable', 'ignoringRequestMatchers\(|ignoringAntMatchers\(', 'CsrfTokenRepository|CsrfFilter', 'sessionCreationPolicy\(', 'oauth2ResourceServer\(|BearerTokenAuthenticationFilter']
scope: file
check_kind: semantic
severity_default: major
---

# CSRF protection stays enabled on every filter chain whose credential the browser attaches by itself, and is disabled only for a chain whose credential is a header the browser never adds

## Thesis
A `SecurityFilterChain` that authenticates a request from a cookie — a session cookie, a JWT or remember-me cookie, HTTP Basic that the browser caches — keeps `csrf` on for its state-changing endpoints; `csrf(AbstractHttpConfigurer::disable)` and `ignoringRequestMatchers(...)` over such endpoints are the defect. Disabling is correct for a chain whose only credential is one the browser does not attach on its own — an `Authorization: Bearer` header on a stateless API, a service used by no browser — and the diff shows that property of the chain, not of the whole application.

## Rationale
A cross-site request forgery works because the browser sends the victim's cookies with any request a third-party page triggers; the server sees a valid session and performs the action. The token defense requires a value in a header or parameter that a foreign page cannot read or set, so a request without it is rejected. A credential in a cookie — session id or JWT alike — is attached automatically, so the chain needs the token. A bearer token in the `Authorization` header is attached only by the application's own JavaScript, so a foreign page cannot forge an authenticated request and the token adds nothing; that is the one condition under which disabling is safe. The `ignoringRequestMatchers` form removes protection for the matched endpoints while keeping the rest, so a pattern like `/api/**` on a cookie-authenticated chain is the same defect scoped to those endpoints. Spring Security enables the protection by default, so the defect exists only where a diff turns it off.

## Example
```java
bad:  http.csrf(AbstractHttpConfigurer::disable);                          // chain with formLogin()
good: http.csrf(csrf -> csrf.csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse()));
      // stateless API whose only credential is Authorization: Bearer — disable is correct here:
      http.securityMatcher("/api/**").csrf(AbstractHttpConfigurer::disable)
          .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
          .oauth2ResourceServer(o -> o.jwt(Customizer.withDefaults()));
```

## Limits
Applies per filter chain. A chain that is `STATELESS`, matches only API paths, and authenticates through a bearer-token filter or `oauth2ResourceServer` with no cookie-based login is the documented case for disabling and is not flagged. A test configuration under `src/test` is out of scope. A project context stating that the application serves no browser clients rejects the finding. A `SameSite` attribute on the session cookie is defense in depth, not a replacement that justifies disabling.

## Validator
On the triggered hunk find each `csrf(...)` disable or `ignoringRequestMatchers`. Open the file and determine how the same chain authenticates: `formLogin`, `httpBasic`, `rememberMe`, a session cookie, a JWT read from a cookie, versus a `STATELESS` policy with `oauth2ResourceServer` or a bearer filter only. Check that the chain's `securityMatcher` limits it to the endpoints that property holds for. Validator question: **does a browser attach the credential of this chain by itself, so that a foreign page can trigger an authenticated state-changing request once the token check is gone?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-09`, severity major, `file`, `symbol`, `code` = the `csrf(...)` call quoted verbatim from the diff, `fix` = the protection restored, or the disable moved to a separate stateless bearer-token chain under its own `securityMatcher`, `rationale` naming the cookie-carried credential the browser attaches).

## Source
Spring Security reference, "Cross Site Request Forgery (CSRF)" — "Our recommendation is to use CSRF protection for any request that could be processed by a browser by normal users. If you are creating a service that is used only by non-browser clients, you likely want to disable CSRF protection"; "Requiring the actual CSRF token in a cookie does not work because cookies are automatically included in the HTTP request by the browser"; servlet page §Disable CSRF Protection with `ignoringRequestMatchers`. OWASP Cross-Site Request Forgery Prevention Cheat Sheet — "CSRF tokens are still essential for web applications that rely on cookies for authentication"; §Employing Custom Request Headers for AJAX/API. OWASP ASVS 5.0 requirement 3.5.1. CWE-352.
