# discovering-subtopics

Builds a maximum-breadth question map across any topic: ten complementary methods run as checkpointed background agents, each writing its own file, and a synthesis pass turns the files into a reader-facing map. Invoke it as `/discovering-subtopics <topic>`.

## Layout

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the session | at invocation |
| `agents/<method>/prompt.md` | each method agent, the coverage-gap auditor and the synthesis agent | when the session spawns it |
| `references/checkpointing-protocol.md` | the session and every method agent | on start and on resume |
| `references/methodology-inventory.md` | the session | when it plans the methods |
| `references/output-template.md` | the session | when it writes the map |
| `references/source-triangulation.md` | the field-intelligence agent | when it searches |
| `maintenance/README.md` | a maintainer | when the skill is evaluated, iterated or gated before a commit; never in a run |
| `maintenance/methodology-provenance.md` | a maintainer | adding a method or re-verifying the source behind one; never in a run |
