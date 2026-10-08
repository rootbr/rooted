---
title: A test waits for asynchronous work by polling the awaited condition or awaiting its completion event under a bounded deadline and never by sleeping for a fixed time
rule_id: TST-32
domain: tests
step: [implement, test, review]
applies_to: [tests]
triggers: ['\b(Thread[.]sleep|TimeUnit[.]\w+[.]sleep|SystemClock[.]sleep)\(', '(?<![\w.])(time[.]|asyncio[.]|anyio[.]|trio[.])?sleep\(\s*[\d.]', '\btime[.]Sleep\(', '\b(std::)?thread::sleep\(|\btokio::time::sleep\(|\bsleep\(\s*(std::time::)?Duration::', '[.](waitForTimeout|wait_for_timeout)\(|\bcy[.]wait\(\s*\d|[.]pause\(\s*\d', '=>\s*setTimeout\(|\bsetTimeout\(\s*\w+\s*,\s*\d+|\bawait\s+setTimeout\(\s*\d']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A test waits for asynchronous work by polling the awaited condition or awaiting its completion event under a bounded deadline and never by sleeping for a fixed time

## Thesis
A test that waits for asynchronous work, such as a message sent through a broker, a network response or a page element that renders, waits on the result itself: it awaits the signal that the work completed or polls the awaited condition, under a timeout that keeps the test from running indefinitely when the result never arrives, in place of a sleep of fixed duration followed by a check.

## Rationale
A fixed sleep guesses how long the work takes. When the guess is too short the test can fail, and when it is set high at every place a wait is needed the run time can become prohibitive. A sleep in a test can make the test fail unpredictably depending on the environment or load, and can slow test execution. In 201 fixes of flaky tests in open-source projects, improper waits for asynchronous responses were one of the three most common causes, typically a sleep that did not wait long enough for the action, such as a network call, to finish. Asynchronous calls were the leading cause of flaky tests in six large-scale proprietary projects at Microsoft. A study across five programming languages finds concurrency and async wait common causes of flakiness in most of them; a single-language study ranks async wait second among causes at 20%, after concurrency at 21%; and among 235 UI-based flaky tests on web and mobile, 106 had async-wait root causes (network resource loading 19, resource rendering 61, animation timing 26), the highest category. Waiting for the result itself, through a signal such as a network event or an element becoming visible, or through an assertion that holds the test until an explicit condition is met, replaces the guess; the timeout keeps the test from hanging when an awaited message is never delivered. A static-analysis rule flags the thread sleep in test code at major severity, and the lint rules that flag fixed-duration waits in browser end-to-end tests are enabled in their recommended configurations.

## Example
```java
bad:  queue.publish(order);
      Thread.sleep(2000);
      assertTrue(store.contains(order.id()));
good: CountDownLatch saved = new CountDownLatch(1);
      store.onSave(id -> { if (id.equals(order.id())) saved.countDown(); });
      queue.publish(order);
      assertTrue(saved.await(10, TimeUnit.SECONDS));
```

## Limits
Awaiting a completion signal, such as a latch or another synchronization mechanism, and polling under a timeout both satisfy the rule; polling serves where the code under test exposes no such signal, as when it sends a message to a channel in an external broker and the assertions wait until the message has gone through. A short pause between re-checks inside a loop that re-tests the condition, with a timeout bounding the whole test, is the poll interval and satisfies the rule. Replacing the asynchronous dependency with a mock removes the wait and satisfies the rule as well. The rule reaches test code only, the scope the static-analysis rule declares; a sleep in the code under test is outside it. The mechanical check starts from a sleep or fixed wait that a trigger matches; an await or a poll with no sleep in it matches no trigger, so the check does not reach a wait that no deadline bounds.

