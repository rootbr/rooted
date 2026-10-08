---
title: Snapshot and golden files are committed beside their tests and rewritten only by an explicit update mode, never by a merge-gating run
rule_id: CHG-20
domain: change
step: [test, review]
applies_to: [tests, build-config]
triggers: ['--updateSnapshot\b|--update-snapshots?\b|--snapshot-update\b|--bless\b|\bcargo\s+insta\s+(accept\b|test\b.*\s--(accept|force-update-snapshots)\b)|\b(jest|vitest)\b.*\s(-u|--update)\b|\bgo\s+test\b.*\s-update\b|\b(INSTA_UPDATE|INSTA_FORCE_PASS)\s*[:=]\s*[\x22\x27]?(always|unseen|force|1|true)\b|\bUPDATE_EXPECT\s*[:=]|--inline-snapshot[=\s]+\S*(create|fix|review|update|trim)|^\s*!?/?(\*\*/)?(__snapshots__|[\w*/.-]*[.](snap|golden|approved[.]\w+)|testdata)/?\s*$|\b(os[.]WriteFile|ioutil[.]WriteFile|fs[.]writeFileSync|write_text|Files[.]write(String)?|fs::write)\(.*(golden|snap|approved|expected)|(?i:golden|snap|approved|expected)\w*[.]write_(text|bytes)\(']
scope: file
check_kind: semantic
severity_default: major
---

# Snapshot and golden files are committed beside their tests and rewritten only by an explicit update mode, never by a merge-gating run

## Thesis
Stored expected output — a snapshot file, an inline snapshot, a golden or approved file — is committed to version control beside the tests that read it. The merge-gating test run only compares: it fails on a missing or changed stored value and writes none. An existing stored value is rewritten only in a run where the developer sets an update flag, mode or environment variable; the developer inspects the diff between the old and the new value, and that diff goes through code review with the change.

## Rationale
A stored value is part of a test, like the value of any other assertion, so it lives with the test and reaches code review with the change that alters it; reviewers then see what changed from the previous version. A run that writes the stored value from the current output compares that output with itself: a new snapshot passes automatically, under a create, fix or review mode every snapshot comparison returns true, and a golden test in update mode writes the file and returns before the comparison. A value left out of version control is absent from the code the gating run checks out, so that run either records it afresh, which passes automatically, or fails on it. An update run rewrites every failing value, the ones a bug broke included, which is why the bug is fixed first and the regenerated values are inspected before they replace the expectation. Separating writing from comparing restores the check: the gating run fails on every mismatch and missing value, and the update run leaves a diff — a pending file beside the stored one, or a regenerated file — for a person to accept.

## Example
```python
bad:  def test_report():
          out = render_report(sample_order())
          golden.write_text(out)
          assert out == golden.read_text()
good: def test_report(request):
          out = render_report(sample_order())
          if request.config.getoption("--update-golden"):
              golden.write_text(out)
          assert out == golden.read_text()
```

## Limits
Several tools record a value for a test that has none during a local run outside continuous integration, write the proposed value into a pending file for review, or show each proposed change at an interactive terminal and write it only when the developer accepts it; that is the tool's documented local default, and the recorded file still enters version control through review. Where a tool recognises continuous integration by an environment variable, its compare-only behaviour holds in a gating job that sets that variable or passes the tool's compare-only switch. A change made to update expected output — the developer runs the update mode and commits the inspected diff — follows the rule, and an update command in a script a developer runs by hand is not a gating run. The rule does not judge which output deserves a stored value.

