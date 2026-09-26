---
title: A log or utility varargs call on a hot path with three or more arguments is level-guarded, uses the fluent builder, or avoids varargs, so no Object[] is allocated when nothing is logged
rule_id: PF-21
domain: performance
triggers: ['(log|logger|LOG|LOGGER)[.](trace|debug|info)\([^;]*,[^;]*,[^;]*,', 'Object[.][.][.]', '[.][.][.] \w+\)', 'atDebug\(\)', 'atTrace\(\)']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A log or utility varargs call on a hot path with three or more arguments is level-guarded, uses the fluent builder, or avoids varargs, so no Object[] is allocated when nothing is logged

## Thesis
A `trace`, `debug` or `info` call with three or more placeholder arguments on a per-request, per-message or per-iteration path is wrapped in `if (log.isDebugEnabled())`, or written through `log.atDebug().addArgument(a).addArgument(b).addArgument(c).log("…")`, or reduced to two arguments; a project-internal method declared with `Object...` (or any `T...`) that is called on a hot path gets fixed-arity overloads for the common argument counts.

## Rationale
Calling a variable-arity method makes the caller wrap the arguments in a new array before the call: for a logger's `debug(String, Object...)` that `Object[]` is allocated even when the logger is disabled for DEBUG — a hidden cost the one- and two-argument overloads exist solely to avoid. On a hot path the discarded arrays are steady garbage. The fluent API returns a no-operation builder when the level is disabled, so its `addArgument` calls cost nothing; a level guard skips the call entirely; a fixed-arity overload removes the array. The compiler removes the array only when it inlines the callee, which a call through the `Logger` interface with more than one binding is not.

## Example
```java
bad:  log.debug("op={} key={} size={} took={}ms", op, key, size, elapsed);
good: if (log.isDebugEnabled()) log.debug("op={} key={} size={} took={}ms", op, key, size, elapsed);
      // or: log.atDebug().addArgument(op).addArgument(key).addArgument(size)
      //        .addArgument(elapsed).log("op={} key={} size={} took={}ms");
```

## Limits
Applies on a hot path; a varargs call at startup, in error handling, or in a rarely-run branch is fine. A `warn` or `error` that is always enabled pays the array as part of a message that is formatted anyway. A varargs callee that the compiler inlines (a small private method in the same class) has its array removed by escape analysis, and the finding is downgraded when the diff shows that. Passing an existing array as the varargs argument allocates nothing.

## Validator
On the triggered hunk find each logger call with three or more arguments after the format string, and each call of a `...`-declared method on a per-request or per-iteration path, outside an `is*Enabled` guard and not through the fluent builder. Validator question: **does this hot-path call allocate a varargs array on every execution, including when the log level is disabled?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-21`, severity minor, `file`, `symbol`, `code` = the call quoted verbatim from the diff, `fix` = the guard, the fluent form or the fixed-arity overload, `rationale` naming the `Object[]` allocated per call).

## Source
SLF4J `org.slf4j.Logger` Javadoc (`slf4j-api`, `master`) — `debug(String format, Object... arguments)`: "this variant incurs the hidden (and relatively small) cost of creating an Object[] before invoking the method, even if this logger is disabled for DEBUG. The variants taking one and two arguments exist solely in order to avoid this hidden cost"; `atDebug()`: a `NOPLoggingEventBuilder` is returned when the level is disabled, "the main optimization in the fluent API". JMH benchmark `ionutbalosin/jvm-performance-benchmarks`, `.../compiler/VarArgsBenchmark.java` — "Using varargs in Java will cause the caller to wrap the arguments in an array and pass the array to the callee. If the callee is inlined, then the array allocation is removed." JLS §15.12.4.2 (a variable-arity invocation creates the array) — not fetched from the authoring environment.
