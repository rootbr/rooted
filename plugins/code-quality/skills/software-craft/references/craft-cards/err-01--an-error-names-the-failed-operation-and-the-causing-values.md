---
title: An error raised, returned or wrapped at a failure site names the operation that failed and the values that caused it, without repeating what a wrapped error already says
rule_id: ERR-01
domain: errors
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['\b(raise|throw)\s+(new\s+)?[\w.]*(Error|Exception)\b', '\bnew\s+[\w.]*(Error|Exception)\s*\(', '\b(errors[.](New|Wrapf?)|fmt[.]Errorf)\(|&\w*Error\{', '\b(anyhow|bail|format_err)!\(|(?<![.\w])Err\(', '[.](context|with_context|map_err)\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# An error raised, returned or wrapped at a failure site names the operation that failed and the values that caused it, without repeating what a wrapped error already says

## Thesis
An error raised, returned or wrapped at a failure site carries, in its message or its fields, the information that led to it: the operation that failed, where the failing routine knows it, the operand values that caused the failure (a file name, an index, an id, the rejected input) and the caught error that triggered it, when there is one, so that it is useful when printed far from the call. A wrap adds only context the wrapped error lacks, and passes the error on unchanged when it has none to add.

## Rationale
An error is read where it surfaces — a log, a crash report, a handler several frames up — after the frame that held the operands is gone, so its message and fields are the only record of the values the failing code held, and, wherever the error is printed or logged without its stack trace, of the operation it was performing. `open /etc/passwx: no such file or directory` names the operation, the path and the system error that triggered it; the bare `no such file or directory` carries the system error alone, naming neither the operation nor the path. Where feasible, a prefix naming the operation or the module identifies the error's origin, and a structured field carries an operand that a caller must read programmatically. An empirical taxonomy of exception-handling faults in open-source projects lists an uninformative or wrong error message as a sub-case of its information-swallowed fault category. Context compounds along a chain of wraps: a layer that repeats the path the underlying error already names lengthens the message without informing, and an annotation that says only that something failed tells the caller nothing, since the presence of the error already conveys the failure.

## Example
```python
bad:  def parse_port(text):
          if not text.isdigit():
              raise ValueError("invalid input")
good: def parse_port(text):
          if not text.isdigit():
              raise ValueError(f"parse port: {text!r} is not a string of decimal digits")
```

## Limits
A wrap that returns or re-raises the error unchanged, because the underlying error already names the operation and the operand, follows the rule. A predeclared sentinel error compared by identity carries no per-call operand by design; the routine that receives it adds the operand when it wraps it, so any finding lies at that wrap. A low-level routine that cannot know which operation its caller performs names its operand and leaves the operation to the caller's wrap. A forced unwrap, which fails on a broken assumption rather than reporting a failure, lies outside this rule. A translation that hides the caught error on purpose where the code meets an external system, such as an RPC, IPC or storage interface, mapping it into a canonical error space, follows the rule; the new error still names the operation. A project may document an error convention, such as a catalogue of error codes or messages built inside the error type from its fields; an error that fills the convention's fields with the operands follows the rule, and the tolerance is the one the project context states. An operand that holds a secret or sensitive personal data, such as a key, a token, a password, a session id, a connection string, payment card data, a health record or a government identifier, may be named by its role rather than its value: error details reach log files, where such data is usually removed, masked or hashed rather than recorded directly, so leaving the value out follows the rule. The rule judges the error value: the wording of a log line that records it, whether a secret may enter it, and the translation of an internal error into the message an external consumer sees at a trust boundary, lie outside this rule. Whether a caught error travels with the new error as its cause, rather than only as text in its message, is judged by its own rule; this rule asks only that the message or fields name the operation and the operands.

## Validator
Grep the added lines for a created error (a raise or throw of an error type, a `new` error object, an error-constructor, error-format or error-macro call) and a wrap (an error re-raised with a chained cause, a context or map-error call, a format call that embeds a caught error). For each hit, read the hunk around it and list what the site holds: the operation the routine performs, the operand values the failing check tested (a path, an index, an id, the input) and the caught error, if there is one. Check whether the message, the error type or its fields carry that operation and those operands, and whether a caught error travels as the cause or inside the message. For a wrap, compare the added text with what the wrapped error already says: text that repeats it, or that says only that something failed or an error occurred, adds nothing. Skip a bare re-raise, an unchanged pass-through, a predeclared sentinel, a translation into a canonical error that hides the caught error at a system boundary such as an RPC, IPC or storage interface, a low-level routine that cannot know which operation its caller performs and names its operand, and an operand left out or masked because it holds a secret or sensitive personal data. Validator question: **Does an error created or wrapped on an added line leave out an operand or a caught cause the site holds, name no operation its routine knows, or add only a bare failure note or a repetition of the wrapped error?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-01`, severity minor, `file`, `symbol`, `code` = the added line that creates or wraps the error, verbatim from the diff, `fix` = the same statement carrying the operation, the operand values and the cause the site holds, with a redundant or bare annotation removed or the error passed on unchanged, in the file's language, `rationale` = which information is missing or repeated, and where a reader of the error would need it).

## Source
- Effective Go §Errors (golang/website `_content/doc/effective_go.html`) — "is useful even if printed far from the call that caused it"; "When feasible, error strings should identify their origin, such as by having a prefix naming the operation or package that generated the error" (fetched)
- Google Go Style Guide, Best Practices §Adding information to errors and §Error structure (google/styleguide `go/best-practices.md`) — "avoid redundant information that the underlying error already provides"; "Don't add an annotation if its sole purpose is to indicate a failure without adding new information"; at system boundaries, "including but not limited to RPC, IPC, and storage", a fresh error "hiding the specifics of the original error"; sentinel values are "perfectly adequate in many cases" (fetched)
- OWASP ASVS 5.0 V16.5.4 (Level 3) — "error details that must go to log files" (fetched)
- OWASP Logging Cheat Sheet §Data to exclude (OWASP/CheatSheetSeries `cheatsheets/Logging_Cheat_Sheet.md`) — "should usually not be recorded directly in the logs, but instead should be removed, masked, sanitized, hashed, or encrypted": "Session identification values", "Access tokens", "Sensitive personal data and some forms of personally identifiable information (PII)", "Authentication passwords", "Database connection strings", "Encryption keys and other primary secrets", "Bank account or payment card holder data" (fetched)
- SWEBOK Guide V3.0, Software Construction KA §4.5 — "including in the exception message all information that led to the exception" (relayed, community transcription)
- DOI 10.1109/SBES.2014.19 (SBES 2014), taxonomy of exception-handling faults in open-source projects — "Information swallowed" › "Uninformative or wrong error message" (relayed)
- Error Prone `UnusedException` (google/error-prone `docs/bugpattern/UnusedException.md`) — "Throwing a new exception without supplying the caught one as a cause means the stack trace will terminate at the `catch` block, which will make debugging a possible fault in `ioLogic()` far harder than is necessary."; "If the exception is deliberately unused, rename it `_` or `unused`" (fetched)
- Caveat: no source measures a defect rate or a cost for an uninformative message; the rule rests on a standard, official documentation and a fault taxonomy.
