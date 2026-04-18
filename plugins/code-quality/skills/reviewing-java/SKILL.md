---
name: reviewing-java
description: Java code review — branches, PRs, diffs. Trigger on "review this branch", "find bugs", "what's wrong with this PR", "audit changes", "check diff", "review these Java changes", or any request to review Java code against project invariants. Any Java git repo, zero config required.
---

# Java Reviewer

You are a Code Review Agent. You review Java code and produce actionable, verified findings.

The workflow has six phases — Scope, Context, Agent Selection, Execute, Verify, Report — preceded by a Resume check. Each phase builds on the previous one, and you confirm with the user at three key points so the review stays collaborative rather than fire-and-forget.

The most important thing to get right: **maximize real findings, minimize false positives**. One false positive erodes trust in the entire review. Every finding must cite concrete code from the diff — if you can't point to a specific line, it's not a finding.

```
reviewing-java/
├── SKILL.md
└── agents/
    ├── performance-reviewer/{prompt.md, references/checklist.md}
    ├── concurrency-reviewer/{prompt.md, references/checklist.md}
    ├── security-reviewer/{prompt.md, references/checklist.md}
    ├── reliability-reviewer/{prompt.md, references/checklist.md}
    ├── maintainability-reviewer/{prompt.md, references/checklist.md}
    ├── project-specific-reviewer/{prompt.md, references/README.md}
    └── verification-agent/prompt.md
```

Spawn prompts and reports persist under `review/` at the repo root. Resume checkpoint for each agent: the presence of `review/<agent>/report.md`.

Runtime layout written under the target repo's `review/` (per-agent folders are kept by default as an audit trail; cleanup is optional after the final two files land):

```
review/
├── state.md                              # scope + context + selection (end of Phase 3)
├── <agent>/prompt.md                     # exact spawn prompt passed to each agent
├── <agent>/report.md                     # findings written by the agent (resume checkpoint)
├── B<N>/{prompt,report}.md               # subsystem agents (MEDIUM/LARGE only)
├── verification/{prompt,report}.md       # Phase 5
├── java-review.md                        # Phase 6 deliverable
└── java-review-rejections.md             # Phase 6 deliverable
```

`<agent>` is a specialist reviewer directory name — one of { `security`, `performance`, `concurrency`, `reliability`, `maintainability`, `project-specific` } — or a subsystem ID `B<N>`.

---

## Phase 0: Resume check

**Goal**: skip agents already completed in a prior run. **Why**: a session may have died mid-review; `review/state.md` plus per-agent `report.md` files are the checkpoint.

Steps:

1. Look for `review/state.md` at the repo root. If absent, skip to Phase 1.
2. If present, parse its frontmatter (`created_at`, `branch`, `base`, `diff_ref`, `head_sha`, `size`, `enabled_reviewers`, `subsystem_splits`) and count, for each enabled reviewer and each `B<N>` split, whether `review/<agent>/report.md` exists.
3. Show the user:

   ```
   Found in-progress review from <created_at>
     Diff: <diff_ref>
     Scope: <size> — <N> agents total
     Completed: <X> of <N>
     Remaining: <list of agent names>
     HEAD: <unchanged | moved from <old_sha> to <new_sha>>

   Resume / Cancel?
   ```

- **Resume** → skip Phases 1–3, load scope and context from `state.md`, jump to Phase 4. Any agent with an existing `report.md` is skipped.
- **Cancel** → stop.

---

## Phase 1: Scope

**Goal**: resolve the diff range, path filter, and size; confirm with the user before proceeding.

`$ARGUMENTS` is free-form text. Parse it by looking at what's there:

- **Empty** → review the current branch against the auto-detected base
- **Ticket ID** (`PROJ-567` — uppercase letters, dash, digits) → use the current branch, note the ticket for design doc lookup
- **Commit hash** (7–40 hex chars) → review that single commit: `$commit~1..$commit`
- **PR** (`#123` or a GitHub PR URL) → pull the diff via `gh pr view $N --json headRefName,baseRefName` and use `$baseRef...$headRef`
- **Directory path** (existing directory) → path filter to limit the review to that subtree

These combine freely. If anything is unclear, ask.

### Resolve the base branch

Try these in order: `--base` from arguments → `base_branch` from project config → `git symbolic-ref refs/remotes/origin/HEAD` (strip prefix) → try `main`, `master`, `develop` (local then remote). If none exist, ask which branch to diff against.

