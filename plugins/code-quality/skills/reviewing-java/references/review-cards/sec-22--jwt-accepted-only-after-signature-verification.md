---
title: A JWT is accepted only after its signature is verified with a server-held key, never by an unsigned parse or a decoded payload
rule_id: SEC-22
domain: security
triggers: ['parseClaimsJwt\(|parseUnsecuredClaims\(|parseUnsecuredContent\(|parseUnprotectedClaims\(|parseUnprotectedContent\(|parseClaimsJws\(|parseSignedClaims\(', 'Jwts[.]parser\(', 'JWT[.]decode\(|JWTParser[.]parse\(|SignedJWT[.]parse\(|PlainJWT', 'Base64[.]getUrlDecoder\(\)', 'JwtDecoder|NimbusJwtDecoder', '(?i)jwt|bearer']
scope: file
check_kind: mechanical
severity_default: critical
---

# A JWT is accepted only after its signature is verified with a server-held key, never by an unsigned parse or a decoded payload

## Thesis
Every token whose claims decide identity or permissions is parsed by a call that verifies the signature against a key the server configured — JJWT `Jwts.parser().verifyWith(key).build().parseSignedClaims(token)` (older API: `parseClaimsJws`), Spring Security's `JwtDecoder`, Nimbus `SignedJWT.parse` followed by `verify(verifier)` — and the claims are read from the verified result only. `parseClaimsJwt`, `parseUnsecuredClaims` or `parseUnprotectedClaims` (the unprotected-token parse under its older and newer names), `JWT.decode(token)` with no verifier, or splitting the token on `.` and Base64-decoding the payload, is the defect.

## Rationale
A JWT is three Base64url segments; the payload is readable by anyone and writable by anyone. Only the signature over header and payload, checked with the server's key, ties the claims to the issuer. A parse method for unprotected tokens accepts a token with no signature, so a client can mint `{"sub":"admin"}` and be believed; a decode-only helper returns the claims before any verification happens, and code that reads `sub` from it has authenticated nothing. The typed signed-parse methods fail on a missing or invalid signature, so the claims a caller sees are the claims that were signed; the library documentation states that a token whose signature fails cannot be safely trusted and is discarded.

## Example
```java
bad:  Claims c = Jwts.parser().setSigningKey(key).parseClaimsJwt(token).getBody();    // unsigned parse
      String sub = new String(Base64.getUrlDecoder().decode(token.split("\\.")[1]));  // no verification
good: Claims c = Jwts.parser().verifyWith(publicKey).build().parseSignedClaims(token).getPayload();
```

## Limits
Applies to tokens used for authentication or authorization decisions. Decoding a token only to read its `kid` or route to the right verifier, followed by verification before use, is correct. JJWT's generic `parse` behind `verifyWith` or `keyLocator` is the documented form and is not flagged: from JJWT 0.12 the parser rejects an unsecured (`alg: none`) token unless the builder enables that explicitly, so a generic `parse` with a bound key admits no unsigned token; a parser built with that option enabled, or one older than 0.12, takes the signed-parse call instead. A token already verified by an upstream filter (`oauth2ResourceServer`) and re-read from the `Authentication` is not re-verified in the controller. Encrypted tokens (JWE) take the decrypting parse with the same discipline. Test code is out of scope.

## Validator
On the triggered hunk find each parse, decode or manual Base64 split of a token, and the calls that read claims from its result. Check the parse method's family (signed, unprotected, generic), whether a key or verifier is bound before the claims are used, and — for a generic `parse` — whether the parser enables unsecured tokens or predates JJWT 0.12. Validator question: **can a token with no valid signature yield claims that this code acts on?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-22`, severity critical, `file`, `symbol`, `code` = the parse or decode call and the claim read quoted verbatim from the diff, `fix` = the signed-parse call with the server key, `rationale` naming the unsigned or unverified path through which forged claims are accepted).

## Source
JJWT README — signed parsing with `verifyWith(key)` and `parseSignedClaims`; "If a JWS and signature verification fails... the JWT cannot be safely trusted and should be discarded"; the unprotected-JWT walkthrough with `"alg": "none"` and the warning that such a token "offers no security protection at all"; `parseUnprotectedClaims`. The 0.12 rejection of an unsecured token unless enabled is not stated in the README cited. OWASP ASVS 5.0 requirement 9.1.1 — tokens "validated using their digital signature or MAC to protect against tampering before accepting the token's contents". Spring Security reference, "OAuth 2.0 Resource Server JWT" — the decoder validates the signature against the JWK Set key. RFC 8725 §3.1 (perform algorithm verification), §3.2 (use appropriate algorithms).
