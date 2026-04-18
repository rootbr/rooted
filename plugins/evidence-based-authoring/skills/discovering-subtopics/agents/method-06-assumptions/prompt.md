# Method 06 — Hidden Assumptions

## Role

Independent agent that runs **First Principles + Assumption Mapping + Blind-Spot Probe** on a topic and writes a flat numbered list of questions.

## Shared scaffold

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}  (= {run_dir}/outputs/06-assumptions.md)

Format: flat numbered list of questions only.
Tag each question with the sub-technique: "N. [Tag] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line MUST be exactly: <!-- COMPLETE -->
```

## Task

Make the invisible visible. What does the topic silently take for granted? What bedrock truths does it depend on? What does the field systematically fail to ask about itself? No repetition across sub-techniques.

## Method

### First principles
Identify 5–7 assumptions so foundational the topic cannot exist without them. For each, produce questions of the form:
- *What if this is false? What would have to change?*
- *Is this bedrock or derivable from something more basic?*

Tag: `[FirstPrinciples]`.

Sources: Aristotle, *Posterior Analytics* (Book I); Descartes, *Discourse on the Method* (1637), Part II.

### Assumption mapping
List 8–12 things taken for granted about the topic — **especially the ones the canonical source does not flag as assumptions**. Categories:
- Definitional ("X is well-defined")
- Stability ("this does not change between observation and action")
- Availability ("this input / resource / cooperation is available")
- Behavioural ("actors behave rationally / predictably / in good faith")
- Environmental ("background conditions remain normal")
- Epistemological ("we can measure / verify / reproduce")

For each, generate the question that its **operational negation** would raise.

Tag: `[Assumption]`.

Source: VanGundy, A. B. (1988). *Techniques of Structured Problem Solving*. Van Nostrand Reinhold; rooted in Osborn, *Applied Imagination* (1953).

### Blind-spot probe
What questions does the field consistently **fail to ask about itself**? What is systematically ignored because it is inconvenient, destabilising, or outside accepted scope? Produce 5–8 questions.

Candidate directions: questions about the field's own track record of error; questions about who the field excludes from its conversations; questions the field treats as settled but actually circulates unresolved; questions whose answers would require the field to reorganise.

Tag: `[BlindSpot]`.

## Output shape

```markdown
# Method 06 — Hidden Assumptions

1. [FirstPrinciples] …?
2. [Assumption] …?
3. [BlindSpot] …?
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

1. First principles: ≥ 5 bedrock assumptions identified; each yields at least one question. Items that are still derivable are not bedrock — drill further.
2. Assumption mapping: ≥ 8 items listed, spanning at least 4 of the 6 categories (definitional / stability / availability / behavioural / environmental / epistemological).
3. Blind-spot probe: ≥ 5 questions, each clearly about the field's self-examination (not about the topic content).
4. Every line `N. [Tag] …?`. Single heading. No sub-sections.
5. Last non-blank line is exactly `<!-- COMPLETE -->`.

## Gotchas

G-01. **First principles applied to humanities or consensus-driven fields** often bottoms out in contested axioms. Record that contestation as a question ("which of these competing axioms is the field quietly assuming?") rather than pretend the bedrock is settled.

G-02. **Assumption mapping** fails when the agent only lists assumptions the canonical source already labels as assumptions. The flagship output is the **unflagged** ones. Look for claims phrased as facts, definitions, or "obvious" observations.

G-03. **Operational** negation matters. "X always holds" negates to "X sometimes does not hold", not to "X is forbidden". Operational negation keeps the derived question meaningful.

G-04. **Blind-spot probe** overlaps with method 09 (Meta-questions) on framing and taboo. This agent works at the **assumption / claim** level; method 09 works at the **framing / power** level. Overlaps are OK — Synthesis merges.

G-05. Method 03 (Inversion) also produces assumption-like questions via negation. Cross-validation at Synthesis is expected; do not deduplicate here.

G-06. Completion marker rules — see [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
