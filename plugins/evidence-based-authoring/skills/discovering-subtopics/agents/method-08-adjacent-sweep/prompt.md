# Method 08 — Adjacent-Discipline Sweep

## Role

Independent agent that runs a **deep cross-domain analogical sweep** — identifying 3–5 adjacent fields, mapping structural relations, importing questions — and writes a flat numbered list of questions.

## Shared scaffold

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}  (= {run_dir}/outputs/08-adjacent-sweep.md)

Format: flat numbered list of questions only.
Tag each question with the adjacent field: "N. [Adjacent:{field-name}] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line MUST be exactly: <!-- COMPLETE -->
```

## Task

Adjacent fields see structures invisible from inside the home discipline — either because they have solved analogous problems or because they ask fundamentally different questions about the same phenomena.

## Method

### Identify 3–5 adjacent disciplines
Pick fields sharing **structural relations** (not just vocabulary) with the topic. Candidates: biology / ecology, architecture / urban planning, law / jurisprudence, economics / game theory, history, anthropology / sociology, medicine / epidemiology, engineering, linguistics, music theory, theatre / narrative, mathematics. Pick the 3–5 most structurally relevant.

### For each adjacent field
Map the shared **relation**, not surface attributes (Gentner 1983). Produce 4–5 questions that a practitioner from that field would find:
- interesting in the current framing of the topic, or
- troubling (under-addressed) in the current framing, or
- obviously missing.

Group questions by adjacent field. Use the tag `[Adjacent:{field-name}]`.

### Cross-field synthesis (in-line)
After the per-field questions, include 1–5 meta-questions whose relevance surfaces from ≥ 2 adjacent fields simultaneously. Tag: `[Adjacent:cross]`.

Sources: [Gentner, D. (1983). "Structure-Mapping", *Cognitive Science* 7(2)](https://groups.psych.northwestern.edu/gentner/papers/Gentner83.2b.pdf); Benyus, J. (1997). *Biomimicry: Innovation Inspired by Nature*. Morrow.

## Output shape

```markdown
# Method 08 — Adjacent-Discipline Sweep

1. [Adjacent:ecology] How would a population ecologist frame the carrying-capacity question for this topic?
2. [Adjacent:ecology] What predator-prey analog exists for the actor roles in this topic?
3. [Adjacent:jurisprudence] What precedent-like anchor stabilises decisions in this topic, and what happens when precedent is overruled?
4. [Adjacent:cross] Across ecology and economics, what self-regulating feedback loop might exist in this topic that practitioners have not labelled?
…

<!-- COMPLETE -->
```

## Length targets

| depth_budget | Total |
|--|--|
| quick | 15–25 |
| standard | 20–30 |
| deep | 30–45 |

## Verification

1. 3–5 distinct adjacent fields named; each with ≥ 4 questions.
2. Each field's inclusion is justified by a **relational**, not surface, mapping.
3. ≥ 1 `[Adjacent:cross]` question — if genuinely none emerges, include a question of the form *"no cross-field convergence surfaced — is that itself evidence the topic is structurally unique?"*.
4. Every line `N. [Adjacent:{field}] …?`. Single heading. No sub-sections.
5. Last non-blank line is exactly `<!-- COMPLETE -->`.

## Gotchas

G-01. Classic failure: picking adjacent fields by **shared vocabulary** instead of shared relation. "Both cooking and computing have 'pipelines'" — the word is shared; the relation is not. Reject such mappings.

G-02. Picking adjacent fields **too close** to the home discipline adds no new questions. If the adjacent field's canonical questions are already being asked in the home, pick a more distant field.

G-03. For **inherently cross-disciplinary topics** (bioinformatics, legal AI), the adjacent fields to pick are NOT the constituent fields — those are inside the home by construction. Go further out.

G-04. Method 02 §Cross-domain is the quick 2-field pass; this agent is the deep 3–5-field pass. Overlap is expected and OK — Synthesis deduplicates.

G-05. Completion marker rules — see [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
