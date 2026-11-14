The task was to stop re-sending a job after an acknowledgement timeout, and to read the per-queue limit from configuration. Both edits are in the code, but the build is red. A colleague's test expects the router to wait 400 milliseconds for an acknowledgement. The code waits 250. 

## What changed

How it works now. The router checks the size of a job against the limit of its queue. That limit now comes from configuration instead of a constant. A job a worker did not acknowledge in time used to be sent again. Now it is not.

```
                          before             now
re-send after a timeout   yes                no
limit of a queue          a constant         read from configuration
```

## The red build

Now the red build. Four of five tests passed. The two router tests for this change pass: no re-send, and a job over the limit is rejected. The colleague's test fails. I cannot tell whether the 250 came with this change or was there before.

```
[ERROR] RouterTest.ackTimeoutIsFourHundredMillis:25 expected: <400> but was: <250>
```

## Not verified

What is not checked. Nobody measured whether reading the limit for every job slows the dispatch path. A rollout is undone only by another rollout, so I hold it until that measurement runs. The routing document was not updated. I did not check what happens to a job whose acknowledgement comes late, now that it is not re-sent.

## Where to look

- re-sending switched off: `src/main/java/dispatch/Router.java:8` `retryOnTimeout = false`
- the limit from configuration: `src/main/java/dispatch/Limits.java:12` `config.limit(queue)`
- the wait in the code: `src/main/java/dispatch/Router.java:7` `Duration.ofMillis(250)`
- the colleague's test: `src/test/java/dispatch/RouterTest.java:25` `assertEquals(400, d.ackTimeout().toMillis())`
- the checks, from the build log: tests 4 of 5 passed, `mvn -q test` exit 1; linter 0 problems, `./lint.sh` exit 0
