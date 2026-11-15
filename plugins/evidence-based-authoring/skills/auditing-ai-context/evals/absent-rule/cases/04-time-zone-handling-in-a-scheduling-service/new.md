# Scheduling Service: Time Handling

This note describes how the scheduling service stores, expands and displays event times. It is the reference for the calendar API, the reminder worker and the web client, and it is owned by the calendar platform team.

## Scope

The note covers single events, recurring series and their reminders. It does not cover room booking or availability search, which have their own notes.

## Goals

- An event created for a local hour in a city happens at that hour in that city on every date of its series.
- Reminders reach attendees at the right moment, wherever they are.
- Every attendee sees each occurrence in their own zone.
- Expanding a series is cheap enough to run on every calendar view.

## Storing event times

Every event start is stored as a local wall-clock date and time together with an IANA zone name such as Europe/Berlin. A recurring series is a recurrence rule over local dates, and each occurrence becomes a UTC instant only when it is expanded. The zone belongs to the event and is chosen by the organizer when the event is created.

The organizer picks the zone from a list in the event form. The zone comes from the organizer's choice in the event form rather than from a guess based on the network address of the request.

| Column | Type | Meaning |
| --- | --- | --- |
| start_local | timestamp without zone | Wall-clock start of the first occurrence |
| zone | text | IANA zone name of the event |
| rrule | text | Recurrence rule over local dates, empty for a single event |
| duration_minutes | integer | Length of each occurrence |

## Recurrence expansion

The expander reads a series rule and produces the local dates of its occurrences within a requested window. For each local date it combines the stored wall-clock time with the event's zone and converts the result to a UTC instant. The gap between two occurrences is not a fixed count of hours, since a week that crosses a transition is an hour shorter or longer.

Some calendar products store each occurrence as a separate row as soon as a series is created. This service does not materialise occurrences ahead of time, so an edit to a series touches a single row.

Exceptions such as a moved or cancelled occurrence are stored as overrides keyed by the occurrence's original local date. An override replaces the computed occurrence when the expander reaches that date.

## Daylight-saving transitions

When a local time falls in a spring gap, the occurrence moves forward by the length of the gap. When a local time occurs twice in an autumn overlap, the expander takes the earlier of the two instants.

Because the wall-clock time is what is stored, a series keeps its local hour across every transition. Organizers do not have to edit a series after a clock change to keep it at its usual hour.

Attendees in other zones see the occurrence move by an hour in their own calendar when only one of the two zones changes its clocks. There is no rebase job, and organizers receive no email around the spring and autumn clock changes.

## Reminders

A reminder is an offset before an occurrence, such as 15 minutes or one day. The reminder worker expands each series for the next 48 hours every five minutes and enqueues one job per reminder at the occurrence's UTC instant minus the offset. Reminder jobs are written to the shared job queue rather than registered as cron entries on the worker hosts.

Each job carries the occurrence's UTC instant so that a duplicate job for the same occurrence is dropped. A reminder is never sent for an occurrence that has been cancelled or deleted.

Reminders are optional for every event. When an event has no reminder setting, no notification is sent before it starts.

## Display

The API returns each occurrence with its UTC instant, the event's zone and the local wall-clock time in that zone. Clients render the time in the viewer's zone, which the web client reads from the browser and the user may override in settings.

Where the viewer's zone differs from the event's zone, the client also shows the time in the event's zone beside it.

## Zone data

The zone rules come from the IANA tz database, which publishes several releases a year as governments change their rules. The operating system zone files on a host can lag behind those releases by months. The service therefore does not read zone rules from the host but ships its own pinned copy of the tz database.

A new release is adopted through an ordinary deployment, after which future occurrences are expanded under the new rules.

## API

- Create and update requests carry the start as a local date-time string without an offset, plus a zone field holding an IANA name.
- Imports from iCalendar files are accepted. The iCalendar standard allows a floating time that carries no zone at all. The import endpoint does not accept floating times and asks the user to pick a zone instead.
- List requests take a window as two UTC timestamps and return every occurrence that starts inside it.

## Testing

The test suite runs the expander against series in Europe/Berlin, America/Sao_Paulo, Australia/Lord_Howe and Asia/Kolkata. Each case checks occurrences across at least one spring and one autumn transition, including a local time inside a gap and one inside an overlap.

## Open questions

- Whether organizers should be able to change the zone of an existing series without moving its occurrences in local time.
- How far ahead the expander should allow a client to request occurrences.
