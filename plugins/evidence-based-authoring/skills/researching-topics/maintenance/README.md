# Maintenance of `researching-topics`

Nothing under `maintenance/` is read or executed in a run; this file is the maintainer's guide. The run set is `SKILL.md` alone, listed in the skill's `README.md` § Layout.

## What a rule rests on

Every rule of `SKILL.md` has one line in `maintenance/skill-provenance.md`, keyed by its section or by its gotcha id. The line states the rule, names the sources found for it and closes with a record in the format of `../../scientific-method/references/record-format.md`: a norm with the document opened, the owner's decision, or a claim with its test, result and bounds. A rule whose claim waits for its test is the owner's decision, and its claim stands in `maintenance/pending-evidence.md` as `H-<id of its line>` with the tests found so far.

A rule that is added or changed goes through `/scientific-method` first: its line and record are written, a claim with no test yet enters the list of hypotheses, and a record that claims support is read by the independent reader of that skill.

## Layout

- `maintenance/skill-provenance.md` — one line per rule of `SKILL.md`: the rule, its sources with locators, its record.
- `maintenance/pending-evidence.md` — the hypotheses the rules rest on, each with its measure, its refuting outcome and the tests found for it.
- `maintenance/citations.json` — the words and figures the two files quote from their sources, one entry per quote with its source; an entry whose source is a PDF names the conversion to text in its `note`.

## Checks before a commit

Run from the repository root:

- `python3 -I plugins/evidence-based-authoring/skills/scientific-method/scripts/check_record.py --root . --require plugins/evidence-based-authoring/skills/researching-topics/maintenance/skill-provenance.md plugins/evidence-based-authoring/skills/researching-topics/maintenance/pending-evidence.md` — every line carries a well-formed record.
- `python3 -I plugins/evidence-based-authoring/skills/scientific-method/maintenance/scripts/check_quotes.py --cache <dir> plugins/evidence-based-authoring/skills/researching-topics/maintenance/citations.json` — every quoted fragment stands in its source.
- `python3 check-skill-layout.py` — the run set names nothing under `maintenance/`.
- The audit of `AGENTS.md` § Quality Gate on a changed `SKILL.md`.
