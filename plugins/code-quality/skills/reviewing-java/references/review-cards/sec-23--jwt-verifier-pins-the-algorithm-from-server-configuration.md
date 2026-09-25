---
title: A JWT verifier pins the accepted algorithm family from server configuration, rejects none, and never takes the algorithm from the token header
rule_id: SEC-23
domain: security
triggers: ['jwsAlgorithm\(|jwsAlgorithms\(|SignatureAlgorithm|MacAlgorithm|JWSAlgorithm', '"alg"|getAlgorithm\(\)|[.]alg\b', 'verifyWith\(|setSigningKey\(|keyLocator\(|JWSKeySelector|JWSVerifier', 'Algorithm[.](HMAC|RSA|ECDSA)', 'NimbusJwtDecoder', 'HS256|RS256|ES256|"none"']
scope: file
check_kind: semantic
severity_default: critical
---

# A JWT verifier pins the accepted algorithm family from server configuration, rejects none, and never takes the algorithm from the token header

## Thesis
The set of signature algorithms a verifier accepts is fixed in the server's code or configuration — `NimbusJwtDecoder...jwsAlgorithm(RS256)`, JJWT's `verifyWith` with a key of one type, a key selector that returns keys for one family — and contains no `none`. The token's `alg` header selects nothing: code that reads `alg` and picks a key or verifier from it, or a key locator that hands an RSA public key to an HMAC verifier because the header said `HS256`, is the defect.

## Rationale
The `alg` header is written by whoever wrote the token, so a verifier that obeys it lets the attacker choose the check. With `none` the check is skipped entirely. With algorithm confusion the attacker takes the server's public RSA key — public by design — signs a forged token with HMAC using that key's bytes as the secret and sets `alg: HS256`; a verifier that selects the algorithm from the header and the key from `kid` then verifies the HMAC with the public key and accepts the forgery. Pinning the family server-side, keeping symmetric and asymmetric keys in separate stores, and rejecting `none` removes the attacker's choice; where both families are accepted, the key material for each is typed so that a key cannot be used under the other family.

## Example
```java
bad:  String alg = JWT.decode(token).getAlgorithm();
      Algorithm a = alg.startsWith("HS") ? Algorithm.HMAC256(publicKeyPem) : Algorithm.RSA256(publicKey, null);
      JWT.require(a).build().verify(token);
good: JWT.require(Algorithm.RSA256(publicKey, null)).withIssuer(ISSUER).build().verify(token);
```

## Limits
Applies to verification code and decoder configuration. A resource server built from an issuer location or JWK Set with the default `RS256` and no algorithm customization is correct. A JWK Set-driven selector that picks the key by `kid` and restricts the algorithm to the family the key's type implies is the documented multi-algorithm form. Choosing a verifier by `kid` (not by `alg`) from a server-held table of typed keys is correct.

## Validator
On the triggered hunk find each read of the token's algorithm header and each verifier or key selection that depends on it, and each decoder builder's algorithm setting. Open the file to see where the accepted algorithms and keys come from. Validator question: **does the token's alg header, rather than server configuration, decide which algorithm or key verifies it, or is none accepted?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-23`, severity critical, `file`, `symbol`, `code` = the algorithm read or key selection quoted verbatim from the diff, `fix` = the verifier pinned to the configured family with typed keys, `rationale` naming the header-chosen algorithm and the confusion or `none` path it opens).

## Source
OWASP ASVS 5.0 requirement 9.1.2 — "only algorithms on an allowlist can be used to create and verify self-contained tokens... must not include the 'None' algorithm. If both symmetric and asymmetric must be supported, additional controls will be needed to prevent key confusion". Spring Security reference, "OAuth 2.0 Resource Server JWT" §Configuring Trusted Algorithms — "By default, NimbusJwtDecoder, and hence Resource Server, will only trust and verify tokens using RS256". JJWT README — `verifyWith(publicKey) // publicKey, not privateKey`. RFC 8725 §2.1 (weak signatures and insufficient signature validation), §3.1 (perform algorithm verification).
