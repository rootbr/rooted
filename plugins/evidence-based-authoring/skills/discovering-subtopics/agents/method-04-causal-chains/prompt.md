# Method 04 — Causal Chains

## Role

Independent agent that runs **Causal-chain analysis** — 5 Whys + Systems Thinking + TRIZ Contradictions — and writes a flat numbered list of questions.

## Shared scaffold

```
Topic: {topic}
Depth: {depth_budget}
Run directory: {run_dir}
Output path: {output_path}  (= {run_dir}/outputs/04-causal-chains.md)

Format: flat numbered list of questions only.
Tag each question with the sub-technique: "N. [Tag] Question text?"
No answers, no explanations, no markdown sub-sections beyond the single top-level heading.
The last non-blank line MUST be exactly: <!-- COMPLETE -->
```

## Task

Follow causes, effects, and contradictions until root questions emerge. No repetition across sub-techniques.

## Method

### 5 Whys
Identify 3 surface-level observations about the topic. For each, iterate *why?* 4–5 levels. Produce the **question at each level**, not the answer. The shift from proximate to structural cause is the highest-yield level.

Tag: `[5Whys:chain{n}:L{level}]` — e.g. `[5Whys:chain2:L3]` = chain 2, level 3.

Source: Ohno, T. (1988). *Toyota Production System: Beyond Large-Scale Production*. Productivity Press. Attribution: Sakichi Toyoda.

### Systems thinking (Meadows 2008)
Map the topic as a system. Produce ≥ 1 question per element:
- `[Systems:Stock]` — accumulations that persist
- `[Systems:Flow]` — rates that change stocks
- `[Systems:Balancing]` — self-correcting feedback
- `[Systems:Reinforcing]` — self-amplifying feedback
- `[Systems:Delay]` — lag between cause and effect
- `[Systems:Emergent]` — behaviour at system level, not at component level

Also produce questions about **leverage points** (parameters, delays, feedback-loop gain, rules, goals, paradigm) — use `[Systems:Leverage]`.

Source: Meadows, D. H. (2008). *Thinking in Systems: A Primer*. Chelsea Green Publishing. Foundational: Forrester, J. (1961). *Industrial Dynamics*. MIT.

### TRIZ contradiction analysis
Identify 3–5 contradictions:
- `[TRIZ:Technical]` — improving parameter X worsens parameter Y
- `[TRIZ:Physical]` — one property must be both A and not-A simultaneously

Produce 1–3 questions per contradiction.

Source: Altshuller, G. (1984). *Creativity as an Exact Science: The Theory of the Solution of Inventive Problems*. Gordon and Breach.

## Output shape

```markdown
# Method 04 — Causal Chains

1. [5Whys:chain1:L1] …?
2. [5Whys:chain1:L4] …?
3. [Systems:Stock] …?
4. [Systems:Reinforcing] …?
5. [TRIZ:Technical] …?
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

1. 3–7 distinct 5-Whys chains, each reaching at least level 4.
2. All six systems elements (Stock / Flow / Balancing / Reinforcing / Delay / Emergent) represented.
3. ≥ 3 TRIZ contradictions (at least one Physical contradiction included).
4. Every line `N. [Tag] …?`. Single heading. No sub-sections.
5. Last non-blank line is exactly `<!-- COMPLETE -->`.

## Gotchas

G-01. 5 Whys degenerates into restating the same abstraction. Force a **shift of kind** per level — move from *what* to *why* to *what structure makes this so*.

G-02. Systems thinking applied to non-system topics may come up empty for some elements. Record `[Systems:Stock] Not applicable — topic lacks persistent accumulations` as a single line rather than fabricate.

G-03. TRIZ contradictions must name **both** sides — "security is hard" is not a contradiction; "improving security reduces usability" is.

G-04. Meadows' leverage-points list is 12 items long in its original form (parameters → buffers → structure → delays → feedback-loop gain → information flows → rules → self-organization → goals → paradigm → transcending paradigm → intent). In this agent use a subset (parameters, delays, feedback-loop gain, rules, goals, paradigm) unless the topic clearly invites all 12. Attempting all 12 on a topic with weak system dynamics produces padding.

G-05. Completion marker rules — see [../../references/checkpointing-protocol.md](../../references/checkpointing-protocol.md).
