**Risk:** high: the edit changes behaviour on the order path, rollback is possible only by a new rollout, the build is red, and the disabling of re-sending is confirmed only by a flag test.
**From the reader:** answer the question on the acknowledgement timeout below; before approving the edit, re-run `mvn -q test` on the current tree.
**Not done:** JMH was not run against the baseline; `docs/routing.md` is not updated, the file is not in the directory; I did not run the build on the current tree; I did not verify that the tests lie outside the agent's write zone, because the directory has no edit history.
**Wrong if:** `build.log` was not taken from the current tree, or the 250 ms timeout in `Router.java` was set by the edit itself.
**Status:** failed; checked 5 tests in two classes and the linter; failed step: `mvn -q test` with `exit code: 1` on `RouterTest#ackTimeoutIsFourHundredMillis`; `./lint.sh` with `exit code: 0`.

## Done and verified

- Re-sending after an acknowledgement timeout is disabled by a flag that the router passes into the send decision: `src/main/java/order/Router.java:8` `retryOnTimeout = false`, then `src/main/java/order/Router.java:19` `Decision.send(order, ackTimeout, retryOnTimeout)`.
  Evidence: `RouterTest` ran three tests with one failure, `build.log:3` `Tests run: 3, Failures: 1`, and the test that failed is a different one, `build.log:4` `ackTimeoutIsFourHundredMillis:24 expected`.
  Counter-argument: the test `RouterTest#timeoutDoesNotRetry` reads only the flag, `src/test/java/order/RouterTest.java:11` `assertFalse(d.retry())`, and does not reproduce the timeout; whether it fails on a rollback of the edit, I did not check, because the class `Decision` is not in the directory.
- The build is red for one reason: the colleague's test expects an acknowledgement timeout of 400 ms, and the code has 250 ms.
  Log: `build.log:4` `expected: <400> but was: <250>`; code: `src/main/java/order/Router.java:7` `Duration.ofMillis(250)`; test: `src/test/java/order/RouterTest.java:25` `assertEquals(400, d.ackTimeout().toMillis());`.
  The log shows no other failures or errors: `build.log:3` `Errors: 0`, `build.log:6` `Failures: 0, Errors: 0`.
- I do not know whether the log was taken from the current tree: it points to a failure at line 24 of the test, but that line holds the router call, and the timeout check comes one line below.
  Log: `build.log:4` `ackTimeoutIsFourHundredMillis:24 expected`; test line: `src/test/java/order/RouterTest.java:24` `Decision d = router.route(new Order("SBER", 10));`; check: `src/test/java/order/RouterTest.java:25` `assertEquals(400`.
- The per-instrument limit is taken from the configuration: `src/main/java/order/Limits.java:12` `return config.limit(instrument);`, and the router checks the order quantity against it, `src/main/java/order/Router.java:16` `if (order.quantity() > limits.limit(order.instrument()))`.
  Evidence: the test `RouterTest#overLimitIsRejected` sets the limit through the configuration, `src/test/java/order/RouterTest.java:16` `new Limits(instrument -> 5)`, and did not fail in the log; `LimitsTest` has no failures, `build.log:6` `Tests run: 2, Failures: 0`.
  The source of `LimitsTest` is not in the directory, and I did not read what it checks.
- The linter raised no remarks: `build.log:10` `0 problems`, `build.log:11` `exit code: 0`.

## Default decisions

- I attribute the failure of `RouterTest#ackTimeoutIsFourHundredMillis` to a divergence of requirements, not to a defect of the edit. Basis: the task names only re-sending and the limit, `task.md:3` `take the per-instrument limit from the configuration instead of a constant`. Overturned by: a diff in which this edit itself changes `Duration.ofMillis` in `Router.java`.

## Question

- The colleague's test expects an acknowledgement timeout of 400 ms, while `src/main/java/order/Router.java:7` `Duration.ofMillis(250)` holds 250 ms; this is the only reason for the red build.\
  The answer decides what we fix: the constant in `Router.java` or the colleague's test.\
  I do not decide by default: the rollout changes behaviour on the order path and is rolled back only by a new rollout, `task.md:3` `rolled back only by a new rollout`, and the right value is known to the test's author or the operator, not to the code.\
  If 400 ms is already agreed: raise the constant to 400 ms in this edit. Consequence: the build turns green, and the rollout changes two behaviours on the order path at once. Cost of error: on a regression in production it is not visible which of the two changes caused it, and rollback goes only through a new rollout.\
  If the test ran ahead of the decision: keep 250 ms and bring the colleague's test to 250 ms. Consequence: the build turns green, the timeout stays what the code has now. Cost of error: if 400 ms is already agreed, the requirement disappears without a trace, and no test guards it any more.\
  Recommendation: the second option in this edit, and the move to 400 ms, if it is agreed, as a separate rollout together with the colleague's test. Basis: the task is limited to re-sending and the limit, and a rollout with one behaviour change on the order path is easier to analyse on a regression.\
  Which acknowledgement timeout do we roll out with this edit: 250 ms or 400 ms?

## Internal

- I read the five assigned files: `task.md`, `build.log`, `Router.java`, `Limits.java`, `RouterTest.java`; I did not run the build or the linter, the status and the test count are taken from `build.log`.
- The directory has no `LimitsTest`, `LimitsConfig`, `Decision`, `Order` or `lint.sh`: the log was taken from a fuller tree, and I have not seen the behaviour of `Decision.send`.
- The registry line for the decision above is not written into the project: the write zone of this task is only the report directory.
