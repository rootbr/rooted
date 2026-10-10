# Skill layout boundary — a run loads SKILL.md, references/, scripts/, agents/ and assets/; a maintainer reads maintenance/ and evals/

Decided by the operator on 2026-10-16 for every skill of `code-quality` and `evidence-based-authoring`. Paths are relative to the repository root unless they start with a skill-relative directory.

## Finding

A run reads whole files: `SKILL.md` enters the conversation at invocation, a skill listed in an agent's `skills:` is injected whole into that agent at startup, and a reference is read when an instruction names it. Before the change four leaks mixed the maintainer's material into what a run sees:

1. `references/` held, beside the cards and gotchas a run reads, the provenance maps — 5.6 MB (`craft-cards-provenance.md`), 0.7 MB (`craft-cards-python-provenance.md`), 0.5 MB (`review-cards-provenance.md`), 43 KB (`rule-cards-provenance.md`) — the taxonomies, the pending-evidence files and the maintenance guides; `scripts/` of software-craft held nine authoring scripts and the unit tests beside seven run scripts, and reviewing-java's held its validator and tests.
2. software-craft's `SKILL.md` (35 KB, about 9 000 tokens) declared the authoring scripts and carried a pre-commit rule for maintainers; reviewing-java's and auditing-ai-context's carried the same kind of maintainer text.
3. `plugins/code-quality/agents/software-developer.md` preloaded the whole software-craft `SKILL.md` through `skills:` on each of its two dispatches, although the dispatch prompt passes the skill's absolute directory and the agent body carries its own rules.
4. A marketplace install copies the plugin directory whole, so a directory name alone excludes nothing.

## Platform facts

