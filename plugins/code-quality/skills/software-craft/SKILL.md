---
name: software-craft
description: Build code by the craft cards and review it against them, in any mainstream language (Java, Python, TypeScript, Go, Rust first-class). Trigger on "build", "implement", "extend", "refactor", "add tests" ("implement rate limiting with tests") — a developer agent designs the change into a brief, then builds the confirmed brief, and a card-dispatched craft review gates it — and on a standalone craft review of a diff ("review this change for craft", "check PR #42 against the craft rules"). Any git repository, zero config (optional .claude/software-craft/config.md tunes invariants and report paths); runs read-only git diff and gh pr view, a pre-pass matching rule cards to the diff, one Workflow with a finder per card and a skeptic per finding, one fix round, two reports under craft/. NOT for a Java-specific review; NOT for debugging as the primary task; NOT for the reserved specialties (low-latency or HFT tuning, concurrency correctness, security-critical design, ML or algorithm research); NOT for codebase search.
disallowed-tools: Edit, NotebookEdit
---

# Software Craft

You orchestrate a build and its craft review, or a craft review alone, and deliver verified findings. The rules live as atomic cards in `references/craft-cards/` — one language-agnostic checkable claim each, an openable source each. On a build run a developer agent is dispatched twice: first to design the change into the brief `craft/design.md` to the `design` cards, then, once the brief is confirmed, to implement it by the other cards — before each step it lists the cards for that step by facet and reads the ones whose titles apply. A deterministic pre-pass then matches each card's dispatch conditions — regular expressions against the added lines, or a structural signal it measures — against the agent's own working-tree diff and writes a dispatch plan; one Workflow runs a finder per (card by slice) plus a logic pass per slice, aggregates deterministically, and runs a skeptic per finding; confirmed findings go back to the developer once; a render script writes the two reports. Every finding cites concrete code from the diff — no anchor in the diff, no finding — and the skeptics exist to reject: the report carries only what survived refutation, the decision the design note `research/2026-09-26_software-craft-cards.md` at the repository root records.

Quick rules:

- One confirmation with the user: at the end of Design on a build run, where the scope summary with the build model and `craft/design.md` are shown together, and at the end of Scope on a review-only run; ask further questions only when every context source is empty or no base branch resolves.
- The developer agent edits only inside the write zone, plus `craft/design.md` on its design dispatch and where a fix round amends it; this skill edits nothing (`disallowed-tools`) and writes only the run's record under `craft/`, the review-run scripts (`static-craft.py`, `bundle-run.py`, `render-reports.py`) write only under `craft/`, plus the two reports at the config's `review_output` path when it is set, the authoring scripts run at authoring time only and never in a build or a review, and the finders and skeptics read. A tree that changed during the review beyond the developer's reported changes is a compromised review, so the integrity check in Follow-ups is mandatory.
- No version-control write by anyone: the developer agent stops before a commit, and so does this skill; the operator commits.
- The developer's dispatches run on the build model by the dispatch table in §Phase 1, and the build dispatch carries `craft/design.md`; no review workflow stage runs on Fable — a change built on Fable is then judged by another model — and the tier check refuses a model naming it at launch; the tiers and their models are in §Phase 6, Tiers (design note §Review workflow contracts).
- The plan is never retyped: `scripts/bundle-run.py` embeds it, and the Workflow call names `craft/run.js`.
- Before committing a card, an agent prompt or this file: `scripts/validate-craft-cards.py` on the corpus, then the audit (repository Quality Gate).

Phases: Scope → Context → Design → Build → Pre-pass → Workflow → Fix round → Follow-ups and report. A review-only run skips Design, Build and the Fix round.

Runtime layout under the target repository's `craft/` (or the config-set report path for the two reports):

