# Runs of the retelling measurement

Every iteration reads the eight texts of `../plants.json` three times in each arm. `python3 ../../grade_retelling.py ../plants.json <iteration>` reproduces an iteration's `grading.json`; its `prompt.md` holds the instructions the readers got.

| Iteration | Reader model | Effort | Claude Code | Instructions |
|--|--|--|--|--|
| 1 | Opus (`claude-opus-5-5`) | high | 2.1.331 | `agents/cold-reader.md` of the plugin at version 10.2.0 |

| Iteration | Arm | Removals caught | Intact texts marked | Readings that list a gap, removed and intact |
|--|--|--|--|--|
| 1 | `retell` | 12 of 12 | 0 of 12 | 12 of 12 and 2 of 12 |
| 1 | `questions` | 12 of 12 | 6 of 12 | none asked |

In iteration 1 the two arms catch the same share, a difference of 0 points with a one-sided Fisher exact p of 1, which goes against the claim. Every answer that marks a removal in the `questions` arm marks it on the question about the steps and names the number of steps the opening announces; the six marked intact texts are `cache` and `rotation` in every round, on the question about the example.

A model name is the alias the agent was dispatched with. A reader sees a text under a name that hides whether a step was removed: `python3 ../../cold-read/plant.py ../plants.json --blind <dir>` writes the copies and their key, and `--collect <dir> <iteration>/<arm>/round-<n>` sorts the answers by the key.
