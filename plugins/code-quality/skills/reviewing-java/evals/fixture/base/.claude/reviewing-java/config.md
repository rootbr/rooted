---
project_name: FixtureApp
base_branch: main
---
# FixtureApp review context

## Tolerances

- The `Stats#sample` counter feeds a dashboard only; it is an approximate statistics counter and lost increments are accepted.

## Invariants

1. **Cache values are loaded once**: A key that two request threads ask for at the same time is loaded once and both see the same value. Violation: duplicate loads and a value that flips between the two.
