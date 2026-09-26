---
title: A public OAuth client keeps PKCE on, and an authorization server requires a code challenge for the authorization code grant
rule_id: SEC-28
domain: security
triggers: ['requireProofKey\(', '(?i)withpkce\(|pkce', 'code_challenge|codeChallenge|code_verifier|codeVerifier', 'ClientAuthenticationMethod[.]NONE|client-authentication-method', 'OAuth2AuthorizationRequestResolver|OAuth2AuthorizationRequestCustomizers', 'ClientSettings']
scope: file
check_kind: mechanical
severity_default: major
---

# A public OAuth client keeps PKCE on, and an authorization server requires a code challenge for the authorization code grant

## Thesis
A client registration without a secret (`ClientAuthenticationMethod.NONE`) keeps `requireProofKey` at its default so the framework sends a `code_challenge` and `code_verifier`; a custom `OAuth2AuthorizationRequestResolver` keeps `withPkce()` in its customizer; an authorization-server `RegisteredClient` for such a client sets `ClientSettings.requireProofKey(true)`, and the server rejects `code_challenge_method=plain`. `requireProofKey(false)` on a public client, or a resolver that drops the challenge, is the defect.

## Rationale
A public client — a browser app, a native app — cannot keep a secret, so an authorization code intercepted on its redirect (a malicious app registered for the same custom scheme, a leaked log, a referrer) can be redeemed by whoever holds it. PKCE binds the code to the client instance that started the flow: the token request presents the `code_verifier` whose hash was sent as the challenge, which the interceptor does not have. It also gives the client its cross-site request forgery protection for the code flow when the server enforces it. The framework turns PKCE on automatically for a registration with no secret or with `requireProofKey` true; a diff that sets the flag to `false` on such a client, or replaces the request resolver without the PKCE customizer, removes the binding.

## Example
```java
bad:  ClientRegistration.withRegistrationId("spa").clientAuthenticationMethod(ClientAuthenticationMethod.NONE)
          .clientSettings(ClientRegistration.ClientSettings.builder().requireProofKey(false).build())
good: ClientRegistration.withRegistrationId("spa").clientAuthenticationMethod(ClientAuthenticationMethod.NONE)
          .clientSettings(ClientRegistration.ClientSettings.builder().requireProofKey(true).build())
```

## Limits
Applies to public clients and to servers issuing codes to them. A confidential client whose provider does not support PKCE may set `requireProofKey(false)`, which the documentation names as the reason to do so; the diff shows a confidential registration (a secret) in that case. Client-credentials and refresh flows have no authorization code and no PKCE.

## Validator
On the triggered hunk find each `requireProofKey`, each custom authorization-request resolver, and each server client-settings block. Determine from the registration whether the client is public (no secret, authentication method `NONE`). Validator question: **does a public client, or a server issuing codes to one, run the authorization code flow without a PKCE challenge?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-28`, severity major, `file`, `symbol`, `code` = the `requireProofKey` setting or the resolver quoted verbatim from the diff, `fix` = PKCE required for the public client, `rationale` naming the intercepted code that an unbound flow lets an attacker redeem).

## Source
Spring Security reference, "OAuth 2.0 Client Authorization Grants" — PKCE "is automatically used when... client-secret is omitted (or empty)... client-authentication-method is set to none... or when ClientRegistration.clientSettings.requireProofKey is true"; the tip on disabling it only for confidential clients whose provider lacks PKCE. OWASP ASVS 5.0 requirements 10.2.1, 10.4.6. OWASP OAuth 2.0 Protocol Cheat Sheet, "PKCE" — clients "must use the Authorization Code Grant with PKCE (response_type=code) for all client types". RFC 9700 §2.1.1 (protecting redirect-based flows), §4.5 (authorization code injection).
