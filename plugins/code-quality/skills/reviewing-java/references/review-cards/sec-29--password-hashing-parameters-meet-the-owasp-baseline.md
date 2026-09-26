---
title: A password-hashing encoder is configured at or above the baseline of Argon2id 19 MiB with 2 iterations, bcrypt cost 10, or PBKDF2-HMAC-SHA256 600,000 iterations
rule_id: SEC-29
domain: security
triggers: ['Argon2PasswordEncoder', 'BCryptPasswordEncoder\(', 'Pbkdf2PasswordEncoder', 'SCryptPasswordEncoder', 'PBEKeySpec\(', 'PBKDF2WithHmac', 'Argon2Parameters', 'BCrypt[.]gensalt\(']
scope: file
check_kind: mechanical
severity_default: major
---

# A password-hashing encoder is configured at or above the baseline of Argon2id 19 MiB with 2 iterations, bcrypt cost 10, or PBKDF2-HMAC-SHA256 600,000 iterations

## Thesis
A password hash is produced by Argon2id, scrypt, bcrypt or PBKDF2 whose parameters, as written in the diff or in the constant it reads, meet the baseline: Argon2id with memory of at least 19,456 KiB and 2 iterations at parallelism 1 (or an equal-cost row: 47,104 KiB with 1 iteration, 12,288 with 3, 9,216 with 4, 7,168 with 5); scrypt with N = 2^17, r = 8, p = 1 (or an equal-cost row: N = 2^16 with p = 2, 2^15 with p = 3, 2^14 with p = 5, 2^13 with p = 10, r = 8 throughout); bcrypt with a cost (log rounds) of at least 10; PBKDF2-HMAC-SHA256 with at least 600,000 iterations, or PBKDF2-HMAC-SHA512 with at least 220,000.

## Rationale
These functions are deliberately slow, and their whole defence is the work factor, which turns each offline guess against a leaked table into memory and time on the attacker's hardware. A parameter below the baseline lowers the cost per guess with no visible change in behaviour: PBKDF2 at 1,000 iterations is six hundred times cheaper per guess than at 600,000. The Argon2id rows have equal defensive value and trade RAM for CPU; the scrypt rows likewise give a similar minimal level of defence, trading parallelism against RAM. A verification should take about one second on the serving hardware, and the work factor should rise as hardware improves, which a delegating encoder supports by re-hashing on the user's next successful login.

## Example
```java
bad:  PasswordEncoder enc = new BCryptPasswordEncoder(4);
      SecretKeyFactory f = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
      byte[] h = f.generateSecret(new PBEKeySpec(pw, salt, 1000, 256)).getEncoded();
good: PasswordEncoder enc = new Argon2PasswordEncoder(16, 32, 1, 19456, 2);
      byte[] h = f.generateSecret(new PBEKeySpec(pw, salt, 600_000, 256)).getEncoded();
```

## Limits
Applies to a hash of a user password or an equivalent low-entropy secret such as a PIN or a recovery code. A PBKDF2 or scrypt call that derives an encryption key from high-entropy key material (112 bits of randomness or more) is key derivation, not password storage, and takes its own parameters. `PasswordEncoderFactories.createDelegatingPasswordEncoder()` and a no-argument `BCryptPasswordEncoder()` use cost 10 and pass. Spring Security's `Argon2PasswordEncoder.defaultsForSpringSecurity_v5_8()` sets 16,384 KiB, 2 iterations, parallelism 1, and `Pbkdf2PasswordEncoder.defaultsForSpringSecurity_v5_8()` sets 310,000 iterations, both under the baseline; a project context that accepts the framework defaults rejects the finding for those factory calls. A test fixture that lowers the cost for test speed and is confined to test sources is out of scope.

## Validator
On the triggered hunk find each encoder constructor, `PBEKeySpec`, `Argon2Parameters.Builder` or `BCrypt.gensalt` call and read its numeric arguments, opening the file for any constant they name. Compare against the rows for the algorithm: Argon2id memory in KiB and iterations, scrypt N, r and p, bcrypt log rounds, PBKDF2 iterations by HMAC; a configuration meets the baseline when it reaches at least one row. Confirm the input is a password or another low-entropy secret. Validator question: **does this password hash run with a work factor below every baseline row for its algorithm?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-29`, severity major, `file`, `symbol`, `code` = the constructor or key-spec call quoted verbatim from the diff, `fix` = the same call with baseline parameters for its algorithm, `rationale` naming the parameter below baseline and the cost reduction per guess it grants an attacker).

## Source
OWASP Password Storage Cheat Sheet — "Use Argon2id with a minimum configuration of 19 MiB of memory, an iteration count of 2, and 1 degree of parallelism"; scrypt with N = 2^17, r = 8, p = 1 and the four equal-cost scrypt rows (2^16/8/2, 2^15/8/3, 2^14/8/5, 2^13/8/10, "a similar minimal level of defense"); bcrypt "work factor of 10 or more"; PBKDF2 "600,000 or more" with HMAC-SHA-256 (HMAC-SHA512: 220,000); the equal-cost Argon2id rows; a hash "should take less than one second". OWASP ASVS 5.0 §11.4.2 — passwords stored with an approved, computationally intensive key derivation function "with parameter settings configured based on current guidance". Spring Security reference, "Password Storage" — work factor tuned to about one second; `BCryptPasswordEncoder` default strength 10; `Argon2PasswordEncoder` and `Pbkdf2PasswordEncoder` sources for the `defaultsForSpringSecurity_v5_8` values.
