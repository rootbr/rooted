# Reading methodology — the canon

One merged reference for the reading companion. It fuses three sources: the compact reading **algorithm** (the actionable spine), the **evidence review** that justifies each step (with strength-of-evidence marks and citations), and the **chapter-to-note pipeline** with the division of labour with AI. Organised by theme, not by source: every section pulls from whichever of the three is relevant.

Evidence marks, where given: **high** — meta-analysis or a consistent series of controlled studies; **moderate** — several studies, limited generalization; **low / extrapolation** — single studies or a mechanism carried beyond the conditions tested. The base is overwhelmingly students, short texts, horizons of days to weeks; transfer to professionals, voluminous books, and horizons of years is justified extrapolation, not proven fact.

---

## 1. The governing principle

The goal of reading is not to get through the text but to extract and apply. The metric of the result is a changed decision, not the number of books read. Two reframings carry the rest:

1. Reading is training in retrieval and application, not the acquisition of information. A durable memory trace is left by **retrieval** (retrieval practice), **distribution over time** (spacing), and **self-generation** of the formulation (the *generation effect*). The popular passive techniques — rereading, highlighting, summarization, speed reading — are low-effectiveness and feed the illusion of knowledge.
2. A technique is chosen by its sustainability, not its laboratory efficacy. The long-term outcome is set not by the best protocol but by the mediocre one a person actually adheres to over years (*efficacy versus effectiveness*, from evidence-based medicine).

**The AI boundary that follows from this (the binding frame).** An assistant must amplify the reader's own act of retrieval and formulation, never substitute for it. It *amplifies* when it stays a source of difficulty and feedback — posing questions, checking a reconstruction, pointing out gaps, removing a language barrier. It *supplants* when it produces the finished product in the reader's place — a ready summary instead of their recall, the answer instead of their search, their notes rewritten by the machine. The freed effort *is* the mechanism of retention; offloading it trades "less effort now" for "worse retention and worse independent capability later" (§7 below). Delegation is admissible as a pointer (what to read, where to look) and as feedback on the reader's own reconstruction; it becomes substitution the moment it replaces the act of reading and generation over material that must enter the reader's operative model.

---

## 2. Why reading fails to change practice — three independent gaps

The chain "read → remembered → applying" is not one thing; it decomposes into three mechanisms that fail separately. "Read more carefully" cures only the first.

| Gap | Mechanism | What does not help | What helps |
|---|---|---|---|
| **Forgetting** | Interference from competing material, not decay over time (**high**) | Simply reread | Retrieval + spacing; sleep between reading and review |
| **Fluency illusion** | The ease of perceiving a familiar text feels like knowledge; the judgment is made with the text in view, the real test (application) without it (**high**) | The feeling "I know this" | An external indicator: reproduced / applied with no prompt |
| **Know → apply** | Transfer is context-bound; at the moment of the task, knowledge is not retrieved on its own (**high** for the gap; **contested** for far transfer) | Good memorization of theses | The rule "if situation X — then action Y", bound to a work trigger |

- **Forgetting is interference, not time.** Reading several similar sources on one topic in a row amplifies interference; distribution over time and content reduces it. After sleep (~24 h) retention gets a bonus (Murre & Dros 2015).
- **The reliable signal of knowledge** is not "the text is familiar" but "reproduced / applied with the book closed" (fluency illusion / foresight bias: Koriat & Bjork).
- **A long-term effect is attainable without holding the fact in the head.** For much material the goal is to change a disposition or build a reliable pointer "I know where to look" (transactive / external memory; Sparrow et al. 2011) — **moderate**.

---

## 3. Before reading — choose the mode by book type

The level of effort must match the material and the goal, not be applied uniformly. **Most books do not deserve analytical reading**; the job of a quick inspection is to decide whether *this* book does (Adler & Van Doren) — **heuristic**.

Adler's four levels: elementary → **inspectional** (a fast survey of structure — table of contents, headings, conclusions — answering "what is this and how is it built") → **analytical** (slow, four questions put to the text) → **syntopical** (several sources on one topic, read together). Inspection is the filter; analytical reading is deserved by a coherent argument in a field where understanding, not being informed, is the goal.

**The type → mode table:**

