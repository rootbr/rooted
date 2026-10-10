---
title: A security primitive such as encryption, password hashing, signing, token generation or HTML sanitization comes from a vetted, maintained library, a cryptographic one through its highest-level API, never from code written in the change
rule_id: INP-11
domain: input
step: [design, implement]
applies_to: [universal]
triggers: ['(?i)\b(def|function|func|fn|static|public|private|void|String|byte\[\])\s+\w*(encrypt|decrypt|cipher|hash_?password|password_?hash|sanitize_?html|strip_?tags)\w*\s*\(', '(?i)\^\s*(key|k|secret)\s*\[|\^=\s*(key|k|secret)\s*\[', '(?i)\b(md5|sha1|sha256|sha512)\b.*\b(password|passwd|pwd)\b|\b(password|passwd|pwd)\b.*\b(md5|sha1|sha256|sha512)\b', '(?i)(re[.](sub|compile)|replace(All)?)\(\s*[r/]?[\"''/]?\s*<\s*/?\s*(script|iframe)', '(?i)(?<![a-z])ecb(?![a-z])|\bNewECB|\bCipher[.]getInstance\(\s*[\"''](AES|DES|DESede|Blowfish)[\"'']\s*\)']
scope: hunk
check_kind: semantic
severity_default: major
---

# A security primitive such as encryption, password hashing, signing, token generation or HTML sanitization comes from a vetted, maintained library, a cryptographic one through its highest-level API, never from code written in the change

## Thesis
When a change performs a cryptographic operation (encryption, password hashing, signing, generation of a non-guessable token) or sanitizes untrusted HTML, an established, maintained library or framework feature performs it (for the cryptographic operation an industry-validated implementation, called through the highest-level API it offers for the task, the one that handles IVs and similar parameters itself, and for a stored password a password hashing function, not a general-purpose digest; for the HTML sanitization a well-known and secure sanitizer), and the change's own code supplies the inputs and consumes the result.

## Rationale
Designing or building cryptographic algorithms is very error-prone, side-channel attacks among the hazards, while an existing component is more likely to be tried and tested and should have security patches available. A stored password calls for an approved, computationally intensive key derivation function, also known as a password hashing function. Calling a library does not settle the matter: of 269 cryptographic vulnerabilities reported in the CVE database, just 17% were in cryptographic libraries and the remaining 83% were misuses of cryptographic libraries by individual applications. In four studies triangulating 100 question-and-answer posts, 100 GitHub repositories and survey input from 48 developers, developers found certain cryptographic algorithms difficult to use correctly, perceived the APIs as generally too low-level and preferred more task-based solutions. In a controlled experiment in which 256 developers recruited from GitHub attempted symmetric and asymmetric cryptography tasks with one of five APIs, the results suggest that APIs designed for simplicity can provide security benefits, since reducing the decision space prevents the choice of insecure parameters, but that simplicity is not enough. In a replication with 129 developers and 22 APIs of a 109-developer, 24-API controlled experiment, professional experience and expertise did not improve developers' ability to reason about APIs with blindspots, and long-term professionals made mistakes as often as relative novices. Delegating the whole operation to the library's highest-level call leaves IVs and similar parameters to the library and narrows the decision space in which insecure parameters get chosen.

## Example
```rust
bad:  fn encrypt(data: &[u8], key: &[u8]) -> Vec<u8> {
          data.iter().enumerate().map(|(i, b)| b ^ key[i % key.len()]).collect()
      }
      let ct = ecb::Encryptor::<Aes128>::new(key.into()).encrypt_padded_vec_mut::<Pkcs7>(data);
      let stored = Sha256::digest(password);
      let clean = comment.replace("<script>", "");
good: let sealed = aead_key.seal(data)?; // the library draws the nonce and appends the tag
      let stored = password_hasher.hash(password)?; // the library draws the salt
      let clean = html_sanitizer.clean(comment);
```

## Limits
Context-specific encoding or escaping is the ideal protection for untrusted content written into an unsafe context; sanitization, and with it the sanitization library, becomes necessary where encoding is not possible, as with untrusted HTML from a rich-text editor. A hash that protects nothing, such as a cache key or a checksum against accidental corruption, is not a security primitive and stays outside the rule. Beyond a password hashing function for a stored password, choosing algorithms, modes, key sizes, key management and protocols is the cryptographic design specialty: the rule stops at calling a vetted library's highest-level API, and the finder names that specialty and stops there.

## Validator
Grep the hunk for a routine named for encryption, decryption, password hashing or HTML sanitization; an XOR against an indexed key or secret; a general-purpose digest applied to a password; a regex or replace that strips script or iframe tags; a cipher requested by bare algorithm name or in ECB mode. Open the hunk around each hit and trace who computes the protected bytes: code written in the change, or one call into an established library or framework feature. Where a library is called, check whether the change picks IVs, nonces, salts, padding or the mode itself while the library offers a higher-level call that picks them. Skip a hash used only as a cache key or checksum. Validator question: **Does the hunk compute an encryption, password hash, signature, non-guessable token or HTML sanitization in its own code, or assemble a cryptographic one from a library's low-level parts with parameters it picks itself?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-11`, severity major, `file`, `symbol`, `code` = the hand-written routine or the low-level library call with its hand-picked parameters, verbatim from the diff, `fix` = the same operation as one call into a vetted library, for a cryptographic operation through its highest-level API for the task, in the file's language, `rationale` = which primitive the change implements or assembles and which parameter it chooses that the library would have chosen).
