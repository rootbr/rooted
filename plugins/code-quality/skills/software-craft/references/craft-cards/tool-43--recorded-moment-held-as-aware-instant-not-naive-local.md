---
title: A value that records a moment, such as when an event happened or an expiry set as a duration from now, is held, stored and exchanged as a time-zone-aware instant and converted to a named time zone only to display it or compute calendar fields, never held as a naive or host-local date-time
rule_id: TOOL-43
domain: tooling
step: [design, implement]
applies_to: [universal]
triggers: ['\bdatetime[.](now|utcnow|today)\(\s*\)|\bdatetime[.]utcfromtimestamp\(|\bdatetime[.]fromtimestamp\([^,]*?\)|\bdate[.]today\(\s*\)|\b(LocalDateTime|LocalDate|LocalTime)[.]now\(\s*\)|\bZoneId[.]systemDefault\(|\bTimeZone[.]getDefault\(|\btime[.]Local\b|[.]Local\(\)|\bLocal::now\(\)|\b(ZoneId[.]of|ZoneInfo|pytz[.]timezone|LoadLocation|TimeZone[.]getTimeZone)\(\s*[''"](EST|EDT|CST|CDT|MST|MDT|PST|PDT|IST|CET|CEST|BST)[''"]', '\bNaiveDateTime\b|\b[Tt]imestamp(?:\s*\(\s*\d+\s*\))?\s+without\s+time\s+zone\b|\bDATETIME\b|\bTIMESTAMP\b(?!\s*(?:\(\s*\d+\s*\))?\s+(?:WITH|with)\s)', '[.]get(Hours|Minutes|Date|Day|Month|FullYear)\(\)|[.]toLocale(String|DateString|TimeString)\(|[.]naive_local\(\)']
scope: hunk
check_kind: semantic
severity_default: major
---

# A value that records a moment, such as when an event happened or an expiry set as a duration from now, is held, stored and exchanged as a time-zone-aware instant and converted to a named time zone only to display it or compute calendar fields, never held as a naive or host-local date-time

## Thesis
A value that records a moment, either the time something happened or a moment computed when it is recorded, such as an expiry set as a duration from now, is held in the language's instant or time-zone-aware type and is stored and exchanged normalized to UTC, or less commonly to one fixed UTC offset. It is turned into date and clock fields only with a time zone the code names, the user's preference or the zone the domain logic dictates, to display it or compute calendar fields; it is never held as a naive date-time and never converted with the host's default zone taken silently. An offset is written as a number such as -0600, not as an abbreviation such as CST.

## Rationale
An aware value represents a specific moment in time that is not open to interpretation. A naive value does not say whether it is UTC, local time or time in some other zone; that is left to the program, and in at least one standard library many date-time methods treat a naive value as local time. A date type that stores only a timestamp does not store the local zone, and its local-time accessors take the zone from the host environment. An API that silently uses the host's default zone is dangerous because that zone can vary from machine to machine and from runtime to runtime. Changing the zone in which an instant is interpreted does not change the instant it represents, and each instant can be transformed for display with various time zones' rules or offsets. Timestamps normalized to UTC, or less commonly to one specific UTC offset, let separate series of data be easily compared and merged. Zone abbreviations are ambiguous in practice: CST means one thing in China and something else in North America, and IST can mean India, Ireland or Israel.

## Example
```rust
bad:  let expires_at: NaiveDateTime = Local::now().naive_local() + ttl;
      store.put("expires_at", expires_at.to_string());
      show(expires_at.format("%H:%M").to_string());
good: let expires_at: SystemTime = SystemTime::now() + ttl;
      let utc_secs = expires_at.duration_since(UNIX_EPOCH)?.as_secs();
      store.put("expires_at_utc", utc_secs.to_string());
      show(format_in_zone(expires_at, &viewer.time_zone));
```

## Limits
Whether every date-time is stored in UTC is contested, and the condition that separates the cases is whether the value is a moment fixed when it is recorded. On one side (W3C time-zone note, Timestamps), events not tied to a specific local time need only the timestamp value, and when in doubt UTC is used for serializing, storing and exchanging it. On the other (tz database theory file; W3C time-zone note, Past and Future Events; Temporal time-zone documentation), a future or recurring event set at a wall-clock time in a place keeps its time zone, because the zone's rules can change before it occurs: for a meeting scheduled for 13:00 next October 1, Dublin time, software can go wrong after Ireland changes its daylight saving rules if it relies on conversions made before the change, and for such an event, whose wall time depends on the zone's rules, the time zone is needed, not merely the offset. An expiry or validity end set at a wall-clock time in a place, such as a certificate valid until noon on 12 July in Los Angeles, is such a future event. A date or time that names no moment, such as a birth date, a holiday or an anniversary, is a floating value held in a plain date or date-time type with no offset or zone. When the wall time a past event had where it happened must be recovered, its offset or time zone may be needed next to the instant. In code that runs on the user's own device, the local zone is determined by that device; where the device's zone is the user's preference, a display conversion with it is a conversion with the user's zone, and the value held stays an instant. A moment held as a bare number rather than a time type is judged by its own rule.

## Validator
Grep the hunk for a current-time call that returns a naive or host-local value, a naive or local date-time type, a lookup of the host's default zone, a local-time field accessor or formatter, a database column type without time zone, and a zone looked up by abbreviation. For each hit, open the declaration of the value at hunk scope, the variable, field, column or serialized key, and decide from its name and use whether it records a moment: something that happened (created, updated, logged, paid) or a moment computed when it is recorded (an expiry or a deadline set as now plus a duration). Trace the value to where the hunk stores it, sends it, compares it or turns it into date and clock fields, and note the zone used there. Skip future or recurring wall-clock events kept with their zone, dates that name no moment, and display conversions with the device's zone in code that runs on the user's own device when the code holds no other time-zone preference for that user. Validator question: **Does the hunk hold, store or exchange a recorded moment as a naive or host-local date-time, or turn one into date and clock fields with the host's default zone or a zone abbreviation rather than a zone the code names?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-43`, severity major, `file`, `symbol`, `code` = the line that creates, declares, stores or converts the naive or host-local value, `fix` = the value held in the language's instant or zone-aware type, stored in UTC, and converted with a named zone only at display, in the file's language, `rationale` = which moment the value records and where it loses its zone or borrows the host's).
