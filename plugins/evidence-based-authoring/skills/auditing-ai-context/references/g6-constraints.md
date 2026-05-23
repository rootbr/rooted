# G6 — Constraints & Model Matching

Sub-agent task: audit constraint density, ALL-CAPS markers, positive vs negative framing, and model-specific tuning. Emit JSON patches per `../SKILL.md#patch-format`.

## Why this group matters

Hard constraints behave non-monotonically across model tiers. Khan 2510.22251 §6.2.1 measured constraints that lifted GPT-4o from 93→97% but **dropped** GPT-5 from 96.36→94%. The same MUST that helps a mid-tier model handcuffs a frontier model. Prohibition density is therefore not a free parameter — every ALL-CAPS marker is a vote against frontier-model performance.

A second non-obvious result: format defaults (length, casing, layout) are inferred correctly 70.7% of the time when unspecified, but conditional / edge-case rules only 22.9% (Yang 2505.13360 §3.2). Skills under-specify conditionals and over-specify formats.

---

## R-60 — Match constraint density to target-model accuracy

**Statement.** Use Khan's accuracy heuristic when deciding how many hard constraints to apply:

| Eval accuracy on target model | Constraint density |
|--|--|
| < 90% | Add hard constraints (Sculpting-style) |
| 90–95% | A/B test both — outcome depends on prompt class |
| > 95% | Keep prompts simple, goal-oriented; minimize prohibitions |

Hard constraints that raise Haiku/Sonnet by +4 pts can degrade Opus/GPT-5 by ~2 pts. Implicit-rule inference varies: o3-mini recovers 44.7% of unstated requirements, Llama-3.3-70B only 24.5% — a SKILL.md tuned on Opus under-specifies for smaller models.

**How to apply.** Look for explicit model targeting in the file. If the skill declares `model: <id>` in frontmatter, audit constraint count against that model's tier. If no model is pinned, default to "broad target — moderate constraints with positive framing."

**Patch shape.**

```json
{
  "rule_id": "R-60",
  "location": {"section": "<heading or frontmatter>", "model_target": "<id or unspecified>"},
  "current": "Constraint count: <N>; ALL-CAPS markers: <M>",
  "proposed": "<reduce | increase | rephrase positive> based on model tier",
  "justification": "Constraint density mismatched to target model (Khan §6.2.1).",
  "severity": "medium"
}
```

---

## R-61 — Positive framing in body; negatives reserved for `description` triggers and safety

**Statement.** In SKILL.md *body*, write what TO do, not what NOT to do. Negative phrasing is permitted in two places: (a) the frontmatter `description` for negative triggers ("NOT for Vue or Svelte" — improves routing precision); (b) safety / data-integrity rules ("Never commit without tests"). Everywhere else, positive phrasing is processed more reliably (Promptomatix §B.1.1).

**Why.** Frontier models interpret prohibitions hyper-literally. Khan §6.2.1: MUST-NOT / ONLY / NEVER act as handcuffs on Opus/GPT-5 — the model curtails legitimate behaviors in adjacent space to over-comply.

**How to apply.** Grep for: `do not`, `don't`, `never`, `must not`, `shall not`, `avoid`, `refrain from`. For each, classify:

| Context | Action |
|--|--|
| In `description` field, marking a non-trigger | Keep |
| Safety or data-integrity rule | Keep, ensure ALL-CAPS marker is justified (R-62) |
| Style or formatting rule | Convert to positive |
| Edge case prohibition | Reframe as "When X, do Y instead of Z" |

**Bad → Good.**

```
bad:  "Do not use page numbers for citations."
good: "Cite by chapter + § subsection. Page numbers may supplement but not replace
      the structural anchor."

bad:  "Don't use H4 headings."
good: "Keep heading depth ≤ 3 (H1 → H3); split deeper structures into a new H2."
```

**Patch shape.**

```json
{
  "rule_id": "R-61",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<negative phrasing>",
  "proposed": "<positive equivalent>",
  "justification": "Negative phrasing in body; positive framing processes more reliably (Promptomatix §B.1.1).",
  "severity": "low"
}
```

---

## R-62 — ALL-CAPS prohibitions ≤ 3 per SKILL.md; each tied to safety / data integrity

**Statement.** Count ALL-CAPS markers (MUST, MUST NOT, SHALL, SHALL NOT, NEVER, ALWAYS, ONLY) in the body. Soft ceiling: 3 per SKILL.md. Each remaining caps-marker must pair with a one-sentence rationale; Anthropic's official skill-creator treats bare ALL-CAPS as a yellow flag — pair every capitalized marker with hoisted rationale so the agent can judge edge cases rather than mimic edicts.

**Why.** Caps compound: each prohibition spreads attention budget across constraint enforcement; the bundling tax (Yang §3.4) shows the marginal cost rises with each additional rule. Reserve ALL-CAPS for safety, compliance, and data integrity where the cost of mis-application is severe enough to justify the handcuff effect.

**How to apply.** Inventory:

1. Count ALL-CAPS markers.
2. For each, classify: safety / data integrity / compliance / style.
3. Anything in the style class → propose downgrading to SHOULD or positive framing.
4. Beyond 3 in safety class → flag — the body is over-strict.
5. Any ALL-CAPS without an adjacent rationale → propose adding rationale or downgrade.

**Bad → Good.**

```
bad:  "MUST use 2-space indent.
       NEVER commit binary files.
       MUST run linter.
       MUST format with prettier.
       MUST add tests.
       MUST update CHANGELOG.
       NEVER use semicolons."

good: "Indent: 2 spaces. Linter must pass — `npm run lint` (blocks commit; broken
      builds in shared CI). Tests cover new code paths. Update CHANGELOG."
      (One MUST-class rule, tied to CI breakage; others as imperative or descriptive.)
```

