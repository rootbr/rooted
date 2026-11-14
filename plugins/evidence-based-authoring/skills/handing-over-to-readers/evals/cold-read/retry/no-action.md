The task was to repeat a request after a timeout, with the wait doubling and four attempts at most. The repeat works, and its own five tests pass. But the build is red. The client now repeats a payment too, and the payments team's test forbids that. 

## How it works

The client sends a request and waits two seconds for an answer. If none comes, it waits and sends the request again. The wait starts at a fifth of a second and doubles each time. After the fourth attempt the client gives up and passes the timeout on. I also capped the wait at one second, which four attempts never reach. By my count, a caller waits at most about nine and a half seconds.

```
attempt          1        2        3        4
wait before it   0 ms     200 ms   400 ms   800 ms
answer awaited   2 s      2 s      2 s      2 s      then the timeout goes to the caller
```

## The red build

The payments team's test sends a payment that always times out. It expects the client to send it once. The client sent it four times. A payment that timed out may already have gone through at the gateway. So a repeat can charge the customer twice. I did not touch that test.

```diff
  client -> gateway: the payment, attempt 1, no answer in time
+ client -> caller: the timeout, the payment not repeated      (what the test expects)
- client -> gateway: the payment, attempt 2                    (what the client does now)
- client -> gateway: the payment, attempt 3
- client -> gateway: the payment, attempt 4
```

## Where to look

- the loop that repeats every request, whatever its method: `src/main/java/http/RetryingClient.java:20` `attempt <= RetryPolicy.MAX_ATTEMPTS`
- the doubling wait: `src/main/java/http/RetryPolicy.java:14` `BASE_DELAY_MILLIS << (attempt - 2)`
- the payments team's check: `src/test/java/payments/PaymentsClientTest.java:24` `assertEquals(1, attempts);`
- the build: `./run-tests.sh` exit 1, 6 tests, 1 failure, `build.log:3` `expected: <1> but was: <4>`
- the repeat's own tests: 5 of 5 passed, `build.log:4` `Tests run: 5, Failures: 0`
