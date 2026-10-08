# Handover — the software-craft build

Read this first. It is the plan, the state and the runbook of the work that builds the `software-craft` skill and its three agents in this repository, written so that another session, in another account and another checkout, continues the work without re-running what is finished, including the sub-agent research runs that were in flight. Everything a continuation needs is in the repository on branch `claude/youthful-thompson-m7gj89`; nothing lives only in a session's container. `series/STATUS.md` is the live status table; this file is the stable part.

## 1. The commission

Build, from research, the skill `plugins/code-quality/skills/software-craft/` (a corpus of atomic, language-agnostic craft rule cards with a build-and-review orchestration) and the plugin agents `software-developer`, `craft-finder`, `craft-verifier`, on the pattern of `plugins/code-quality/skills/reviewing-java/`. The binding rules, which every continuation keeps:

- **Evidence.** Every card cites an openable admissible source: research with an arXiv id or DOI, a technical standard or official documentation by section, a static-analysis rule page, or hands-on evidence in an openable form (a fixture test, a public benchmark, a linked commit). A trade book, a blog or a talk is formulation or reception only: named in `references/craft-cards-provenance.md` and the topic's research note, never in a card. No traceable source, no card: the rule goes to `references/pending-evidence.md`. The repository's `CLAUDE.md` states the rule; the design note §Source policy states the fetch statuses (`fetched`, `relayed`, `unfetched`).
- **Quality Gate.** `/auditing-ai-context` runs on every SKILL.md and agent-prompt change before its commit (`CLAUDE.md`). Cards are no longer gated per topic (operator's decision of 2026-10-08, §5.7): a topic is committed after the validator and the spot-read, and the card audit runs once as the series' closing stage over a sample. Target types: `kb-card` for a card, `kb-corpus` for the cards directory, `agent-prompt` for an agent, `skill` for SKILL.md, `doc` for the design note and the references.
- **Text.** Present-design text everywhere: no history narration, no dates or ticket ids in shipped text, at most three ALL-CAPS markers per file, self-contained cards (no sibling ids, no deixis, no practitioner attribution, no language named in a Thesis).
- **Rules.** Language-agnostic, with Examples rotating over Java, Python, TypeScript, Go and Rust; one checkable claim per card; severities `major`, `minor`, `suggestion`; a contested rule ships only with a sourced separating condition; reserved specialties (low-latency tuning, concurrency correctness, security-critical design, ML and algorithm research) are named, not solved.
- **Card schema.** Frontmatter `title, rule_id, domain, step, applies_to, triggers, scope, check_kind, severity_default`; body `## Thesis → ## Rationale → ## Example → ## Limits → ## Validator → ## Finding output → ## Source`. `references/craft-cards-taxonomy.md` is the schema and the controlled vocabulary; `scripts/validate-craft-cards.py` enforces it.
- **Models.** Research: `claude-opus-5-5` at `xhigh` for sources, spine and drafts, `max` for the skeptic. Review: `mechanical` high, `semantic` xhigh, `verdict` max. Developer: opus at max. No stage runs on a Fable model.
- **Repository discipline.** Develop and push only on branch `claude/youthful-thompson-m7gj89`. Conventional Commits; stage files by name, never `git add -A`; push after every commit; never merge to `main`; never open a pull request. Everything in the repository is in English. The final report to the operator is in Russian.
- **Honesty.** State a file's contents only after opening it; name anything unverified as unverified, in the first person. Report failures with their output.

## 2. Where the specification lives

| What | Where |
|--|--|
| The design: layout, card schema, 48-topic taxonomy (groups A–J, ten domains), vocabulary, structural signals, contested rules, ownership and priority, pre-pass and workflow contracts, research workflow, source policy, evals, progress table, cost, deviations from the brief | `research/2026-09-26_software-craft-cards.md` |
| Corpus schema and vocabulary | `plugins/code-quality/skills/software-craft/references/craft-cards-taxonomy.md` |
| The skill's procedure (seven phases) | `plugins/code-quality/skills/software-craft/SKILL.md` |
| The three agents | `plugins/code-quality/agents/{software-developer,craft-finder,craft-verifier}.md` |
| Cards, provenance, pending rules | `references/craft-cards/`, `references/craft-cards-provenance.md`, `references/pending-evidence.md` |
| Research notes, one per topic, `status` in frontmatter | `research/software-craft/<slug>.md` |
| Scripts (pre-pass, bundling, workflows, writer, continuation, validator, renderer, tests) | `plugins/code-quality/skills/software-craft/scripts/` |
| Evals: fixture, expected triples, grader, recorded runs, pinned models | `plugins/code-quality/skills/software-craft/evals/` |
| Symptom → cause → fix | `references/gotchas.md` (G-16 search budget, G-18 continuation, G-19 concurrency) |
| This transient state | `research/software-craft/.state/` (removed at the close) |

## 3. The plan and its state

| Step | Gate | State |
|--|--|--|
| 1 Design note and taxonomy | audit clean | done |
| 2 Pilot: naming, error handling, test doubles | 36 cards, validator and audit clean, notes `verified` | done |
| 3 Scripts and agents | tests pass, agents audit clean | done |
| 4 Dry run: fixture, both pre-pass modes, grading, smoke task | 72/72, smoke task built and reviewed, `evals/evals.json` | done |
| 5 Series: 45 remaining topics, domain reviewers, corpus audit, fixture to three seeds per new domain | validator, audit and grading clean, every note `done`, provenance round-trip holds | paused by the operator: 23 topics part-way (groups A, B, C, D), their journals snapshotted under `journals/`; 22 not started (E, F, G, H, I, J) |
| 6 Close: SKILL.md, READMEs, maintenance, gotchas, report format, `overview.sh`, versions, final audit, final report | final audit clean | open; `overview.sh` done; the remaining documentation edits are held in `docs-pending.patch` |

Where the series stands (2026-10-08T15:45 UTC, wind-down on the operator's instruction): 37 of 48 topics are done and the corpus holds 331 cards (CODE 82, DSN 70, API 31, ERR 51, TST 51, CHG 37, PRF 6, with 3 cards' ids folded away; `validate-craft-cards.py` clean, 3 `[]`-trigger warnings by design). Domains complete: change (6 topics), code (7), design (9), errors (4), interface (3), tests (4). Running when this was written, each to be finished by whoever reads this (`series/batch4.json` holds task and workflow ids; a container restart or a usage cut ends them, and §5.3 rebuilds from the journals under `journals/`): profiling-and-code-tuning (verify2), algorithm-and-data-structure-choice (verify), build-warnings-static-analysis-ci and dependency-management (sources). Not started (7): runtime-configuration, internationalization-and-text-encoding, reading-and-understanding-code, code-review-as-author-and-reviewer, documentation-beyond-comments, parsing-and-grammar-based-input, security-hygiene-in-ordinary-code; their bundles are regenerated by `series/make-bundles.py` (§5.5) and launched one per free slot under the cap of four. The operator stopped new launches at 15:05 UTC ("finish the running workflows, launch no new ones"); the next session asks before launching the seven.

**What the next session does first.** (1) Read `series/STATUS.md`, `series/batch4.json` and `git log`; finish any topic whose run completed (§5.5: `finish-topic.sh <slug> outputs/<slug>.output.json.gz`, spot-read, commit; no per-topic audit, §5.7); if a run was cut, §5.3 with `--write-carded`. (2) Apply the change-domain reviewer's report `reviews/change.json` (saved 2026-10-08T15:40 UTC and applied in commits 00f6046 and c93af76; the description that follows records what was done, so the next reviewers' reports are applied the same way): its 20 `DEFER_TO` proposals go into `scripts/craft-review-workflow.js` and `references/maintenance.md` (an entry may list several owners: `'CHG-01': ['API-20', 'CHG-02', 'CHG-03']`); its three contradictions become Limits sentences on CODE-59, CHG-14 and CODE-22 with the source bullets copied from CHG-14, CHG-13 and CHG-07; its ten facet fixes are frontmatter edits; its trigger findings on CHG-25, CHG-29, CHG-30, CHG-35 and CHG-27 are fixed by adding declaration triggers (CHG-25), manifest triggers (CHG-29) and a Limits sentence naming what the finder can and cannot reach (CHG-29, CHG-30, CHG-35), by quoting the added line in CHG-35's Finding output, and by making CHG-27's bad Example an added file; its two gaps with a source (fix-up squashing: kubernetes/community pull-requests.md §Squashing; deliberate debt only for an emergency: google/eng-practices review/emergencies.md) are research runs to queue, never hand-written cards; the eleven other gaps are spine rules held as not checkable and need no entry. (3) Run the reviewer of §5.8 for the five other complete domains (code, design, errors, interface, tests), one at a time (one opus/max read-only agent each, about 0.6M tokens and 40 minutes for change), save each report under `reviews/<domain>.json`, apply as above. (4) When the last topic is in: the closing-stage card audit (§5.7, `series/audit-samples.json` lists the cards already sampled), the remaining domain reviewers, then the close (§6).

