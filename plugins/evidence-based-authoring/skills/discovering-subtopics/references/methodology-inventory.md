# Subtopic-Discovery Methodology Inventory

> Theory reference for the 10 methods the skill dispatches as independent agents. Every method is traceable to a primary source per the repo's evidence-based contract. Each agent prompt under `agents/method-NN-*/prompt.md` delegates "theory" to the matching section here and focuses on the task.

## Contents
- §Method index
- §1. Structural decomposition (Starbursting / Morphological / SCAMPER)
- §2. Perspective shifting (Six Hats / Stakeholder / Rolestorming / Cross-domain)
- §3. Inversion (Munger-Jacobi / Pre-mortem / Reverse brainstorming)
- §4. Causal chains (5 Whys / Systems thinking / TRIZ contradictions)
- §5. Temporal and scale lenses
- §6. Surfacing hidden assumptions (First principles / Assumption mapping)
- §7. Field intelligence (Experts / Books / Conferences / Publications / Communities)
- §8. Adjacent-discipline sweep
- §9. Meta-questions
- §10. Coverage audit
- §Invocation order and combining rules

---

## Method index

| # | Method group | Sub-techniques | Agent |
|--|--|--|--|
| 1 | Structural decomposition | Starbursting, Morphological analysis, SCAMPER | `agents/method-01-structural-decomposition/` |
| 2 | Perspective shifting | Six Thinking Hats, Stakeholder mapping, Rolestorming, Cross-domain analogy | `agents/method-02-perspective-shifting/` |
| 3 | Inversion | Munger-Jacobi inversion, Pre-mortem, Reverse brainstorming | `agents/method-03-inversion/` |
| 4 | Causal chains | 5 Whys, Systems thinking, TRIZ contradictions | `agents/method-04-causal-chains/` |
| 5 | Temporal and scale lenses | Past / present / future + micro → macro | `agents/method-05-temporal-scale/` |
| 6 | Surfacing hidden assumptions | First principles, Assumption mapping | `agents/method-06-assumptions/` |
| 7 | Field intelligence | Experts / books / conferences / papers / communities | `agents/method-07-field-intelligence/` |
| 8 | Adjacent-discipline sweep | Operationalized cross-domain scan | `agents/method-08-adjacent-sweep/` |
| 9 | Meta-questions | Framing, history, taboo, beneficiaries | `agents/method-09-meta-questions/` |
| 10 | Coverage audit | Post-run gap detection across all previous methods | `agents/method-10-coverage-audit/` |

---

## 1. Structural decomposition

Break the topic into independent dimensions and enumerate possible states within each.