## Validator
Grep the hunk for an update switch (`--updateSnapshot`, `-u` or `--update` on a snapshot runner, `--snapshot-update`, `--bless`, `cargo insta accept` or `cargo insta test --accept`, `-update`, an update environment variable set to always, unseen or force, a force-pass variable set to 1, an inline-snapshot create, fix, review, update or trim flag), for a write to a path or variable named golden, snapshot, approved or expected, and for an ignore-file line naming a snapshot directory, a snapshot or golden extension or a test-data directory. For an update switch, open the file and decide whether the command runs in continuous integration, a pre-merge hook or the default test script; a script a developer invokes by name to update values is outside. For a write, open the test and trace whether it runs only when an update flag, option or variable is set and whether that setting defaults to off. For an ignore line, check whether it excludes stored expected output that tests read. Validator question: **Does the hunk make a merge-gating run write a stored expected value or pass on a missing or changed one, let a test overwrite a stored value without an explicit update setting, or keep stored expected values out of version control?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-20`, severity major, `file`, `symbol`, `code` = the update switch, the unguarded write or the ignore line verbatim from the diff, `fix` = the compare-only gating command, the write moved behind an update flag that defaults to off, or the ignore line removed, in the file's language, `rationale` = that a run writing its own expectation or passing without comparing passes whatever the code produces and the stored value then escapes review).

## Source
- Jest docs, Snapshot Testing, raw.githubusercontent.com/jestjs/jest/main/docs/SnapshotTesting.md (fetched): "The snapshot artifact should be committed alongside code changes, and reviewed as part of your code review process"; "snapshots in Jest are not automatically written when Jest is run in a CI system without explicitly passing `--updateSnapshot`. It is expected that all snapshots are part of the code that is run on CI and since new snapshots automatically pass, they should not pass a test run on a CI system"; "all snapshot files should be committed alongside the modules they are covering and their tests. They should be considered part of a test, similar to the value of any other assertion"; "Jest can tell what changed from the previous version ... reviewers can study your changes better"; "This will re-generate snapshot artifacts for all failing snapshot tests. ... we would need to fix the bug before re-generating snapshots to avoid recording snapshots of the buggy behavior."
- Jest docs, CLI `--ci`, raw.githubusercontent.com/jestjs/jest/main/docs/CLI.md (fetched): "Instead of the regular behavior of storing a new snapshot automatically, it will fail the test and require Jest to be run with `--updateSnapshot`."
- Vitest docs, Snapshot, CI behavior, raw.githubusercontent.com/vitest-dev/vitest/main/docs/guide/snapshot.md (fetched): "By default, Vitest does not write snapshots in CI (`process.env.CI` is truthy) and any snapshot mismatches, missing snapshots, and obsolete snapshots fail the run."
- insta crate docs, Updating snapshots, raw.githubusercontent.com/mitsuhiko/insta/master/insta/src/lib.rs (fetched): "the new snapshots are stored next to the old ones with the extra `.new` extension"; "`auto`: the default. `no` for CI environments or `new` otherwise"; "`new`: writes snapshots for any failing tests into `.snap.new` files, pending review"; "`always`: writes snapshots for any failing tests into `.snap` files, bypassing review".
- insta source, raw.githubusercontent.com/mitsuhiko/insta/master/cargo-insta/src/cli.rs and insta/src/runtime.rs (fetched): `accept` "Accept all snapshots"; `cargo insta test` `--accept` "Accept all snapshots after test."; the failing-assertion path runs only `if update_result != SnapshotUpdateBehavior::InPlace && !self.tool_config.force_pass()`.
- syrupy README, raw.githubusercontent.com/syrupy-project/syrupy/main/README.md (fetched): "Syrupy will fail a test suite if a snapshot does not exist"; "The `__snapshots__` directory and all its children should be committed along with your test code"; `--snapshot-warn-unused` "Prints a warning on unused snapshots rather than fail the test suite."
- inline-snapshot docs, raw.githubusercontent.com/15r10nk/inline-snapshot/main/docs/pytest.md and docs/index.md (fetched): "You can also use inline-snapshot without any CLI options, in which case the default flags will be used."; "Snapshot comparisons always return `True` when you use one of the flags *create*, *fix*, or *review*."; `review` "Shows a diff report for each category and asks whether you want to apply the changes."; `disable` "is also the default for CI runs"; "The default flags when you are in an interactive terminal are `--inline-snapshot=create,review`"; "Review these changes carefully so that you do not record the result of buggy code in your tests."
- Go source, src/go/printer/printer_test.go, raw.githubusercontent.com/golang/go/master/src/go/printer/printer_test.go (fetched): `var update = flag.Bool("update", false, "update golden files")`; "// update golden files if necessary / if *update { ... os.WriteFile(golden, res, 0644) ... return }"; "// Use go test -update to create/update the respective golden files."
- gotest.tools/v3/golden, pkg.go.dev/gotest.tools/v3/golden (fetched): "Golden files are files in the ./testdata/ subdirectory of the package under test. ... To ensure the update is correct compare the diff of the old expected value to the new expected value."
- ApprovalTests.Java README, Approved File Artifacts, raw.githubusercontent.com/approvals/ApprovalTests.Java/master/README.md (fetched): "The `*.approved.*` files must be checked into source your source control."
- rustc-dev-guide, UI tests, Output comparison, raw.githubusercontent.com/rust-lang/rustc-dev-guide/master/src/tests/ui.md (fetched): "UI tests store the expected output from the compiler in `.stderr` and `.stdout` snapshots next to the test. You normally generate these files with the `--bless` CLI option, and then inspect them manually to verify they contain what you expect."
- go command docs, Test packages, raw.githubusercontent.com/golang/go/master/src/cmd/go/alldocs.go (fetched): "The go tool will ignore a directory named \"testdata\", making it available to hold ancillary data needed by the tests."
- Caveat: the evidence is tool documentation and a standard library's own test practice; no empirical study measures how often a self-writing gating run hides a regression.
