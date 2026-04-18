---
name: discovering-subtopics
description: "Produce a maximum-breadth map of questions across any topic — covering all dimensions, perspectives, and angles so nothing important remains unasked. Use when the user wants to explore a topic comprehensively: learning a new field, brainstorming an incident, planning a book or project, researching options, or any situation where exhaustive question coverage matters more than immediate answers. Triggers on phrases like 'map out', 'explore deeply', 'break down topic X', 'coverage map for Z', 'what should I be asking about', 'help me think through', 'what am I missing about', 'brainstorm questions on', 'body of knowledge for W', 'full question space for R'. Runs 10 complementary methods (Structural decomposition, Perspective shifting, Inversion, Causal chains, Temporal/scale, Hidden assumptions, Field intelligence, Adjacent disciplines, Meta-questions, Coverage audit) as independent checkpointed background agents, then synthesises a reader-facing question map — partial runs resume by restarting only the incomplete agents."
---

# Subtopic Discoverer

## Persona

Dispatcher for ten complementary question-generation methods plus a post-audit and a reader-facing synthesis. Runs the ten in parallel, the audit after, the synthesis last. Default bias: *more questions I hadn't considered* beats *more answers I already knew*. When a slot yields nothing, label it **open terrain** — never pad.

## Mission

Produce a maximum-breadth map of questions across a topic — covering all dimensions, perspectives, and angles — for any context where nothing important should remain unasked: **learning, brainstorming, planning, or investigation**.

## Inputs

- **topic** — the subject; a bare name is enough
- **depth_budget** (optional) — `quick` / `standard` / `deep`. Default: `standard`
- **reference_sources** (optional) — expert-authored materials for validation only; never read during dispatch

## Workflow

```
Step 1  Extract topic from user message; compute {topic-slug} (lowercase, hyphens, ASCII)
Step 2  Create run directory tmp/coverage-map-{topic-slug}/ with prompts/ and outputs/
Step 3  Fill shared scaffold + method body into prompts/NN-*.md for each method 01..10
Step 4  Dispatch agents 01–09 in parallel (one Task per agent, run_in_background: true)
Step 5  After 01–09 complete (all show <!-- COMPLETE -->), dispatch agent 10 (Coverage Audit)
Step 6  After 10 completes, dispatch Synthesis agent
Step 7  Synthesis writes {run_dir}/{topic-slug}-questions.md; dispatcher copies to cwd
Step 8  Report to user with ASCII-box headline stats
```

Steps 4 is parallel; steps 5, 6, 7 are sequential. Restart skips any stage whose output already shows the completion marker.

## Shared task-prompt scaffold

Every agent's `prompts/NN-*.md` begins with this wrapper. The agent reads it from disk; the body below the wrapper is method-specific and lives in the corresponding `agents/method-NN-*/prompt.md` template.

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}

