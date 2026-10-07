# Series status

Snapshot taken 2026-10-07T17:03 UTC by `series/series-status.py --snapshot`. Journals under `journals/`, finished runs' outputs under `outputs/`.

`done` counts the agents whose results the journal holds (cached for a continuation); `failed` the agents a usage-limit stop or an error ended, which a continuation re-runs. `cards` is the count in the run's own output; a run whose agents failed shipped none, and its cards come from the continuation. A continuation run (batch 3 and later) is one bundle of a topic, named by its part; a topic is finished when every part's run is complete.

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
| 3 | `comments-and-self-documenting-code` 1of2 | 12 | verify 5, fix 5, verify2 1 | fix 1, verify2 4, close1 1 | 0 | run ended, agents failed |
| 3 | `comments-and-self-documenting-code` r2-finish | ? | - | - | - | running or stopped |
| 3 | `layout-and-coding-style` 1of2 | 11 | verify 5, fix 5 | fix 1, verify2 5 | 0 | run ended, agents failed |
| 3 | `layout-and-coding-style` r2-finish | ? | - | - | - | running or stopped |
| 3 | `routine-size-and-parameters` 1of2 | 9 | verify 3, fix 4, verify2 2 | fix 1, verify2 2, close1 2 | 0 | run ended, agents failed |
| 3 | `routine-size-and-parameters` r2-finish | ? | - | - | - | running or stopped |
| 3 | `variables-scope-and-numerics` 1of2 | 12 | verify 5, fix 5 | fix 1, verify2 5 | 0 | run ended, agents failed |
| 3 | `variables-scope-and-numerics` r2-finish | 12 | verify2 5 | - | 5 | run complete |
| 3 | `control-flow` 1of2 | 12 | draft 1, verify 6, fix 5 | fix 1, verify2 5 | 0 | run ended, agents failed |
| 3 | `control-flow` r2-finish | ? | - | - | - | running or stopped |
| 3 | `table-driven-and-state-machines` 1of2 | 8 | verify 3, fix 4, verify2 3, close1 1 | verify2 1, close1 1 | 2 | run ended, agents failed |
| 3 | `table-driven-and-state-machines` r2-finish | ? | - | - | - | running or stopped |
| 3 | `table-driven-and-state-machines` r2-finish | 8 | verify2 1 | - | 2 | run complete |
| 3 | `table-driven-and-state-machines` r2-rest-1of1 | ? | verify 3, fix 3, verify2 1 | - | - | running or stopped |
| 3 | `generics-and-parameterization` 1of2 | 10 | verify 3, fix 4, verify2 2 | fix 1, verify2 2, close1 2 | 0 | run ended, agents failed |
| 3 | `generics-and-parameterization` r2-finish | ? | - | - | - | running or stopped |
| 3 | `api-design-and-use` 1of2 | 12 | verify 6, fix 6 | verify2 6 | 0 | run ended, agents failed |
| 3 | `api-design-and-use` r2-finish | ? | verify2 6 | - | - | running or stopped |
| 3 | `contracts-assertions-and-invariants` 1of2 | 7 | verify 3, fix 4, verify2 2, close1 1 | verify2 2, close1 1 | 1 | run ended, agents failed |
| 3 | `contracts-assertions-and-invariants` r2-finish | ? | - | - | - | running or stopped |
| 3 | `contracts-assertions-and-invariants` r2-finish | 7 | verify2 2 | - | 3 | run complete |
| 3 | `contracts-assertions-and-invariants` r2-rest-1of1 | ? | verify 2, fix 3, verify2 1 | - | - | running or stopped |
| 3 | `api-evolution-and-deprecation` 1of2 | 12 | verify 5, fix 6 | verify2 6 | 0 | run ended, agents failed |
| 3 | `api-evolution-and-deprecation` r2-finish | 12 | verify2 6 | - | 6 | run complete |
| 3 | `defensive-programming` 1of2 | 6 | verify 1, fix 3, verify2 3, close1 3 | - | 3 | run complete |
| 3 | `defensive-programming` 2of2 | 6 | fix 2 | verify 1, verify2 2 | 0 | run ended, agents failed |
| 3 | `defensive-programming` r2-finish | ? | - | - | - | running or stopped |
| 3 | `defensive-programming` r2-rest-1of1 | 6 | verify 1, fix 1, verify2 1, close1 1 | - | 1 | run complete |
| 3 | `defensive-programming` r2-finish | 6 | verify2 2 | - | 2 | run complete |
| 3 | `fault-tolerance-retries-timeouts-fallbacks` 1of2 | 9 | verify 4, fix 5, verify2 2 | verify2 3, close1 2 | 0 | run ended, agents failed |
| 3 | `fault-tolerance-retries-timeouts-fallbacks` r2-finish | ? | - | - | - | running or stopped |
| 3 | `resource-management-and-ownership` 1of2 | 12 | verify 5, fix 6 | verify2 6 | 0 | run ended, agents failed |
| 3 | `resource-management-and-ownership` r2-finish | ? | verify2 6 | - | - | running or stopped |
| 3 | `logging-and-diagnostic-output` 1of2 | 12 | verify 5, fix 5, verify2 2 | fix 1, verify2 3, close1 1 | 1 | run ended, agents failed |
| 3 | `logging-and-diagnostic-output` r2-finish | ? | - | - | - | running or stopped |
| 3 | `complexity-and-deep-modules` 1of2 | 6 | verify 2, fix 3, verify2 3, close1 3 | - | 3 | run complete |
| 3 | `complexity-and-deep-modules` 2of2 | 6 | - | verify 3 | 0 | run ended, agents failed |
| 3 | `complexity-and-deep-modules` r2-rest-1of1 | ? | - | - | - | running or stopped |
| 3 | `complexity-and-deep-modules` r2-rest-1of1 | ? | verify 3, fix 3, verify2 2 | - | - | running or stopped |
| 3 | `information-hiding-and-encapsulation` 1of2 | 8 | verify 4, fix 4, verify2 1 | verify2 3, close1 1 | 0 | run ended, agents failed |
| 3 | `information-hiding-and-encapsulation` r2-finish | ? | - | - | - | running or stopped |
| 3 | `information-hiding-and-encapsulation` r2-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `coupling-and-dependency-direction` 1of2 | 6 | verify 3, fix 3, verify2 3, close1 3 | - | 3 | run complete |
| 3 | `coupling-and-dependency-direction` 2of2 | 6 | - | verify 3 | 0 | run ended, agents failed |
| 3 | `coupling-and-dependency-direction` r2-rest-1of1 | ? | - | - | - | running or stopped |
| 3 | `coupling-and-dependency-direction` r2-rest-1of1 | ? | verify 3, fix 3, verify2 1 | - | - | running or stopped |
| 3 | `duplication-and-single-source-of-truth` 1of2 | 8 | verify 4, fix 4, verify2 2 | verify2 2, close1 2 | 0 | run ended, agents failed |
| 3 | `duplication-and-single-source-of-truth` r2-finish | ? | - | - | - | running or stopped |
| 3 | `duplication-and-single-source-of-truth` r2-finish | 8 | verify2 2 | - | 4 | run complete |
| 3 | `duplication-and-single-source-of-truth` r2-rest-1of1 | ? | verify 3, fix 1 | - | - | running or stopped |
| 3 | `inheritance-versus-composition` 1of2 | 8 | draft 1, verify 4, fix 4 | verify2 4 | 0 | run ended, agents failed |
| 3 | `inheritance-versus-composition` r2-finish | ? | - | - | - | running or stopped |
| 3 | `design-patterns-in-construction` 1of2 | 7 | verify 3, fix 4, verify2 3, close1 3 | verify2 1 | 3 | run ended, agents failed |
| 3 | `design-patterns-in-construction` r2-finish | ? | - | - | - | running or stopped |
| 3 | `design-patterns-in-construction` r2-rest-1of1 | ? | verify 2, fix 3, verify2 2, close1 1 | - | - | running or stopped |
| 3 | `design-patterns-in-construction` r2-finish | 7 | verify2 1 | - | 1 | run complete |
| 3 | `mutable-state-and-immutability` 1of2 | 11 | draft 2, verify 6 | fix 6 | 0 | run ended, agents failed |
| 3 | `mutable-state-and-immutability` r2-rest-1of2 | ? | fix 1 | - | - | running or stopped |
| 3 | `mutable-state-and-immutability` r2-rest-2of2 | ? | - | - | - | running or stopped |
| 3 | `functional-style-and-pipelines` 1of2 | 11 | draft 2, verify 6, fix 4 | fix 2, verify2 4 | 0 | run ended, agents failed |
| 3 | `functional-style-and-pipelines` r2-finish | ? | - | - | - | running or stopped |
| 3 | `domain-modeling-and-domain-language` 1of2 | 10 | verify 5, fix 5, verify2 2 | verify2 3, close1 2 | 0 | run ended, agents failed |
| 3 | `domain-modeling-and-domain-language` r2-finish | ? | - | - | - | running or stopped |
