---
title: A failing or flaky check left unfixed is disabled by a framework mark naming its reason and tracking issue, and a rerun is not its fix
rule_id: TOOL-17
domain: tooling
step: [test]
applies_to: [tests, build-config]
triggers: ['signal:commented_out_code', '@(?:Disabled|Ignore)\b', '#\[ignore\b', 'pytest[.]mark[.](?:skip|xfail)|@unittest[.](?:skip|expectedFailure)|pytest[.](?:skip|xfail)\(', '\b(?:it|test|describe)[.](?:skip|todo|failing)\(|\bx(?:it|test|describe)\(', '\bt[.]Skip(?:f|Now)?\(', '@flaky\b|\breruns\s*=|retryTimes\(|[.]retries\(', '^\s*(?:#|//)\s*(?:def\s+test_|@Test\b|func\s+Test\w*\(|#\[test\]|(?:it|test)\()']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A failing or flaky check left unfixed is disabled by a framework mark naming its reason and tracking issue, and a rerun is not its fix

## Thesis
A failing or flaky test or check that a change does not fix stays in the suite under the test framework's skip, ignore or expected-failure mark, and that mark carries the reason and the issue that tracks the failure, in its reason argument or, for a mark that takes none, in a comment beside it; commenting the check out, or deleting it while no other test covers its behaviour, hides the failure instead. A check that fails on every run takes the strict expected-failure mark where the framework offers one, so the suite fails as soon as the check passes again. An automatic rerun, or a non-strict expected-failure mark, lets a flaky check fail without breaking the build; it mitigates the flakiness without fixing it, so a change that adds one carries the tracking issue as well.

## Rationale
Flaky tests have non-deterministic outcomes and make it difficult to rely on test results. Once a failure is no longer a reliable signal that the change broke the test, developers can become mistrustful of the results and overlook genuine failures, and they spend time re-running suites and investigating spurious failures. A catalog of 79 CI bad smells, drawn from 13 expert interviews and more than 2,300 developer Q&A posts, advises practitioners not to ignore nor hide build failures. A framework mark keeps the disabled check on record: the mark stays in the source where a search finds it, one framework's run counts and lists skips and expected failures separately in its summary, the mark's reason documents why the check is disabled, and an issue tracking number in the reason gives traceability. A commented-out or deleted check leaves the run nothing to count. A strict expected-failure mark makes an unexpectedly passing check fail the suite; a non-strict one lets the check fail without breaking the build, a manual quarantine that is dangerous to use permanently. Rerunning a failed test gives it additional chances to pass so that the build does not fail, and the test's outcome stays non-deterministic. Restarts carry their own cost: in one CI service's data developers restarted at least 1.72% of builds, 56,522 builds, and restarted builds slowed pull-request merging by a factor of three, the median merging time rising from 16h to 48h. In a study of flaky-test issues across five programming languages, 5 of 13 root causes cover 78.07% of the issues and 10 of 23 fix strategies cover 85.20%, so most of the studied issues could be fixed by a small fraction of the fix strategies.

## Example
```python
bad:  @pytest.mark.flaky(reruns=3)
      def test_export(): ...
      # def test_import(): ...
good: @pytest.mark.skip(reason="times out under load, tracked in issue 412")
      def test_export(): ...
      @pytest.mark.xfail(strict=True, reason="drops header row, issue 413")
      def test_import(): ...
```

## Limits
A skip conditioned on the environment is outside the rule: such a skip means the test is expected to pass only when some conditions are met, such as a platform or an external resource that is not available at the moment. A test removed together with the behaviour it checks is outside it too, as is a flaky test removed because other tests cover its behaviour or replaced in the same change by a rewritten test, and so is how to make a flaky test deterministic. A strict expected-failure mark fails the suite whenever the check passes, so on a flaky check it fails the runs where the check happens to pass; a flaky check takes a skip mark, or a non-strict expected-failure mark as a temporary quarantine, with its tracking issue. Whether a failing check may be disabled at all is contested. One position keeps every test running at commit: a lint rule for one test framework warns about disabled tests so that all tests are running before committing, and the CI bad-smell catalog advises not to ignore nor hide build failures. The other accepts a disable that stays on record: test frameworks document skip, ignore and expected-failure marks with a reason, one framework's guide says they keep the suite green while its summary counts and lists them, and another recommends a reason and notes teams that require an issue tracking number in it. The separating condition is whether the disable is visible and tracked: a mark that carries its reason and its tracking issue keeps the failure on record, commenting out the check, or deleting it while its behaviour stays untested, hides it, and a mark with no reason leaves the record without the why. A project that enforces a lint rule against any disabled test holds the stricter position, and there the fix is the check itself.

A rerun set so that a test that passes only on retry still fails the build lets no flaky check pass and needs no tracking issue beside it. A commented-out test declaration dispatches the rule through its own line; a commented-out test body with no declaration line among the comments is reached only where two or more consecutive comment lines carry statement syntax.

## Validator
Grep the hunk for added skip, ignore, disabled and expected-failure marks, rerun settings, commented-out test definitions and assertions, and removed test functions. Open the hunk and read each mark's reason, or the comment beside a mark or rerun setting that takes no reason: check that it states why the check is disabled and names the issue that tracks the failure, as an issue number or a tracker link. For a rerun setting or a non-strict expected-failure mark, look for the tracking issue on the same test. Where the reason says the check fails on every run, look for the strict expected-failure form the framework offers. Pass over a skip conditioned on a platform or an unavailable resource, a test removed with the code it checks, and a flaky test removed where the change adds its rewritten replacement or names the tests that still cover its behaviour. Validator question: **Does the hunk comment out a failing or flaky test or check, delete one with neither a rewritten replacement nor a named test that still covers its behaviour, add a skip, ignore or expected-failure mark to one without both its reason and the issue that tracks the failure, in the mark's reason or beside it, add an automatic rerun to one without that issue beside it, or disable a check whose reason says it fails on every run with a skip, an ignore or a non-strict expected-failure mark where the framework offers a strict expected-failure one?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-17`, severity major, `file`, `symbol`, `code` = the commented-out or removed test line, the bare mark or the rerun setting quoted verbatim from the diff, `fix` = the framework's skip, ignore or expected-failure mark in the file's language with a reason naming the tracking issue, strict where the check fails on every run, or, for a rerun setting or a mark that takes no reason, a comment beside it naming the tracking issue, `rationale` = names the disabled check, the failure it hides or leaves untracked and the missing reason or tracking issue).
