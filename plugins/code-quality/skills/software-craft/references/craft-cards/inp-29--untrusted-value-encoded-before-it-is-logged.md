---
title: A value from another trust zone reaches a log record through an encoding or a sanitizer that keeps line breaks and delimiters from forging or splitting a record, and a malformed field of a security event is replaced with the failure recorded
rule_id: INP-29
domain: input
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['(?i)\b(log|logger|logging|slog|console)[.](trace|debug|info|warn|warning|error|critical|fatal|severe|print\w*)\(.*\b(request|req|params|getParameter|getHeader|query|headers|form|body|user_?input)\b', '(?i)\b(log|logger|logging|slog|console)[.]\w+\(\s*(f["'']|["''][^"'']*["'']\s*(\+|%\s*[\w(])|`[^`]*\$\{)']
scope: file
check_kind: semantic
severity_default: major
---

# A value from another trust zone reaches a log record through an encoding or a sanitizer that keeps line breaks and delimiters from forging or splitting a record, and a malformed field of a security event is replaced with the failure recorded

## Thesis
A value from another trust zone reaches the log record through a logging component that encodes it for the output format, or through a sanitizer at the call, so that carriage return, line feed and the format's delimiter characters cannot split a legitimate entry in two or insert a fake one. For a security event, a malformed field from another trust zone is omitted or safely replaced and the validation failure recorded, and the event itself is still logged.

## Rationale
A log message built from external input without neutralizing special elements lets an attacker insert fake log data and deceive administrators about the system's behaviour; a carriage return and line feed sequence can split one legitimate entry into two to mislead an auditor. Encoding log data correctly for its format prevents injections or attacks on the logging and monitoring systems, and user input in an entry displayed as HTML should be HTML-encoded before it is logged, to prevent forgery and other HTML injection. Encoding inside the logging component covers every call at once: a sanitizing logger saves the developer from having to worry about unsanitized messages, and a structured text handler that quotes any value containing a Unicode space character, a non-printing character, a double quote or an equals sign writes control characters as escape sequences, so a line feed stays inside one quoted value. Omitting or replacing only the malformed field, rather than discarding the security event, preserves the evidence the event carries.

## Example
```typescript
bad:  console.info(`login failed user=${req.body.user}`); // a CR LF in the name starts a forged line
good: logger.info({ user: req.body.user }, "login failed"); // JSON output escapes CR and LF
```

## Limits
The encoding duty covers values built from external input or taken from another trust zone; a value the program itself produces is outside it. A call that hands the value to a logging component already configured to encode or strip CR, LF and the format's delimiters for all message events satisfies the rule without a sanitizer at the call. Which secrets and personal data a record may hold is a separate rule's matter, and so is restricting who may read the log file.

## Validator
Grep the hunk for log, logger, console, print and tracing calls that interpolate or concatenate request parameters, headers, form fields, bodies or other values from outside the trust boundary. Open the file and trace each such argument to its origin. For an untrusted value, check the logger's configuration in the file and its imports for a handler or layout that encodes values for the output format, and otherwise the call for a sanitizer that neutralizes CR, LF and the format's delimiters. Where the hunk validates such a value on the path of a security event, check that a malformed value is omitted or replaced and the validation failure recorded while the event is still logged. Validator question: **Does a log statement the hunk adds or changes write a value from outside the trust boundary through a path where neither the logging component nor the call encodes or strips CR, LF and the format's delimiters, or, for a security event, does the hunk drop the event because such a value is malformed, or omit or replace that value without recording the validation failure?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-29`, severity major, `file`, `symbol`, `code` = the log statement and the argument carrying the untrusted value, quoted verbatim from the diff, `fix` = the untrusted value passed as a field to an encoding logger or through a sanitizer, or the dropped security event logged with the malformed field replaced and the validation failure recorded, in the file's language, `rationale` = the value's untrusted origin and the record forgery or evidence loss that follows).

## Source
- OWASP Logging Cheat Sheet, §Event collection (fetched): "Validate event data from other trust zones before logging it. If a field is malformed, omit or safely replace that field and record the validation failure with bounded, safe context; do not discard the entire security event. This preserves evidence"; "Perform sanitization on all event data to prevent log injection attacks e.g. carriage return (CR), line feed (LF) and delimiter characters"; "Encode data correctly for the output (logged) format".
- OWASP ASVS 5.0 V16, 16.4.1, Level 2 (fetched): "Verify that all logging components appropriately encode data to prevent log injection."
- OWASP Top 10:2025 A09 Security Logging and Alerting Failures (fetched): "logging sensitive information that should not be logged (such as PII or PHI)"; "Ensure log data is encoded correctly to prevent injections or attacks on the logging or monitoring systems."
- CWE-117 Improper Output Neutralization for Logs (fetched): "The product constructs a log message from external input, but it does not neutralize or incorrectly neutralizes special elements when the message is written to a log file."
- SEI CERT IDS03-J (fetched): "A malicious user can insert fake log data and consequently deceive system administrators as to the system's behavior"; "an attacker might split a legitimate log entry into two log entries by entering a carriage return and line feed (CRLF) sequence to mislead an auditor"; "A sanitized logger saves the developer from having to worry about unsanitized log messages."
- CodeQL java/log-injection, Recommendation (fetched): "If the log entries are plain text then line breaks should be removed from user input"; "For log entries that will be displayed in HTML, user input should be HTML encoded before being logged, to prevent forgery and other forms of HTML injection".
- find-sec-bugs CRLF_INJECTION_LOGS, Solution (fetched): "You can manually sanitize each parameter. ... You can also configure your logger service to replace new line for all message events."
- Go log/slog, TextHandler.Handle and doc.go (fetched): "Keys and values are quoted with [strconv.Quote] if they contain Unicode space characters, non-printing characters, '\"' or '='"; "If a type implements the [LogValuer] interface ... you can redact secret information like passwords"; strconv.Quote (fetched): "uses Go escape sequences (\t, \n, ...) for control characters and non-printable characters".
