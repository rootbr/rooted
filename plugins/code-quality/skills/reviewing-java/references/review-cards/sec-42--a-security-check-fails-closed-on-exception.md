---
title: An authentication, authorization or cryptographic check fails closed; an exception on that path denies, never returns true, a default principal or a permissive fallback
rule_id: SEC-42
domain: security
triggers: ['AuthorizationManager', 'AuthenticationProvider', 'AuthenticationManager', 'PermissionEvaluator', 'hasPermission\(', '(?i)authoriz', '(?i)authentic', '(?i)fallback', 'exceptionally\(|onErrorReturn\(|recover\(', '(?i)(allowed|permission|policy)\b', 'SecurityContextHolder', 'JwtException', 'Signature[.]getInstance\(', 'Mac[.]getInstance\(']
scope: file
check_kind: semantic
severity_default: critical
---

# An authentication, authorization or cryptographic check fails closed; an exception on that path denies, never returns true, a default principal or a permissive fallback

## Thesis
In a method that decides whether a request is authenticated or authorised, verifies a token, signature or MAC, or decrypts data, every `catch`, every fallback (a circuit-breaker `fallbackMethod`, a resilience decorator, an `exceptionally` or `onErrorReturn` stage) and every default branch ends in a denial — an exception, `AuthorizationDecision(false)`, `false`, an empty result — never in `return true`, a synthetic or elevated principal, a skipped verification or the unverified input passed through.

## Rationale
A security check that throws on an unexpected condition — a malformed token, a missing claim, an unreachable authorisation service, a key that does not parse — has established nothing; a handler that turns that into "allow" converts every failure mode into a bypass, and an attacker can usually cause the failure at will by sending malformed input or exhausting the dependency. A fallback that returns a cached or default user widens trust the same way. Failing closed keeps the failure a denial or an error the caller sees, which is the outcome a working check would have produced for an invalid input.

## Example
```java
bad:  public boolean allowed(Auth a, Resource r) {
          try { return policy.decide(a, r); } catch (Exception e) { log.warn("policy down", e); return true; } }
      Claims fallback(String token, Throwable t) { return Jwts.claims().subject("anonymous").build(); }
good: public boolean allowed(Auth a, Resource r) {
          try { return policy.decide(a, r); } catch (Exception e) { log.error("policy down", e); return false; } }
```

## Limits
Applies to the decision path. A `catch` that logs and rethrows, translates to `AccessDeniedException` or `AuthenticationException`, or returns `false` or `Optional.empty()` is correct. A fallback that serves cached content for a public, read-only resource is not a security decision. A method whose failure is handled by an outer filter that denies, shown in the file or named in the project context, is correct. Business decisions outside authentication, authorisation and cryptography are a different concern.

## Validator
On the triggered hunk find each `catch`, fallback method, `exceptionally`/`onErrorReturn`/`recover` stage and default branch inside a method that authenticates, authorises, verifies or decrypts. Read what it returns or does next: `true`, a granted decision, a constructed principal or claims, a `chain.doFilter` that proceeds with an authentication set, or plaintext passed through is a fail-open. Validator question: **does an exception or fallback on this security path grant access or skip the verification?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-42`, severity critical, `file`, `symbol`, `code` = the `catch` or fallback quoted verbatim from the diff, `fix` = the same handler ending in a denial or a rethrow, `rationale` naming the failure an attacker can provoke and the access it then grants).

## Source
OWASP ASVS 5.0 §16.5.3 — "the application fails gracefully and securely, including when an exception occurs, preventing fail-open conditions"; §16.5.2 — the application "continues to operate securely when external resource access fails, for example, by using patterns such as circuit breakers"; §11.2.5 — cryptographic modules fail securely and errors are handled in a way that does not enable vulnerabilities. CWE-636 "Not Failing Securely ('Failing Open')" — by id.
