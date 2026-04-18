# Output Templates

> Two output shapes live in this skill: (1) the **per-agent raw output** each of the 10 method agents writes to `outputs/NN-*.md` — a flat numbered list of questions with sub-technique tags; and (2) the **synthesised reader-facing report** the Synthesis agent writes to `{run_dir}/{topic-slug}-questions.md`. This file documents both.

## Contents
- §Per-agent output format
- §Agent 10 (Coverage Audit) output format
- §Synthesis output format
- §Tag reference by agent
- §Length expectations

---

## Per-agent output format (agents 01–09)

Each of the nine method agents produces a flat numbered question list. No structured sub-sections — the sub-technique that produced each question is carried by a bracketed tag at the start of the question.

```markdown
# Method 0N — {Method Name}

1. [Tag] Question text?
2. [Tag] Question text?
3. [Tag] Question text?
…
N. [Tag] Question text?

<!-- COMPLETE -->
```

Rules:
- **Questions only.** No answers, no explanations, no commentary.
- **One question per line.** Sequentially numbered from 1.
- **Sub-technique tag in brackets** at the start of each question — see §Tag reference.
- **Single top-level heading** naming the method; no sub-sections.
- **Completion marker** as the last non-blank line, exactly `<!-- COMPLETE -->`.
- **No repetition** within the agent's own output (across sub-techniques). Cross-agent repetition is fine — Agent 10 flags it, Synthesis merges.

Example (Method 01):
```
# Method 01 — Structural Decomposition

1. [5W1H:Who] Who is the primary actor this topic concerns?
2. [5W1H:What] What observable changes when this topic is applied?
3. [Zwicky:scale×time] What happens at small scale over long horizons?
4. [SCAMPER:Eliminate] What could be removed without losing the essential behaviour?
…

<!-- COMPLETE -->
```

---

## Agent 10 (Coverage Audit) output format

Agent 10 reads outputs 01–09 and writes a structured report — not a question list. Exact headers are load-bearing (the Synthesis agent parses them).

```markdown
# Method 10 — Coverage Audit

## Gaps Found
{dimension name}: {generated questions filling the gap, as a numbered list}

{another dimension name}: {questions}

## Most Important Questions
1. {question text} (Agent {n}, Q{x})
2. {question text} (Agent {n}, Q{x})
…
10. {question text} (Agent {n}, Q{x})

## Duplicate Flags
Agent {n} Q{x} ≈ Agent {m} Q{y}: {shared phrasing or theme}
Agent {n} Q{x} ≈ Agent {m} Q{y}: …
(or "None found")

## Partial Agents
- outputs/NN-*.md missing <!-- COMPLETE --> — dispatcher should re-run
(or "All nine complete")

<!-- COMPLETE -->
```

- **Gaps Found** — dimensions / sub-techniques that received zero or few questions across agents 01–09. Agent 10 generates fill-in questions for each gap (this is the one place where Agent 10 generates, not just audits).
- **Most Important Questions** — top 10 questions across all agents' outputs whose answers would most change understanding of the topic. Each is tagged with source agent + question number.
- **Duplicate Flags** — near-duplicate questions across agents. Used by Synthesis for merge decisions.
- **Partial Agents** — honest report on missing completion markers. Dispatcher acts on this.

---

## Synthesis output format

Written by the Synthesis agent to `{run_dir}/{topic-slug}-questions.md`, then copied to user's cwd.

```markdown
# Question Map: {Topic}

## Overview
{One paragraph: total questions generated across agents, approximate deduplication ratio, number of thematic clusters, the 3 most unexpected question clusters, and any dimensions Agent 10 flagged as under-covered.}

## Questions by Dimension

### {Cluster name 1 — descriptive, not method-named}
1. {question}
2. {question}
…

### {Cluster name 2}
1. {question}
…

(8–12 clusters total. Questions within a cluster are ordered foundational → advanced. No `surfaced-by` / `[Tag]` attribution — those live in the per-agent raw outputs.)

## Frontier Questions
> Ten questions whose answers would most change how someone understands the topic.

1. {question} — {one-sentence rationale: why this question is frontier}
2. {question} — {rationale}
…
10. {question} — {rationale}

## Open Terrain
> Dimensions still underexplored after all agents ran. Named explicitly rather than hidden.

- {gap name}: {one-sentence reason this gap is hard to question}
- {gap name}: …

---

*Raw per-agent outputs: `{run_dir}/outputs/`. Coverage audit: `{run_dir}/outputs/10-coverage-audit.md`. Checkpoint protocol: [references/checkpointing-protocol.md]({link}).*

<!-- COMPLETE -->
```

