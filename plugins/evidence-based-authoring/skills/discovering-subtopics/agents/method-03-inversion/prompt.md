# Method 03 — Inversion

## Role

Independent agent that runs **Inversion** — Munger-Jacobi flip + Pre-mortem + Reverse Brainstorming — and writes a flat numbered list of questions.

## Shared scaffold

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}  (= {run_dir}/outputs/03-inversion.md)

Format: flat numbered list of questions only.
Tag each question with the sub-technique: "N. [Tag] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line MUST be exactly: <!-- COMPLETE -->
```

## Task

Negate, invert, or assume-failed before asking. Surface questions that forward thinking never reaches. No repetition across sub-techniques.

## Method

### Munger-Jacobi inversion
For each obvious aspect of the topic, flip the question. Produce 8–10 inverted questions.

- Default *how does this work?* → invert *under what conditions does it break, become false, or produce the opposite?*
- Default *how do I succeed?* → invert *how would I reliably fail?*
- Default *why is X best practice?* → invert *when was X best practice before, but has quietly stopped being so?*

Source: Munger, C. (1986). *Harvard School commencement speech* — *Invert, always invert* — attributed to Carl Jacobi.

Tag: `[Munger-Jacobi]`.

### Pre-mortem (three independent lenses)
Assume the topic has already failed catastrophically. Reconstruct questions that were never asked.

- `[Premortem:Tech]` — technical / operational failure. ≥ 3 questions.
- `[Premortem:Reliability]` — liveness, starvation, partial failure, stale data. ≥ 3 questions.
- `[Premortem:Semantic]` — *structurally correct but semantically wrong* (negative balance, double-booked slot, reversed translation, dosage-by-factor). ≥ 3 questions. **Most-skipped lens; include anyway.**

Each lens runs independently — do not merge. Repetition across lenses is NOT permitted within this agent (cross-lens repetition within one method looks like lens confusion).

Source: [Klein, G. (2007). "Performing a Project Premortem", *HBR*](https://hbr.org/2007/09/performing-a-project-premortem).

### Reverse brainstorming
Ask *how would we guarantee maximum misunderstanding or failure?* Produce 5–7 anti-answers, then invert each into a question about what prevents that failure.

Tag: `[Reverse]`.

## Output shape

```markdown
# Method 03 — Inversion

1. [Munger-Jacobi] …?
2. [Premortem:Tech] …?
3. [Premortem:Semantic] …?
4. [Reverse] …?
…

<!-- COMPLETE -->
```

## Length targets

| depth_budget | Total |
|--|--|
| quick | 20–30 |
| standard | 30–45 |
| deep | 45–70 |

## Verification

1. All three pre-mortem lenses populated (at least 3 questions each).
2. Semantic-failure lens questions are domain-specific, not generic technical ones.
3. Munger-Jacobi inversions state both the default and the inverted form implicitly; no inverted-without-anchor questions.
4. Reverse-brainstorming items derive from concrete anti-answers, not platitudes.
5. Every line `N. [Tag] …?`. Single top-level heading. No sub-sections.
6. Last non-blank line is exactly `<!-- COMPLETE -->`.

## Gotchas

G-01. Pre-mortem drifts into best-practice brainstorming. Anchor every item in *prospective hindsight* — "this HAS failed"; reject forward-conditional items.

G-02. **Semantic-failure lens** is most-skipped. For technical topics: output is structurally valid but semantically wrong. For humanities: interpretation is grammatical but misses the point. For practical-craft: process completed but outcome unusable.

G-03. Overlap with method 06 (Assumption Mapping) is **expected** — same question from different angles is cross-validation. Do NOT deduplicate against method 06; Synthesis handles it.

G-04. Do **not** aggregate clusters across the three pre-mortem lenses inside this file. Each lens produces its own questions tagged `[Premortem:Tech]` / `[Premortem:Reliability]` / `[Premortem:Semantic]`; cross-lens deduplication is Agent 10's (Duplicate Flags) and Synthesis's job. Aggregating inside this agent erases the lens attribution and defeats the three-lens design.

G-05. Completion marker rules — see [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
