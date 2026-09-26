---
title: A verified JWT is accepted only after its issuer, audience and validity window are checked against server configuration
rule_id: SEC-24
domain: security
triggers: ['requireIssuer\(|requireAudience\(|requireSubject\(|[.]require\(', 'JwtValidators|OAuth2TokenValidator|JwtIssuerValidator|JwtTimestampValidator|JwtClaimValidator', 'NimbusJwtDecoder[.]with(JwkSetUri|PublicKey|SecretKey)\(', 'getExpiration\(\)|getIssuer\(\)|getAudience\(\)|getNotBefore\(\)', 'parseSignedClaims\(|parseClaimsJws\(|withIssuer\(|withAudience\(', 'issuer-uri|audiences']
scope: file
check_kind: mechanical
severity_default: major
---

# A verified JWT is accepted only after its issuer, audience and validity window are checked against server configuration

## Thesis
After signature verification, the code (or the decoder's validator) checks that `iss` equals the configured issuer, that `aud` contains this service's identifier, and that the current time lies between `nbf` and `exp` (with a small clock skew); the claims are used only when all hold. A `NimbusJwtDecoder` built from `withJwkSetUri`, `withPublicKey` or `withSecretKey` with no `setJwtValidator` carrying an issuer validator, a JJWT parser without `requireIssuer` and `requireAudience`, or manual claim reads that skip `exp`, is the defect.

## Rationale
A valid signature proves who signed the token, not that it was meant for this service or is still current. Without an audience check, a token issued to a different service by the same issuer — same key, different `aud` — is accepted here, so a low-value service's token opens a high-value one. Without an issuer check, any issuer whose key the decoder can fetch is trusted. Without `exp` and `nbf`, a stolen token lives forever and a not-yet-valid one works early. A decoder built from an issuer location validates `iss`, `exp` and `nbf` by default; one built from a JWK Set URI or a raw key validates the timestamps but neither issuer nor audience, so the issuer validator has to be added; the audience check is not in the default set in either case.

## Example
```java
bad:  JwtDecoder d = NimbusJwtDecoder.withJwkSetUri(jwks).build();              // no iss, no aud check
good: NimbusJwtDecoder d = NimbusJwtDecoder.withJwkSetUri(jwks).build();
      d.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
          JwtValidators.createDefaultWithIssuer(issuer),
          new JwtClaimValidator<List<String>>("aud", a -> a != null && a.contains("orders-api"))));
```

## Limits
Applies to a decoder or parser the diff configures or a claim set the diff reads for decisions. A Spring Boot resource server configured by `issuer-uri` plus `audiences` is complete. A token type without `exp` by design (an internal long-lived service credential) is a project tolerance to state. A token whose audience is checked at an upstream gateway, documented in the project context, rejects the audience part only.

## Validator
On the triggered hunk find each decoder or parser construction and the validators attached to it, or each manual claim read. Check for issuer, audience and timestamp validation. Validator question: **can a signed token from the wrong issuer, for a different audience, or outside its validity window be accepted here?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-24`, severity major, `file`, `symbol`, `code` = the decoder or parser construction quoted verbatim from the diff, `fix` = the issuer, audience and timestamp validators attached, `rationale` naming the claim that goes unchecked and the token it lets in).

## Source
OWASP ASVS 5.0 requirements 9.2.1 ("for JWTs, the claims 'nbf' and 'exp' must be verified") and 9.2.3 ("validating the 'aud' claim against an allowlist defined in the service"). Spring Security reference, "OAuth 2.0 Resource Server JWT" — with `issuer-uri`, "Resource Server will default to verifying the iss claim as well as the exp and nbf timestamp claims"; `audiences` and the programmatic `aud` validator; `JwtValidators.createDefaultWithIssuer`. JJWT README — `require(claimName, requiredValue)` and the `requireSubject`-style family. RFC 7519 §4.1 (registered claims); RFC 8725 §3.8 (validate issuer and subject) and §3.9 (use and validate audience).
