The task was to stop re-sending a job after an acknowledgement timeout, and to read the per-queue limit from configuration. Both edits are in the code, but the build is red. You decide which wait is right, and only then can the change go out.

## What changed

How it works now. The router checks the size of a job against the limit of its queue. That limit now comes from configuration instead of a constant. A job a worker did not acknowledge in time used to be sent again. Now it is not.

```
                          before             now
re-send after a timeout   yes                no
limit of a queue          a constant         read from configuration
```

## Not verified

What is not checked. Nobody measured whether reading the limit for every job slows the dispatch path. A rollout is undone only by another rollout, so I hold it until that measurement runs. The routing document was not updated. I did not check what happens to a job whose acknowledgement comes late, now that it is not re-sent.

## What to decide

There are two ways.

```diff
  1. Wait 400 milliseconds, as the test expects
+ the build turns green and the colleague's test stays as written
+ a slow worker gets more time, which matters now that nothing is re-sent
- a job sent to a dead worker waits longer before it times out

  2. Keep 250 milliseconds and change the test
+ the dispatch path keeps the wait it has today
- the colleague's test is rewritten, and he has to agree
- a slow acknowledgement times out sooner, with no second attempt
```

I would take 400. The colleague's test is the latest written word on the wait. Only you or he know the intent, so I did not pick it myself.

400 or 250?

## Where to look

- re-sending switched off: `src/main/java/dispatch/Router.java:8` `retryOnTimeout = false`
- the limit from configuration: `src/main/java/dispatch/Limits.java:12` `config.limit(queue)`
- the checks, from the build log: tests 4 of 5 passed, `mvn -q test` exit 1; linter 0 problems, `./lint.sh` exit 0