### Starbursting (5W1H questioning)
Six question vectors (Who / What / Where / When / Why / How) applied to the topic. **Generate questions only — do not answer.** Primary lineage: Kipling, *Just So Stories* (1902) — "six honest serving-men"; modern form popularized in creative-problem-solving literature (see [Mindtools, *Starbursting*](https://www.mindtools.com/ab1w9zu/starbursting/)).

### Morphological analysis (Zwicky box)
List 3–7 logically independent parameters of the topic; list 3–7 values for each parameter; walk the n-dimensional matrix. Every cell is a candidate case. Combinations the canonical source doesn't address are non-obvious questions. Source: [Zwicky, 1969, *Discovery, Invention, Research — Through the Morphological Approach*](https://www.swemorph.com/pdf/gma.pdf) (Macmillan).

### SCAMPER
Seven transformations applied to the topic: **S**ubstitute, **C**ombine, **A**dapt, **M**odify/Magnify, **P**ut to other uses, **E**liminate, **R**everse. Each transformation forces a distinct class of questions. Source: Eberle, B. (1971). *SCAMPER: Games for Imagination Development*; rooted in Osborn's *Applied Imagination* (1953) checklist questions.

---

## 2. Perspective shifting

Force the topic through structurally different eyes.

### Six Thinking Hats (de Bono)
Six cognitive modes, applied sequentially, each generating a distinct question class:
- **White** — facts, data, what is known
- **Red** — emotions, intuitions, unreasoned reactions
- **Black** — risks, caution, what could go wrong
- **Yellow** — benefits, optimism, what could go right
- **Green** — creativity, alternatives, possibilities
- **Blue** — process, meta, governance of the inquiry itself

Source: de Bono, E. (1985). *Six Thinking Hats*. Little, Brown.

### Stakeholder mapping
Enumerate everyone affected by or interested in the topic: users, critics, regulators, outsiders, beneficiaries, opponents, future adopters, future victims. For each party, ask: *what do they want to understand about this topic that no one else does?* Source: Freeman, R. E. (1984). *Strategic Management: A Stakeholder Approach*. Pitman.

### Rolestorming
Temporarily adopt a specific persona — novice, skeptic, regulator, child, competitor, domain outsider — and generate questions exclusively from that persona's viewpoint. Blocks the author's default frame. Source: Griggs, R. E. (1985). *Rolestorming*. Training Magazine; formalized in [VanGundy 2004 *101 Activities for Teaching Creativity and Problem Solving*](https://www.griggsachieve.com/Rolestorming/).

### Cross-domain analogy
Ask how a biologist, architect, lawyer, economist, historian, musician, or any adjacent-discipline practitioner would frame the topic. Surface the questions their training would prompt. Underpinned by Gentner's structure-mapping theory: map **relations, not attributes**. Source: [Gentner, D. (1983). "Structure-Mapping: A Theoretical Framework for Analogy", *Cognitive Science* 7(2)](https://groups.psych.northwestern.edu/gentner/papers/Gentner83.2b.pdf).

---

## 3. Inversion

Turn the topic upside down to reach questions forward thinking never visits.

### Munger-Jacobi inversion
Flip the framing: instead of *how does this work?* ask *under what conditions does it break, become false, or produce the opposite?* Source: Munger, C. (1986). "Harvard School commencement speech" — *Invert, always invert* — attributed to Carl Jacobi, 19th-century mathematician.

### Pre-mortem
Assume the plan / understanding / investigation has already failed; reconstruct the questions that were never asked and would have surfaced the failure. Source: [Klein, G. (2007). "Performing a Project Premortem", *Harvard Business Review*](https://hbr.org/2007/09/performing-a-project-premortem) — reports a 30 % risk-forecast accuracy lift via prospective hindsight (Mitchell, Russo & Pennington 1989).

### Reverse brainstorming
Instead of *how do we understand / solve this?* ask *how would we guarantee maximum misunderstanding or failure?* Invert the anti-answers into questions. Source: creative-problem-solving literature; see [Design Thinking Tools: Reverse Brainstorming](https://www.designorate.com/design-thinking-tools-reverse-brainstorming/).

---

## 4. Causal chains

Follow causes and effects until root questions emerge.

### 5 Whys
Each answer generates a new *why?* Iterative causal drilling. Five is a heuristic; stop when further *why* no longer reveals structure. Source: Ohno, T. (1988). *Toyota Production System: Beyond Large-Scale Production*. Productivity Press. Attribution: Sakichi Toyoda, founder of Toyota.

### Systems thinking
Identify the topic's **stocks** (accumulations), **flows** (rates), **balancing loops** (self-correcting), and **reinforcing loops** (self-amplifying). Ask about delays, buffers, emergent properties, second- and third-order effects, and leverage points. Source: Meadows, D. H. (2008). *Thinking in Systems: A Primer*. Chelsea Green Publishing. Foundational: Forrester, J. (1961). *Industrial Dynamics*. MIT Press.

### TRIZ contradiction analysis
Identify **technical contradictions** (improving X worsens Y) and **physical contradictions** (one property must be both A and not-A). Questions arise about the contradictions themselves and about the field's evasions of them. Source: Altshuller, G. (1984). *Creativity as an Exact Science: The Theory of the Solution of Inventive Problems*. Gordon and Breach. Original Russian work: 1946–1979.

---

## 5. Temporal and scale lenses

Shift the time horizon and the level of magnification.

### Temporal lens
- **Past** — how did this topic emerge? What has been tried and abandoned?
- **Present** — what is actively contested right now?
- **Future** — where is this heading? What could change everything?

Grounded in futures-studies practice: Bell, W. (1997). *Foundations of Futures Studies*. Transaction Publishers. Also *back-casting* from desired futures (Dreborg 1996).

### Scale shifting
What changes when moving micro → macro, individual → systemic, local → global, short-term → long-term? Each scale surfaces a distinct question class. Holonic / nested-scale framing: Koestler, A. (1967). *The Ghost in the Machine*. Hutchinson.

---

## 6. Surfacing hidden assumptions

Make the invisible visible.

### First principles
What must be true for everything else in this topic to hold? Strip each claim until only bedrock truths remain (axioms, physical constants, definitional invariants). Rebuild upward from the bedrock; mismatches with the field's standard decomposition are non-obvious questions. Sources: Aristotle, *Posterior Analytics* (Book I); Descartes, *Discourse on the Method* (1637), Part II.

### Assumption mapping
Explicitly list everything taken for granted about the topic. For each item, ask: *what if this is false?* Questions that remain important under the negation are questions the canonical source hides. Source: VanGundy, A. B. (1988). *Techniques of Structured Problem Solving* (2nd ed.). Van Nostrand Reinhold — rooted in Osborn's *Applied Imagination* (1953) "rearrange / reverse" checklist.

---

## 7. Field intelligence

Surface questions the field itself considers hardest, most contested, or most neglected — through the channels where serious practitioners record their thinking. This method operates by retrieval, not generation.

### Recognized experts
Top 2–5 living or historical figures whose work anchors the field. For each: name the specific contribution (not a general reputation), and the hardest open problem they publicly identify.

### Books and foundational texts
Canonical works: what questions do they open rather than close? What do different authors disagree about? Each era's preoccupation reveals a question the field was working through.

### Conferences and talks
What themes dominate recent gatherings? Which sessions recur year after year without resolution?

### Scientific publications and preprints
Extract open questions from paper introductions and conclusions; replication failures; "future work" paragraphs.

### Communities and practitioners
What do forums, working groups, and professional societies argue about? What questions recur from newcomers that veterans find hard to answer well?

Triangulation discipline is detailed in [source-triangulation.md](source-triangulation.md).

---

## 8. Adjacent-discipline sweep

Operationalize cross-domain analogy into a scan. Identify 3–5 fields that neighbor or intersect the topic; for each, ask what a practitioner from that field would find interesting, troubling, or obviously missing in how the topic is currently framed. Adjacent fields see structures invisible from inside the home discipline — they have either solved analogous problems or asked fundamentally different questions about the same phenomena.

Grounded in Gentner structure-mapping (1983) and in biomimicry literature: Benyus, J. (1997). *Biomimicry: Innovation Inspired by Nature*. Morrow.

---

## 9. Meta-questions

Ask questions about the topic's structure, history, and framing — not its content.

- How has this topic been framed historically, and what was excluded?
- What questions have been treated as taboo, premature, or out of scope?
- What would make the entire topic dissolve or become irrelevant?
- Who benefits from the current framing, and who does not?
- What assumptions are so foundational that the field has stopped noticing them?

Grounded in Paul & Elder's Socratic "question about the question" type (the sixth Socratic type). Source: [Paul, R. & Elder, L. (2006). *The Thinker's Guide to Socratic Questioning*](https://www.criticalthinking.org/files/SocraticQuestioning2006.pdf). Critical-systems-heuristics framing: Ulrich, W. (1983). *Critical Heuristics of Social Planning*.

---

## 10. Coverage audit

After methods 1–9 run, explicitly identify which dimensions, stakeholders, time scales, or analogies received zero or few questions. Name those gaps as either **open questions** for future iteration or **candidate re-runs** where a specific method should be re-dispatched. Prevents the illusion of completeness.

This method has no new theory — it is a meta-application of the *Scope / Routed / Open* labelling pattern to the aggregated output of the other nine methods.

---

## Invocation order and combining rules

1. Agents 1–9 run **in parallel**. They are genuinely independent: none reads another's output.
2. Agent 10 runs **after** 1–9 complete. It reads all nine outputs and writes a structured audit (Gaps / Most Important / Duplicate Flags / Partial Agents).
3. The **Synthesis** agent runs after Agent 10 and reads all ten outputs. It writes the reader-facing `{topic-slug}-questions.md` (Overview / Questions by Dimension / Frontier Questions / Open Terrain) and drops `[Tag]` / `(Agent N)` attribution — that attribution stays in the raw per-agent outputs.
4. Overlap between methods is **expected and welcomed**. A question surfaced by both *assumption mapping* (method 6) and *pre-mortem* (method 3) is evidence the question is real. Deduplication happens at Synthesis time, not per-agent.
5. If an agent's output is thin (below the method's minimum-row target), the dispatcher may re-dispatch that one agent with a "go deeper" instruction before Stage 2.