Fourth batch so far (fresh topics, one run each, no continuation):

| topic | cards | agents | sub-agent tokens (M) |
|--|--|--|--|
| code-smells-and-antipatterns | 6 | 34 | 4.2 |
| debugging | 6 | 34 | 3.9 |
| large-scale-changes-and-migrations | 9 | 47 | 5.6 |
| larger-tests-integration-and-end-to-end | 12 | 62 | 7.0 |
| property-based-testing | 12 | 63 | 7.2 |
| refactoring | 5 | 29 | 3.7 |
| seams-and-characterization-tests | 7 | 39 | 5.0 |
| small-steps-and-minimal-diffs | 6 | 34 | 3.8 |
| technical-debt | 6 | 34 | 4.0 |
| test-first-and-test-driven-development | 2 | 13 | 1.8 |
| unit-testing-and-test-quality | 12 | 64 | 7.7 |

Total: 83 cards, 453 agents, 53.9M sub-agent tokens; a topic takes 2 to 4.5 hours of wall-clock at two agents per workflow.

The earlier record follows. Where the series stands (2026-10-08T06:50 UTC): 26 topics are done (the 3 pilot topics and the 23 topics the pause left part-way, every one of them finished in the third round through the continuation bundles of `series/batch3.json` and committed after its audit sample); the corpus holds 249 cards; 4 not-started topics of group E run as the fourth batch (`series/batch4.json`, fresh bundles under `<scratch>/bundles/`); 18 remain not started: `refactoring`, `code-smells-and-antipatterns`, `seams-and-characterization-tests`, `large-scale-changes-and-migrations`, `small-steps-and-minimal-diffs`, `technical-debt` (F); `debugging`, `profiling-and-code-tuning`, `algorithm-and-data-structure-choice` (G); `build-warnings-static-analysis-ci`, `dependency-management`, `runtime-configuration`, `internationalization-and-text-encoding` (H); `reading-and-understanding-code`, `code-review-as-author-and-reviewer`, `documentation-beyond-comments` (I); `parsing-and-grammar-based-input`, `security-hygiene-in-ordinary-code` (J). Nine duplicates the writer produced across topics were folded by hand at the spot-read and six partial overlaps are tabled as deferring pairs (`references/maintenance.md`, `DEFER_TO`); a fresh topic's cards are checked against the corpus the same way before their audit. Update 2026-10-08T10:50 UTC: 31 topics done and 293 cards (test-first, refactoring, unit-testing, larger-tests and property-based-testing finished as fresh fourth-batch topics; TST-39 split from TST-18 at an audit); code-smells, seams, large-scale-changes and small-steps run; the card audit moved to the closing stage (§5.7).

