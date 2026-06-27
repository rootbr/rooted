# Checkpointing Protocol

> Every stage of the appraisal is independently resumable. If the process is interrupted mid-run, the dispatcher restarts **only the incomplete stages** without redoing finished work. This document defines the on-disk layout, the completion-marker contract, and the restart logic. It mirrors `discovering-subtopics/references/checkpointing-protocol.md`, adapted for the critic's five stages.

## Contents
- §Run directory layout
- §Completion-marker rule
- §Dispatcher restart logic
- §Agent contract (shared across all agents)
- §File naming
- §Failure modes

---

## Run directory layout

A single skill invocation creates one **run directory** under `tmp/`. Everything about the run lives there — inputs, per-agent prompts, per-agent outputs, and the final appraisal.

```
tmp/appraisal-{report-slug}/
├── run.md                                   # report path, inputs, depth, dispatcher state
├── claims.md                                # decomposer output: main conclusion(s) + atomic claims + cited sources + topic type
├── prompts/
│   ├── decomposer.md
│   ├── c01-evidence-grading.md … c07-logic-fallacy.md
│   ├── adjudicator.md
│   ├── debate-<finding-id>.md               # one per debated finding
│   └── synthesis.md
├── outputs/
│   ├── c01-evidence-grading.md … c07-logic-fallacy.md   # each ends with <!-- COMPLETE -->
│   ├── adjudication.md                                   # ranked findings + debate selection
│   ├── debate/<finding-id>.md                            # one verdict file per debated finding
│   └── (synthesis writes below, not here)
├── {report-slug}-appraisal.md               # reader-facing deliverable; ends with <!-- COMPLETE -->
└── {report-slug}-appraisal-rejections.md    # audit trail of rejected / downgraded findings
```

The pipeline has five sequential stages; only Stage 2 fans out in parallel:

1. **Stage 1 — Decompose** (one agent): writes `claims.md`.
2. **Stage 2 — Methods** (parallel, batches of 4): agents c01..c07 read `claims.md` + the report, write `outputs/cNN-*.md`.
3. **Stage 3 — Adjudicate** (one agent, after Stage 2): reads all seven outputs, writes `outputs/adjudication.md` (dedup, false-positive rejection, priority ranking, `debate: yes` flags).
4. **Stage 4 — Debate** (parallel triads, after Stage 3): for each `debate: yes` finding, writes `outputs/debate/<finding-id>.md`.
5. **Stage 5 — Synthesize** (one agent, after Stage 4): reads `adjudication.md` + debate verdicts, writes `{report-slug}-appraisal.md` and `{report-slug}-appraisal-rejections.md`.

- `{report-slug}` follows the global naming rule: lowercase, hyphens, ASCII (transliterate non-ASCII).
- `run.md` is written once at dispatch and updated with timestamps as stages complete.
- `prompts/*.md` is the **actual spawn prompt dispatched**: a thin wrapper that (a) tells the sub-agent to read its canonical prompt at `<skill>/agents/<name>/prompt.md` and follow it, and (b) supplies the run-specific inputs (report path, `run_dir`, output path, depth). It does **not** inline the method body — the canonical prompt stays the single source of truth, and its relative links (`../../references/…`) resolve only when read from that skill location. Saving the wrapper guarantees bit-exact reproducibility on restart.
- Each output file's **completion marker is the last thing its agent writes**.

## Completion-marker rule

**Sentinel**: the last non-blank line of every output file (`claims.md`, `outputs/*.md`, `outputs/debate/*.md`, and the two deliverables) MUST be exactly:

```
<!-- COMPLETE -->
```

- Agents write it **only after every other piece of output is finalized** (all findings written, all citations verified, empty case emitted if nothing found).
- Partial files MUST NOT contain the sentinel. If an agent exits mid-stream, the sentinel is absent — the dispatcher treats the stage as incomplete and re-dispatches.
- The sentinel is the only truth signal; `run.md` timestamps are advisory.

## Dispatcher restart logic

On every invocation the dispatcher runs this decision tree:

