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
The rule leaves retries in place where they are tracked: a retry used alongside processes for tracking and fixing the flaky tests it finds is the documented use of a retry mechanism. A retry set so that a test passing on retry still fails the build identifies flaky tests instead of letting them pass, and meets the rule without a separate record; whether a project's build fails that way is a CI policy the rule does not set. The rule reaches retries that rerun a failed test as a whole — failed tests retried after the run up to a maximum count, or a test executed up to three times — and a loop inside a test that polls for a condition before asserting reruns no test and falls outside it. A repeat that runs a test many times to observe it both passing and failing on the same code is the traditional way to identify a flaky test, and falls outside the rule when any failed run fails the build.

## Validator
Grep the hunk for the triggers: a retry or flaky annotation, a retries, reruns or retry-count setting, a flaky attribute set true, a rerun flag on a test command, a retry call with a count. For each match, read the hunk around it for a reference to a tracked record of the tests the retry lets pass: an issue link or id in a comment or annotation, a flaky-test list kept across runs that names each test until it is fixed, or a setting that fails the build when a test passes on retry; a reporter that prints or writes the tests passing on retry in each run is the retry's own output and does not count. Read the hunk's comments, test names and any change description given with it for a claim that the retry fixes a flaky test, and check whether the hunk changes the test, the code under test or its setup beyond the retry. Skip a polling loop that waits on a condition inside a test and a repeat that fails when any run fails. Validator question: **Does the hunk turn on or raise a test retry or rerun without a reference to a tracked record of the tests it lets pass, or present a retry added alone as the fix for a flaky test?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-29`, severity major, `file`, `symbol`, `code` = the retry or rerun line verbatim from the diff, `fix` = the same retry kept with a reference to the issue or flaky-test list that tracks each test it lets pass, or set so that a pass on retry fails the build, or the change to the test or its setup that makes it pass reliably, in the file's language, `rationale` = names that a test passing on retry leaves the build passing so the flaky test is no longer identified, and that reruns detect flakiness poorly, at 170 reruns on average for 95% confidence in one study).

## Source
- Gradle Test Retry plugin, README.adoc, 'What it does' and its NOTE (fetched): "After executing all tests, any failed tests are retried. The process repeats with tests that continue to fail until the maximum specified number of retries has been attempted" · "By default, all failed tests passing on retry prevents the test task from failing. This mode prevents flaky tests from causing build failure. This setting can be changed so that flaky tests cause build failure, which can be used to identify flaky tests." · "Retrying tests alone is not a viable flaky test mitigation strategy. This plugin should only be used alongside processes for tracking and fixing discovered flaky tests."
- Bazel Build Encyclopedia, common test attribute `flaky` (fetched): "If set, executes the test up to three times, marking it as failed only if it fails each time. [...] use of this attribute is generally discouraged - tests should pass reliably when their assertions are upheld."
- doi:10.1109/ICST49551.2021.00026, arXiv:2101.09077, abstract (fetched): "we sampled 22 352 open source projects from the popular PyPI package index [...] Our data also suggests that finding flaky tests requires more runs than are often done in the literature: A 95 % confidence that a passing test case is not flaky on average would require 170 reruns."
- doi:10.1109/ICSE43902.2021.00140, abstract (fetched): "The traditional approach to identify flaky tests is to rerun them multiple times: if a test is observed both passing and failing on the same code, it is definitely flaky. [...] rerunning the test suites of 24 projects 10,000 times each, and found that even with this many reruns, some previously identified flaky tests were still not detected."
- arXiv:2111.03382, abstract (fetched): "the defacto approach to address this concern is to rerun failing tests hoping that they would pass [...] completely filtering out false alerts may require a disproportionate number of reruns, and thus incurs important costs both computation and time-wise."
- doi:10.1145/3236024.3275529, abstract (fetched): "Builds with all tests passing have a median of only two crash reports. [...] ``flaky'' tests [...] have a median of 514 and 234 crash reports for Beta and Production builds. [...] ignoring test failures is related to a dramatic increase in the number of crashes reported by users."
- Caveat: the rerun counts measure reruns as a way to detect flaky tests, and the 170-rerun figure comes from one package ecosystem's projects; the crash figures come from one browser's builds, observational.
