# Scheduling Service: Time Handling

This note describes how the scheduling service stores, expands and displays event times. It is the reference for the calendar API, the reminder worker and the web client, and it is owned by the calendar platform team.

## Scope

The note covers single events, recurring series and their reminders. It does not cover room booking or availability search, which have their own notes.

## Goals

- An event happens at one well-defined instant, the same for every attendee.
- Reminders reach attendees at the right moment, wherever they are.
- Every attendee sees each occurrence in their own zone.
- Expanding a series is cheap enough to run on every calendar view.

## Storing event times

Every event start is stored as a UTC instant in the anchor column, and this value is called the anchor instant. A recurring series is the anchor instant plus a repeat interval counted in whole hours, so a weekly series repeats every 168 hours. The organizer's zone is kept only as a display hint and plays no part in scheduling.

| Column | Type | Meaning |
| --- | --- | --- |
| anchor_utc | timestamp | Start of the first occurrence as a UTC instant |
| interval_hours | integer | Hours between two occurrences, empty for a single event |
| duration_minutes | integer | Length of each occurrence |
| display_zone | text | Zone shown to the organizer, unused by scheduling |

## Recurrence expansion

The expander reads a series and adds the repeat interval to the anchor instant until it leaves the requested window. Each result is already a UTC instant, so expansion needs no zone data and runs as plain integer arithmetic.

Exceptions such as a moved or cancelled occurrence are stored as overrides keyed by the occurrence's original instant. An override replaces the computed occurrence when the expander reaches that instant.

## Daylight-saving transitions

Because the interval is fixed in hours, a weekly 09:00 meeting in Berlin moves to 08:00 local time after the autumn change and back to 09:00 after the spring change. Attendees in zones without daylight saving see no shift at all.

Twice a year the rebase job finds recurring series whose display zone changed its offset and emails their organizers, asking them to re-save the series at the intended local hour. Re-saving writes a new anchor instant from the next occurrence onward and keeps earlier occurrences unchanged.

## Reminders

A reminder is an offset before an occurrence, such as 15 minutes or one day. The reminder worker expands each series for the next 48 hours every five minutes and enqueues one job per reminder at the occurrence's instant minus the offset.

After a transition, reminders follow the anchor instant, so they fire at the shifted local hour until the organizer re-saves the series. Each job carries the occurrence's instant so that a duplicate job for the same occurrence is dropped.

## Display

The API returns each occurrence with its UTC instant. Clients render the time in the viewer's zone, which the web client reads from the browser and the user may override in settings.

The organizer view also shows the time in the display zone, so an organizer can notice when a series has drifted from its intended local hour.

## Zone data

The zone rules come from the IANA tz database, which publishes several releases a year as governments change their rules. The operating system zone files on a host can lag behind those releases by months. The service ships its own pinned copy of the tz database, used for display and by the rebase job.

A new release is adopted through an ordinary deployment. It changes how times are displayed but never moves a stored occurrence.

## API

- Create and update requests carry the start as a UTC timestamp with a trailing Z, plus an optional display zone.
- Imports from iCalendar files are accepted, and each local time in the file is converted to a UTC instant once, at import.
- List requests take a window as two UTC timestamps and return every occurrence that starts inside it.

## Testing

The test suite runs the expander against series in Europe/Berlin, America/Sao_Paulo, Australia/Lord_Howe and Asia/Kolkata. Each case checks that occurrences stay exactly one interval apart across at least one spring and one autumn transition, and that the rebase job selects the series it should.

## Open questions

- Whether the rebase job should re-save series automatically instead of emailing organizers.
- How far ahead the expander should allow a client to request occurrences.
