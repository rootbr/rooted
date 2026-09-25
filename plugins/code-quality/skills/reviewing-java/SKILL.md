---
name: reviewing-java
description: Java code review — branches, PRs, diffs. Trigger on "review this branch", "find bugs", "what's wrong with this PR", "audit changes", "check diff", "review these Java changes", or any request to review Java code against project invariants. Any Java git repo, zero config required (optional .claude/reviewing-java/config.md tunes invariants and report paths); runs read-only git diff and gh pr view commands, a deterministic pre-pass that matches atomic rule cards against the diff, one Workflow that dispatches a finder per triggered card and a skeptic per finding, and writes two reports under review/ or the config-set report path. NOT for reviewing Python / JavaScript / Kotlin / Go / other non-Java code; NOT for writing new code or implementing features; NOT for searching the codebase (use Grep / Glob).
disallowed-tools: Edit, NotebookEdit
---

# Java Reviewer

You orchestrate a Java code review and deliver verified findings. The rules live as atomic cards in `references/review-cards/` — one checkable claim each, an openable source each; a deterministic pre-pass selects the cards a diff triggers and writes a dispatch plan; one Workflow runs a finder per (card by slice) plus a logic pass per slice, aggregates deterministically, and runs a skeptic per finding; a render script writes the two reports. Every finding cites concrete code from the diff — no anchor in the diff, no finding — and the skeptics exist to reject: the report carries only what survived refutation, the decision the design note under `research/` at the repository root records.

Quick rules:

- One confirmation with the user, at the end of Scope; no other question unless every context source is empty.
- Read-only on the repository: the scripts write only under `review/` and the finders and skeptics read; a tree that changed during the run is a compromised review, so the integrity check in Follow-ups is mandatory.
- No stage runs on Fable; the tiers are `claude-opus-5-5` at `high`, `xhigh` and `max`.
- The plan is never retyped: `scripts/bundle-run.py` embeds it, and the Workflow call names `review/run.js`.
- Before committing a card, an agent prompt or this file: `scripts/validate-review-cards.py` on the corpus, then the audit (repository Quality Gate).

Phases: Scope → Context → Pre-pass → Workflow → Follow-ups → Report.

Runtime layout under the target repository's `review/` (or the config-set report path for the two reports):

```
review/
├── plan.json                       # pre-pass output: inventory, card index, jobs, slices, candidates, project cards
├── plan.log                        # every merge, split, drop and skip the pre-pass performed
├── run.js                          # the workflow script with this run's arguments embedded (scripts/bundle-run.py)
├── findings.json                   # aggregated findings after the find stage (the cross-session checkpoint)
├── verdicts.json                   # findings with verdicts (and rulings) after the verify stage
├── java-review-<branch>.md         # deliverable 1
└── java-review-<branch>-rejections.md   # deliverable 2
```

Paths below are relative to this skill's directory unless they start with `review/` (the target repository) or `plugins/`.

---

## Phase 1: Scope

Goal: resolve the diff range, path filter and size; confirm with the user before spending anything.

`$ARGUMENTS` is free-form text. Parse it by looking at what is there:

- **Empty** → review the current branch against the auto-detected base
- **Ticket ID** (`PROJ-567` — uppercase letters, dash, digits) → use the current branch, note the ticket for the design-doc lookup
- **Commit hash** (7–40 hex chars) → review that single commit: `$commit~1..$commit`
- **PR** (`#123` or a GitHub PR URL) → `gh pr view $N --json headRefName,baseRefName` and use `$baseRef...$headRef`
- **Directory path** (existing directory) → path filter limiting the review to that subtree

These combine freely. If anything is unclear, ask.

### Resolve the base branch

Try in order: `--base` from arguments → `base_branch` from the project config → `git symbolic-ref refs/remotes/origin/HEAD` (strip the prefix) → `main`, `master`, `develop` (local then remote). If none exists, ask which branch to diff against.

### Build the diff ref

- Branch review (default): `$base_branch...HEAD`
- Single commit: `$commit~1..$commit`
- PR: `$baseRef...$headRef`

### Load the project config

`.claude/reviewing-java/config.md` in the repository root, when present: YAML frontmatter plus a Markdown body. Keys, all optional: `project_name`, `base_branch`, `branch_pattern`, `ticket_id_pattern`, `ticket_design_doc` (`{TICKET_ID}` substituted), `review_output` (report path, `{TICKET_ID}` substituted), `documentation` (a directory of architecture docs), `modules` (`[{name, packages: [..]}]`, the module boundaries the pre-pass slices by). The body is `project_context`; its numbered invariants — `N. **Title**: rule. Violation: consequence.` — become project cards, and full cards under `.claude/reviewing-java/cards/*.md` are indexed as written. A missing or malformed config is fine; everything works without it.

