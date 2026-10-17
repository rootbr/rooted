# Maintaining reading-companion

Nothing under `maintenance/` is read or executed in a run of the skill. Paths are relative to the skill directory.

## What changes together

- A methodology claim: its sentence in `references/reading-methodology.md` and its line in `maintenance/reading-methodology-provenance.md`, keyed by section and claim. The methodology carries the claim, its numbers and its evidence mark alone; the author, year and title behind it stand on the provenance line.
- The KB card specification: `references/kb-card-specification.md` is a copy of `../auditing-ai-context/references/kb-card-specification.md`, which is the canonical file. Edit the canonical file and copy it over this one; rule f of the repository's `check-skill-layout.py` rejects a copy that differs. Its sources stand in `../auditing-ai-context/maintenance/skill-provenance.md`.
- The workspace scaffold: `scripts/init-workspace.sh`, the two templates under `assets/`, and the steps of `SKILL.md` that fill `CLAUDE.md` from the template.

## Layout

- `maintenance/reading-methodology-provenance.md` — one line per source reference behind a methodology claim, keyed by section, then the grouped bibliography.

Who reads or runs every other file of the skill, and when: `README.md` §Layout.
