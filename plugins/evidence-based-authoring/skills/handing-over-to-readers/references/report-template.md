# Report template for the operator

The first page is a handover: a reader who was away learns in five lines the risk, what is expected of him, what is not done, and the condition under which the conclusion is wrong. The output of the checks fills the status line, never prose. Then come the claims with their evidence, the decisions, the questions, the internal block. `scripts/check_report.py --profile operator` checks this form; it accepts the English labels below and their Russian equivalents.

```markdown
**Risk:** medium: the change touches the order path, the tests on it are green, jcstress was not run.
**From the reader:** approve the diff of `src/order/Router.java` and answer the question below.
**Not done:** the JMH run against the baseline; the documentation `docs/routing.md` is not updated.
**Wrong if:** the per-instrument limit is set at runtime rather than in `limits.yaml`.
**Status:** findings; 14 units checked; failed steps: `mvn test` (exit 1, 1 failure in RouterTest).

## Claims
- The retry on timeout is off: `src/order/Router.java:118` `retryOnTimeout = false`; evidence: `RouterTest#timeoutDoesNotRetry` fails when the change is reverted.
- The limit comes from the configuration, not from a constant: `src/order/Limits.java:42` `return config.limit(instrument)`; evidence: the test `LimitsTest#readsFromConfig`, exit 0.

## Decisions
- The field name `retryOnTimeout` stays as in the neighbouring class; basis: the project's vocabulary; overturned by: a rename in `Sender`. Recorded in the registry.

## Questions
- The acknowledgement timeout is 250 ms, and the exchange's p99 response is 180 ms. The answer changes the retry limit and its test; the decision is irreversible after the rollout to production. Keep 250 ms or raise it to 400?

## Internal
- Transcript: 6 of 6 assigned files read; `docs/routing.md` opened, not changed.
```

Rules of the form:

- The four first-page lines and the status line stand first, in this order. The status value is one of `clean`, `findings`, `failed`, `not-run`; with `clean` and `findings` the count of checked units and the list of failed steps, or "none", stand beside it.
- A claim about code carries a `path:line` anchor and the line's fragment in the adjacent code span; a claim about behaviour carries evidence that `references/evidence.md` accepts. A claim with neither stays out of the report.
- The riskiest claim stands first.
- A question follows the card: the fact with its decisive number, what the answer changes and why the decision was not taken by default, one question at the end. Options, where there are any, each carry their consequence and the cost of error.
- The prose carries no identifiers of runs, workflows and agents; a commit hash is allowed as what an approval is bound to.
- What the prose carries beyond the claims — the motive, the decisions, what is unverified — follows the bullet in `references/rules.md` § What the research adds.