Rules:
- **Cluster names describe dimensions, not methods.** Reject names like "Inversion questions" or "Temporal questions"; prefer names like "Failure modes", "Historical evolution", "Stakeholder concerns".
- **No agent attribution in the reader-facing report.** That stays in the raw per-agent outputs and in Agent 10's duplicate flags.
- **Deduplicate aggressively at Synthesis time.** Near-duplicates (from Agent 10's Duplicate Flags) are merged into the stronger formulation — the one with clearer grammar, more concrete object, or more pointed framing.
- **Foundational → advanced ordering** within each cluster. Entry-level questions first; questions that assume mastery last.
- **Frontier Questions are NOT the same as Agent 10's Most Important Questions** — Synthesis may agree, but is free to promote or demote based on cluster-level context.
- **Open Terrain ≠ Agent 10's Gaps Found**. Synthesis surfaces gaps still standing *after* Agent 10's fill-ins were considered and integrated into clusters.
- **Completion marker** as the last non-blank line.

---

## Tag reference by agent

Agents embed these tags in their flat numbered lists:

| Agent | Tags |
|--|--|
| 01 Structural | `[5W1H:Who]`, `[5W1H:What]`, `[5W1H:Where]`, `[5W1H:When]`, `[5W1H:Why]`, `[5W1H:How]`, `[Zwicky:paramA×paramB]`, `[SCAMPER:Substitute]`, `[SCAMPER:Combine]`, `[SCAMPER:Adapt]`, `[SCAMPER:Modify]`, `[SCAMPER:PutToOther]`, `[SCAMPER:Eliminate]`, `[SCAMPER:Reverse]` |
| 02 Perspective | `[Hat:White]`, `[Hat:Red]`, `[Hat:Black]`, `[Hat:Yellow]`, `[Hat:Green]`, `[Hat:Blue]`, `[Stakeholder:{name}]`, `[Role:Novice]`, `[Role:Sceptic]`, `[Role:Regulator]`, `[Role:CultureOutsider]`, `[Role:Child]`, `[Role:Competitor]`, `[Analog:{field-name}]` |
| 03 Inversion | `[Munger-Jacobi]`, `[Premortem:Tech]`, `[Premortem:Reliability]`, `[Premortem:Semantic]`, `[Reverse]` |
| 04 Causal | `[5Whys:chain{n}:L{level}]`, `[Systems:Stock]`, `[Systems:Flow]`, `[Systems:Balancing]`, `[Systems:Reinforcing]`, `[Systems:Delay]`, `[Systems:Emergent]`, `[TRIZ:Technical]`, `[TRIZ:Physical]` |
| 05 Temporal-scale | `[Time:Past]`, `[Time:Present]`, `[Time:Future]`, `[Scale:Individual]`, `[Scale:Team]`, `[Scale:Org]`, `[Scale:Industry]`, `[Scale:Society]`, `[Scale:Civilization]`, `[Scale:Short]`, `[Scale:Long]`, `[Scale:Local]`, `[Scale:Global]`, `[Scale:Micro]`, `[Scale:Macro]`, `[PhaseTransition]` |
| 06 Assumptions | `[FirstPrinciples]`, `[Assumption]`, `[BlindSpot]` |
| 07 Field intel | `[Experts]`, `[Books]`, `[Conferences]`, `[Papers]`, `[Communities]` |
| 08 Adjacent | `[Adjacent:{field-name}]` — field names free-form (e.g. `[Adjacent:biology]`, `[Adjacent:architecture]`) |
| 09 Meta | `[Framing]`, `[Taboo]`, `[Dissolution]`, `[Power]`, `[Epistemology]`, `[MethodReflection]` |

---

## Length expectations

| Agent | quick | standard | deep |
|--|--|--|--|
| 01 Structural | 20–30 Qs | 30–50 Qs | 50–80 Qs |
| 02 Perspective | 25–35 | 35–55 | 55–85 |
| 03 Inversion | 20–30 | 30–45 | 45–70 |
| 04 Causal | 20–30 | 30–45 | 45–70 |
| 05 Temporal-scale | 20–30 | 30–45 | 45–70 |
| 06 Assumptions | 20–30 | 30–45 | 45–70 |
| 07 Field intel | 20–30 | 30–45 | 45–65 |
| 08 Adjacent | 15–25 | 20–30 | 30–45 |
| 09 Meta | 15–25 | 20–30 | 30–45 |
| **Raw total** | **~175–265** | **~255–390** | **~390–600** |
| 10 Audit — gaps + top-10 + dup flags | short report | short report | short report |
| Synthesis — deduplicated total | 80–150 | 120–220 | 180–320 |
| Synthesis — clusters | 8–10 | 8–12 | 10–12 |
| Synthesis — Frontier Questions | 10 | 10 | 10 |

Deduplication ratio of ~2:1 from raw → Synthesis is expected; higher dedup ratios signal strong cross-method confirmation.
