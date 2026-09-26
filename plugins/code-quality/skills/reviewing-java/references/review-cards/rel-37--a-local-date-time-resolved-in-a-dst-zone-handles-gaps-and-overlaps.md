---
title: A LocalDateTime resolved into a zone with daylight saving is resolved with ofStrict or ZoneRules where a silent adjustment would be wrong
rule_id: REL-37
domain: reliability
triggers: ['ZonedDateTime[.]of\(', '[.]atZone\(', 'ofLocal\(', 'ofStrict\(', 'getValidOffsets\(', 'isValidOffset\(', 'LocalDateTime[.]of\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A LocalDateTime resolved into a zone with daylight saving is resolved with ofStrict or ZoneRules where a silent adjustment would be wrong

## Thesis
Code that turns a local date-time into a zoned one for a zone with daylight saving — a schedule, an appointment, a user-entered time — decides what happens in a gap (a local time that does not exist) and an overlap (a local time that occurs twice): it uses `ZonedDateTime.ofStrict`, checks `ZoneRules.getValidOffsets`, or documents that the default adjustment of `ZonedDateTime.of` and `atZone` is the intended behaviour.

## Rationale
`ZonedDateTime.of(localDateTime, zone)` never fails: "In the case of an overlap, when clocks are set back, there are two valid offsets. This method uses the earlier offset typically corresponding to 'summer'"; "In the case of a gap, when clocks jump forward, there is no valid offset. Instead, the local date-time is adjusted to be later by the length of the gap". A job scheduled at 02:30 on the spring transition day runs at 03:30 with no error; one scheduled at 02:30 on the autumn day runs on the first of the two 02:30s whether or not that was meant; a user-entered time in a gap is silently moved. The behaviour is documented and correct for a wall-clock reading, and wrong for code that assumes the time it wrote is the time it gets back. `ofStrict` throws `DateTimeException` on an invalid combination, and `ZoneRules` exposes both offsets so the code can choose.

## Example
```java
bad:  ZonedDateTime run = ZonedDateTime.of(LocalDateTime.of(date, LocalTime.of(2, 30)), zone);   // 02:30 may not exist
good: ZoneOffset offset = zone.getRules().getValidOffsets(local).stream().findFirst()
          .orElseThrow(() -> new InvalidScheduleException(local, zone));
      ZonedDateTime run = ZonedDateTime.ofStrict(local, offset, zone);
```

## Limits
A conversion of a time that can never fall in a transition — a date-only value at midnight in a zone whose transitions are at 02:00, a time in a zone without daylight saving — is out of scope. A comment stating that the default adjustment is acceptable for this use (a rough scheduling window) rejects the finding. Display-only conversions of an `Instant` through `atZone` are exact and are not flagged.

## Validator
On the triggered hunk find each `ZonedDateTime.of(LocalDateTime, ZoneId)` and each `LocalDateTime.atZone` whose input comes from a schedule, user entry or stored local time, in a zone that may observe daylight saving. Check for `ofStrict`, a `ZoneRules` check, or a comment accepting the adjustment. Validator question: **can this local time fall into a gap or overlap, with the silent adjustment producing a moment the author did not intend?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-37`, severity minor, `file`, `symbol`, `code` = the conversion quoted verbatim from the diff, `fix` = `ofStrict` with an offset from `ZoneRules.getValidOffsets`, or a comment stating the accepted adjustment, `rationale` naming the gap or overlap day).

## Source
`java.time.ZonedDateTime#of(LocalDateTime, ZoneId)` Javadoc, Java SE 21 — "Time-zone rules, such as daylight savings, mean that not every local date-time is valid for the specified zone, thus the local date-time may be adjusted ... In the case of an overlap, when clocks are set back, there are two valid offsets. This method uses the earlier offset typically corresponding to 'summer'. In the case of a gap, when clocks jump forward, there is no valid offset. Instead, the local date-time is adjusted to be later by the length of the gap"; `#ofStrict(LocalDateTime, ZoneOffset, ZoneId)` — "If the offset is invalid, an exception is thrown".
