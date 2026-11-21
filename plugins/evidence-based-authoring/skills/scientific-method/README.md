# scientific-method

Skill for Claude Code that takes a statement on its way to becoming a rule through the scientific method and leaves a record of what the rule rests on; paths in this file are relative to this directory. The method is `references/method.md`: four kinds of statement (decision, definition, norm, claim), seven standings of a claim (opinion, hypothesis, supported, law, leading, contested, refuted), seven rules with their check questions, and one acceptance path, with a path of its own for a claim about one event. The support of a claim is a test that could have refuted it: someone else's, opened or, for a peer-reviewed source, read by its abstract; our own, committed; for a claim about one event, a trace on record that tells it from its named rivals.

## Checks

```
python3 -I scripts/check_record.py --root <repo> [--require] [--stats] [FILE ...]
python3 -I scripts/check_record.py --root <repo> --changed [--base REV]
python3 -I scripts/check_record.py --root <repo> --staged
python3 -I scripts/check_verdict.py <verdict.json>
```

`check_record.py` exits 0 when no record breaks the form, 1 on a finding, 2 on unreadable input or a failed git command. With no file named it checks every file under the root whose name matches `*provenance*.md` or `pending-evidence*.md`. An id is unique among the rule lines of one directory, so each skill numbers its own rules. In plain mode a rule line without a record is counted, and it is a finding only under `--require`; `--changed` and `--staged` require a record on every added or changed rule line, so a repository adopts the records line by line as its rules change. `check_verdict.py` exits 0 when every applicable rule holds in the reader's answers, 1 otherwise, 2 on unreadable input. `references/record-format.md` lists the fields and every finding code.

## A claim of our own

A claim of our own enters through a test in the repository. Its hypothesis is committed first, with the measure, the comparison, the scope, the refuting outcome and the threshold; the result is committed after it. `check_record.py --staged` rejects a result whose hypothesis is absent from the base revision or stands there with a different prediction. The order is read from the ancestry of the commits, so it holds in a repository that sets its commit dates by hand, and a map that git reports as renamed is compared with its text under the earlier name, so it holds when a skill's directory moves.

## The reader

The plugin's agent `../../agents/claim-skeptic.md` reads one record without the context of the work behind it, opens the test files and the sources the record names, and answers the check questions of the seven rules as one JSON object. Its answers are a model's output, so `check_verdict.py` holds them to the shape and to the table that says which rule applies to which kind.

## Layout

- `SKILL.md` — the procedure; enters the conversation when the skill is invoked.
- `references/method.md` — the method; read at the start of a session of the skill, and by the reader.
- `references/record-format.md` — the fields of a record, the forms of a test, the finding codes and the shape of the reader's verdict; read when a record is written, and by the reader.
- `scripts/check_record.py`, `scripts/check_verdict.py` — the checks of §6 of `SKILL.md`.
- `maintenance/README.md` — what changes together.
- `maintenance/method-provenance.md` — one line per part of the method: the texts its formulation follows, and its record.
- `maintenance/pending-evidence.md` — the skill's list of hypotheses.
- `maintenance/tests/` — the unit tests of the scripts.
- `evals/kind-agreement/` — the first test of the method itself: its protocol, the script that draws a sample, builds the readers' brief and scores their agreement, the two draws, and every run.
