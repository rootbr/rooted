# researching-topics

Researches a question on the web with source verification and critical analysis: it classifies the query, chooses sources by its class, verifies each claim across independent sources and presents the findings with the certainty the sources support. A broad topic first gets a question map from `/discovering-subtopics`, and the report on it is appraised by `/appraising-research`. Invoke it as `/researching-topics <question>`.

## Layout

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the session | at invocation |
| `maintenance/README.md` | a maintainer | when a rule is added, changed or re-verified; never in a run |
| `maintenance/skill-provenance.md` | a maintainer | to see what a rule rests on, or to record it for a new rule; never in a run |
| `maintenance/pending-evidence.md` | a maintainer | to see which claims wait for a test and which tests were found; never in a run |
| `maintenance/citations.json` | a maintainer | to check that the quoted words of the two files stand in their sources; never in a run |