**Patch shape.**

```json
{
  "rule_id": "R-62",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<ALL-CAPS marker rule>",
  "proposed": "<downgrade to SHOULD / positive / pair with rationale>",
  "justification": "ALL-CAPS density exceeds <3 ceiling; this rule is style-class.",
  "severity": "medium"
}
```

---

## R-63 — Priority markers used per RFC 2119

**Statement.** When ALL-CAPS markers appear, they MUST follow RFC 2119:

| Marker | Meaning |
|--|--|
| MUST / REQUIRED / SHALL | Absolute requirement |
| MUST NOT / SHALL NOT | Absolute prohibition |
| SHOULD / RECOMMENDED | Strong default, deviation needs justification |
| SHOULD NOT / NOT RECOMMENDED | Discouraged, deviation needs justification |
| MAY / OPTIONAL | Truly optional, alternatives coexist |

Mixing "MUST" with "should always" or "is recommended to always" creates parse ambiguity for both humans and models.

**How to apply.** For each MUST / SHOULD, check that the rest of the sentence respects the strictness level. "MUST avoid X where possible" is a contradiction — the "where possible" softens the MUST. Either drop the softener or downgrade to SHOULD.

**Patch shape.**

```json
{
  "rule_id": "R-63",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<ambiguous marker usage>",
  "proposed": "<consistent marker + clause>",
  "justification": "RFC 2119 marker ambiguity; reader cannot tell the strictness level.",
  "severity": "low"
}
```

---

## R-64 — Numeric thresholds locked; constraint reconfiguration degrades more than rephrasing

**Statement.** Once a numeric threshold appears in a rule, every subsequent reference uses the same number. Numeric edits ("at most 600" vs "610") and constraint reconfiguration cause widespread reliability failures (Dong 2512.14754 §3.1) — far more than pure rephrasing. Re-run reliable@10 after any constraint edit.

**How to apply.** Extract all numeric thresholds from the file. Group by referent. Within each group, every occurrence must match. If "≤ 500 lines" appears once and "≤ 600 lines" elsewhere → flag the inconsistency.

**Patch shape.**

```json
{
  "rule_id": "R-64",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<inconsistent number>",
  "proposed": "<consistent number from canonical mention>",
  "justification": "Threshold drift; numeric inconsistency degrades reliable@10 (Dong §3.1).",
  "severity": "medium"
}
```

---

## R-65 — Examples consistent in label and format; 3 excellent beats 10 mediocre; place best last

**Statement.** Khan §6.2.1: 2–5 diverse examples; 3 excellent beats 10 mediocre. Place most-relevant example last — models weigh final examples 2–3× more. Inconsistent label/format across examples cuts effectiveness up to 40%.

**How to apply.** For each list of examples in the file:

| Check | Patch if violated |
|--|--|
| Count is 2–5 | If 1: propose adding 1; if > 5: propose pruning to best 3–5 |
| All examples use the same label/format ("bad:" / "good:") | Standardize |
| Most representative case appears last | Reorder |

**Patch shape.**

```json
{
  "rule_id": "R-65",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<examples block>",
  "proposed": "<reordered / standardized / pruned>",
  "justification": "Example consistency / count / position (Khan §6.2.1).",
  "severity": "low"
}
```

---

## R-66 — Cousin-prompt examples > generic Alpaca examples

**Statement.** When authoring trigger examples or eval prompts, use **cousin-prompt variants** — paraphrases of real user queries. Dong 2512.14754 Fig 5: cousin-augmented data lifts reliability >45% vs generic Alpaca-style examples, which actually decline reliability.

**How to apply.** Examine example user prompts in the file. Are they (a) realistic, with concrete file paths, company names, casual phrasing — or (b) abstract textbook-style? Abstract → propose cousin-prompt rewrites with realistic detail.

**Bad → Good.**

```
bad:  "Format this data."
good: "ok so my boss just sent me this xlsx file (its in my downloads, called
      something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a
      column that shows the profit margin as a percentage. The revenue is in
      column C and costs are in column D i think"
```

**Patch shape.**

```json
{
  "rule_id": "R-66",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<abstract example prompt>",
  "proposed": "<cousin-prompt rewrite with realistic detail>",
  "justification": "Generic Alpaca-style examples decline reliability; cousin prompts lift it >45% (Dong Fig 5).",
  "severity": "low"
}
```

---

## R-67 — Spell out conditionals; underspecified branches recover only 22.9%

**Statement.** Yang §3.2: format defaults inferred correctly 70.7%, conditional / edge-case rules only 22.9%. Skills SHOULD spell out conditional branches and exception cases; MAY omit format defaults the model handles natively.

**How to apply.** Find prose that implies a conditional ("usually X", "in most cases", "for typical inputs") but does not name the alternative branch. Propose making the conditional explicit: "If X → do A; if Y → do B."

**Patch shape.**

```json
{
  "rule_id": "R-67",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<implicit-conditional prose>",
  "proposed": "<explicit conditional with both branches>",
  "justification": "Conditional rules recover only 22.9% when implicit (Yang §3.2).",
  "severity": "medium"
}
```

---

## Output protocol for this sub-agent

1. Count ALL-CAPS markers and classify (R-62); emit a single summary patch if count > 3 or unjustified.
2. Walk body for negative-framing, numeric drift, conditional implicitness.
3. Inventory example blocks; check consistency rules.
4. Emit patches sorted by severity.