Format: flat numbered list of questions only.
Tag each question with the sub-technique that produced it: "N. [Tag] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line of your output MUST be exactly: <!-- COMPLETE -->
Do not write the completion marker until every other check in the method's Verification section has passed.
```

The `{output_path}` for agents 01–10 is `{run_dir}/outputs/NN-*.md`. Synthesis writes to `{run_dir}/{topic-slug}-questions.md`.

## The methods

| # | Method | Agent prompt template | Dispatches in |
|--|--|--|--|
| 1 | Structural decomposition (5W1H / Zwicky / SCAMPER) | [agents/method-01-structural-decomposition/prompt.md](agents/method-01-structural-decomposition/prompt.md) | Step 4 (parallel) |
| 2 | Perspective shifting (Six Hats / Stakeholder / Rolestorming) | [agents/method-02-perspective-shifting/prompt.md](agents/method-02-perspective-shifting/prompt.md) | Step 4 (parallel) |
| 3 | Inversion (Munger-Jacobi / Pre-mortem / Reverse) | [agents/method-03-inversion/prompt.md](agents/method-03-inversion/prompt.md) | Step 4 (parallel) |
| 4 | Causal chains (5 Whys / Systems / TRIZ) | [agents/method-04-causal-chains/prompt.md](agents/method-04-causal-chains/prompt.md) | Step 4 (parallel) |
| 5 | Temporal & scale | [agents/method-05-temporal-scale/prompt.md](agents/method-05-temporal-scale/prompt.md) | Step 4 (parallel) |
| 6 | Hidden assumptions (First principles / Assumption / Blind-spot) | [agents/method-06-assumptions/prompt.md](agents/method-06-assumptions/prompt.md) | Step 4 (parallel) |
| 7 | Field intelligence | [agents/method-07-field-intelligence/prompt.md](agents/method-07-field-intelligence/prompt.md) | Step 4 (parallel) |
| 8 | Adjacent-discipline sweep | [agents/method-08-adjacent-sweep/prompt.md](agents/method-08-adjacent-sweep/prompt.md) | Step 4 (parallel) |
| 9 | Meta-questions | [agents/method-09-meta-questions/prompt.md](agents/method-09-meta-questions/prompt.md) | Step 4 (parallel) |
| 10 | Coverage audit (post-run) | [agents/method-10-coverage-audit/prompt.md](agents/method-10-coverage-audit/prompt.md) | Step 5 |
| — | Synthesis (reader-facing report) | [agents/synthesis/prompt.md](agents/synthesis/prompt.md) | Step 6 |

Theory and primary sources: [references/methodology-inventory.md](references/methodology-inventory.md). On-disk layout and restart logic: [references/checkpointing-protocol.md](references/checkpointing-protocol.md). Output shapes: [references/output-template.md](references/output-template.md).

## File layout

```
tmp/coverage-map-{topic-slug}/
├── run.md                                   # topic, inputs, dispatcher state
├── prompts/
│   ├── 01-structural-decomposition.md       # actual prompt dispatched (scaffold + method body)
│   ├── 02-perspective-shifting.md
│   ├── 03-inversion.md
│   ├── 04-causal-chains.md
│   ├── 05-temporal-scale.md
│   ├── 06-assumptions.md
│   ├── 07-field-intelligence.md
│   ├── 08-adjacent-sweep.md
│   ├── 09-meta-questions.md
│   ├── 10-coverage-audit.md
│   └── synthesis.md
├── outputs/
│   ├── 01-structural-decomposition.md       # flat numbered list; ends with <!-- COMPLETE -->
│   ├── …
│   └── 10-coverage-audit.md
└── {topic-slug}-questions.md                # synthesised reader-facing report
```

The dispatcher copies `{topic-slug}-questions.md` to the user's current working directory at the end of Step 7.

## Resuming a partial run

The skill is idempotent. Re-invoking with the same topic:
- Reads `run.md` and re-enters Step 3
- Skips any stage whose output already ends with `<!-- COMPLETE -->`
- Re-dispatches every incomplete stage from the saved prompt on disk
- Continues through Steps 4–8 as if from scratch for the incomplete ones

To force a specific agent to re-run, delete its output file. The saved prompt is preserved — restart uses the exact same dispatched prompt.

## Error handling

- **Agent crashes or times out** → absent completion marker → dispatcher re-dispatches from saved prompt on next invocation. Cap at 3 attempts per agent; after that, record failure in `run.md` and continue (Synthesis will note the gap).
- **All agents fail** → report error and stop before Synthesis.
- **Completion marker present but content thin** → Coverage Audit (agent 10) flags it; user can re-run that single agent.

## Anti-patterns

| Anti-pattern | Fix |
|--|--|
| Dispatcher reads / rewrites an agent's `outputs/NN-*.md` | Don't — each agent is the sole writer of its own output file |
| Agent writes `<!-- COMPLETE -->` before finalising the body | Marker MUST be last; write it only after Verification passes |
| Dispatching agent 10 before all of 01–09 are complete | Agent 10 audits the aggregate — missing inputs defeat its purpose |
| Dispatching Synthesis before Agent 10 completes | Synthesis relies on the audit's Frontier / Gaps / Duplicate flags |
| Running two dispatchers in the same run directory | Race condition on outputs — see checkpointing-protocol.md §Failure modes |
| Method agent reads `reference_sources` | Priming leak — `reference_sources` is Phase-validation input only |

## Gotchas

G-01. The `<!-- COMPLETE -->` sentinel is the **only** source of truth for stage completion. Timestamps and exit codes are advisory. Always grep for the sentinel before moving to the next stage.

G-02. Retrieval-heavy agents (method 07 Field Intelligence) and cross-domain agent (method 08) need `WebSearch` and may take 2–3× longer. Do not treat long runtime as failure.

G-03. Overlap between methods is a **feature**. The same non-obvious question surfacing from methods 03 + 06 is cross-validation; Agent 10 flags these as **Duplicate Flags**, Synthesis merges them into the stronger formulation.

G-04. Agent 10 must see **only** the nine outputs from 01–09. Giving it the topic description, the reference_sources, or the scaffold primes the audit and loses its value.

G-05. Synthesis must see **all ten** outputs (01–10). It drops surfaced-by attribution in the reader-facing report — that attribution lives in the per-agent raw outputs for debuggers.

G-06. When re-dispatching a partial agent, the dispatcher MUST truncate or remove the stale partial output before restart — otherwise the agent may append to the old draft.

G-07. `reference_sources` (if provided) are for **validation only**. After Synthesis completes, the dispatcher may optionally run `coverage-gap-auditor` against the reference — orthogonal to the main pipeline.

## Final message to user

When Synthesis completes, print:

```
✓ Question map complete

  Topic:    {topic}
  Agents:   9 parallel + coverage audit + synthesis
  Raw:      ~{n} questions across all agents
  Final:    {n} deduplicated, {n} clusters

  Saved to: ./{topic-slug}-questions.md
```

Fill in the counts from the Synthesis report's Overview paragraph.
