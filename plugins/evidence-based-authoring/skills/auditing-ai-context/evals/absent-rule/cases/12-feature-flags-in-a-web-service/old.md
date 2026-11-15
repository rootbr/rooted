# Feature Flags in the Storefront Service

Owner: Platform team. Status: in force.

## Purpose

The storefront web service ships new behaviour behind feature flags so that a change can reach production dark and be switched on for a growing share of users without a deploy. This note sets out how flags are defined, evaluated, rolled out and removed.

## Kinds of flag

- Release flags guard unfinished or risky code paths and are removed once the feature is fully on.
- Experiment flags split users between variants for an A/B test and are removed when the test ends.
- Operational flags let on-call engineers disable an expensive or fragile feature during an incident.

## Defining a flag

Every flag is declared in the flags repository as one entry of the ruleset file. An entry names the flag, its kind, its owner, its default value, its variants and its targeting rules. A pull request to the ruleset needs approval from the flag's owner and from one platform engineer.

| Field | Required | Meaning |
|---|---|---|
| name | yes | Lowercase words joined by dots, starting with the owning area |
| kind | yes | release, experiment or operational |
| owner | yes | The team that answers for the flag |
| default | yes | The value served when no rule matches |
| remove_by | release only | The date by which the flag must be deleted |

Names are lowercase words joined by dots and begin with the owning area, as in checkout.express-pay.

## Evaluation

All flags are evaluated once per request by the edge gateway. The gateway writes every result into the X-Flag-Snapshot header, and downstream services read flag values from that header only. Services never call the flag store themselves.

The flag store pushes a new ruleset to the gateway within a few seconds of a merge to the flags repository. The gateway evaluates every active flag for every request, which keeps the snapshot complete for whichever service reads it.

## Targeting and consistency

Targeting rules match on the user ID, the country and the client platform. Percentage rollouts hash the user ID with the flag name, so a user stays in the same bucket as the percentage grows.

Because the snapshot is computed once at the edge, every service that handles a request sees the same value for a flag, even if the ruleset changes while the request is in flight. A request that fans out to five services therefore never mixes two variants of one flag.

## Rollout procedure

1. Merge the flag with its default set to off and no targeting rules.
2. Turn it on for internal staff and watch the error dashboard for one day.
3. Raise the percentage in steps of 1, 10, 50 and 100, waiting at least an hour between steps.
4. Record each step in the flag's rollout log.

A step that raises the error rate by more than half a percentage point is rolled back at once, and the owner writes a short note in the rollout log before trying again.

## Testing

Unit tests read flags through a small helper that parses the snapshot header, so a test sets the header on the fake request to choose a variant. Integration tests run against a gateway stub that emits a fixed snapshot. Every test suite covers both values of each release flag it touches.

## Failure behaviour

If the gateway cannot reach the flag store, it keeps serving the last ruleset it received and raises an alert after five minutes. If a request arrives at a service without a snapshot header, the helper treats every flag as its default value and logs a warning.

## Removal

A release flag must be deleted by its remove_by date. The weekly flag report lists flags past their date, and the owner deletes the flag and the dead code path in one pull request. Experiment flags are deleted within two weeks of the end of the test.

Operational flags have no removal date and stay for as long as the feature they guard.

## Ownership

The owning team answers for a flag from creation to deletion. When a team is dissolved, its flags pass to the team that inherits its code. The platform team owns the flag store, the gateway evaluation and the helper library.

## Open questions

- Whether operational flags should also carry a review date.
- Whether the rollout log should move from the wiki into the ruleset entry.
