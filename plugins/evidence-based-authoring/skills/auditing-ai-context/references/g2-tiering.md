# G2 — Token Economy & Progressive Disclosure

Sub-agent task: audit the target file's tier (hot / warm / cold) and verify its size, structure, and compression respect the budgets and the asymmetric loading rules. Output JSON patches per `../SKILL.md#patch-format`.

## Why this group matters

Working memory is finite, and the cost structure is asymmetric across tiers. Hot-tier content (CLAUDE.md / AGENTS.md) is always loaded; warm-tier (SKILL.md) is loaded only when its `description` triggers; cold-tier (reference files, schemas) is loaded only when SKILL.md says to. A rule placed in the wrong tier either consumes budget on every turn it shouldn't, or never reaches the model when it's needed.

Two non-obvious facts shape this group:

- **Long-context retention beats fact-extracted memory by 33–35 pp** (Pollertlam 2603.04814 §4.1: LoCoMo 92.85% vs 57.68%; LongMemEval 82.40% vs 49.00%). Retrieval *isn't* the default for reference material — it wins only at ~10+ reuses of ~100k-token content with caching.
- **Full-rewrite compression collapses accuracy.** ACE (Zhang 2510.04618 §2.2, Fig 2) compressed a playbook 18,282 → 122 tokens and dropped accuracy 66.7% → 57.1% — below the uncompressed baseline. Compress *format* (tables, fragments, abbreviations), not *meaning*.

---

## R-10 — Identify the tier; budget caps differ

**Statement.** Before applying any size rule, classify the file. Hot-tier (`CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md`): ≤ 200 lines / ~2,000 tokens. Warm-tier (`SKILL.md`, per-task agents): ≤ 500 lines / ~5,000 tokens. Cold-tier (reference files, schemas): no hard cap, but each file > 100 lines MUST start with a table of contents because partial-read clients (head -100) only see the top.

**Why.** Empirical baselines:

- Hot-tier qualifying triple (conventions + architecture + project description) reduces mean output tokens 20.08% and wall-clock 20.27% (Lulla 2601.20404, Codex + gpt-5.2).
- Ecosystem median SKILL.md ≈ 1.5k tokens / 2.3 KB; 95% of 601 surveyed skills stay under 5,000 tokens (Li 2602.12670 Table 6).
- SkillsBench measured Detailed +18.8pp and Compact +17.1pp gains; Comprehensive (no compression) **hurts −2.9pp**. Bigger is not better.

**How to apply.** Inspect file path and frontmatter:

| Signal | Tier |
|--|--|
| Path ends in `CLAUDE.md`, `AGENTS.md`, `copilot-instructions.md` | Hot |
| YAML frontmatter has `name:` + `description:`, path matches `**/skills/<name>/SKILL.md` or `.claude/agents/<name>.md` | Warm |
| Path is `references/`, `assets/`, `schemas/`, or referenced from SKILL.md | Cold |

Then count lines and tokens (rough: `wc -l`; tokens ≈ chars / 4). Compare to tier budget.

**Patch shape.**

```json
{
  "rule_id": "R-10",
  "location": {"section": "<whole file>", "tier": "<hot|warm|cold>"},
  "current": "<line count>/<token estimate>",
  "proposed": "Move <specific section> to <target file> to bring tier inside budget.",
  "justification": "Tier <T> budget exceeded; <section> qualifies for demotion because <reason>.",
  "severity": "medium"
}
```

---

## R-11 — Compress format, never meaning

**Statement.** Tables, fragments, abbreviations, and merged bullets are safe compressions. Paraphrasing, summarizing, or bulk-deleting accumulated bullets is not. When in doubt, append-and-refine; never wholesale-rewrite.

**Why.** ACE (Zhang §2.2, Fig 2) reproduced the collapse: a working playbook reduced from 18,282 to 122 tokens — i.e., paraphrased into "essentials" — dropped accuracy from 66.7% to 57.1%, below the uncompressed *baseline*. Each removed bullet was a load-bearing failure-mode reminder; the paraphrase looked tighter but had lost the operational specifics.

**How to apply.** When proposing a compression patch, classify:

| Type | Safe? | Example |
|--|--|--|
| Bullet → table cell | yes | "Frontmatter must be ≤ 1024 chars" → row in a table |
| Bullet → fragment | yes | "You should make sure to lock numeric thresholds" → "Lock numeric thresholds" |
| Long word → short synonym | yes | "in order to" → "to" |
| Two bullets stating one rule → one bullet | yes | merging only when *exact* duplicate (see R-43) |
| Paraphrase rewrite of accumulated playbook | no | "rewrite tighter" — refuse |
| Bulk-delete bullets to hit a token target | no | refuse, propose tier demotion instead |

