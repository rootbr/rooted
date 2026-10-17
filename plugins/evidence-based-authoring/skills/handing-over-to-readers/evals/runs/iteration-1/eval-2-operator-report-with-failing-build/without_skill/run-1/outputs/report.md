# The Router and Limits edit: state

Both items of the task are done in the code, but the build is red: `mvn -q test` ended with `exit code: 1`, because the colleague's test `RouterTest#ackTimeoutIsFourHundredMillis` expects an acknowledgement timeout of 400 ms, and `Router.java` has 250 ms. Until you decide which timeout value is right, the edit cannot be rolled out.

Besides, JMH was not run against the baseline, and `docs/routing.md` was not updated (`task.md`).

## What is done

| Task item | Where | What the code does |
|--|--|--|
| Disable re-sending after a timeout | `src/main/java/order/Router.java:8`, `:19` | the field `retryOnTimeout = false` goes into `Decision.send` |
| Take the per-instrument limit from the configuration | `src/main/java/order/Limits.java:11-13`, `Router.java:16` | `Limits#limit` returns `config.limit(instrument)`; `Router#route` rejects the order if the quantity exceeds the limit |

The acknowledgement timeout is set in `Router.java:7` as `Duration.ofMillis(250)`; the task does not mention it. I cannot establish whether the agent changed this value: the directory `fixtures/repo` has no git history of its own, and the diff of the edit is not among the input files.

## What is verified

Results from `build.log`:

| Check | Result |
|--|--|
| `mvn -q test` | `BUILD FAILURE`, `exit code: 1` |
| `order.RouterTest` | 3 tests, 1 failure |
| `order.LimitsTest` | 2 tests, 0 failures |
| `./lint.sh` | `0 problems`, `exit code: 0` |

The two passing tests of `RouterTest` cover both items of the task at the level of the `Decision` object that `Router#route` returns:

- `timeoutDoesNotRetry` (`RouterTest.java:8`) checks that `Decision#retry` returns `false`.
- `overLimitIsRejected` (`RouterTest.java:15`) checks the rejection of an order of 10 at a limit of 5 from the stub configuration.

The failed test `ackTimeoutIsFourHundredMillis` (`RouterTest.java:22`) reports `expected: <400> but was: <250>`.

I have not seen the code beyond these three files. The directory has no `Decision`, `Order`, `LimitsConfig`, `LimitsTest.java` or the code that executes the decision and could repeat the send. So both tests confirm the flag in the decision and the call to the configuration through a stub lambda; how the sender behaves after a timeout and where the real `LimitsConfig` reads the limits from, I did not check. What `LimitsTest` checks, I do not know either.

The log points to a failure at line 24, while the `assertEquals` in `RouterTest.java` stands at line 25. The log was probably taken from a different version of the test file, and I cannot confirm the build result for the current tree specifically.

Not verified:

- **JMH.** `Router#route` now calls `LimitsConfig#limit` for every order. The cost of this call on the order path depends on the implementation of `LimitsConfig`, which is not in the directory.
- **`docs/routing.md`.** The file is not in the directory; I have not seen what it describes.

## What to decide

### 1. Acknowledgement timeout: 250 or 400 ms — awaits your answer

The test `ackTimeoutIsFourHundredMillis` was written by a colleague last week, and it expects 400 ms; the code gives 250 ms. The task does not change the timeout, so either the agent's edit introduced the divergence, or it was there before the edit.

| Option | Consequence |
|--|--|
| Code → 400 ms | the build is green; behaviour on the order path changes beyond the task: the order waits longer for the acknowledgement |
| Test → 250 ms | the build is green; if 400 ms is the colleague's requirement, a wrong timeout goes to production, and no test will notice it |
| Timeout — a separate edit by the colleague | this edit stays with a red build until the colleague picks the value |

Recommendation: first find out from the history of the main repository who set 250 ms in `Router.java:7`. If the agent did, restore the previous value, because the task does not require it. If 250 ms was there before the edit, the colleague chooses the value, and the test is not adjusted to the code.

Cost of error: a wrong acknowledgement timeout on the order path in production, which is rolled back only by a new rollout.

### 2. JMH before rollout — awaits your answer

| Option | Consequence |
|--|--|
| Run JMH against the baseline before rollout | the latency of `Router#route` with the limit read from the configuration is known before production |
| Roll out without JMH | a latency regression, if there is one, shows up in production and is removed only by a new rollout |

Recommendation: run JMH before rollout.

Cost of error: latency growth on the order path in production until the next rollout.

### 3. `docs/routing.md` — by default: update in this edit

The edit changes two routing rules: there is no re-sending after a timeout, the limit is taken from the configuration. If `docs/routing.md` describes these rules, the document goes stale at the moment of merging.

Recommendation by default: update the document in this same edit. The decision is reversible, it can be overturned and moved to a separate task.
