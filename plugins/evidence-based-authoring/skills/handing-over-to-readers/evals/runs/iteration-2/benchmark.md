# Skill Benchmark: handing-over-to-readers

**Model**: Opus worker agents; graded by `grade.py`
**Date**: 2026-11-07
**Evals**: 1–6 (1 run each per configuration)
**Language**: English prompts, fixtures and outputs

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 43% ± 22% | +0.57 |
| Time | 81.2s ± 26.9s | 28.9s ± 8.1s | +52.2s |
| Tokens | 64986 ± 6015 | 45052 ± 1293 | +19934 |

Expectations passed: 52 of 52 with the skill, 21 of 52 without it.

## Per eval

| Eval | With Skill | Without Skill |
|--|--|--|
| 1 · client-question-list | 8/8 | 6/8 |
| 2 · operator-report-with-failing-build | 10/10 | 3/10 |
| 3 · question-to-operator-with-default | 6/6 | 4/6 |
| 4 · operator-report-retry-and-another-teams-test | 10/10 | 3/10 |
| 5 · operator-report-rename-and-a-stale-override | 9/9 | 3/9 |
| 6 · operator-report-upgrade-that-silences-an-alert | 9/9 | 2/9 |

## Notes

- The reports are written in English from English prompts and fixtures; it is the first run of the story form in English.
- Both configurations ran on the same worker agent type, whose own definition still carries the report shape of version 5.0.0 (a first page of labelled lines). The baseline is therefore the earlier habit of this environment, not an agent without guidance.
- The runs came in two batches on one day: all six evals, then evals 1, 2 and 6 once more after their fixtures were rewritten. The outputs kept for those three are of the second batch.
- Seven checks of grade.py tested a wording instead of the expectation and were corrected after a first grading. From the first batch: the client list's 'second channel' written as 'second line'; a count of passing tests that stands beside the exit code of the run; the performance run named without the tool's name; the config location told as a decision in plain words; anchors read from the directory above the fixtures. From the second batch: the second channel written as 'second link'; the performance run told as 'nobody measured whether it slows the path'. Before the corrections the skill's outputs failed six expectations in the first batch and two in the second, for those reasons alone.
- An eighth check of grade.py was corrected on 2026-11-22, after the run was read: an option bullet of a client's list is read as part of the item above it. Eval 1 without the skill passes the expectation on the second channel, 6 of 8, where the first grading counted its option B as a second item.
- One run per configuration: the standard deviations are across the six evals, not across repeated runs.
