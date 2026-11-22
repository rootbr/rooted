# Runs of the cold-read measurement

Every iteration reads the same sixteen texts once: four reports, each intact and with one of three omissions planted (`../plants.json`). `python3 ../../grade_cold_read.py ../plants.json <iteration>` reproduces an iteration's `grading.json`; its `prompt.md` and `questions.json` are the instructions and the questions the readers got.

| Iteration | Reader model | Instructions | Questions | Decision marked | Cause marked | Introducing sentence noticed | Intact reports marked |
|--|--|--|--|--|--|--|--|
| 1 | Opus | the first version | 5 | 4 of 4 | 3 of 4 | 0 of 4 | 2 of 4 |
| 2 | Opus | before the context audit's wording fixes | 6 | 4 of 4 | 4 of 4 | 0 of 4 | 0 of 4 |
| 3 | Opus | as shipped | 6 | 4 of 4 | 4 of 4 | 0 of 4 | 0 of 4 |
| 4 | Sonnet | as shipped | 6 | 4 of 4 | 4 of 4 | 1 of 4 | 1 of 4 |
| 5 | Haiku | as shipped | 6 | 4 of 4 | 4 of 4 | 1 of 4 | 1 of 4 |
| 6 | Opus | with the retelling of a first part | 6 | 4 of 4 | 4 of 4 | 0 of 4 | 0 of 4 |

A model name is the alias the agent was dispatched with, in Claude Code 2.1.325 for iterations 1 to 5 and 2.1.331 for iteration 6. The questions file of iteration 6 carries no `retell`, so it measures the answers to the questions under the instructions that add the retelling; each of its readers wrote its object to a file, where the instructions deliver it as the message. In iterations 4 and 5 the marked intact report is the same one, on the question about what is unverified: the report names what was not verified, and the reader asked whether there was more.
