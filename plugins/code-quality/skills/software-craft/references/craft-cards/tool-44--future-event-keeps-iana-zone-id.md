---
title: A future or recurring event set at a wall-clock time in a place is stored with its intended local time and that place's IANA time zone identifier, never only an instant or a UTC offset computed when it was scheduled
rule_id: TOOL-44
domain: tooling
step: [design, implement]
applies_to: [universal]
triggers: ['(?i)(schedul|meeting|appointment|reminder|recurr|occurrence|booking|calendar)\w*.*\b(utc|toInstant|toISOString|astimezone|timestamp|epoch)', '(?i)\b(utc|instant|timestamp|epoch)\w*.*(schedul|meeting|appointment|reminder|recurr|booking|calendar)', '\bOffsetDateTime\b|\bFixedOffset\b|\bfixed_offset\b|\bZoneOffset[.]of']
scope: file
check_kind: semantic
severity_default: major
---

# A future or recurring event set at a wall-clock time in a place is stored with its intended local time and that place's IANA time zone identifier, never only an instant or a UTC offset computed when it was scheduled

## Thesis
A stored or serialized future or recurring event that is set at a wall-clock time in a place carries its intended local time together with that place's IANA time zone identifier, so that each occurrence is computed from the zone's rules; an instant, epoch count or UTC offset computed when the event was scheduled is at most a derived value kept beside them.

## Rationale
Zone rules for future dates are predictions: the time zone database predicts future timestamps, and those predictions become incorrect after a government changes the rules. A meeting scheduled today for 13:00 next October 1, Dublin time, can be mis-handled after Ireland changes its daylight saving rules when the software relies on conversions made before the change. A future event's wall time depends on time zone information such as summer time transitions, so an application with future events needs the time zone and not merely the local time offset. When the zone's rules change, a stored incremental value for a future event needs to be checked or updated if the event's wall time is expected to stay the same, and values pre-computed for future events might need refreshing after the runtime's copy of the time zone database is updated. Future meetings are stored as the calendar date and wall-clock time together with the time zone, not as an exact time, because the zone's daylight saving rules can change before a meeting that is still held at the same wall-clock time, and the meeting's exact time then changes with them. A recurring event is in many cases meant to recur at a local wall time in a specific zone; each occurrence's start depends on that zone's offset and summer time rules, and computing it with the zone avoids assuming that the number of units between occurrences, such as hours in a week or minutes in a day, is fixed, and helps avoid wall times that can never exist. A serialization that stores the offset but not the location name loses the daylight saving information, and an offset-only value read back no longer gives daylight-saving-safe arithmetic in the original zone; the RFC 9557 format embeds the identifier in brackets, as in `2024-07-21T17:11-04[America/New_York]`. When a stored future value holds both the offset and the zone and the zone's definition later changes, the two may conflict, and the reading code chooses whether to keep the exact time or the local time.

## Example
```java
bad:  Instant start = meeting.localStart().atZone(zone).toInstant();
      store.save(meeting.id(), OffsetDateTime.ofInstant(start, zone));
good: store.save(meeting.id(), meeting.localStart(), zone.getId());
```

## Limits
Records of events that have already occurred are outside the rule: once an event is in the past its local time offset to UTC is fixed, so an incremental time with an offset can always produce its wall time, although the zone identifier is still needed to display the zone's name or abbreviation. Floating values that are not tied to a specific offset or time zone rules, such as a list of holidays, a birth date or another anniversary date, are stored without an offset or a zone. An instant pre-computed for scheduling or notifications and kept beside the record's intended local time and zone identifier meets the rule; it might need refreshing after the runtime's copy of the time zone database is updated. An instant stored with only the zone identifier keeps the zone for display, but when the zone's rules change it has to be checked or updated if the event's wall time is expected to stay the same, and the record holds no wall time to check it against; for an event set at a wall-clock time it meets the rule only beside the intended local time. A future event meant to keep its exact time rather than its wall time when the zone's rules change is outside the rule.

## Validator
Grep the hunk for the time of a scheduled, future or recurring event (a meeting, appointment, reminder, booking, recurrence or calendar entry) converted to an instant, an epoch count, a UTC value or a fixed-offset type, or written out through a formatter or marshaller. Open the file and trace that value to where it is stored or sent: a column, a document field, a message, a serialized string. Check whether the stored record also carries the event's intended local time and the IANA time zone identifier of the place whose wall clock set it: a local date-time column or field beside a zone column or field, an RFC 9557 string with the local date-time, its offset and a bracketed zone suffix such as `2024-07-21T17:11-04[America/New_York]`, or a zoned type whose serialization keeps both; a UTC time with a zone suffix or beside a zone column keeps the identifier but not the intended local time. Pass records of events that have already occurred and floating dates tied to no zone. Validator question: **Does the hunk store or serialize a future or recurring event set at a wall-clock time in a place as an instant, epoch count or UTC offset without keeping both its intended local time and its IANA time zone identifier?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-44`, severity major, `file`, `symbol`, `code` = the line that converts or serializes the event's time without keeping both its intended local time and its zone identifier, verbatim from the diff, `fix` = the stored record carrying the intended local time with the IANA zone identifier, any instant kept beside them as a derived value, in the file's language, `rationale` = names the event, the zone identifier or intended local time that is dropped, and that a later rule change in that zone moves the event away from its intended wall time).
