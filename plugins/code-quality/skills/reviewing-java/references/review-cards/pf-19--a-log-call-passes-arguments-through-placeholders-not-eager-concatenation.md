---
title: A log call passes its arguments through {} placeholders or behind a level guard, never through string concatenation or a toString evaluated before the level is checked
rule_id: PF-19
domain: performance
triggers: ['(log|logger|LOG|LOGGER)[.](trace|debug|info)\(', 'isDebugEnabled\(\)', 'isTraceEnabled\(\)', 'isInfoEnabled\(\)', 'atDebug\(\)', 'atTrace\(\)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A log call passes its arguments through {} placeholders or behind a level guard, never through string concatenation or a toString evaluated before the level is checked

## Thesis
A `trace`, `debug` or `info` statement builds no message eagerly: it passes a constant format string with `{}` placeholders and the raw arguments, and when an argument is itself expensive to compute — a `toString` over a large graph, a serialization, a `String.format`, a collection copy — the call is wrapped in `if (log.isDebugEnabled())` or goes through the fluent `log.atDebug().addArgument(() -> …)` supplier form.

## Rationale
The message argument of a log call is evaluated by the caller before the logger sees it: `"state=" + state + " user=" + user` concatenates and runs both `toString` methods on every execution, whether or not the level is enabled — the cost is paid on the hot path for output that is normally discarded. The parameterized form defers formatting until the logger has checked the level, so a disabled level costs one boolean check and the argument references, and the one- and two-argument overloads allocate nothing. A `Supplier` argument through the fluent builder defers even the computation of the argument, and a level guard skips the whole statement.

## Example
```java
bad:  log.debug("state=" + state + " user=" + user.toString());
      log.debug("payload={}", mapper.writeValueAsString(payload));   // serialized even when off
good: log.debug("state={} user={}", state, user);
      if (log.isDebugEnabled()) log.debug("payload={}", mapper.writeValueAsString(payload));
```

## Limits
A `warn` or `error` that is always enabled in production formats its message anyway; the placeholder form is still the house style but carries no cost argument. A message that is a compile-time constant needs no placeholders. A trivial `toString` (a `record`, an id) passed as a placeholder argument is fine; the guard is for the expensive case. Whether the log line leaks sensitive data is a separate concern.

## Validator
On the triggered hunk find each `trace`, `debug` or `info` call whose message argument contains `+` concatenation, an explicit `toString()`, a `String.format`, or a method call that builds a string or copies data, outside an `is*Enabled` guard or a `Supplier`. Validator question: **does this log statement compute its message or an expensive argument before the logger checks the level?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-19`, severity minor, `file`, `symbol`, `code` = the log call quoted verbatim from the diff, `fix` = the placeholder form with a guard or supplier for the expensive argument, `rationale` naming the evaluation that runs while the level is disabled).

## Source
SLF4J `org.slf4j.Logger` Javadoc (`slf4j-api`, `master`) — `debug(String format, Object arg)`: "This form avoids superfluous object creation when the logger is disabled for the DEBUG level"; `debug(String format, Object... arguments)`: "This form avoids superfluous string concatenation when the logger is disabled for the DEBUG level"; `atDebug()`: "If this logger is disabled for the DEBUG level, then a NOPLoggingEventBuilder instance is returned. As the name indicates, this builder does not perform any operations. This is the main optimization in the fluent API"; `org.slf4j.spi.LoggingEventBuilder#addArgument(Supplier<?>)` — the deferred-argument form. The same text is carried on the `trace` and `info` overloads.
