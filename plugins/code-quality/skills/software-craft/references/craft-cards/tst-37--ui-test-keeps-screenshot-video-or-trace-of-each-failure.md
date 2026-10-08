---
title: A UI-driven test suite keeps a screenshot, video or trace of each failing test so the test's user interface can be inspected after the run
rule_id: TST-37
domain: tests
step: [test, review]
applies_to: [tests, build-config]
triggers: ['(?i)\b(new\s+\w*Driver|webdriver([.]\w+|::new)|launch_?browser|(chromium|firefox|webkit|puppeteer)(\(\))?[.]launch)\(|\b(playwright|cypress|wdio|nightwatch)[.]config\b|\bdefineConfig\(|\b(screenshotOnRunFailure|takeScreenshot|save_screenshot|get_screenshot_as_\w+|getScreenshotAs)\b|\b(screenshot|video|trace)\w*\s*[:=]\s*[\x22\x27]?(off|false|none|never)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A UI-driven test suite keeps a screenshot, video or trace of each failing test so the test's user interface can be inspected after the run

## Thesis
A suite of tests that drive a user interface is configured to keep a screenshot, a video or a trace for each failing test, taken from the failing run itself or, in a suite that retries failed tests, from the test's first retry, so the user interface of each failing test can be inspected after the run; a capture from the failing run shows the state at the failure itself.

## Rationale
Flaky tests pass or fail seemingly at random on unchanged code, and the challenges developers report with them regard mostly reproducing the flaky behaviour and identifying the cause of the flakiness; 21 professional developers classified 200 flaky tests they had fixed, and 121 developers answered a follow-up survey. A screenshot or a video saved on failure shows what the state of the user interface was when the test failed and can help to isolate the cause. A browser test tool's trace records the timeline, a DOM snapshot for each action and the network requests in a form that can easily be shared, and that tool's documentation prefers it to videos and screenshots for failures on a continuous-integration server. Recording such a trace on every test is very performance heavy, so it can be recorded only on the first retry of a failed test; a screenshot can be captured after each test failure, and a video or a trace can be recorded on every run and kept only when that run failed.

## Example
```java
bad:  WebDriver driver = new ChromeDriver();
      @AfterEach void close() { driver.quit(); }
good: WebDriver driver = new ChromeDriver();
      @RegisterExtension AfterTestExecutionCallback keepScreenshot = ctx -> {
        if (ctx.getExecutionException().isPresent())
          Files.write(Path.of("target", ctx.getDisplayName() + ".png"),
              ((TakesScreenshot) driver).getScreenshotAs(OutputType.BYTES));
      };
      @AfterEach void close() { driver.quit(); }
```

## Limits
The rule concerns tests that drive a user interface; tests with no user interface are outside it. A recording made only on the first retry shows the retry rather than the run that failed first; capturing the failing run itself takes a screenshot on failure or a video or trace kept when that run failed. The wording of a failure message, and a trace that follows one request across several processes, are outside this rule.

## Validator
Grep the hunk for a browser or UI driver being created or launched, a UI test runner's configuration, a screenshot call, or a screenshot, video or trace option set to off. Open the file and the shared setup it names (a base class, a registered extension or hook, the runner's configuration file) and trace what a failing test leaves behind: an after-test hook that saves a screenshot when the test failed and runs before the driver is closed, or an option that keeps a screenshot, video or trace on failure or records one on the first retry of a suite that retries failed tests; a first-retry option in a suite that does not retry keeps nothing. A capture configured once for the whole suite covers every test it reaches. Validator question: **Does a UI-driven test or its suite configuration in the diff leave a failing test with no screenshot, video or trace of the user interface?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-37`, severity minor, `file`, `symbol`, `code` = the line that creates or launches the UI driver, opens the UI test runner's configuration, or sets the screenshot, video or trace option to off, quoted verbatim from the diff, `fix` = an after-test hook that saves a screenshot when the test failed, or the runner option that keeps a screenshot, video or trace on failure, in the file's language, `rationale` = names the failing UI test whose interface state is lost and the reproduction its diagnosis then needs).

## Source
- pytest documentation, 'Flaky tests' › 'Video/screenshot on failure' (pytest-dev/pytest, doc/en/explanation/flaky.rst): "For UI tests these are important for understanding what the state of the UI was when the test failed. [...] save a screenshot on test failure [...], which can help to isolate the cause." (fetched)
- Playwright documentation, 'Best Practices' › 'Debugging on CI' (microsoft/playwright, docs/src/best-practices-js.md): "For CI failures, use the Playwright trace viewer instead of videos and screenshots. The trace viewer gives you a full trace of your tests as a local Progressive Web App (PWA) that can easily be shared. With the trace viewer you can view the timeline, inspect DOM snapshots for each action using dev tools, view network requests [...] Traces are configured in the Playwright config file and are set to run on CI on the first retry of a failed test. We don't recommend setting this to `on` so that traces are run on every test as it's very performance heavy." (fetched)
- Playwright documentation, 'Test use options' › 'Recording Options' (microsoft/playwright, docs/src/test-use-options-js.md): "Capture screenshot after each test failure. screenshot: 'only-on-failure'"; trace and video mode `'retain-on-failure'`: recorded "every run", kept when "that run failed"; mode `'on-first-retry'`: recorded "first retry only"; the scenario tables are stated "assuming `retries: 2` is configured". (fetched)
- Playwright documentation, 'Retries' (microsoft/playwright, docs/src/test-retries-js.md): "When enabled, failing tests will be retried multiple times until they pass, or until the maximum number of retries is reached. By default failing tests are not retried." (fetched)
- ESEC/FSE 2019, doi:10.1145/3338906.3338945 (arXiv:1907.01466), abstract: "Flaky tests are software tests that exhibit a seemingly random outcome (pass or fail) despite exercising unchanged code. [...] We asked 21 professional developers to classify 200 flaky tests they previously fixed [...] online survey with 121 developers [...] the challenges developers report to face regard mostly the reproduction of the flaky behavior and the identification of the cause for the flakiness." (fetched)
- Caveat: the survey concerns flaky tests in general, not UI tests only; the documentation states a practice, and no source measures its effect on diagnosis time.
