---
title: A property or fuzz target in the run that gates every commit stops at a set case count or time limit, and an open-ended search for new failures, or one sized for one-off or fuzzing runs, runs as a separate job
rule_id: TST-54
domain: tests
step: [test]
applies_to: [tests, build-config]
triggers: ['(?i:\bmax_examples\s*=|\bnumRuns\s*:|\bPROPTEST_CASES\b|\bwith_cases\()|(^|[\s"\x27])-fuzz(time)?\b|\b(maxSuccess|withMaxSuccess|quickchecks|MaxCount)\b|@Property\s*\(\s*tries\s*=|POSITIVE_INFINITY|\bfuzz-seconds\s*:|-max_total_time=']
scope: callers
check_kind: semantic
severity_default: minor
---

# A property or fuzz target in the run that gates every commit stops at a set case count or time limit, and an open-ended search for new failures, or one sized for one-off or fuzzing runs, runs as a separate job

## Thesis
Each property-based test or fuzz target in the run that gates every commit executes a bounded number of cases, set by the stored seed inputs, the framework's default case count, an explicit case count, or a time or iteration limit. A search for new failures with no such limit, such as a fuzzing run without a time limit or a case count of infinity, runs in a separate job, such as a scheduled or non-gating one. So does a search whose case count the framework's documentation assigns to one-off tests or to fuzzing rather than to a regularly executed suite.

## Rationale
A fuzzing run with no time limit can run indefinitely when it finds no error, and the default of the flag that sets that limit is to run forever. The plain test command instead runs each stored seed input against the fuzz target and exits, and an iteration limit of N runs the target N times, so a fuzz target stays bounded in the gating run when that run executes only the seed inputs or passes a time or iteration limit. One framework chooses its default of 100 cases "to suit a workflow where the test will be part of a suite that is regularly executed locally or on a CI server, balancing total running time against the chance of missing a bug"; two others default to 256 cases and to 1000 tries. The same documentation calls tens of thousands of cases "quite reasonable" for one-off tests, reports novel bugs found in very complex code after several million cases, and points runs above 100,000 cases to coverage-guided fuzzing, which "really shines when given minutes or hours to run". Another framework's fuzzing guide sets the number of runs to infinity or to 1,000,000, since fuzzing's primary requirement is "a large number of runs". In a study of 30 interviews with 31 participants at one company, property-based tests were almost always described as running in the build, under strict time budgets from 50 milliseconds to 30 seconds "to ensure it would not slow down the build" and below the 1-minute-per-library timeout that many developers there set for their unit test suite; some participants considered their fuzzing to run "out of band", outside of the normal continuous integration, at time scales on the order of hours or days, and fuzzing tools were given much longer to run than property-based tests. In a parameter sweep over the number of random inputs generated, 76% of the mutations property-based tests found were found within the first 20 inputs. Batch fuzzing lets a corpus of inputs build up over time, which greatly improves the effectiveness of fuzzing, and can run on a cron schedule; its documentation marks running it on each push to the main branch as not recommended. One framework's settings documentation gives this example of separate settings profiles: "quick deterministic tests on every commit, and a longer non-deterministic nightly testing run". One project runs its property-based tests in a dedicated job with a 60-minute timeout that its required-checks gate lists among the allowed failures.

## Example
```go
bad:  func gate() error { // job required on every commit
          return exec.Command("go", "test", "-fuzz=FuzzParse", "./parser").Run()
      }
good: func gate() error { // job required on every commit: seed inputs only
          return exec.Command("go", "test", "./parser").Run()
      }
      func nightly() error { // scheduled job, not required
          return exec.Command("go", "test", "-fuzz=FuzzParse", "-fuzztime=10m", "./parser").Run()
      }
```

## Limits
A time-boxed search on each change, run in its own job, meets the rule: one per-change fuzzing service runs the fuzzers "for a short amount of time", 600 seconds by default, and another's pull-request workflow sets 600 seconds. The rule sets no case count: framework defaults are 100, 256 and 1000, and one framework's documentation shows raising the count on a CI server to 1000. It requires no per-case deadline either: one framework's deadline is 200 milliseconds by default and none on a CI server, and another's per-case timeout defaults to 0, meaning no timeout. Whether the separate job itself stops lies outside the rule: one fuzzing guide sets the number of runs to infinity, batch fuzzing runs for 3600 seconds at a time on a cron schedule, and one project's property-test job stops at a 60-minute job timeout. Whether the gating run fixes its random seed, and how a slow test is marked for selection into a separate run, also lie outside this rule.

## Validator
Grep the hunk for a fuzzing flag or its time-limit flag, a case-count setting (maximum examples, number of runs, cases, tries, maximum successes, maximum count), an infinite count or a fuzzing-seconds setting. Open at the card's scope the job or command that runs the test (CI workflow, build script, test profile) and its trigger, and decide whether that job gates every commit: it runs on each push or pull request and its failure blocks the merge. Trace the bound of each property or fuzz target in that job: the stored seed inputs, the framework default, an explicit count, or a time or iteration limit; a fuzzing command with no time limit is unbounded. Compare an explicit count with the range the framework's documentation assigns to one-off tests or to fuzzing. Validator question: **Does the change make the run that gates every commit generate inputs with no case or time limit, or set a property's count in that run to one the framework's documentation assigns to one-off tests or fuzzing, rather than running that search as a separate job?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-54`, severity minor, `file`, `symbol`, `code` = the fuzzing command, case-count setting or job trigger line verbatim from the diff, `fix` = the gating run left at the default or a bounded count, or at the seed inputs only, with the open-ended or one-off-sized search moved into a scheduled or non-gating job, in the file's language, `rationale` = names the missing limit or the one-off-sized count and the job that gates every commit).
