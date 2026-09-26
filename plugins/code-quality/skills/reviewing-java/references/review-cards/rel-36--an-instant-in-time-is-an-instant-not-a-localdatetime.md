---
title: A point in time that is stored, transmitted or compared across zones is an Instant or an offset-bearing type, never a LocalDateTime
rule_id: REL-36
domain: reliability
triggers: ['LocalDateTime', 'LocalDateTime[.]now\(\)', 'createdAt', 'updatedAt', 'timestamp', 'expiresAt', '@Column.*LocalDateTime']
scope: file
check_kind: semantic
severity_default: major
---

# A point in time that is stored, transmitted or compared across zones is an Instant or an offset-bearing type, never a LocalDateTime

## Thesis
A field, column, message attribute or API value that records when something happened — a creation time, an expiry, a schedule, an event timestamp — is typed `Instant` (or `OffsetDateTime`/`ZonedDateTime` when the zone is part of the data), and `LocalDateTime` is reserved for a wall-clock reading that has no zone by design, such as a birthday or an opening hour.

## Rationale
`LocalDateTime` "does not store or represent a time-zone ... It cannot represent an instant on the time-line without additional information such as an offset or time-zone". A `LocalDateTime.now()` written by a server in one zone and read by a server in another, or by the same server after a zone change or across a daylight-saving transition, denotes a different instant; expiries drift by an hour twice a year, orderings across regions are wrong, and an hour of local times is either ambiguous or non-existent on the transition days. `Instant` is "an instantaneous point on the time-line" that "might be used to record event time-stamps in the application", and is the same value everywhere; conversion to a zone happens at the display boundary.

## Example
```java
bad:  @Column private LocalDateTime createdAt = LocalDateTime.now();
      boolean expired() { return expiresAt.isBefore(LocalDateTime.now()); }
good: @Column private Instant createdAt;
      Token(Clock clock) { createdAt = clock.instant(); }
      boolean expired(Clock clock) { return expiresAt.isBefore(Instant.now(clock)); }
```

## Limits
A local date-time that is genuinely zone-free — a recurring local opening time, a date of birth with a time, a calendar entry the user reads in their own zone — is correct as `LocalDateTime`. A database column type that cannot carry an offset, mapped to `Instant` through the JDBC driver's UTC normalization stated in the project context, is correct. A `LocalDateTime` converted to `Instant` with an explicit zone at the boundary is out of scope.

## Validator
On the triggered hunk find each `LocalDateTime` field, parameter, column or `now()` call and read what it denotes: a moment that other zones, servers or later dates must agree on, or a zone-free local reading. Validator question: **does this LocalDateTime stand for a point on the time-line that will be compared, stored or transmitted beyond one wall clock?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-36`, severity major, `file`, `symbol`, `code` = the declaration or `now()` call quoted verbatim from the diff, `fix` = `Instant` (or `OffsetDateTime`) with conversion to a zone only at display, `rationale` naming the zone or daylight-saving drift).

## Source
`java.time.LocalDateTime` class Javadoc, Java SE 21 — "This class does not store or represent a time-zone. Instead, it is a description of the date, as used for birthdays, combined with the local time as seen on a wall clock. It cannot represent an instant on the time-line without additional information such as an offset or time-zone". `java.time.Instant` class Javadoc — "An instantaneous point on the time-line ... This might be used to record event time-stamps in the application".
