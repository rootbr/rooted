---
title: An OAuth client or authorization-server registration uses no password or implicit grant
rule_id: SEC-26
domain: security
triggers: ['AuthorizationGrantType', '"password"|"implicit"', 'authorization-grant-type|authorizationGrantType\(', 'response_type=token|"token"\)', 'RegisteredClient', 'ClientRegistration']
scope: hunk
check_kind: mechanical
severity_default: major
---

# An OAuth client or authorization-server registration uses no password or implicit grant

## Thesis
A `ClientRegistration`, `RegisteredClient` or hand-built token request uses the authorization code grant (with PKCE), client credentials, refresh token, device code or token exchange; a grant type of `password` (resource owner password credentials) or `implicit` (`response_type=token`), whether written as a constant or as a string, is the defect.

## Rationale
The password grant hands the user's credentials to the client, which is the exposure OAuth exists to avoid, and it cannot carry multi-factor or consent steps. The implicit grant returns the access token in the URL fragment, where browser history, `Referer` headers and logs record it, and the token cannot be sender-constrained; its replacement, the authorization code grant with PKCE, works for single-page and native clients as well as confidential ones. Both grants are removed from the current best practice; the framework's 6.x grant-type constants keep `PASSWORD` only as deprecated for removal and carry no implicit constant, and 7.x removes `PASSWORD` too, so on 7.x a string literal is the only way to request either.

## Example
```java
bad:  ClientRegistration.withRegistrationId("app").authorizationGrantType(new AuthorizationGrantType("password"))
good: ClientRegistration.withRegistrationId("app").authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
          .clientAuthenticationMethod(ClientAuthenticationMethod.NONE)      // public client: PKCE applies
```

## Limits
Applies to registrations and token requests the diff writes. A migration that keeps a `password` grant behind a feature flag with a removal plan named in the project context is a tolerance the finder reports at lower severity. Test fixtures are out of scope. Grant types a server lists as supported for other clients are judged per client registration.

## Validator
On the triggered hunk find each grant type constant or string in a registration or token request. Validator question: **is a password or implicit grant configured or requested?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-26`, severity major, `file`, `symbol`, `code` = the grant type declaration quoted verbatim from the diff, `fix` = the authorization code grant with PKCE or the client credentials grant, `rationale` naming the credential or token exposure of the removed grant).

## Source
OWASP ASVS 5.0 requirement 10.4.4 — "the grants 'token' (Implicit flow) and 'password' (Resource Owner Password Credentials flow) must no longer be used". OWASP OAuth 2.0 Protocol Cheat Sheet — "Implicit Grant (DEPRECATED — DO NOT USE)"; "The Resource Owner password credentials grant is not used. This grant type insecurely exposes the credentials of the Resource Owner to the client". Spring Authorization Server reference, "Core Model / Components" — the supported `authorizationGrantTypes` list. Spring Security `org.springframework.security.oauth2.core.AuthorizationGrantType` — on 6.5.x `PASSWORD` is `@Deprecated(since = "5.8", forRemoval = true)` citing RFC 9700 §2.4 and no implicit constant exists; on `main` (7.x) `PASSWORD` is gone. RFC 9700 §2.1.2 (implicit grant), §2.4 (resource owner password credentials grant).
