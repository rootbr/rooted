---
title: A log record holds no password, key, access token, connection string, payment data or sensitive personal data in clear text, and a session identifier only hashed or masked
rule_id: INP-26
domain: input
step: [implement]
applies_to: [universal]
triggers: ['(?i)(\b(log|logger|logging|slog|klog|console|tracing|zap|logrus|log4j)(::|[.])\w+!?|\b(trace|debug|info|warn|error)!)\(.*\b\w*(pass(word|wd|phrase)?|secret|token|api_?key|private_?key|credential|session_?id|ssn|card_?num(ber)?|conn(ection)?_?str(ing)?)\w*', '\b(print|println|log\w*|logger[.]\w+|logging[.]\w+|console[.]\w+|fmt[.]Print\w*)\(.*\b(os[.]environ\s*\)|process[.]env\s*\)|System[.]getenv\(\s*\)|os[.]Environ\(\))']
scope: file
check_kind: semantic
severity_default: major
---

# A log record holds no password, key, access token, connection string, payment data or sensitive personal data in clear text, and a session identifier only hashed or masked

## Thesis
A log statement the change adds or changes leaves out, masks, hashes or encrypts each authentication password, encryption key or other primary secret, access token, database connection string, bank account or payment card holder datum, and each sensitive personal datum such as health data or a government identifier, and it records a session identifier only hashed or masked, in full or in part.

## Rationale
A secret or personal datum written to a log entry could be exposed to an attacker who gains access to the logs, and logging it raises concerns over the privacy of the stakeholders, legal limits on collecting personal information and data exposure by insiders. The duty holds after the value has been read: an application must avoid logging a secret in the clear whether it arrived through an environment variable or a mounted volume. A build platform's automatic redaction of secrets in its workflow logs is not guaranteed: a secret value can be transformed in multiple ways, and because redaction largely relies on an exact match for the value, structured data around a secret can make it fail. Mobile app logs frequently expose personally identifiable information due to inattentive logging practices: across 3,885 Android apps, runtime analysis found such leakage in 233 apps (approximately 6%), 7,485 violations in all, and static analysis of 300,073 log statements across 3,994 apps identified 1,788 potential log-based leaks of such information in 932 apps and 97 distinct libraries. A type that controls how its values appear in logs can redact secret information such as passwords wherever a value of that type is logged.

## Example
```typescript
bad:  logger.debug(`calling api with key ${apiKey}`);
      console.log(process.env);
good: logger.debug({ key: mask(apiKey) }, "calling api");
      logger.debug({ envKeys: Object.keys(process.env) }, "environment read");
```

## Limits
Some data, such as access times, can be safely logged. The exclusion list is hedged as what should usually not be recorded directly, and further personal data, such as user names, email addresses or IP addresses, is logged according to the data's protection level as the application's logging policy sets it, some of it only to a log file restricted to particular administrators; the rule flags the named categories in clear text and defers to that policy on the rest. The sources part on whether a password or payment card data may enter a record masked, hashed or encrypted: one lists masking, hashing and encryption as remedies for every named category, while others say a password is not logged at all and a credit card number only in encrypted form, and give credentials and payment details as data that may not be logged; the rule flags the clear-text form, on which they agree, and its fix leaves a password, other credential or payment datum out. Which channel supplies a secret at run time, an environment variable or a mounted volume, is outside the rule, which applies once the value has been read; so is restricting who may read the log file. How a value from another trust zone is encoded before it is logged is a separate rule's matter.

## Validator
Grep the hunk for log, logger, console, print and tracing calls whose arguments name a password, passphrase, secret, token, API or private key, credential, session identifier, connection string, card number or government identifier, and for calls that write a dump of the environment. Open the file and trace each such argument to its origin: a named secret or sensitive personal datum. Check whether the call leaves it out, masks, hashes or encrypts it, and for a session identifier whether it is left out, hashed or masked, or whether its type redacts itself when logged. Validator question: **Does a log statement the hunk adds or changes write a named secret or sensitive personal datum in clear text, or a session identifier neither hashed nor masked?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-26`, severity major, `file`, `symbol`, `code` = the log statement and the argument carrying the secret or personal datum, quoted verbatim from the diff, `fix` = the statement with a password, other credential or payment datum left out and any other secret or sensitive personal datum left out, masked or hashed, in the file's language, `rationale` = the category of the logged value and the exposure that follows).
