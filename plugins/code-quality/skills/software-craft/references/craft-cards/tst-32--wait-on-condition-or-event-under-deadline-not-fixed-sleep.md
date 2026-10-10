---
title: A test waits for asynchronous work by polling the awaited condition or awaiting its completion event under a bounded deadline and never by sleeping for a fixed time
rule_id: TST-32
domain: tests
step: [test]
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
