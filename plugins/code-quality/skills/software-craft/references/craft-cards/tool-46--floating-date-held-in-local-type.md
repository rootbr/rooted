---
title: A calendar date or wall-clock time that names no moment, such as a birth date, a holiday, an anniversary or an opening time set for every location, is held, stored and serialized in a local date or time type with no offset or zone, never as an instant at midnight in UTC or in the host's zone
rule_id: TOOL-46
domain: tooling
step: [design, implement]
applies_to: [universal]
triggers: ['(?i)\b(birth_?(day|date)?|dob|date_?of_?birth|holiday|anniversary|hire_?date|wedding_?date|opening_?(hours|time)|closing_?time|business_?hours)\w*\b.*\b(?:to)?(Instant|ZonedDateTime|OffsetDateTime|DateTimeOffset|DateTime2?|Timestamp|timestamptz|toISOString|fromtimestamp|time[.]Time)\b', '\b(Instant|ZonedDateTime|OffsetDateTime|DateTimeOffset|DateTime|Timestamp|time[.]Time)\b\??\s+\w*(?i:birth|dob|holiday|anniversary|hire_?date|opening|closing)', '\bDateMidnight\b|[.]withTimeAtStartOfDay\(|[.]atStartOfDay\(\s*\w|\bToDateTime\(\s*TimeOnly[.]MinValue|[.]combine\([^)]*\b(time[.]min|min[.]time\(\))|\bnew\s+Date\(\s*[''"]\d{4}-\d{2}-\d{2}[''"]\s*\)|\bDate[.]parse\(\s*[''"]\d{4}-\d{2}-\d{2}[''"]\s*\)']
scope: hunk
check_kind: semantic
severity_default: major
---

# A calendar date or wall-clock time that names no moment, such as a birth date, a holiday, an anniversary or an opening time set for every location, is held, stored and serialized in a local date or time type with no offset or zone, never as an instant at midnight in UTC or in the host's zone

## Thesis
A date or time value that is not tied to a specific offset or time zone rules, whether a calendar date such as a birth date, a holiday or an anniversary or a wall-clock time such as an opening or closing time set as a policy rather than for a specific location, is held in a floating type, a local or plain date, time or date-time, and is stored and serialized without an offset or zone identifier. It is not typed, stored or exchanged as an instant fixed at midnight in UTC or in the host's zone.

## Rationale
A floating value is one whose wall time matters more than its place on the timeline: a birth date of 1980-06-01 has to display as 1980-06-01 whether it is viewed in Tokyo, London or San Francisco. Errors often result when such a value is deserialized into an instant type, which ties it to UTC. A date held in a date-time can roll into the previous or next day once it is offset by a time zone, while a type that holds only the date cannot be offset and always represents the date that was set. An instant at midnight is a single millisecond rather than a day, and in some time zones midnight does not exist where the daylight-saving forward shift skips the midnight hour. One standard date API, by a historical specification error kept for web compatibility, interprets a date-only string with no offset as a UTC time. A local date cannot represent an instant on the timeline without additional information such as an offset or time zone, so the value is attached to the timeline only where code adds a zone or offset to it.

## Example
```java
bad:  Instant birthDate = LocalDate.of(1980, 6, 1).atStartOfDay(ZoneOffset.UTC).toInstant();
      String stored = birthDate.toString();
      LocalDate shown = LocalDate.ofInstant(Instant.parse(stored), ZoneId.systemDefault());
good: LocalDate birthDate = LocalDate.of(1980, 6, 1);
      String stored = birthDate.toString();
      LocalDate shown = LocalDate.parse(stored);
```

## Limits
The separating condition is whether the value names a moment. A value whose place on the timeline matters, such as a date of birth recorded with its time of day, is a specific moment in time and is held as an instant that represents the same moment wherever it is restored; the linter position that zone-aware date-times are preferred rests on their representing a specific moment in time, and it holds for such values. A floating value compared with an instant is first reconciled to the same reference point on the timeline, using a zone identifier or an explicit offset where one is available and UTC where none is. Where an interface hands a date over as an instant at midnight UTC on the morning of that date, that instant is only a zone-less value that happens to use UTC as a simple way of storing it: the code never confuses it with an instant at that moment in UTC and floats it at that boundary by taking its fields in UTC and removing its zone or offset, which makes it easier to format later without its field values changing incorrectly. An instant an interface builds at midnight in the host's zone is floated by taking its fields in that zone, since its fields in UTC fall on the previous day wherever that zone is ahead of UTC. An opening or closing time set for one location is tied to that location's time zone rules: it is held in a local time type with the location's zone identifier kept beside it, and each occurrence is computed with that zone.

## Validator
Grep the hunk for instant, timestamp, zoned or offset date-time types and timestamp column types, for start-of-day or midnight conversions and for date-only strings parsed into an instant type, together with names such as birth date, date of birth, holiday, anniversary, hire date, opening or closing time and business hours. For each match, open the hunk and decide whether the value names a moment, recorded with its time of day and tied to an offset or zone, or is a calendar date or wall time whose displayed value must stay the same in every zone. Trace a floating value to where the hunk stores it (the column type), serializes it (an offset or UTC designator in the written text) and reads it back (a conversion into the host's or the viewer's zone). Set aside a conversion written for a comparison with an instant, an opening or closing time of one location kept with that location's zone identifier, and an instant an interface hands over that the hunk floats at that boundary by taking its fields in the zone the interface built it in, UTC for an instant at midnight UTC, and never treats as a moment. Validator question: **Does the hunk type, store or serialize a date or wall-clock time that names no moment as an instant, a zoned or offset date-time, or a midnight in UTC or the host's zone?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-46`, severity major, `file`, `symbol`, `code` = the declaration, column, conversion or parse that gives the floating value an instant, offset or zone type, `fix` = the value held in the file's local or plain date or time type and serialized as an ISO 8601 date or time with no offset, `rationale` = the value names no moment, and an offset or zone applied to it can shift its date or wall time for viewers in other zones).
