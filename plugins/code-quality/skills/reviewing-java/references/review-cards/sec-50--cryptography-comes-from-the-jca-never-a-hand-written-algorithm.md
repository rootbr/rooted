---
title: Encryption, hashing and MACs come from the JCA or a vetted library, never from a hand-written algorithm, an XOR scheme or an encoding presented as encryption
rule_id: SEC-50
domain: security
triggers: ['(?i)encrypt', '(?i)decrypt', '(?i)obfuscat', '(?i)scrambl', '\^=', 'Base64[.]getEncoder\(\)', '(?i)cipher']
scope: file
check_kind: semantic
severity_default: major
---

# Encryption, hashing and MACs come from the JCA or a vetted library, never from a hand-written algorithm, an XOR scheme or an encoding presented as encryption

## Thesis
A method whose name or use promises confidentiality, integrity or authentication — `encrypt`, `decrypt`, `sign`, `hash`, `obfuscate`, `protect` — delegates to `javax.crypto.Cipher`, `Mac`, `MessageDigest`, `Signature`, `SecretKeyFactory`, `KeyAgreement` or a vetted library (Spring Security crypto, Tink, BouncyCastle), never to arithmetic the application wrote — an XOR against a repeated key, a shift or substitution, a home-made mixing function — and never to Base64, hex or compression standing in for encryption.

## Rationale
The security of a cipher, a MAC or a hash is a property established by public analysis of a specific construction; an algorithm the application invents has none of that, and the record of such schemes is that they fall to the first person who examines them. An XOR with a repeated key leaks the key from any known or repeated plaintext; a substitution preserves letter frequencies; Base64 and hex are reversible by definition and are encoding, not protection. The JCA providers and vetted libraries implement the analysed constructions with their parameters and modes, which is the only route to the property the method name claims.

## Example
```java
bad:  static byte[] encrypt(byte[] data, byte[] key) {
          byte[] out = data.clone();
          for (int i = 0; i < out.length; i++) out[i] ^= key[i % key.length];
          return out; }
good: static byte[] encrypt(byte[] data, SecretKey key, byte[] iv) throws GeneralSecurityException {
          Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
          c.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
          return c.doFinal(data); }
```

## Limits
Applies to a method relied on for security. A checksum for corruption detection, a hash for a bloom filter or a hash table, a one-time pad with a truly random key of message length used once, and an encoding named as encoding (`encodeBase64`) are not flagged. A published algorithm transcribed into the application (a copied SHA-256) is out of scope only when the project context says a vetted provider was unavailable; the provider remains the fix. Test vectors and puzzles are out of scope.

## Validator
On the triggered hunk find each method that promises confidentiality, integrity or authentication by its name or its call site. Open the file and read its body: a delegation to a JCA engine class or a vetted library is correct; byte arithmetic, XOR, shifts, substitution, a bespoke mixing function, or an encoder alone is the finding. Validator question: **does this method claim a cryptographic property it implements with arithmetic or encoding of its own rather than a vetted primitive?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-50`, severity major, `file`, `symbol`, `code` = the method's operative lines quoted verbatim from the diff, `fix` = the JCA or library call that provides the claimed property, `rationale` naming the scheme and how it is reversed or forged).

## Source
OWASP Cryptographic Storage Cheat Sheet, "Custom Algorithms" — "Don't do this"; "Algorithms" — AES with a secure mode as the symmetric preference. OWASP ASVS 5.0 §11.2.1 — "industry-validated implementations (including libraries and hardware-accelerated implementations) are used for cryptographic operations"; §14.1.1 — data "that is only encoded and therefore easily decoded, such as Base64 strings". CWE-1240 "Use of a Cryptographic Primitive with a Risky Implementation" — by id.
