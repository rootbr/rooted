---
title: A digest, MAC or signature with a security purpose uses SHA-256 or stronger; MD5 and SHA-1 are absent from signatures, integrity checks, MACs and secret derivation
rule_id: SEC-49
domain: security
triggers: ['"MD5"', '"SHA-?1"', 'HmacMD5', 'HmacSHA1', 'MD5with', 'SHA1with', 'DigestUtils[.](md5|sha1)', 'Hashing[.](md5|sha1)\(', 'MessageDigest[.]getInstance\(', 'Mac[.]getInstance\(', 'Signature[.]getInstance\(']
scope: file
check_kind: mechanical
severity_default: major
---

# A digest, MAC or signature with a security purpose uses SHA-256 or stronger; MD5 and SHA-1 are absent from signatures, integrity checks, MACs and secret derivation

## Thesis
Where a hash protects something — a signature (`Signature.getInstance`), an HMAC (`Mac.getInstance`), an integrity check on downloaded or stored data, a token or key derived by hashing, a certificate or key fingerprint comparison — the algorithm named is SHA-256, SHA-384, SHA-512 or SHA-3, and `MD5`, `SHA-1`, `HmacMD5`, `HmacSHA1`, `MD5withRSA` and `SHA1with…` do not appear; a password belongs to a password-hashing function and to no digest here.

## Rationale
A hash in a signature, a data-authentication or an integrity role must be collision resistant with an output of at least 256 bits; MD5's 128 bits and SHA-1's 160 bits both fall under that floor, and a collision for full SHA-1 — two distinct inputs with the same digest — has been produced in practice, so a signature or an integrity tag over one input certifies the other and a fingerprint match proves nothing. ASVS disallows MD5 for any cryptographic purpose and requires collision-resistant functions with at least 256-bit output where signatures, data authentication or integrity depend on them; a MAC keyed with MD5 or SHA-1 falls under the same policy and gains nothing over HMAC-SHA-256. The JDK's own security configuration disables MD5 and SHA-1 signatures in certificate paths and signed jars and lists both as legacy algorithms, so a certificate or jar signed with them is already rejected by the platform; SHA-256 costs nothing more to use.

## Example
```java
bad:  Mac mac = Mac.getInstance("HmacMD5");
      String fp = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-1").digest(cert.getEncoded()));
      Signature sig = Signature.getInstance("SHA1withRSA");
good: Mac mac = Mac.getInstance("HmacSHA256");
      String fp = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(cert.getEncoded()));
      Signature sig = Signature.getInstance("SHA256withRSA");
```

## Limits
Applies to a digest with a security role. A digest used as a non-adversarial checksum, an ETag, a cache or partition key, or a content address where a collision is a correctness concern only, and a digest required by a legacy wire format that names the algorithm, are not flagged; a project context naming such a use is the tolerance. PBKDF2 with HMAC-SHA1 is a password-storage profile, not a digest with a security role, and is not flagged here. `UUID.nameUUIDFromBytes` (MD5 inside) as a stable id for non-secret input is a naming choice, not a security use.

## Validator
On the triggered hunk find each `MessageDigest`, `Mac`, `Signature`, `DigestUtils` or `Hashing` use naming MD5 or SHA-1. Open the file to see what the digest protects: a signature, a MAC, an integrity or fingerprint comparison, a token or key derivation is a security use; a checksum or cache key is not; a password is out of scope here. Validator question: **does MD5 or SHA-1 protect a signature, MAC, integrity check, fingerprint or derived secret?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-49`, severity major, `file`, `symbol`, `code` = the `getInstance` or digest call quoted verbatim from the diff, `fix` = the same call naming SHA-256 or stronger (`HmacSHA256`, `SHA256withRSA`), `rationale` naming the security role of the digest and the collision that defeats it).

## Source
OWASP ASVS 5.0 §11.4.1 — "only approved hash functions are used for general cryptographic use cases, including digital signatures, HMAC, KDF, and random bit generation. Disallowed hash functions, such as MD5, must not be used for any cryptographic purpose"; §11.4.3 — collision-resistant hash functions with at least 256-bit output for signatures, data authentication and integrity. JDK 21 `conf/security/java.security` — `jdk.certpath.disabledAlgorithms=MD2, MD5, SHA1 jdkCA & usage TLSServer, …`, `jdk.jar.disabledAlgorithms=MD2, MD5, …, SHA1 denyAfter 2019-01-01`, `jdk.security.legacyAlgorithms=SHA1, …, MD5, …`. OWASP Transport Layer Security Cheat Sheet, "Use Strong Cryptographic Hashing Algorithms" — certificates use SHA-256 "rather than the older MD5 and SHA-1 algorithms. These have a number of cryptographic weaknesses". Stevens, Bursztein, Karpman, Albertini and Markov, "The First Collision for Full SHA-1", CRYPTO 2017 — DOI 10.1007/978-3-319-63688-7_19. CWE-327 and CWE-328 — by id.
