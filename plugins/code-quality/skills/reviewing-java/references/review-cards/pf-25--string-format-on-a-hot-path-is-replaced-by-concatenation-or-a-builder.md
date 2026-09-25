---
title: String.format, formatted and MessageFormat.format on a hot path are replaced by concatenation or a StringBuilder, or by a formatter parsed once
rule_id: PF-25
domain: performance
triggers: ['String[.]format\(', '[.]formatted\(', 'MessageFormat[.]format\(', 'new Formatter\(', 'printf\(', 'new MessageFormat\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# String.format, formatted and MessageFormat.format on a hot path are replaced by concatenation or a StringBuilder, or by a formatter parsed once

## Thesis
A string assembled per request, per record or per iteration — a cache key, an identifier, a line of output — is built with `+` or a `StringBuilder`; `String.format`, `String.formatted`, `Formatter.format` and `MessageFormat.format(String, Object...)` are used where their formatting (padding, width, locale-aware numbers or dates) is needed, off the hot path, or through a `MessageFormat` instance parsed once and reused.

## Rationale
`String.format(fmt, args)` creates a new `Formatter` and its `StringBuilder`, parses the format string into its specifiers on every call — the parse result is not cached — walks the specifiers interpreting each conversion at run time, and receives its arguments through a varargs array with each primitive boxed. A `+` expression or a `StringBuilder` chain writes the pieces directly with no parsing, no interpreter and no boxing of primitives. `MessageFormat.format(String, Object...)` likewise constructs and parses a `MessageFormat` per call, while the instance form parses once. The difference is per call, so it matters exactly where the call is per element.

## Example
```java
bad:  String key = String.format("%s:%d:%s", tenant, shard, id);   // per request
good: String key = tenant + ':' + shard + ':' + id;
```

## Limits
A format that needs width, precision, or locale-sensitive number or date rendering keeps `String.format` (or a `DecimalFormat` or `DateTimeFormatter` held statically). A call off the hot path — an error message, a startup banner, a once-per-request audit line — is not worth rewriting. A `MessageFormat` instance kept in a static field and applied per call has paid its parse once; message formats are not synchronized, so the shared instance is used under a lock or cloned per thread.

## Validator
On the triggered hunk find each `String.format`, `formatted`, `MessageFormat.format` or `Formatter.format` call. Confirm it runs per request, per record or inside a loop, and that its specifiers are plain `%s` or `%d` with no width, precision or locale-dependent conversion. Validator question: **does this hot path parse a format string on every call to produce plain concatenation output?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-25`, severity minor, `file`, `symbol`, `code` = the format call quoted verbatim from the diff, `fix` = the concatenation or builder, `rationale` naming the per-call parse and interpretation of the format string).

## Source
`java.lang.String#format(String, Object...)` and `java.util.Formatter#format(Locale, String, Object...)`, Java SE 21 source — `String.format` returns `new Formatter().format(format, args).toString()`, and `Formatter.format` calls `parse(format)` on every invocation (an implementation detail, not a documented contract). `java.text.MessageFormat#format(String, Object...)` Javadoc — "Creates a MessageFormat with the given pattern and uses it to format the given arguments"; class Javadoc — "Message formats are not synchronized." JMH benchmarks `kabutz/string-performance`, `.../PlainStringAppendBenchmark.java` — `stringBuilder`, `stringBuilderSized`, `stringBuffer` and `stringFormat` on the same five-argument message; `ionutbalosin/jvm-performance-benchmarks`, `.../api/string/StringFormatBenchmark.java` — `String.format`, `MessageFormat` as a constant versus a per-call instance, and `String.formatted`.
