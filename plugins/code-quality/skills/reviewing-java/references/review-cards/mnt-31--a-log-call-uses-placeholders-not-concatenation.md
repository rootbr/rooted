---
title: A log call uses a parameterized message with {} placeholders rather than string concatenation, and passes a throwable as an argument
rule_id: MNT-31
domain: maintainability
triggers: ['log\w*[.](trace|debug|info|warn|error)\(\s*"[^"]*"\s*\+', 'log\w*[.](trace|debug|info|warn|error)\([^;]*\+\s*\w', 'String[.]format\(', 'LOGGER[.]|logger[.]|log[.]', 'getMessage\(\)\s*\)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A log call uses a parameterized message with {} placeholders rather than string concatenation, and passes a throwable as an argument

## Thesis
A logging statement passes a constant message with `{}` placeholders and the values as arguments — `log.info("order {} placed by {}", id, user)` — not a message built by `+` or `String.format`; a caught exception is passed as the final argument so the logger records its stack trace, not appended to the message or reduced to `getMessage()`.

## Rationale
A concatenated message is built before the logger checks whether the level is enabled, so every disabled `debug` call still formats and allocates; the parameterized form skips that work when the level is off, and its varargs form still allocates an `Object[]` even then, which is why the one- and two-argument overloads exist. The constant message is also what log tooling groups on: with placeholders every occurrence of the event shares one template and the values become fields. An exception concatenated into the message contributes its `toString()` — class and message — and drops the stack trace and cause chain; passed as the throwable argument it is logged whole.

## Example
```java
bad:  log.debug("loaded " + orders.size() + " orders for " + customerId);
      log.error("payment failed: " + e.getMessage());
good: log.debug("loaded {} orders for {}", orders.size(), customerId);
      log.error("payment failed for order {}", orderId, e);
```

## Limits
A message assembled once outside the logger for another purpose and then logged is not this finding. A logging API without `{}` placeholders (`java.util.logging`) uses its own `{0}` form or a supplier overload. Concatenation of two constants is folded by the compiler. Whether the log line should exist at that level is a separate concern.

## Validator
On the triggered hunk find each logger call whose message argument contains `+` with a non-constant operand or a `String.format`, and each call that appends an exception or its `getMessage()` into the message without passing the throwable as an argument. Validator question: **is this log message built by concatenation or formatting, or does it drop the throwable from the argument list?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-31`, severity minor, `file`, `symbol`, `code` = the log call quoted verbatim from the diff, `fix` = the placeholder form with the throwable last, `rationale` naming the eager formatting and, where it applies, the lost stack trace).

## Source
SLF4J `org.slf4j.Logger` Javadoc — `debug(String format, Object arg)`: "This form avoids superfluous object creation when the logger is disabled for the DEBUG level"; `debug(String format, Object... arguments)`: "This form avoids superfluous string concatenation when the logger is disabled for the DEBUG level … The variants taking one and two arguments exist solely in order to avoid this hidden cost"; `error(String msg, Throwable t)`: "Log an exception (throwable) at the ERROR level with an accompanying message" (fetched from `slf4j-api/src/main/java/org/slf4j/Logger.java`, branch `master`).
