# Method 09 — Meta-Questions

## Role

Independent agent that generates **meta-questions** about a topic's structure, history, and framing — not its content — and writes a flat numbered list of questions.

## Shared scaffold

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}  (= {run_dir}/outputs/09-meta-questions.md)

Format: flat numbered list of questions only.
Tag each question with the sub-technique: "N. [Tag] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line MUST be exactly: <!-- COMPLETE -->
```

## Task

Ask questions about the topic's framing, not its content. No repetition across sub-techniques.

Grounded in Paul & Elder's sixth Socratic type ("question about the question"). Source: [Paul, R. & Elder, L. (2006). *The Thinker's Guide to Socratic Questioning*](https://www.criticalthinking.org/files/SocraticQuestioning2006.pdf). Critical-systems framing: Ulrich, W. (1983). *Critical Heuristics of Social Planning*.

## Method

Produce 3–5 questions per sub-prompt.

### `[Framing]` — Framing history
How has the topic been defined over time? What was included or excluded by each major framing? Who decided? What was it called before it was this? Which once-dominant framings were abandoned, and why?

### `[Taboo]` — Taboo and suppressed questions
What questions are considered premature, dangerous, or outside acceptable scope? Why, and for whom? What questions are publicly unspeakable but privately common among practitioners?

### `[Dissolution]` — Dissolution conditions
What would make the topic irrelevant, obsolete, or revealed as a false problem? What discovery would dissolve it? What alternative framing would subsume it as a special case?

### `[Power]` — Power and framing
Who benefits from the current framing, and who does not? Whose professional identity depends on the current framing holding? Whose interests would be served by an alternative framing?

### `[Epistemology]` — Epistemology
How does this field decide what counts as knowledge? What evidence is privileged or dismissed? What findings are repeated without re-verification long after they should have been re-tested?

### `[MethodReflection]` — Method reflection
How should this topic be studied? What method is being assumed when we study it? What methods from other disciplines have NOT been tried on this topic, and why?

## Output shape

```markdown
# Method 09 — Meta-Questions

1. [Framing] How was this topic defined before the current consensus, and who decided to abandon that earlier framing?
2. [Taboo] What question, if asked publicly at a flagship conference, would be immediately deflected by the chair?
3. [Dissolution] What single empirical discovery would make this topic's central concern vanish?
4. [Power] Whose livelihood depends on the current framing, and how do they defend it?
5. [Epistemology] What evidence does this field treat as axiomatic that another adjacent field would treat as in need of proof?
6. [MethodReflection] What would the topic look like if we applied ethnography where quantitative methods dominate?
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

1. All six sub-prompts (Framing / Taboo / Dissolution / Power / Epistemology / MethodReflection) populated.
2. Questions are **about the framing**, not content. Reject any "how does X work?" — that belongs in methods 1–8.
3. **Taboo** slot is non-empty — if no taboo surfaces naturally, search "controversies in {topic}" and extract from there.
4. **Dissolution** items are inquiries ("under what conditions would…?"), not predictions.
5. Every line `N. [Tag] …?`. Single heading. No sub-sections.
6. Last non-blank line is exactly `<!-- COMPLETE -->`.

## Gotchas

G-01. Meta-questions drift into content-questions. Test each: *is this about how the topic is framed, studied, or maintained? Or about what the topic is made of?* Only the former belongs here.

G-02. The **Power** prompt reads as politically loaded but is methodologically essential. Keep the analysis descriptive, not advocative.

G-03. **Dissolution** is surprisingly hard. If stuck, try: *if the topic didn't exist, what need would go unmet? If that need were met differently, what would the topic become?*

G-04. Method 06 `[BlindSpot]` works at the assumption / claim level; this method's `[Framing]` and `[Taboo]` work at the framing / power level. Overlap is expected and OK — Synthesis merges.

G-05. Completion marker rules — see [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
