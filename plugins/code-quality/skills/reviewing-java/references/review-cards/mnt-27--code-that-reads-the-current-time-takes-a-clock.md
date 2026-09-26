---
title: Code that reads the current time takes a Clock and calls now(clock), not Instant.now(), LocalDate.now() or System.currentTimeMillis()
rule_id: MNT-27
domain: maintainability
triggers: ['Instant[.]now\(\)', 'LocalDate(Time)?[.]now\(\)', 'ZonedDateTime[.]now\(\)|OffsetDateTime[.]now\(\)|LocalTime[.]now\(\)', 'System[.]currentTimeMillis\(\)', 'new Date\(\)', 'Clock[.]system']
scope: file
check_kind: mechanical
severity_default: minor
---

# Code that reads the current time takes a Clock and calls now(clock), not Instant.now(), LocalDate.now() or System.currentTimeMillis()

## Thesis
A class whose logic depends on the current instant or date — an expiry check, a timestamp on a record, a scheduling decision — receives a `java.time.Clock` (injected through its constructor, or passed as a parameter) and reads time through `Instant.now(clock)`, `LocalDate.now(clock)` and the like; `Instant.now()`, `LocalDateTime.now()`, `System.currentTimeMillis()` and `new Date()` are not called in that logic.

## Rationale
A direct read of the system clock cannot be controlled from a test, so the test either sleeps, computes expected values relative to "now" and races midnight and month ends, or leaves the branch untested; the same code cannot be replayed at a chosen time in a debugger. A `Clock` is the JDK's designed seam: the class obtains time from an object rather than a static method, a test passes `Clock.fixed(...)` or `Clock.offset(...)`, and production passes `Clock.systemUTC()` from configuration. Every date-time `now()` factory has an overload that takes the clock.

## Example
```java
bad:  boolean isExpired(Token t) { return t.expiresAt().isBefore(Instant.now()); }
good: private final Clock clock;
      TokenService(Clock clock) { this.clock = clock; }
      boolean isExpired(Token t) { return t.expiresAt().isBefore(Instant.now(clock)); }
```

## Limits
Measuring elapsed time for a metric or a timeout uses `System.nanoTime()`, which is not this concern. Logging a timestamp, a `main` method, a `@Bean Clock clock() { return Clock.systemUTC(); }` factory, and test code itself read the system clock legitimately. A clock already injected under another name (a time-provider interface the project context names) satisfies the rule.

## Validator
On the triggered hunk find each `now()` without a `Clock` argument and each `currentTimeMillis()` or `new Date()`. Open the file to see whether the value feeds logic (a comparison, a stored field, a computation) and whether the class has a `Clock` available. Validator question: **does this logic read the system clock directly where a `Clock` could be injected and passed to `now(clock)`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-27`, severity minor, `file`, `symbol`, `code` = the `now()` call quoted verbatim from the diff, `fix` = the `Clock` field or parameter and `now(clock)`, `rationale` naming the test that cannot control time).

## Source
`java.time.Clock` class Javadoc, Java SE 21 — "Applications use an object to obtain the current time rather than a static method. This can simplify testing"; "Best practice for applications is to pass a Clock into any method that requires the current instant and time-zone. A dependency injection framework is one way to achieve this … This approach allows an alternative clock, such as fixed or offset to be used during testing"; `Clock` "can be used instead of System.currentTimeMillis()".
