# Retry on timeout: report

**The build is red, and you need to decide before this merges.** Every request is now retried, POST included. The payments team's test says a payment must reach the gateway at most once, and that test now fails (build.log: `PaymentsClientTest.postIsNotRetriedOnTimeout:24 expected: <1> but was: <4>`, `BUILD FAILURE`, `exit code: 1`).

## What is done

- `src/main/java/http/RetryPolicy.java:RetryPolicy`: up to `MAX_ATTEMPTS = 4` attempts. The first attempt starts at once. After that the wait is 200 ms and doubles each time (`BASE_DELAY_MILLIS << (attempt - 2)`), with a ceiling of 1 s (`MAX_DELAY_MILLIS = 1_000`). With four attempts the waits are 0, 200, 400 and 800 ms, so the ceiling never applies. I added it as a safeguard; the task didn't ask for it.
- `src/main/java/http/RetryingClient.java:RetryingClient.send`: tries again only on `HttpTimeoutException`, with a 2 s timeout per attempt (`TIMEOUT_MILLIS = 2_000`). If all four attempts time out, it rethrows the last timeout. In the worst case one call blocks for about 9.4 s (4 × 2 s plus 1.4 s of waits). The method does not look at `request.method()`, so it retries POST the same way as GET.
- `src/test/java/http/RetryingClientTest.java`: 5 new tests. They cover the doubling delays, the 1 s ceiling, stopping at the first success, giving up after 4 attempts, and the waits actually recorded between attempts.

## What is verified

- According to build.log, `http.RetryingClientTest` ran 5 tests with 0 failures.
- `payments.PaymentsClientTest` ran 1 test with 1 failure. This report has only the build.log run as evidence. I did not run the build again for it.
- Not verified: behaviour against a real gateway or server. Every test uses a stub transport.

## What you have to decide

**Fact:** the payments test (`src/test/java/payments/PaymentsClientTest.java`, which says "Owned by the payments team") requires a POST that timed out to be sent exactly once, because "a POST that timed out may have been applied". My change sends it 4 times. A payment could be charged twice.

**What the answer changes:** whether I change our client or ask the payments team to change their test. I did not choose either by default, because the test belongs to another team and the risk is double charging.

- **A. Retry only idempotent methods** (GET, HEAD, PUT, DELETE, OPTIONS) and send POST once. The payments test passes without anyone touching it and the build goes green. Our POST callers get no retry.
- **B. Keep retrying everything** and ask the payments team to change or drop their test. GET and POST behave the same. Payments could be charged twice unless the gateway removes duplicate requests (for example with an idempotency key), and I have not checked whether it does.

My recommendation is A.

**Do I restrict the retry to idempotent methods (A), or do we take it to the payments team (B)?**