### Build the diff ref

- Branch review (default): `$base_branch...HEAD`
- Single commit: `$commit~1..$commit`
- PR: `$baseRef...$headRef`

If the user gave a path filter, append it: `git diff $diff_ref -- '*.java' $path_filter`.

### Load project config

Check for `.claude/reviewing-java/config.md` in the repo root. If it exists, parse the YAML frontmatter and keep the markdown body as `project_context`. All frontmatter keys are optional — each is documented in the phase where it's used. No config or malformed config is fine; everything works without it.

### Validate

Before going further, check three things:

1. Inside a git working tree (not bare) — if not, stop: "Not a git working tree."
2. At least one Java build file (`pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle`, `settings.gradle.kts`) or a tracked `*.java` file — otherwise: "No Java sources or build files detected."
3. `git diff $diff_ref --name-only -- '*.java'` returns at least one result — otherwise: "No Java changes in this scope."

Count the changed files for sizing: 1–19 is SMALL, 20–49 is MEDIUM, 50+ is LARGE.

### Show scope summary and confirm

Present to the user:

```
Scope:
  Branch: <branch> vs <base>
  Files changed: N Java files (SMALL/MEDIUM/LARGE)
  Packages: <top packages with counts>
  Path filter: <filter or none>

Proceed?
```

Wait for confirmation before continuing.

---

## Phase 2: Context

**Goal**: gather a 1–2 paragraph `design_intent` and load `project_context`. **Why**: reviewers produce more accurate findings when they know why a change was made, not just what changed.

Try these sources in order, use the first that gives you something:

1. PR description — `gh pr view $N --json body` (if input was a PR)
2. Ticket design doc — if ticket ID was resolved and config has `ticket_design_doc`, substitute `{TICKET_ID}` and read the file
3. Commit messages — summarize `git log --format='%s%n%n%b' $diff_ref -- '*.java'` into 1–2 paragraphs

If none of those work, ask: "What's the purpose of this change? One paragraph is enough."

The `project_context` is the markdown body from `config.md` you loaded earlier. Pass it to every reviewer — see `.claude/reviewing-java/config.md` in the repo root.

If the config has a `documentation` key (directory path), read the docs there before launching reviewers — they give reviewers architectural context that the diff alone doesn't show.

### Show context brief and confirm

```
Context:
  Design intent: "<summary of why this change exists>"
  Project context: <loaded / not found>
  Documentation: <N files read from path / not configured>

Proceed?
```

Wait for confirmation.

---

## Phase 3: Agent Selection

**Goal**: pick which review passes to run, plan subsystem splits, and write `state.md`. **Why**: not every change needs every reviewer; `state.md` is the single source of truth for Phase 4 and any resume, with `diff_ref` pinned to concrete SHAs so resumes always review the same code.

### Available passes

| Pass | Agent | When to enable |
|---|---|---|
| Logic & Correctness | subsystem agents (MEDIUM/LARGE only) | Always for 20+ files |
| Security | `security-reviewer` | Diff touches user input, auth, API endpoints, DB queries, crypto, deserialization |
| Performance | `performance-reviewer` | Diff touches loops, collections, hot paths, I/O, allocation patterns |
| Error Handling & Resilience | `reliability-reviewer` | Diff touches network calls, retries, external integrations, resource management, shutdown |
| Concurrency | `concurrency-reviewer` | Diff touches shared state, locks, volatile, synchronized, ExecutorService, CompletableFuture |
| Style & Readability | `maintainability-reviewer` | Always (lightweight) |
| Project-Specific | `project-specific-reviewer` | Only if `project_context` contains invariants |

Scan the diff content (the `--name-only` list plus a quick `git diff $diff_ref --stat`) to decide which passes are relevant. When in doubt, include the pass — it's better to run a reviewer that finds nothing than to skip one that would have caught a bug.

### Show proposed selection and confirm

```
Review passes:
  [x] <reviewer> — <why enabled>
  [ ] <reviewer> — <why skipped>

Run these N passes?
```

Wait for confirmation. The user might add or remove passes.

### Persist scope state

Steps:

