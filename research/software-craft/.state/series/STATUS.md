# Series status

Snapshot taken 2026-10-14T23:52 UTC by `series/series-status.py --snapshot`. Journals under `journals/`, finished runs' outputs under `outputs/`.

`done` counts the agents whose results the journal holds (cached for a continuation); `failed` the agents a usage-limit stop or an error ended, which a continuation re-runs. `cards` is the count in the run's own output; a run whose agents failed shipped none, and its cards come from the continuation. A continuation run (batch 3 and later) is one bundle of a topic, named by its part; a topic is finished when every part's run is complete.

| Batch | Topic | Spine card rules | Done | Failed | Cards in output | State |
|--|--|--|--|--|--|--|
| 5 | `security-hygiene-in-ordinary-code` r1 | ? | sources 2 | sources 1, spine 1 | - | running or stopped |
| 5 | `security-hygiene-in-ordinary-code` r1-sources | 12 | sources 1, spine 1, draft 12, verify 12, fix 12, verify2 12, close1 11 | - | - | running or stopped |
| 5 | `security-hygiene-in-ordinary-code` r2-1of2 | ? | fix2 6, verify3 6, close2 4 | - | - | running or stopped |
| 5 | `security-hygiene-in-ordinary-code` r2-2of2 | ? | fix2 5, verify3 5, close2 5 | - | - | running or stopped |
| 5 | `parsing-and-grammar-based-input` r1 | 13 | sources 3, spine 1, draft 12, verify 12, fix 3 | fix 9, verify2 3 | - | running or stopped |
| 5 | `parsing-and-grammar-based-input` r1-rest | ? | fix 9, verify2 9, close1 8 | - | - | running or stopped |
| 5 | `parsing-and-grammar-based-input` r1-finish | ? | verify2 3, close2 2 | - | - | running or stopped |
| 5 | `parsing-and-grammar-based-input` r2-1of2 | ? | fix2 5, verify3 5, close2 5 | - | - | running or stopped |
| 5 | `parsing-and-grammar-based-input` r2-2of2 | ? | fix2 5, verify3 5, close2 3 | - | - | running or stopped |
| 5 | `runtime-configuration` r1 | 11 | sources 3, spine 1, draft 11, verify 8 | verify 3, fix 8 | - | running or stopped |
| 5 | `runtime-configuration` r1-rest | ? | verify 3, fix 11, verify2 11, close1 10 | - | - | running or stopped |
| 5 | `runtime-configuration` r2-1of2 | ? | fix2 5, verify3 3 | verify3 2, close2 1 | - | running or stopped |
| 5 | `runtime-configuration` r2-2of2 | ? | fix2 4 | fix2 1, verify3 4 | - | running or stopped |
| 5 | `runtime-configuration` r2-finish | ? | verify3 6, close3 6 | - | - | running or stopped |
| 5 | `runtime-configuration` r2-rest | ? | fix2 1, verify3 1 | - | - | running or stopped |
| 5 | `internationalization-and-text-encoding` r1 | 14 | sources 3, spine 1, draft 12, verify 12, fix 12, verify2 12, close1 11 | - | 12 | run complete |
| 5 | `internationalization-and-text-encoding` r2-1of2 | 12 | fix2 6 | verify3 6 | 0 | run ended, agents failed |
| 5 | `internationalization-and-text-encoding` r2-2of2 | 12 | fix2 5, verify3 5, close2 2 | - | 5 | run complete |
| 5 | `internationalization-and-text-encoding` r2-finish-1of2 | 12 | verify3 3, close3 2 | - | 3 | run complete |
| 5 | `internationalization-and-text-encoding` r2-finish-2of2 | 12 | verify3 3, close3 2 | - | 3 | run complete |
| 5 | `code-review-as-author-and-reviewer` r1 | 6 | sources 3, spine 1, draft 6, verify 6, fix 6, verify2 6, close1 4 | - | 6 | run complete |
| 5 | `code-review-as-author-and-reviewer` r2 | 6 | fix2 4, verify3 4, close2 3 | - | 4 | run complete |
| 5 | `documentation-beyond-comments` r1 | 13 | sources 3, spine 1, draft 12, verify 12, fix 12, verify2 12, close1 10 | - | 12 | run complete |
| 5 | `documentation-beyond-comments` r2 | 12 | fix2 10, verify3 6 | verify3 4, close2 5 | 1 | run ended, agents failed |
| 5 | `documentation-beyond-comments` r2-finish | 12 | verify3 4, close3 8 | - | 9 | run complete |
| 5 | `reading-and-understanding-code` r1 | 4 | sources 3, spine 1, draft 4, verify 4, fix 4, verify2 4, close1 4 | - | 4 | run complete |
| 5 | `reading-and-understanding-code` r2 | 4 | fix2 4, verify3 4, close2 2 | - | 4 | run complete |
| 6 | `gaps-performance` r1 | 5 | sources 3, spine 1, draft 5, verify 2 | verify 3, fix 2 | 0 | run ended, agents failed |
| 6 | `gaps-performance` r1-finish | 5 | verify 3, fix 5, verify2 5, close1 4 | - | 5 | run complete |
| 6 | `gaps-performance` r2 | 5 | fix2 4, verify3 4, close2 3 | - | 4 | run complete |
| 6 | `gaps-errors` r1 | 3 | sources 3, spine 1 | - | - | running or stopped |
| 6 | `gaps-code` r1 | ? | - | - | - | running or stopped |
| r2 | `comments-and-self-documenting-code` r2tree | 12 | verify3 12, close3 3 | - | 12 | run complete |
| r2 | `layout-and-coding-style` r2tree | 11 | verify3 11, close3 2 | - | 11 | run complete |
| r2 | `routine-size-and-parameters` r2tree | 9 | verify3 7, close3 3 | - | 7 | run complete |
| r2 | `variables-scope-and-numerics` r2tree | 14 | verify3 9 | verify3 3, close3 1 | 8 | run ended, agents failed |
| r2 | `variables-scope-and-numerics` r2tree-rest | 14 | verify3 4, close3 2 | - | 4 | run complete |
| r2 | `control-flow` r2tree | 18 | verify3 10, close3 1 | - | 10 | run complete |
| r2 | `table-driven-and-state-machines` r2tree | 8 | verify3 8, close3 3 | - | 8 | run complete |
| r2 | `generics-and-parameterization` r2tree | 10 | verify3 10, close3 3 | - | 10 | run complete |
| r2 | `api-design-and-use` r2tree | ? | verify3 12 | - | - | running or stopped |
