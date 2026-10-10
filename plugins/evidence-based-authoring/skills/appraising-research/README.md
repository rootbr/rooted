# appraising-research

Critically appraises a finished research report or analytical document: seven independent critique methods run as background agents, an adjudicator deduplicates and ranks their findings, a debate stage stress-tests the highest-stakes ones, and the result is a ranked re-check list with revised confidence in the main conclusions. Invoke it as `/appraising-research <report>`.

## Layout

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the session | at invocation |
| `agents/method-c0N-*/prompt.md` | each of the seven critique agents | when the session spawns it |
| `agents/decomposer/`, `agents/adjudicator/`, `agents/debate/`, `agents/synthesis/` | the single-agent stages | in their phase |
| `references/appraisal-methodology.md` | the session and the seven critique agents | when a method is applied |
| `references/finding-schema.md` | the session and every agent that emits or ranks findings | when a finding is written or ranked |
| `references/checkpointing-protocol.md` | the session | on start and on resume |
| `maintenance/README.md` | a maintainer | when the skill is evaluated, iterated or gated before a commit; never in a run |