```
craft/
|-- design.md                       # the design brief the developer writes in §Phase 3 and builds from in §Phase 4 (build runs)
|-- plan.json                       # pre-pass output: inventory with signals, card index, jobs, slices, candidates, project cards
|-- plan.log                        # every skip, merge, split and drop the pre-pass performed
|-- run.js                          # the workflow script with this run's arguments embedded (scripts/bundle-run.py)
|-- findings.json                   # aggregated findings after the find stage (the cross-session checkpoint)
|-- raw-<i>.json                    # the raw findings of find part i (a run in parts)
|-- verdicts.json                   # findings with verdicts (and rulings) after the verify stage
|-- build-report.md                 # the developer agent's report (build runs)
|-- craft-review-<task>.md          # deliverable 1
`-- craft-review-<task>-rejections.md   # deliverable 2
```

Paths below are relative to this skill's directory unless they start with `craft/` (the target repository) or `plugins/`.

---

## Phase 1: Scope

Goal: decide whether this is a build or a review, resolve the repository, the write zone or the diff and the build model, and show the scope summary before any agent is dispatched.

`$ARGUMENTS` is free-form text. Parse it by looking at what is there:

- **A task description** (imperative prose: "implement…", "add…", "refactor…", "scaffold…", "rename … across …") → a build run. An optional write zone is any path or glob the text names as the place to change ("in `src/billing/`", "touch only `pkg/auth`"); without one the zone is the files the task's subject lives in and their tests, and the summary says so.
- **A review target** → a review-only run: empty text reviews the current branch against the auto-detected base; a commit hash (7–40 hex chars) reviews `$commit~1..$commit`; a PR (`#123` or a GitHub PR URL) reviews `$baseRef...$headRef` via `gh pr view $N --json headRefName,baseRefName`; `--worktree` or "the working tree" reviews uncommitted changes; a directory path is a path filter.
- **A ticket id** (`PROJ-567`) beside either → the ticket for the design-doc lookup and the report title.

### Resolve the base branch

Try in order: `--base` from arguments → `base_branch` from the project config → `git symbolic-ref refs/remotes/origin/HEAD` (strip the prefix) → `main`, `master`, `develop` (local then remote). If none exists, ask which branch to diff against.

### Load the project config

`.claude/software-craft/config.md` in the repository root, when present: YAML frontmatter plus a Markdown body. Keys, all optional: `project_name`, `base_branch`, `branch_pattern`, `ticket_id_pattern`, `ticket_design_doc` (`{TICKET_ID}` substituted), `review_output` (report path, `{TICKET_ID}` substituted), `documentation` (a directory of architecture docs), `modules` (`[{name, paths: [..]}]`, the module boundaries the pre-pass slices by). The body is `project_context`; its numbered invariants — `N. **Title**: rule. Violation: consequence.` — become project cards, and full cards under `.claude/software-craft/cards/*.md` are indexed as written. A missing or malformed config is fine; everything works without it.

### Validate

1. Inside a git working tree (not bare) — otherwise stop: "Not a git working tree."
2. A review-only run: `git diff $diff_ref --name-only $path_filter` returns at least one path — otherwise: "No changes in this scope." A build run: the working tree is clean, or the user has named the dirty files as theirs to keep — the developer's diff must be separable from earlier edits.

### Build model

A build run names its build model, `fable` or `opus`, in the scope summary. The task text decides it when it names a model ("on fable", "on opus"). Otherwise `fable` when the task adds or changes a boundary — a module, a public interface, a service edge — a data flow across modules, a failure contract, concurrency, or an invariant `project_context` names; `opus` otherwise: logic behind an existing boundary, a test, a rename, a move. The developer's dispatches run on it by this table (design note §Design → Build contract); the review runs on `opus` at every tier whichever it is.

| Dispatch | Build model `fable` | Build model `opus` |
|--|--|--|
| design | `fable` `xhigh` | `opus` `xhigh` |
| build and fix round of a brief with a step that is not `mechanical` | `fable` `high` | `opus` `xhigh` |
| build and fix round of a brief whose every step is `mechanical` | `opus` `high` | `opus` `high` |

