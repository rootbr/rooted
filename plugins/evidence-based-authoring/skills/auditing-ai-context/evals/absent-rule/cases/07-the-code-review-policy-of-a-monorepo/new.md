# Code review in the platform monorepo

This note describes how changes to the platform monorepo are reviewed and merged. It applies to every engineer with write access and to the bots that open pull requests on their behalf.

## Scope

The monorepo holds about forty packages under three top-level directories.

- services, which holds the deployable backends.
- libs, which holds shared libraries used by services and clients.
- clients, which holds the web and mobile applications.

Documentation-only changes follow the same process as code changes. Generated files are reviewed with the source that produces them.

## Who reviews

Each package keeps an owners file at its root that lists the engineers responsible for it. A pull request needs one approval from an owner of every package it touches. No review desk sign-off is needed, even for changes that span many packages.

The reviewer is chosen by what the change touches, not by whose turn it is. Approvals from people outside the owning group carry no weight, however many of them a change collects. Anyone may leave comments, and owners are expected to read them.

Owners review for correctness and fit with the package, not for code style, which the formatter already settles. An approval is a statement about the code as merged, not a courtesy to the author.

## Owners files

An owners file lists at least three engineers, so that a review is not blocked by the absence of one person. Owners are added or removed by a pull request to the owners file, approved by an existing owner of that package.

Every package must have an owners file. If a package has no owners file, the merge bot refuses every pull request that touches it.

## Requesting review

Open the pull request as a draft until the build passes. When it is ready, mark it so, and the merge bot requests review from the owners of each package it touches.

Newcomers often expect that a green build is enough to merge. It is not, because the build checks behaviour while the owner checks whether the change belongs in the package.

Write a description that an owner can follow quickly. Say what the change does, why it is needed, and how it was tested. Link the ticket.

Keep pull requests small, and split a change that touches many packages into one pull request per package wherever the packages can land independently.

## Turnaround

| Size of change | First response from an owner |
|---|---|
| Under 100 lines | 4 working hours |
| 100 to 400 lines | 1 working day |
| Over 400 lines | 3 working days |

If no owner has responded within the target, ping the package channel named in the owners file rather than individual owners.

Each package lead looks at the response times of their package once a month and adds owners where reviews wait too long.

## Merging

All changes land through the merge queue. Git offers several ways to land a branch, including merge commits, squashing and rebasing. The merge queue accepts only squash merges, and the other methods are disabled in the repository settings. The queue runs the full build again on top of the current main branch.

The queue admits a pull request when every touched package has an owner approval and every required check is green. The merge queue never lands a pull request whose required checks have not finished on the exact commit being merged. A new push after approval clears the approvals.

If the rebuild in the queue fails, the pull request is removed from the queue and its author is notified. It keeps its approvals unless new commits are pushed.

## Security-sensitive paths

The security team has asked that every change touching authentication code be reviewed by one of its members. Such pull requests carry the security label, and the merge bot adds the security team as a required owner alongside the package owners. That request does not extend to the client libraries, which call the auth service but hold no secrets.

## Exceptions and emergencies

During an incident, the on-call engineer may merge a fix with the approval of any one owner of the affected service. The fix is reviewed again by the package owners within one working day, and any follow-up lands as a normal pull request.

Reverts of a change merged in the last 24 hours need no approval at all. The author of the revert notifies the package channel.

Dependency updates opened by the update bot are grouped by package, and each group is reviewed by the owners of that package.

## Tooling

The merge bot reads the owners files and enforces the approvals and the labels. Its configuration lives in the repository under the tooling package, which has its own owners file and is reviewed like any other package.

The bot also posts a daily summary to each package channel, listing the open pull requests of that package with their age and their current approvals.
