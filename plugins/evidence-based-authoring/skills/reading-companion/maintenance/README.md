# Maintaining reading-companion

Nothing under `maintenance/` is read or executed in a run of the skill. Paths are relative to the skill directory.

## What changes together

- A methodology claim: its sentence in `references/reading-methodology.md` and its line in `maintenance/reading-methodology-provenance.md`, keyed by section and claim. The methodology carries the claim, its numbers and its evidence mark alone; the author, year and title behind it stand on the provenance line. The line closes with the record of what the claim rests on; a claim that waits for a test stands in `maintenance/pending-evidence.md` as the hypothesis the record names, and each quoted word or figure of the two files has its entry in `maintenance/citations.json`. A clause of `SKILL.md` that claims an effect has its line in the same map, keyed `SKILL.md` and the heading it stands under. A source a rule was drawn from stands in the hypothesis as the claim's origin, and a test is a result found or made after the claim was written.
- The KB card specification: `references/kb-card-specification.md` is a copy of `../auditing-ai-context/references/kb-card-specification.md`, which is the canonical file. Edit the canonical file and copy it over this one; rule f of the repository's `check-skill-layout.py` rejects a copy that differs. Its sources stand in `../auditing-ai-context/maintenance/skill-provenance.md`.
- The workspace scaffold: `scripts/init-workspace.sh`, the two templates under `assets/`, and the steps of `SKILL.md` that fill `CLAUDE.md` from the template.

## Checks before a commit

From the repository root:

```
python3 -I plugins/evidence-based-authoring/skills/scientific-method/scripts/check_record.py --root . --staged
python3 -I plugins/evidence-based-authoring/skills/scientific-method/maintenance/scripts/check_quotes.py --cache <dir> plugins/evidence-based-authoring/skills/reading-companion/maintenance/citations.json
```

The first checks the form of every record a commit adds or changes and that no recorded result is erased. The second fetches each cited source and says whether the quoted words stand in it; a source it could not fetch, behind a paywall or a bot check, is reported as `unfetched`.

## Layout

- `maintenance/reading-methodology-provenance.md` — one line per source reference behind a methodology claim, keyed by section, each closed by its record, then the grouped bibliography.
- `maintenance/pending-evidence.md` — the claims that wait for a test, each with its measure, the outcome that would refute it and the tests found so far.
- `maintenance/citations.json` — the words and figures the two files quote, each with its source.

Who reads or runs every other file of the skill, and when: `README.md` §Layout.
