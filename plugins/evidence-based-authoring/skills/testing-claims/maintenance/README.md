# Maintaining testing-claims

Nothing under `maintenance/` is read or executed in a run of the skill. Paths are relative to the skill directory; `../../agents/` is the plugin's agent directory.

- A rule of `references/method.md` changes together with its line in `maintenance/method-provenance.md`, its question in `../../agents/claim-skeptic.md`, its row in the applicability table of `references/record-format.md` and the summary of the method in the repository's `README.md` § Methodology.
- A field or a standing changes together with the tables of `references/record-format.md`, the vocabularies and the per-kind requirements of `scripts/check_record.py`, and the cases of `maintenance/tests/test_check_record.py`.
- The shape of the reader's verdict changes together with the JSON example of `references/record-format.md`, the section "What to return" of `../../agents/claim-skeptic.md`, `scripts/check_verdict.py` and `maintenance/tests/test_check_verdict.py`.
- A prescription added to `SKILL.md` that `references/method.md` does not carry gets its `S-n` line in `maintenance/method-provenance.md`.
- The skill's own rules pass through the skill: a new part of the method enters `maintenance/method-provenance.md` with its record, and a belief about the method that no test backs yet enters `maintenance/pending-evidence.md` as a hypothesis with its refuting outcome.
- A test of our own about the method keeps its protocol, its script and its draw under `evals/<name>/`. Its hypothesis is committed in `maintenance/pending-evidence.md` before a run, every run stays under `evals/<name>/runs/`, and the result enters the hypothesis line in a later commit.
- The unit tests run from the skill directory: `python3 -m unittest discover -s maintenance/tests -p 'test_*.py'`. They build their files under temporary directories and create their own git repositories there.
- `python3 -I scripts/check_record.py --root <repository> maintenance/method-provenance.md maintenance/pending-evidence.md --require` passes before a commit that touches either file.

## Layout

- `maintenance/method-provenance.md` — one line per part of the method, keyed `M-n`, and per prescription of `SKILL.md` outside the method, keyed `S-n`: the texts or rules the formulation follows, how each text was seen, and the record.
- `maintenance/pending-evidence.md` — the hypotheses about the method, keyed `H-n`, each with its measure and refuting outcome.
- `maintenance/tests/` — `test_check_record.py`, `test_check_verdict.py` and `test_kind_agreement.py`.

Who reads or runs every other file of the skill, and when: `README.md` § Layout.
