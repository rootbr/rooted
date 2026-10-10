---
title: Secrets stay out of source code, tests, build artifacts and version control, and tests use designated fake secrets
rule_id: INP-10
domain: input
step: [implement, test]
applies_to: [universal]
triggers: ['(?i)\b\w*(pass(word|wd|phrase)?|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key|(encryption|signing|hmac|jwt|aes)[_-]?key|client[_-]?secret|credential)\w*["'']?\s*(:\s*&?(''static\s+)?[\w.]+\s*)?(:=|=|:)\s*(\[\]byte\(|b)?["''][^"''\s]{8,}["'']', '-----BEGIN ([A-Z]+ )?PRIVATE KEY-----', '\b(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]{10,}|sk_live_[0-9a-zA-Z]{24,}|AIza[0-9A-Za-z_-]{35})\b', '(?i)\b[a-z][a-z0-9+.-]*://[^/\s:@"'']+:[^/\s@"''$<{]+@[\w.-]+', '(?i)\b[\w.-]*(pass(word|wd|phrase)?|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key|credential)[\w.-]*\s*[=:]\s*[^;"''\s$<{}(),]{3,}(;|\s*$)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# Secrets stay out of source code, tests, build artifacts and version control, and tests use designated fake secrets

## Thesis
Every live secret a change handles, whether a password, an API key, a token, private key material or a credential inside a connection string, stays out of source code, test code, build artifacts and every file committed to version control; a test that needs a secret uses a fake value, the one designated for that secret type where the project has one; and a live secret that has reached a commit is revoked or rotated.

## Rationale
A secret in source code or in a binary is easy for an attacker to extract, especially in distributed or open-source applications: anyone with access to compiled classes can decompile them and discover it, and changing a hard-coded password in a deployed program may require distributing a patch. Leakage through public repositories is pervasive: a nearly six-month scan of real-time public commits plus a snapshot of 13% of open-source repositories, limited to private key files and 11 platforms with distinctive API key formats, found leakage affecting over 100,000 repositories and thousands of new, unique secrets leaked every day. Inspecting newly uploaded public code files for 75 days found password leakage affecting over sixty thousand repositories. Discovery is near immediate: in the study's own experiment, its search-API collector discovered secrets with a median time to discovery of 20 seconds, ranging from half a second to over 4 minutes. Removing the secret afterwards does not withdraw it: adversaries who monitor commits in real time can discover leaked secrets even if they are naively removed, and even with commit history rewritten the full contents of deleted commits could be recovered from the hosting service with only the commit's SHA-1 ID. Hard-coded secrets also persist: static analysis of 15,232 infrastructure-as-code scripts from 293 open-source repositories found 1,326 hard-coded passwords, and a hard-coded secret could persist for as long as 98 months, with a median lifetime of 20 months. A secret exposed in source code is rotated immediately, and an exposed key is revoked so that it is de-authorized. One standard fake value per secret type, used across the organization, lets secret detection track a single test secret for each type and so reduces false positives.

## Example
```go
bad:  const apiToken = "q8Vz3LmT7wXr2NpK"
      dsn := "postgres://app:Pr0dPassw0rd@db.internal/orders"
      awsKeyID := "AKIA3QZ7TXW5RMPL2KDE"
      conn := "Server=db.internal;User Id=app;Password=Pr0dPassw0rd;"
      pemKey := "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0B..."
good: func NewClient(apiToken, dsn string) *Client {
          return &Client{token: apiToken, dsn: dsn}
      }
      // test code: the organization's one designated fake value per secret type
      const fakeAPIToken = "FAKE-API-TOKEN-FOR-TESTS"
```

## Limits
A trigger match is a candidate, not a finding: of 97,479 candidate secrets extracted from 818 public repositories selected with 761 regular-expression patterns, manual inspection of each value in its source-code context labeled 15,084 as true secrets, and name-based hard-coded-password checks are documented as noisy and prone to false positives. Patterns also miss secrets: approaches built for secrets with distinctive formats let textual passwords fall through the crack, and a naive regular-expression scheme detects them poorly. Detectors scoped to main code leave test code unchecked by those rules, since two hard-coded-secret rules are scoped to main code only and one scanner's documentation shows its hard-coded-credential rule excluded for a test/ path; test code is source code all the same, and there a fake value, the designated one where the project has one, is the compliant form. Where the live value comes from at run time is outside the rule, and the sources differ on it: one lists a configuration file that is not committed to the code repository, a database or a cloud provider's secrets management service, while another advises against configuration files and environment variables and for a secrets vault. A secret stored encrypted in version control is a documented option when developers cannot decrypt it, each environment's secret is different and encrypted with another key, and only the designated consumer in that environment can decrypt it; under those conditions the encrypted value is outside the rule.

## Validator
Grep the added lines for a string literal assigned to a name containing password, secret, token, key or credential, for a private-key header, for a provider key prefix, and for a URL or connection string that carries a user and a password. For each hit, open the file at hunk scope and read the value in its context: a placeholder, an empty or obviously dummy string, the project's designated fake value for that secret type, a value encrypted so that developers cannot decrypt it and only its designated consumer can, or a value read at run time is not a live secret. Where the name and value leave it open, the literal's use within the hunk, such as an authorization header, a database connection, a client constructor or a signing call, decides whether it is a credential. Validator question: **Does the hunk add to source code, test code or a committed file a literal that its value and context show to be a real credential rather than a designated fake value, a placeholder or a value only its designated consumer can decrypt?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-10`, severity major, `file`, `symbol`, `code` = the added line that holds the literal, verbatim except the secret value masked, `fix` = the literal replaced by a parameter or by the lookup the project already uses for configuration, in the file's language, and the designated fake value in test code, `rationale` = names the secret type, that anyone who can read the repository or the artifact can extract it, and that the committed value is revoked or rotated).
