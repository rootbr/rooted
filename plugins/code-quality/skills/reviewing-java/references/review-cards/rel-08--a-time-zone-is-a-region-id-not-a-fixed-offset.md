---
title: A time zone that observes daylight saving is identified by a region ZoneId, never by a fixed offset
rule_id: REL-08
domain: reliability
triggers: ['ZoneOffset[.]of\(', 'ZoneId[.]of\("[+-]', 'ZoneOffset[.]ofHours\(', 'ZoneId[.]of\(', 'atZone\(', 'withZoneSameInstant\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A time zone that observes daylight saving is identified by a region ZoneId, never by a fixed offset

## Thesis
Code that converts between an instant and a local date-time for a place uses a region id such as `ZoneId.of("Europe/Berlin")` or `ZoneId.of("America/New_York")`, not a fixed offset such as `ZoneOffset.of("+01:00")`, `ZoneOffset.ofHours(-5)` or `ZoneId.of("+02:00")`, unless the offset is itself the datum (a value parsed from an ISO string, or UTC).

## Rationale
A `ZoneId` is one of two kinds: a fixed offset, "a fully resolved offset from UTC/Greenwich, that uses the same offset for all local date-times", or a geographical region, "an area where a specific set of rules for finding the offset from UTC/Greenwich apply". A place with daylight saving has two offsets in a year — Paris is one hour ahead of Greenwich in winter and two in summer — and only the region id carries the rules that pick the right one for a given instant. A fixed offset chosen while writing the code is right for half the year and off by an hour for the other half: schedules fire an hour early, deadlines and opening hours shift, and the error appears only on the day the clocks change. Region rules also track government changes that a hard-coded offset cannot.

## Example
```java
bad:  ZonedDateTime local = instant.atZone(ZoneOffset.of("+01:00"));   // Berlin
      LocalTime open = LocalTime.of(9, 0).atOffset(ZoneOffset.ofHours(-5)).toLocalTime();
good: ZonedDateTime local = instant.atZone(ZoneId.of("Europe/Berlin"));
      ZonedDateTime open = date.atTime(9, 0).atZone(ZoneId.of("America/New_York"));
```

## Limits
`ZoneOffset.UTC`, an offset parsed from an incoming ISO-8601 string, or an offset stored alongside the instant it belongs to, is the correct type: the offset is the data. A place that has no daylight saving and whose rules are documented as fixed may use a region id anyway, and is not flagged either way. `ZoneId.systemDefault()` is a region id and is out of scope here.

## Validator
On the triggered hunk find each fixed-offset construction — `ZoneOffset.of`, `ZoneOffset.ofHours`, `ZoneId.of` with a `+`/`-` string — and read what it stands for: a comment, a variable name, a nearby city or country, a schedule. Flag when the offset represents a place or a business locale rather than a datum received or stored with the instant. Validator question: **does this fixed offset stand in for a place whose offset changes during the year?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-08`, severity major, `file`, `symbol`, `code` = the offset construction quoted verbatim from the diff, `fix` = the region `ZoneId.of("Region/City")`, `rationale` naming the half of the year in which the offset is wrong).

## Source
`java.time.ZoneId` class Javadoc, Java SE 21 — "There are two distinct types of ID: Fixed offsets - a fully resolved offset from UTC/Greenwich, that uses the same offset for all local date-times; Geographical regions - an area where a specific set of rules for finding the offset from UTC/Greenwich apply"; "The actual rules, describing when and how the offset changes, are defined by ZoneRules". `java.time.ZoneOffset` class Javadoc — "The rules for how offsets vary by place and time of year are captured in the ZoneId class. For example, Paris is one hour ahead of Greenwich/UTC in winter and two hours ahead in summer".
