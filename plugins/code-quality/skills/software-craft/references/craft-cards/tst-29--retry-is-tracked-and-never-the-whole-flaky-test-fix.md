---
title: A retry or rerun added for tests comes with a tracked record of the tests it lets pass and is never the whole fix for a flaky test
rule_id: TST-29
domain: tests
step: [test, review]
applies_to: [tests, build-config]
triggers: ['@(?:RepeatedTest|RetryingTest|[Ff]laky|FlakyTest|Retry)\b|(?i:\b(?:retry|retries|max_?retries|rerunFailingTestsCount|reruns|flaky_reruns|retryAnalyzer)\s*(?:[:=]|[.]set\())|\bpytest[.]mark[.]flaky\b|--reruns\b|--only-rerun\b|\bflaky\s*=\s*(?:True|true|1)\b|\b(?:jest[.]retryTimes|this[.]retries|retry|FlakeAttempts)\(\s*\d|(?i:--(?:retries|retry|rerun[-_]?fail(?:ed|s)?|flake-attempts|flaky_test_attempts)\b)|<rerunFailingTestsCount>']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A retry or rerun added for tests comes with a tracked record of the tests it lets pass and is never the whole fix for a flaky test

## Thesis
A change that turns on or raises retries or reruns for tests — a retry annotation, a retry or rerun count, a flaky attribute, a rerun flag — comes with a tracked record of the flaky tests the retries let pass, such as an issue or a flaky-test list kept across runs, alongside a process that fixes those tests. A change meant to fix a flaky test makes the test pass reliably when its assertions hold; a retry added alone changes the verdict on a failed run, not the test.

## Rationale
With retries on, by default a failed test that passes on retry leaves the test task passing, so a flaky test stops causing build failure; a flaky attribute runs a test up to three times and marks it failed only if it fails each time. The build result then no longer identifies the flaky test. Retrying alone is not a viable flaky-test mitigation, and a retry belongs alongside tracking and fixing the flaky tests it finds; a flaky attribute is generally discouraged because tests should pass reliably when their assertions are upheld. Reruns are also a weak and costly detector. In one study of a single package ecosystem's projects, a 95% confidence that a passing test is not flaky would require on average 170 reruns; rerunning the suites of 24 projects 10,000 times each still left some previously identified flaky tests undetected; and filtering out false alerts completely may need a disproportionate number of reruns, with costs in computation and time. Builds with flaky tests had a median of 514 and 234 crash reports for beta and production builds, against a median of two for builds with all tests passing, and ignoring test failures is related to a dramatic increase in the crashes users report. The tracked record restores what the retry removes from the build result: each flaky test stays identified until it is fixed.

## Example
```typescript
bad:  // fix flaky checkout test
      export default defineConfig({ retries: 2 });
good: // a test that passes on retry still fails the run and is reported as flaky
      export default defineConfig({ retries: 2, failOnFlakyTests: true });
```

## Limits
The rule leaves retries in place where they are tracked: a retry used alongside processes for tracking and fixing the flaky tests it finds is the documented use of a retry mechanism. A retry set so that a test passing on retry still fails the build identifies flaky tests, and meets the rule without a separate record; whether a project's build fails that way is a CI policy the rule does not set. The rule reaches retries that rerun a failed test as a whole — failed tests retried after the run up to a maximum count, or a test executed up to three times — and a loop inside a test that polls for a condition before asserting reruns no test and falls outside it. A repeat that runs a test many times to observe it both passing and failing on the same code is the traditional way to identify a flaky test, and falls outside the rule when any failed run fails the build.

## Validator
Grep the hunk for the triggers: a retry or flaky annotation, a retries, reruns or retry-count setting, a flaky attribute set true, a rerun flag on a test command, a retry call with a count. For each match, read the hunk around it for a reference to a tracked record of the tests the retry lets pass: an issue link or id in a comment or annotation, a flaky-test list kept across runs that names each test until it is fixed, or a setting that fails the build when a test passes on retry; a reporter that prints or writes the tests passing on retry in each run is the retry's own output and does not count. Read the hunk's comments, test names and any change description given with it for a claim that the retry fixes a flaky test, and check whether the hunk changes the test, the code under test or its setup beyond the retry. Skip a polling loop that waits on a condition inside a test and a repeat that fails when any run fails. Validator question: **Does the hunk turn on or raise a test retry or rerun without a reference to a tracked record of the tests it lets pass, or present a retry added alone as the fix for a flaky test?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-29`, severity major, `file`, `symbol`, `code` = the retry or rerun line verbatim from the diff, `fix` = the same retry kept with a reference to the issue or flaky-test list that tracks each test it lets pass, or set so that a pass on retry fails the build, or the change to the test or its setup that makes it pass reliably, in the file's language, `rationale` = names that a test passing on retry leaves the build passing so the flaky test is no longer identified, and that reruns detect flakiness poorly, at 170 reruns on average for 95% confidence in one study).
