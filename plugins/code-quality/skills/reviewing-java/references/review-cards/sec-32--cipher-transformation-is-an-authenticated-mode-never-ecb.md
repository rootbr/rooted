---
title: Cipher.getInstance names AES or ChaCha20 in an authenticated mode, never ECB, a bare AES transformation, DES, DESede, RC4 or Blowfish
rule_id: SEC-32
domain: security
triggers: ['Cipher[.]getInstance\(', '"AES"', '/ECB/', '"DES', 'DESede', 'RC4', 'ARCFOUR', 'Blowfish', 'AES/CBC', 'AES/CTR']
scope: file
check_kind: mechanical
severity_default: major
---

# Cipher.getInstance names AES or ChaCha20 in an authenticated mode, never ECB, a bare AES transformation, DES, DESede, RC4 or Blowfish

## Thesis
Every `Cipher.getInstance` transformation in the diff names an authenticated-encryption mode — `AES/GCM/NoPadding` or `ChaCha20-Poly1305` — or a CBC or CTR transformation whose ciphertext is covered by an HMAC computed after encryption and verified before decryption; it never names `AES/ECB/…`, the bare `"AES"` transformation, `DES`, `DESede`, `RC4`/`ARCFOUR`, `RC2` or `Blowfish`.

## Rationale
A transformation of the form "algorithm" alone leaves mode and padding to provider-specific defaults, and the JDK's SunJCE provider constructs an AES cipher in ECB mode with PKCS5 padding. ECB encrypts each 16-byte block independently, so equal plaintext blocks give equal ciphertext blocks and the ciphertext reveals structure and repetition of the plaintext, for a short token as much as for a long file. CBC and CTR hide that but authenticate nothing: a modified ciphertext decrypts to modified plaintext without detection, and a padding-oracle path can decrypt CBC without the key unless a MAC rejects modified ciphertext first. GCM and ChaCha20-Poly1305 bind a tag to the ciphertext and any associated data; the tag is verified on decryption and a modified message is rejected. DES, DESede and RC4 are disabled for TLS, and DES, DESede, RC2 and RC4 are listed as legacy, by the JDK's own security configuration; only approved ciphers and modes, AES with GCM the named example, are used, which excludes Blowfish and RC2 as well, and any primitive below 128 bits of security fails the ASVS minimum.

## Example
```java
bad:  Cipher c = Cipher.getInstance("AES");
      c.init(Cipher.ENCRYPT_MODE, key);
      byte[] ct = c.doFinal(pt);
good: byte[] iv = new byte[12]; new SecureRandom().nextBytes(iv);
      Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
      c.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
      byte[] ct = c.doFinal(pt);
```

## Limits
Applies to data the application encrypts for confidentiality or integrity. A CBC or CTR transformation is correct when the file shows an HMAC (SHA-256 or stronger) over the IV and ciphertext computed after encryption and verified before decryption, or when the project context names a legacy transformation as an interoperability requirement for reading data another system wrote, in decrypt mode only. AES/ECB as a raw block primitive inside a documented construction of a vetted library (a key wrap, a CMAC) is out of scope. RSA transformations and key wrapping are a separate concern.

## Validator
On the triggered hunk read each transformation string, resolving a constant through the file. Flag a bare algorithm name, an `ECB` mode, or a legacy algorithm (DES, DESede, RC4/ARCFOUR, RC2, Blowfish). For `CBC` or `CTR`, open the file and look for a `Mac` over the ciphertext that is verified before `Cipher.DECRYPT_MODE` runs; none → flag. Validator question: **does this transformation encrypt without authentication, or with ECB, a provider default or a legacy cipher?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-32`, severity major, `file`, `symbol`, `code` = the `Cipher.getInstance` call quoted verbatim from the diff, `fix` = the `AES/GCM/NoPadding` (or `ChaCha20-Poly1305`) transformation with its parameter spec, `rationale` naming the mode or cipher and what it leaks or fails to authenticate).

## Source
`javax.crypto.Cipher` class Javadoc, Java SE 21 — a transformation is "algorithm/mode/padding" or "algorithm", and "in the latter case, provider-specific default values for the mode and padding scheme are used"; AEAD modes "provide authenticity assurances". JDK 21 reference implementation `com.sun.crypto.provider.CipherCore` — `cipherMode = ECB_MODE` as the initial value; `AESCipher` — "default ECB mode". OWASP Cryptographic Storage Cheat Sheet, "Cipher Modes" — "authenticated modes should always be used… GCM and CCM… first preference"; CTR or CBC only with separate authentication such as Encrypt-then-MAC; "ECB should not be used outside of very specific circumstances"; "Algorithms" — AES with a key of at least 128 bits. OWASP ASVS 5.0 §11.3.1, §11.3.2, §11.3.3 and §11.2.3. JDK 21 `conf/security/java.security` — `jdk.tls.disabledAlgorithms` lists RC4, DES and 3DES_EDE_CBC; `jdk.security.legacyAlgorithms` lists DES, DESede, RC2 and ARCFOUR. CWE-327 — by id. Blowfish and RC2 in the title rest on §11.3.2, "only approved ciphers and modes such as AES with GCM are used": neither is an approved cipher; no cited source names Blowfish, and RC2 appears only in the JDK legacy list.
