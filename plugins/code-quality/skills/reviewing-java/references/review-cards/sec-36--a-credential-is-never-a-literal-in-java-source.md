---
title: A credential is read from configuration or a secrets store, never written as a literal in Java source
rule_id: SEC-36
domain: security
triggers: ['(?i)(password|passwd|pwd|secret|api[_-]?key|apikey|token|client[_-]?secret|private[_-]?key)\s*=\s*"[^"]{4,}"', 'jdbc:[a-z0-9]+://[^"]*:[^"]*@', 'AKIA[0-9A-Z]{16}', '-----BEGIN [A-Z ]*PRIVATE KEY-----', '\{noop\}', 'withDefaultPasswordEncoder\(', '(?i)(password|secret|token)\("[^"]{4,}"\)', 'Basic [A-Za-z0-9+/=]{16,}']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A credential is read from configuration or a secrets store, never written as a literal in Java source

## Thesis
A password, API key, bearer or OAuth client secret, signing key, private key, or a JDBC or broker URL with an embedded `user:password@`, is obtained at runtime from configuration (`@Value("${…}")`, `Environment`, a `@ConfigurationProperties` bean), the process environment or a secrets manager; the Java source, tests included, other than a fixture-only value, carries no such value as a string literal or as the default of a placeholder.

## Rationale
A literal in source is in every clone, build artefact and fork and in the whole history of the repository, readable by anyone with read access to any of them and by every tool that scans them; removing it later requires rotating the credential, because the old value stays in the object store. The same literal in a test class ships in the test jar and is reused against real systems whenever the test's target is production-like. A value injected at runtime exists only in the process that needs it, rotates without a code change, and leaves the source free of secrets to scan for.

## Example
```java
bad:  private static final String DB_URL = "jdbc:postgresql://app:hunter2@db/app";
      String apiKey = "sk_live_51H8f3kL9pQ2rS7tUvWxYz";
good: @Value("${db.url}") private String dbUrl;               // credentials arrive from config
      String apiKey = env.getRequiredProperty("payments.api-key");
```

## Limits
Applies to a value that authenticates to something. An obvious placeholder (`"changeme"`, `"<your-key>"`, a repeated character), a test-only credential for an in-memory or containerised fixture that exists only within the test run, a public key or certificate, and a digest used as a test vector are out of scope. A default password in a local-development profile that the project context documents is a tolerance. A literal that names a property key (`"db.password"`) rather than a value is not a secret.

## Validator
On the triggered hunk find each string literal assigned to or passed for a field or parameter whose name says password, secret, key, token or credential, each URL with `user:password@`, and each value whose shape marks it (an `AKIA…` access key, a PEM private-key block, a `Basic` or `Bearer` header value). Decide whether the value is real: a placeholder or fixture-only value is not; a value with the entropy and shape of a live credential, or one a comment or hostname ties to a real system, is. Validator question: **does this literal authenticate to a real system?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-36`, severity major, `file`, `symbol`, `code` = the literal's line quoted verbatim from the diff with the secret value replaced by `…`, `fix` = the same field read from configuration or the environment, `rationale` naming the system the credential opens and the rotation the leak now requires).

## Source
OWASP ASVS 5.0 §13.3.1 — a secrets management solution stores backend secrets; "Secrets must not be included in application source code or included in build artifacts". OWASP Secrets Management Cheat Sheet — §1, secrets "hardcoded within the source code in plaintext" as the problem addressed; §3.2, a CI/CD secret store "is not the same as committing it to code"; §2.7.3, a secret found in code persists in commit history unless the history is rewritten. Spring Security reference, "Password Storage" — a password placed in source through `withDefaultPasswordEncoder` "is still exposed in memory and in the compiled source code" and "not considered secure for a production environment". CWE-798 — by id.
