---
title: A security-relevant random value comes from SecureRandom, never from java.util.Random, ThreadLocalRandom, Math.random or a name-based UUID
rule_id: SEC-31
domain: security
triggers: ['new Random\(', 'ThreadLocalRandom', 'Math[.]random\(', 'SplittableRandom', 'nameUUIDFromBytes\(', 'RandomStringUtils[.]', 'RandomGenerator[.]', 'setSeed\(']
scope: file
check_kind: mechanical
severity_default: major
---

# A security-relevant random value comes from SecureRandom, never from java.util.Random, ThreadLocalRandom, Math.random or a name-based UUID

## Thesis
A token, session or reset identifier, nonce, salt, IV, one-time code, CSRF token, API key or key material is generated from `java.security.SecureRandom` (or `UUID.randomUUID()`, which is backed by it) and never from `java.util.Random`, `ThreadLocalRandom`, `SplittableRandom`, `Math.random()`, a `RandomGenerator` selected by algorithm name, `RandomStringUtils.insecure()`, or `UUID.nameUUIDFromBytes`, which is a deterministic MD5 of its input.

## Rationale
`java.util.Random` uses a 48-bit seed modified by a linear congruential formula, its period is only 2^48, and its class documentation states that instances "are not cryptographically secure"; `ThreadLocalRandom` and the algorithmic `RandomGenerator` implementations carry the same note, and `Math.random()` is one shared `Random`. Output from such a generator can be guessed or predicted by an attacker who observes earlier output, so a password-reset token or session id drawn from it is guessable. `SecureRandom` "provides a cryptographically strong random number generator" whose output is non-deterministic and self-seeded from the platform's entropy source; that self-seeding is skipped when `setSeed` is called first, so a constant seed turns it into a predictable generator too. `UUID.randomUUID()` draws its 122 random bits from `SecureRandom`; `nameUUIDFromBytes` hashes its argument with MD5, so equal inputs give equal ids and the id is as guessable as the input.

## Example
```java
bad:  byte[] token = new byte[32];
      new Random().nextBytes(token);
      String reset = UUID.nameUUIDFromBytes(email.getBytes(UTF_8)).toString();
good: byte[] token = new byte[32];
      new SecureRandom().nextBytes(token);
      String reset = UUID.randomUUID().toString();
```

## Limits
Applies to a value whose unpredictability is a security property. Randomness for shuffling, sampling, jitter, backoff, load balancing, test data or simulation is not flagged. `UUID.randomUUID()` is accepted; a token that must carry at least 128 bits of entropy draws 16 or more bytes from `SecureRandom` directly, since a version-4 UUID carries 122. A `SecureRandom` whose `setSeed` is called after first use adds entropy and is fine; one seeded with a constant before first use is the same defect as `Random`. `RandomStringUtils.secure()` and the class's static methods since commons-lang 3.16 use `SecureRandom`; `insecure()` and older static methods do not.

## Validator
On the triggered hunk find each `new Random`, `ThreadLocalRandom.current()`, `Math.random()`, `SplittableRandom`, `RandomGenerator.of`, non-secure `RandomStringUtils`, `nameUUIDFromBytes` or `setSeed` call. Open the file to follow the value: a token, nonce, salt, IV, one-time code, key, session or reset id, or a string returned to a client as a credential, is security-relevant. Validator question: **does a value that must be unguessable come from a generator other than `SecureRandom`, or from a `SecureRandom` seeded with a constant before use?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-31`, severity major, `file`, `symbol`, `code` = the generator construction or call quoted verbatim from the diff, `fix` = the same value drawn from `SecureRandom` (or `UUID.randomUUID()`), `rationale` naming the predictable generator and the value it makes guessable).

## Source
`java.util.Random` class Javadoc, Java SE 21 — "its period is only 2^48. The class uses a 48-bit seed, which is modified using a linear congruential formula"; "Instances of java.util.Random are not cryptographically secure. Consider instead using java.security.SecureRandom". `java.util.concurrent.ThreadLocalRandom` — the same note. `java.util.random.RandomGenerator` interface Javadoc — "Objects that implement RandomGenerator are typically not cryptographically secure. Consider instead using SecureRandom"; `java.util.SplittableRandom` class Javadoc — "Instances of SplittableRandom are not cryptographically secure". `java.security.SecureRandom` class Javadoc — "a cryptographically strong random number generator", non-deterministic output per RFC 4086, and "This self-seeding will not occur if setSeed was previously called". `java.util.UUID#randomUUID` — "generated using a cryptographically strong pseudo random number generator"; `#nameUUIDFromBytes` — a type 3 (name-based) UUID, computed with MD5 in the reference implementation. OWASP Cryptographic Storage Cheat Sheet, "Secure Random Number Generation" — Java unsafe: `Math.random()`, `java.util.Random`, `SplittableRandom`, `ThreadLocalRandom`; secure: `SecureRandom`, `UUID.randomUUID()`. OWASP ASVS 5.0 §11.5.1 — non-guessable values from a CSPRNG with at least 128 bits of entropy, which a UUID does not meet. SEI CERT MSC02-J and CWE-330 — by id.