### Validate

1. Inside a git working tree (not bare) — otherwise stop: "Not a git working tree."
2. At least one Java build file (`pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle`, `settings.gradle.kts`) or a tracked `*.java` file — otherwise: "No Java sources or build files detected."
3. `git diff $diff_ref --name-only -- '*.java' $path_filter` returns at least one path — otherwise: "No Java changes in this scope."

Count the changed files: 1–19 is SMALL, 20–49 MEDIUM, 50+ LARGE.

### Show the scope summary and confirm

```
Scope:
  Branch: <branch> vs <base>
  Files changed: N Java files (SMALL/MEDIUM/LARGE)
  Packages: <top packages with counts>
  Path filter: <filter or none>
  Project config: <loaded (K invariants) / not found>

Proceed?
```

Wait for confirmation.

---

## Phase 2: Context

Goal: a 1–2 paragraph `design_intent`. Why: the finder and the skeptic receive the intent as data, so a deliberate trade-off the intent names is told from an accident (a design decision, recorded in the design note).

Take the first source that yields something:

1. PR description — `gh pr view $N --json body` (when the input was a PR)
2. Ticket design doc — when a ticket id was resolved and the config has `ticket_design_doc`, substitute `{TICKET_ID}` and read the file
3. Commit messages — summarize `git log --format='%s%n%n%b' $diff_ref -- '*.java'` into 1–2 paragraphs

Only if all three are empty, ask once: "What's the purpose of this change? One paragraph is enough." The answer becomes `design_intent`, which every prompt carries inside `<target_excerpt>` as data. No confirmation of the context.

When the config has a `documentation` directory, read it and fold the architectural facts that bear on the diff into `design_intent`; the finders see intent and context, not the docs.

---

## Phase 3: Pre-pass

Goal: `review/plan.json` — the whole dispatch decided without an LLM. Why: a script reads the diff and the card frontmatter deterministically, so the same diff yields the same plan, and the plan is the checkpoint a resumed session starts from.

```
python3 <skill-dir>/scripts/static-review.py \
  --diff-ref "$diff_ref" --cards-dir "<skill-dir>/references/review-cards" \
  [--path-filter "$path_filter"] [--repo <repo-root>] [--meta]
```

It reads `git diff -U0 $diff_ref -- '*.java' [path_filter]`, every card's frontmatter and the project config, and writes `review/plan.json` and `review/plan.log`, nothing else; standard library only, no network. Exit status 2 means the diff holds no Java change. `plan.json` carries:

| Key | Content |
|--|--|
| `inventory` | `base_sha`, `head_sha`, `diff_ref` pinned to SHAs, changed files with package, group and hunks (added lines with HEAD line numbers), `size_class`, build files, config path and whether the diff changed it, and — when the `META-` cards run — the config's own hunks as `config_file` |
| `cards` | the index of the dispatched cards (every `rule_id` a job or a candidate names): `rule_id`, absolute `path`, `domain`, `triggers`, `scope`, `check_kind`, `severity_default`, `title` |
| `jobs` | one per (card by slice): the card's `rule_id` and the files whose added lines matched its triggers, each carrying the indices of its matching hunks in the inventory record, so no hunk text repeats; a card over 400 matching lines splits by module or package prefix; the total is capped at 96 with every merge and drop written to `plan.log` |
| `slices` | three to eight file groups for the logic pass, by config `modules` else by package prefix; fewer than three files means one slice per file |
| `candidates` | mechanical hits named outright (`Pattern.compile(` in a method body, `new SimpleDateFormat(`, `Runtime.getRuntime().exec(`, weak `MessageDigest`, Jackson default typing, `new Random(` near a secret word, a synchronized wrapper on a concurrent map, `printStackTrace()`, an empty catch), tagged `needs_verification` |
| `project_cards` | the `PROJ-N` cards parsed from the config body, and the paths of full project cards |
| `meta_run` | whether the `META-` cards run: the diff changed `config.md`, or `--meta` was passed |

Read `plan.log` and tell the user what was merged, split, dropped or skipped.

---

## Phase 4: Workflow

Goal: verified findings. Why: one finder per card and one adversarial skeptic per finding are the design's two decisions, recorded in the design note with the pilot and extended dry runs that graded them.

Primary, the review workflow. Bundle the run, then call the Workflow tool on the bundle with no `args` (per the quick rules, the bundle carries the plan verbatim):