The earlier pause, for the record: The pause: every running workflow was stopped at 2026-10-07T12:01 UTC on the operator's instruction, after a snapshot.3 in a new session or §5.4 in the session that launched them. Per-topic state is `series/STATUS.md` (regenerate with `series/series-status.py --snapshot`). The 48 topics: 3 done (pilot), 23 in flight with their journals snapshotted under `journals/`, 22 not started: `unit-testing-and-test-quality`, `test-first-and-test-driven-development`, `larger-tests-integration-and-end-to-end`, `property-based-testing` (E); `refactoring`, `code-smells-and-antipatterns`, `seams-and-characterization-tests`, `large-scale-changes-and-migrations`, `small-steps-and-minimal-diffs`, `technical-debt` (F); `debugging`, `profiling-and-code-tuning`, `algorithm-and-data-structure-choice` (G); `build-warnings-static-analysis-ci`, `dependency-management`, `runtime-configuration`, `internationalization-and-text-encoding` (H); `reading-and-understanding-code`, `code-review-as-author-and-reviewer`, `documentation-beyond-comments` (I); `parsing-and-grammar-based-input`, `security-hygiene-in-ordinary-code` (J). Their validated argument objects are `series/topics-*.json`.

## 4. Environment facts that shape the work

- **Fetch channel.** The egress policy denies arXiv, doi.org, publishers, vendor documentation sites and search engines; it admits GitHub-hosted content (`raw.githubusercontent.com`), `pkg.go.dev` and the WebSearch tool. Papers reach a card through GitHub-hosted copies or the orchestrator's relayed search snippets (`candidate_evidence` items marked "relayed by the orchestrator's search"). The channel note embedded in every series bundle lists the openable paper channels.
- **Search budget.** `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` is 200 per session for all sub-agents together, and it was spent before the pilot's source layer ran; the bundles tell the agents not to call WebSearch. A fresh session has a fresh budget: spend it from the orchestrator on paper abstracts for the not-started topics (the `topics-*.json` objects already carry relayed snippets) rather than letting sub-agents spend it on the first topic.
- **Concurrency.** The workflow runtime caps agents per workflow at `min(16, CPUs - 2)`, two on this four-CPU host; run many workflows at once. A workflow script above 512 KiB is refused: continuation bundles use `--split 3` or more.
- **Usage limit.** The account's usage window is five hours; two windows each absorbed about 35M sub-agent tokens in about 50 minutes with 23 topics running, then every live agent failed with "You've hit your session limit · resets HH:MM (UTC)". A workflow whose agents fail still ends "completed" with the finished agents' results in its journal; a continuation re-runs only the failed ones (§5.3, §5.4). At the measured rate the series needs roughly 11 more windows. The one cut the design admits without changing what ships: the skeptic's second verdict at `xhigh` instead of `max` (design note §Cost); the operator decides.
- **Agent types.** The plugin's agent types resolve only where the plugin is installed; in a checkout, every workflow agent is the runtime's default sub-agent with the same prompt and tiers, and the developer runs as a general-purpose agent carrying `agents/software-developer.md`'s body (design note deviation 3, `evals/evals.json`).
- **Cost profile of the card agents** (268 finished agents of batch 3, from their transcripts; `measure-agents.py` computes it; weight in Opus-price input equivalents, output undercounted by the transcripts). Drafter: 42 calls, 0.40M, 10 min. First skeptic (`max`): 58 calls, context 232k at the end, 0.65M, 18 min. Fix: 17 calls, 0.17M. Second skeptic (`max`): 55 calls, 0.62M, 18 min. Closing edit: 12 calls, 0.15M. Skeptics are about 80 percent of the weight and 60 percent of theirs is the re-read of a growing context on every call: of 11.8k skeptic Bash calls, 11 percent read the validator's source, 9 percent listed directories, 8 percent read sibling cards. The card prompts therefore carry a working-method block (scratch directory, batched reads, the validator run as one command, a provisional call budget: drafter 20, skeptic 25, fix 10). Measured on the third-round and later bundles (`measure-agents.py <their workflow ids>`, 232 finished agents against the 372 earlier ones): first skeptic 7.3 calls, context 162k, 0.22M, 16 min (was 56 calls, 229k, 0.64M, 18 min); second skeptic 7.2 calls, 0.22M (was 54, 0.63M); fix 4.9 calls, 0.09M (was 17, 0.17M); closing edit about 4 calls, 0.08M (was 11, 0.14M); drafter 10.5 calls, 0.11M, 6.5 min on the two drafts the rebuilt bundles ran (was 42 calls, 0.40M, 10 min; a small sample, since the rebuilt bundles carry most drafts from the journals). A card now costs about a third of its former weight, and the skeptics still fetch every cited source, test every trigger and run the validator (their verdicts record each check). A container restart stops every agent in flight (two restarts cost 17 cut agents, 1.7M); the journals survive it, and `--write-carded` plus a rebuilt bundle recover the finished work (§5.3). Agents cut by a usage limit or a stop are pure waste (169 cut agents, 34M), which is why the series runs four workflows at a time.
- **Resume semantics.** `Workflow({scriptPath, resumeFromRunId})` replays finished agents from the runtime's cache and is same-session only. Across sessions, `scripts/research-continue.py` rebuilds the state from the journal (§5.3).