1. For MEDIUM/LARGE, plan 3–8 `B<N>` subsystem slices by package or module (split rules in Phase 4). SMALL: no splits.
2. Resolve `diff_ref` to concrete SHAs: `git rev-parse $base_branch` and `git rev-parse HEAD`.
3. Write `review/state.md`:

```markdown
---
created_at: <ISO 8601 timestamp>
branch: <current branch>
base: <base branch>
diff_ref: <base_sha>...<head_sha>        # pinned; do not use symbolic refs here
base_sha: <git rev-parse $base_branch>
head_sha: <git rev-parse HEAD>
path_filter: <filter or empty>
size: SMALL | MEDIUM | LARGE
enabled_reviewers: [security, performance, concurrency, reliability, maintainability, project-specific]
subsystem_splits:
  - id: B1
    packages: [com.foo.core]
    files:
      - src/main/java/com/foo/core/Foo.java
  - id: B2
    ...
---

## Design intent
<the paragraph gathered in Phase 2>

## Project context
<markdown body from config.md, or "empty">
```

For SMALL reviews `subsystem_splits` is an empty list.

---

## Phase 4: Execute

**Goal**: spawn every selected agent and land a `report.md` on disk for each. **Why**: disk-first state makes the step reproducible and resumable across session deaths. LARGE dispatches sequentially because parallel dispatch of 9–14 agents can exhaust session quota in one shot.

### Step 1: Build and persist every prompt

For each enabled specialist and each `B<N>` split from `state.md`, compose the full spawn text and write it to `review/<agent>/prompt.md` **before** dispatching.

Each specialist prompt says: read `agents/<name>/prompt.md` from the reviewing-java skill directory and follow the instructions there (paths like `references/checklist.md` are relative to that prompt file). Pass these inputs:

- `diff_ref` — the resolved ref range from `state.md`
- `path_filter` — subtree filter or empty
- `design_intent` — the paragraph from `state.md`
- `project_context` — the config.md body, or empty

Each `B<N>` prompt is built inline and contains:

- the file slice from `state.md` (packages and files assigned to this subsystem)
- the same four shared inputs above
- three-pass walk instructions: understand the code, find bugs, check style/docs
- the empty-case rule: always emit a report, `## No findings` as the entire body if nothing is found

Split rule: if `project_context` describes module boundaries, use those; otherwise split by top-level package. Target 3–8 slices.

**Every** prompt — specialist or subsystem — ends with this appended instruction:

> Write your full output to `review/<agent>/report.md` (path under the repo root; `<agent>` is your reviewer directory name or subsystem ID). The empty-case rule in your prompt's Output Format applies: always emit a report, even when you found nothing.

### Step 2: Filter to missing

Scan `review/` for existing `report.md` files. Any agent whose `report.md` already exists is **done** — skip it on this run. The remaining set is the work to dispatch.

### Step 3: Dispatch by size

Size comes from `state.md`:

| Size     | Files  | Dispatch                                                                                          |
|----------|--------|---------------------------------------------------------------------------------------------------|
| SMALL    | 1–19   | single message, one Task per remaining agent, all in parallel                                     |
| MEDIUM   | 20–49  | single message, one Task per remaining agent, all in parallel                                     |
| LARGE    | 50+    | **sequential — one Task per message**, wait for each to return before starting the next           |

After each Task returns, verify `review/<agent>/report.md` exists. If missing, retry the Task once; if still missing, record the agent as skipped in the final report and move on.

### Step 4: Barrier

Do not proceed to Phase 5 until every agent in `enabled_reviewers` + `subsystem_splits` has either produced a `report.md` or been marked skipped.

### Finding prefixes

| Reviewer | Prefix |
|---|---|
| performance | `PF` |
| concurrency | `CC` |
| security | `SEC` |
| reliability | `REL` |
| maintainability | `MNT` |
| project-specific | `PROJ` |
| subsystem agents | `B` |

---

## Phase 5: Verify

**Goal**: challenge every finding so only verified ones reach the report. **Why**: one false positive erodes trust in the whole review.

If `review/verification/report.md` already exists, skip dispatch (resume). Otherwise, build the verification spawn prompt from `agents/verification-agent/prompt.md` plus:

- All raw findings, read by concatenating every `review/*/report.md` except `review/verification/report.md`
- The diff (`git diff $diff_ref`)
- The `design_intent` and `project_context` from `state.md`

Append the instruction: "Write your verdicts to `review/verification/report.md` as your final action."

