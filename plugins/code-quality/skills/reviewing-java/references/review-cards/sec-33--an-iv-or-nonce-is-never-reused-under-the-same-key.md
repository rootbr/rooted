---
title: Every encryption uses an IV or nonce generated for that message and never reused under the same key: 12 bytes from SecureRandom for AES-GCM and ChaCha20-Poly1305
rule_id: SEC-33
domain: security
triggers: ['GCMParameterSpec\(', 'IvParameterSpec\(', 'ChaCha20ParameterSpec\(', 'new byte\[(12|16)\]', 'ENCRYPT_MODE']
scope: file
check_kind: semantic
severity_default: major
---

# Every encryption uses an IV or nonce generated for that message and never reused under the same key: 12 bytes from SecureRandom for AES-GCM and ChaCha20-Poly1305

## Thesis
Each call that initialises a `Cipher` in `ENCRYPT_MODE` with an IV or nonce — a `GCMParameterSpec`, a `ChaCha20ParameterSpec` or an `IvParameterSpec` — supplies a value used for one encryption under that key and transmitted or stored alongside the ciphertext; for GCM and ChaCha20-Poly1305 it is 12 bytes freshly drawn from `SecureRandom` for that message. The value is not a constant, a zero array, a field filled once and reused across calls, a value derived from the key or the plaintext, or a counter that can restart.

## Rationale
A nonce, an IV or any other single-use number is used for one encryption-key and data-element pair, and its method of generation is appropriate to the algorithm. GCM's confidentiality and authenticity both rest on the (key, IV) pair being used once: the mode has "a uniqueness requirement on IVs used in encryption with a given key", and when IVs repeat "such usages are subject to forgery attacks", so after each encryption the cipher is to be re-initialised with a different IV; ChaCha20 and ChaCha20-Poly1305 carry the same requirement for unique nonces with a given key. The JDK's own GCM implementation refuses to initialise for encryption with the same key and IV it last used, but that check covers one `Cipher` object in one process, not a stored constant, a second instance or another host. Twelve bytes is the IV length GCM is specified around and the length the JDK generates when the caller supplies none, and the nonce length ChaCha20 requires; a randomly drawn 96-bit value keeps the repeat probability negligible for the number of messages a single key should encrypt, after which the key rotates.

## Example
```java
bad:  private static final byte[] IV = new byte[12];
      c.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, IV));
good: byte[] iv = new byte[12];
      random.nextBytes(iv);                        // one SecureRandom per class
      c.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
      out.write(iv); out.write(c.doFinal(pt));     // the IV travels with the ciphertext
```

## Limits
Applies to encryption. Decryption reads the IV from the message and is not flagged. A deterministic IV from a strictly increasing counter persisted with the key — a message sequence number that never restarts across restarts and instances — is a valid construction when the file shows the counter's persistence. A CBC `IvParameterSpec` is judged on the same single-use question. A test that fixes an IV to compare against a known vector is out of scope.

## Validator
On the triggered hunk find each `Cipher.init(ENCRYPT_MODE, …)` with a `GCMParameterSpec`, `IvParameterSpec` or `ChaCha20ParameterSpec`. Trace the IV array to its origin through the file: a `SecureRandom.nextBytes` call executed on every encryption is correct; a constant, a static or instance field filled once, a zero array, a value derived from the key, the plaintext or a timestamp, or a counter with no persistence is not. Validator question: **can two encryptions under the same key run with the same IV?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-33`, severity major, `file`, `symbol`, `code` = the IV declaration and the `init` call quoted verbatim from the diff, `fix` = a per-message `SecureRandom.nextBytes` into a 12-byte array (GCM or ChaCha20-Poly1305) written out with the ciphertext, `rationale` naming the reuse path and the forgery and confidentiality loss it enables).

## Source
`javax.crypto.Cipher` class Javadoc, Java SE 21 — "GCM mode has a uniqueness requirement on IVs used in encryption with a given key. When IVs are repeated for GCM encryption, such usages are subject to forgery attacks. Thus, after each encryption operation using GCM mode, callers should re-initialize the Cipher objects with GCM parameters which have a different IV value."; "The ChaCha20 and ChaCha20-Poly1305 algorithms have a similar requirement for unique nonces with a given key." JDK 21 reference implementation `com.sun.crypto.provider.GaloisCounterMode` — `DEFAULT_IV_LEN = 12` and the check that throws `InvalidAlgorithmParameterException("Cannot reuse iv for GCM encryption")`. `javax.crypto.spec.ChaCha20ParameterSpec` class Javadoc — "The parameters consist of a 12-byte nonce and an initial counter value". OWASP ASVS 5.0 §11.3.4 — "nonces, initialization vectors, and other single-use numbers are not used for more than one encryption key and data-element pair. The method of generation must be appropriate for the algorithm being used." NIST SP 800-38D §5.2.1.1 (96-bit IV) and §8 (uniqueness requirement) — by section. The generation method §11.3.4 requires is carried only as the 12-byte `SecureRandom` form for GCM and ChaCha20-Poly1305; for a CBC IV the card checks single use alone, and no cited source is carried for any further CBC IV property.
