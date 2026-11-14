The task was to repeat a request after a timeout, with the wait doubling and four attempts at most. The repeat works, and its own five tests pass. But the build is red. You decide whether the client repeats only reads, or the payments team changes its test.

## How it works

The client sends a request and waits two seconds for an answer. If none comes, it waits and sends the request again. The wait starts at a fifth of a second and doubles each time. After the fourth attempt the client gives up and passes the timeout on. I also capped the wait at one second, which four attempts never reach. By my count, a caller waits at most about nine and a half seconds.

```
attempt          1        2        3        4
wait before it   0 ms     200 ms   400 ms   800 ms
answer awaited   2 s      2 s      2 s      2 s      then the timeout goes to the caller
```

## What to decide

There are two ways.

```diff
  1. Repeat only requests that read
+ the build turns green, and a payment goes out once
- a request that writes gets no repeat after a timeout
- not written yet, so its tests have not run

  2. Repeat every request, and the payments team changes its test
+ the task is done as it was written
- a payment that timed out can be charged twice
```

I would take the first. A double charge reaches a customer, and no change of ours takes it back.

Repeat only reads, or ask the payments team to change its test?

## Where to look

- the loop that repeats every request, whatever its method: `src/main/java/http/RetryingClient.java:20` `attempt <= RetryPolicy.MAX_ATTEMPTS`
- the doubling wait: `src/main/java/http/RetryPolicy.java:14` `BASE_DELAY_MILLIS << (attempt - 2)`
- the repeat's own tests: 5 of 5 passed, `build.log:4` `Tests run: 5, Failures: 0`
