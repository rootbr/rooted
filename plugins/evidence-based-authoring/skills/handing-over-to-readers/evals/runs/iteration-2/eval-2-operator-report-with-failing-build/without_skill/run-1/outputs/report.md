# Change report: dispatch router (retryOnTimeout off, per-queue limit from config)

**Status: not ready to roll out. The build fails** (`mvn -q test` exit code 1; `./lint.sh` exit code 0).
**Risk:** this changes behaviour on the dispatch path. A rollout can only be undone by another rollout.
**What you need to do:** decide what the ack timeout should be (250 ms or 400 ms, see Decision 1). Until that is settled the build stays red.
**Not done:** `docs/routing.md` is not updated. JMH has not been run against the baseline.
**This report is wrong if** the 250 ms in `Router` is a value the agent introduced and not an existing one. I could not see a diff or a baseline, so I could not tell which it is.

## What is done

| Item | Where | State in the code |
|---|---|---|
| Resend after an ack timeout is turned off | `src/main/java/dispatch/Router.java:8` | `private final boolean retryOnTimeout = false;`, passed into `Decision.send(job, ackTimeout, retryOnTimeout)` (line 19) |
| The per-queue limit is read from configuration | `src/main/java/dispatch/Limits.java:12` | `return config.limit(queue);` (a `LimitsConfig` is passed in through the constructor) |
| The router uses that limit | `src/main/java/dispatch/Router.java:16` | `if (job.size() > limits.limit(job.queue()))` leads to `Decision.reject("over limit")` |

## What is verified (from build.log)

- `RouterTest`: 3 tests ran and 1 failed.
  - `timeoutDoesNotRetry` passes. It checks that `d.retry()` is false, which covers the retryOnTimeout change.
  - `overLimitIsRejected` passes. It checks that a job of size 10 is rejected when the configured limit is 5, which covers the limit coming from config.
  - **`ackTimeoutIsFourHundredMillis` fails.** The log line is `RouterTest.ackTimeoutIsFourHundredMillis:25 expected: <400> but was: <250>`. The test is at `RouterTest.java:25` (`assertEquals(400, d.ackTimeout().toMillis());`) and the value in the code is at `Router.java:7` (`Duration.ofMillis(250)`).
- `LimitsTest`: 2 tests ran and both passed. I could not see what they test because the test file is not in this directory.
- Lint reported 0 problems (exit 0).

## Not verified

- **Performance.** JMH was not run against the baseline, so I have no numbers for the dispatch path.
- **Documentation.** `docs/routing.md` is not updated. The file is outside this directory, so I did not check what it currently says.
- **Edge cases of the config limit.** I found no test for a queue that is missing from the configuration. I did not see `LimitsConfig`, so I don't know what `config.limit(queue)` does when a queue has no entry.
- **Scope of the diff.** I had no baseline or diff, so I can't confirm which lines the agent changed.

## Your decisions

**1. Ack timeout: 250 ms or 400 ms?**
A colleague wrote this test last week and it expects 400 ms. The code has 250 ms. The task doesn't say the timeout should change.
- If 400 ms is correct: change `Router.java:7` to `Duration.ofMillis(400)`. The build should then go green, but rerun it to confirm. Workers will get 400 ms before a job is treated as timed out.
- If 250 ms is correct: update or remove the colleague's test, and tell the colleague. The timeout stays at 250 ms.

Which ack timeout should production have, 250 ms or 400 ms?

**2. Should JMH run against the baseline before rollout?**
The rollout can only be undone by a new rollout, and no performance numbers exist yet.
- Run it first: rollout waits for the benchmark, and you have a baseline to compare against.
- Skip it: rollout is faster, but if the dispatch path regresses you only find out in production.

**3. Should `docs/routing.md` be updated in this change or separately?**
- In this change: the docs match the behaviour from the moment it ships.
- Separately: until that edit lands, the docs say resend-on-timeout is on and the limit is a fixed value.
