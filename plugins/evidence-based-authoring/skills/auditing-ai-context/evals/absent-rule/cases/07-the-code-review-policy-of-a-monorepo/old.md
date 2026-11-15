# Code review in the platform monorepo

This note describes how changes to the platform monorepo are reviewed and merged. It applies to every engineer with write access and to the bots that open pull requests on their behalf.

## Scope

The monorepo holds about forty packages under three top-level directories.

- services, which holds the deployable backends.
- libs, which holds shared libraries used by services and clients.
- clients, which holds the web and mobile applications.

Documentation-only changes follow the same process as code changes. Generated files are reviewed with the source that produces them.

## Who reviews

Every pull request is reviewed by the review desk, a rota of four engineers that changes every Monday. A pull request merges once two members of the desk on duty that week have approved it. Package maintainers may comment, but their approval does not count toward the two.

The rota is published in the team calendar, and each engineer serves on the desk about once a quarter. While on the desk, an engineer spends roughly half of each day on review and the rest on their own work.

Desk members review for correctness and readability. When a change needs knowledge of a package that no desk member has, the desk may ask a maintainer of that package for an opinion before approving.

## Requesting review

Open the pull request as a draft until the build passes. When it is green, mark it ready and add the review-desk label, which posts it to the queue of the desk.

Write a description that a desk member can follow without knowing the package. Say what the change does, why it is needed, and how it was tested. Link the ticket.

Keep pull requests small. A desk member reviews changes from every corner of the repository, so a change of more than four hundred lines is usually sent back to be split.

## Turnaround

| Size of change | First response from the desk | Expected approvals |
|---|---|---|
| Under 100 lines | 4 working hours | 2 |
| 100 to 400 lines | 1 working day | 2 |
| Over 400 lines | Sent back to be split | 2 |

If the desk has not responded within the target, ping the desk channel rather than individual members.

The desk lead reviews the response times at the end of each week and hands any open pull requests to the next rota with a short note.

## Merging

All changes land through the merge queue. The queue squashes each pull request into one commit and runs the full build again on top of the current main branch.

The queue admits a pull request when it has two desk approvals and every required check is green. A new push after approval clears both approvals.

If the rebuild in the queue fails, the pull request is removed from the queue and its author is notified. It keeps its approvals unless new commits are pushed.

## Security-sensitive paths

The security team has asked that every change touching authentication code be reviewed by one of its members. Such pull requests carry the security label, and one of the two desk approvals must come from a security engineer on the desk that week.

If no security engineer is on the desk, the desk lead asks the security team for a reviewer, whose approval then counts as one of the two.

## Exceptions and emergencies

During an incident, the on-call engineer may merge a fix with one desk approval. The fix is reviewed again by the full desk within one working day, and any follow-up lands as a normal pull request.

Reverts of a change merged in the last 24 hours need no approval at all. The author of the revert notifies the desk channel.

Dependency updates opened by the update bot are batched once a week and reviewed by the desk as a single pull request.

## Tooling

The merge bot enforces the approval count and the labels. Its configuration lives in the repository under the tooling package, and changes to it are reviewed like any other change.

The bot also posts a daily summary of the desk queue to the desk channel, listing each pull request with its age and its current approvals.