## 5. Runbook

Paths below are relative to the repository root; `<K>` is `plugins/code-quality/skills/software-craft`, `<ST>` is `research/software-craft/.state`.

### 5.1 Set up

```
git fetch origin claude/youthful-thompson-m7gj89 && git checkout claude/youthful-thompson-m7gj89
./overview.sh
python3 -m unittest discover -s <K>/scripts/tests -q
python3 <K>/scripts/validate-craft-cards.py --provenance <K>/references/craft-cards-provenance.md --pending <K>/references/pending-evidence.md <K>/references/craft-cards
python3 <ST>/series/make-bundles.py --out-dir <scratch>/bundles <ST>/series/topics-*.json
```

The last line writes the 45 series bundles into a scratch directory outside the repository (they embed the absolute checkout path as `root`), one `<slug>.js` per topic, with the existing card titles of the topic's domain, the rotation by topic index, the channel note and `closing_edit: true`. Regenerate them whenever cards of a domain land, so a later topic of that domain sees the titles already shipped.

### 5.2 Orient

```
python3 <ST>/series/series-status.py            # reads batch*.json; live journals if this session has them, else journals/*.gz
cat <ST>/series/STATUS.md
```

A topic is in one of four states: not started (no row); in flight (journal has `done` agents, no finished output); run ended with failed agents (the usage limit; `cards` 0 or partial); run complete (every agent done, output holds the cards). A topic is finished for the series when its note under `research/software-craft/` says `status: done`.

