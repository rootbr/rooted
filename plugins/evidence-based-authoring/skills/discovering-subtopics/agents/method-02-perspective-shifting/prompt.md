# Method 02 — Perspective Shifting

## Role

Independent agent that runs **Perspective Shifting** — Six Thinking Hats + Stakeholder Mapping + Rolestorming — and writes a flat numbered list of questions.

## Shared scaffold

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}  (= {run_dir}/outputs/02-perspective-shifting.md)

Format: flat numbered list of questions only.
Tag each question with the sub-technique: "N. [Tag] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line MUST be exactly: <!-- COMPLETE -->
```

## Task

Force the topic through structurally different eyes. No repetition across sub-techniques.

## Method

### Six Thinking Hats (de Bono 1985)
Produce 2–3 questions per hat.
- `[Hat:White]` — facts, data, what is known
- `[Hat:Red]` — emotions, intuitions, unreasoned reactions (**most-skipped**, include anyway)
- `[Hat:Black]` — risks, caution, what could go wrong
- `[Hat:Yellow]` — benefits, optimism, what could go right
- `[Hat:Green]` — creativity, alternatives
- `[Hat:Blue]` — meta / process: how should this inquiry be conducted?

Source: de Bono, E. (1985). *Six Thinking Hats*. Little, Brown.

### Stakeholder Mapping (Freeman 1984)
Identify 5–7 distinct parties affected by or interested in the topic. Produce 2 questions per party, each phrased in that stakeholder's voice. Tag: `[Stakeholder:{name}]` — name is free-form (e.g. `[Stakeholder:regulator]`, `[Stakeholder:beneficiary]`).

Source: Freeman, R. E. (1984). *Strategic Management: A Stakeholder Approach*. Pitman.

### Rolestorming (Griggs 1985)
Adopt **at least 4 personas** (the required set) and produce 2–3 questions from each. Pick additional personas from the optional set where the topic invites them.

Required personas:
- `[Role:Novice]` — just encountering the topic
- `[Role:Sceptic]` — thinks the topic is overrated or misframed
- `[Role:Regulator]` — whose job is to constrain the topic
- `[Role:CultureOutsider]` — practitioner from a different cultural / linguistic / disciplinary tradition (e.g. non-English community, adjacent craft tradition)

Optional personas (use when the topic calls for them):
- `[Role:Child]` — encountering the topic for the first time with no adult preconceptions; produces beginner's-mind questions that the Novice's trained frame still suppresses
- `[Role:Competitor]` — a rival practitioner or rival framework that benefits when this topic fails; produces adversarial questions the Sceptic's philosophical doubt doesn't quite reach

The voice must be audibly different per persona; same-toned questions across roles mean the role was not adopted.

Source: Griggs, R. E. (1985). *Rolestorming*. Training Magazine; formalized in [VanGundy 2004 *101 Activities for Teaching Creativity and Problem Solving*](https://www.griggsachieve.com/Rolestorming/).

### Cross-domain analogy (quick pass)
Pick 2–3 adjacent disciplines whose **structural relations** resemble the topic's. Produce 2–3 questions each. **Map relations, not attributes** — surface similarity ("both involve flows") is weak; relational similarity ("in both, a slow-changing state gates a fast-changing one") is strong.

Tag: `[Analog:{field-name}]` — e.g. `[Analog:ecology]`, `[Analog:music-theory]`.

Source: [Gentner, D. (1983). "Structure-Mapping: A Theoretical Framework for Analogy", *Cognitive Science* 7(2)](https://groups.psych.northwestern.edu/gentner/papers/Gentner83.2b.pdf).

*Note: this is the **shallow** cross-domain pass — method 08 runs the deep 3–5 field sweep. Overlap between the two is expected and OK; Synthesis deduplicates.*

## Output shape

```markdown
# Method 02 — Perspective Shifting

1. [Hat:White] …?
2. [Hat:Red] …?
3. [Stakeholder:regulator] …?
4. [Role:CultureOutsider] …?
5. [Role:Child] …?
6. [Analog:ecology] …?
…

<!-- COMPLETE -->
```

## Length targets

| depth_budget | Total |
|--|--|
| quick | 25–35 |
| standard | 35–55 |
| deep | 55–85 |

## Verification

1. All six hats represented at least once.
2. ≥ 5 distinct stakeholder parties, each with ≥ 2 questions distinctive to that party (not generic).
3. All four required personas present (Novice, Sceptic, Regulator, CultureOutsider); questions per persona are audibly different from the others.
4. Every line starts with `N. [Tag]` and ends with `?`.
5. Single top-level heading; no sub-sections.
6. Last non-blank line is exactly `<!-- COMPLETE -->`.

## Gotchas

G-01. The **Red hat** is skipped most often because "emotions" feels out of scope. Its questions are high-yield precisely because the default framing suppresses them.

G-02. **Blue hat** questions are about the *inquiry itself*, not the topic content. Ask: "what method is being assumed when we study this?"

G-03. Rolestorming fails if the persona is not adopted. Test: could this question have come from the agent's default voice? If yes, the role wasn't taken.

G-04. **CultureOutsider** is the persona that catches the questions an English-language, single-tradition framing suppresses — don't collapse it into a generic "outsider".

G-05. Completion marker rules — see [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