The operator read the Claude Code documentation on 2026-10-16 — [skills](https://code.claude.com/docs/en/skills), [sub-agents](https://code.claude.com/docs/en/sub-agents), [plugin components](https://code.claude.com/docs/en/plugins/components), [plugin evals](https://code.claude.com/docs/en/plugin-evals), [plugin loading](https://code.claude.com/docs/en/plugins/loading) — and records from it:

- only `SKILL.md` loads on invocation; supporting files load on demand;
- `skills:` in an agent definition injects the full skill content;
- no subdirectory name inside a skill is reserved beyond the `scripts/` convention;
- the skill-creator eval format lives at `<skill>/evals/evals.json`;
- a marketplace install copies the plugin directory whole, with no exclusion mechanism.

## Decision

1. Every skill separates its run set — `SKILL.md`, `references/`, `scripts/`, `agents/`, `assets/`, and the plugin-level `agents/` — from its maintainer set, `maintenance/` and `evals/`, by directory. No run-set file names a path under either; `SKILL.md` carries one pointer line to `maintenance/README.md`.
2. software-craft and reviewing-java move their provenance maps, taxonomies, pending-evidence files, maintenance guides (as `maintenance/README.md`), authoring scripts (`maintenance/scripts/`) and every test (`maintenance/tests/`, one runner) out of the run set; reviewing-java's `java-invariants-review-checklist.md` moves too, since no run file names it.
3. auditing-ai-context moves its provenance map, taxonomy and `maintenance-map.md`, and its `SKILL.md` §Maintenance bullets become `maintenance/README.md`.
4. `cardlib.provenance_map_path` is the one place that knows a provenance map's address, `<skill>/maintenance/<corpus>-provenance.md`.
5. reading-companion's copy of `kb-card-specification.md` is kept byte-identical to the audit skill's canonical file.
6. The developer agent loses its `skills:` preload.
7. `check-skill-layout.py` enforces the layout, with tests under `tests/`; the repository Quality Gate runs it before a commit that touches `plugins/`; `overview.sh` prints a `Maintenance:` line per skill.
8. The root `README.md` §Skill layout states the convention once; each skill README's §Layout table is its instance.
9. code-quality 7.3.0, evidence-based-authoring 4.11.0.

`maintenance/` stays inside the skill because the provenance maps must travel with the cards: `scripts/craft-cards.py --provenance` prints a card's line and `scripts/render-reports.py` takes a finding's source pointer from it, so a map outside the plugin would break both on an installed copy. `evals/` stays where it is because the skill-creator eval format expects `<skill>/evals/evals.json`.

## Result

What moved, per skill (the cards are untouched):

| Skill | To `maintenance/` | To `maintenance/scripts/` | To `maintenance/tests/` |
|--|--|--|--|
| software-craft | `craft-cards-provenance.md`, `craft-cards-python-provenance.md`, `craft-cards-taxonomy.md`, `pending-evidence.md`, `pending-evidence-python.md`; `references/maintenance.md` → `README.md` | `research-topic-workflow.js`, `python-topic-workflow.js`, `python-triage-workflow.js`, `harvest-python-sources.py`, `python-corpus.py`, `research-continue.py`, `write-topic-result.py`, `check-python-cards.py`, `validate-craft-cards.py` | 9 test modules |
| reviewing-java | `review-cards-provenance.md`, `review-cards-taxonomy.md`, `pending-evidence.md`, `java-invariants-review-checklist.md`; `references/maintenance.md` → `README.md` | `validate-review-cards.py` | 4 test modules |
| auditing-ai-context | `rule-cards-provenance.md`, `rule-cards-taxonomy.md`, `maintenance-map.md`; `SKILL.md` §Maintenance (10 bullets) → `README.md` | — | — |

software-craft's gotchas G-10, G-16 and G-18 moved with their ids to its `maintenance/README.md` §Authoring gotchas, and the authoring script declarations, with summary, inputs, outputs and privileges, to its §Scripts. `SKILL.md` sizes: software-craft 35 496 → 34 179 bytes, reviewing-java 20 273 → 19 770, auditing-ai-context 32 925 → 30 467. auditing-ai-context gained a `README.md`.

Changes the move required beyond the decision's list:

- The validators take the provenance map from `cardlib.provenance_map_path` when `--provenance` is absent and the map exists, so `validate-craft-cards.py <cards-dir>` checks one provenance line per card.
- `research-continue.py` resolves its default `--root` six directories above its new location, the repository root; from `scripts/` it had resolved four above, `plugins/`.
- `overview.sh` counts every `references/*-cards*` directory as a corpus, so the Python corpus prints as one line.
- The four audit cards D-02, D-03, D-04 and D-06 cite their eval seeds by file name (`seed7_old_name.ts` "of the audit skill's eval suite"); the seeds' paths stay on the cards' provenance lines. The check therefore carries no exemption list: the first version of the check had one for these four cards, and the session replaced it by the bare names, the simpler design with the same safety.
- `java-invariants-review-checklist.md` is the guide to writing a project's `config.md` invariants; the cards' origin checklists are the per-domain checklists the provenance map's header names in git history.

Checks, all run with outbound traffic sent to a closed proxy port:

| Command | Result |
|--|--|
| `python3 -m unittest discover -s maintenance/tests -p 'test_*.py'` in software-craft | 152 tests OK |
| the same in reviewing-java | 29 tests OK |
| `python3 -m unittest discover -s tests -p 'test_*.py'` at the root | 18 tests OK (19 before the exemption test was removed with the exemption) |
| `python3 check-skill-layout.py` | exit 0; `--table` prints the eight skills |
| `maintenance/scripts/validate-craft-cards.py references/craft-cards` | 520 cards, 0 errors, 4 warnings |
| the same with `--language python` on `references/craft-cards-python` | 178 cards, 0 errors |
| `maintenance/scripts/validate-review-cards.py references/review-cards` | 240 cards, 0 errors, 1 warning |
| `scripts/craft-cards.py --cards-dir references/craft-cards --provenance API-22` | prints the API-22 line |
| `node --check` on the five workflow scripts | passes |
| `python3 -m py_compile` on the 27 moved or touched Python files | passes |
| `cmp` of the two `kb-card-specification.md` copies | silent |

The grep for the former paths finds them only in dated notes under `research/`.

Two more skills turned out to hold a maintainer document under `references/`: the validation protocols of discovering-subtopics (named by no run file) and appraising-research (named by one pointer sentence of its SKILL.md) — the eval corpus, the metrics, the iteration loop and the gate before a commit. Each became that skill's `maintenance/README.md`, each skill received a `README.md` with its layout table, and the pointer sentence in appraising-research's SKILL.md names `maintenance/README.md`. The eval-corpus table of discovering-subtopics had named six reviewer checklists deleted in commit `fbd78b5` and the invariants checklist at its former path; it now names the review-card corpus by domain prefix and the checklist under reviewing-java's `maintenance/`. Three untracked directories holding only `.DS_Store` — `reviewing-java/agents/`, which made `overview.sh` list a phantom agent, `cleaning-code/` and `engineering-ai-requirements/` — were deleted from disk; the ignored `*-workspace/` directories of skill-creator runs stay.

## R-43 pass

The two gate audits of the day (the Source-footer change and this one) flagged 18 distinct R-43 pairs — a prescription stated in two sections — in the SKILL.md files of software-craft, reviewing-java and appraising-research and in the developer agent, none of them created by either change. The operator asked for the right treatment on 2026-10-16, and it is of three kinds:

- Eleven are a fact stated twice — a checkpoint path, a script constraint, the review model, a restart rule, the brief rule of the developer agent — and the second copy became a reference to the owning section (the Stages and Parts paragraphs, the script declarations, the tiers table, §Phase 0, the agent's quick rules).
- Six are not duplicates: five are a block that declares itself a summary of the file's own sections — the "Quick rules" list of a skill and the dispatch overview of the audit skill, whose owner is the detailed section — and one is a script declaration R-82 requires. Both limits are now in R-43's Limits and on its provenance line, so a gate does not raise them again.
- One pair looked risky to cut: the Enforcement caveat of software-craft repeated the `agentTypes` rule. The bundle paragraph owns it ("omit where the plugin's types do not resolve"), so the caveat's copy went and the owner stayed.

The gate on this pass found two more things in the touched text and they were fixed before the commit: the developer agent's step 2 called a step that cannot be done as written an "open question" while its quick rule called the same case a "deviation" (R-70); step 2 now states the merged rule — the nearest way that keeps the brief's decisions is taken and reported as a deviation (report item 5), and only a step no way keeps stays undone as an open question (item 7). The R-43 card's own Example was seven lines of prompt-authoring jargon against its corpus's C-F3; it is now a two-line everyday pair (a packing list and a reminder that points to it). The fifteen further pairs that gate listed sit in text no pass of the day touched; `tmp/audit-r43-summary.md` records them, with the observation that the semantic R-43 check returns a different subset of a long file's pairs on each run (6, 4 and 3 pairs in software-craft's SKILL.md across the three gates, one line in common), so the backlog is a matter for one full-file sweep whose first pass — the card's mechanical near-duplicate inventory — runs as a script.
