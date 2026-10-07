# Series status

Snapshot taken 2026-10-07T12:01 UTC by `series/series-status.py --snapshot`. Journals under `journals/`, finished runs' outputs under `outputs/`.

`done` counts the agents whose results the journal holds (cached for a continuation); `failed` the agents a usage-limit stop or an error ended, which a continuation re-runs. `cards` is the count in the run's own output; a run whose agents failed shipped none, and its cards come from the continuation.

| Batch | Topic | Spine card rules | Done | Failed | Cards in output | State |
|--|--|--|--|--|--|--|
| 1 | `comments-and-self-documenting-code` | 12 | sources 3, spine 1, draft 12, verify 2 | spine 1, draft 4, verify 8 | - | running or stopped |
| 1 | `layout-and-coding-style` | 11 | sources 3, spine 1, draft 11, verify 2 | spine 1, draft 5, verify 6 | - | running or stopped |
| 1 | `routine-size-and-parameters` | 9 | sources 3, spine 1, draft 9, verify 3 | spine 1, draft 1, verify 8 | - | running or stopped |
| 1 | `variables-scope-and-numerics` | 14 | sources 3, spine 1, draft 12, verify 1 | spine 1, draft 5, verify 7 | - | running or stopped |
| 1 | `control-flow` | 18 | sources 3, spine 1, draft 9 | sources 1, spine 1, draft 11, verify 1 | - | running or stopped |
| 1 | `table-driven-and-state-machines` | 8 | sources 3, spine 1, draft 8, verify 2 | spine 1, draft 2, verify 6 | - | running or stopped |
| 1 | `generics-and-parameterization` | 10 | sources 3, spine 1, draft 10, verify 3 | spine 1, draft 3, verify 7 | - | running or stopped |
| 1 | `api-design-and-use` | 13 | sources 3, spine 1, draft 12 | spine 1, draft 6, verify 6 | - | running or stopped |
| 1 | `contracts-assertions-and-invariants` | 7 | sources 3, spine 1, draft 7, verify 2 | sources 1, spine 1, draft 3, verify 4 | - | running or stopped |
| 1 | `api-evolution-and-deprecation` | 14 | sources 3, spine 1, draft 12, verify 1 | spine 1, draft 5, verify 7 | - | running or stopped |
| 1 | `defensive-programming` | 6 | sources 3, spine 1, draft 6, verify 4 | spine 1, verify 6 | - | running or stopped |
| 1 | `fault-tolerance-retries-timeouts-fallbacks` | 9 | sources 3, spine 1, draft 9, verify 2 | sources 1, spine 1, draft 5, verify 4 | - | running or stopped |
| 1 | `resource-management-and-ownership` | 13 | sources 3, spine 1, draft 12, verify 2 | spine 1, draft 4, verify 8 | - | running or stopped |
| 1 | `logging-and-diagnostic-output` | 12 | sources 3, spine 1, draft 12, verify 2 | spine 1, draft 5, verify 7 | - | running or stopped |
| 2 | `complexity-and-deep-modules` | 6 | sources 3, spine 1, draft 6, verify 1 | sources 3, draft 5, verify 1 | - | running or stopped |
| 2 | `information-hiding-and-encapsulation` | 8 | sources 3, spine 1, draft 8 | sources 3, draft 6, verify 2 | - | running or stopped |
| 2 | `coupling-and-dependency-direction` | 6 | sources 3, spine 1, draft 6 | sources 3, draft 6 | - | running or stopped |
| 2 | `duplication-and-single-source-of-truth` | 8 | sources 3, spine 1, draft 8 | sources 3, draft 8 | - | running or stopped |
| 2 | `inheritance-versus-composition` | 8 | sources 3, spine 1, draft 6 | sources 3, draft 8 | - | running or stopped |
| 2 | `design-patterns-in-construction` | 7 | sources 3, spine 1, draft 7, verify 2 | sources 3, draft 5, verify 2 | - | running or stopped |
| 2 | `mutable-state-and-immutability` | 11 | sources 3, spine 1, draft 9 | sources 3, draft 9, verify 2 | - | running or stopped |
| 2 | `functional-style-and-pipelines` | 11 | sources 3, spine 1, draft 8 | sources 3, draft 11 | - | running or stopped |
| 2 | `domain-modeling-and-domain-language` | 10 | sources 3, spine 1, draft 10 | sources 3, draft 9, verify 1 | - | running or stopped |
