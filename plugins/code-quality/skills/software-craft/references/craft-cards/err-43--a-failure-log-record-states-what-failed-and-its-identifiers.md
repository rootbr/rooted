---
title: A log record of a failure states what failed as the code detected it and carries the identifiers and values needed to diagnose it, without asserting a cause the code has not checked
rule_id: ERR-43
domain: errors
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['(?i)(\b(log|logger|logging|slog|klog|console)[.](error|warn|warning|exception|critical|fatal|severe)\w*|\b(error|warn)!)\(\s*[`"'']([^`"''%{}$]*[`"'']\s*\)|(something went wrong|an error (has )?occurred|error|failed|failure|oops|unexpected error)[.!]?[`"''])', '(?i)(\b(log|logger|logging|slog|klog|console)[.](error|warn|warning|exception|critical|fatal|severe)\w*|\b(error|warn)!)\(\s*f?[`"''][^`"'']*\b(already|because|due to|probably|likely|must have|does ?n[o'']t exist|not found|missing|no such)\b']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A log record of a failure states what failed as the code detected it and carries the identifiers and values needed to diagnose it, without asserting a cause the code has not checked

## Thesis
A log record written for a failure clearly expresses what went wrong: it names the operation that failed and the object it failed on, and it carries the identifiers and the run-time values causally related to the failure that a maintainer needs to diagnose it, each interpolated value clearly identifiable as such in the text. Its message precisely matches the condition the code detected and states no cause the code has not checked. Identifiers that every record of one request or interaction shares, such as the request's URL or trace identifier, may come from a logger constructed to carry them, so that no single call need repeat them.

## Rationale
In many cases log messages are the only data available to diagnose a reported failure: an engineer maps the message's content back to the source statements and works backwards to infer what conditions might have led to the failure. An error message that simply reads "system failed" gives that work no further context; the key problem with existing log messages is that they contain too little information. Developers often do not get a log message right at the first attempt and spend significant effort revising it afterwards: in four large open-source systems, one fourth (27%) of log modifications were to variable logging and the majority (62%) of those added new variables causally related to the log message, a sign that developers often need additional run-time information to understand how a failure occurred; a study of 21 further open-source projects also found 27% of after-thought logging changes related to variable logging, and one web server's more than 900 error messages received 5,409 patches over five years to improve their fidelity. A message that does not match the condition the code detected can mislead: a warning that a directory was already deleted, written when its removal failed, makes an assumption that might not be true, since the removal might have failed for some other reason, and misleads whoever has to debug the failure; in the four systems, more than one third (39%) of the modifications to the static text of log messages fixed inconsistency between the logs and the actual execution information they were meant to record. A value spliced into the text without a marker leaves the message confusing for some values — a directory named "deleted" turns a warning into "The deleted directory could not be deleted." — and harder to grep for than necessary, while an error message should allow simple automated processing such as grepping. An interaction identifier links all the events of a single interaction, such as a web page request or a web service call, so the link is recorded rather than lost and left for later correlation to reconstruct; a logger built with such attributes adds them to the output of every call.

## Example
```java
bad:  try { Files.delete(dir); }
      catch (IOException e) { log.warn("Directory was already deleted"); }
good: try { Files.delete(dir); }
      catch (IOException e) { log.warn("Could not delete directory '{}'", dir, e); }
```

## Limits
A cause the code has checked, such as an error kind it tested or a condition it evaluated before logging, may be stated, since the message then matches the actual error condition; the error the code caught or received may be named as the reason, as in a warning that a directory could not be removed with the error given as its reason. An identifier the logger was built to carry for every record of the request or interaction counts as carried, and its absence from the message text is no finding. Some variables should not be logged, considering security and privacy concerns; a value left out of the record for that reason is no finding, and which values those are is judged by its own rule. A record of an event that is not a failure is outside the rule; whether a failure warrants a record, at which level, whether the record carries the error object with its stack trace, at which layer it is written and whether its values go in structured fields are judged by their own rules.

## Validator
Grep the added lines for log calls at warning level or above and for log calls inside a catch, except or error-check block or an error branch. For each, read the hunk around the call: what the code detected — the condition it tested, the error it caught or received — which operation failed, and which identifiers and values that operation was working on are in scope. Read the message and its arguments: whether they name the failed operation and the object it failed on, carry the in-scope identifiers and values the failure depends on, mark each interpolated value apart from the text (quotes, a key, a placeholder after a colon), and state as the cause only what the code checked or the error it received. Check how the logger in the hunk was obtained; identifiers it was built with count as carried. Set aside a record of an event that is not a failure and a value left out because it is a secret or a personal datum. Validator question: **Does an added log record of a failure leave out the operation that failed, the identifier of what it failed on or the in-scope values that drove the failing step, splice a value into the text without marking it, or state a cause the code did not check?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-43`, severity minor, `file`, `symbol`, `code` = the added log call quoted verbatim from the diff, `fix` = the same call with a message that names the failed operation and the object, carries the in-scope identifiers and values as marked placeholders or keyed arguments and states only the condition the code detected, in the file's language, `rationale` = what the record leaves out or asserts without a check, and what a maintainer reading only the log could not tell or would be misled into).
