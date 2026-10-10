---
title: An unexpected or security-sensitive error that crosses a trust boundary reaches the consumer as a generic message with no stack trace, exception message or type, query, key or token, while its details are logged on the server
rule_id: INP-27
domain: input
step: [handle-errors, implement]
applies_to: [service-boundary]
triggers: ['(?i)\b(http[.]Error|(res|resp|response|reply|ctx|c|w|writer)[.](send|json|write|end|body|status\(\s*\d+\s*\)[.](send|json))\w*|jsonify|JsonResponse|HttpResponse|Response|HTTPException|JSONResponse|PlainTextResponse|abort|body)\(.*(\b(str|repr)\(\s*(e|ex|exc|err|error)\s*\)|\b(e|ex|exc|err|error|exception)[.](message\b|stack\b|StackTrace\b|getMessage\(\)|getLocalizedMessage\(\)|getStackTrace\(\)|Error\(\)|toString\(\))|\b(traceback[.]format_exc|traceback[.]format_exception|debug[.]Stack|ExceptionUtils[.]getStackTrace)\()|[.]printStackTrace\(\s*[^)\s]|\binclude[-_.]?(stacktrace|message|exception|binding[-_]?errors)"?\s*[:=]\s*\W?(\w+[.])?(always|on[-_]param|true)\b|\bUseDeveloperExceptionPage\(|InternalServerError|INTERNAL_SERVER_ERROR|\b(status|statuscode|status_code|sendStatus|abort)\s*\W\s*500\b']
scope: file
check_kind: semantic
severity_default: major
---

# An unexpected or security-sensitive error that crosses a trust boundary reaches the consumer as a generic message with no stack trace, exception message or type, query, key or token, while its details are logged on the server

## Thesis
Where an unexpected or security-sensitive error crosses a trust boundary, such as an HTTP, RPC or API response or an error page shown to the user, the consumer receives a generic message, and the response carries none of the error's stack trace, exception message text, exception type, query, server-side file name, secret key or token. The error's details are logged on the server for investigation, typically by one global or last-resort handler that catches every unhandled error, so the generic message replaces only what the consumer sees and the error details are not lost.

## Rationale
Error detail returned to the consumer is reconnaissance: if an attack fails, the attacker may use the error information the server provides to launch another, more focused attack. An SQL injection attempt might not succeed at first, yet an error message could reveal the malformed query, which would expose the query logic and possibly passwords used within it; the message at the top of a stack trace can include server-side file names and SQL code, and the sequence of class names in the trace can reveal the structure of the application and the internal components it relies on. Both the exception's message text and its type can leak information: a file-not-found message reveals information about the file system layout, and the exception type reveals that the requested file is absent, so both are filtered wherever an exception can propagate across a trust boundary. Logging the details only on the server keeps them available to developers in the error log while remote users do not see them. A last-resort handler serves two ends: it avoids losing error details that must go to log files, and it keeps one error from taking down the entire application process.

## Example
```go
bad:  if err != nil {
          http.Error(w, err.Error(), http.StatusInternalServerError)
          return
      }
good: if err != nil {
          log.Printf("load record: %v", err)
          http.Error(w, "internal error", http.StatusInternalServerError)
          return
      }
```

## Limits
The rule covers the unexpected or security-sensitive error. An expected error the caller can resolve is outside that scope; its message should help a reasonably technical user understand and resolve the issue, and must not assume the user knows anything about the underlying implementation. The generic message carries the minimal detail useful to its intended audience, striking the balance between too cryptic, which confuses users, and too detailed, which reveals more than intended. Where the language has no exceptions or last-resort handler, a pattern suited to the language or framework should ensure that exceptional, unexpected or security-related events are handled securely. A framework whose default error response already omits the stack trace and the message complies, and the check is then that no code writes the error into the response and no configuration turns the inclusion back on: one framework's error properties default to never including the trace or the message, and one standard HTTP server recovers a panicking handler, logs a stack trace to the server error log, and closes the connection or resets the stream. A default that depends on the environment complies only where the production deployment sets that environment: one common final error handler writes the status message as the body when the environment is production and the error's stack otherwise. The log keeps its own exposure in view: the guidance that sends details to the log asks to consider what could occur if attackers can view the log messages, and says passwords should never be saved to log files. The rule does not reach turning a debug mode on as such, the wording of the error value itself, or recording an error that is suppressed instead of reported.

## Validator
Grep the hunk for an error value written into a response: the error's string, message, stack or type name passed to a response writer, a response or exception constructor or an abort call; a stack trace printed into the response; configuration that sets the inclusion of the stack trace, message, exception or binding errors to always, on a parameter, or true; a developer exception page enabled. Open the file and decide whether the write answers a consumer across a trust boundary (an HTTP, RPC or API response or an error page) and whether the error is unexpected or security-sensitive, as opposed to an expected error the caller can resolve. For a configuration hit, trace whether it applies to the production deployment. For a handler that sends a generic message, trace whether the error's details reach the server log, in that handler or in a global or last-resort handler. Validator question: **Does the stack trace, exception message or type, query, file path, key or token of an unexpected or security-sensitive error reach a response sent across a trust boundary, or does the handler that sends the generic message leave the error's details out of the server log?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-27`, severity major, `file`, `symbol`, `code` = the line that writes the error's detail into the response, the configuration line that turns its inclusion on, or the line that sends the generic message for an error whose details reach no server log, `fix` = the handler logging the error on the server and sending a generic message with an error status, in the file's language, `rationale` = which detail reaches the consumer and the trust boundary it crosses, or that the error's details reach no server log).
