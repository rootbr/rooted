# auditing-ai-context

Audit skill for Claude Code; paths in this file are relative to this directory. It checks what an agent reads — `CLAUDE.md`, `SKILL.md`, agent prompts, knowledge-base cards — and what an agent writes — a README, a design doc, code comments, a drafted answer — against a corpus of atomic rule cards, one sub-agent per card that applies to the target, and returns ranked patches it applies only after you approve them. Invoked for writing, it drafts against the same rules.

## Quickstart

```
/auditing-ai-context path/to/SKILL.md
/auditing-ai-context README.md
```

The audit needs the Workflow tool (Claude Code with dynamic workflows enabled); without it the skill dispatches one sub-agent per card itself and says so.

## Layout

This skill's instance of the repository `README.md` §Skill layout:

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the session | on invocation, whole |
| `references/rule-cards/` | the card-indexer agent (frontmatter), one audit sub-agent per card that applies to the target | every audit |
| `references/kb-card-specification.md` | the session | auditing or writing a knowledge-base card |
| `references/gotchas.md` | the session | when a skill misbehaves or the audit workflow fails |
| `scripts/static-audit.py` | the session | the static pre-pass of every audit |
| `scripts/audit-workflow.js` | the Workflow tool | every audit |
| `maintenance/README.md` | a maintainer | before changing a card, a script, a sub-agent prompt or an eval |
| `maintenance/rule-cards-provenance.md` | a maintainer | adding a card or re-verifying its source |
| `maintenance/rule-cards-taxonomy.md` | a maintainer | adding a card or a facet value |
| `maintenance/maintenance-map.md` | a maintainer, a reviewer | decoding an anchor token, flipping a volatile dependency |
| `evals/` | a maintainer | a model upgrade, an edit judged against eval results |