### 5.3 Continue an in-flight topic in a new session

The journal snapshot `journals/<slug>.journal.jsonl.gz` holds every finished agent's result. Build continuation bundles from it and run them:

```
mkdir -p <scratch>/cont/<slug> && gunzip -c <ST>/journals/<slug>.journal.jsonl.gz > <scratch>/cont/<slug>/journal.jsonl
python3 <K>/scripts/research-continue.py \
  --journal <scratch>/cont/<slug>/journal.jsonl \
  --from-bundle <scratch>/bundles/<slug>.js \
  --round 1 --split 3 --out-dir <scratch>/cont/<slug> --root <repo root> \
  --write-output <scratch>/cont/<slug>/cutshort.json
Workflow({ scriptPath: "<scratch>/cont/<slug>/continue-<slug>-1of3.js" })   # and 2of3, 3of3, no args
```

`--from-bundle` takes the topic, `next_id`, `rotation_start`, `max_rules`, `channel_note` and `closing_edit` from the bundle; `--round 1` carries the sources, the spine, the cached drafts (`draft:`) and first verdicts (`verify:`) as `resume_state`, so a bundle drafts only the rules with no draft, verifies only the drafts with no verdict, then runs the fix, the second verdict and the closing edit for every rule it owns. `--write-output` writes the cut-short run's output (sources and spine, no cards) so the writer can merge it as the first run. When a finished output of the original run exists under `outputs/`, pass it with `--from-output` instead and it serves as the first run. Check after launch that each bundle starts live at a draft or a verdict and not at the sources (`series-status.py` or the journal's `started` lines): a run that starts at `sources:*` is replaying and must be stopped.

