# Checkpointing Protocol

> Every agent in this skill is independently resumable. If the process is interrupted mid-run, the dispatcher can restart **only the incomplete agents** without redoing finished work. This document defines the on-disk layout, the completion-marker contract, and the restart logic.

## Contents
- §Run directory layout
- §Completion-marker rule
- §Dispatcher restart logic
- §Agent contract (shared across all 10 methods)
- §File naming
- §Failure modes

---

## Run directory layout

A single skill invocation creates one **run directory**. Everything about the run lives there — inputs, per-agent prompts, per-agent outputs, and the final aggregated report.

```
tmp/coverage-map-{topic-slug}/
├── run.md                                       # topic, inputs, timestamps, dispatcher state
├── prompts/
│   ├── 01-structural-decomposition.md           # prompt actually dispatched to agent 1
│   ├── 02-perspective-shifting.md
│   ├── 03-inversion.md
│   ├── 04-causal-chains.md
│   ├── 05-temporal-scale.md
│   ├── 06-assumptions.md
│   ├── 07-field-intelligence.md
│   ├── 08-adjacent-sweep.md
│   ├── 09-meta-questions.md
│   ├── 10-coverage-audit.md
│   └── synthesis.md                             # prompt for the reader-facing synthesis stage
├── outputs/
│   ├── 01-structural-decomposition.md           # agent 1 output; ends with <!-- COMPLETE --> when done
│   ├── 02-perspective-shifting.md
│   ├── …
│   └── 10-coverage-audit.md
└── {topic-slug}-questions.md                    # reader-facing synthesised question map (also ends with <!-- COMPLETE -->)
```

The pipeline has three sequential stages; the first stage's nine agents run in parallel:
1. **Stage 1 — parallel**: agents 01..09
2. **Stage 2 — sequential after Stage 1 completes**: agent 10 (Coverage Audit), reading outputs/01..09
3. **Stage 3 — sequential after Stage 2 completes**: Synthesis, reading outputs/01..10 and writing `{topic-slug}-questions.md`

Each stage has its own completion marker contract (below). A restart skips any stage whose output is already complete.

- `{topic-slug}` follows the global naming rule: lowercase, hyphens, date-prefix optional per `~/.claude/CLAUDE.md` conventions. Example: `tmp/coverage-map-http-caching/`.
- `run.md` is written **once** at dispatch and updated with timestamps as each agent completes.
- `prompts/NN-method.md` is the **actual prompt dispatched** — it equals `agents/method-NN-*/prompt.md` with the topic + inputs substituted. Saving it (not the template) guarantees bit-exact reproducibility on restart.
- `outputs/NN-method.md` is the agent's own writing. The agent writes a partial file as it works; the **completion marker is the last thing it writes**.

## Completion-marker rule

**Sentinel**: the last non-blank line of every `outputs/NN-*.md` file MUST be exactly:

```
<!-- COMPLETE -->
```

- Agents write this line **only after every other piece of their output is finalized** (all tables populated, all citations verified, all sections filled or explicitly marked `open — needs source`).
- Partial files MUST NOT contain `<!-- COMPLETE -->`. If an agent exits mid-stream, the sentinel is absent — the dispatcher treats the run as incomplete and re-dispatches.
- The sentinel is the only truth signal; timestamps in `run.md` are advisory (the dispatcher may write them, but they do not determine completeness).

## Dispatcher restart logic

On every invocation (first run or restart), the dispatcher executes this decision tree for each of the 10 methods:

