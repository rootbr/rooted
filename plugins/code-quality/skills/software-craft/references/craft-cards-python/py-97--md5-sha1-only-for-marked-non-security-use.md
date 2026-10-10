---
title: MD5 or SHA-1 from hashlib serves only a non-security use that passes usedforsecurity=False, and a security use takes SHA-256 or stronger or, for a password, a salted key-derivation function
rule_id: PY-97
domain: input
step: [implement, review]
applies_to: [python]
triggers: ['hashlib[.](?:md4|md5|sha1)\(', 'hashlib[.]new\(\s*["''](?:md4|md5|sha1|sha)["'']', '\bhashes[.](?:MD5|SHA1)\(', '(?<![\w.])(?:md5|sha1)\(', '\b(?:MD2|MD4|MD5|SHA)[.]new\(']
scope: hunk
check_kind: semantic
severity_default: major
---

# MD5 or SHA-1 from hashlib serves only a non-security use that passes usedforsecurity=False, and a security use takes SHA-256 or stronger or, for a password, a salted key-derivation function

## Thesis
In a Python security context (storing passwords, generating security tokens or verifying data integrity) a digest comes from a known secure hash function such as SHA-256, and a password goes through a salted key-derivation function such as hashlib.scrypt or hashlib.pbkdf2_hmac; MD5 and SHA-1, whether hashlib.md5, hashlib.sha1, hashlib.new with "md4", "md5", "sha" or "sha1", or the MD2, MD4, MD5 and SHA-1 hashes of cryptography, Crypto and Cryptodome, serve only a use outside any security context, and a hashlib call for such a use passes usedforsecurity=False (Python 3.9 and later).

## Rationale
MD2, MD4, MD5 and SHA-1 are no longer considered secure, because it is computationally feasible to find two different inputs that produce the same hash output, a collision, and weak or broken hash functions may also be susceptible to pre-image attacks. When a weak hashing algorithm is used to protect sensitive data, such as storing passwords, generating security tokens or verifying data integrity, its weakness can be exploited to defeat that protection: an attacker who obtains hashed passwords or tokens can recover the original data more easily through brute force or precomputed (rainbow table) attacks, and an attacker facing an integrity check can craft a different input that produces the same hash and substitute malicious content without detection. Naive algorithms such as sha1(password) are not resistant against brute-force attacks; key derivation and key stretching algorithms are designed for secure password hashing, a good password hashing function must be tunable, slow and include a salt, and the salt of hashlib.pbkdf2_hmac and hashlib.scrypt should be about 16 or more bytes from a proper source such as os.urandom. Since Python 3.9 all hashlib constructors take a keyword-only argument usedforsecurity with default value True; False indicates that the hashing algorithm is not used in a security context, for example as a non-cryptographic one-way compression function, and allows insecure and blocked algorithms in restricted environments. One position accepts usedforsecurity=False where the algorithm is not used in a security context, and checks that keyword on all function variations of hashlib.

## Example
```python
bad:  token = hashlib.md5(session_key).hexdigest()
      stored = hashlib.new("sha1", password).hexdigest()
      digest = hashes.Hash(hashes.SHA1())
      checksum = md5(download).hexdigest()
good: token = hashlib.sha256(session_key).hexdigest()
      stored = hashlib.pbkdf2_hmac("sha256", password, salt, ITERATIONS)
      digest = hashes.Hash(hashes.SHA256())
      checksum = hashlib.sha256(download).hexdigest()
      cache_key = hashlib.md5(blob, usedforsecurity=False).hexdigest()
```

## Limits
The sources differ on a weak hash outside a security context. One position accepts MD5 or SHA-1 with usedforsecurity=False when the algorithm is not used in a security context, for example as a non-cryptographic one-way compression function; the stricter position asks that even non-sensitive use cases such as data integrity or fingerprinting use a modern cryptographic hash function such as SHA-256, SHA-512 or SHA-3. The separating condition is whether the hash serves a security context as hashlib defines usedforsecurity: the stricter position counts verifying data integrity among the protections a weak hash defeats, so an integrity check takes SHA-256, and a marked MD5 or SHA-1 stays only where the digest has no security role. For password storage the stricter position names a slow, memory-hard algorithm designed for that purpose, in order of preference Argon2, scrypt, bcrypt or PBKDF2, of which hashlib provides scrypt and pbkdf2_hmac. Ruff S324 does not lint OpenSSL- or platform-specific aliases and object identifiers such as "sha-1", "ssl3-md5" or "1.3.14.3.2.26"; a finder reading the call still sees them.

## Validator
Grep the hunk for hashlib.md4, hashlib.md5 and hashlib.sha1 calls, hashlib.new with "md4", "md5", "sha" or "sha1", a bare md5( or sha1( imported from hashlib, hashes.MD5() and hashes.SHA1() from cryptography, and MD2, MD4, MD5 or SHA from Crypto.Hash or Cryptodome.Hash. For each call, trace in the hunk and its function what the digest is for: a stored or compared password, a token, session key or signature, and a checksum that verifies a file or message against tampering are security uses; a digest with no security role, such as a cache key, is not, and there a hashlib call needs usedforsecurity=False. Validator question: **Does the hunk hash with MD5 or SHA-1 for a security use, or call a hashlib MD5 or SHA-1 constructor for a use with no security role without usedforsecurity=False?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PY-97`, severity major, `file`, `symbol`, `code` = the hash call and the line that uses its digest, verbatim from the diff, `fix` = `hashlib.sha256(...)` for a token or an integrity check, `hashlib.scrypt(...)` or `hashlib.pbkdf2_hmac(...)` with a salt for a password, or `usedforsecurity=False` on a hashlib call with no security role, `rationale` = collisions of MD5 and SHA-1 are computationally feasible, so a password, token or integrity check built on them can be defeated).
