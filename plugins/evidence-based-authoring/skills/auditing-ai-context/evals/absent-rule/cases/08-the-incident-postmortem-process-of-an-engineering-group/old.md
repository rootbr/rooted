# Incident Postmortems in Platform Engineering

This note describes how the platform engineering group writes, reviews and closes postmortems after production incidents. It applies to every team in the group and to every incident of severity 1 or 2.

## Purpose

A postmortem records what happened, why the system allowed it, and what we will change. It is written to help the next on-call engineer, not to judge the last one.

We write postmortems blamelessly. Contributing factors are described as conditions of the system, its tooling and its processes.

## When a postmortem is required

- Every severity 1 incident requires a postmortem.
- Every severity 2 incident requires a postmortem unless the incident commander and the owning team lead agree in writing that it adds nothing new.
- A severity 3 incident may get a postmortem if the owning team asks for one.
- A near miss that would have been severity 1 may get a postmortem at the incident commander's request.

## Roles

- **Incident commander**: ran the response and opens the postmortem document from the template within one business day.
- **Author**: an engineer from the team that owns the affected service, named by the incident commander when the document is opened.
- **Review chair**: a senior engineer from the rotating chair rota who runs the Thursday Postmortem Review that week.
- **Owning team lead**: accountable for the action items once the postmortem is approved.

## Writing the document

The author starts from the shared template. The template has five parts: summary, impact, timeline, contributing factors and action items.

The timeline is assembled from the incident channel, the paging history and the deploy log. Each entry has a timestamp in UTC and a source.

Impact is stated in numbers wherever possible: minutes of degraded service, failed requests, affected customers and any breached commitment.

## Review and approval

Every postmortem is presented by its author at the Thursday Postmortem Review within five business days of the incident. The review chair and the attendees question the author in the room, and the postmortem is approved when the chair records the decision in the meeting notes. A postmortem that misses its Thursday slot is carried to the next week and flagged in the group's weekly report.

The author books a slot on the review agenda as soon as the draft exists. Slots are twenty minutes long, and the agenda holds at most six postmortems per week.

Before the meeting, the author circulates the draft to the attendees by Wednesday noon so that they can read it in advance.

Attendees who cannot come may leave written questions in the draft, and the chair reads them out during the slot.

## Deadlines

| Step | Deadline |
|---|---|
| Document opened | 1 business day after the incident |
| Draft circulated | Wednesday noon before the review |
| Presented and approved | 5 business days after the incident |
| Action items filed | 2 business days after approval |

If the agenda is full, the review chair may add an extra session on Friday morning.

## Action items

Each action item has one owner, one due date and a link back to the postmortem. Action items are filed in the owning team's regular backlog and labelled with the incident number.

The owning team lead reviews open postmortem action items in the team's planning meeting. An action item may be closed as won't do only with a written reason in the item itself.

## Closing

A postmortem is closed when all of its action items are done or closed with a reason. The incident commander marks the document as closed and links it from the incident record.

Closed postmortems stay readable to the whole engineering organization. They are indexed by service, severity and contributing factor so that patterns across incidents can be found.

## Confidentiality

Postmortems are internal documents. Data copied from logs is redacted before the draft is circulated to the attendees.

A postmortem that touches a security incident is shared only with the review chair and the security team until the chair approves wider circulation.

## Questions

Questions about this process go to the platform engineering leads. Proposed changes to the template are discussed in the group's monthly retrospective.