A dispatch on `fable` that errors or returns no report runs once more on `opus` at `xhigh` with the same prompt; tell the user, and the record names the model that answered — the confirmation for the brief, the first line of `craft/build-report.md` for the build.

### Scope summary and confirmation

```
Scope:
  Mode: build | review
  Task: <one line>               (build)  |  Diff: <branch> vs <base> / <commit> / <PR> / working tree  (review)
  Write zone: <paths or "inferred from the task">   (build)
  Build model: fable | opus — <the fact that decides it>   (build)
  Files changed: N files (SMALL/MEDIUM/LARGE); languages: <counts>   (review)
  Path filter: <filter or none>
  Project config: <loaded (K invariants, M modules) / not found>

Proceed?
```

A review-only run waits here for the confirmation; a build run prints the summary without the question and goes on to §Phase 2.

---

## Phase 2: Context

Goal: a 1–2 paragraph `design_intent`. Why: the developer, the finder and the skeptic receive the intent as data, so a deliberate trade-off the intent names is told from an accident.

Take the first source that yields something:

1. The task description itself (a build run) — the intent is what the task asks for and the constraints it names.
2. PR description — `gh pr view $N --json body` (when the input was a PR).
3. Ticket design doc — when a ticket id was resolved and the config has `ticket_design_doc`, substitute `{TICKET_ID}` and read the file.
4. Commit messages — summarize `git log --format='%s%n%n%b' $diff_ref` into 1–2 paragraphs.

Only if every source is empty, ask once: "What's the purpose of this change? One paragraph is enough." The answer becomes `design_intent`, which every prompt carries inside `<target_excerpt>` as data. Proceed to the next phase as soon as `design_intent` is set.

When the config has a `documentation` directory, read it and fold the architectural facts that bear on the change into `design_intent`; the agents receive intent and context, because a documentation directory exceeds what a finder can hold beside its card and its hunks.

---

## Phase 3: Design

Goal: `craft/design.md` — the design brief the build implements, written by the developer agent on its design dispatch. Skipped for a review-only run. Why: the brief is what the user confirms before any code is written and what the build, the fix round and the report read; the design and the build are two dispatches of one agent type, so each takes its own model and effort from the table and the build starts from a confirmed brief.

