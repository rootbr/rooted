# Synthesis

## Role

Independent agent that runs **after Agent 10 (Coverage Audit) completes**. Reads all ten outputs (01–09 + 10) and writes the reader-facing question map to `{run_dir}/{topic-slug}-questions.md` with a completion marker.

## Shared scaffold (adapted for Synthesis)

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {run_dir}/{topic-slug}-questions.md
Inputs to read: {run_dir}/outputs/01-*.md through {run_dir}/outputs/10-*.md (all ten)

Synthesis uses a STRUCTURED output shape (Overview / Questions by Dimension / Frontier / Open Terrain).
Drop the per-question [Tag] and (Agent N) attribution in the public report — those belong in the raw per-agent outputs.
The last non-blank line MUST be exactly: <!-- COMPLETE -->
```

## Task

Produce the reader-facing question map. This is the artifact the user reads — the raw per-agent outputs are debug material.

## Inputs

All ten files under `{run_dir}/outputs/`:
- 01 through 09 — flat numbered question lists with `[Tag]` attribution
- 10 — structured audit (Gaps Found, Most Important Questions, Duplicate Flags, Partial Agents)

If Agent 10's **Partial Agents** section is non-empty, record the partial coverage in the Overview paragraph and proceed.

## Method

### Step S.1 — Merge and deduplicate

Pull every question from 01–09 and from 10's Gaps-Found section. For every pair flagged in 10's Duplicate Flags, merge into the **stronger formulation**:
- Clearer grammar wins over looser
- More concrete object wins over generic
- More pointed framing wins over diffuse
- If both are equally good, pick the one whose phrasing carries more information

### Step S.2 — Cluster into 8–12 thematic dimensions

Group deduplicated questions into 8–12 clusters. **Cluster names describe dimensions, not methods.** Reject names like "Inversion questions" or "Temporal questions"; prefer names like "Failure modes", "Historical evolution", "Stakeholder concerns", "Scale transitions", "Adjacent-field analogs", "Assumptions & blind spots", "Meta-framing".

Within each cluster, order questions **foundational → advanced**: entry-level first, mastery-requiring last.

### Step S.3 — Select Frontier Questions

Pick 10 questions whose answers would most change how someone understands the topic. These may overlap with Agent 10's Most Important Questions, but Synthesis is free to promote or demote based on cluster-level context. Provide a one-sentence rationale per frontier question.

### Step S.4 — Name Open Terrain

Dimensions still underexplored **after** Agent 10's Gap-fills were integrated. These are the remaining gaps — the frontier beyond the frontier. For each, give a one-sentence reason it is hard to question.

### Step S.5 — Write the Overview paragraph

One paragraph covering:
- Total questions generated across all agents (raw count from 01–09)
- Total deduplicated questions in this report
- Number of clusters
- The 3 most unexpected question clusters (by whatever heuristic: newly named dimensions, cross-validated from ≥ 3 methods, or flagged by Agent 10)
- Any dimensions Agent 10 flagged as under-covered that still appear in Open Terrain

## Output shape

```markdown
# Question Map: {Topic}

## Overview
{One paragraph per Step S.5.}

## Questions by Dimension

### {Cluster 1 name — describes dimension}
1. {question}
2. {question}
…

### {Cluster 2 name}
1. {question}
…

(8–12 clusters. Ordered foundational → advanced within each. No tags, no agent attribution.)

## Frontier Questions
> Ten questions whose answers would most change understanding of the topic.

1. {question} — {one-sentence rationale}
2. {question} — {rationale}
…
10. {question} — {rationale}

## Open Terrain
> Dimensions still underexplored after all agents ran.

- {gap name}: {one-sentence reason this gap is hard to question}
- {gap name}: …

---

*Raw per-agent outputs: {run_dir}/outputs/. Coverage audit: {run_dir}/outputs/10-coverage-audit.md.*

<!-- COMPLETE -->
```

## Length targets

| depth_budget | Deduplicated total | Clusters | Frontier | Open Terrain |
|--|--|--|--|--|
| quick | 80–150 | 8–10 | 10 | 3–6 |
| standard | 120–220 | 8–12 | 10 | 4–8 |
| deep | 180–320 | 10–12 | 10 | 5–10 |

Deduplication ratio of ~2:1 from raw → Synthesis is expected.

## Verification

1. All ten inputs actually read — evidence: questions traceable to each agent appear in the clusters (even though the report hides attribution, Synthesis must have consumed them).
2. 8–12 thematic clusters; cluster names describe dimensions, not methods.
3. Within each cluster, questions ordered foundational → advanced.
4. **Frontier Questions** has exactly 10 entries, each with a one-sentence rationale.
5. **Open Terrain** names the remaining gaps and explains why each is hard.
6. No `[Tag]` or `(Agent N)` attribution anywhere in the report (they live in raw outputs).
7. Overview paragraph names totals, cluster count, and the 3 most unexpected clusters.
8. Last non-blank line is exactly `<!-- COMPLETE -->`.

## Gotchas

G-01. **Cluster naming is the hardest single step**. A method-named cluster ("Inversion questions") is a failed cluster — it reveals that the synthesis did not actually synthesise, it just grouped by origin.

G-02. **Deduplication is aggressive**. Near-duplicates from Agent 10's Duplicate Flags MUST be merged. Same question surfaced from 3 methods is one entry in the report (but a signal worth noting in the Overview paragraph as cross-validated).

G-03. Frontier Questions are NOT "the 10 hardest questions". They are questions whose answers would **most change understanding**. A hard question no one cares about is not frontier.

G-04. Open Terrain is NOT the same as Agent 10's Gaps Found. Agent 10's gaps are filled by its own generated questions (which Synthesis then integrates into clusters). Open Terrain is what remains **after** those fill-ins — the gaps the skill cannot close on its own.

G-05. If Agent 10's Partial Agents section is non-empty, explicitly mention in the Overview that coverage is incomplete and which agents need re-running.

G-06. Completion marker rules — see [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
