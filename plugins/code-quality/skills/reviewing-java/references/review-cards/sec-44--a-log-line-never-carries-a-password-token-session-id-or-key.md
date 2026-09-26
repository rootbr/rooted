---
title: A log line, MDC entry or exception message never carries a password, token, session id, key or card number; the value is omitted or masked
rule_id: SEC-44
domain: security
triggers: ['log(ger)?[.](trace|debug|info|warn|error)\(', 'MDC[.]put\(', '(?i)(password|passwd|secret|token|authorization|api[_-]?key|cookie|session[_-]?id|jwt|ssn|card[_-]?number)\b', 'getHeader\("(Authorization|Cookie)"\)', 'new \w*Exception\("[^"]*" \+']
scope: file
check_kind: semantic
severity_default: major
---

# A log line, MDC entry or exception message never carries a password, token, session id, key or card number; the value is omitted or masked

## Thesis
No logging call, MDC or structured-log field, `toString()` of a logged object, or message of an exception that will be logged carries a password, a session id, a bearer or refresh token, a JWT, a CSRF token, an API key, an encryption key, a database connection string with credentials, a full payment-card number or a government identifier; where a value is needed for correlation, a stable hash or its last four characters stands in.

## Rationale
Logs are copied to aggregators, retained for months, read by operators, and exposed by every incident that touches the logging pipeline; a credential written there is a credential stored in plaintext with wider access than the store it came from, and a session token in a log lets its reader take over the session for as long as it lives. The `Authorization` and `Cookie` headers, a request object with a password field and a default `toString()`, and an exception message built from the token ("invalid token abc…") are the common carriers. Masking or hashing keeps the correlation value without the secret.

## Example
```java
bad:  log.info("login attempt user={} password={}", req.getUsername(), req.getPassword());
      log.debug("headers: {}", request.getHeader("Authorization"));
      throw new IllegalArgumentException("invalid token " + token);
good: log.info("login attempt user={}", req.getUsername());
      log.debug("authorization scheme={}", scheme(request.getHeader("Authorization")));
      throw new IllegalArgumentException("invalid token (suffix " + last4(token) + ")");
```

## Limits
Applies to values that grant access or identify a person beyond what the audit trail needs. A username, a user id, a client id, a token's `jti` or expiry, and a hash of a session id for correlation are not flagged. A `debug` level is no protection: debug logging is switched on in production during incidents. A logging-framework converter that masks the field by name, named in the project context, is the tolerance. A test log is out of scope.

## Validator
On the triggered hunk find each log call, MDC put and exception construction, and follow each argument: a variable, field, getter or header whose name or origin marks it as a credential, token, key, session id or card number, or an object whose `toString()` (open its class or record in the file) includes such a field. Validator question: **does a secret, token, session id, key or card number reach a log line or an exception message that will be logged?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-44`, severity major, `file`, `symbol`, `code` = the log or exception line quoted verbatim from the diff, `fix` = the same line with the value omitted, masked or replaced by a correlation hash, `rationale` naming the secret and where the log carries it).

## Source
OWASP Logging Cheat Sheet, "Data to exclude" — session identification values, access tokens, authentication passwords, database connection strings, encryption keys and other primary secrets, bank account or payment card holder data, and sensitive personal data "should usually not be recorded directly in the logs, but instead should be removed, masked, sanitized, hashed, or encrypted". OWASP ASVS 5.0 §16.2.5 — certain data such as credentials or payment details may not be logged; session tokens only hashed or masked. CWE-532 — by id.