**Bad → Good.**

```
bad:  "Make sure to always use the appropriate tier for context content in
       order to ensure efficient token utilization."
good: "Tier content by access frequency."

bad (rewrite):  "Be brief and focused."
                (replacing 12 bullets that captured the bundling tax)
good (refine):  keep the 12 bullets, refactor into a 3-column table
```

**Patch shape.**

```json
{
  "rule_id": "R-11",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<verbose excerpt>",
  "proposed": "<format-compressed excerpt with same propositional content>",
  "justification": "Format compression only; no propositional content removed.",
  "severity": "low"
}
```

---

## R-12 — State each fact once; cross-link within the file

**Statement.** Distinct propositions appear once. Subsequent mentions refer by rule ID or section name. See G4 R-43 for the audit procedure; this rule exists in G2 because *the motivation* — token budget — is a Token Economy concern.

**Why.** Duplicated rules eat slots in the model's attention budget without delivering distinct signal; bundling tax (Yang 2505.13360 §3.4) shows that adding a rule does not "squeeze in" but displaces.

**Patch reference.** Apply via R-43 in G4 — this entry is here purely to point sub-agents at the canonical anti-duplication rule rather than re-implementing it under a different ID. **Do not emit duplicate patches** if G4 already reports the same issue; the main agent dedupes by `(rule_id, location)`.

---

## R-13 — Hot tier MUST cover the qualifying triple

**Statement.** A hot-tier file (CLAUDE.md / AGENTS.md / copilot-instructions.md) must contain three classes of content: (i) **conventions and best practices**, (ii) **architecture and project structure**, (iii) **project description**. Lulla 2601.20404 found this triple to be the minimum that produces the 20.08% mean-output-token reduction; partial triples regress.

**How to apply.** For a hot-tier file, classify each section:

- Conventions: naming, formatting, tooling, lint rules, commit style.
- Architecture: data flow, layering, key components, integration points.
- Project description: what the repo *is*, who uses it, the goal.

Any class missing → flag with a proposed section skeleton.

**Patch shape.**

```json
{
  "rule_id": "R-13",
  "location": {"file": "<path>", "tier": "hot"},
  "current": "Missing: <conventions | architecture | project_description>",
  "proposed": "Add section: ## <Section Name>\\n<3-line bullet skeleton>",
  "justification": "Qualifying triple incomplete; Lulla 2601.20404 baseline requires all three.",
  "severity": "medium"
}
```

---

## R-14 — Warm tier MUST keep load-bearing rules near the top

**Statement.** Hong 2025 Context Rot established that retrieval accuracy drops as position moves later in the input — and the effect compounds with input length. For SKILL.md files, place safety rules, routing triggers, MUSTs, and "before any other step" instructions in the first ~30% of the file. Counter-intuitively, *shuffled or discrete* content beats logically structured prose for reference material — "structural coherence consistently hurts model performance" (Hong 2025).

**Why.** Two phenomena combine: positional decay (later content is weighted less by attention) and prose flow (narrative tends to bury load-bearing rules behind context-setting paragraphs).

**How to apply.** For each MUST / SHALL / safety rule in the file, record its line position. Compute `position_pct = line / total_lines`. Any load-bearing rule with `position_pct > 0.30` is a candidate; propose moving it up or repeating it in a top-of-file summary block.

**Patch shape.**

```json
{
  "rule_id": "R-14",
  "location": {"section": "<heading>", "line_hint": <int>, "position_pct": <float>},
  "current": "<rule sentence>",
  "proposed": "Hoist to: ## Quick Rules section near top; keep canonical body in <current section>.",
  "justification": "Load-bearing rule positioned at <pct>% — retrieval decays past ~30% (Hong 2025).",
  "severity": "medium"
}
```

---

## R-15 — Single-shot artifact outputs MUST be decomposed when > ~230 tokens

**Statement.** Skills that demand one large generated artifact in a single response are fragile. Liang 2410.21647 §4.2 measured GPT-4o pass@1 collapsing below 10% when single-shot output exceeded ~230 tokens. Decompose into bounded outputs or iterative edits.

**Why.** The same paper traced the collapse to attention-budget contention between maintaining the constraint set and generating long structured output simultaneously. Bounded outputs let the model re-read constraints between segments.

