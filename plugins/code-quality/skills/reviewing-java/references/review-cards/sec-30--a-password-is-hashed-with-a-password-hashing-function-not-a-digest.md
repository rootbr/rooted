---
title: A password is hashed with a password-hashing function, never with MD5, SHA-1, SHA-256 or another MessageDigest, and never stored as plaintext
rule_id: SEC-30
domain: security
triggers: ['MessageDigest[.]getInstance\(', 'DigestUtils[.]', 'Hashing[.](md5|sha1|sha256|sha512)\(', '(NoOp|MessageDigest|Standard|LdapSha|Md4|Md5)PasswordEncoder', '\{noop\}']
scope: file
check_kind: mechanical
severity_default: major
---

# A password is hashed with a password-hashing function, never with MD5, SHA-1, SHA-256 or another MessageDigest, and never stored as plaintext

## Thesis
A user password, PIN or recovery code is stored and verified through a password-hashing function — Argon2id, scrypt, bcrypt or PBKDF2, through a `PasswordEncoder` in Spring — and never through a plain digest such as `MessageDigest.getInstance("MD5")`, `"SHA-1"` or `"SHA-256"`, salted or not, and never as plaintext or under a `{noop}` encoding.

## Rationale
MD5, SHA-1 and the SHA-2 family were designed to be fast, and a GPU computes billions of them per second, so a leaked table of digests is brute-forced offline at that rate; a salt defeats precomputed tables but not the guessing rate. A password-hashing function is deliberately slow and, for Argon2id and scrypt, memory-hard, with a work factor that rises as hardware improves, so each guess costs the attacker resources comparable to what a verification costs the server. Layering a slow function over an existing fast digest, `bcrypt(md5(p))`, is a migration step only, to be replaced by a direct hash of the password on the user's next login.

## Example
```java
bad:  byte[] d = MessageDigest.getInstance("SHA-256").digest(password.getBytes(UTF_8));
      String stored = HexFormat.of().formatHex(d);
good: PasswordEncoder enc = PasswordEncoderFactories.createDelegatingPasswordEncoder();
      String stored = enc.encode(password);
      boolean ok = enc.matches(password, stored);
```

## Limits
Applies to a credential a person chooses or remembers. A digest of a high-entropy secret — an API key or a lookup code carrying 112 bits of randomness or more — may use a standard hash. A digest used as a checksum, an ETag, a cache key or a content address is not password storage. A `bcrypt(md5(p))` wrapper introduced to migrate an existing MD5 table is correct when the migration re-hashes on the next login. A test that fixes a known digest for a fixture is out of scope.

## Validator
On the triggered hunk find each `MessageDigest`, `DigestUtils`, Guava `Hashing` or legacy `PasswordEncoder` use, and each `{noop}` prefix. Open the file to see what bytes go into it: a password, PIN or recovery code, from a request, a form or a user entity, is a credential. Validator question: **does a user-chosen credential reach a plain digest, a no-op encoder or plaintext storage instead of a password-hashing function?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-30`, severity major, `file`, `symbol`, `code` = the digest or encoder line quoted verbatim from the diff, `fix` = the `PasswordEncoder` (or Argon2id/bcrypt/PBKDF2 call) that replaces it, `rationale` naming the fast digest and the offline guessing rate it permits).

## Source
OWASP Password Storage Cheat Sheet — "Fast hashing algorithms such as SHA-256 are not suitable for password storage because they allow attackers to perform large numbers of guesses quickly"; password hashing functions "should be slow (unlike algorithms such as MD5 and SHA-1, which were designed to be fast)"; `bcrypt(md5($password))` as an upgrade step to be replaced on next login. OWASP ASVS 5.0 §11.4.2 (approved, computationally intensive key derivation function for passwords) and §6.5.2 (a standard hash function only for secrets with 112 bits of entropy or more). CWE-916 and CWE-328 — by id.
