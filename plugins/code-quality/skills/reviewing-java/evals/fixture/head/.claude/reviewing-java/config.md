---
project_name: FixtureApp
base_branch: main
---
# FixtureApp review context

## Tolerances

- The `Stats#sample` counter feeds a dashboard only; it is an approximate statistics counter and lost increments are accepted.

## Invariants

1. **Cache values are loaded once**: A key that two request threads ask for at the same time is loaded once and both see the same value. Violation: duplicate loads and a value that flips between the two.
2. **Cache loads stay cheap**: `Cache#load` allocates no large buffers per call. Violation: a large buffer allocated inside `Cache#load`. Enforced by `CacheLoadBench`.
3. **Repositories prefer constructor injection**: Repository classes should take their dependencies through the constructor. Violation: a field-injected repository (`@Autowired` on a field).
4. **Totals never go negative**: `Totals#transfer` rejects a transfer that would drive a balance below zero. Violation: a negative balance written by `Totals#transfer`. Enforced by `TotalsTransferTest`.

We also want to avoid `System.out` in production classes.
