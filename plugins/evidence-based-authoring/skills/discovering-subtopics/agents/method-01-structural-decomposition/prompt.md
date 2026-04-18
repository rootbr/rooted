# Method 01 — Structural Decomposition

## Role

Independent agent that runs **Structural Decomposition** — Starbursting + Morphological Analysis + SCAMPER — and writes a flat numbered list of questions.

## Shared scaffold (dispatcher fills placeholders)

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}  (= {run_dir}/outputs/01-structural-decomposition.md)

Format: flat numbered list of questions only.
Tag each question with the sub-technique that produced it: "N. [Tag] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line of your output MUST be exactly: <!-- COMPLETE -->
```

## Task

Break the topic into independent dimensions and enumerate possible states within each. Produce questions — do not answer them. Do not repeat questions across sub-techniques.

## Method

### Starbursting (5W1H)
Six question vectors. Produce 3–5 questions per vector. Primary lineage: Kipling, *Just So Stories* (1902). Tag: `[5W1H:Who]`, `[5W1H:What]`, `[5W1H:Where]`, `[5W1H:When]`, `[5W1H:Why]`, `[5W1H:How]`.

### Morphological analysis (Zwicky)
Identify 4–6 logically independent dimensions. List 3–5 values per dimension. Walk the matrix; produce one question per **non-obvious** cell (skip trivial combinations). Prefer combinations the canonical overview of the topic would not naturally address.

Source: [Zwicky, 1969, *Discovery, Invention, Research — Through the Morphological Approach*](https://www.swemorph.com/pdf/gma.pdf) (Macmillan). Tag: `[Zwicky:paramA×paramB]` with the actual parameter names.

### SCAMPER
Seven transformations. Produce 1–3 questions per transformation. Each transformation forces a distinct question class:

- `[SCAMPER:Substitute]` — what part of the topic could be replaced, and with what?
- `[SCAMPER:Combine]` — what could be merged with what inside the topic, or with an external element?
- `[SCAMPER:Adapt]` — what from a related field could be adapted here?
- `[SCAMPER:Modify]` — what if some parameter is magnified or shrunk by 10×? What changes qualitatively?
- `[SCAMPER:PutToOther]` — what other domain could use the same concept? What would the transfer look like?
- `[SCAMPER:Eliminate]` — what could be removed without losing the essential behaviour? (Removing something exposes what it was silently doing — **highest-yield transformation**; do not skip.)
- `[SCAMPER:Reverse]` — what if the flow / sequence / hierarchy is inverted?

Source: Eberle, B. (1971). *SCAMPER: Games for Imagination Development* — rooted in Osborn, *Applied Imagination* (1953).

## Output shape

```markdown
# Method 01 — Structural Decomposition

1. [5W1H:Who] …?
2. [5W1H:What] …?
3. [Zwicky:scale×domain] …?
4. [SCAMPER:Eliminate] …?
…
N. [SCAMPER:Reverse] …?

<!-- COMPLETE -->
```

## Length targets

| depth_budget | Total |
|--|--|
| quick | 20–30 |
| standard | 30–50 |
| deep | 50–80 |

## Verification (run before writing `<!-- COMPLETE -->`)

1. At least one question per 5W1H vector (all six: Who / What / Where / When / Why / How).
2. Morphological analysis: at least 4 independent parameters named, at least 8 non-obvious cells walked.
3. SCAMPER: all seven transformations represented at least once.
4. Every line starts with `N. [Tag]` and ends with `?`.
5. No duplicate questions within this agent's output.
6. Single top-level heading `# Method 01 — Structural Decomposition`; no sub-headings.
7. Last non-blank line is exactly `<!-- COMPLETE -->`.

Write the completion marker only after all checks pass.

## Gotchas

G-01. Morphological parameters must be **logically independent** — "speed" and "throughput" covary; collapse redundant dimensions before walking cells.

G-02. SCAMPER **Eliminate** is skipped most often and yields the highest-value questions; including it is required, not optional.

G-03. Starbursting is generation-only. Do not pre-answer — Synthesis and downstream methods use them as prompts.

G-04. Do not output structured sections (§1.1 / §1.2). All questions in one flat numbered list, distinguished by their bracketed tag only.

G-05. Completion marker is load-bearing for dispatcher restart. See [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