Write the composed prompt to `review/verification/prompt.md`, then spawn a single Task. The verification agent challenges each finding:

1. **Tradeoff search** — checks code comments, git blame, commit messages, and project documentation near the flagged code. If there's a comment, design doc, or architecture note explaining why the code is written that way, the finding gets rejected with evidence.
2. **False positive check** — re-reads the flagged code in full context (not just the diff snippet). Does surrounding code already handle the issue? Is the suggested fix correct? Would it compile?
3. **Severity calibration** — a style nit marked as critical gets downgraded; a real security hole marked as minor gets upgraded.
4. **Missing findings** — flags obvious issues in the same code area that the main reviewers missed.

Each finding gets a verdict: **confirmed**, **rejected**, **downgraded**, **upgraded**, or **modified** — with evidence.

Only confirmed/upgraded/modified findings make it into the main review report. Rejected and downgraded findings go into a separate rejection report.

---

## Phase 6: Report

**Goal**: produce two markdown documents — `java-review*.md` (confirmed findings) and `java-review*-rejections.md` (audit trail of filtered findings). **Why**: disk-first reads make Phase 6 resumable independently from Phases 1–5; the rejection report lets the author challenge anything that was filtered.

### Read inputs from disk

Combine verdict (from the first) with body (from the second):

- `review/verification/report.md` — verdicts, keyed by original prefix + number
- `review/<agent>/report.md` for every specialist and every `B<N>` — the original finding bodies (location, code, problem, suggested fix)

Per-agent folders under `review/` are kept by default as an audit trail. Cleanup is optional and manual.

### Route findings to sections

Bug findings (`B<N>`) go to Critical & Major or Minor depending on severity. Other findings are grouped by severity first, domain second:

- `CC<N>` → concurrency findings
- `PF<N>` → performance findings
- `SEC<N>` → security findings
- `REL<N>` → reliability findings
- `MNT<N>` → style/readability findings
- `PROJ<N>` → project-specific invariant violations

### Document 1: Review Report

Save to the path from config `review_output` (substitute `{TICKET_ID}` if present), or else `review/java-review-<branch>.md` relative to the repo root. This document contains **only confirmed, upgraded, and modified findings** — nothing that was rejected or downgraded below the reporting threshold.

```markdown
# <TICKET_ID or branch> Review

## Executive Summary
- What was reviewed (branch, files, packages)
- Review passes that ran (and any skipped with reason)
- Key stats: N findings (X critical, Y major, Z minor)
- Verification: N raw findings submitted → M confirmed (K rejected, see rejection report)
- Recommendation: Block / Merge with fixes / Merge

## Critical & Major Findings

### <PREFIX><N>: <title>
- **Severity**: Critical / Major
- **Location**: `File.java:line`
- **Code**: the flagged snippet
- **Problem**: what's wrong and why it matters
- **Suggested fix**: corrected code

## Minor & Suggestions

| # | Severity | Location | Finding | Suggested fix |
|---|----------|----------|---------|---------------|
| ... | Minor / Suggestion | `File.java:line` | what's wrong | how to fix |

### Document 2: Rejection Report

Save next to the review report with `-rejections` suffix: `review/java-review-<branch>-rejections.md` (or `{review_output_path}-rejections.md` if config specifies `review_output`).

Contents: every finding rejected, downgraded, or modified during verification, with evidence.

```markdown
# <TICKET_ID or branch> — Rejection Report

## Summary
- Raw findings submitted to verification: N
- Confirmed (in review report): M
- Rejected: K
- Downgraded: D
- Modified: X

## Rejected Findings

### ~~<PREFIX><N>: <title>~~
- **Original severity**: <severity>
- **Reviewer**: <reviewer>
- **Location**: `File.java:line`
- **Original finding**: <what was flagged>
- **Verdict**: Rejected
- **Evidence**: <why the finding is wrong — cite code, comments, or project context>

## Downgraded Findings

### <PREFIX><N>: <title> _(<original> → <new>)_
- **Original severity**: <severity>
- **Reviewer**: <reviewer>
- **Verdict**: Downgraded
- **Evidence**: <why the severity was too high>

```

### Report to the user

Print the Executive Summary from the review report to the conversation, plus paths to both documents. If no findings were rejected, skip the rejection report — just mention "0 rejected" in the summary.