```
# Stage 1 — Decompose
IF prompts/decomposer.md missing: write it
IF claims.md exists AND ends with "<!-- COMPLETE -->": SKIP
ELSE: truncate claims.md; DISPATCH decomposer; WAIT

# Stage 2 — Methods (parallel, batch of 4)
FOR each method cNN in c01..c07:
    IF prompts/cNN-*.md missing: write it
    IF outputs/cNN-*.md exists AND ends with "<!-- COMPLETE -->": MARK done
    ELSE: truncate outputs/cNN-*.md; MARK to-dispatch
DISPATCH to-dispatch in batches of 4 (run_in_background: true); WAIT for all

# Stage 3 — Adjudicate
IF prompts/adjudicator.md missing: write it
IF outputs/adjudication.md exists AND ends with "<!-- COMPLETE -->": SKIP
ELSE: truncate outputs/adjudication.md; DISPATCH adjudicator (reads outputs/c01..c07); WAIT

# Stage 4 — Debate (parallel triads)
READ debate set from outputs/adjudication.md (findings with debate: yes)
FOR each finding-id in debate set:
    IF outputs/debate/<finding-id>.md exists AND ends with "<!-- COMPLETE -->": MARK done
    ELSE: write prompts/debate-<finding-id>.md; MARK to-dispatch
DISPATCH to-dispatch triads in batches (≤ 4 concurrent Judges); WAIT

# Stage 5 — Synthesize
IF prompts/synthesis.md missing: write it
IF {report-slug}-appraisal.md exists AND ends with "<!-- COMPLETE -->": SKIP
ELSE: truncate it; DISPATCH synthesis (reads adjudication.md + outputs/debate/*); WAIT

COPY {report-slug}-appraisal.md (and -rejections.md) to the user's cwd
```

- Stage 2 agents dispatch in batches of 4 (`run_in_background: true`); Stages 1, 3, 5 are single agents; Stage 4 fans out triads.
- Stages 3, 4, 5 each block on the previous stage's completion markers.
- A re-invocation with the same report is a no-op for already-complete stages — only incomplete ones re-run.
- To force a stage to re-run, delete its output file; its saved prompt on disk is preserved for a bit-exact restart.

## Agent contract (shared across all agents)

Every agent prompt under `agents/*/prompt.md` follows this structure:

1. **Role** — one sentence on what this agent is.
2. **Inputs** — how to read the report, `claims.md`, and anchors from `run.md`; where inputs live on disk.
3. **Process** — read the method's theory in `references/appraisal-methodology.md`, then concrete steps.
4. **Output contract** — the exact file path to write, the finding schema (`references/finding-schema.md`), the length target, and the completion-marker rule.
5. **Verification** — self-checks before writing the marker (every finding has an anchor and a method source; no fabricated citations; empty case handled).
6. **Gotchas** — method-specific pitfalls.

Every agent has at minimum **Read, Write, Grep**. Retrieval-grounded agents (c02, c04, c05, c06, and both debaters + judge) also have **WebSearch, WebFetch**. The adjudicator and synthesis also have **Glob** to read sibling outputs.

## File naming

- Run directory: `appraisal-{report-slug}/` under `tmp/`.
- Method prompt/output files: `cNN-short-method-name.md`, `NN` zero-padded 01–07. The `cNN` prefix is load-bearing — it fixes the order the adjudicator reads outputs.
- Debate files: `debate/<finding-id>.md` where `<finding-id>` is the finding's ID (e.g. `ACH2`).
- Deliverables: `{report-slug}-appraisal.md` and `…-rejections.md`.

## Failure modes

| Symptom | Diagnosis | Fix |
|--|--|--|
| `outputs/cNN-*.md` exists but no `<!-- COMPLETE -->` | Agent crashed mid-run | Dispatcher re-dispatches cNN next invocation |
| Marker present but output thin / sections missing | Agent stubbed its verification | Delete the output; re-dispatch; fix the prompt if it recurs |
| `outputs/adjudication.md` lists a `debate: yes` finding with no debate output | Stage 4 interrupted | Re-dispatch only that triad |
| `claims.md` missing | Dispatcher interrupted before Stage 1 | Re-invoke; dispatcher rebuilds from the report |
| Two dispatchers in one run directory | Race on `outputs/*` | `run.md` acts as lock — if newer than 10 s with `state: dispatching`, abort |

**Key invariant**: no agent edits another agent's output file. The dispatcher is the only writer of `run.md`; each method agent is the only writer of its own `outputs/cNN-*.md`; each debate triad is the only writer of its `outputs/debate/<finding-id>.md`; synthesis is the only writer of the two deliverables.