**How to apply.** Search the skill body for instructions of the form "produce a complete X", "write the full Y", "generate the entire Z" where X/Y/Z is plausibly > 230 tokens. For each: propose decomposition — bounded sections, per-step outputs, or iterative-edit phrasing.

**Bad → Good.**

```
bad:  "Generate the full README in one response."
good: "Generate the README outline first. Then fill each section one at a time."
```

**Patch shape.**

```json
{
  "rule_id": "R-15",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<single-shot artifact instruction>",
  "proposed": "<decomposed instruction with bounded steps>",
  "justification": "Single-shot output >230 tokens collapses pass@1 below 10% (Liang 2410.21647 §4.2).",
  "severity": "medium"
}
```

---

## R-16 — History growth MUST be bounded: summarize or truncate past ~20 turns

**Statement.** Transcripts grow O(T²) in tokens because each turn re-encodes prior turns. Past ~20 turns, "context rot" sets in (Tokalator 2604.08290 §3.4). For skills that manage conversational state or store transcripts, prescribe summarization or window-based truncation.

**How to apply.** Grep for "transcript", "history", "all prior turns", "full conversation". Each usage either:

- Names an explicit summarization / truncation policy → keep.
- Implies unbounded retention → flag.

**Patch shape.**

```json
{
  "rule_id": "R-16",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<unbounded-history instruction>",
  "proposed": "<same instruction with explicit window / summarization policy>",
  "justification": "Unbounded history grows O(T²); rot past ~20 turns (Tokalator §3.4).",
  "severity": "medium"
}
```

---

## R-17 — Observations: prefer masking and pointer-IDs over LLM summarization

**Statement.** Runtime tool outputs consume ~84% of agent tokens (Lindenbauer 2508.21433 §1). Three structural mechanisms beat semantic rewrites:

| Mechanism | Token cut | Overhead |
|--|--|--|
| Masking stale observations | 50.9–57.1% | none |
| LLM summarization | 41.5–55.4% | 2.86–7.20% summary pass |
| Pointer-ID (return handle, agent dereferences) | up to 16,900× and 7× in two case studies (Bulle Labate 2511.22729 §3) | none |

Favor masking and pointer-IDs.

**How to apply.** For skills whose tools return large blobs:

- If the tool currently inlines the blob → propose returning a handle / path the agent reads on demand.
- If the skill instructs the model to "summarize the output" → flag, propose masking-by-recency or pointer-ID.

**Patch shape.**

```json
{
  "rule_id": "R-17",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<observation-handling instruction>",
  "proposed": "<masking / pointer-ID instruction>",
  "justification": "Structural observation management cheaper than semantic summarization (Lindenbauer §1; Bulle Labate §3).",
  "severity": "low"
}
```

---

## R-18 — Hot-tier inclusion beats retrieval for content reused in-session

**Statement.** Long-context retention outperforms fact-extracted retrieval by 33–35 pp on accuracy (Pollertlam §4.1). Retrieval pays off only at ~10+ reuses of ~100k-token content with caching. Prefer hot/warm inclusion for anything used within a session; reserve MCP / search for rarely-touched specs.

**How to apply.** When the file recommends "retrieve from <vector store>" or "look up in <RAG index>" for content reused within typical sessions, flag — propose moving the content into a cold-tier file referenced from SKILL.md. Conversely, content with truly low reuse and large volume (full API specs, schemas referenced ad hoc) belongs in cold tier or external retrieval.

**Patch shape.**

```json
{
  "rule_id": "R-18",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<retrieval-based instruction>",
  "proposed": "<inclusion-based instruction>",
  "justification": "Reuse pattern below retrieval break-even; long-context retention wins by 33–35 pp (Pollertlam §4.1).",
  "severity": "low"
}
```

---

## R-19 — Static lists of project state MUST be replaced by discovery commands

**Statement.** Same as R-45 in G4 — listed here because the *motivation* is token economy: an inventory of 30 plugins burns 30 lines of warm-tier budget per invocation. The fix is shared. Sub-agent should not emit two patches for the same violation; if G4 reports R-45, G2 omits.

---

## Output protocol for this sub-agent

1. Determine the tier from file path and frontmatter.
2. Measure line and token count first — record in a `meta` field of the first patch (`meta: {tier, lines, tokens_est}`) so the aggregator has a budget read-out.
3. Walk the file; emit patches in file order.
4. Defer to G4 on R-43 (state-once) and R-45 (inventory replacement); do not re-emit.
