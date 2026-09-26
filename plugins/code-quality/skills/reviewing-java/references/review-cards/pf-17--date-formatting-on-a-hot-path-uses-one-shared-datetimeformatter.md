---
title: Date and time formatting on a hot path goes through one shared static DateTimeFormatter, never a SimpleDateFormat or DateTimeFormatter constructed per call
rule_id: PF-17
domain: performance
triggers: ['new SimpleDateFormat\(', 'DateTimeFormatter[.]ofPattern\(', 'DateFormat[.]get\w*Instance\(', 'ofPattern\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Date and time formatting on a hot path goes through one shared static DateTimeFormatter, never a SimpleDateFormat or DateTimeFormatter constructed per call

## Thesis
A method that formats or parses a date on each call uses a `DateTimeFormatter` held in a `private static final` field, or a shared constant such as `DateTimeFormatter.ISO_INSTANT`; it neither constructs a `SimpleDateFormat` per call nor calls `DateTimeFormatter.ofPattern` per call.

## Rationale
`SimpleDateFormat` is not synchronized, and its documentation recommends a separate instance per thread — so code that is correct with it either builds one per call or pins one per thread, and the per-call form compiles the pattern and allocates the formatter and its calendar on every invocation. `DateTimeFormatter` is immutable and thread-safe: a formatter created from a pattern can be used as many times as necessary from any thread, so one static instance serves every call, and `ofPattern` — which parses the pattern and builds the formatter — runs once at class initialization instead of on every request. The legacy API remains only where a `java.util.Date` API forces it.

## Example
```java
bad:  String stamp(Instant t) {
          return new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(Date.from(t));
      }
good: private static final DateTimeFormatter STAMP =
          DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss").withZone(ZoneOffset.UTC);
      String stamp(Instant t) { return STAMP.format(t); }
```

## Limits
A pattern that varies per call (a user-chosen format) is built per distinct pattern and cached. A `SimpleDateFormat` required by a legacy API that accepts only `DateFormat` is acceptable when held in a `ThreadLocal` on a platform pool and that is documented; sharing one `SimpleDateFormat` across threads is a thread-safety defect outside this rule. A one-off format at startup needs no hoisting.

## Validator
On the triggered hunk find each `new SimpleDateFormat(...)` and each `DateTimeFormatter.ofPattern(...)` that is not the initializer of a static final field. Confirm the enclosing method runs per request, per record or in a loop. Validator question: **does this method construct a date formatter on every call instead of using one shared DateTimeFormatter?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-17`, severity minor, `file`, `symbol`, `code` = the constructor or `ofPattern` call quoted verbatim from the diff, `fix` = the `static final DateTimeFormatter` and its use, `rationale` naming the per-call pattern parse and allocation).

## Source
`java.time.format.DateTimeFormatter` class Javadoc, Java SE 21 — "A formatter created from a pattern can be used as many times as necessary, it is immutable and is thread-safe"; implementation specification — "This class is immutable and thread-safe". `java.text.SimpleDateFormat` class Javadoc — "Date formats are not synchronized. It is recommended to create separate format instances for each thread"; API note — "Consider using java.time.format.DateTimeFormatter as an immutable and thread-safe alternative."
