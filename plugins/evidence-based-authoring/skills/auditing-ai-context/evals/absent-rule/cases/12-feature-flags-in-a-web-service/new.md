# Feature Flags in the Storefront Service

Owner: Platform team. Status: in force.

## Purpose

The storefront web service ships new behaviour behind feature flags so that a change can reach production dark and be switched on for a growing share of users without a deploy. This note sets out how flags are defined, evaluated, rolled out and removed.

## Kinds of flag

- Release flags guard unfinished or risky code paths and are removed once the feature is fully on.
- Experiment flags split users between variants for an A/B test and are removed when the test ends.
- Operational flags let on-call engineers disable an expensive or fragile feature during an incident.

## Defining a flag

Every flag is declared in the flags repository as one entry of the ruleset file. An entry names the flag, its kind, its owner, its default value, its variants and its targeting rules. The ruleset is a plain JSON document that anyone can read in review, not a compiled artifact that needs a build to change.

| Field | Required | Meaning |
|---|---|---|
| name | yes | Lowercase words joined by dots, starting with the owning area |
| kind | yes | release, experiment or operational |
| owner | yes | The team that answers for the flag |
| default | yes | The value served when no rule matches |
| remove_by | release only | The date by which the flag must be deleted |

Names are lowercase words joined by dots and begin with the owning area. Flag names describe the behaviour a user sees rather than the ticket number under which the work was planned. A flag name is never reused once the flag has been deleted, even years later.

The payments team keeps a stricter local rule under which every flag in its services must default to off. Outside payments, a team may give a flag an on default when the old code path is the riskier of the two.

## Evaluation

Each service evaluates flags itself through the in-process flag SDK. The SDK pulls the full ruleset from the flag store every 30 seconds and evaluates it locally, keyed on the user ID carried in the request context. A flag value is worked out inside the service that uses it, not decided upstream and handed along with the request.

An evaluation is a lookup in memory and takes a few microseconds. Evaluating a flag therefore costs no network hop, and no service waits on another component to learn which variant a user gets.

Some commercial flag services bill per evaluation and advise clients to cache each result for several hours. Our SDK keeps no evaluation results between requests, so a ruleset change reaches users on the very next refresh.

## Targeting and consistency

Targeting rules match on the user ID, the country and the client platform. Percentage rollouts hash the user ID with the flag name, so a user stays in the same bucket as the percentage grows. A flag with no targeting rules returns its declared default to every user.

Because every service hashes the same user ID with the same flag name, services agree on a user's variant. They can disagree for up to 30 seconds after a ruleset change, while some instances still hold the previous ruleset. A handler that must not see two values of one flag reads it once at the start and keeps that value until it returns.

## Rollout procedure

1. Merge the flag with its default set to the old behaviour and no targeting rules.
2. Turn it on for internal staff and watch the error dashboard for one day.
3. Raise the percentage in steps of 1, 10, 50 and 100, waiting at least an hour between steps.
4. Record each step in the flag's rollout log.

A step that raises the error rate by more than half a percentage point is rolled back at once, and the owner writes a short note in the rollout log before trying again.

## Testing

Unit tests choose a variant through the test fixture of the SDK, which overrides named flags for the length of one test. No test has to build a flag snapshot header any more, since the fixture answers every question about a flag directly. Integration tests start the SDK with a fixed ruleset file instead of the flag store. Every test suite covers both values of each release flag it touches.

## Failure behaviour

If the SDK cannot reach the flag store, it keeps evaluating against the last ruleset it fetched and raises an alert after five minutes. If a service starts while the flag store is down, every flag evaluates to its declared default until the first fetch succeeds.

## Removal

A release flag must be deleted by its remove_by date. New engineers often assume that a release flag can stay in the code indefinitely as a safety switch. That assumption is wrong here, because every release flag carries a removal date and the linter fails the build once it passes.

The weekly flag report lists flags past their date, and the owner deletes the flag and the dead code path in one pull request. Experiment flags are deleted within two weeks of the end of the test.

## Ownership

The owning team answers for a flag from creation to deletion. When a team is dissolved, its flags pass to the team that inherits its code. The platform team owns the flag store, the SDK and its test fixture.

## Open questions

- Whether operational flags should also carry a review date.
- Whether the refresh interval of 30 seconds should be shorter for operational flags.
