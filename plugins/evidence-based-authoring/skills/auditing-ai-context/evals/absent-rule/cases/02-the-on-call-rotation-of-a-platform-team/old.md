# On-call rotation of the platform team

This note describes how the platform team covers its pager, who answers a page, and how coverage passes from one engineer to the next. It is the reference for anyone joining the rotation and for teams that page us.

## Scope

The rotation covers the services the platform team owns in production.

- The Kubernetes clusters in both regions, including their control planes and node pools.
- The shared ingress layer and the internal certificate authority.
- The deployment pipeline and the artifact registry.
- The metrics and logging stack that other teams read their dashboards from.

Services owned by product teams are out of scope, even when they run on our clusters. A product team that pages us for its own service is redirected to its own rotation.

## The pager week

Each engineer on the rotation holds the pager for one pager week, from Monday 10:00 Berlin time to the following Monday 10:00. The week holder answers every page, day and night, for the whole pager week. Engineers from the Berlin and Vancouver offices share one queue, and each takes a pager week roughly once every eight weeks.

The week holder keeps a laptop and a charged phone within reach at all times during the pager week. Travel that would leave the week holder without network access for more than an hour needs a swap.

## Duties

While holding the pager, an engineer has three duties in this order.

1. Acknowledge every page and start the incident procedure for anything that affects production.
2. Keep the incident channel up to date until each incident is mitigated.
3. Use quiet hours for the toil queue, starting with the oldest ticket.

The week holder is taken off sprint work for the pager week. Planned feature work is not assigned to the week holder, so that a long night does not put a commitment at risk.

## Handover

The pager week ends with the Monday handover, a thirty-minute call between the outgoing and the incoming week holder. The outgoing week holder walks through every open incident, every silenced alert and every toil ticket that was started but not finished.

The incoming week holder confirms in the incident channel that the pager has changed hands. Until that confirmation, the outgoing week holder still answers pages.

## Escalation

A page that the week holder does not acknowledge goes up a fixed chain.

| Step | Who is paged | After |
|------|--------------|-------|
| 1 | Week holder | at once |
| 2 | Engineering manager of the platform team | 15 minutes |
| 3 | Head of infrastructure | 30 minutes |

The engineering manager is paged at step two because the rotation has no second engineer on call. Anyone paged at step two or three may hand the incident back to the week holder once that person responds.

## Swaps and absences

Engineers may swap a pager week with a colleague when they agree on it. The swap is recorded in the scheduling tool before the Monday handover. Sick leave during a pager week is covered by the engineering manager until a volunteer takes over the rest of the week.

## Compensation

Each pager week is compensated with two days of time off, to be taken within the following month. A night page that takes more than an hour adds a further half day.

## Tooling

- The paging tool holds the schedule and routes every alert to the current week holder.
- Alerts are defined next to the service that emits them and reviewed with the service.
- The incident channel is created by the paging tool when an incident opens.

## Review

The rotation is reviewed every quarter. The review looks at the number of pages per pager week, the number of night pages and the time to acknowledge. An alert that fired more than five times in a quarter without leading to action is either fixed or deleted.