```
python3 <skill-dir>/scripts/bundle-run.py --root <absolute repo root> --plan review/plan.json \
  --intent <file holding design_intent> --context <file holding the config.md body, or omitted> \
  [--stage all|find|verify] [--findings review/findings.json] [--tiers <json>] [--agent-types <json>] --out review/run.js
Workflow({ scriptPath: "<absolute repo root>/review/run.js" })
```

`review/run.js` is `scripts/review-workflow.js` with `const EMBEDDED_ARGS = {...}` inserted after its `meta` block: `root`, `stage` (`all`, or `find` then `verify` across sessions), `plan`, `design_intent`, `project_context`, `findings` (stage `verify`), `tiers` (`{ mechanical: { model, effort }, semantic, verdict }`, defaults below) and `agentTypes` (`{ finder: "code-quality:review-finder", verifier: "code-quality:review-verifier" }`; omit where the plugin's types do not resolve). Explicit `args` on the call override the embedded object.

Phases inside the run: **Find** — one finder per job at the card's tier, one logic pass per slice and one finder per (project card by slice) at the semantic tier; **Aggregate** — deterministic JS per §Aggregation; **Verify** — one skeptic per finding; **Refute** — a rejected Critical or Major gets a second skeptic who defends it and, when the defense holds, an arbiter. Tiers, overridable through `tiers` in the bundle:

| Tier | Model | Effort | Runs |
|--|--|--|--|
| `mechanical` | `claude-opus-5-5` | `high` | finders of mechanical cards |
| `semantic` | `claude-opus-5-5` | `xhigh` | finders of semantic cards, the logic pass, project invariants; skeptics of Minor and Suggestion findings |
| `verdict` | `claude-opus-5-5` | `max` | skeptics of Critical and Major findings; every second skeptic and arbiter |

Effort values are validated loud; a model naming Fable is rejected.

Stages are the cross-session checkpoint: `stage: "find"` returns the aggregated findings — write them to `review/findings.json`; `stage: "verify"` takes `findings` from that file and skips Find. There are no per-agent files.

The finder prompt names the card path, the slice files and hunks, the card's scope, the candidates for that card, `design_intent`, `project_context` and the empty-case rule, and wraps hunks, intent, context and candidates in `<target_excerpt>` tags as untrusted data. The skeptic prompt carries the finding inside `<finding>` tags as data and is adversarial: try to refute; refute only with something opened; suspicion is not a refutation; a confirmed finding is a real result; calibrate severity against the four definitions in §Report. A skeptic's output is a verdict; discovery belongs to the finders and the logic pass.

Enforcement caveat: the workflow runtime grants `Write`/`Edit` to sub-agents regardless of their `tools:` allowlist (claude-code#63762), so inside a run each prompt's read-only prohibition is the operative barrier: every finder and skeptic is told to read, grep and run read-only git only, to write nothing, and to execute no code from the diff; the integrity check in Phase 5 is mandatory. The two agent types are declared by this plugin and resolve only where it is installed, as `code-quality:review-finder` and `code-quality:review-verifier`; in a repository checkout, omit `agentTypes`.

Script declarations: `scripts/review-workflow.js` orchestrates only — it reads its arguments, writes no files, and its sole privilege is spawning sub-agents; zero external dependencies. `scripts/static-review.py` reads the repository and the cards and writes the two plan files. `scripts/bundle-run.py` reads the plan, the intent and the context and writes `review/run.js`. `scripts/validate-review-cards.py` reads the cards and the two maps and writes nothing; `scripts/tests/` reads a fixture repository it builds under a temporary directory. Every script is standard library only, no network; a change to any of them re-runs `scripts/tests/` and the fixture grading, as `references/maintenance.md` states. `scripts/render-reports.py` reads `plan.json` and `verdicts.json` and writes the two reports.

Fallback, manual dispatch (degraded). When the Workflow tool is unavailable, dispatch one Agent-tool sub-agent per triggered domain — `plan.jobs` grouped by `card.domain` — with `Read, Grep, Glob, Bash` as its tools (Bash for read-only git), giving each the paths of its cards, the slices from the plan, `design_intent`, `project_context` and the same `FINDINGS` schema, using the `code-quality:review-finder` type (the Agent tool enforces its allowlist). Then aggregate by hand per §Aggregation, and dispatch one `code-quality:review-verifier` sub-agent per finding with the skeptic prompt from the script. This path bundles a domain's cards into one agent, so it misses more than the primary path; name it as degraded in the report's Executive Summary.

---

## Phase 5: Follow-ups

The workflow returns `findings`, `conflicts`, `tally`, `agents_run` and `main_agent_followups`. Do them in this order:

1. **Integrity** — `git status` and `git diff` in the repository root, both read-only. Per the quick rules a changed tree is a compromised review: discard the findings, tell the user which files changed, and re-run through the fallback once the user has restored the tree.
2. **Persist** — write the returned `findings` to `review/verdicts.json` (after `stage: "find"`, to `review/findings.json`).
3. **Render** — `python3 <skill-dir>/scripts/render-reports.py --verdicts review/verdicts.json --plan review/plan.json --out <report path> --title "<TICKET_ID or branch>" --passes "<one line: N card jobs, M logic slices, K project invariants; fallback if used>"`.

---

## Phase 6: Report

Goal: two Markdown documents. Why: the review report carries only what survived verification; the rejection report lets the author challenge anything filtered.

Severity, the scale finders start from and skeptics calibrate against:

| Severity | Definition |
|--|--|
| Critical | data loss, a security breach (remote code execution, injection, auth bypass), data corruption under normal operation |
| Major | a correctness bug, a resource leak that degrades over time, a concurrency defect that yields wrong results, a security defect that needs specific conditions |
| Minor | a performance cost, a clarity problem, missing error handling for an unlikely scenario |
| Suggestion | style, documentation, naming |

Every finding carries its `rule_id` (`CC-NN` concurrency, `SEC-NN` security, `PF-NN` performance, `REL-NN` reliability, `MNT-NN` maintainability, `META-NN` config audit, `PROJ-N` project invariant, `LOGIC` the logic pass), an ordinal (`CC-08.1`), and a one-line source pointer taken from the card's `## Source`.

### The two documents

Document 1, the review report, is saved to the config's `review_output` (with `{TICKET_ID}` substituted) or `review/java-review-<branch>.md`: an executive summary (diff ref, size, passes, finding counts by severity, verification tally, a Block / Merge with fixes / Merge recommendation), the critical and major findings in full (rule id with its one-line source, location, code, problem, suggested fix, rationale), a table of minor findings and suggestions, and a section for findings an arbiter left `uncertain`. Document 2, the rejection report, sits beside it with the `-rejections` suffix: every finding rejected or downgraded, with the evidence the skeptic opened. `scripts/render-reports.py` writes both; their exact layout is `references/report-format.md`.

### Report to the user

Print the Executive Summary to the conversation with the paths of both documents. With zero rejections, say "0 rejected" and still write the rejection report, which then holds only the summary.

---

## Aggregation

Deterministic; the definitions here are canonical and `scripts/review-workflow.js` encodes them (`DEFER_TO`, `DOMAIN_PRIORITY`, `compatible`).

1. Drop exact duplicates — same `rule_id`, `file`, `symbol` and whitespace-normalized `code`.
2. Group by span — (`file`, `symbol`, normalized `code`).
3. Ownership — `DEFER_TO` maps a deferring `rule_id` to its owner(s); a finding drops when its owner also flagged the span. The pairs, found by the corpus reviewers where one concept is stated twice, are tabled in `references/maintenance.md` and encoded in `scripts/review-workflow.js`.
4. Fold compatible fixes — two fixes are compatible when their whitespace-normalized code is equal or one contains the other. Within a group, compatible findings collapse into the one with the highest domain priority, then the highest severity; the others' rule ids go to `also`, their problem and rationale to `folded`, and the kept finding takes the highest severity among them. A leak flagged as performance is carried by reliability; a lock-scope span flagged by concurrency and performance is carried by concurrency with the performance note folded in.
5. Conflict — incompatible fixes on one span: `DOMAIN_PRIORITY` security (0) > concurrency = reliability = project = logic (1) > performance (2) > maintainability = meta (3); the highest wins, the losers' rule ids go to its `also` and their problem, rationale and fix to `superseded`; a tie at the top keeps both, marks them `conflict`, and lists them for the author.
6. Sort by severity (critical, major, minor, suggestion), then file, then symbol; ids are `<rule_id>.<ordinal>` in that order.

The finder's dispatched card is authoritative for `rule_id`: a finding a finder tags with another id is retagged and the retag logged.

---

## Maintenance

Adding, removing or changing a card, a script, a prompt or a tier: `references/maintenance.md` names what changes together and what to re-run.

## Gotchas

Symptom-indexed reference — each entry ties a failure of the review to its cause and fix — lives in `references/gotchas.md` (G-01 … G-15; retired numbers stay vacant). Read it when a review misfires: shallow findings, a rejected control that reached the report, a workflow dying on its first agent, a card that never triggers, a syntax check that fails on the script.
