# Method 05 — Temporal and Scale Lenses

## Role

Independent agent that applies **Temporal** and **Scale** lenses to a topic and writes a flat numbered list of questions.

## Shared scaffold

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}  (= {run_dir}/outputs/05-temporal-scale.md)

Format: flat numbered list of questions only.
Tag each question with the sub-technique: "N. [Tag] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line MUST be exactly: <!-- COMPLETE -->
```

## Task

Shift time horizon and level of magnification. Each axis produces a distinct class of questions. No repetition across sub-techniques.

## Method

### Temporal lens
Produce 3–6 questions per horizon.

- `[Time:Past]` — how did the topic emerge? What has been tried and abandoned? What paradigm shifts happened, why?
- `[Time:Present]` — what is actively contested? What consensus is fragile?
- `[Time:Future]` — where is it heading? What could change everything? What would make it obsolete?

Grounded in futures-studies practice: Bell, W. (1997). *Foundations of Futures Studies*.

### Scale-shifting lens

**Social-organizational scale ladder** — produce ≥ 1 question at each rung:
- `[Scale:Individual]` — single person / agent / unit
- `[Scale:Team]` — small coordinated group
- `[Scale:Org]` — single institution or firm
- `[Scale:Industry]` — field, sector, or professional community
- `[Scale:Society]` — national / cultural scale
- `[Scale:Civilization]` — species / civilisational scale

**Other scale axes** — produce 1–3 questions each:
- `[Scale:Short]` vs `[Scale:Long]` — short-term vs long-term
- `[Scale:Local]` vs `[Scale:Global]` — local vs global
- `[Scale:Micro]` vs `[Scale:Macro]` — micro-mechanism vs macro-pattern

**Phase transitions** — note any scale at which the topic stops being the same *kind* of thing and becomes something qualitatively different. Tag: `[PhaseTransition]`.

Nested-scale framing: Koestler, A. (1967). *The Ghost in the Machine*. Hutchinson.

## Output shape

```markdown
# Method 05 — Temporal and Scale Lenses

1. [Time:Past] …?
2. [Time:Future] …?
3. [Scale:Individual] …?
4. [Scale:Team] …?
5. [Scale:Civilization] …?
6. [Scale:Short] …?
7. [PhaseTransition] …?
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

1. All three time horizons (Past / Present / Future) populated.
2. All six rungs of the social-organisational scale ladder populated.
3. Short/Long, Local/Global, Micro/Macro axes each populated.
4. At least one `[PhaseTransition]` entry attempted — if none observed, record `[PhaseTransition] No qualitative-kind change observed across examined scales — is that itself evidence of topic rigidity?` (still a question).
5. Every line `N. [Tag] …?`. Single heading. No sub-sections.
6. Last non-blank line is exactly `<!-- COMPLETE -->`.

## Gotchas

G-01. The **Past** horizon often produces the weakest set without priming. Run `WebSearch` on "history of {topic}" or "{topic} early work" to seed historical anchors before generating.

G-02. **Future** questions are not predictions. Reject "X will happen"; keep "under what conditions would X happen?"

G-03. Scale questions default to generic ("is this harder at scale?"). Force specificity: *which scale? measured how? what breaks first?*

G-04. Scale ladder — the ladder is ORDINAL and relevant rungs may compress for some topics (a fungal-cultivation topic has little "civilisation-scale" relevance); still attempt the rung and record explicit inapplicability as its own question.

G-05. Completion marker rules — see [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
