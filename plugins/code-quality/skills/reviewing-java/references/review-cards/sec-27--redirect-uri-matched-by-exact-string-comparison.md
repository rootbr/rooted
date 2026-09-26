---
title: A registered OAuth redirect URI is matched by exact string comparison, with no wildcard, prefix or pattern matcher
rule_id: SEC-27
domain: security
triggers: ['redirectUri|redirect_uri|redirect-uri|RedirectUri', 'authenticationValidator\(|OAuth2AuthorizationCodeRequestAuthenticationValidator', 'getRedirectUris\(\)', 'RegisteredClient', 'ClientRegistration', 'postLogoutRedirectUri']
scope: file
check_kind: semantic
severity_default: major
---

# A registered OAuth redirect URI is matched by exact string comparison, with no wildcard, prefix or pattern matcher

## Thesis
The redirect URIs registered for a client are complete, literal URIs, and the code that accepts a `redirect_uri` parameter compares it to them by exact string equality. A registration holding `https://app.example/*` or a regex, and a custom authorization-request validator that accepts a prefix, a matching host, or any localhost port outside a development profile, is the defect. A client's own `redirect-uri` is likewise a literal, with template variables that resolve to the deployed base URL only.

## Rationale
The authorization server sends the authorization code to the redirect URI the request names. A prefix or pattern check lets the request name a URI the attacker controls that still matches — a path under the registered prefix that hosts an open redirector, a subdomain, a query the parser treats differently — and the code, or with implicit flows the token itself, is delivered to the attacker. Exact comparison of the whole string removes the parsing ambiguity as well as the wildcard: only the literal the operator registered is accepted. The default validator compares exactly; loosening it for localhost during development is documented, and the loosening must not ship.

## Example
```java
bad:  RegisteredClient.withId(id).redirectUri("https://app.example/*")
      // custom validator: registeredClient.getRedirectUris().stream().anyMatch(requested::startsWith)
good: RegisteredClient.withId(id).redirectUri("https://app.example/login/oauth2/code/app")
      // default validator, or: registeredClient.getRedirectUris().contains(requested)
```

## Limits
Applies to authorization-server registrations and to custom validators. A validator that allows `localhost` with any port in a profile that never runs in production, with the profile guard in the diff, is the documented development exception. A native client using loopback redirection with a variable port is a protocol-level exception the project context may name. Client-side `redirect-uri` templates (`{baseUrl}/login/oauth2/code/{registrationId}`) resolve to one literal per deployment and are not flagged.

## Validator
On the triggered hunk find each registered redirect URI and each redirect-URI comparison; open the file to read the validator's `accept` body and every `redirectUri(...)` on the registration. Check for wildcards, regexes, `startsWith`, `endsWith`, host-only comparisons, or a replaced default validator. Validator question: **can a redirect_uri other than a registered literal pass the check?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-27`, severity major, `file`, `symbol`, `code` = the registration or comparison quoted verbatim from the diff, `fix` = the literal URI and the exact-equality comparison, `rationale` naming the attacker-chosen URI the pattern admits).

## Source
OWASP ASVS 5.0 requirement 10.4.1 — "validates redirect URIs based on a client-specific allowlist of pre-registered URIs using exact string comparison". Spring Authorization Server reference, "Protocol Endpoints" — the default authorization-request validator "validates the redirect_uri and scope parameters"; the custom-validator example's "Use exact string matching when comparing client redirect URIs against pre-registered URIs" with its localhost development allowance. OWASP OAuth 2.0 Protocol Cheat Sheet — no "open redirectors" that "enable exfiltration of authorization codes and access tokens". RFC 9700 §4.1.3 (redirect URI validation: exact string matching).
