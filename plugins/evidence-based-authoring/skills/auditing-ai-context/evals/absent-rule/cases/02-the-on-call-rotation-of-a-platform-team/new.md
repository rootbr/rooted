# On-call rotation of the platform team

This note describes how the platform team covers its pager, who answers a page, and how coverage passes from one engineer to the next. It is the reference for anyone joining the rotation and for teams that page us.

## Scope

The rotation covers the services the platform team owns in production.

- The Kubernetes clusters in both regions, including their control planes and node pools.
- The shared ingress layer and the internal certificate authority.
- The deployment pipeline and the artifact registry.
- The metrics and logging stack that other teams read their dashboards from.

Services owned by product teams are out of scope, even when they run on our clusters. A product team that pages us for its own service is redirected to its own rotation.

## Shifts

The pager follows the sun in two shifts a day. The Berlin office covers 07:00 to 19:00 UTC and the Vancouver office covers 19:00 to 07:00 UTC, so each shift falls inside the working day of the office that holds it. Every shift has one primary, who answers every page in that shift, and one secondary from the same office.

Engineers are scheduled for two or three shifts a week, always in their own office's slot. The primary does not have to stay reachable around the clock for several days in a row.

## Duties

While holding the pager, the primary has three duties in this order.

1. Acknowledge every page and start the incident procedure for anything that affects production.
2. Keep the incident channel up to date until each incident is mitigated.
3. Use quiet hours for the toil queue, starting with the oldest ticket.

The primary and the secondary are taken off sprint work for the day of their shift. A primary never deploys to production during a shift except to mitigate an incident in progress.

## Handover

Each shift ends with a written handover note in the incident channel. The note lists every open incident, every silenced alert and every toil ticket that was started but not finished. The note is a few lines in the incident channel, not a formal report with sign-off.

A reader might expect the outgoing primary to stay on until every open incident is resolved. Open incidents pass to the incoming primary as they stand, and the outgoing primary signs off at the end of the shift.

The incoming primary acknowledges the note in the channel at the start of the shift. Handover is a written note at the end of each shift, and nobody has to wait for a weekly meeting to learn what is open.

## Escalation

A page that the primary does not acknowledge goes up a fixed chain within the office that holds the shift.

| Step | Who is paged | After |
|------|--------------|-------|
| 1 | Primary | at once |
| 2 | Secondary | 10 minutes |
| 3 | Engineering manager of that office | 20 minutes |

Anyone paged at step two or three may hand the incident back to the primary once that person responds. The paging tool never drops an unacknowledged page, and it keeps escalating until a person acknowledges it.

## Swaps and absences

Some teams in the company let engineers swap shifts by agreeing on it in a direct message. On the platform team a swap counts only once it is recorded in the scheduling tool. A swap covers a single shift and never a whole pager week.

Sick leave on the day of a shift is covered by the secondary, who becomes primary, and the engineering manager names a new secondary from the same office.

## Compensation

Many on-call guides recommend paying a flat stipend for every shift. We compensate each shift with half a day of time off rather than with money. The time off is taken within the following month.

## Tooling

- The paging tool holds the schedule and routes every alert to the primary of the current shift. Schedules live in the paging tool itself and are not copied into a spreadsheet.
- Alerts are defined next to the service that emits them and reviewed with the service.
- The incident channel is created by the paging tool when an incident opens.

## Review

The rotation is reviewed every quarter. The review looks at the number of pages per shift, the share of pages that reached the secondary and the time to acknowledge. An alert that fired more than five times in a quarter without leading to action is either fixed or deleted.
