# Incident Postmortems in Platform Engineering

This note describes how the platform engineering group writes, reviews and closes postmortems after production incidents. It applies to every team in the group and to every incident of severity 1 or 2.

## Purpose

A postmortem records what happened, why the system allowed it, and what we will change. It is written to help the next on-call engineer, not to judge the last one.

Some organizations assign a numeric blame score to each contributing factor. Our template has no such score, and contributing factors are described only as conditions of the system, its tooling and its processes.

## When a postmortem is required

- Every severity 1 incident requires a postmortem.
- Every severity 2 incident requires a postmortem unless the incident commander and the owning team lead agree in writing that it adds nothing new.
- A severity 3 incident may get a postmortem if the owning team asks for one.
- A near miss that would have been severity 1 may get a postmortem at the incident commander's request.

## Roles

- **Incident commander**: ran the response, opens the postmortem document from the template within one business day and assigns the reviewers.
- **Author**: an engineer from the team that owns the affected service, named by the incident commander when the document is opened.
- **Reviewers**: two engineers from teams other than the author's, drawn from the group's review rota.
- **Owning team lead**: accountable for the action items once the postmortem is approved.

## Writing the document

The author starts from the shared template. When no single team clearly owns the affected service, the author is taken from the incident commander's own team. The template has five parts: summary, impact, timeline, contributing factors and action items.

The timeline is assembled from the incident channel, the paging history and the deploy log. It is built from these records rather than from anyone's recollection of the night. Each entry has a timestamp in UTC and a source.

Impact is stated in numbers wherever possible: minutes of degraded service, failed requests, affected customers and any breached commitment.

## Review and approval

Every postmortem is reviewed in its own document by the two assigned reviewers. Reviewers comment directly on the text, the author answers or revises, and the postmortem is approved when both reviewers have marked it approved in the document. A postmortem is never reviewed in a meeting, and its author is not asked to walk a room through it.

The author marks the draft ready for review as soon as every part of the template is filled in. Authors do not book a slot at the Thursday Postmortem Review, since approval happens entirely in the document.

Each reviewer answers within three business days of the draft being marked ready. If a reviewer has not responded by then, the incident commander replaces them from the rota.

A reviewer who disagrees with a contributing factor says so in a comment, and the two reviewers settle it with the author before either of them approves.

## Deadlines

| Step | Deadline |
|---|---|
| Document opened | 1 business day after the incident |
| Draft marked ready | 6 business days after the incident |
| Approved by both reviewers | 10 business days after the incident |
| Action items filed | 2 business days after approval |

The author has ten business days in all. The author gets two full working weeks rather than one, because the timeline is rarely complete within the first few days. A postmortem not approved by then is flagged in the group's weekly report.

## Action items

Each action item has one owner, one due date and a link back to the postmortem. Items are filed in the owning team's regular backlog instead of a separate tracker that someone would have to remember to check. They are labelled with the incident number.

The owning team lead reviews open postmortem action items in the team's planning meeting. An action item may be closed as won't do only with a written reason in the item itself.

A common view in the group is that a postmortem with no action items is an unfinished postmortem. We disagree, and a postmortem that finds nothing worth changing is approved like any other one.

## Closing

A postmortem is closed when all of its action items are done or closed with a reason. The incident commander marks the document as closed and links it from the incident record.

Closed postmortems stay readable to the whole engineering organization. They are indexed by service, severity and contributing factor so that patterns across incidents can be found.

## Confidentiality

Postmortems are internal documents. The postmortem document never contains customer names, account identifiers or credentials copied from logs.

The security team runs its own disclosure review for incidents that exposed customer data. That review is separate from this process, and a postmortem may be approved before the disclosure review has concluded.

## Questions

Questions about this process go to the platform engineering leads. Proposed changes to the template are discussed in the group's monthly retrospective.
