# Series status

Snapshot taken 2026-10-09T05:27 UTC by `series/series-status.py --snapshot`. Journals under `journals/`, finished runs' outputs under `outputs/`.

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
| 3 | `comments-and-self-documenting-code` 1of2 | ? | verify 5, fix 5, verify2 1 | fix 1, verify2 4, close1 1 | - | running or stopped |
| 3 | `comments-and-self-documenting-code` r2-finish | ? | - | - | - | running or stopped |
| 3 | `comments-and-self-documenting-code` r3-finish | ? | verify2 4 | - | - | running or stopped |
| 3 | `comments-and-self-documenting-code` r3-rest | ? | verify 5, fix 7, verify2 7, close1 6 | - | - | running or stopped |
| 3 | `layout-and-coding-style` 1of2 | ? | verify 5, fix 5 | fix 1, verify2 5 | - | running or stopped |
| 3 | `layout-and-coding-style` r2-finish | ? | - | - | - | running or stopped |
| 3 | `layout-and-coding-style` r3-finish | ? | verify2 5 | - | - | running or stopped |
| 3 | `layout-and-coding-style` r3-rest | ? | verify 4, fix 6, verify2 6, close1 6 | - | - | running or stopped |
| 3 | `routine-size-and-parameters` 1of2 | ? | verify 3, fix 4, verify2 2 | fix 1, verify2 2, close1 2 | - | running or stopped |
| 3 | `routine-size-and-parameters` r2-finish | ? | - | - | - | running or stopped |
| 3 | `routine-size-and-parameters` r3-finish | ? | - | - | - | running or stopped |
| 3 | `routine-size-and-parameters` r4-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `routine-size-and-parameters` r3-rest | ? | verify 3, fix 4 | - | - | running or stopped |
| 3 | `routine-size-and-parameters` r5-finish | ? | verify2 4 | - | - | running or stopped |
| 3 | `variables-scope-and-numerics` 1of2 | ? | verify 5, fix 5 | fix 1, verify2 5 | - | running or stopped |
| 3 | `variables-scope-and-numerics` r2-finish | ? | verify2 5 | - | - | running or stopped |
| 3 | `variables-scope-and-numerics` r3-rest | ? | verify 6, fix 7, verify2 7, close1 5 | - | - | running or stopped |
| 3 | `variables-scope-and-numerics` r4-finish | ? | - | - | - | running or stopped |
| 3 | `control-flow` 1of2 | ? | draft 1, verify 6, fix 5 | fix 1, verify2 5 | - | running or stopped |
| 3 | `control-flow` r2-finish | ? | - | - | - | running or stopped |
| 3 | `control-flow` r3-finish | ? | verify2 5 | - | - | running or stopped |
| 3 | `control-flow` r3-rest | ? | draft 3, verify 6, fix 7, verify2 7, close1 7 | - | - | running or stopped |
| 3 | `table-driven-and-state-machines` 1of2 | ? | verify 3, fix 4, verify2 3, close1 1 | verify2 1, close1 1 | - | running or stopped |
| 3 | `table-driven-and-state-machines` r2-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `table-driven-and-state-machines` r2-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `table-driven-and-state-machines` r2-rest-1of1 | ? | verify 3, fix 3, verify2 1 | fix 1, verify2 2, close1 1 | - | running or stopped |
| 3 | `table-driven-and-state-machines` r3-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `table-driven-and-state-machines` r3-rest | ? | fix 1, verify2 1, close1 1 | - | - | running or stopped |
| 3 | `generics-and-parameterization` 1of2 | ? | verify 3, fix 4, verify2 2 | fix 1, verify2 2, close1 2 | - | running or stopped |
| 3 | `generics-and-parameterization` r2-finish | ? | - | - | - | running or stopped |
| 3 | `generics-and-parameterization` r3-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `generics-and-parameterization` r3-rest | ? | verify 4, fix 6, verify2 6, close1 4 | - | - | running or stopped |
| 3 | `api-design-and-use` 1of2 | ? | verify 6, fix 6 | verify2 6 | - | running or stopped |
| 3 | `api-design-and-use` r2-finish | ? | verify2 6 | - | - | running or stopped |
| 3 | `api-design-and-use` r3-rest | ? | verify 6, fix 6, verify2 6, close1 6 | - | - | running or stopped |
| 3 | `contracts-assertions-and-invariants` 1of2 | ? | verify 3, fix 4, verify2 2, close1 1 | verify2 2, close1 1 | - | running or stopped |
| 3 | `contracts-assertions-and-invariants` r2-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `contracts-assertions-and-invariants` r2-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `contracts-assertions-and-invariants` r2-rest-1of1 | ? | verify 2, fix 3, verify2 2, close1 1 | verify2 1, close1 1 | - | running or stopped |
| 3 | `contracts-assertions-and-invariants` r3-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `api-evolution-and-deprecation` 1of2 | ? | verify 5, fix 6 | verify2 6 | - | running or stopped |
| 3 | `api-evolution-and-deprecation` r2-finish | ? | verify2 6 | - | - | running or stopped |
| 3 | `api-evolution-and-deprecation` r3-rest | ? | verify 6, fix 6, verify2 6, close1 6 | - | - | running or stopped |
| 3 | `defensive-programming` 1of2 | ? | verify 1, fix 3, verify2 3, close1 3 | - | - | running or stopped |
| 3 | `defensive-programming` 2of2 | ? | fix 2 | verify 1, verify2 2 | - | running or stopped |
| 3 | `defensive-programming` r2-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `defensive-programming` r2-rest-1of1 | ? | verify 1, fix 1, verify2 1, close1 1 | - | - | running or stopped |
| 3 | `defensive-programming` r2-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `fault-tolerance-retries-timeouts-fallbacks` 1of2 | ? | verify 4, fix 5, verify2 2 | verify2 3, close1 2 | - | running or stopped |
| 3 | `fault-tolerance-retries-timeouts-fallbacks` r2-finish | ? | - | - | - | running or stopped |
| 3 | `fault-tolerance-retries-timeouts-fallbacks` r3-finish | ? | verify2 3 | - | - | running or stopped |
| 3 | `fault-tolerance-retries-timeouts-fallbacks` r3-rest | ? | verify 1 | - | - | running or stopped |
| 3 | `fault-tolerance-retries-timeouts-fallbacks` r4-rest | ? | verify 2, fix 4, verify2 2 | - | - | running or stopped |
| 3 | `fault-tolerance-retries-timeouts-fallbacks` r5-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `resource-management-and-ownership` 1of2 | ? | verify 5, fix 6 | verify2 6 | - | running or stopped |
| 3 | `resource-management-and-ownership` r2-finish | ? | verify2 6 | - | - | running or stopped |
| 3 | `resource-management-and-ownership` r3-rest | ? | verify 5, fix 6, verify2 6, close1 6 | - | - | running or stopped |
| 3 | `logging-and-diagnostic-output` 1of2 | ? | verify 5, fix 5, verify2 2 | fix 1, verify2 3, close1 1 | - | running or stopped |
| 3 | `logging-and-diagnostic-output` r2-finish | ? | - | - | - | running or stopped |
| 3 | `logging-and-diagnostic-output` r3-finish | ? | verify2 3 | - | - | running or stopped |
| 3 | `logging-and-diagnostic-output` r3-rest | ? | verify 5, fix 7, verify2 7, close1 6 | - | - | running or stopped |
| 3 | `complexity-and-deep-modules` 1of2 | ? | verify 2, fix 3, verify2 3, close1 3 | - | - | running or stopped |
| 3 | `complexity-and-deep-modules` 2of2 | ? | - | verify 3 | - | running or stopped |
| 3 | `complexity-and-deep-modules` r2-rest-1of1 | ? | verify 3, fix 3, verify2 2, close1 2 | verify2 1 | - | running or stopped |
| 3 | `complexity-and-deep-modules` r2-rest-1of1 | ? | verify 3, fix 3, verify2 2, close1 2 | verify2 1 | - | running or stopped |
| 3 | `complexity-and-deep-modules` r3-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `information-hiding-and-encapsulation` 1of2 | ? | verify 4, fix 4, verify2 1 | verify2 3, close1 1 | - | running or stopped |
| 3 | `information-hiding-and-encapsulation` r2-finish | ? | verify2 3 | - | - | running or stopped |
| 3 | `information-hiding-and-encapsulation` r2-finish | ? | verify2 3 | - | - | running or stopped |
| 3 | `information-hiding-and-encapsulation` r3-rest | ? | verify 4, fix 4, verify2 4, close1 4 | - | - | running or stopped |
| 3 | `coupling-and-dependency-direction` 1of2 | ? | verify 3, fix 3, verify2 3, close1 3 | - | - | running or stopped |
| 3 | `coupling-and-dependency-direction` 2of2 | ? | - | verify 3 | - | running or stopped |
| 3 | `coupling-and-dependency-direction` r2-rest-1of1 | ? | verify 3, fix 3, verify2 1 | verify2 2 | - | running or stopped |
| 3 | `coupling-and-dependency-direction` r2-rest-1of1 | ? | verify 3, fix 3, verify2 1 | verify2 2 | - | running or stopped |
| 3 | `coupling-and-dependency-direction` r3-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `duplication-and-single-source-of-truth` 1of2 | ? | verify 4, fix 4, verify2 2 | verify2 2, close1 2 | - | running or stopped |
| 3 | `duplication-and-single-source-of-truth` r2-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `duplication-and-single-source-of-truth` r2-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `duplication-and-single-source-of-truth` r2-rest-1of1 | ? | verify 3, fix 3 | verify 1, verify2 3 | - | running or stopped |
| 3 | `duplication-and-single-source-of-truth` r3-finish | ? | verify2 3 | - | - | running or stopped |
| 3 | `duplication-and-single-source-of-truth` r3-rest | ? | verify 1, fix 1, verify2 1, close1 1 | - | - | running or stopped |
| 3 | `inheritance-versus-composition` 1of2 | ? | draft 1, verify 4, fix 4 | verify2 4 | - | running or stopped |
| 3 | `inheritance-versus-composition` r2-finish | ? | - | - | - | running or stopped |
| 3 | `inheritance-versus-composition` r3-finish | ? | verify2 4 | - | - | running or stopped |
| 3 | `inheritance-versus-composition` r3-rest | ? | draft 1, verify 4, fix 4 | - | - | running or stopped |
| 3 | `inheritance-versus-composition` r4-finish | ? | verify2 4 | - | - | running or stopped |
| 3 | `design-patterns-in-construction` 1of2 | ? | verify 3, fix 4, verify2 3, close1 3 | verify2 1 | - | running or stopped |
| 3 | `design-patterns-in-construction` r2-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `design-patterns-in-construction` r2-rest-1of1 | ? | verify 2, fix 3, verify2 2, close1 2 | verify2 1 | - | running or stopped |
| 3 | `design-patterns-in-construction` r2-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `design-patterns-in-construction` r3-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `mutable-state-and-immutability` 1of2 | ? | draft 2, verify 6 | fix 6 | - | running or stopped |
| 3 | `mutable-state-and-immutability` r2-rest-1of2 | ? | fix 1 | - | - | running or stopped |
| 3 | `mutable-state-and-immutability` r2-rest-2of2 | ? | - | - | - | running or stopped |
| 3 | `mutable-state-and-immutability` r3-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `mutable-state-and-immutability` r3-rest | ? | verify 5, fix 10, verify2 10, close1 10 | - | - | running or stopped |
| 3 | `functional-style-and-pipelines` 1of2 | ? | draft 2, verify 6, fix 4 | fix 2, verify2 4 | - | running or stopped |
| 3 | `functional-style-and-pipelines` r2-finish | ? | - | - | - | running or stopped |
| 3 | `functional-style-and-pipelines` r3-finish | ? | verify2 4 | - | - | running or stopped |
| 3 | `functional-style-and-pipelines` r3-rest | ? | draft 1, verify 5, fix 7, verify2 7, close1 5 | - | - | running or stopped |
| 3 | `domain-modeling-and-domain-language` 1of2 | ? | verify 5, fix 5, verify2 2 | verify2 3, close1 2 | - | running or stopped |
| 3 | `domain-modeling-and-domain-language` r2-finish | ? | - | - | - | running or stopped |
| 3 | `domain-modeling-and-domain-language` r3-finish | ? | verify2 2 | - | - | running or stopped |
| 3 | `domain-modeling-and-domain-language` r3-rest | ? | - | - | - | running or stopped |
| 3 | `domain-modeling-and-domain-language` r4-finish | ? | verify2 1 | - | - | running or stopped |
| 3 | `domain-modeling-and-domain-language` r4-rest | ? | verify 5, fix 5, verify2 5, close1 5 | - | - | running or stopped |
| 4 | `unit-testing-and-test-quality` | 13 | sources 3, spine 1, draft 12, verify 12, fix 12, verify2 12, close1 12 | - | - | running or stopped |
| 4 | `test-first-and-test-driven-development` | 2 | sources 3, spine 1, draft 2, verify 2, fix 2, verify2 2, close1 1 | - | - | running or stopped |
| 4 | `larger-tests-integration-and-end-to-end` | 12 | sources 3, spine 1, draft 12, verify 12, fix 12, verify2 12, close1 10 | - | - | running or stopped |
| 4 | `property-based-testing` | 14 | sources 3, spine 1, draft 12, verify 12, fix 12, verify2 12, close1 11 | - | - | running or stopped |
| 4 | `refactoring` | 5 | sources 3, spine 1, draft 5, verify 5, fix 5, verify2 5, close1 5 | - | - | running or stopped |
| 4 | `code-smells-and-antipatterns` | 6 | sources 3, spine 1, draft 6, verify 6, fix 6, verify2 6, close1 6 | - | - | running or stopped |
| 4 | `seams-and-characterization-tests` | 7 | sources 3, spine 1, draft 7, verify 7, fix 7, verify2 7, close1 7 | - | - | running or stopped |
| 4 | `large-scale-changes-and-migrations` | 9 | sources 3, spine 1, draft 9, verify 9, fix 9, verify2 9, close1 7 | - | - | running or stopped |
| 4 | `small-steps-and-minimal-diffs` | 6 | sources 3, spine 1, draft 6, verify 6, fix 6, verify2 6, close1 6 | - | - | running or stopped |
| 4 | `technical-debt` | 6 | sources 3, spine 1, draft 6, verify 6, fix 6, verify2 6, close1 6 | - | - | running or stopped |
| 4 | `debugging` | 6 | sources 3, spine 1, draft 6, verify 6, fix 6, verify2 6, close1 6 | - | - | running or stopped |
| 4 | `profiling-and-code-tuning` | 8 | sources 3, spine 1, draft 8, verify 8, fix 8, verify2 8, close1 8 | - | - | running or stopped |
| 4 | `algorithm-and-data-structure-choice` | 10 | sources 3, spine 1, draft 10, verify 10, fix 10 | - | - | running or stopped |
| 4 | `algorithm-and-data-structure-choice` finish | 10 | verify2 10 | - | 7 | run ended, agents failed |
| 4 | `algorithm-and-data-structure-choice` r2-finish | 10 | - | - | 3 | run complete |
| 4 | `build-warnings-static-analysis-ci` | 10 | sources 3, spine 1, draft 10, verify 2 | - | - | running or stopped |
| 4 | `build-warnings-static-analysis-ci` r1-1of2 | 10 | verify 4, fix 5, verify2 5, close1 4 | close1 1 | 4 | run ended, agents failed |
| 4 | `build-warnings-static-analysis-ci` r2-1of2 | 10 | - | - | 1 | run complete |
| 4 | `build-warnings-static-analysis-ci` r1-2of2 | ? | - | - | - | running or stopped |
| 4 | `dependency-management` | 11 | sources 3, spine 1, draft 6 | - | - | running or stopped |
| 4 | `dependency-management` r1-1of2 | 11 | draft 3, verify 6, fix 5, verify2 2 | verify2 3, close1 2 | 1 | run ended, agents failed |
| 4 | `dependency-management` r1-2of2 | 11 | draft 2, verify 5, fix 5, verify2 3 | verify2 2, close1 3 | 0 | run ended, agents failed |
| 4 | `dependency-management` r2-1of2 | ? | verify2 2 | - | - | running or stopped |
| 4 | `dependency-management` r2-2of2 | 11 | verify2 2 | - | 5 | run complete |