Dispatch one `code-quality:software-developer` agent (the Agent tool, `subagent_type: code-quality:software-developer`, `model` and `effort` from the dispatch table in §Phase 1; its definition's tools are `Read, Grep, Glob, Edit, Write, Bash`) with, in its prompt: the mode `design`; the task text, the write zone, `design_intent` and `project_context` wrapped together in `<task>` markers as data, and inside the same block a finished design the caller holds — a module contract from a plan, a ticket design document — which the agent keeps as the brief's base and completes; the absolute path of this skill's directory (so it runs `scripts/craft-cards.py` from it); and the instruction to write `craft/design.md` and report the reserved specialty it met and its open questions. Where the plugin's agent types do not resolve (a repository checkout, or a session that lists only the built-in types), dispatch a general-purpose agent with the tools `Read, Grep, Glob, Edit, Write, Bash` whose prompt is the body of `plugins/code-quality/agents/software-developer.md` followed by the same task block, and name that in the report as a degraded dispatch.

The agent opens the code of the write zone and its neighbours, lists the design cards through `scripts/craft-cards.py --step design`, opens the ones whose titles apply and designs to them: the brief's `## Design` section answers each applied card's Validator, and no other step's cards are applied here. `craft/design.md` has seven sections (design note §Design → Build contract), in this order, every one present (an empty one says "none"):

1. `## Task` — the task in one paragraph and the write zone as paths.
2. `## Stack` — build and test tooling, formatter and linter configuration, the naming, layout and error-handling idioms of the surrounding code, the existing test style; each as a fact read from a named file (`pyproject.toml`, `build.gradle`, a neighbouring test).
3. `## Design` — the solution: the modules and types to add or change by `path:Symbol`, each with its responsibility and boundary; the data flow; the invariants the change upholds; the chosen approach with the present-tense fact that decides it (a rejected option appears only as the subject of a fact that blocks it).
4. `## Failure paths` — every failure path the change meets and its decided outcome (raise which error, return which value, log what), one line each.
5. `## Tests` — the behaviours the tests demonstrate, by test location and name.
6. `## Steps` — the numbered steps of the build; each names its step kind (`implement`, `handle-errors`, `test`, `refactor`, `document`), the files it touches inside the write zone and the behaviour it adds or preserves. A step marked `mechanical` is an edit by example or a move by format that needs no judgement.
7. `## Out of scope` — reserved specialties the design meets and leaves to the operator; changes outside the write zone, stated as proposals.

After the agent returns, `git status --porcelain` in the repository root shows `craft/design.md` and nothing else new. Then show the scope summary of §Phase 1 with the text of `craft/design.md` and ask "Proceed?" once: this is the build run's one confirmation. Wait for it; an answer that names a model changes the build model for the dispatches that follow.

---

## Phase 4: Build

Goal: the change, implemented from `craft/design.md` by the cards, with its tests, inside the write zone. Skipped for a review-only run.

Dispatch one `code-quality:software-developer` agent (the Agent tool, `subagent_type: code-quality:software-developer`, `model` and `effort` from the dispatch table in §Phase 1 by the brief's `## Steps`; its tools as §Phase 3 states) with, in its prompt: the mode `build`; the task text, the write zone, `design_intent`, `project_context` and the full text of `craft/design.md` wrapped together in `<task>` markers as data; the absolute path of this skill's directory (so it runs `scripts/craft-cards.py` and `scripts/static-craft.py` from it); and the instruction to return its report in the shape its definition names. The brief is required: a build dispatch without one is a defect of this skill. Where the plugin's agent types do not resolve, dispatch a general-purpose agent as §Phase 3 does, with the same task block.

The developer reads the brief and verifies its `## Stack` against the tree, follows its `## Steps` as the plan, lists the cards for each step through `scripts/craft-cards.py --step <step>`, implements each failure path's outcome as `## Failure paths` states, adds and runs the tests `## Tests` names, runs the pre-pass on its own diff and applies the triggered cards' Validators to its own code, and reports what changed by `path:Symbol`, the cards it applied, what it verified and how, what it could not verify, its deviations from the brief with the fact that forced each, and its open questions. It adapts a name or a signature to the surrounding convention and keeps the boundary, the approach and the failure outcomes as the brief states them; a step it cannot do as written is an open question at that step. It launches no sub-agents (no version-control write, as §Quick rules states). Write its report to `craft/build-report.md` verbatim, under a first line naming the model and effort that produced it.

After the agent returns: `git status --porcelain` and `git diff --stat` in the repository root — the changed files are inside the write zone and match the report, with the run's own files under `craft/` expected; a commit, a stash or a branch the agent made is a compromised build (`references/gotchas.md`, G-17).

---

## Phase 5: Pre-pass

Goal: `craft/plan.json` — the whole dispatch decided without an LLM. Why: a script reads the diff, measures the structural signals and reads the card frontmatter deterministically, so the same diff yields the same plan, and the plan is the checkpoint a resumed session starts from.

```
python3 <skill-dir>/scripts/static-craft.py --cards-dir "<skill-dir>/references/craft-cards" \
  [--diff-ref "$diff_ref"] [--path-filter "$path_filter"] [--repo <repo-root>]
```

Without `--diff-ref` it reads the working tree against `HEAD` — staged, unstaged and untracked — which is the build run's diff; with one it reads `git diff -U0 $diff_ref`. It reads every card's frontmatter and the project config, and writes `craft/plan.json` and `craft/plan.log`, nothing else (the dependency rule is in §Phase 6, Script declarations). Exit status 2 means the diff holds no reviewable change. `plan.json` carries:

| Key | Content |
|--|--|
| `inventory` | `mode` (`committed` or `worktree`), `base_sha`, `head_sha` (or `worktree`), changed files with language, kind, group and hunks (added lines with head line numbers and the structural signals measured per hunk), file-level signals, `skipped` files with the deny-list reason, `size_class`, config path and state |
| `cards` | the index of the dispatched cards (every `rule_id` a job or a candidate names): `rule_id`, absolute `path`, `title`, `domain`, `step`, `applies_to`, `triggers`, `scope`, `check_kind`, `severity_default` |
| `jobs` | one per (card by slice): the card's `rule_id` and the files whose added lines matched its patterns or whose hunks carry its signal, each carrying the indices of its matching hunks and which patterns and signals matched; a card over 400 matching lines splits by module or directory; the total is capped at 96 with every merge and drop written to `plan.log` (both caps: design note §Pre-pass contract) |
| `slices` | three to eight file groups for the logic pass, by config `modules` else by directory prefix, test files sliced apart; fewer than three files means one slice per file |
| `candidates` | mechanical hits named outright (an empty handler, a boolean argument, commented-out code, a TODO marker, a null returned for a collection, a print call outside tests), tagged `needs_verification` |
| `project_cards` | the `PROJ-N` cards parsed from the config body, and the paths of full project cards |

The structural signals — `long_routine`, `deep_nesting`, `many_parameters`, `boolean_argument`, `empty_handler`, `magic_number`, `commented_out_code`, `todo_marker`, `duplicate_block`, `test_file`, `added_file` — are defined with their thresholds in the design note `research/2026-09-26_software-craft-cards.md` under "Structural signals"; a card names one as `signal:<name>` in its triggers.

Read `plan.log` and tell the user what was skipped, merged, split or dropped.

---

## Phase 6: Workflow

Goal: verified findings. Why: one finder per card and one adversarial skeptic per finding are the design's two decisions, recorded in the design note `research/2026-09-26_software-craft-cards.md` with the dry run that graded them.

Primary, the craft review workflow. Bundle the run, then call the Workflow tool on the bundle with no `args` (per the quick rules, the bundle carries the plan verbatim):

```
python3 <skill-dir>/scripts/bundle-run.py --root <absolute repo root> --plan craft/plan.json \
  --intent <file holding design_intent> --context <file holding the config.md body, or omitted> \
  [--stage all|find|aggregate|verify] [--part <i>/<n>] [--raw craft/raw-<i>.json ...] [--findings craft/findings.json] \
  [--tiers <json>] [--agent-types <json>] --out craft/run.js
Workflow({ scriptPath: "<absolute repo root>/craft/run.js" })
```

`craft/run.js` is `scripts/craft-review-workflow.js` with `const EMBEDDED_ARGS = {...}` inserted after its `meta` block: `root`, `stage` (`all`, or `find` then `verify` across sessions, with `aggregate` between them for a run in parts), `part` (`{ index, of }`, a run in parts), `raw` (stage `aggregate`), `plan`, `design_intent`, `project_context`, `findings` (stage `verify`), `tiers` (`{ mechanical: { model, effort }, semantic, verdict }`, defaults below) and `agentTypes` (`{ finder: "code-quality:craft-finder", verifier: "code-quality:craft-verifier" }`; omit where the plugin's types do not resolve). Explicit `args` on the call override the embedded object.

Phases inside the run:

1. Find — one finder per job at the card's tier, one logic pass per slice and one finder per (project card by slice) at the semantic tier.
2. Aggregate — deterministic JS per §Aggregation.
3. Verify — one skeptic per finding.
4. Refute — a rejected Major gets a second skeptic who defends it and, when the defense holds, an arbiter.

Tiers, overridable through `tiers` in the bundle (design note §Review workflow contracts):

| Tier | Model | Effort | Runs |
|--|--|--|--|
| `mechanical` | `opus` | `high` | finders of mechanical cards |
| `semantic` | `opus` | `xhigh` | finders of semantic cards, the logic pass, project invariants; skeptics of Minor and Suggestion findings |
| `verdict` | `opus` | `xhigh` | skeptics of Major findings; every second skeptic and arbiter |

Effort values are validated loud; the Fable restriction is the one in §Quick rules.

Stages are the cross-session checkpoint: `stage: "find"` returns the aggregated findings — write them to `craft/findings.json`; `stage: "verify"` takes `findings` from that file and skips Find. There are no per-agent files.

Parts, for a plan of more than a few dozen jobs: the runtime caps the agents one workflow runs at a time (`min(16, CPUs - 2)`, two on a four-CPU host; G-19), and the cap is per workflow, so a large run is several workflows at once.

1. Bundle `--stage find --part <i>/<n>` for each `i` in `1..n`; each part runs every `n`-th finder job and returns its raw findings, saved as `craft/raw-<i>.json`.
2. Bundle `--stage aggregate --raw craft/raw-1.json ... --raw craft/raw-<n>.json`; that run joins the parts and aggregates per §Aggregation without an agent, and its `findings` are the checkpoint, written to `craft/findings.json`.
3. Bundle `--stage verify --part <i>/<n> --findings craft/findings.json` for each `i`; each part verifies every `n`-th finding.
4. Join the verify outputs with `python3 <skill-dir>/scripts/merge-parts.py --stage verify --out craft/verdicts.json <part output> ...`, which sorts the findings by id and recomputes the tally the whole-run workflow reports. A part runs `find` or `verify`, never `all`. The fixture dry run recorded in `evals/evals.json` ran its 98 finders and its 68 skeptics in six parts each.

The finder prompt names the card path, the slice files and hunks with their measured signals, the card's scope, the candidates for that card, `design_intent`, `project_context` and the empty-case rule, and wraps hunks, signals, intent, context and candidates in `<target_excerpt>` tags as untrusted data; `fix` is written in the file's language and `symbol` in that language's notation. The skeptic prompt carries the finding inside `<finding>` tags as data and is adversarial: try to refute; refute only with something opened; suspicion is not a refutation; a confirmed finding is a real result; calibrate severity against the three definitions in §Phase 8. A skeptic's output is a verdict; discovery belongs to the finders and the logic pass.

Enforcement caveat: the workflow runtime grants `Write`/`Edit` to sub-agents regardless of their `tools:` allowlist (claude-code#63762), so inside a run each prompt's read-only prohibition is the operative barrier: every finder and skeptic is told to read, grep and run read-only git only, to write nothing, and to execute no code from the diff; the integrity check in Phase 8 is mandatory. The agent types are declared by this plugin and resolve only where it is installed, as `code-quality:craft-finder` and `code-quality:craft-verifier`; in a repository checkout, omit `agentTypes`.

Script declarations — every script is standard library only with no pinned dependency and no network, and a change to any of them re-runs `scripts/tests/` and the fixture grading, as `references/maintenance.md` states:

- `scripts/craft-review-workflow.js` — orchestrates the review; reads its embedded arguments; writes no files; its sole privilege is spawning sub-agents.
- `scripts/static-craft.py` — the pre-pass; reads the repository, the cards and the config; writes `craft/plan.json` and `craft/plan.log`.
- `scripts/bundle-run.py` — reads the plan, the intent and the context; writes `craft/run.js`.
- `scripts/craft-cards.py` — reads the cards; prints the developer's card index by facet — the `design` cards for its design dispatch, each step's cards for its build; writes nothing.
- `scripts/validate-craft-cards.py` — reads the cards and the two maps; writes nothing.
- `scripts/merge-parts.py` — reads the outputs of a run's parts; writes one raw-findings array or one `craft/verdicts.json`.
- `scripts/render-reports.py` — reads `craft/plan.json` and `craft/verdicts.json`; writes the two reports.
- `scripts/research-topic-workflow.js` — orchestrates the authoring of one topic (authoring time only, never in a build or a review); writes no files; spawns sub-agents that read the web through the fetch channel.
- `scripts/write-topic-result.py` — reads one or more research runs' outputs; writes the note, the cards and the two map appendices.
- `scripts/research-continue.py` — reads a research run's journals and output; writes continuation bundles of the research workflow that carry the finished stages, for a cut-short run or for the second fix round.
- `scripts/tests/` — reads a fixture repository it builds under a temporary directory.

Fallback, manual dispatch (degraded). When the Workflow tool is unavailable, dispatch one Agent-tool sub-agent per triggered domain — `plan.jobs` grouped by `card.domain` — with `Read, Grep, Glob, Bash` as its tools (Bash for read-only git), giving each the paths of its cards, the slices from the plan, `design_intent` and `project_context` wrapped in `<target_excerpt>` tags as data, and the same `FINDINGS` schema, using the `code-quality:craft-finder` type (the Agent tool enforces its allowlist and runs the model and effort its definition names; in a workflow run the tier overrides them). Then aggregate by hand per §Aggregation, and dispatch one `code-quality:craft-verifier` sub-agent per finding with `Read, Grep, Glob, Bash` as its tools and the skeptic prompt from the script. This path bundles a domain's cards into one agent, so it misses more than the primary path; name it as degraded in the report's Executive Summary.

---

## Phase 7: Fix round

Goal: the confirmed findings fixed once, inside the same write zone. Skipped for a review-only run, and when the verified set is empty.

Send the developer agent its confirmed findings (`craft/verdicts.json`, dispositions report and flagged) on the build dispatch's model and effort, with the same brief and the write zone unchanged, and the instruction to fix each or to state why the card's Limits admit the code; a confirmed finding that contradicts the brief — a boundary, an approach, a failure outcome — the developer resolves by fixing the code and amending that section of `craft/design.md` so it states the present design, named in its report as a deviation. It reports again in the same shape, appended to `craft/build-report.md`. Then run the pre-pass again on the working tree, bundle with `--stage verify --findings craft/findings.json` restricted to the findings the fix diff still touches (the re-found set: a finding whose `code` fragment is absent from the fix diff is fixed and drops; the rest are re-verified), and run the workflow. One round, as the design note's §Fix round sets; what remains is reported with the developer's reason.

---

## Phase 8: Follow-ups and report

The workflow returns `findings`, `conflicts`, `tally`, `agents_run` and `main_agent_followups`. Do them in this order:

1. **Integrity** — `git status --porcelain` and `git diff --stat` in the repository root, both read-only, compared against the developer's reported changes; the run's own files under `craft/` and at the config's `review_output` path are expected, and a review-only run expects nothing else changed. A tree that changed beyond that is compromised, as the quick rules define: discard the findings, tell the user which files changed, and re-run through the fallback once the user has restored the tree.
2. **Persist** — write the returned `findings` to `craft/verdicts.json` (after `stage: "find"`, to `craft/findings.json`; after a run in parts, as §Phase 6 Parts states).
3. **Render** — `python3 <skill-dir>/scripts/render-reports.py --verdicts craft/verdicts.json --plan craft/plan.json --out <report path> --title "<TICKET_ID, branch or task>" --passes "<one line: N card jobs, M logic slices, K project invariants; fallback if used>" [--built craft/build-report.md] [--fix-round "<F fixed, L left>"]`.

Severity, the scale finders start from and skeptics calibrate against:

| Severity | Definition |
|--|--|
| Major | a correctness or maintainability defect the card's evidence ties to failures or to measured cost |
| Minor | a clarity or design cost |
| Suggestion | style, naming, documentation |

Every finding carries its `rule_id` (`CODE-NN` code inside a function, `DSN-NN` module design, `API-NN` interfaces, `ERR-NN` errors and resilience, `TST-NN` tests, `CHG-NN` changing code, `PRF-NN` diagnostics and performance, `TOOL-NN` tools and hygiene, `DOC-NN` reading and documenting, `INP-NN` input and security hygiene, `PROJ-N` project invariant, `LOGIC` the logic pass), an ordinal (`ERR-03.1`), and a one-line source pointer taken from the card's `## Source`.

### The two documents

Document 1, the review report, is saved to the config's `review_output` (with `{TICKET_ID}` substituted) or `craft/craft-review-<task>.md`: an executive summary (diff ref and mode, size and languages, passes, finding counts by severity, verification tally, the fix round, a Fix before merge / Merge with fixes / Merge recommendation), the developer's report under "What was built" on a build run, the major findings in full (rule id with its one-line source, location, code, problem, suggested fix in the file's language, rationale), a table of minor findings and suggestions, and a section for findings an arbiter left `uncertain`. Document 2, the rejection report, sits beside it with the `-rejections` suffix: every finding rejected or downgraded, with the evidence the skeptic opened. `scripts/render-reports.py` writes both; their exact layout is `references/report-format.md`.

### Report to the user

Print the Executive Summary to the conversation with the paths of both documents, then: what was built (by `path:Symbol`), the findings fixed, the findings left with their reason, the developer's deviations from the brief and its open questions. With zero rejections, say "0 rejected" and still write the rejection report, which then holds only the summary. No commit: name the files the operator will commit.

---

## Aggregation

Deterministic; the definitions here are canonical and `scripts/craft-review-workflow.js` encodes them (`DEFER_TO`, `DOMAIN_PRIORITY`, `compatible`).

1. Drop exact duplicates — same `rule_id`, `file`, `symbol` and whitespace-normalized `code`.
2. Group by span — (`file`, `symbol`, normalized `code`).
3. Ownership — `DEFER_TO` maps a deferring `rule_id` to its owner(s); a finding drops when its owner also flagged the span. The pairs, found by the corpus reviewers where one concept is stated twice, are tabled in `references/maintenance.md` §Deferring pairs and encoded in `scripts/craft-review-workflow.js`; the manual fallback loads that table before this step.
4. Fold compatible fixes — two fixes are compatible when their whitespace-normalized code is equal or one contains the other. Within a group, compatible findings collapse into the one with the highest domain priority, then the highest severity; the others' rule ids go to `also`, their problem and rationale to `folded`, and the kept finding takes the highest severity among them.
5. Conflict — incompatible fixes on one span: `DOMAIN_PRIORITY` (design note §Concept ownership and priority) input (0) > errors = interface = project = logic (1) > design = architecture = tests = change (2) > performance (3) > code = docs = tooling (4); the highest wins, the losers' rule ids go to its `also` and their problem, rationale and fix to `superseded`; a tie at the top keeps both, marks them `conflict`, and lists them for the author.
6. Sort by severity (major, minor, suggestion), then file, then symbol; ids are `<rule_id>.<ordinal>` in that order.

The finder's dispatched card is authoritative for `rule_id`: a finding a finder tags with another id is retagged and the retag logged.

---

## Maintenance

Adding, removing or changing a card, a script, a prompt, a signal or a tier: `references/maintenance.md` names what changes together and what to re-run; a topic is re-researched or added through `scripts/research-topic-workflow.js` and `scripts/write-topic-result.py`.

## Gotchas

Read `references/gotchas.md` when a run misfires; each entry ties a failure of the build or the review to its cause and fix (G-01 … G-19; retired numbers stay vacant): shallow findings, a rejected control that reached the report, a workflow dying on its first agent, a card that never triggers, a signal that stays below threshold, a developer agent that edited outside its zone.
