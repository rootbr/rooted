# reading-companion

Skill for Claude Code that helps a reader work through a book or other material; paths in this file are relative to this directory. It sets up a per-book workspace — classifies the book, recommends a reading mode, scaffolds a customized `CLAUDE.md` — and then runs as a companion that explains, translates and checks the reader's own reconstruction without substituting for it. The methodology behind every step is `references/reading-methodology.md`; the sources of each of its claims stand on the claim's line in `maintenance/reading-methodology-provenance.md`.

## Layout

This skill's instance of the repository `README.md` §Skill layout:

| Path | Who reads or runs it | When |
|--|--|--|
| `SKILL.md` | the session | on invocation, whole |
| `references/reading-methodology.md` | the session | classifying a book, choosing a mode, filling the workspace `CLAUDE.md`, running as companion |
| `references/kb-card-specification.md` | the session; `scripts/init-workspace.sh` copies it into the workspace | distilling notes into cards |
| `scripts/init-workspace.sh` | the session | scaffolding a new workspace |
| `assets/CLAUDE.template.md` | `scripts/init-workspace.sh`, then the session | scaffolding and filling the workspace `CLAUDE.md` |
| `assets/log.template.md` | `scripts/init-workspace.sh` | scaffolding the workspace's `notes/log.md` |
| `maintenance/README.md` | a maintainer | before changing a methodology claim, the card specification or the scaffold |
| `maintenance/reading-methodology-provenance.md` | a maintainer | adding a methodology claim or re-verifying its source |
