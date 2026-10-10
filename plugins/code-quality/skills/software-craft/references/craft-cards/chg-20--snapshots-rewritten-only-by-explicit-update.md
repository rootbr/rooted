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