Record the new task ids in a batch file: a continuation batch (`series/batch3.json` is the shape) lists per topic a `runs` array of `{part, task, wf}`, one per bundle launched, and `series-status.py` prints one row per run and snapshots its journal and output as `journals/<slug>--<part>.journal.jsonl.gz` and `outputs/<slug>--<part>.output.json.gz`. Take a snapshot (`series-status.py --snapshot`) and commit it after every run ends, whatever ended it. Pace: `--split 2` keeps every bundle of the 23 in-flight topics under the script limit. The operator's cap is four workflows at a time (about eight agents in flight): an agent takes about twelve minutes and about 0.2M tokens, so four workflows run about 200 agents per five-hour window, which is about 80 percent of the window's quota with no usage-limit cut; 23 workflows at once spent the quota in an hour and lost the 50 agents in flight at the cut. A run a container restart stops keeps its journal: `research-continue.py --carded-journal <that journal> --write-carded <out.json>` writes the cards the journal already finished (closing edits and accepted fixes) as a task output that the writer merges and a rebuilt bundle leaves out with `--skip-carded`; `series/rebuild.sh` does this for every run of the topic that has a journal and no task output, and `queue.py add <slug> <r4-finish|r4-rest> <finish|rest> <rules>` queues the rebuilt bundle (the round directory follows the part). A run the limit or a stop cut short twice is rebuilt from every journal of the topic with `--skip-fixed` (a plain round-1 bundle leaves out the rules whose fix the journals hold) and `--skip-carded <output>` (every earlier output's cards are left out); the writer then merges the cut-short output and every bundle output of the topic.

### 5.4 Resume in the same session after a usage-limit stop

When the runtime that launched the run is still alive, `Workflow({scriptPath: <bundle>, resumeFromRunId: "<wf id>"})` replays the finished agents from the runtime cache and re-runs only the failed ones, for a run that ended "completed" with failed agents as much as for one that failed outright. After the launch, confirm from the journal that the live agents are the ones that failed (two per run) and nothing earlier re-runs. Then snapshot and commit.

### 5.5 Launch a not-started topic

`Workflow({ scriptPath: "<scratch>/bundles/<slug>.js" })` with no args; record `{"task", "wf"}` in a new `series/batchN.json` (the shape of `batch1.json`) and commit it. Batches of about ten to twenty topics; the usage window, not concurrency, sets the pace.

### 5.6 Finish a topic

When every run of a topic is complete (the task output's `result.cards` holds its cards, no failed agents):

```
python3 <ST>/series/series-status.py --snapshot
<ST>/series/finish-topic.sh <slug> <ST>/outputs/<slug>.output.json.gz [<continuation outputs> ...]
```

`finish-topic.sh` runs `scripts/write-topic-result.py --status done` over the runs (a cut-short output first, then the continuation bundles' outputs; the later run's card wins per rule key, ids are renumbered contiguously per domain from the cards already in the tree) and the validator. Open the note and spot-read the cards. Then the per-card audit sample (§5.7) and the commit:

```
git add research/software-craft/<slug>.md <K>/references/craft-cards/<prefix>-*.md <K>/references/craft-cards-provenance.md <K>/references/pending-evidence.md <ST>/journals/<slug>.journal.jsonl.gz <ST>/outputs/<slug>.output.json.gz <ST>/series/batchN.json <ST>/series/STATUS.md <ST>/series/status.json
git commit -m "feat(software-craft): <slug> — N cards, M pending entries"
git push -u origin claude/youthful-thompson-m7gj89
```

Regenerate the bundles of the topic's domain afterwards (§5.1) so their `existing_titles` carry the new cards.

### 5.7 Audit (Quality Gate)

The audit is the `/auditing-ai-context` skill (`plugins/evidence-based-authoring/skills/auditing-ai-context/SKILL.md`): it builds a discovery inventory per target, then runs its audit workflow (`scripts/audit-workflow.js`) with `targets` of `{path, target_type}` and one `invPath`. `<ST>/make-inventory.py --target-type <type> --tier <tier> --out <inventory.md> <target>` writes one target's inventory (a file); `<ST>/make-corpus-inventory.py <cards-dir> <out.md> "<new in this change>" "<validator warnings>"` writes the corpus directory's; concatenate the inventories of a run's targets into one file for `invPath`. Cost: about 1–1.6M sub-agent tokens for a targeted run (a few cards, one agent, SKILL.md), 8.7M for the full four-document audit. Pattern used so far: after each topic, the corpus directory as `kb-corpus` plus one new card per domain as `kb-card`; before the close, SKILL.md as `skill`, the three agents as `agent-prompt`, the design note and the references as `doc`. Known false positives: R-42 "backslash path" on a card's `triggers` line (G-10); D-05 and D-01 markers on quoted rule text. The research workflow's card prompts are an `agent-prompt` target too: `render-card-prompts.js` renders the four prompts with placeholders into one Markdown file (the ARGS JSON names `root` and a placeholder topic), `make-inventory.py --target-type agent-prompt --tier warm` builds the inventory, and the audit runs on haiku/sonnet (`modelByCheckKind`, about 3.5M). Dismissed there by design: R-42 on the absolute `root` path (an argument value, not prose), R-14/R-10/R-43 on the concatenation of four separate prompts, R-50 on thresholds the taxonomy states. A finding that names a documented schema delta of `craft-cards-taxonomy.md` is dismissed with the taxonomy as the justification.

**Closing stage (operator's decision of 2026-10-08, replacing the per-topic sample).** The card audit runs once, after the last topic, as a stage of its own: (1) the corpus directory as `kb-corpus` (two checks, cheap); (2) a `kb-card` sample of two cards from every topic that `series/audit-samples.json` does not list (the topics finished earlier had their two-card sample after each topic; the file records them), in runs of about ten cards each. Cost is linear in cards: about 1.6M sub-agent tokens per card (a run of 4 cards took 6.7M and 8 minutes; 2 cards 3.3M and 4 minutes), so about 60M for the 19 topics finished after the decision, or half that with one card per topic. Apply or dismiss as before: C-F3 Example length is dismissed under the taxonomy's Example-form deviation when the pair is fenced, in one of the five languages and at most ten lines; C-E2 → name the idea instead of the publication; C-C1 inside a quoted source → bracket gloss; C-B1 → narrow the Thesis to one claim and, when the clause has sources and a validator clause of its own, split it into a card of its own from the same fetched sources (TST-39 from TST-18 is the precedent), otherwise move it to `pending-evidence.md`; C-E3 → carry the source's numbers; C-D1 → lead Limits with the decision. Integrity: nothing in the corpus directory may change while a run is in flight (compare the run journal's birth time with the cards' mtimes, and `git status` the tracked cards), so run the stage when no topic is being written. Why the change: a per-topic run cost the same per card but serialised the series (no cards could be written while a run was in flight) and its yield had fallen to about one small fix per run; the closing stage fixes with the whole corpus in view. The spot-read stays per topic: duplicates are folded, partial overlaps become `DEFER_TO` pairs, and a contradiction between a new card and an existing one is settled by a carve-out edit with a source (TST-17/TST-32 and TST-24/TST-43 are the precedents).

### 5.8 Domain reviewers

When every topic of a domain is written (CODE: 8 topics; DSN: 9; API: 3; ERR: 5; TST: 5; CHG: 6; PRF: 3; TOOL: 4; DOC: 3; INP: 2), run the reviewer of `series/REVIEWER.md`: one read-only agent (opus, max; tools Read, Grep, Glob, Bash) per domain, the prompt with `<DOMAIN>`, `<PREFIX>`, `<TOPICS>` and `<skill-dir>` filled. Act on its JSON as the file's preamble says: `overlaps` become `DEFER_TO` entries in `scripts/craft-review-workflow.js` and the table in `references/maintenance.md`; `contradictions` and `facet_errors` become card edits reviewed one by one (then validator and audit); `gaps` are checked against `pending-evidence.md` and become a research run when a source is named, never a hand-written card; `trigger_errors` are fixed in the card's `triggers` and re-validated.

### 5.9 Fixture and grading

The fixture seeds one defect and one control per pilot card in three languages per domain (`evals/fixture/head/`, `evals/expected.json`; the generator of the pilot rows is `<ST>/pilot-expected-gen.py`). The design asks at least three seeds per domain: for each new domain (DSN, API, CHG, PRF, TOOL, DOC, INP) add three seeds and three controls on cards of that domain, in files of the fixture's languages, with `expected.json` rows. Grade:

```
dir=$(<K>/evals/fixture/make-fixture.sh)                      # committed mode; --worktree for the working-tree mode
python3 <K>/scripts/static-craft.py --cards-dir <K>/references/craft-cards --repo $dir --diff-ref HEAD~1..HEAD   # omit --diff-ref in worktree mode
python3 <K>/scripts/bundle-run.py --root $dir --plan $dir/craft/plan.json --intent <intent file> --stage find --part 1/6 --out $dir/craft/run-find-1.js   # one bundle per part, one Workflow each
python3 <K>/scripts/bundle-run.py --root $dir --plan $dir/craft/plan.json --intent <intent file> --stage aggregate --raw <find part outputs ...> --out $dir/craft/run-aggregate.js
python3 <K>/scripts/bundle-run.py --root $dir --plan $dir/craft/plan.json --intent <intent file> --stage verify --part 1/6 --findings $dir/craft/findings.json --out $dir/craft/run-verify-1.js
python3 <K>/scripts/merge-parts.py --stage verify --out $dir/craft/verdicts.json <verify part outputs ...>
python3 <K>/evals/grade.py --expected <K>/evals/expected.json --verdicts $dir/craft/verdicts.json --findings $dir/craft/findings.json
```

Record the run under `evals/runs/` and the figures in `evals/evals.json` (SKILL.md §Phase 5 and §Phase 7 describe the parts path once `docs-pending.patch` is applied).

### 5.10 Close (step 6)

1. `git apply <ST>/docs-pending.patch` (SKILL.md §Phase 5 parts path and tree, gotchas G-19, maintenance.md, the skill README's Bundle row, the design note's one-round decision for series topics); then the remaining edits: the skill README's counts and domain table, the repository `README.md` row for `/software-craft` next to `/reviewing-java` (and its Sources section), `plugins/code-quality/.claude-plugin/plugin.json` description (it names only the Java review today) and version `5.0.0 → 5.1.0`, the same version in `.claude-plugin/marketplace.json`, `references/report-format.md` if the report changed, the design note's progress rows 5 and 6 and its cost section with the series figures.
2. Fill `DEFER_TO` from the reviewers (§5.8); mark every research note `status: done`; confirm the provenance round-trip (every card has one provenance line, every line one card; `validate-craft-cards.py --provenance --pending`).
3. Audits: SKILL.md (`skill`), the three agents (`agent-prompt`), the corpus (`kb-corpus` plus the closing-stage card sample of §5.7: two cards from every topic `series/audit-samples.json` does not list), the design note and the references (`doc`).
4. Remove `research/software-craft/.state/` and any `tmp/` artifacts; final commit and push.
5. The final report to the operator, in Russian: paths and counts (cards per domain, pending entries, notes), the grading (fixture 72/72 plus the extended seeds), the smoke task, the cost (tokens and agents per stage and per topic; the series total), the deviations from the brief (the design note lists eight; add any new one), what is not done, and the open questions with a recommended answer each: raising `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`; re-verifying the `relayed` citations from an environment with arXiv access; the second verdict at `xhigh`; the `tst-04` slug.

## 6. What is held and why

- `docs-pending.patch`: documentation edits that await the Quality Gate audit; applied at the close. Regenerate it, if the base files move, from the edit script's pairs (the patch is a plain `git diff`).
- `index.json` and the `*.gz` files at the top of `.state/`: the pilot's journals and outputs, kept for re-verification; the pilot is written and committed.
- `series/REVIEWER.md`: the domain reviewer prompt. `series/PROMPT.md` and `series/exemplar-*.json`: the prompt and exemplars the topic-argument agents followed; `series/merge-seeds.py` merged the relayed paper seeds into the topic objects.

## 7. Open questions for the operator

1. Pace or cost: continue at `max` for the second verdict (about 10M tokens a topic, 11 more usage windows), or run it at `xhigh` for the 22 not-started topics (about 15 percent less; the verdict's findings at that effort are unmeasured).
2. Whether `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` can be raised for the authoring environment, which would let the evidence layer search papers directly.
3. Whether a later environment with arXiv access should re-verify every `relayed` citation and mark it `fetched`.