```
# Stage 1 — parallel (dispatch all to-be-run agents in a single batched Agent call)
FOR each method NN in 01..09:
    IF prompts/NN-*.md does not exist:
        write it (fill the template with topic + inputs + output_path)
    IF outputs/NN-*.md exists AND last non-blank line == "<!-- COMPLETE -->":
        MARK done
    ELSE:
        truncate / remove outputs/NN-*.md
        MARK to-dispatch

DISPATCH to-dispatch agents in parallel with run_in_background: true
WAIT for all to complete

# Stage 2 — sequential
IF prompts/10-coverage-audit.md does not exist: write it
IF outputs/10-coverage-audit.md exists AND ends with "<!-- COMPLETE -->":
    SKIP
ELSE:
    truncate outputs/10-coverage-audit.md
    DISPATCH agent 10 (reads outputs/01..09)
    WAIT

# Stage 3 — sequential
IF prompts/synthesis.md does not exist: write it
IF {topic-slug}-questions.md exists AND ends with "<!-- COMPLETE -->":
    SKIP
ELSE:
    truncate {topic-slug}-questions.md
    DISPATCH Synthesis (reads outputs/01..10)
    WAIT

COPY {topic-slug}-questions.md to user's cwd
```

- Stage 1 agents dispatch in **parallel** (one batched `Agent` tool call with multiple blocks, `run_in_background: true`).
- Stages 2 and 3 each block on the previous stage's completion marker.
- A second or third invocation with the same topic is a no-op for already-complete stages — only incomplete ones re-run.
- To force a specific stage to re-run, delete its output file. Its saved prompt on disk is preserved so the restart is bit-exact.

## Agent contract (shared across all 10 methods)

Every agent prompt under `agents/method-NN-*/prompt.md` follows this structure:

1. **Role** — one sentence on what this agent is.
2. **Task** — the specific method to run (with a primary-source citation).
3. **Inputs** — how to read topic + anchors from `run.md`; where inputs live on disk.
4. **Method** — concrete steps (usually 3–7 numbered steps).
5. **Output contract** — the exact file path to write to (`outputs/NN-*.md`), the required shape (sections, tables), the length target, and the completion-marker rule.
6. **Verification** — self-checks the agent runs before writing the completion marker (citations verified, no fabricated sources, minimum row counts met).
7. **Gotchas** — method-specific pitfalls (e.g. "don't conflate Gentner's relational mapping with surface similarity").

The agent's prompt on disk (`prompts/NN-*.md`) is the same structure with the `{topic}` and `{run_dir}` placeholders already substituted.

Every agent has at minimum the tools: **Read, Write, WebSearch, Grep**. Agents that need to re-read other agents' outputs (only agent 10) also use **Glob**.

## File naming

- Run directory: `coverage-map-{topic-slug}/` under `tmp/`
- Topic slug: lowercase, hyphens, ASCII only. Non-ASCII topics are transliterated (`психоанализ` → `psychoanalysis`).
- Prompt files: `NN-short-method-name.md` where `NN` is the method number (01–10, zero-padded).
- Output files: same name as prompt file, different directory.
- The NN prefix is load-bearing — it defines dispatch order for agent 10 (which reads 01..09 in numerical order) and the final report assembly order.

## Failure modes

| Symptom | Diagnosis | Fix |
|--|--|--|
| `outputs/NN-*.md` exists but no `<!-- COMPLETE -->` | Agent crashed or was cancelled mid-run | Dispatcher re-dispatches agent NN on next invocation |
| `outputs/NN-*.md` has the marker but output is thin / missing sections | Agent stubbed its own verification | Re-run with `force_redispatch: NN` flag; fix the agent prompt if the pattern repeats |
| Prompt file exists but output never appeared | Background agent failed to start | Check the dispatcher's session log; re-dispatch |
| `run.md` missing | Dispatcher was interrupted before any work | Re-invoke with the same topic — dispatcher rebuilds `run.md` from defaults |
| Two concurrent dispatchers in the same run directory | Race condition on the same `outputs/*.md` | Dispatcher MUST hold a lock file (`run.md` itself acts as the lock — if newer than 10 s and has `state: dispatching`, abort) |

**Key invariant**: no agent ever edits another agent's output file. The dispatcher is the only writer of `run.md`. Each method-NN agent is the only writer of its own `outputs/NN-*.md`. The Synthesis agent is the only writer of `{topic-slug}-questions.md`.
