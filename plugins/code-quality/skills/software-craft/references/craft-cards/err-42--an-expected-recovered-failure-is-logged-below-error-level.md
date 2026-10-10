---
title: A failure the code expects and recovers from is logged below error level, and error level is kept for a failure the code did not handle or recover from
rule_id: ERR-42
domain: errors
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['\berror!\(|\bconsole[.]error\(|(?i:\b\w*log\w*[.](error|severe|critical|exception)\w*\(|[.]at(error|severe)\(|\b(level|logging)[.:]*(error|severe|critical)\b)']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A failure the code expects and recovers from is logged below error level, and error level is kept for a failure the code did not handle or recover from

## Thesis
A log record's level follows the failure's expected impact, not the bare presence of an exception or an error value. A failure the code expects and meets with the recovery it was written for, so that the software is still working as expected — a connection attempt to a remote service that times out, a write to a file that fails with an I/O error, each met by the retry or the fallback the code provides — is recorded below error level: at warning, or at info, a level application code may also use for an exception it records, and at debug when the failure indicates no actual issue, such as a request the client cancelled. Error level is kept for the failures the code does not recover from as designed, among them a failure that application code did not handle and that does not shut the application down, such as an exception that reaches a server's top-level error handler, which suppresses it without raising it; a message at error level is then actionable, rather than more serious than a warning.

## Rationale
A record at error level or above indicates an erroneous situation, and its reader decides what to do with that: a viewer may show such records in a different colour or find all of them together. An error-level message is meant to be actionable, rather than more serious than a warning. Warning marks an event in which something unexpected happened while the software is still working as expected; error marks a problem with which the software has not been able to perform some function. A failure met by the recovery the code was written for leaves the software working as expected, so a record of it at error level presents a handled condition as an erroneous situation that calls for action. The conventions for exceptions in log records grade the level by the failure's expected impact: an exception application code is expected to handle at warning, severity number 13; one that application code did not handle, short of shutting the application down, at error, 17; one that indicates no actual issue at debug, 5; and application code may use info, 9, for an exception it records. Warning keeps the record in view: a facility whose default level is warning tracks events of that severity and higher. An error-level record can also cost more to write: in one documented facility, error-level logging causes a flush and is more expensive than lower levels, which can have a serious performance impact.

## Example
```rust
bad:  if let Err(e) = send(&batch) {
          error!("batch {} not sent, queued for retry: {e}", batch.id);
          retry_queue.push_back(batch);
      }
good: if let Err(e) = send(&batch) {
          warn!("batch {} not sent, queued for retry: {e}", batch.id);
          retry_queue.push_back(batch);
      }
```

## Limits
The level of a failure the code handles is contested. One position reads a level as the seriousness of what went wrong: error level means that something went wrong, and an error the code suppresses without raising it is reported at error level or above. The condition that separates the cases is whether the failure is expected and met by the recovery the code was written for, with the software still working as expected. The suppression that position places at error has as its example the error handler of a long-running server process, the catch-all point at which the conventions for exceptions also place error; the documentation that gives that example defines, in its table of levels, warning as an unexpected event after which the software is still working as expected and error as a problem that leaves some function unperformed; and another facility's documentation places at warning abnormal or unexpected events, typically including errors or conditions that do not cause the application to fail, and at error the errors and exceptions that cannot be handled, a failure in the current operation or request rather than of the whole application. A failure the code expects but does not recover from, so that the function it was performing is given up, such as a call that still fails after its last retry, lies outside the rule: the conventions for exceptions record a client library call that fails after exhausting its retries at warning, while the level table that defines error as a problem with which the software has not been able to perform some function fits it to error. Where the facility has no warning level and offers info and error only, info is the level below error, and application code may use info for an exception it records. A failure that shuts the application down is recorded at fatal, severity number 21, and its level lies outside the rule. The rule judges a record the code writes where it handles a failure without passing it on; whether to record a failure the code returns or raises, and what the record says, lie outside it. Severity is set by the context in which the failure occurs, so a level policy the project documents for its domain governs which failures it treats as expected; the tolerance is the one the project context states.

## Validator
Grep the added lines for a log call at error level or above: a logger or console method named error, exception, critical or severe, an error-level macro, a fluent call that selects the error or severe level, or a log call that takes an error, severe or critical level as an argument. Skip a fatal-level call that stops the process. For each call, read the hunk around it, name the failure the call records, and trace what the code does with the failure after the call. Treat the failure as expected when the handler names it — a timeout, a refused or reset connection, an I/O error, a resource that is busy or not found — or when the surrounding code or its comments treat it as part of normal operation. Skip the call when the code raises, returns or rethrows the failure; when the code gives up the function it was performing, such as a call that still fails after its last retry; when the handler catches every failure at the top of a request, task, message or process and only records it; when nothing in the hunk shows the failure to be expected; and when a level policy the project documents assigns the level. Flag the call when the failure is expected and the code meets it with the recovery it was written for — a retry, a re-queue, a fallback to another source or to a default — after which the software is still working as expected. Validator question: **Does an added log call record, at error level or above, a failure the code expects and recovers from by design, so that the software is still working as expected?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-42`, severity minor, `file`, `symbol`, `code` = the added error-level log call, verbatim from the diff, `fix` = the same call at warning, or at info where the facility has no warning level, or at debug when the failure indicates no actual issue, in the file's language, `rationale` = the expected failure the call records, the recovery that already handles it, and that an error-level record presents this handled condition as an erroneous situation calling for action).
