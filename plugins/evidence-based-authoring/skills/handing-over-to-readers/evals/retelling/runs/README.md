# Runs of the retelling measurement

Every iteration reads the eight texts of `../plants.json` three times in each arm. `python3 ../../grade_retelling.py ../plants.json <iteration>` reproduces an iteration's `grading.json`; its `prompt.md` holds the instructions the readers got.

| Iteration | Reader model | Effort | Claude Code | Instructions |
|--|--|--|--|--|
| 1 | Opus (`claude-opus-5-5`) | high | 2.1.331 | `agents/cold-reader.md` of the plugin at version 10.2.0 |

A model name is the alias the agent was dispatched with. A reader sees a text under a name that hides whether a step was removed: `python3 ../../cold-read/plant.py ../plants.json --blind <dir>` writes the copies and their key, and `--collect <dir> <iteration>/<arm>/round-<n>` sorts the answers by the key.