## Validator
Grep the hunk for the triggers: a sleep call, a fixed-duration wait or a timer callback in a test file. Open the enclosing test at hunk scope and read what follows each match. Pass a pause inside a loop that re-tests the awaited condition under a timeout, whether the timeout is set on the call, on the enclosing test, or by the default of the waiting library or test framework. Treat a sleep or fixed wait that precedes a check of the asynchronous work's result as the defect. Validator question: **Does a test in the hunk wait for asynchronous work by a sleep of fixed duration before checking its result?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-32`, severity major, `file`, `symbol`, `code` = the sleep or fixed wait and the check that follows it, quoted verbatim from the diff, `fix` = the wait rewritten to await the completion signal or to poll the condition under a timeout, in the file's language, `rationale` = the asynchronous work awaited and how the guessed duration makes the test flaky or slow).

## Source
- doi:10.1145/2635868.2635920 (relayed): "studied 201 fixes to flaky tests in open-source projects [...] the three most common causes of fixable flaky tests were: improper waits for asynchronous responses; concurrency; and test order dependency"; "there was typically a sleep() call which didn't wait long enough for the action (perhaps a network call) to finish. The best practice is to use some sort of wait() call to wait for the result instead of hardcoding a sleep time."
- doi:10.1145/3377811.3381749, abstract (fetched): "we study the lifecycle of flaky tests in six large-scale proprietary projects at Microsoft. We find, as in prior work, that asynchronous calls are the leading cause of flaky tests in these Microsoft projects."
- doi:10.1109/TSE.2022.3208864, abstract (fetched): "for any given programming language that we studied (C, Go, Java, JS, and Python), most issues could be explained by a small fraction of root causes"; "although there were commonalities in root causes and fixes across languages (e.g., concurrency and async wait are common causes of flakiness in most languages), we also found important differences"; "A test is said to be flaky when it non-deterministically passes or fails on a fixed environment."
- arXiv:2207.01047, §IV-A (fetched): "The top four causes of test flakiness in JavaScript projects are concurrency (21%), async wait (20%), OS (18%) and network (13%)."
- doi:10.1109/ICSE43902.2021.00141, Table 4 on the study site (fetched): "the highest causes of flakiness come from causes under Async Wait"; Async Wait cells 19, 61 and 26 of a total of 235 (web 152, mobile 83).
- SonarSource java:S2925 "Thread.sleep should not be used in tests" (fetched; scope Tests, default severity Major): "Using Thread.sleep in this case can cause flaky tests, slow test execution, and inaccurate test results. It creates brittle tests that can fail unpredictably depending on the environment or load. Use mocks or libraries such as Awaitility instead."
- eslint-plugin-playwright no-wait-for-timeout, recommended (fetched): "Use signals such as network events, selectors becoming visible and others instead."
- eslint-plugin-cypress no-unnecessary-waiting, with the Cypress best-practices page (fetched): "Disallow waiting for arbitrary time periods. This rule is enabled in the ✅ `recommended` config."; "Use route aliases or assertions to guard Cypress from proceeding until an explicit condition is met."
- JUnit User Guide, Timeouts, "Using @Timeout for Polling Tests", and its PollingTimeoutDemo (fetched): "In some cases you can rewrite the logic to use a `CountDownLatch` or another synchronization mechanism, but sometimes that is not possible — for example, if the subject under test sends a message to a channel in an external message broker and assertions cannot be performed until the message has been successfully sent through the channel. Asynchronous tests like these require some form of timeout to ensure they don't hang the test suite by executing indefinitely, as would be the case if an asynchronous message never gets successfully delivered."; "@Timeout(5) // Poll at most 5 seconds", "Thread.sleep(250); // custom poll interval".
- Selenium documentation, Waiting Strategies (fetched): "Because the code can't know exactly how long it needs to wait, this can fail when it doesn't sleep long enough. Alternately, if the value is set too high and a sleep statement is added in every place it is needed, the duration of the session can become prohibitive."
- Caveat: the studies count the root causes of flaky tests that developers fixed; they establish how often asynchronous waits cause flakiness, not a measured effect of the fix.