| Type of material | Mode | Rationale |
|---|---|---|
| Foundational primary source, dense argument | **Analytical**, reread hard parts | The value is the developed argument; the loss under a summary is maximal |
| Non-fiction around 1–2 ideas | **Inspectional, then selective** | Most do not pass the filter into analytical |
| Several books on one contested topic | **Syntopical** | Compare the ideas and terms of several authors |
| Reference, specification, tables (API, RFC) | **Lookup on demand**, not continuous | Not meant to be read in full; narrative skills do not transfer |
| Large volume, goal "be informed" | **Skim / inspectional** | A conscious trade of understanding for coverage |
| A practical skill (code, a tool) | **Foundations only** from the book; the rest is practice, a mentor, reading code | The book lacks feedback |

**Adler's four analytical questions** (questions 3–4 are the reader's own contribution — they turn a retelling into an original note):
1. What is the chapter about as a whole? (the leading theme)
2. What exactly is asserted, and how? (the main ideas, the arguments)
3. Is it true? (the reader's assessment)
4. What follows from it? (the significance, the application)

**Two before-reading actions:**
- **Formulate the goal and 3–5 questions** the book must answer for the current task. Prequestioning improves later assimilation and sets the criterion for measuring the effect (Pan & Carpenter 2023) — **high**. The goal and questions are the *reader's* to produce; authoring them is substitution.
- **Raise the starting stock** in an unfamiliar field — an overview, a glossary, an introductory text — to launch the Matthew loop (§10) and avoid an "undesirable difficulty". Without a foundation, deep reading is not assimilated, and self-questioning on unsupported material is counterproductive.

**Speed reading is refuted** (an established fact). The speed–accuracy trade-off is physiologically irremovable; RSVP/Spritz worsen comprehension above ~250 wpm. The only loss-free way to read faster is growth of language skill and vocabulary (Rayner et al. 2016) — **high**.

---

## 4. While reading — comprehension that sticks

Of ten common techniques only two have high utility in controlled studies: **retrieval practice** (self-testing) and **distributed practice** (spacing). Highlighting and rereading sit at the bottom — passive, the chief sources of the illusion of knowledge (Dunlosky et al. 2013) — **high**.

1. **Read by chapters with retrieval, not highlighting.** After a chapter, **close the book and write out the theses in your own words** (free recall + generation), then check against the text. This replaces the highlighter and the verbatim outline. On a delayed test retrieval far outperforms rereading (over 2 days rereading lost ~56% of reproducible material, testing ~13%; Roediger & Karpicke 2006) — **high**. Trap: on an *immediate* test rereading can win; the effect reverses only with delay.
2. **Feynman check.** Explain the idea in plain words, with your own analogy, as if to a child. The place you stumble is the gap in understanding. Self-explanation ("why is it so, how does it connect to what I know") is a confirmed elaboration technique (Dunlosky et al. 2013 rate it moderate).
3. **Encode the transferable as an abstract principle**, not as a recipe bound to one example — otherwise it will not transfer (§8). Restore the situational binding separately, through an if-then rule.
4. **Do not read to the end before applying.** *(heuristic)* By the middle of the book, pick one thesis, turn it into "if [work trigger] — then [action]", and execute it on the current task. This shortens the delay "reading → application" and constructs transfer.

**Desirable difficulty.** Retrieval, interleaving, and generation improve long-term retention at the price of visible slowing (Bjork & Bjork) — **high**. Difficulty becomes *un*desirable without a baseline foundation: build the minimal base first, then retrieve.

---

## 5. Consolidation — spacing and retrieval over time

1. **Distribute the reviews over time** — the first not immediately, then expand the intervals moderately; review by **retrieving the meaning**, not by rereading or rote-learning cards. Distributed reviews beat massed ones at equal cost (Cepeda et al. 2006) — **high**. Into flashcards goes only what is atomic, frequently needed from memory, and worth the upkeep; conceptual and procedural knowledge is fixed through application.
2. **Let at least one sleep pass** between reading and the first review. Fixation proceeds in sleep: it transfers memory to the cortex and makes it resistant to interference (Diekelmann & Born 2010) — **high**.
3. **Notes — atomic, reformulated, immediately linked** to existing notes and to the current project; work in short cycles of "read → processed" so a dead archive does not accumulate. Keep the personal base on personal tools. (The form is §6.)
4. **Retell it to others** — a talk, a workshop, an ADR with a reference to the source, a wiki entry. The strongest collective lever and at the same time the strongest test of understanding: even the *expectation* of teaching yields fuller, better-organized recall (Nestojko et al. 2014); on a delayed test the best are those who actually taught (Fiorella & Mayer 2013) — **high**. For an engineer the **ADR** (Architecture Decision Record) is the sustainable format — one decision with its context and consequences, next to the code, through a pull request.

---

## 6. From a read chapter to a note — the pipeline

The value of a note is not storage but two functions: it *forces a reformulation* in the reader's own words (and so fixes it — the generation effect, **high**), and it serves as an *index for re-entry*. Storage alone creates no value — the **collector's fallacy**: accumulated but unprocessed extracts are a dead archive and an illusion of knowledge.

**Three note types (Ahrens / Luhmann frame — practical, not controlled-verified):**

| Type | What it is | Lifespan |
|---|---|---|
| **Fleeting** | An instant capture of a thought, no format | Hours–days, then reworked or discarded |
| **Literature** | What you took from the source, **in your own words, one idea, with a reference** — records "what the author said" | Until the permanent note is created |
| **Permanent** | Atomic, self-contained, "as if for print" — records "what follows from this for me"; linked to others | Indefinite — the core of the base |

Permanent-note rules: one idea per note (atomicity); write as if for another person; do not merely record but develop, remix, and challenge; link to at least one existing note and to the project. A network of links — not separate cards — generates the unplanned combinations; an unlinked note is not found on re-entry.

**The pipeline (where AI is admissible and where its involvement destroys the value):**

| Step | What the reader does | The AI's role |
|---|---|---|
| 1. Inspection | Survey the chapter's structure | None — this is the reader's reading |
| 2. Analytical reading | Read against Adler's 4 questions; mark agreement / dispute | None |
| 3. Fleeting notes | Capture sparks of thought on the fly | None |
| 4. Close the book and recall | Explain the main idea from memory (Feynman) | **Examiner** — poses checking questions, does not answer for the reader |
| 5. Literature note | Write the ideas taken, in own words, one idea, with a reference | Minimal — may flag where a phrasing sounds like someone else's |
| 6. Permanent note | Rewrite as atomic and self-contained; add own example and assessment (Q3–4) | **Prose editor** — turns the draft into smooth text in the reader's style |
| 7. Atomicity & links | Check "is it one idea"; link to existing notes | May *suggest* link candidates — the reader decides |
| 8. Attribution | State the source and the AI assistance | Add a standard source + AI-disclosure line |

**The critical invariant:** the "someone else's → your own" transformation completes at **step 5** (source closed, own words). The AI joins only from **step 6** and works with the reader's literature note, **never with the source text**.

**Auxiliary methods, chosen by task:** *Cornell* (notes / questions / own-words summary — a one-page structure with built-in self-testing); *Progressive Summarization* (layered compression, when findability across many sources matters more than deep comprehension); *Zettelkasten* as the frame for a growing network. Adler at the entrance (depth), Feynman/recall at comprehension.

---

## 7. Writing notes with AI — the division of labour

One rule governs everything: the thinking is the reader's, the prose is the AI's.

- **The reader does:** read, understand, recall from memory, extract the ideas, set the structure, add own examples and judgement.
- **The AI does:** turn the reader's notes into smooth prose; fix clarity, rhythm, grammar.

Why the line falls exactly here: when the thinking itself is handed off, both learning and quality fall and the ability to work without AI declines (cognitive offloading; the MIT EEG and RCT signals in §8). The protective test, before bringing in the AI at step 6: "Can I explain this idea and my assessment with no text in front of me at all?" If not — go back to recall (steps 2–4); the AI will not help here.

**The safe AI roles** (with ready prompts):

- **Examiner** (step 4, before writing): *"I will explain an idea in my own words: '[explanation]'. Ask me 3 questions that check whether I understood it and where the gaps are. Do not explain for me — only ask."*
- **Prose editor** (step 6, the safest mode): *"Here is my draft: '[draft]'. Improve clarity and rhythm; keep my structure, meaning, and examples. Mark separately any phrasing that sounds like someone else's, so I can rewrite it myself."*
- **Atomicity checker** (step 7): *"Here is my note: '[text]'. Does it contain exactly one idea? If more, name the atomic ideas to split it into. Do not rewrite the content."*
- **Link-candidate finder** (step 7): *"New note: '[text]'. Titles of existing notes: [list]. Which 3 is it connected to, and why? Leave the decision to me."*

**Practical craft.** Tune to the reader's voice with 3–5 samples of their own text plus named parameters (register, rhythm, sentence length), not vague adjectives. Work structure-first: a thesis plan, then prose from it, then editing.

---

## 8. Transfer into practice

The gap "know → apply" is an independent phenomenon, not a memory defect. Spontaneous transfer is rare and narrow; it must be **constructed**, not awaited.

- **Where the chain breaks:** not at memorization but at the *spontaneous recognition of applicability*. Memory is context-bound (encoding specificity); the context of reading and the context of the task differ on many dimensions, so what was learned does not surface on its own (the organizational "knowing-doing gap").
- **What works — implementation intentions.** "If situation Y — then action Z" delegates the launch of the action to a pre-chosen situational cue. Effects are large and concentrated on *launching* (self-examination by 100% of if-then planners versus 53% with intention alone; meta-analysis d ≈ 0.65; Gollwitzer & Sheeran 2006) — **high**. Transfer a thesis not as "I must remember X" but as "when the specific trigger occurs, I perform the specific action".
- **The paradox resolved:** encode at the level of an **abstract principle** (transfers independently of surface detail), then restore the binding separately through an if-then linking the principle to a work trigger.
- **The environment can suppress adoption:** deadlines, processes that reward following an instruction over independent recognition, incentives for the familiar template. Even a correctly assimilated thesis is not adopted if the environment leaves no trigger and no time.

---

## 9. Habit and sustainability

Years-long practice is set not by the best method but by **compliance**. A mediocre protocol that is adhered to beats a flawless one that breaks under load.

- **The habit period is not "21 days":** the median to automaticity is ~66 days, spread 18–254 (Lally et al. 2010); realistically 2–5 months — **high**.
- **A minimal "zero" variant** (one page, one card; <30 sec) holds as the explicit floor of practice — a hard day yields a small win, not a skip. Its function is to preserve the chain and the identity, not to imitate progress.
- **What sustains over years:** habit-stacking onto an existing routine ("after [anchor] — [tiny action]"); a stable environment; a self-chosen practice; a morning placement over evening; and most strongly, the **identity** "I work through books" rather than progress counters (habits bound to an outcome goal fade on achievement; those bound to identity continue) — **moderate**.
- **Recovery after a break — "never miss twice":** one miss is an accident, two in a row begin a new habit. Return through the minimal variant, not by trying to catch up. Free notes and elaboration **degrade gracefully**; rigid spaced repetitions fall apart after an interruption (a backlog domino) — cap reviews per day, allow easy days.

---

## 10. Knowledge obsolescence — what to invest in deeply

Reading accumulates *stocks* (mental models, the vocabulary of the discipline, the file of processed notes), governed by loops and delays — not a *flow* of "N pages". Measure the level of the stock, not the inflow; intervene on the system's **rules** (selection criteria, the obligation to apply before the next book), not its parameters ("hours of reading" is the lowest leverage).

- **The Matthew effect** (reinforcing loop: more background → easier reading → more read → more background; Stanovich 1986, **high**). In an unfamiliar field the loop first works against the reader; launch it by raising the starting stock (§3).
- **Delays explain why people abandon what works:** a multi-month lag between reading and effect leads to quitting before the return. So *shorten* the delay "reading → first application" (early feedback) and *lengthen* the delay between reviews (spacing).
- **The half-life of knowledge is measurable** (engineering knowledge ~7–10 years and less) — **moderate**. The shorter a field's half-life, the stronger the preference for durable classics over rapidly obsolescing applied literature.
- **Write off the obsolete** (a blind spot of the methodologies). There is no "citator" for non-fiction; the surrogate is a personal mark of a thesis's **status and shelf life** when taking notes, so advice from 2018 is not applied as current in 2026. The conscious discarding of the outdated is *unlearning*.
- **Frontier:** deep reading stops paying off against "search on demand" when a field's half-life is shorter than the time to assimilate plus the interval until application — the stock obsolesces before it amortizes. The threshold **never arrives** for long-half-life knowledge with a high cost of access in the moment: fundamental models, methods of reasoning, invariants operated in real time that cannot be "googled" mid-task. Invest deeply in those; keep versions and APIs on a "find it when I need it" strategy.

---

## 11. What not to do

- Do not reread or highlight instead of reproducing from memory.
- Do not trust the feeling "I know this" with the text open — check with the book closed.
- Do not chase reading speed: a gain in speed inevitably cuts comprehension.
- Do not read several similar sources back-to-back — it amplifies interference; distribute over time and content.
- Do not over-engineer the note system — tuning the tool is an ideal pretext for procrastination; both hoarding and perfecting the system mask the absence of processing.
- Do not hand the AI the generation of formulations or a summary of material that is to become the reader's working model — see §1 (the binding frame) and §7.

---

## 12. Honest limits — what is not proven

Stated because the request concerns the *long-term* effect, where the base is weakest.

- **No causal data "reading professional books → career"** — only correlation, which admits reverse causation. RCTs exist for clinical bibliotherapy, not professional reading.
- **Transfer to professionals, voluminous books, horizons of years is extrapolation** — almost the entire base is students, short texts, days–weeks.
- **Far transfer is contested** for a century (Barnett & Ceci vs Detterman); reliable is only the transfer of abstract principles in close contexts.
- **Retrieval practice on complex conceptual material is contested** (van Gog & Sweller vs Karpicke & Aue).
- **"Ego depletion" did not replicate** — do not rely on it.
- **Analogies, not constructs:** "overtraining during reading", a "recovery phase", the RAG analogy of memory — they illustrate, they do not prove.
- **Open terrain:** methods for nonlinear, technically dense material (code, formulas, diagrams — most recommendations assume argumentative prose); neurodivergent readers; tacit knowledge without a factual support.

---

## 13. Helping the reader understand — the mentor and checker move

When the reader states an understanding — a reconstruction, a guess, a paraphrase — the companion's job is to check it against the source and help the reader correct it *themselves*, not to hand over the finished reading. The gain in one-to-one work comes from the reader constructing and self-correcting; a companion that delivers a polished explanation captures the low-value mode and forfeits it (ICAP — generating outranks receiving, Chi & Wylie 2014; self-explanation g ≈ 0.55, and self-generated prompts beat ready-made explanations, Bisra et al. 2018) — **high**. The moves, default to last resort:

1. **Diagnose first.** Elicit the reader's own account, then check it against the text (correct / partial / off) before offering anything. Helping before the reader has committed to a reading undercuts the effect (the contingent-teaching cycle: diagnose → check → intervene → check; van de Pol et al. 2010) — **moderate**.
2. **Elicit before telling.** Prefer, in order: a pointer to the relevant lines → one *focusing* question rooted in the reader's own words or a precise place in the text ("you said X — what in this paragraph supports that?") → a partial demonstration → telling. Each step hands more of the work back.
3. **One graduated, contingent question — not a chain.** Intervene at the lightest level that closes the gap and raise specificity only on failure (the contingent-shift principle; Wood, Bruner & Ross 1976; Chi et al. 2001 — tutors suppressed to prompts still produced learning) — **moderate**. Fade as the reader succeeds, and default to under-helping: frequent help erases the benefit (van de Pol et al. 2015).
4. **Feedback elaborates, it does not just grade.** Bare right/wrong is near-inert (knowledge-of-results d ≈ 0.05; elaborated d ≈ 0.49; Van der Kleij et al. 2015) — **high**. Elaborate facilitatively — name the misconception, cite the sentence to reread — not directively (stating the corrected reading), which is kept for last resort.
5. **Hard boundary: never a quiz or guessing game.** Do not run a chain of narrow closed questions, each judged right/wrong, that walks the reader to the answer already in your head (funneling / the IRE triad; Herbel-Eisenmann & Breyfogle 2005; Mehan 1979 — **low/moderate**, qualitative). The mechanism is solid: feedback that draws attention to the self — scores, "correct!/wrong" tallies, praise — *decreased* performance in 38% of cases (Kluger & DeNisi 1996, 607 effect sizes) — **high**; graded hint ladders get gamed for answers (Roll et al. 2011). Keep it conversation, not examination; the retrieval check (§4) is an invitation to reconstruct, not a test to pass.
6. **Know when to simply explain.** Tell directly when (a) the reader meets a genuinely new mechanism with no schema yet — walk **one** worked instance, then fade backward, doing the early steps and asking only for the last (worked-example effect d ≈ 0.55, Sweller & Cooper 1985; Atkinson et al. 2003) — **high**; (b) the reader has attempted and is stuck — give the canonical explanation anchored to their own words, since the attempt primes it to land ("a time for telling" / productive failure, observed g ≈ 0.36; Sinha & Kapur 2021; Schwartz & Bransford 1998) — **high**; or (c) they are overloaded or ask. Unguided struggle without footing overloads working memory and does not build understanding (Kirschner, Sweller & Clark 2006).
7. **Stop re-explaining what the reader already holds.** Once they restate a mechanism correctly or volunteer the next step, switch to checking-plus-one-question; superfluous explanation adds load and signals distrust (expertise reversal; Kalyuga et al. 2003) — **high**.

**Honest limits.** Bloom's "2-sigma" tutoring figure is not replicated — realistic one-to-one gains are about d ≈ 0.4–0.8, not 2.0 (VanLehn 2011); promise careful checking and self-correction, not a transformative gain. The focusing-versus-funneling distinction is well-described but largely qualitative — the anti-quiz rule rests on the feedback-locus mechanism (Kluger & DeNisi), not an effect size. Feedback timing (immediate vs delayed) is roughly equivalent, so let the reader finish the thought before correcting; no timing dogma.

---

## Sources (grouped)

- **Memory & techniques (§§2,4):** Dunlosky et al. 2013 (PSPI); Roediger & Karpicke 2006; Karpicke & Blunt 2011; Cepeda et al. 2006, 2008; Karpicke & Roediger 2007; Bjork & Bjork; Koriat & Bjork; Murre & Dros 2015; Diekelmann & Born 2010; Pan & Rickard 2018; van Gog & Sweller / Karpicke & Aue 2015; Sparrow et al. 2011.
- **Transfer (§8):** Barnett & Ceci 2002; Detterman 1993; Godden & Baddeley 1975; Gollwitzer 1999, Gollwitzer & Sheeran 2006; Pfeffer & Sutton 2000; Pan & Carpenter 2023.
- **Selection & modes (§3):** Adler & Van Doren, *How to Read a Book*; Rayner et al. 2016; Springer 2024 (multiple-text vs rereading).
- **Notes & PKM (§§6,7):** Slamecka & Graf 1978; Bangert-Drowns et al. 2004; Ahrens 2017; Luhmann; Forte (Progressive Summarization); "collector's fallacy". AI-writing & offloading: OpenAI Academy (Writing); Zapier (voice tuning); EDUCAUSE / MDPI / MIT EEG (Kosmyna et al. 2025, preprint); Barcaui 2025 (RCT, preliminary).
- **Habit (§9):** Lally et al. 2010; 2024 meta-analysis (PMC11641623); Wood & Neal 2007; Fogg, *Tiny Habits*; Clear; Hagger et al. 2016 (ego depletion).
- **Systems & obsolescence (§10):** Meadows, *Thinking in Systems* / *Leverage Points*; Stanovich 1986; Arbesman 2012; Shepardizing (Stanford Law); Hedberg / Rushmer & Davies (unlearning).
- **Alternatives & AI (§§1,8):** Recht & Leslie 1988; Bransford & Johnson 1972; Macnamara et al. 2014; Risko & Gilbert 2016; Wolf, *Reader, Come Home*.
- **Collective (§5):** Nestojko et al. 2014; Fiorella & Mayer 2013; Nygard / Fowler (ADR); Lave & Wenger (CoP).
- **Helping understanding / tutoring (§13):** Chi & Wylie 2014 (ICAP); Bisra et al. 2018 (self-explanation); Chi et al. 2001; van de Pol, Volman & Beishuizen 2010 and van de Pol et al. 2015 (scaffolding contingency); Wood, Bruner & Ross 1976; Van der Kleij et al. 2015, Hattie & Timperley 2007 (feedback); Kluger & DeNisi 1996; Sinha & Kapur 2021, Schwartz & Bransford 1998 (productive failure / time for telling); Sweller & Cooper 1985, Atkinson, Renkl & Merrill 2003 (worked examples); Kalyuga et al. 2003 (expertise reversal); VanLehn 2011; Kirschner, Sweller & Clark 2006; Roll et al. 2011 (hint abuse).
