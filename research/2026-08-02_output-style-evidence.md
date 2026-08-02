# Output-style rules — evidence report

The programme establishes that both rule sets can enter `/auditing-ai-context`, in one specific shape — a small ordered resident core plus the long form as rule cards, enforced by an audit over produced text — because a rule that governs every answer has no routable trigger and residency alone does not deliver compliance. Twelve topics closed. 25 sources were verified first-hand; 23 were reached only through a search summary and may not be cited on a card. One finding recurred across three literatures and outranks the rest: the output's shape is applied after reasoning completes, never as a constraint on it.

This file carries the whole programme in one place: the report, the twelve topic notes it was compiled from, the first-hand verification of six relayed sources, and the hook design that came out of it. [Topic map](#topic-map) is the entry point.

## What was investigated and why

The goal is absorbing two hand-written rule sets into `/auditing-ai-context`: the personal skill `documenting-present-design` (prose attached to code) and the operator's global `CLAUDE.md` § Style, § Screen, § Voice and § Input-and-output. Neither carries a citation, and under the repository's Evidence-Based Rule neither can enter the corpus as it stands. Both are to be deleted at their current homes once the corpus covers them.

The magnitude is fixed and measurable — of ~3,100 tokens in the always-loaded `~/.claude/CLAUDE.md`, ~2,060 are uncited writing and speaking rules:

| Section | chars | ~tokens |
|--|--|--|
| § Style | 5,120 | 1,280 |
| § Voice | 1,409 | 352 |
| § Screen | 1,272 | 318 |
| § Input and output | 443 | 110 |

The gap in one sentence: every one of the 78 existing rule cards addresses an **agent reading an instruction file**, while these rules address a **human reading the agent's answer** — so the corpus needs a second consumer axis, and each rule class on that axis needs an evidence base outside the context-engineering corpus it already has.

## Method

The programme was run local-corpus-first. Each topic began by re-reading the repository's own verified findings — [`2026-04-18_context-engineering-research.md`](2026-04-18_context-engineering-research.md), its corrections in [`2026-07-05_context-engineering-update.md`](2026-07-05_context-engineering-update.md), and the critical-thinking note — before any web search. Search was targeted only at what the local corpus could not answer: D1 needed whether style-class constraints survive as instructions, D2 needed judge behaviour on style specifically, and clusters A, B, C and E sat outside the corpus entirely.

Before any number was used, the primary source was fetched first-hand. Where text extraction failed, the numbers were read from the scanned page images: Haviland & Clark 1974 for the given–new comprehension times, Gibson 2000 for the open-dependency series. Every claim that arrived through a search summary rather than a fetched source is marked **relay only** in its note and in the source list below, and is barred from citing on a rule card until fetched.

Two claims from one search summary were checked against the four sources fetched for D3 — ConInstruct, PRIME, IH-Benchmark and Wallace — and appear in none of them: "GPT-4o achieved only 63.8% obedience to designated priority instructions even with explicit emphasis", and that societal-hierarchy framings outweigh system/user roles. Both are parked as unattributed and must not be cited; the summary appears to have conflated sources. A third figure met the same fate in D1 — an "88% → 71% for o1-preview" drop attributed to the multi-turn constraint literature, absent from the SEQUOR abstract, and dropped.

Each topic produced one note ending in a Sources section plus provenance lines pre-formatted for [`rule-cards-provenance.md`](../plugins/evidence-based-authoring/skills/auditing-ai-context/references/rule-cards-provenance.md). The topic map carried per-topic status throughout, so an interrupted run resumed at the next open topic rather than restarting. The report below was compiled from the twelve notes without re-fetching their sources; the first-hand/relay split it records is the split the notes recorded, as corrected by the three verification passes.

One method note the verification passes produced: both PDFs recorded as "unextractable" did carry a text layer. The refusal came from the fetch summarizer, not the file — so "does not extract" was a conclusion reached too early.

## Ruling: a trade book is never a source class

Operator ruling, 2026-08-02. The three admissible classes stay exactly as `CLAUDE.md` states them — academic research, technical standards, verified hands-on experience. A practitioner book may be named as the formulation a rule follows; it may never be its evidence.

Applied and outstanding:

| Site | State |
|--|--|
| `references/rule-cards-taxonomy.md` Source-block schema | **fixed** — the "book + §" permission is removed and replaced by the three classes |
| The three comment-craft rules drafted from Clean Code and Ousterhout | do not ship as cited cards; they survive only if the migrated eval seeds carry them as hands-on evidence |
| `references/rule-cards-provenance.md:100` — C-B1 rested on Ahrens 2017, zettelkasten.de and Matuschak | **fixed, and no exception was needed.** Both web pages were fetched and are live, and both self-describe as convention rather than evidence — "not a rigid law, but a guiding compass" and "no clear litmus test or correct answer here". C-B1 now rests on Dense X Retrieval 2312.06648, already in the corpus for C-A1 and a genuinely different claim from it (title form vs card scope). The two live pages stay, named as the formulation the rule follows. Ahrens 2017 is dropped |
| `references/kb-card-specification.md:177, 231–233` | outstanding — the same three appear in the spec's numbered evidence list and must be relabelled as formulation there too |

A second axis surfaced while resolving this and is worth its own rule: **a citation nobody can open cannot be re-verified by anyone, the audit included.** Online resolvability is independent of evidence class — a live practitioner page fails the class test while passing the openability test, and a trade book fails both. Where a resolvable source carries the same formulation, the unresolvable one is dropped rather than kept beside it.

The Fowler extract-method rule was already out of scope for a different reason (`code-quality:cleaning-code` owns it; `R-76` forbids the overlap), so the ruling costs nothing there.

## Coverage against the existing 78 cards

Covered, but by a rule derived for a different consumer:

| Rule class in § Style / § Screen | Closest card | Verdict |
|--|--|--|
| State how a thing is done, not what is absent | `R-61` | same thesis, other consumer — needs re-derivation |
| Form fits content (list / table / prose) | `R-21` | rationale is agent-side retrieval |
| Topology as text, not a drawing | `R-23` | **inverted** for the screen: arrows for the agent, boxes for the terminal |
| Bold only for a warning or a first use | `R-27`, `R-62` | near-identical; widen the consumer |
| Heading depth ≤ 3 | `R-20` | covered |
| Dates and provenance live in git | `R-57` | covered for files |
| One rule per class of failure (§ Upkeep) | `R-72` | covered |

Not covered by any card: answer-first ordering; given–new inside the sentence; sentence load and nesting; nominalization and actor-as-subject; filler, hedges and offers of further work; calibrated uncertainty; magnitude vs exact number; register; glossing a term for a known reader; audience calibration; the whole § Screen rendering table; the whole § Voice split; cross-lingual restatement of the request; the Russian-specific rules.

## Topic map

Every topic is closed and carries its full note below.

| Topic | Question | Note |
|--|--|--|
| D1 | Where must a rule that governs every answer live, and at what cost? | [Where output-style rules must live](#d1--where-output-style-rules-must-live) |
| D2 | How is a rule whose check is semantic verified at all? | [How a style rule is verified](#d2--how-a-style-rule-is-verified) |
| D3 | Declared precedence or merging, for a corpus of ~100 rules? | [Precedence or merging](#d3--precedence-or-merging-for-a-corpus-of-100-rules) |
| A1 | What does answer-first ordering and given–new structure measurably do? | [Order of exposition](#a1--order-of-exposition) |
| A2 | Which sentence features predict reading difficulty, and what replaces a readability score? | [Sentence load](#a2--sentence-load) |
| A3 | Which verbosity is a training artifact, and where does compression start costing? | [What may be cut](#a3--what-may-be-cut) |
| A4 | Which form of expressed uncertainty improves the reader's calibration? | [Calibrated uncertainty](#a4--calibrated-uncertainty) |
| B1 | When does a diagram or table beat prose for a human reader? | [Form for a human reader](#b1--form-for-a-human-reader) |
| B2 | Which § Screen conventions rest on a standard? | [Terminal rendering and accessibility](#b2--terminal-rendering-and-accessibility) |
| B3 | What must change between a text and its spoken version? | [Writing for the ear](#b3--writing-for-the-ear) |
| C1 | Does restating a Russian request in English improve the result? | [Language of operation](#c1--language-of-operation) |
| E1 | Why does "used to / no longer" in a live document harm its reader? | [Stale comments and history artifacts](#e1--stale-comments-and-history-artifacts) |
| E2 | Does a decision's rationale belong in the living document or a separate record? | [Deliberation residue and the home of rationale](#e2--deliberation-residue-and-the-home-of-rationale) |

Three verification passes read the relay-only sources first-hand and corrected the notes above:

| Pass | Sources read | Note |
|--|--|--|
| Diagrams and graphical perception | Larkin & Simon 1987; Cleveland & McGill 1984 | [Verification](#verification--larkin--simon-1987-cleveland--mcgill-1984) |
| Multimedia and speech | Mayer's redundancy and modality principles; speech transience | [Verification](#verification--mayers-principles-and-speech-transience) |
| Structure and drift | Lang 1989; Wolfer 2016; Ferreira 2021; Wen 2019 | [Verification](#verification--news-structure-nominalisation-passive-voice-comment-drift) |

One design came out of the programme rather than out of a topic: [a Stop hook that checks the finished answer](#appendix--a-stop-hook-for-the-finished-answer) against the mechanically decidable half of § Screen and § Voice.

## Findings by cluster

### D — Artifact shape and verifiability

Residency is forced, and it does not buy obedience. A rule governing every answer has no trigger event to route on, skill bodies are injected lazily on invocation, routing on name and description alone already costs 31.4–44.0 pp Hit@1, and similarity retrieval systematically misses causally essential content that is textually unrelated to the query. Cost is not the binding constraint — prompt caching breaks even at n\*=2 reuses. Compliance decay is: SEQUOR measures >11% accuracy loss as a conversation grows, >40% under multiple simultaneous constraints, and >9% when constraints are added or replaced mid-conversation. Hence the three-part shape, with the resident core ordered hard-to-easy. [D1](#d1--where-output-style-rules-must-live)

Verification splits into two jobs with opposite bias exposure. The per-rule audit poses one binary question per card — the architecture the corpus already has; per-requirement validators reached 95.6% human agreement over 1,095 validations, and binary decomposition raises cross-model agreement by 0.45. The eval harness comparing corpus-on against corpus-off is where the biases bite: style bias dominates at 0.10–0.76 and favours markdown over plain text, while Claude's verbosity bias runs toward brevity (−0.12) where Gemini and Llama run long. Because § Style is mostly cutting rules and the audit runs on Claude, the systematic error is over-flagging deletions; the residual-fact test is the corrective. The best cheap judge configuration reached 71.0% agreement (κ = 0.549), which keeps `needs_human` on every semantic card. [D2](#d2--how-a-style-rule-is-verified)

Merging beats declared precedence. An unresolved contradiction fails silently — Claude-4.5-Sonnet detects conflicts at 87.3% F1 and DeepSeek-R1 at 91.5%, yet models rarely notify the user or ask for clarification. Declared hierarchy is unreliable even where it is best trained: instruction-hierarchy compliance across 37 models spans 98.2% down to 20.5%, and Wallace's contribution is the training that produces compliance, not the declaration. Conflict type outweighs model scale, so a stronger model will not absorb corpus contradictions. Precedence that must hold is executed, never declared — `GROUP_PRIORITY` is the corpus's own instance of the correct pattern. [D3](#d3--precedence-or-merging-for-a-corpus-of-100-rules)

### A — Reader-side prose

The two ordering rules of § Style do not share evidence. Given–new at sentence scale is measured and confound-controlled: 835 vs 1016 ms with a direct antecedent versus an indirect one (Δ181 ms, minF'(1,36) = 6.47, p < .025, n = 16), and 1031 vs 1168 ms with lexical repetition controlled (Δ137 ms, minF'(1,23) = 15.7, p < .001, n = 10). Document-scale answer-first has no comprehension support and no comprehension disadvantage either: the counter-finding attributed to Lang 1989 turned out to be Sternadori's 2008 dissertation, whose recognition and recall results are null and whose comprehension result trends *toward* the inverted pyramid. What that dissertation does measure in the rule's favour is processing cost — 396.4 ms against 412.7 ms secondary-task reaction time. [A1](#a1--order-of-exposition)

Reading load is driven by the peak number of simultaneously open dependencies, not by length — Gibson's worked series holds 1, 3 and 5 open dependencies, and his Japanese pair reorders the same words out of a nesting and becomes easier, which is exactly § Style's long-left-to-right rule. No score can serve as the check: readability formulas, NLP methods, commercial education systems and frontier LLMs are all poor predictors of eye-tracked reading ease. Gopen & Swan 1990 is settled as an expert essay with no experiment and cannot back a card. [A2](#a2--sentence-load)

Verbosity is a reward-model artifact — a purely length-based reward reproduces most of RLHF's downstream gains over supervised fine-tuning — so the cutting rules correct a known bias rather than impose taste. Compression meets a per-task floor ("token complexity"), and that floor sits in the reasoning, not the prose, so the cutting rules scope to the delivered answer only. Response length is invalid as a success metric. Nominalisations were verified to slow *reading* (β = 0.131, t = 8.911) with no measured comprehension gain, and the passive is not banned: flag an agentless passive only where the agent is known and material. [A3](#a3--what-may-be-cut)

First-person hedging is the form that works. In a pre-registered N=404 experiment, first-person uncertainty raised participant accuracy by reducing overreliance on wrong answers, while the impersonal form's effects were weaker and not statistically significant. Separately, longer explanations raise reader confidence without raising accuracy, which gives the cutting rules a calibration rationale and a severity above ordinary style. [A4](#a4--calibrated-uncertainty)

### B — Rendering and modality

A diagram earns its place by lowering the cost of inference, not by carrying more information, so `R-23` (arrow text for an agent) and § Screen (drawn trees for a terminal) are the same rule under different consumers and need the consumer named rather than a rewrite. Larkin & Simon carry the qualifier the title's "sometimes" announces: a diagram fails without the operators to read it. The larger result outgrew the topic: output shape taxes the reasoning producing it — Haiku −36.2 pp (p < 0.0001, largely truncation), GPT-4o-mini −28.0 pp (p < 0.001, capacity competition), Sonnet on MATH-Hard unaffected (88.7 ± 4.0% JSON vs 89.3 ± 1.7% CoT), and Opus 4.7 on AIME 96.2% → 91.0% (−5.3 pp). Reasoning freely before formatting recovers 80–87% of the loss. [B1](#b1--form-for-a-human-reader)

Colour redundancy is normative, not preference: WCAG 2.2 SC 1.4.1 at Level A states that colour is not used as the only visual means of conveying information. This is the corpus's first conformance-grade citation, and it stands alone — Cleveland & McGill exclude colour hue as categorical and never showed saturation to a subject. One assumption was corrected: UAX #11 says display width cannot be resolved from the character code and explicitly disclaims use by modern terminal emulators, so the aligned-block rule is about glyph determinacy, not about counting columns. The six-rank perceptual ordering is *hypothesized*; what is measured is position against length — errors 40–250% larger, 5.3× the rate of gross errors — which is exactly why a magnitude row prints its number. [B2](#b2--terminal-rendering-and-accessibility)

§ Voice's screen/speech split divides content across channels rather than duplicating it, and the completeness rule that duplicates the conclusion needs no defence: Mayer names "the material lacks graphics" as a condition under which the redundancy effect is eliminated or reversed, and a spoken span has no graphics. The graphics-free experiment favours the redundant presentation at 0.78 retention, 1.62 transfer, 0.39 matching. The blunt transience claim is refuted for competent adults — listening against reading is not reliably different (g = 0.07, p = 0.23, 46 studies, N = 4,687) — while nesting in heard sentences is measured at about nine accuracy points per embedded clause. Cyrillic transliteration is reclassified as a workaround for a missing pronunciation lexicon; W3C PLS 1.0 defines the standard mechanism and `terms.tsv` already is one. [B3](#b3--writing-for-the-ear)

### C — Language of operation

English is the models' internal pivot — the abstract concept space lies closer to English than to other languages — but that result is bounded to the Llama-2 family. The measured gain from self-translating a prompt into English is 2.4% on a weakly multilingual model, concentrates in exactly that class, and can reverse for models trained across many languages (relay only). What the **Prompt:** line reliably buys is different: an explicit interpretation the user can correct before the work starts, which is an underspecification control. A card claiming an accuracy gain would overstate the evidence. The Russian-specific § Style 5 rules remain unsourced and need their own topic. [C1](#c1--language-of-operation)

### E — Prose attached to code

The empirical base for purging stale prose exists and beats the books the personal skill currently cites — but it is narrower than the programme first claimed. Comments and code mostly do not co-evolve: 13% to 20% of code changes trigger a comment change, verified first-hand across 1.3 billion AST-level changes in 1,500 Java systems. The drift-tracks-defects half does *not* ship: the ~1.5× bug-introducing figure is not in Wen 2019 at all, belongs to a non-peer-reviewed 2024 preprint whose own table yields 1.417, and the upstream study it displaces runs the other way. Independently and first-hand: code-element references survive in documentation after every source instance is deleted, and most of 3,000+ GitHub projects carry at least one at some point. For an agent reader a stale line is a distractor carrying the same authority as the current rule. [E1](#e1--stale-comments-and-history-artifacts)

Deliberation residue is defensible as relocation, not deletion. Rationale is first-class — an architecture is a set of explicit design decisions — so a rule that removed it would be wrong, and the card must name the destination. Storage location "has a massive influence on perceived usefulness" (relay only). The ADR template scoring best overall, Nygard's, is the concise one and carries no considered-alternatives section, which is consistent with dissolving those tables rather than propagating them. [E2](#e2--deliberation-residue-and-the-home-of-rationale)

## The cross-cutting rule

Three topics reached the same structural finding from three separate literatures:

```
A1  answer-first is free only when reasoning precedes the visible answer
A3  brevity must scope to the delivered answer, never to the reasoning budget
B1  format applied before reasoning completes costs up to 36.2 pp
```

Stated once: **the output's shape is applied after reasoning completes, never as a constraint on it.** The measured cost of violating it is up to −36.2 pp on Haiku; frontier immunity is qualified rather than granted, since Opus 4.7 still loses 5.3 pp; reasoning before formatting recovers 80–87%. Under `R-43` this belongs in one corpus-level place referenced by every shape card, and by D1 and D3 it sits early in the resident core. It also bears on the audit's own `modelByCheckKind` dispatch, where schema-heavy output runs on Haiku.

## Rules that survived on a different justification than they were written with

| Rule | Written justification | Justification that survived |
|--|--|--|
| Document-level answer-first | comprehension and recall | lower processing cost at no cost to recall (Sternadori 2008: 396.4 vs 412.7 ms) |
| Russian-to-English **Prompt:** restatement | better model accuracy in English | an explicit interpretation the user can correct before work starts — an underspecification control |
| Deliberation residue | delete the residue | relocate it: the living document keeps the decision and its determining reason, catalogues move to a dedicated record |

Two consequences follow. Each card states the justification that survived, not the one the rule was written with. And § Style's premise→conclusion exception stays a **house heuristic**: the clause that justified it — complex material fares better in sequential order — was that dissertation's H3, reported disconfirmed.

## House numbers with no located source

| Number | Home | Status |
|--|--|--|
| "one claim per sentence, two at most" | § Style 4 | no supporting evidence located |
| "a second level of nesting" starts a new sentence | § Style 4 | usable heuristic, but the stated trigger is the proxy the field moved away from — the load is peak open dependencies |
| aligned block within 100 columns | § Screen | no source located; typographic-measure research not consulted |

`R-50` settles what must happen: a prescription without an attributable source is cut or marked provisional. `CONTRIBUTING.md` names the third path — a linked hands-on test counts as a source, which is what the D2 eval harness would supply. `R-54` and `C-E3` require a quantified claim to keep its number, and `R-64` requires every repeat of a threshold to match, so a number that stays must be one of these three: re-derived from a located source, backed by a linked hands-on test, or dropped so the rule ships as a heuristic with its reason.

## What the verification round caught

Six relay-only sources were read first-hand. Every claim below had been asserted by the programme and was corrected in its topic note; this is what the relay-only marking was for.

| Claim as written | What verification found |
|--|--|
| Cleveland & McGill rank the perceptual tasks "by measured accuracy" | They **hypothesize** the ordering (§3 *Theory*, p. 537). Only position-vs-length and position-vs-angle were measured. Colour hue is excluded at p. 532; saturation was never shown to a subject. The colour rule now rests on WCAG alone |
| Inconsistent comments are ~1.5× more likely to precede a bug-introducing commit (Wen 2019) | **Not in Wen 2019 at all** — no bug analysis, no SZZ, no odds ratio. The sentence is from [arXiv:2409.10781](https://arxiv.org/abs/2409.10781), a non-peer-reviewed preprint; its own Table 4 gives a pooled 1.417, not 1.52. Ibrahim 2012, cited by Wen, runs the other way. The drift-tracks-defects argument does not ship |
| Lang 1989 is a counter-finding against document-level answer-first | The PDF was **the wrong document** — Sternadori's 2008 dissertation. That dissertation contradicts the relay: recognition and recall null, comprehension trending *toward* the inverted pyramid (p = .08), and the "complex topics favour chronological" clause was its disconfirmed H3 |
| Nominalisations slow comprehension (Freiburg corpus) | They slow **reading** (β = 0.131, t = 8.911); comprehension showed no gain (84 / 88 / 87%). Wolfer says so himself |
| *In Defense of the Passive Voice* supports the "hides who acts" scope | Ferreira 2021 is a review essay with no new data, and holds that omitting the agent is usually correct. The defensible rule narrows further: flag an agentless passive only where the agent is known and material |
| Larkin & Simon's two definitions | Confirmed verbatim at p. 67, but four relayed quotes were stitched and one dropped the clause that gives the concept meaning. The paper runs to p. 100 and carries no pulley-problem search count, so no speedup ratio may be quoted |
| § Voice's completeness rule sits in tension with Mayer's redundancy principle | **No tension exists — the rule is the measured-better arrangement.** Mayer names "the material lacks graphics" as a condition that reverses the effect (ch. 12, p. 299), and a spoken span has none. Moreno & Mayer 2002, graphics-free, favours the redundant presentation at 0.78 / 1.62 / 0.39. The modality principle stops being citable here: four of its boundary conditions hold at once |
| The redundancy effect size is 0.69 | Real but stale — Mayer & Moreno 2003, a median of three comparisons. Mayer's current figure is 0.86 over 16 of 16 tests. A card must carry the year |
| Speech is transient, therefore harder | Refuted for competent adults: listening against reading is "not reliably different" (g = 0.07, p = 0.23; 46 studies, N = 4,687). What is measured is nesting in *heard* sentences — about nine accuracy points per embedded clause (Peelle 2010). "No forward references" stays a house convention |

## Sources

Every source named in a topic note's Sources section is listed. Leads the notes recorded as "not consulted, still open" are excluded — they carry no claim.

### Verified first-hand

| Source | Topic | What it carries |
|--|--|--|
| [2605.06353](https://arxiv.org/abs/2605.06353) — SEQUOR | D1 | >11% / >40% / >9% constraint-following drops |
| [2502.17204](https://arxiv.org/abs/2502.17204) — Order Matters | D1, D3 | hard-to-easy constraint order preferred |
| [2604.23178](https://arxiv.org/abs/2604.23178) — Judging the Judges | D2 | style bias 0.10–0.76; 71.0% agreement, κ=0.549 |
| [2403.18771](https://arxiv.org/abs/2403.18771) — CheckEval | D2 | binary decomposition, +0.45 agreement |
| [2404.04475](https://arxiv.org/abs/2404.04475) — LC-AlpacaEval | D2 | length debiasing, Spearman 0.94 → 0.98 |
| [2511.14342](https://arxiv.org/abs/2511.14342) — ConInstruct | D3 | 87.3% / 91.5% F1 detection; no notification |
| [2607.25987](https://arxiv.org/abs/2607.25987) — IH-Benchmark | D3 | compliance spans 98.2%–20.5% over 37 models |
| [2404.13208](https://arxiv.org/abs/2404.13208) — Wallace | D3 | hierarchies are trained, not declared |
| [2606.22470](https://arxiv.org/abs/2606.22470) — PRIME | D3 | conflict type outweighs model scale |
| [Haviland & Clark 1974](https://web.stanford.edu/~clark/1970s/Haviland,%20S.E.%20_%20Clark,%20H.H.%20_What's%20new_%20Acquiring%20new%20information%20as%20a%20process%20in%20comprehension_%201974.pdf) | A1 | 181 ms and 137 ms given–new penalties (page images) |
| [2307.13702](https://arxiv.org/abs/2307.13702) — Lanham | A1 | CoT before the answer; faithfulness falls with scale |
| [Sternadori 2008](https://pdfs.semanticscholar.org/f2eb/ad1fa4020d0647314314457ec2c003516087.pdf) | A1 | print-medium test: memory null, comprehension trends to inverted pyramid, STRT 396.4 vs 412.7 ms |
| [Gibson 2000, DLT](https://tedlab.mit.edu/tedlab_website/researchpapers/Gibson_2000_DLT.pdf) | A2 | peak open dependencies 1/3/5; the Japanese pair (page images) |
| [2502.11150](https://arxiv.org/abs/2502.11150) — Shubi et al. | A2 | formulas, systems and LLMs are poor readability predictors |
| [2310.03716](https://arxiv.org/abs/2310.03716) — Singhal | A3 | length-only reward reproduces most RLHF gains |
| [2503.01141](https://arxiv.org/abs/2503.01141) — token complexity | A3 | per-task compression floor; adaptive compression |
| [Wolfer 2016](https://langsci-press.org/catalog/view/108/298/512-1) | A3 | nominalisations slow reading (β=0.131, t=8.911); comprehension unchanged |
| [Ferreira 2021](https://psycnet.apa.org/manuscript/2020-19385-001.pdf) | A3 | review essay; agent omission usually legitimate |
| [2405.00623](https://arxiv.org/abs/2405.00623) — Kim, FAccT 2024 | A4 | N=404; first-person hedging raises reader accuracy |
| [2401.13835](https://arxiv.org/abs/2401.13835) — Steyvers, NMI | A4 | length inflates confidence, not accuracy |
| [Larkin & Simon 1987](https://mechanism.ucsd.edu/bill/teaching/F12/cs200/Readings/larkin.whyadiagramissometimesworth.1987.pdf) | B1 | informational vs computational equivalence; three failure conditions (page images) |
| [2408.02442](https://arxiv.org/abs/2408.02442) — Tam | B1 | reasoning declines under format restrictions |
| [2606.09410](https://arxiv.org/abs/2606.09410) — Capacity, Not Format | B1 | −36.2 pp; Opus 4.7 −5.3 pp; recovery 80–87% |
| [WCAG 2.2 SC 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) | B2 | colour redundancy, Level A — normative |
| [UAX #11](https://www.unicode.org/reports/tr11/) | B2 | display width not computable; terminal use disclaimed |
| [Cleveland & McGill 1984](https://www.math.pku.edu.cn/teachers/xirb/Courses/biostatistics/Biostatistics2016/GraphicalPerception_Jasa1984.pdf) | B2 | ordering hypothesized; position vs length measured (page images) |
| [Mayer & Fiorella 2014, ch. 12](https://edtechuvic.ca/wp-content/uploads/sites/11/2022/09/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles.pdf) | B3 | redundancy 16/16, d=0.86; boundary conditions p. 299 |
| [Mayer & Pilegard 2014, ch. 13](https://edtechuvic.ca/edci337/wp-content/uploads/sites/11/2022/09/principles-for-managing-essential-processing-in-multimedia-learning-segmenting-pre-training-and-modality-principles.pdf) | B3 | modality 53/61, d=0.76; its boundary conditions |
| [Moreno & Mayer 2002](https://tecfa.unige.ch/tecfa/teaching/methodo/MorenoMayer2002.pdf) | B3 | graphics-free: redundant presentation wins 0.78 / 1.62 / 0.39 |
| [Clinton-Lisell 2022](https://eric.ed.gov/?id=EJ1347325) | B3 | listening vs reading g = 0.07, n.s., 46 studies |
| [Peelle et al. 2010](https://pmc.ncbi.nlm.nih.gov/articles/PMC2837088/) | B3 | heard object-relative 0.843 vs subject-relative 0.935 |
| [Schotter, Tran & Rayner 2014](http://faculty.cas.usf.edu/eschotter/papers/Schotter_Tran_Rayner_2014_PsychSci.pdf) | B3 | blocking re-reading lowers comprehension (b = −0.92) |
| [W3C PLS 1.0](https://www.w3.org/TR/pronunciation-lexicon/) | B3 | pronunciation belongs in a lexicon |
| [2402.10588](https://arxiv.org/abs/2402.10588) — Wendler | C1 | English as internal pivot; Llama-2 scope |
| [2212.01479](https://arxiv.org/abs/2212.01479) | E1 | outdated code references across 3,000+ projects |
| [Wen 2019, ICPC](https://csnagy.github.io/research/pdfs/2019/Wen2019-preprint.pdf) | E1 | 1.3B AST changes, 1,500 Java systems; 13–20% co-evolution |
| [Radmanesh 2409.10781](https://arxiv.org/abs/2409.10781) | E1 | the misattributed 1.5×: preprint, pooled 1.417 |
| [2604.27333](https://arxiv.org/abs/2604.27333) | E2 | five ADR templates; the concise one wins overall |

### Relay only — barred from citing on a card until fetched

| Source | Topic | What it would carry |
|--|--|--|
| [2410.03608](https://arxiv.org/abs/2410.03608) — TICK | D2 | generated YES/NO checklists improve evaluation |
| [Lang 1989](https://doi.org/10.1080/08838158909364093) | A1 | broadcast-news structure; paywalled, abstract truncated |
| [NN/g, Inverted Pyramid](https://www.nngroup.com/articles/inverted-pyramid/) | A1 | practitioner guidance for the scanning claim, not an experiment |
| [Gopen & Swan 1990](https://www.usenix.org/sites/default/files/gopen_and_swan_science_of_scientific_writing.pdf) | A2 | read for classification only — expert essay, barred as evidence |
| [Nested dependencies, German verbal clusters](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5787339/) | A2 | nesting count contributes little on its own |
| [2507.04023](https://arxiv.org/abs/2507.04023) | A3 | the relayed 28% maths loss under "be concise" |
| [2503.16419](https://arxiv.org/abs/2503.16419) | A3 | the relayed 18.75-point loss under a 1,024-token budget |
| [One Step at a Time](https://journalofcognition.org/articles/10.5334/joc.36) | A3 | delayed filler reactivation in passive forms |
| [Why Diagrams Are Six Times Easier](https://adrenaline.ucsd.edu/kirsh/fileupload/Diagrams/whay_diagrams_are_worth.pdf) | B1 | diagram benefits beyond locational indexing |
| [Adesope & Nesbit 2012](https://rex.libraries.wsu.edu/esploro/outputs/journalArticle/Verbal-Redundancy-in-Multimedia-Learning-Environments/99900601157101842) | B3 | 57 studies; spoken–written beats spoken-only without pictures |
| [Working memory load in spoken-word recognition](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4871876/) | B3 | load delays spoken-word discrimination |
| [Working memory and attention, reading vs listening](https://pmc.ncbi.nlm.nih.gov/articles/PMC6096896/) | B3 | modality difference in comprehension load |
| [2507.22923](https://arxiv.org/abs/2507.22923) | C1 | translation strategy governs the outcome |
| [2504.09378](https://arxiv.org/abs/2504.09378) | C1 | cross-lingual alignment and multilingual performance |
| [Beyond English](https://www.researchgate.net/publication/392498346_Beyond_English_The_Impact_of_Prompt_Translation_Strategies_across_Languages_and_Tasks_in_Multilingual_LLMs) | C1 | the 2.4% gain and its reversal on multilingual models |
| [Stulova et al., SCAM 2020](https://software.imdea.org/~alessandra.gorla/papers/Stulova-UpDoc-SCAM20.pdf) | E1 | automatic detection of inconsistent Java comments |
| [Ibrahim et al. 2012](https://sailresearch.github.io/sail-website/data/pdfs/JSS_OnTheRelationshipBetweenCommentUpdatePracticesAndSoftwareBugs.pdf) | E1 | counter-evidence: inconsistent changes not necessarily buggier |
| [ADR in Practice](https://link.springer.com/chapter/10.1007/978-3-031-70797-1_22) | E2 | storage location governs perceived usefulness |
| [Jansen & Bosch](https://www.semanticscholar.org/paper/4cd105262aa01f62b88baeda78570325661f67d3) | E2 | architecture as a set of explicit design decisions |

## What this licenses

Each topic note ends in its own "What this licenses" section; together they authorize a second consumer axis in the taxonomy, the merge shape stated at the top of this report, one corpus-level shape-after-reasoning rule referenced by every shape card, and the eval harness the repository does not yet have — binary per-rule checklists, conflict cases, format held constant across compared variants, length control on scores, and a judge from a different provider family than the author. Two rules gain the strongest backing in the corpus: colour redundancy on a Level A conformance criterion, and shape-after-reasoning on a −36.2 pp measurement.

Four things are barred. No card may cite a relay-only source until it is fetched. The two parked claims from the D3 search summary and the dropped o1-preview figure may not be cited at all. Response length is invalid as a success metric, and a readability score is invalid as a style check. No card may claim an accuracy gain from Russian-to-English restatement.

## Implementation debt already scoped

Established in the comparison of the two skills; blocked on the topics above only for citations.

- New target types `doc` (README / spec) and `code` (source comments) in `TARGET_TYPES` (`scripts/audit-workflow.js`), in `rule-cards-taxonomy.md` `applies_to_target`, and in the Phase 0 classification table.
- A new card group (prefix `D-`, group `G10`) with its branch in `groupOf()` and its tier in `GROUP_PRIORITY`.
- Temporal / deliberation markers and identifier smells (`*V2`, `New*`, `Legacy*`) added to `scripts/static-audit.py` as candidate hits requiring human judgement.
- A purge-pass dispatch mode beside gate mode: the scan set is built from a `git diff` (old symbol names + marker grep), git-dependent parts going to `main_agent_followups`.
- The description budget: the auditor's description value is 932 of 1,024 characters (`R-02`), leaving 92 — measured as characters, not bytes; a byte count reads 947 because the value contains a multi-byte character; the new triggers must fit, and the "rather than human documentation" NOT-clause must be rewritten.
- The personal skill's 8 evals (seed files with absent/present assertions) migrate as hands-on evidence; `research/` currently has no eval harness at all.

## D1 — Where output-style rules must live

**Question:** does an
always-loaded ~2,000-token style block change the output, at what per-turn cost,
and is a rule that applies to *every* answer expressible as an on-demand skill?

**Method:** re-read of the repo's own verified findings
(`2026-04-18_context-engineering-research.md`, corrections in
`2026-07-05_context-engineering-update.md`), plus two abstracts fetched
first-hand for the gap the local corpus did not cover — whether style-class
constraints survive as instructions, and how compliance behaves as constraints
accumulate.

### Verdict

Residency is forced, but residency alone does not deliver compliance. The
binding constraint is not token cost — prompt caching makes that cheap after two
reuses — it is **compliance decay**: a resident block of many simultaneous
constraints sits in exactly the regime where instruction-following collapses
(SEQUOR: accuracy "reducing … by over 40%" under multiple simultaneous
constraints, and dropping over a long conversation). So the merge's shape is
**not** "move § Style into a skill", and **not** "leave § Style as it is":

```
operative core   --> hot tier, resident, ordered hard-to-easy, kept small
long form        --> cold tier: rule cards, read when auditing
enforcement      --> audit pass over produced text, not trust in residency
```

### Findings

#### 1. Instructions are followed; overviews are not — style rules are instructions

Gloaguen 2602.11988 §4.3: "the absence of improvements with context files is not
due to a lack of instruction-following" — tools mentioned in a context file were
used 1.6× per instance versus < 0.01× unmentioned, repo-specific tools 2.5×.
What fails is the *repository overview*, not the instruction. The paper's own
keep-list is "context files are useful for specifying non-standard coding
practices" — an idiosyncratic personal style guide is that class.

Counter-finding, recorded honestly: the same paper names style boilerplate among
the categories that cost without paying — "style/overview/testing boilerplate
causes more grep/test/write activity without more solves." Scope boundary: that
was *code*-style guidance measured against SWE-bench solve rate. § Style governs
the prose of the answer, whose outcome is reader comprehension, not solve rate.
The finding constrains code-convention rules; it does not transfer to
answer-prose rules without re-measurement.

#### 2. A style rule cannot be routed, so it cannot live in a skill body

Liu 2604.14228 §6.1, §6.3: skills are the "Low (descriptions only)" tier — only
frontmatter descriptions stay in the prompt; the body is injected lazily by
`SkillTool` when invoked. A rule that governs every answer has no trigger event:
"the user asked about a Java bug and I am about to write the reply" is not a
routable phrase.

Routing is unreliable even when there *is* a topic to match — SkillRouter
2603.22455 §3 Fig 1: routing on name + description alone costs 31.4–44.0 pp
Hit@1 against full-text routing. And retrieval systematically misses this class
of content: Li 2604.11462 §2 — similarity retrieval shows "retrieval bias; they
frequently fail to retrieve implicit reasoning anchors — causally essential
information that may be textually dissimilar to the current query." A style rule
is exactly that: causally essential to the answer, textually unrelated to the
question.

Converging: Pollertlam 2603.04814 §4.1 — always-loaded beats fact-extracted
retrieval by 33.4–35.2 pp (LoCoMo 92.85% vs 57.68%; LongMemEval 82.40% vs
49.00%), and retrieval only wins after ~10 reuses. Vishnyakova 2603.09619 §6
names `CLAUDE.md` as the architectural home for "explicit declarations of goals
and constraints that the agent will see in every session".

#### 3. Compliance decays with conversation length and constraint count — the decisive finding

SEQUOR 2605.06353 (abstract, fetched first-hand): "instruction-following
accuracy consistently decreases as the conversation grows longer, with drops
exceeding 11%"; "This decline becomes larger when models have to follow multiple
constraints simultaneously, reducing their accuracy by over 40%"; and where
"constraints are added or replaced at arbitrary points of the conversation,
model accuracy decreases by more than 9%".

Caveat kept: the abstract does not state whether the 40% is absolute or
relative, and gives no per-model breakdown. A search summary attributed an
"88% → 71% for o1-preview" figure to this area; it was **not** found in the
SEQUOR abstract and is not cited here.

Consistent with material already in the corpus: Tokalator 2604.08290 (context
rot after 20+ turns), Vishnyakova 2603.09619 §9 (context clash — 39% quality
drop when one prompt was split across sequential turns).

Consequence: a 40-rule resident style guide is in the worst regime for
constraint following — many constraints, held simultaneously, over a long
session. Residency buys presence, not obedience.

#### 4. Order among constraints is itself a lever

"Order Matters: Investigate the Position Bias in Multi-constraint Instruction
Following", 2502.17204 (abstract, fetched first-hand): LLMs "show dramatic
performance fluctuation when the order of constraints changes"; the measured
preference is that "LLMs are more performant when presented with the constraints
in a 'hard-to-easy' order", introduced with a Constraint Difficulty Distribution
Index. The abstract reports no numeric spread, and the effect is claimed to
generalize across architectures and parameter sizes.

§ Style is currently ordered by topic (Content → Order → Form → Sentence →
Register) with an explicit precedence clause ("on a collision the earlier step
wins"), which is a *conflict* rule, not a *difficulty* ordering. This is the
concrete input to topic D3.

#### 5. Cost is not the binding constraint; density might be

Tokalator 2604.08290: instruction files are an "invisible budget consumer"
(worked example: 4,200 tokens per prompt), but prompt-caching break-even sits at
n\*=2 reuses on current Anthropic models — from the second turn of a session the
marginal price of a resident block is the cached rate. The +20–23% figure in
Gloaguen is USD inference cost driven by *added agent steps* (2.45 and 3.92 more
steps), not by prompt tokens alone.

The real ceiling is density, not price: Khan 2510.22251 — constrained prompts
help sub-90%-accuracy models and degrade frontier models (OpenAI-only; the
Claude-tier mapping is extrapolation, per the repo's own caveat on R-60). Li
2602.12670 Table 6 — Detailed skills +18.8 pp and Compact +17.1 pp beat Standard
+10.1 pp, while Comprehensive skills *hurt* by −2.9 pp: "Overly elaborate Skills
can consume context budget without providing actionable guidance."

Precedent for a large resident tier exists: Vasilopoulos 2602.20478 §3 runs a
~660-line always-loaded constitution, with over half of each specification being
domain knowledge rather than behavioral instruction.

### What this licenses

- The merged skill owns the **long form** (rule cards, cold tier) and the
  **audit pass**; the hot tier keeps a compressed operative core. Deleting
  § Style outright and relying on skill invocation is ruled out by finding 2.
- A house rule that a resident constraint block is kept small and ordered
  hard-to-easy, with the long form one hop away (findings 3, 4).
- A house rule that style compliance is verified by an audit over produced text
  rather than assumed from residency (finding 3) — this is what topic D2 must
  make operable.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
SEQUOR 2605.06353 (abstract) · multi-turn constraint following: >11% drop with
  conversation length; >40% reduction under simultaneous multiple constraints;
  >9% when constraints are added/replaced mid-conversation · caveat: abstract
  does not state absolute vs relative, no per-model breakdown
Order Matters 2502.17204 (abstract) · constraint order changes performance;
  hard-to-easy ordering preferred; CDDI index · caveat: no numeric spread in
  the abstract
```

Both are new to the repository — they need README reference entries when the
first card cites them.

### Open after D1

Whether a resident style guide measurably improves *answer prose* (as opposed to
mechanically verifiable format constraints) is unresolved and cannot be settled
from the literature: IFEval and its successors verify mechanical constraints —
word counts, JSON format, "start each paragraph with a question" — while the
§ Style core ("open with the answer and its decisive reason") is not mechanically
checkable. That boundary is the agenda for D2.

### Sources

Fetched first-hand for this note, abstract level:

- 2026-05 · [2605.06353](https://arxiv.org/abs/2605.06353) — SEQUOR: A Multi-Turn Benchmark for Realistic Constraint Following
- 2025-02 · [2502.17204](https://arxiv.org/abs/2502.17204) — Order Matters: Investigate the Position Bias in Multi-constraint Instruction Following

Carried from the repository's verified corpus — full entries in
`2026-04-18_context-engineering-research.md`, corrections in
`2026-07-05_context-engineering-update.md`: Gloaguen
[2602.11988](https://arxiv.org/abs/2602.11988), Liu
[2604.14228](https://arxiv.org/abs/2604.14228), SkillRouter
[2603.22455](https://arxiv.org/abs/2603.22455), Li
[2604.11462](https://arxiv.org/abs/2604.11462), Pollertlam
[2603.04814](https://arxiv.org/abs/2603.04814), Vishnyakova
[2603.09619](https://arxiv.org/abs/2603.09619), Tokalator
[2604.08290](https://arxiv.org/abs/2604.08290), Khan
[2510.22251](https://arxiv.org/abs/2510.22251), Li
[2602.12670](https://arxiv.org/abs/2602.12670), Vasilopoulos
[2602.20478](https://arxiv.org/abs/2602.20478).

## D2 — How a style rule is verified

**Question:** the personal skill's
evals assert on substrings (`absent: "used to"`), which cannot express "opens
with the answer" — what method verifies a rule whose check is semantic? D1 made
this load-bearing: residency does not deliver compliance, so an audit over
produced text is the enforcement mechanism, not an optional extra.

**Method:** the repo's existing judge doctrine
(`2026-07-01_critical-thinking-layer-for-research-pipeline.md` §4,
`appraising-research/references/appraisal-methodology.md`) plus four abstracts
fetched first-hand for what that doctrine does not cover — judging *style*
specifically.

### Verdict

Two verification jobs exist, and they carry opposite bias exposure. Separating
them is the whole answer.

```
Job A  per-rule audit over produced text
       one binary question per rule, no comparison
       exposed to: self-preference, the model's own style prior
       NOT exposed to: position bias, pairwise verbosity bias

Job B  eval harness — does the style corpus improve the output?
       pairwise or scored comparison of variants
       exposed to: style bias (dominant), verbosity bias, position bias
       needs: fixed format, length control, order randomization, cross-family judge
```

Job A is what the audit skill already does architecturally — one card, one
validator, one sub-agent — and that architecture is the method the literature
endorses. Job B is what the repository does not have at all, and it is where the
biases are severe.

### Findings

#### 1. Decomposition into binary checks is the method — the corpus already has it

Yang 2505.13360 §A.6 (repo-verified): per-requirement validators reached **95.6%
human–LLM agreement on 1,095 validations** — one validator per rule, not a
holistic score.

Converging, both fetched first-hand:

- CheckEval 2403.18771 (EMNLP 2025): "Existing LLM-as-a-Judge approaches … suffer
  from rating inconsistencies, with low agreement and high rating variance across
  different evaluator models. We attribute this to subjective evaluation criteria
  combined with Likert scale scoring." Decomposing into binary questions
  "dramatically improves the average agreement across evaluator models by **0.45**
  and reduces the score variance", across 12 evaluator models. The paper also
  claims interpretability: "traceable binary decisions".
- TICK 2410.03608 generates instruction-specific checklists of YES/NO questions
  and reports the strongest agreement with human preference. *Not fetched
  first-hand — relayed from a search summary; verify before citing on a card.*

Consequence: what must change is not the audit architecture but the semantic
card's `## Validator` block — it must pose one binary question with a decision
procedure, never "is this good style".

#### 2. Style bias is the dominant judge bias — and a style audit judges exactly that

"Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in
LLM-as-a-Judge Pipelines", 2604.23178 (abstract, fetched first-hand): nine
debiasing strategies × five judge models across four provider families (Google,
Anthropic, OpenAI, Meta), three benchmarks, 975 evaluation pairs, four bias
types. Measured bias magnitudes:

| Bias | Magnitude | Direction |
|--|--|--|
| Style | **0.10–0.76** | favours markdown over plain text |
| Verbosity | +0.24…+0.44 (Pro, Flash, Llama); −0.12 (Claude); −0.04 (GPT-4o) | heterogeneous by family |
| Position | ≤ 0.04 | minor |

Style bias dominates and points at markdown. Two direct consequences for this
corpus: § Voice spans are plain prose by construction, so any comparative judge
will systematically undervalue them; and § Style's prose-versus-structure rule
(prose for a connected causal chain, structure for co-orderable items) is judged
by an evaluator predisposed to structure. Both are Job B exposures — fix the
format across compared variants rather than trusting the judge.

Debiasing pays where it is applied: Claude +11.5 pp and +7.3 pp under two
strategies, Flash +7.5 pp, Llama +4.5 pp. Best cost-performance was Gemini 2.5
Flash with a combined strategy at **71.0% agreement (κ = 0.549)** for roughly
$0.001 per evaluation.

#### 3. On Claude the verbosity bias runs toward brevity — the audit over-cuts

Claude judges prefer concise answers (−0.12) where Gemini and Llama prefer longer
ones. The audit runs on Claude, and § Style's rules are largely cutting rules, so
judge bias and rule direction point the same way: the systematic error is
**over-flagging deletions**, not missing them.

The corrective already exists in `documenting-present-design`: the residual-fact
test — strip the framing, keep the rewrite only if a self-standing fact survives.
Carried into the corpus, every delete-class patch must name the fact that
survives, or the patch is a recommendation rather than an edit.

#### 4. The audit's blind spot is the model's own default style

Self-preference is established in the repo's doctrine: Zheng 2306.05685 (a model
rates text in its own style more favourably; corroborated by 2410.21819), with
sycophancy (Sharma 2310.13548) and the finding that pure self-reflection can
worsen results (Huang et al. 2023, ICLR 2024) — which is why the skill already
demands a fresh session (G-05).

Sharpened for style: the author is Claude and the judge is Claude, so the audit
will under-flag exactly Claude's native habits — and most of § Style is written
*against* the model's default register (filler openers, echo summaries, offers of
further work, hedging). A rule aimed at a default the judge shares cannot be
enforced by asking the judge whether the prose is good. It must be posed as an
explicit positive checkable item — the constitution pattern of Bai 2212.08073,
which the repo already uses for its critic agents.

#### 5. The agreement ceiling justifies the corpus's existing `needs_human` default

Even the best-configured cheap judge reached 71.0% agreement (κ = 0.549) —
moderate, not substitutable for review. The corpus's `check_kind: semantic` →
`proposed: null` + `needs_human: true` convention is therefore correct as it
stands and must be preserved for every style card whose check is not mechanical.

#### 6. Length control is a Job B statistical correction, not a per-patch one

Length-Controlled AlpacaEval 2404.04475 (abstract, fetched first-hand) fits "a
generalized linear model to predict the biased auto-annotator's preferences based
on the mediators we want to control for (length difference)", then predicts
"while conditioning the GLM with a zero difference in lengths", answering the
counterfactual "What would the preference be if the model's and baseline's output
had the same length?". This "increases the Spearman correlation with LMSYS
Chatbot Arena from 0.94 to 0.98."

Applicable to the eval harness comparing corpus-on against corpus-off outputs;
not applicable to a per-rule audit, which makes no length comparison.

### What this licenses

- **Card schema, semantic validators.** A style card's `## Validator` states one
  binary question plus a decision procedure. Holistic quality scoring is excluded
  by finding 1.
- **Delete-class patches carry the surviving fact** (finding 3), else they are
  recommendations.
- **Eval harness design** (Job B), the repository's current blank: per-rule
  binary checklists instead of substring assertions for semantic rules; substring
  assertions kept where the rule is mechanical — marker greps for history
  artifacts genuinely work and the personal skill's 8 evals are reusable as-is
  for that half; a judge from a different provider family than the author; format
  held constant across compared variants; length control on scores; order
  randomized (cheap, low yield at ≤ 0.04); the judge model pinned and re-run on
  upgrade, repeated per the corpus's existing repetition rule.
- **Preserving `needs_human` on semantic style cards** (finding 5).

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Judging the Judges 2604.23178 (abstract) · 9 strategies × 5 judges × 4 families,
  975 pairs · style bias dominant 0.10–0.76 (markdown over plain text); verbosity
  heterogeneous (+0.24…+0.44 Pro/Flash/Llama, −0.12 Claude, −0.04 GPT-4o);
  position ≤0.04; best cheap config 71.0% agreement, κ=0.549
CheckEval 2403.18771 (EMNLP 2025, abstract) · binary-question decomposition
  raises average cross-model agreement by 0.45 and cuts score variance;
  12 evaluator models
Length-Controlled AlpacaEval 2404.04475 (abstract) · GLM conditioned on zero
  length difference; Spearman vs Chatbot Arena 0.94 → 0.98
TICK 2410.03608 · generated YES/NO checklists; NOT first-hand verified
```

All four are new to the repository; README entries follow the first citing card.

### Open after D2

Whether the style corpus actually improves answer prose remains unmeasured — D2
supplies the instrument, not the reading. Running Job B once the first style
cards exist is the natural close, and its result belongs in this file's successor
rather than in a card.

### Sources

Fetched first-hand for this note, abstract level:

- 2026-04 · [2604.23178](https://arxiv.org/abs/2604.23178) — Judging the Judges: A Systematic Evaluation of Bias Mitigation Strategies in LLM-as-a-Judge Pipelines
- 2024-03 · [2403.18771](https://arxiv.org/abs/2403.18771) — CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists (EMNLP 2025; [ACL Anthology](https://aclanthology.org/2025.emnlp-main.796/))
- 2024-04 · [2404.04475](https://arxiv.org/abs/2404.04475) — Length-Controlled AlpacaEval: A Simple Way to Debias Automatic Evaluators

Relayed from a search summary, **not** fetched — verify before citing on a card:

- 2024-10 · [2410.03608](https://arxiv.org/abs/2410.03608) — TICKing All the Boxes: Generated Checklists Improve LLM Evaluation and Generation

Carried from the repository's corpus: Yang
[2505.13360](https://arxiv.org/abs/2505.13360) §A.6, Nair
[2506.00178](https://arxiv.org/abs/2506.00178), Dong
[2512.14754](https://arxiv.org/abs/2512.14754); and via
`2026-07-01_critical-thinking-layer-for-research-pipeline.md` §4 — Zheng
[2306.05685](https://arxiv.org/abs/2306.05685), Sharma
[2310.13548](https://arxiv.org/abs/2310.13548), Bai
[2212.08073](https://arxiv.org/abs/2212.08073), self-preference corroboration
[2410.21819](https://arxiv.org/abs/2410.21819), and Huang et al. 2023 (ICLR 2024)
on self-reflection.

## D3 — Precedence or merging, for a corpus of ~100 rules

**Question:** § Style declares a
resolution order ("on a collision the earlier step wins") where `R-70` demands
contradictions be merged into one rule with explicit conditions. Which is right
at corpus scale — and is a declared precedence obeyed at all?

**Method:** four abstracts fetched first-hand, plus the corpus's own `R-70` and
`GROUP_PRIORITY`, whose current backing is a house procedure over Hong 2025's
primacy effect.

### Verdict

Merging wins for runtime conflicts; declared precedence does not work as an
enforcement mechanism and must be demoted to maintainer guidance. The one place
precedence *is* reliable is where the corpus already puts it — in executed code.

```
conflict between two rules  --> merge into one rule with explicit conditions (R-70)
precedence among peer rules --> maintainer guidance only; not obeyed at runtime
precedence that must hold   --> execute it (GROUP_PRIORITY in JS), never declare it
```

### Findings

#### 1. An unresolved contradiction fails silently — the model sees it and says nothing

ConInstruct 2511.14342 (abstract, first-hand) benchmarks conflict detection and
resolution *within user instructions*. Two findings: "Most proprietary LLMs
exhibit strong conflict detection capabilities … DeepSeek-R1 and Claude-4.5-Sonnet
achieve the highest average F1-scores at **91.5%** and **87.3%**, respectively";
and "Despite their strong conflict detection abilities, LLMs **rarely explicitly
notify users about the conflicts or request clarification** when faced with
conflicting constraints."

Consequence for a rule corpus: a contradiction between two cards does not raise an
error. The model detects it, silently picks one, and produces a plausible answer.
Nothing in the output marks the arbitrary choice. This upgrades `R-70` from a
house procedure to measured behaviour, and it independently justifies an existing
house convention — the audit's Phase 2a conflict flagging with `needs_human` —
because the *audit* must surface what the runtime model will not.

#### 2. A declared precedence is not reliably obeyed

IH-Benchmark 2607.25987 (abstract, first-hand) measures instruction-hierarchy
compliance on system-over-user and user-over-tool conflicts across **37 models**:
compliance ranges from **98.2% down to 20.5%**. On strengthening the wording —
"constraint hardening" — "some failures are largely fixed by stronger warnings,
while others persist across all strictness levels."

Scope caveat, load-bearing: this measures *privilege* hierarchies between message
roles, not precedence among peer rules inside one document. Applying it to
§ Style's "earlier step wins" is an extrapolation and must be recorded as one.
The extrapolation runs in the pessimistic direction, though — role hierarchies are
the case models are explicitly trained for, and peer-rule precedence is not.

#### 3. Hierarchies work when trained, not when declared

Wallace 2404.13208 (abstract, first-hand) proposes "an instruction hierarchy that
explicitly defines how models should behave when instructions of different
priorities conflict", then contributes "a data generation method to demonstrate
this hierarchical instruction following behavior, which teaches LLMs to
selectively ignore lower-privileged instructions", applied to GPT-3.5 with
robustness that "drastically increases … even for attack types not seen during
training — while imposing minimal degradations on standard capabilities."

The contribution is the *training*, not the declaration. A precedence clause
written inside a user-authored document rides on whatever the model was trained to
respect between roles; precedence among peer rules within one document has no
trained backing at all. This is the decisive argument: § Style's collision clause
sits at a level nothing enforces.

#### 4. The conflict dimensions of a style corpus are exactly the studied ones

PRIME 2606.22470 (abstract, first-hand) "purposefully produces calibrated
conflicts across **response length, output format, and reasoning**; classifying
model responses with a deterministic behavioral taxonomy", over five
instruction-tuned open-weight models. Its conclusion: "**conflict type is more
significant in affecting behavior than model scale**", and "ability of LLM to
follow instructions cannot be assessed through isolated constraints alone."

Those three dimensions are precisely what § Style and § Screen legislate — brevity
rules (length), the print-form table (output format), and premise-versus-conclusion
order (reasoning). Two consequences: a stronger model will not absorb corpus
contradictions, and the D2 eval harness must include conflict cases, since per-rule
checks in isolation cannot detect this failure class.

#### 5. Ordering of the resident core

From D1: Order Matters 2502.17204 finds models "more performant when presented
with the constraints in a 'hard-to-easy' order". Combined with the corpus's `R-14`
(load-bearing rules near the top, on Hong 2025's primacy effect), the resident
core's ordering rule is: hardest and most load-bearing first. The two sources
agree in direction and neither gives a numeric spread.

### What this licenses

- **`R-70` keeps its thesis and gains real provenance** — ConInstruct's silent-
  resolution finding plus PRIME's conflict-type dominance replace the house
  procedure. Merging into one rule with explicit conditions stays the primary
  treatment.
- **A new rule against declared peer precedence**: a working file states the
  merged rule, not a precedence clause between rules; where a precedence must
  hold, it is executed rather than declared. `GROUP_PRIORITY` in
  `scripts/audit-workflow.js` is the corpus's own instance of the correct pattern
  and now has a justification rather than being a bare house convention.
- **§ Style's collision clause is re-labelled** when the section is restructured
  for the merge: it is guidance to the maintainer about which rule survives an
  edit, not an instruction the model obeys at runtime.
- **The eval harness gains conflict cases** (PRIME) — an addition to D2's design.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
ConInstruct 2511.14342 (abstract) · conflict detection within user instructions:
  DeepSeek-R1 91.5% F1, Claude-4.5-Sonnet 87.3% F1; models rarely notify the user
  of a detected conflict or ask for clarification
IH-Benchmark 2607.25987 (abstract) · instruction-hierarchy compliance across 37
  models spans 98.2%–20.5%; constraint hardening fixes some failures, others
  persist at every strictness level · caveat: measures role privilege, not
  peer-rule precedence — extrapolation
Wallace 2404.13208 (abstract) · hierarchy compliance is obtained by training
  (data-generation method), not by declaration; GPT-3.5, generalizes to unseen
  attacks, minimal capability loss
PRIME 2606.22470 (abstract) · calibrated conflicts over response length, output
  format, and reasoning; conflict type outweighs model scale; isolated-constraint
  evaluation cannot assess conflict behaviour · no numbers in the abstract
```

All four are new to the repository.

### Parked — claimed in a search summary, not found in any fetched source

A search summary asserted "GPT-4o achieved only 63.8% obedience to designated
priority instructions even with explicit emphasis" and that "societal hierarchy
framings (authority, expertise, consensus) showed stronger influence than
system/user roles". Neither appears in the ConInstruct, PRIME, IH-Benchmark, or
Wallace abstracts fetched here; the summary appears to have conflated sources.
Both claims are unattributed and must not be cited. The second is interesting
enough to chase separately if peer-rule precedence is ever revisited.

### Open after D3

Whether a *merged* conditional rule is itself followed better than the two rules
it replaced is unmeasured here. It is a Job B question in D2's harness, not a
literature question.

### Sources

Fetched first-hand for this note, abstract level:

- 2025-11 · [2511.14342](https://arxiv.org/abs/2511.14342) — ConInstruct: Evaluating Large Language Models on Conflict Detection and Resolution in Instructions
- 2026-07 · [2607.25987](https://arxiv.org/abs/2607.25987) — IH-Benchmark: A Conflict-Centered Benchmark for Instruction-Hierarchy Robustness in LLM Applications
- 2024-04 · [2404.13208](https://arxiv.org/abs/2404.13208) — Wallace et al., The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions
- 2026-06 · [2606.22470](https://arxiv.org/abs/2606.22470) — PRIME: Evaluating Prompt Resolution Under Incompatible Instructions in LLMs

Carried from D1: [2502.17204](https://arxiv.org/abs/2502.17204) — Order Matters.
From the repository's corpus: Hong 2025 Context Rot (positional / primacy bias,
backing `R-14` and `R-70`) and the corpus's own `GROUP_PRIORITY` in
`scripts/audit-workflow.js`.

## A1 — Order of exposition

**Question:** what is the measured
effect of answer-first ordering and given–new sentence structure on comprehension,
and does it hold for expert readers?

**Method:** the original Haviland & Clark 1974 paper read first-hand from the scanned
PDF (text extraction fails on it — the numbers below come from the page images),
plus one fetched abstract and one relayed counter-finding.

### Verdict

§ Style's second section states two ordering rules and asserts that they "sit at
different scales and do not conflict". The evidence for the two is very
different, and the section should not present them as one law:

| Rule | Scale | Evidence |
|--|--|--|
| Open on what the reader holds, end on the new | sentence | measured, replicated, confound-controlled |
| Open with the answer and its decisive reason | document | a scanning convention; the comprehension and recall claim is contested |

A third constraint appears from the generation side: answer-first is free only
when the reasoning has already happened out of sight.

### Findings

#### 1. Given–new at sentence scale is measured, replicated, and confound-controlled

Haviland & Clark 1974 (*Journal of Verbal Learning and Verbal Behavior* 13,
512–521) state the strategy: the reader extracts the Given information, searches
memory for a matching Antecedent, and attaches the New information to it. With no
direct antecedent the reader must build an inferential bridge — "these additional
steps will take time." Comprehension time was measured by button press on a
target sentence preceded by a context sentence.

| Experiment | Direct antecedent | Indirect | Difference | Statistic | n |
|--|--|--|--|--|--|
| I (68 pairs) | 835 ms | 1016 ms | **181 ms** | minF'(1,36) = 6.47, p < .025 | 16 |
| II (repetition controlled) | 1031 ms | 1168 ms | **137 ms** | minF'(1,23) = 15.7, p < .001 | 10 |
| III (144 pairs, adverbs) | 1023 ms | 1097 ms (indirect), 1088 ms (negative) | — | — | 27 |

Experiment II exists precisely to kill the obvious confound: in Experiment I every
Direct pair repeated a noun and no Indirect pair did, so the effect might have
been mere lexical repetition. Experiment II gave both conditions the repetition
and the gap survived — "mere repetition of the critical noun is not enough to
account for the results of Experiment I."

Limits, stated plainly: subjects were Stanford undergraduates, not domain experts;
materials were two-sentence pairs, not extended technical prose; the measure is
self-paced comprehension time, not error rate or retention; the work is from 1974.
The direction is robust across three experiments; the transfer to expert readers
of technical documents is an extrapolation.

#### 2. Document-level answer-first has no comparable support — and a counter-finding

**The counter-finding did not survive verification.** See
[§ Verification — news structure and comment drift](#verification--news-structure-nominalisation-passive-voice-comment-drift).

Two failures. First, the PDF I relied on is not Lang (1989) at all — it is
Sternadori's 2008 University of Missouri dissertation, which cites Lang in text.
Lang (1989) is real ([doi:10.1080/08838158909364093](https://doi.org/10.1080/08838158909364093),
JoBEM 33(4):441–452) but paywalled and unread; it studies *broadcast television*
news, law-enforcement stories only, and is exploratory.

Second, the dissertation is the closest print-medium test of exactly the transfer
I was making, and it runs the other way: recognition null (F(1,50) = .01,
p = .94), cued recall null (F(1,50) = 1.32, p = .26), and comprehension trending
toward the *inverted pyramid* (F(1,49) = 3.20, p = .08). Its H3 — the "complex
topics favour chronological" clause I relayed — was disconfirmed.

So there is no measured comprehension advantage for the inverted pyramid, and no
measured disadvantage either. What the dissertation does measure in its favour is
processing cost: secondary-task reaction time 396.4 ms against 412.7 ms for
chronological (F(1,44) = 3.92, p = .05). The answer-first order costs the reader
less to process while costing nothing on recall — and that, not scanning, is what
card S-24 rests on.

The scanning and stop-anywhere benefit — the one § Style actually claims — has no
admissible source. Its only located support is Nielsen Norman Group practitioner
guidance, which the repository's Evidence-Based Rule excludes on the same ground as
a trade book. S-24 therefore drops the scanning wording entirely rather than
carrying an unsourceable rationale.

§ Style's existing exception stays a **house heuristic**, not an evidence-backed
condition. "Switch to premise→conclusion when the conclusion is contestable for
this reader, or inseparable from a prior step" was justified by the clause that
complex material fares better in sequential order — and that clause is this
dissertation's H3, which finding 2 above records as **disconfirmed**. The card
labels it a house heuristic for exactly that reason.

#### 3. Answer-first presupposes that reasoning already happened

Lanham et al. 2307.13702 (abstract, fetched first-hand) opens on the established
result: "Large language models (LLMs) perform better when they produce
step-by-step, 'Chain-of-Thought' (CoT) reasoning **before answering** a question".
The paper's own contribution is about faithfulness — "As models become larger and
more capable, they produce less faithful reasoning on most tasks we study" — and
it notes that CoT's benefit "does not seem to come from CoT's added test-time
compute alone or from information encoded via the particular phrasing of the CoT".

Consequence for the rule: opening the *visible* answer with the conclusion costs
nothing when reasoning precedes the visible output, which is the case with an
extended-thinking block. Where no such block exists, "open with the answer" asks
the model to commit before reasoning, and the ordering rule for the reader
collides with the generation order that produces a correct answer. The card must
carry that precondition.

### What this licenses

- **A sentence-scale card**, `check_kind: semantic`, carrying the 137–181 ms
  spread and the bridging mechanism: open a sentence on the antecedent the reader
  already holds, end it on the new element.
- **A document-scale card** whose rationale is stop-anywhere scanning and early
  decision, explicitly *not* comprehension or recall, with the
  premise→conclusion condition for contestable or dependent conclusions.
- **A precondition on the answer-first rule**: it applies to the visible answer
  and presumes reasoning has already occurred; it is not an instruction to decide
  the answer first.
- Separating the two scales in § Style when the section is restructured — the
  present text presents them as one law with one justification, and they do not
  share evidence.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Haviland & Clark 1974, JVLVB 13:512–521 · given-new comprehension time:
  Exp I 835 vs 1016 ms (Δ181, minF'(1,36)=6.47, p<.025, n=16); Exp II with
  repetition controlled 1031 vs 1168 ms (Δ137, minF'(1,23)=15.7, p<.001, n=10);
  Exp III 1023 / 1097 / 1088 ms (n=27) · caveat: undergraduates, sentence pairs,
  comprehension-time measure — transfer to expert technical prose is extrapolation
Lanham 2307.13702 (abstract) · CoT reasoning before answering improves
  performance; larger models produce less faithful stated reasoning
Lang 1989 · inverted-pyramid news yields less knowledge gain and poorer memory
  than chronological structure · NOT first-hand verified — relay only
```

### Sources

Read first-hand for this note:

- Haviland, S. E. & Clark, H. H. (1974). *What's new? Acquiring new information as
  a process in comprehension.* Journal of Verbal Learning and Verbal Behavior 13,
  512–521 — [scanned PDF](https://web.stanford.edu/~clark/1970s/Haviland,%20S.E.%20_%20Clark,%20H.H.%20_What's%20new_%20Acquiring%20new%20information%20as%20a%20process%20in%20comprehension_%201974.pdf)
  (numbers taken from the page images; text extraction fails on this scan)
- 2023-07 · [2307.13702](https://arxiv.org/abs/2307.13702) — Lanham et al.,
  Measuring Faithfulness in Chain-of-Thought Reasoning

Relayed, **not** verified — verify before citing on a card:

- Lang, A. (1989) on cognitive processing of news as a function of structure, via
  [this PDF](https://pdfs.semanticscholar.org/f2eb/ad1fa4020d0647314314457ec2c003516087.pdf)
- Nielsen Norman Group, [Inverted Pyramid: Writing for Comprehension](https://www.nngroup.com/articles/inverted-pyramid/)
  — practitioner guidance, useful for the scanning claim, not an experiment

Related theory not consulted here and still open: Clark & Haviland (1977),
*Comprehension and the given-new contract*; Gopen & Swan (1990) on topic and
stress position, whose status as expert essay rather than experiment must be
checked before it backs a card.

### Open after A1

Whether the sentence-scale effect holds for expert readers of technical prose is
untested in the source and stays an extrapolation on the card. Gopen & Swan's
stress-position doctrine — the other half of § Style's sentence rule — is
unexamined and is the first thing A2 should settle, since A2 covers sentence
load.

## A2 — Sentence load

**Question:** which sentence
features actually predict reading difficulty — nesting, subject–verb distance,
claims per sentence — and what serves as a measurable check now that readability
formulas are discredited? Plus the question A1 handed over: is Gopen & Swan's
stress-position doctrine an experiment or an expert essay?

**Method:** Gibson's DLT chapter read first-hand from the page images (the 8.8 MB PDF
does not extract as text), one arXiv abstract fetched first-hand, two search
sweeps.

### Verdict

§ Style's section title — "reduce reading load before length" — is exactly what
the literature says, and the section's central sentence rule is well founded.
Its two numeric thresholds are not.

| § Style claim | Status |
|--|--|
| Prefer a long left-to-right sentence over a short one nesting a clause in the middle | **supported** — Gibson's minimal pair: same words, reordered, easier |
| Keep the subject next to its verb | **supported** — an unresolved subject–verb link is an open dependency held across everything between |
| New sentence at a second level of nesting | proxy the field moved away from — the load is the peak count of open dependencies, not depth |
| One claim per sentence, two at most | no evidence found — house convention |
| Readability score as the measurable check | **ruled out** — formulas, commercial systems and frontier LLMs are all poor predictors |

### Findings

#### 1. The driver is open dependencies, not length

Gibson (2000), *The Dependency Locality Theory*, pp. 97–98, states the
nesting-complexity account it builds on: "difficulty is indexed by the maximal
number of incomplete syntactic dependencies that the processor has to keep track
of during the course of processing a sentence." His worked series: sentence (1a)
holds at most one incomplete dependency; (1b) holds three at the point of
processing *the senator*; (1c) holds five at the point of processing *John* —
"Thus (1c) is the most difficult to understand of the three."

The decisive demonstration is the Japanese pair. (3c) and (4) carry the same
propositional content in the same words; (4) fronts the clausal object so that
"this clause is no longer nested between the subject NP … and the verb", and
Gibson concludes "Sentence (4) is therefore easier to understand than (3c)."
Same length, same content, different order, different difficulty. That is the
evidence § Style's long-left-to-right rule needs, and it is not an argument about
brevity.

The same mechanism explains the subject-next-to-verb rule: while the verb is
outstanding, the subject's dependency stays open and every intervening word is
carried under it.

Scope note kept honest: the passage I read is Gibson's §5.2, "Previous Theories
of Nesting Complexity" — the incomplete-dependency hypothesis he then refines
into DLT proper with distance-based integration and storage costs. I extracted
the mechanism and the demonstration, not DLT's own quantitative formulation; a
card citing integration-cost numbers would need a further pass.

#### 2. Nesting depth is the wrong counter

Gibson's own move is from *counting nestings* to *distance and peak open
dependencies*, and a later study — "The Limited Role of Number of Nested
Syntactic Dependencies in Accounting for Processing Cost: Evidence from German
Simplex and Complex Verbal Clusters" — argues the count contributes little on its
own. *Relayed from a search result, not fetched.*

Consequence: § Style's "a second level of nesting starts a new sentence" is a
usable heuristic but its stated trigger is the weaker proxy. The validator should
ask how many dependencies stand open at the sentence's hardest point, and whether
anything sits between a subject and its verb.

#### 3. Readability formulas cannot serve as the measurable check — and neither can an LLM rating

Shubi et al., arXiv:2502.11150 (abstract, fetched first-hand), evaluates against
real-time reading ease measured by eye tracking, "while controlling for content
variation across texts". The result covers everything one might reach for:
"prominent traditional readability formulas, NLP-based methods, commercial
systems used in education, and frontier LLMs … are all poor predictors of English
reading ease in adults as compared to word properties commonly used in
psycholinguistics for the prediction of reading times." It holds "across L1 and
L2 speakers, different reading regimes, and textual units of different lengths".

Two consequences. For A2: the check is structural (open dependencies, subject–verb
adjacency), not a score. For D2: an LLM judge asked to rate readability is a poor
instrument — an independent confirmation of D2's conclusion that holistic scoring
must give way to per-rule binary questions.

#### 4. Gopen & Swan is an expert essay, not an experiment — A1's handover, settled

"The Science of Scientific Writing", *American Scientist* 78(6):550–558 (1990),
is a feature article presenting rhetorical principles through worked rewrites. No
experiment, validation study, or replication surfaced. Under the repository's
evidence rule it cannot back a card on its own.

It does not need to. Its topic-position / stress-position doctrine restates the
given–new contract for writers, and that has measured backing from A1 (Haviland &
Clark 1974: 137–181 ms penalties, confound-controlled). The card cites Haviland &
Clark; Gopen & Swan may be named as the practitioner formulation, never as the
evidence.

### What this licenses

- **A sentence-structure card**, `check_kind: semantic`: no clause between a
  subject and its verb; where a clause must be embedded, reorder to left-to-right
  rather than shorten. Rationale cites open dependencies; the example is Gibson's
  reordering pair.
- **A statement that sentence length is not the check** — this replaces
  length-based advice rather than supplementing it.
- **Two house numbers flagged**: "two claims at most" and "second level of
  nesting" have no located support. Under the repository's rule they need a linked
  hands-on test or must lose the number and become a heuristic.
- **A negative result for the D2 harness**: readability scores and LLM readability
  ratings are invalid instruments for this rule class.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Gibson 2000, DLT chapter pp. 97–98 · difficulty indexed by the maximal number of
  incomplete syntactic dependencies held at once (1 / 3 / 5 across the worked
  series); the Japanese pair (3c) vs (4) — same words reordered out of a nesting
  is easier · caveat: passage is §5.2, the predecessor account DLT refines;
  integration-cost numbers not extracted
Shubi et al. 2502.11150 (abstract) · against eye-tracking reading ease, readability
  formulas, NLP methods, commercial systems and frontier LLMs are all poor
  predictors versus psycholinguistic word properties; holds across L1/L2, reading
  regimes, and text lengths
Gopen & Swan 1990, American Scientist 78(6):550–558 · expert essay, no experiment
  located — usable as a practitioner formulation only
```

### Sources

Read or fetched first-hand for this note:

- Gibson, E. (2000). *The dependency locality theory: A distance-based theory of
  linguistic complexity*, pp. 95–126 —
  [PDF](https://tedlab.mit.edu/tedlab_website/researchpapers/Gibson_2000_DLT.pdf)
  (pp. 97–98 read from page images; text extraction fails on this file)
- 2025-02 · [2502.11150](https://arxiv.org/abs/2502.11150) — Readability Formulas,
  Systems and LLMs are Poor Predictors of Reading Ease

Relayed, **not** verified — verify before citing on a card:

- [The Limited Role of Number of Nested Syntactic Dependencies in Accounting for
  Processing Cost](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5787339/) —
  German verbal clusters
- Gopen, G. D. & Swan, J. A. (1990). The Science of Scientific Writing.
  *American Scientist* 78(6):550–558 —
  [PDF](https://www.usenix.org/sites/default/files/gopen_and_swan_science_of_scientific_writing.pdf)
  (read for classification only; no experiment to verify)

Not consulted, still open: Gibson (1998), *Linguistic complexity: locality of
syntactic dependencies*, Cognition 68:1–76 — the primary statement, which would
supply DLT's quantitative formulation; Levy (2008) on surprisal, and the question
of whether expectation or locality better predicts reading time.

### Open after A2

Whether the nominalization and actor-as-subject rule ("the parser rejects the
token", not an impersonal passive) has experimental support is untouched here —
it belongs with A2's subject matter but was not reached. It joins A3's queue.

## A3 — What may be cut

**Question:** which verbosity
patterns are training artifacts, which cuts lose information, whether a "be brief"
instruction degrades reasoning — plus the nominalization / actor-as-subject rule
handed over by A2.

### Verdict

Verbosity is a measured artifact of how the models were trained, so § Style's
cutting rules correct a known bias rather than impose taste. But compression has a
task-specific floor, and the floor lives in the reasoning, not in the prose. The
rule survives exactly in the form § Style already uses — cut what is not
load-bearing — and fails in the form it avoids: a length target.

### Findings

#### 1. Verbosity is an artifact of reward modelling

Singhal et al., arXiv:2310.03716 (abstract, fetched first-hand): "optimizing for
response length is, much more than previously thought, a significant factor behind
RLHF"; reward improvements are "largely … driven by increasing response length,
instead of other features"; and decisively, "even a purely length-based reward
reproduces most downstream RLHF improvements over supervised fine-tuned models."
The cause is located: "the dominant source of these biases to be reward models,
which … are non-robust and easily influenced by length biases in preference data."
Three settings; the abstract gives no percentage.

This reframes the whole cutting section. Filler openers, echo summaries and
offers of further work are not a stylistic weakness to be discouraged — they are
the residue of an optimization target, and a rule that removes them is a
correction. It also aligns with D2's finding that a Claude judge prefers concise
answers (−0.12): the auditor's bias and the rule point the same way, which is
useful for enforcement and dangerous for over-cutting.

#### 2. Compression has a floor, and it is task-specific

Lee et al., arXiv:2503.01141 (abstract, fetched first-hand) runs "the first
systematic study of the relationship between reasoning length and model
performance across a diverse range of compression instructions". It reports "a
universal tradeoff between reasoning length and accuracy" arising "from a sharp
threshold behavior at the question level: each task has an intrinsic 'token
complexity' — a minimal number of tokens required for successful problem-solving."
Prompt-based compression "operate[s] far from these theoretical limits", and the
paper argues for "adaptive compression — giving shorter responses for easier
questions".

Relayed, not verified: a "be concise" instruction reportedly cut length ~49% with
little effect on most tasks but cost GPT-3.5 28% on maths, and a 1,024-token
budget dropped Phi-4-reasoning to 53.48%, an 18.75-point absolute loss. Direction
consistent with the above; do not cite the numbers without fetching.

#### 3. The floor is in the reasoning, so the boundary is the same one A1 found

The measured trade-off is about *reasoning* length. § Style governs the visible
answer. When reasoning happens in a thinking block, cutting the answer does not
touch token complexity and the trade-off does not apply. Without such a block, a
brevity instruction spends the reasoning budget, and that is where the sharp drops
come from.

Card consequence: the cutting rules carry a scope line — they apply to the
delivered answer, never to the reasoning budget — and adaptive compression is the
policy, which is what "cut a fragment when the rest still says the same thing"
already encodes.

#### 4. Nominalization: supported in direction, with the qualifier doing real work

**Verified first-hand, with two corrections.** See
[§ Verification — news structure and comment drift](#verification--news-structure-nominalisation-passive-voice-comment-drift).

Wolfer (2016), on the Freiburg Legalese Reading Corpus, measures a strong and
confirmed *reading-time* effect — total reading time β = 0.131, t = 8.911;
nominalisation estimate 0.053 against 0.016 for finite verbs. But his
comprehension questions showed no gain at all (84% / 88% / 87%), and he says so.
So the claim is that nominalisations slow **reading**, not that they harm
comprehension; my earlier wording overstated it.

The counterweight is Ferreira (2021), *In Defense of the Passive Voice*,
*American Psychologist* 76(1):145–153 — a review essay with no new data. It does
**not** endorse the narrower "hides who acts" trigger I attributed to it: on her
account omitting the agent is usually the right choice. The defensible residue is
narrower still — flag an agentless passive only where the agent is both known and
material to the reader.

### What this licenses

- **A cutting card** whose test is whether removal changes truth or scope, with an
  explicit prohibition on length targets as the criterion. Rationale: verbosity is
  a reward-model artifact; blanket compression meets a task-specific floor.
- **A scope line** on every cutting rule: the delivered answer, not the reasoning.
- **An actor-as-subject card** keeping the "hides who acts" qualifier, with the
  passive not banned.
- **For the D2 harness**: response length is invalid as a success metric, both
  because it is the artifact being corrected and because it is confounded with
  task difficulty.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Singhal 2310.03716 (abstract) · a purely length-based reward reproduces most
  downstream RLHF improvements over SFT; reward models are the dominant source of
  length bias · three settings; no percentage in the abstract
Lee 2503.01141 (abstract) · universal reasoning-length/accuracy tradeoff from a
  sharp per-question threshold — an intrinsic "token complexity"; prompt-based
  compression operates far from the information-theoretic limit; adaptive
  compression is the recommended policy
Freiburg Legalese Reading Corpus case study · nominalisations slow comprehension;
  converting to verbal structures resolves it · NOT verified — relay only
In Defense of the Passive Voice, American Psychologist · counterweight against a
  blanket passive ban · NOT verified — relay only
```

### Sources

Fetched first-hand:

- 2023-10 · [2310.03716](https://arxiv.org/abs/2310.03716) — A Long Way to Go: Investigating Length Correlations in RLHF
- 2025-03 · [2503.01141](https://arxiv.org/abs/2503.01141) — How Well do LLMs Compress Their Own Chain-of-Thought? A Token Complexity Approach

Relayed, **not** verified — verify before citing on a card:

- [Freiburg Legalese Reading Corpus case study](https://langsci-press.org/catalog/view/108/298/512-1) — nominalisation and comprehension
- [In Defense of the Passive Voice](https://psycnet.apa.org/manuscript/2020-19385-001.pdf), American Psychologist
- [Do LLMs Overthink Basic Math Reasoning? (2507.04023)](https://arxiv.org/abs/2507.04023) and [Stop Overthinking (2503.16419)](https://arxiv.org/abs/2503.16419) — the relayed 28% / 18.75-point figures
- [One Step at a Time: active, be-passive and get-passive forms](https://journalofcognition.org/articles/10.5334/joc.36)

### Open after A3

Sycophancy as a distinct source of filler (as opposed to length bias) was not
separated here; Sharma 2310.13548 is already in the repository's corpus via the
critical-thinking note and covers it if a card needs the distinction.

## A4 — Calibrated uncertainty

**Question:** which forms of
expressed uncertainty improve the reader's calibration, and which increase
overreliance?

### Verdict

§ Style's rule — "state a load-bearing uncertainty in the first person" — is the
one house rule so far that matches an experiment on its exact wording: the
first-person form is what reached significance, the impersonal form did not. And
a second result changes the standing of the cutting rules: unnecessary length
raises the reader's confidence without raising accuracy, so cutting is a
calibration measure, not only an economy one.

### Findings

#### 1. First person is the form that works — impersonal is not significant

Kim et al., arXiv:2405.00623 (FAccT 2024; abstract fetched first-hand). Design:
"a large-scale, pre-registered, human-subject experiment (N=404) in which
participants answer medical questions with or without access to responses from a
fictional LLM-infused search engine."

Result: "first-person expressions (e.g., 'I'm not sure, but...') decrease
participants' confidence in the system and tendency to agree with the system's
answers, **while increasing participants' accuracy**." The mechanism is named:
"this increase can be attributed to reduced (but not fully eliminated)
overreliance on incorrect answers."

The asymmetry is the load-bearing part: "While we observe similar effects for
uncertainty expressed from a general perspective (e.g., 'It's not clear,
but...'), these effects are weaker and **not statistically significant**." The
paper's own conclusion — "the precise language used matters."

So the rule is not "hedge"; it is "hedge in the first person". An impersonal
hedge is measured and found wanting.

#### 2. Length manufactures unwarranted confidence

Steyvers et al., arXiv:2401.13835, *Nature Machine Intelligence* (abstract
fetched first-hand). Two quantities: the **calibration gap** — "the difference
between human confidence in LLM-generated answers and the models' actual
confidence" — and the **discrimination gap**, "how well humans and models can
distinguish between correct and incorrect answers".

Findings: "users tend to overestimate the accuracy of LLM responses when provided
with default explanations", and users showed increased confidence with longer
explanations "even when the extra length did not improve answer accuracy". When
explanations were adjusted to reflect the model's internal confidence, "both the
calibration gap and the discrimination gap narrowed". The abstract gives no
magnitudes or sample size.

This upgrades A3. Verbosity does not merely spend tokens — it inflates the
reader's trust without inflating correctness, which is a calibration failure with
consequences. The cutting cards therefore carry a calibration rationale and a
severity above ordinary style.

#### 3. The rule's own distinction survives

§ Style keeps two instructions that could look contradictory: cut the empty
softener ("maybe", "it seems"), and keep the epistemic marker because "cutting one
falsely changes the certainty or the scope". The evidence supports exactly that
split — what reduced overreliance was a specific first-person hedge attached to a
real uncertainty, not generic vagueness. The card must carry both halves or it
will be read as licence to hedge everywhere.

### What this licenses

- **An uncertainty card**: state a load-bearing uncertainty in the first person,
  never impersonally; cite the N=404 pre-registered result and the significance
  asymmetry, since the asymmetry is what makes the wording prescriptive.
- **A severity upgrade for the cutting cards**: unnecessary length is a
  calibration failure, not a style blemish.
- **The keep/cut split stated on one card**, so the two halves cannot drift apart.
- For § Voice, a consequence worth carrying into B3: a spoken span that drops the
  caveat while the screen keeps it produces exactly the calibration gap this topic
  measures.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Kim 2405.00623 (FAccT 2024, abstract) · N=404 pre-registered; first-person
  uncertainty lowers agreement and confidence while raising participant accuracy
  via reduced overreliance on wrong answers; the impersonal form's effects are
  weaker and not statistically significant
Steyvers 2401.13835 (Nature Machine Intelligence, abstract) · calibration gap and
  discrimination gap; users overestimate accuracy on default explanations; longer
  explanations raise confidence without raising accuracy; matching explanations to
  internal confidence narrows both gaps · no magnitudes or N in the abstract
```

### Sources

Fetched first-hand:

- 2024-05 · [2405.00623](https://arxiv.org/abs/2405.00623) — "I'm Not Sure, But…": Examining the Impact of Large Language Models' Uncertainty Expression on User Reliance and Trust ([FAccT 2024 PDF](https://facctconference.org/static/papers24/facct24-56.pdf))
- 2024-01 · [2401.13835](https://arxiv.org/abs/2401.13835) — What Large Language Models Know and What People Think They Know ([Nature Machine Intelligence](https://www.nature.com/articles/s42256-024-00976-7))

Related, not consulted: [Not All Uncertainty Is Equal (2605.28571)](https://arxiv.org/abs/2605.28571) on uncertainty granularity, and [From Calibration to Collaboration (2506.07461)](https://arxiv.org/abs/2506.07461).

### Open after A4

Whether the first-person effect holds for an expert reader in a technical domain
is untested — the experiment used medical questions with lay participants, and
the transfer is an extrapolation the card must record.

## B1 — Form for a human reader

**Question:** when does a diagram
or table beat prose for a human reader, and what does that imply for `R-21` and
`R-23`, whose rationale is agent-side retrieval?

### Verdict

Two results, one expected and one that outgrew this topic.

The expected one: a diagram earns its place by lowering the *cost of inference*,
not by carrying more information — which is precisely § Style's test ("draw the
diagram only when removing it breaks the relation") and which dissolves the
apparent conflict between `R-23` and § Screen.

The larger one: shaping the output constrains the reasoning that produces it, and
the penalty is measurable and capacity-dependent. This is the third topic in the
programme to land on the same principle, so it belongs at corpus level rather than
on one card — see "The cross-cutting rule" below.

### Findings

#### 1. Diagrams win on computation, not information

Larkin & Simon (1987), *Why a Diagram is (Sometimes) Worth Ten Thousand Words*,
*Cognitive Science* 11(1):65–100, separate two equivalences (p. 67).
**Informational equivalence**: "Two representations are informationally equivalent
if all of the information in the one is also inferable from the other, and vice
versa." **Computational equivalence**: "Two representations are computationally
equivalent if they are informationally equivalent and, in addition, any inference
that can be drawn easily and quickly from the information given explicitly in the
one can also be drawn easily and quickly from the information given explicitly in
the other, and vice versa." The comparison runs over what each representation
states outright, not over what could be derived from it.

The two forms differ by their index (p. 68): "A data structure in which elements
appear in a single sequence is what we will call a sentential representation. A
data structure in which information is indexed by two-dimensional location is what
we call a diagrammatic representation." The abstract states the payoff (p. 65):
"Diagrammatic representations also typically display information that is only
implicit in sentential representations and that therefore has to be computed,
sometimes at great cost, to make it explicit for use."

The authors mark the advantage as their own reading (p. 99): "The advantages of
diagrams, in our view, are computational. That is diagrams can be better
representations not because they contain more information, but because the
indexing of this information can support extremely useful and efficient
computational processes. But this means that diagrams are useful only to those who
know the appropriate computational processes for taking advantage of them."

That last sentence is the title's "sometimes". A diagram fails first where the
reader lacks the operators to read it (p. 71): "If the students lack productions
for making physics inferences from diagrams, they may not only fail to
'appreciate' the value of diagrams, but will find them largely useless." Two
further conditions carry the same qualifier — a diagram built so that it groups
nothing (pp. 98–99), and one whose easy perceptual inferences are irrelevant to
the problem (p. 99).

**Read first-hand from page images**;
[§ Verification — Larkin & Simon, Cleveland & McGill](#verification--larkin--simon-1987-cleveland--mcgill-1984)
carries the full passages and the provenance line. The text above is the repaired
version. The gloss this section previously carried dropped "from the information
given explicitly in" from computational equivalence, the clause that gives the
concept its meaning; dropped the symmetry ("and vice versa") from the
informational gloss; fused two sentences into the p. 99 quote and dropped "in our
view"; and stated no failure condition at all, leaving the title's "sometimes"
unaccounted for. The paper runs to p. 100, not p. 99. Its only counted search is
sentential — "Total Elements Searched: 138" for the pulley problem (p. 77,
Table 2) — and the diagrammatic solution is never counted, so no speedup ratio may
be quoted from it.

Consequence for the corpus's apparent contradiction: `R-23` prescribes
arrow-notation text over ASCII art for an agent-read file, while § Screen
prescribes drawn trees and branching diagrams for the terminal. Under Larkin &
Simon these are the same rule under different consumers — an agent consuming a
token sequence gains little from planar indexing, a human scanning a terminal
gains a lot. The merge does not need to overturn `R-23`; it needs to name the
consumer on both.

#### 2. Output shape taxes the reasoning that produces it — with numbers

Tam et al., arXiv:2408.02442 (abstract, fetched first-hand) reports "a significant
decline in LLMs reasoning abilities under format restrictions" and that "stricter
format constraints generally lead to greater performance degradation in reasoning
tasks". The abstract carries no figures.

The refinement does, and it is the strongest quantitative result in this
programme so far — arXiv:2606.09410, *Capacity, Not Format* (abstract, fetched
first-hand). Design: "information-matched prose controls and a four-level schema
complexity gradient … across 4 models and 5 benchmarks with 0% parse failures".

| Model / setting | Effect |
|--|--|
| Sonnet, MATH-Hard | 88.7 ± 4.0% JSON vs 89.3 ± 1.7% CoT — no degradation |
| Haiku, standard token budget | −36.2 pp (p < 0.0001), largely truncation |
| GPT-4o-mini, extended budget | −28.0 pp (p < 0.001) — capacity competition, not truncation |
| Opus 4.7, AIME under JSON | 96.2% → 91.0%, −5.3 pp (exact 7/133 = 5.26 pp) |

The penalty "scales with schema complexity (McNemar p < 0.0001) and cannot be
explained by prompt length alone". And the repair: "A delayed-structure ablation —
reasoning freely before formatting — recovers most of the lost accuracy (3-run
mean: 80–87%)."

Two things matter for this corpus. First, "frontier model immunity" is qualified,
not granted: even Opus loses 5.3 pp. Second, the cost is a function of spare
capacity, so a shape rule that is free on a large model is expensive on a small
one — which bears directly on the audit's own `modelByCheckKind` dispatch, where
mechanical checks run on Haiku.

### The cross-cutting rule

Three topics have now produced the same structural finding from different
literatures:

```
A1  answer-first is free only when reasoning precedes the visible answer
A3  brevity must scope to the delivered answer, never to the reasoning budget
B1  format applied before reasoning completes costs up to 36.2 pp
```

Stated once: **the output's shape is applied after reasoning finishes, never as a
constraint on it.** Under `R-43` this belongs in one place at corpus level, with
the shape cards referencing it rather than each restating a scope line. It is
also the single most load-bearing sentence for the resident core identified in D1,
and by D3's ordering finding it is a hard constraint that should sit early.

### What this licenses

- **A form-choice card**: structure earns its place when it lowers the reader's
  inference cost, not when it merely holds the same content — with the removal
  test as the validator.
- **Naming the consumer on `R-21` and `R-23`** rather than rewriting them; the
  terminal-facing rules of § Screen are their counterparts, not their refutation.
- **One corpus-level rule** for shape-after-reasoning, referenced by every shape
  card.
- **A caveat on cheap-model dispatch**: a formatting constraint that a large model
  absorbs can cost a small one tens of points, so schema-heavy sub-agent output on
  Haiku needs the delayed-structure pattern.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Larkin & Simon 1987, Cognitive Science 11(1):65-100 · informational equivalence
  (mutual inferability) vs computational equivalence (mutual ease from what is
  stated EXPLICITLY), p. 67; diagrams win by two-dimensional indexing (p. 68), not
  by holding more information (p. 99); a diagram fails without the operators to
  read it (p. 71) · first-hand, page images — full line in
  § Verification — Larkin & Simon, Cleveland & McGill
Tam 2408.02442 (abstract) · significant decline in reasoning under format
  restrictions; stricter constraints degrade more · no numbers in the abstract
Capacity, Not Format 2606.09410 (abstract) · 4 models × 5 benchmarks; Sonnet
  88.7 vs 89.3% unaffected; Haiku −36.2pp (p<0.0001, truncation); GPT-4o-mini
  −28.0pp (p<0.001, capacity competition); Opus 4.7 AIME 96.2→91.0% (−5.3pp);
  penalty scales with schema complexity (McNemar p<0.0001); reasoning-before-
  formatting recovers 80–87%
```

### Sources

Fetched first-hand:

- 1987 · Larkin, J. H. & Simon, H. A. Why a Diagram is (Sometimes) Worth Ten Thousand Words. *Cognitive Science* 11(1):65–100 — [PDF](https://mechanism.ucsd.edu/bill/teaching/F12/cs200/Readings/larkin.whyadiagramissometimesworth.1987.pdf) · [publisher](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1101_4). The scan's OCR layer is unreliable, so every quoted page was read as an image — see [§ Verification — Larkin & Simon, Cleveland & McGill](#verification--larkin--simon-1987-cleveland--mcgill-1984)
- 2024-08 · [2408.02442](https://arxiv.org/abs/2408.02442) — Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models
- 2026-06 · [2606.09410](https://arxiv.org/abs/2606.09410) — Capacity, Not Format: Rethinking Structured Reasoning Failures

Relayed, **not** verified — verify before citing on a card:

- [Why Diagrams Are (Sometimes) Six Times Easier than Words](https://adrenaline.ucsd.edu/kirsh/fileupload/Diagrams/whay_diagrams_are_worth.pdf) — benefits beyond locational indexing; its title ratio is its own, and no ratio may be carried over to Larkin & Simon

Not consulted, still open: Mayer's multimedia principles (coherence, signaling,
redundancy) and Cleveland & McGill (1984) on the accuracy of graphical encodings,
which is the specific evidence the `▁▂▃` bar rule of § Screen would need. Both
move to B2.

### Open after B1

Cleveland & McGill's ranking of graphical encodings is the one piece § Screen's
magnitude-bar row actually rests on, and it was not reached here. It was read
first-hand afterwards, in
[§ Verification — Larkin & Simon, Cleveland & McGill](#verification--larkin--simon-1987-cleveland--mcgill-1984):
the six-rank ordering is hypothesized (p. 536), and the paper's own experiments
measure only position against length (errors 40%–250% larger) and position against
angle (a factor of 1.96). Mayer's principles were read in
[§ Verification — Mayer's principles and speech transience](#verification--mayers-principles-and-speech-transience).

## B2 — Terminal rendering and accessibility

**Question:** which § Screen
conventions rest on a standard, and which are personal taste? Plus Cleveland &
McGill, handed over by B1 as the only evidence the magnitude-bar row could rest on.

This topic was predicted to be extraction rather than discovery, and it was — with
one correction to my assumption about column alignment.

### Verdict

| § Screen convention | Status |
|--|--|
| A word or prefix carries what the colour shows | **normative** — WCAG 2.2 SC 1.4.1, Level A |
| Magnitude bars, each row carrying its number | **supported** — length ranks 3rd of 6; the printed number is what makes it sound |
| Meaning never rides on colour alone | **doubly supported** — WCAG, and colour saturation ranks last for accuracy |
| One glyph source per line; aligned blocks | supported, but by a different argument than assumed — width is not computable |
| Aligned block within 100 columns | house convention — no source located |

### Findings

#### 1. Colour redundancy is a Level A conformance criterion

WCAG 2.2, Success Criterion 1.4.1 *Use of Color* (Level A), verbatim: "Color is
not used as the only visual means of conveying information, indicating an action,
prompting a response, or distinguishing a visual element." The associated
technique G14 is "Ensuring that information conveyed by color differences is also
available in text".

This is the strongest class of source available under the repository's evidence
rule — a technical standard, not a paper. It licenses § Screen's rule directly,
and it also certifies the diff-fence convention as already conformant: `+` and
`-` are the redundant encoding beside green and red, so the rule and its example
agree.

#### 2. Column width is not computable, so the rule is glyph choice, not arithmetic

Unicode Standard Annex #11, *East Asian Width*, defines six property values —
Wide, Fullwidth, Halfwidth, Narrow, Ambiguous, Neutral — resolving to two abstract
widths. Two statements matter here.

First, the annex disclaims exactly the use one would reach for: "The
East_Asian_Width property is not intended for use by modern terminal emulators
without appropriate tailoring on a case-by-case basis."

Second, on the awkward category: "Ambiguous characters require additional
information not contained in the character code to further resolve their width",
and they should default to narrow when context cannot be established.

I had assumed the rule about aligned blocks was about counting characters
correctly. It is not — the standard says the width cannot be resolved from the
character alone. The sound rule is therefore about *choosing* characters with
determinate width inside an aligned block, which is what "draw one line from one
glyph source" already achieves for the wrong stated reason. The card states
determinacy, not counting.

#### 3. Length beats colour for reading a magnitude — and the number beats both

**Corrected after first-hand verification** — see
[§ Verification — Larkin & Simon, Cleveland & McGill](#verification--larkin--simon-1987-cleveland--mcgill-1984).
Cleveland & McGill (1984), *Graphical Perception: Theory, Experimentation, and
Application to the Development of Graphical Methods*, JASA 79(387), **hypothesize**
this ordering of the elementary perceptual tasks; they do not measure it. Section 3
is titled *Theory* and opens "we hypothesize an ordering", sourced at p. 537 to
"our own reasoning …, results of psychophysical experiments, and the theory of
psychophysics". The ordering:

```
1  position along a common scale
2  position along non-aligned scales
3  length, direction, angle
4  area
5  volume, curvature
6  shading, colour saturation
```

Their guideline: graphs should employ tasks as high in the ordering as possible.

Only two comparisons were put to subjects: position versus length (errors 40–250%
larger, 5.3× the rate of gross errors) and position versus angle (1.96×). Ranks 4,
5 and 6 were never shown to anyone — they inherit from Stevens' power law and
Baird's 1970 review. So the ordering may be cited only as a hypothesis, and only
its first three ranks carry measurement.

For § Screen's `▁▂▃▄▅▆▇█` row this cuts both ways. Bar length is rank 3, well
short of the best encodings — but the rule's own requirement that "each row
carrying its number" removes the estimation task entirely, leaving the bars as a
scanning aid over exact values. That hedge is what makes the convention
defensible, and the card must keep the number mandatory rather than optional.

It does **not** give an independent second reason for finding 1, as I first wrote.
Colour *hue* is explicitly excluded from the list at p. 532 as a categorical
encoding, and colour *saturation* was never illustrated to a subject, let alone
measured. The colour-redundancy card rests on WCAG 2.2 SC 1.4.1 alone; Cleveland &
McGill may be named beside it only for saturation and shading, and only as a
hypothesis.

Card S-21 gains rather than loses: bar length is rank 3 with a measured error
penalty against position, which is exactly why the printed number stays mandatory
rather than decorative.

### What this licenses

- **A colour-redundancy card** citing WCAG 2.2 SC 1.4.1 Level A — the corpus's
  first rule backed by a conformance criterion rather than a study.
- **An aligned-block card** stating glyph determinacy: inside an aligned block,
  use characters whose width does not depend on context; ambiguous-width
  characters and emoji break alignment because the width is not in the character.
- **A magnitude card** with the printed number as a required part, not decoration.
- **The 100-column cap flagged** as a house number with no located source, like
  A2's two thresholds.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
WCAG 2.2 SC 1.4.1 Use of Color (Level A) · "Color is not used as the only visual
  means of conveying information…"; technique G14 — the same information also
  available in text
UAX #11 East Asian Width · six categories; the property "is not intended for use
  by modern terminal emulators without appropriate tailoring"; ambiguous widths
  are unresolvable from the character code and default to narrow
Cleveland & McGill 1984, JASA 79(387):531–554 · elementary perceptual tasks
  ordered position on a common scale > non-aligned position > length/angle > area
  > volume/curvature > shading/colour saturation — **hypothesized, not measured**
  (§3 "Theory", p. 537). Measured only: position vs length (errors 40–250% larger,
  5.3× gross errors) and position vs angle (1.96×). Colour hue excluded at p. 532;
  saturation never shown to a subject · verified first-hand from page images
```

### Sources

Fetched first-hand:

- [WCAG 2.2 — Understanding SC 1.4.1 Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html), W3C
- [Unicode Standard Annex #11 — East Asian Width](https://www.unicode.org/reports/tr11/)

Relayed, **not** verified — verify before citing on a card:

- Cleveland, W. S. & McGill, R. (1984). Graphical Perception. *JASA* 79(387):531–554 — [PDF](https://www.math.pku.edu.cn/teachers/xirb/Courses/biostatistics/Biostatistics2016/GraphicalPerception_Jasa1984.pdf) · [publisher](https://www.tandfonline.com/doi/abs/10.1080/01621459.1984.10478080)

Not consulted, still open: UAX #29 on grapheme cluster boundaries (the other half
of why a rendered "character" is not one code point), and typographic measure
research, which is what a defensible column cap would need.

### Open after B2

Mayer's multimedia principles were queued here from B1 and again not reached; they
bear on § Style's "beside a block write only what it cannot show", which is the
redundancy principle. They move to B3, which is already the multimedia-adjacent
topic.

## B3 — Writing for the ear

**Question:** what must change
between a text and its spoken version, and what backs § Voice's screen/speech
split? Plus Mayer's principles, queued from B1 and B2.

### Verdict

§ Voice's central design — the span carries the conclusion, the screen keeps
code, commands, tables, paths and formulas — is the configuration multimedia
research recommends: divide content across modalities rather than duplicate it.

Verification changed two of this note's three findings. The tension I recorded
between § Voice's completeness rule and the redundancy principle **does not
exist** — a spoken span has no graphics, which is a condition Mayer names as
reversing the effect, and the graphics-free experiments favour carrying the
conclusion in both channels. And the blunt transience claim is refuted for
competent adults, though nesting in heard sentences is measured.

The third finding stands: the Cyrillic-transliteration rule is a workaround for a
missing pronunciation lexicon, where a W3C Recommendation defines the proper
mechanism — one the operator's setup already has in another form.

### Findings

#### 1. Dividing across modalities is the recommended configuration

**Verified first-hand against Mayer's own chapters** — see
[§ Verification — Mayer's principles and speech transience](#verification--mayers-principles-and-speech-transience).

Redundancy, Mayer & Fiorella 2014, ch. 12 p. 279: "people learn more deeply from
graphics and narration than from graphics, narration, and on-screen text …
supported in 16 out of 16 experimental tests, yielding a median effect size of
0.86." Modality, Mayer & Pilegard 2014, ch. 13 p. 316: spoken over printed words,
53 of 61 tests, median 0.76.

The 0.69 I relayed is real but stale: it is Mayer & Moreno 2003, Table 3, a median
of **three** transfer comparisons. The 2014 chapter recomputes those same three as
0.88, 1.21 and 0.72 inside a 16-test median of 0.86. A card citing this number
must carry its year.

§ Voice's split is exactly this: the material that would compete — code,
commands, tables, file paths, formulas — stays in one channel, and the conclusion
goes to the other. The rule is not a concession to the hook's limitations; it is
the arrangement with the better measured outcome.

#### 2. The tension I recorded does not exist — the rule is the measured-better arrangement

I wrote that § Voice's "the span never carries less meaning than the screen"
duplicates the conclusion across both channels and therefore sits in tension with
the redundancy principle. That was wrong on scope, and the graphics-free evidence
runs the opposite way.

Mayer states the boundary himself, ch. 12 p. 299: "the redundancy effect can be
eliminated or even reversed when the learners are experienced, the on-screen text
is short, or **the material lacks graphics**." A `[SAY]` span has no graphics at
all, so the principle does not reach it — and all three listed conditions hold at
once here.

Where the case has been measured directly, redundancy wins. Moreno & Mayer (2002),
74 college students, narration against narration plus identical on-screen text with
no concurrent animation: effect sizes 0.78 retention, 1.62 transfer, 0.39 matching
— **favouring the redundant presentation**. Adesope & Nesbit's 57-study
meta-analysis agrees, moderated by materials without pictures.

So the rule needs no condition attached and no defence. The modality principle
also stops being citable here: four of its own boundary conditions — knowledgeable
learner, self-paced, technical terms, no graphics — hold simultaneously.

#### 3. Transience is what the sentence-level voice rules rest on

The mechanism holds, but the blunt form — speech is harder — is refuted for
competent adults. Clinton-Lisell (2022), 46 studies, N = 4,687: listening against
reading is "not reliably different (g = 0.07, p = 0.23)"; reading wins only when
self-paced (g = 0.13) and on inferential comprehension (g = 0.36).

The no-rewind cost has been isolated, but in reading: Schotter, Tran & Rayner
(2014), 40 adults, blocking re-reading lowered comprehension (b = −0.92, z = 5.09,
p < .001). Their 84%-versus-56% figure is the authors' own speculative
explanation and must not be quoted as a result.

Nesting in *heard* sentences is measured: Peelle et al. (2010), 40 adults,
object-relative 0.843 against subject-relative 0.935 proportion correct
(F(1,38) = 45.47, p < .001) — about nine accuracy points per embedded clause.

So "one claim per sentence, no nesting" may cite Peelle, without transferring the
number to prose of arbitrary length. Nothing measures forward references or
claims-per-sentence in spoken prose at all; "no forward references" stays a house
convention whose evidence is the operator's own hook usage.

#### 4. Pronunciation belongs in a lexicon, not in the prose

W3C **Pronunciation Lexicon Specification (PLS) Version 1.0**, a Recommendation
dated 14 October 2008, defines "a mapping between words (or short phrases), their
written representations, and their pronunciations suitable for use by an ASR
engine or a TTS engine". It supports several orthographies for one lexeme through
multiple `<grapheme>` elements — the specification's own example gives Romaji,
Kanji and Hiragana for the same word — and "PLS is intended to be the standard
format of the documents referenced by the `<lexicon>` element of SSML".

This reclassifies § Voice's rule about spelling English terms in Cyrillic inside a
Russian span. It is a workaround for a TTS voice with no lexicon entry, not a
writing rule. The standard mechanism is a lexicon, and the operator's setup
already keeps one in another form (`terms.tsv`, per the dotfiles documentation).
The card should say so: transliterate in the span while the term is unregistered,
and register it rather than transliterating forever.

### What this licenses

- **A modality-split card**: content that competes for the same channel is
  divided, not duplicated — code, tables, paths and formulas stay on screen.
- **A conditional on the completeness rule**, so it does not read as a general
  claim the redundancy principle refutes.
- **Sentence-level voice rules** justified by transience, stated as a mechanism
  without a number.
- **Reclassifying transliteration as a workaround**, with the lexicon named as the
  durable fix — a rule that points at its own removal.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Mayer, redundancy principle · narration alone beats narration plus identical
  on-screen text, reported transfer effect size 0.69; modality principle —
  spoken beats printed text alongside graphics · NOT first-hand verified
W3C PLS 1.0 (Recommendation, 2008-10-14) · lexicon maps written representations to
  pronunciations for ASR/TTS; multiple <grapheme> orthographies per lexeme; the
  standard format referenced by SSML's <lexicon> element
Speech transience · no rewind in real time, structure carried in working memory;
  working-memory load delays spoken-word discrimination · secondary sources only
```

### Sources

Fetched first-hand:

- [W3C Pronunciation Lexicon Specification (PLS) Version 1.0](https://www.w3.org/TR/pronunciation-lexicon/), Recommendation, 14 October 2008

Relayed, **not** verified — verify before citing on a card:

- Mayer's multimedia principles via secondary summaries, e.g. [University of Pittsburgh checklist](https://teaching.pitt.edu/wp-content/uploads/2023/03/multimedia-principles-checklist.pdf) and [Cognitive Theory of Multimedia Learning](https://litfl.com/cognitive-theory-of-multimedia-learning/) — the 0.69 figure needs Mayer's own source
- [Working Memory Load Affects Processing Time in Spoken Word Recognition](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4871876/)
- [Are working memory and behavioral attention equally important for reading and listening comprehension?](https://pmc.ncbi.nlm.nih.gov/articles/PMC6096896/)

Not consulted, still open: [SSML 1.1](https://www.w3.org/TR/speech-synthesis11/)
itself, which would supply the markup side if the voice hook ever emits SSML
rather than plain text.

### Open after B3

Whether a spoken conclusion improves retention of a technical answer at all is
unmeasured — the multimedia results concern instructional material with graphics,
not a terminal assistant's summary. The transfer is an extrapolation the cards
must record.

## C1 — Language of operation

**Question:** does restating a
Russian request as an English **Prompt:** measurably improve the result, and which
style rules must be re-derived per language rather than translated?

### Verdict

The rule survives, but not on the justification it was written with — the same
pattern A1 found for answer-first ordering.

English *is* the models' internal pivot, and self-translation does help models with
weaker multilingual coverage. But the effect is small, model-dependent, and
reverses for models trained across many languages, which is the class the operator
actually uses. What the restatement reliably buys is different: it makes the
interpretation explicit before work starts, so a misreading is caught by the user
rather than discovered in the output.

### Findings

#### 1. English is the internal pivot — with a scope bound

Wendler et al., arXiv:2402.10588 (abstract, fetched first-hand) asks "whether
multilingual language models trained on unbalanced, English-dominated corpora use
English as an internal pivot language". Method: layer-by-layer analysis of
embedding transformations on non-English prompts with unique single-token
continuations. Three phases emerge — embeddings first move away from output token
embeddings, middle layers decode semantically but favour English token versions,
and a final phase converges on input-language-specific regions.

The conclusion the card would rest on: "the abstract 'concept space' lies closer
to English than to other languages, which may have important consequences
regarding the biases held by multilingual language models."

Scope bound stated in the paper itself: the analysis focuses on the Llama-2
family. Generalizing to a current frontier model is extrapolation.

#### 2. The measured benefit is small and conditional — and can reverse

Relayed from search summaries, not fetched:

- Self-translating non-English prompts to English improved Llama-2 by **2.4% on
  average** over native prompts.
- The benefit concentrates in "models with limited multilingual capabilities".
- It can invert: "English translations can sometimes negatively impact
  performance, as observed with models trained on a higher number of languages."
- "Naïve translation consistently degraded performance" — how the translation is
  done matters more than whether it happens.
- The outcome is "highly dependent on the task, language setting, translation
  quality, the tokenizer, and the LLM deployed for inference."

Taken together, the accuracy argument for a Russian-to-English restatement is
weak for a strong multilingual model and possibly negative. A card claiming an
accuracy gain would overstate the evidence.

#### 3. The rule's real work is specification, not translation

What the **Prompt:** line does is state the interpretation explicitly, in one
line, before any work — which is an underspecification control, not a language
intervention. That places it beside the repository's existing evidence on
underspecified prompts (Yang 2505.13360, already in corpus: rules that are not
spelled out are recovered at low rates), and it explains why the practice is
useful regardless of which language wins internally.

Card consequence: the rationale is "the reader can correct a misreading before the
work happens", and the language of the restatement is a secondary detail
justified by finding 1 rather than the point of the rule.

### What this licenses

- **A restatement card** justified as an explicit-interpretation control, with the
  English pivot as a secondary reason carrying its scope bound.
- **A prohibition on claiming an accuracy gain** from translation, since the
  measured effect is 2.4% on a weaker model class and reverses on stronger ones.
- **A standing caveat for the whole corpus**: a style rule derived from
  English-language reading research does not transfer to Russian by translation.
  Nothing in this topic settles the Russian-specific rules; they remain unsourced.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Wendler 2402.10588 (abstract) · multilingual transformers pivot through an abstract
  concept space closer to English than to other languages; three-phase layer
  analysis · scope: Llama-2 family only
Cross-lingual prompt translation · self-translation to English improved Llama-2 by
  2.4% on average; benefit concentrated in weakly multilingual models and can
  reverse for models trained on many languages; naïve translation degrades
  · NOT first-hand verified — relay only
```

### Sources

Fetched first-hand:

- 2024-02 · [2402.10588](https://arxiv.org/abs/2402.10588) — Do Llamas Work in English? On the Latent Language of Multilingual Transformers

Relayed, **not** verified — verify before citing on a card:

- [How and Where to Translate? The Impact of Translation Strategies in Cross-lingual LLM Prompting (2507.22923)](https://arxiv.org/abs/2507.22923)
- [Can you map it to English? The Role of Cross-Lingual Alignment in Multilingual Performance of LLMs (2504.09378)](https://arxiv.org/abs/2504.09378)
- [Beyond English: The Impact of Prompt Translation Strategies across Languages and Tasks in Multilingual LLMs](https://www.researchgate.net/publication/392498346_Beyond_English_The_Impact_of_Prompt_Translation_Strategies_across_Languages_and_Tasks_in_Multilingual_LLMs)

### Open after C1

The Russian-specific rules of § Style 5 — emphasis by word order rather than
amplifiers, verb aspect carrying completion, a native word over a calque — were
not researched and have no source. Russian information structure (theme–rheme)
interacts with A1's given–new finding in a language with free word order, and that
interaction is the natural next question; it is a separate topic, not a corollary
of this one.

## E1 — Stale comments and history artifacts

**Question:** why does "used to /
no longer" in a live document harm the reader — and specifically, what empirical
base can replace the book citations `documenting-present-design` currently rests
on (Clean Code Ch. 4, Ousterhout, Fowler)?

### Verdict

The empirical base exists and it is stronger than the books it replaces. Two
independent lines: prose and code drift apart as the *normal* case rather than the
exceptional one, and the drift correlates with defects; and documentation
references to deleted code elements survive in most projects. Together they turn
the skill's purge rules from craft advice into maintenance evidence.

### Findings

#### 1. Comments and code do not co-evolve, and inconsistency tracks defects

Wen et al. (2019), *A Large-Scale Empirical Study on Code-Comment
Inconsistencies*, ICPC 2019. Method: mining 1.3 billion AST-level changes across
the complete history of 1,500 systems. Reported results:

- 13% to 20% of code changes trigger a comment change in the class and/or method
  comments.
- "in most of the cases, code and comments do not co-evolve" — roughly 20% of the
  time.
**Verified first-hand; the third figure was wrong.** See
[§ Verification — news structure and comment drift](#verification--news-structure-nominalisation-passive-voice-comment-drift).
The first two are exact — the dataset line appears in the abstract and again in
§III-A p. 4 (a 476 GB database), the 13–20% in §IV-A p. 6 and the RQ1 box p. 7 —
and both need a Java-only qualifier.

The "**1.5× more likely to lead to a bug-introducing commit**" claim **is not in
Wen 2019 at all.** That paper has only RQ1 (co-evolution rates) and RQ2 (a
taxonomy of fixed inconsistencies): no bug-proneness analysis, no SZZ, no odds
ratio. The sentence comes from the abstract of
[Radmanesh et al. 2024, arXiv:2409.10781](https://arxiv.org/abs/2409.10781) §4.2,
whose provenance is materially weaker — a preprint, not peer-reviewed;
inconsistency labelled by a fine-tuned GPT-3.5; "bug-introducing" derived from
GitCProc plus SZZ; 32 Apache Java projects; no confidence interval, no
significance test. Recomputing the pooled 7-day odds ratio from its own Table 4
gives **1.417**, not the stated 1.52, which is a per-repository "Total" row whose
eight values span 0.72–2.68.

And the direction is contested: Wen's own related work cites Ibrahim et al. 2012,
which reports that "inconsistent changes are not necessarily correlated with more
bugs."

So the drift-tracks-defects argument does **not** ship. What survives from Wen is
the prevalence result — comments and code mostly do not co-evolve — which is
enough to justify purging stale prose on maintenance grounds, but not on defect
grounds.

What it gives the skill: the argument for purging stale prose stops being "a
comment that drifts is untidy" and becomes "drift is the default behaviour of the
artifact, and drifted prose sits next to defects". That also justifies the skill's
strongest move — deleting rather than rewriting — since a comment that will not be
maintained is a liability at whatever tense it is written in.

#### 2. Documentation keeps pointing at code that no longer exists

*Detecting Outdated Code Element References in Software Repository
Documentation*, arXiv:2212.01479 (abstract, fetched first-hand). The object of
study is precise: "code element references that survive in the documentation after
all source code instances have been deleted."

Prevalence across "over 3,000 GitHub projects": "most projects contain at least
one outdated code element reference at some point in their history." The authors
validated the finding in the field by "submit[ting] GitHub issues to real-world
projects containing outdated references", some of which led to documentation
fixes.

This is direct backing for `R-73` (verify every pointer against the current repo)
and for the personal skill's delete-list entry on stale references to removed
functions, parameters, flags, files and config keys. It also supports the purge
pass being triggered by a rename or deletion, since that is exactly the event that
creates these references.

#### 3. For an agent reader, a stale line is a distractor with authority

Already in the repository's corpus and needing no new work: Vishnyakova
2603.09619 §9 names context *poisoning* (a wrong statement reproduced at every
step) and *clash* among the four context-rot modes, with a measured 39% quality
drop when one prompt was split across turns; Hong 2025 measures accuracy loss from
a single distractor. A superseded design left in a context file is precisely a
distractor the model has no reason to distrust — it carries the same authority as
the current rule.

This is the argument the personal skill states in prose ("the model blends 'how it
used to work' into 'how it works now'") and now has corpus citations for.

### What this licenses

- **A history-artifact card** citing Wen 2019 for the drift-and-defects argument
  once verified, with the corpus's context-rot citations for the agent-reader half.
- **A stale-pointer card** — or a severity increase on `R-73` — citing
  2212.01479's prevalence result.
- **The purge pass** triggered by rename and deletion events, which is the
  documented origin of outdated references.
- The residual-fact test (delete rather than translate to present tense) stays a
  house convention: nothing located measures it, and it should ship with the
  personal skill's eval seeds as its hands-on evidence, per D2.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Wen 2019, ICPC · 1.3B AST-level changes over 1,500 systems; 13–20% of code changes
  trigger a comment change; code and comments mostly do not co-evolve; inconsistent
  changes ~1.5× more likely to precede a bug-introducing commit
  · NOT verified — both PDFs failed to extract; verify before citing
2212.01479 (abstract) · code element references surviving in documentation after
  every source instance was deleted; most of 3,000+ GitHub projects contain at
  least one at some point; validated by filing issues that led to fixes
```

### Sources

Fetched first-hand:

- 2022-12 · [2212.01479](https://arxiv.org/abs/2212.01479) — Detecting Outdated Code Element References in Software Repository Documentation

Relayed, **not** verified — verify before citing on a card:

- Wen, F., Nagy, C., Bavota, G., Lanza, M. (2019). A Large-Scale Empirical Study
  on Code-Comment Inconsistencies. ICPC 2019 —
  [ACM](https://dl.acm.org/doi/abs/10.1109/ICPC.2019.00019) ·
  [preprint mirror](https://csnagy.github.io/research/pdfs/2019/Wen2019-preprint.pdf)
  (does not extract) · [Semantic Scholar](https://www.semanticscholar.org/paper/07bb8b93b2b448ec943b861c58bc357a54575c66)
- [Towards Detecting Inconsistent Comments in Java Source Code Automatically](https://software.imdea.org/~alessandra.gorla/papers/Stulova-UpDoc-SCAM20.pdf) — SCAM 2020

From the repository's corpus, no new work needed: Vishnyakova
[2603.09619](https://arxiv.org/abs/2603.09619) §9 (context poisoning and clash,
39% drop); Hong 2025 [Context Rot](https://www.trychroma.com/research/context-rot)
(single-distractor effect).

### Open after E1

Panthaplackel et al. on just-in-time inconsistency detection was not reached; it
would strengthen the case that the drift is detectable automatically, which
matters if the purge pass is ever run as a gate rather than on demand.

## E2 — Deliberation residue and the home of rationale

**Question:** does a decision's rationale belong in the living document or in a
separate record — and is `documenting-present-design`'s move of dissolving
"alternatives considered" tables defensible?

### Verdict

Defensible, provided the rule is read as *relocation* and not deletion. The
architectural-knowledge literature makes rationale first-class rather than
optional, so a rule that removed it would be wrong. What the literature adds is
that **where** it lives decides whether it is useful — and that the ADR template
scoring best overall is the concise one that carries no alternatives catalogue.

### Findings

#### 1. Rationale is first-class, so the rule must relocate rather than delete

Jansen & Bosch, *Software Architecture as a Set of Architectural Design
Decisions*, argue that an architecture is a composition of explicit design
decisions rather than only an arrangement of components and connectors — the
decisions and their rationale are the architecture, not commentary on it.
*Relayed from search summaries.*

This sets the boundary for the skill's rule. "The search is not the design" may
strip candidate catalogues and decidedness announcements from a living document;
it may not strip the decision or its determining reason, and the destination must
be named. The skill already does this — its "What to leave alone" list keeps ADRs
as history's home — and this finding is why that clause is load-bearing rather
than a politeness.

#### 2. Where the record lives decides whether it is used

An action-research study introducing ADRs at a company building a microservice
system without decision documentation (seven developer interviews before
introduction) reports two results: cooperation among teams improved after
introduction, and "the decision on where documentation is stored has a massive
influence on its perceived usefulness". *Relayed; not fetched.*

That is the empirical form of the skill's distinction between a living design doc
and a dedicated record. The residue is not harmful because it is history — it is
harmful because it sits in the artifact whose job is to describe the present, and
moving it makes it more useful, not less.

#### 3. The best-scoring ADR template carries no alternatives catalogue

*One Size Fits All? An Empirical Comparison of ADR Templates regarding
Comprehension, Usability, and Ease of Adoption*, arXiv:2604.27333 (abstract,
fetched first-hand). Five templates compared — Tyree/Akerman, Nygard's ADR,
arc42, Y-statements, and MADR — using the DESMET FA method for expert screening
followed by a controlled experiment with undergraduate students. Nygard's template
is the Overall Score winner, and the paper's guidance is that "Nygard supports
concise and objective documentation, while MADR facilitates structural details".

Nygard's template is Context / Decision / Status / Consequences — it has no
considered-alternatives section, where MADR does. The abstract does not claim the
alternatives section hindered anything, and the participants were students, so
this is a ranking rather than a causal result about that section. Stated at the
strength the evidence supports: the concise template without a candidate catalogue
scored best overall, which is consistent with dissolving such catalogues rather
than propagating them.

### What this licenses

- **A deliberation-residue card** whose thesis is relocation: the living document
  keeps the decision and its determining reason; candidate catalogues, decidedness
  announcements and "alternatives considered" tables move to a dedicated record or
  go.
- **Naming the destination on the card**, since storage location governs
  usefulness — a rule that says only "delete" would destroy first-class knowledge.
- The determinant-versus-guard test — does a fresh designer need this to *arrive*
  at the design or to *not depart* from it — stays a house convention. Nothing
  located tests it, and it ships with the personal skill's eval seeds per D2.

### Provenance lines (ready for `rule-cards-provenance.md`)

```
Jansen & Bosch · architecture as a set of explicit design decisions — rationale is
  part of the architecture, not commentary · NOT verified — relay only
ADR in Practice, action research (7 interviews, microservice system) · cooperation
  improved after ADR introduction; storage location has a massive influence on
  perceived usefulness · NOT verified — relay only
2604.27333 (abstract) · five ADR templates compared by comprehension, usability
  and ease of adoption; Nygard is Overall Score winner, "concise and objective",
  while MADR "facilitates structural details" · undergraduate participants; no
  numbers in the abstract; no causal claim about the alternatives section
```

### Sources

Fetched first-hand:

- 2026-04 · [2604.27333](https://arxiv.org/abs/2604.27333) — One Size Fits All? An Empirical Comparison of ADR Templates regarding Comprehension, Usability, and Ease of Adoption

Relayed, **not** verified — verify before citing on a card:

- [Architecture Decision Records in Practice: An Action Research Study](https://link.springer.com/chapter/10.1007/978-3-031-70797-1_22)
- Jansen, A. & Bosch, J. *Software Architecture as a Set of Architectural Design Decisions* — [Semantic Scholar](https://www.semanticscholar.org/paper/4cd105262aa01f62b88baeda78570325661f67d3)
- [Software Architecture Decision-Making Practices and Challenges (1610.09240)](https://arxiv.org/abs/1610.09240)
- [An Empirical Study on Collaborative Architecture Decision Making (1707.00107)](https://arxiv.org/abs/1707.00107)

### Open after E2

Whether a *living* document that keeps a guard beside its decision is better or
worse than one that ships the guard to the ADR is untested — the studies compare
templates and locations for the record, not the residue left behind in the design
doc. That is the one question the skill's own eval seeds are best placed to answer.

## Verification — Larkin & Simon 1987, Cleveland & McGill 1984

Both papers read first-hand from page images; both blocked cards can proceed, one of them with a corrected claim.

| Source | Verdict |
|--|--|
| Larkin & Simon 1987 | **confirmed with correction** — every claim holds, but two relayed quotes were stitched from separate sentences and one definition lost its load-bearing clause |
| Cleveland & McGill 1984 | **confirmed with correction** — the six-rank ordering and every task name are exact, but the paper *hypothesizes* the ordering; its own experiments measure only two of the pairs |

The Larkin scan's OCR layer is unreliable on tables and italics, so I located passages by extraction and then read every quoted page as an image: Larkin 67, 71, 77, 90, 99 and Cleveland 531, 532, 536, 537. Nothing needed was illegible. The Cleveland URL fails TLS verification through WebFetch ("unable to verify the first certificate"), so I downloaded it with `curl -k`; the file is a genuine 25-page JSTOR scan, stable URL `http://www.jstor.org/stable/2288400`. Its text layer is accurate in prose and garbage inside figures, so every figure-derived number below comes from the prose describing the figure — those axis labels are unreadable in both the text layer and the image.

### Source 1 — Larkin & Simon (1987)

**Verdict: confirmed with correction.**

#### The two equivalences (p. 67)

> "At the core of our analysis lie the wholly distinct concepts of *informational* and *computational* equivalence of representations (Simon, 1978). Two representations are informationally equivalent if all of the information in the one is also inferable from the other, and vice versa. Each could be constructed from the information in the other. Two representations are computationally equivalent if they are informationally equivalent and, in addition, any inference that can be drawn easily and quickly from the information given explicitly in the one can also be drawn easily and quickly from the information given explicitly in the other, and vice versa."

The authors weaken their own terms on the same page: "'Easily' and 'quickly' are not precise terms. The ease and rapidity of inference depends upon what operators are available for modifying and augmenting data structures, and upon the speed of these operators."

#### Computational, not informational (p. 99)

> "The advantages of diagrams, in our view, are computational. That is diagrams can be better representations not because they contain more information, but because the indexing of this information can support extremely useful and efficient computational processes. But this means that diagrams are useful only to those who know the appropriate computational processes for taking advantage of them."

Indexing by location is the stated mechanism (p. 68): "A data structure in which elements appear in a single sequence is what we will call a sentential representation. A data structure in which information is indexed by two-dimensional location is what we call a diagrammatic representation."

#### What qualifies "sometimes" — three conditions

Missing operators (p. 71): "Because a representation is useful only if one has the productions that can use it, we can readily understand the common complaint of physics professors that students 'refuse to draw diagrams' or 'don't appreciate their value.' If the students lack productions for making physics inferences from diagrams, they may not only fail to 'appreciate' the value of diagrams, but will find them largely useless."

Poor construction (pp. 98–99): "None of these points insure that an arbitrary diagram is worth 10,000 of any set of words. To be useful a diagram must be constructed to take advantage of these features. The possibility of placing several elements at the same or adjacent locations means that information needed for future inference can be grouped together. It does not ensure that a particular diagram does group such information together."

Irrelevant perceptual inferences (p. 99): "Similarly, although every diagram supports some easy perceptual inferences, nothing ensures that these inferences must be useful in the problem-solving process. Failing to use these features is probably part of the reason why some diagrams seem not to help solvers, while others do provide significant help (Paige & Simon, 1966, Larkin, 1983)."

#### Worked examples with numbers

Pulley problem, sentential solution (p. 77, Table 2, read as an image): "Total Elements Searched: 138", per-step row `25 7 20 19 14 22 31`.

The diagrammatic solution is never counted (p. 80): "Compared with the 138 considerations of elements for the sentential representation (see Table 2), the diagrammatic representation provides a large saving." No ratio may be quoted from this paper. Geometry problem (p. 90): "the costs of developing the perceptual elements are evident in Table 5 which includes 40 elements in part (b) (compared with just 5 in part (c) added by the geometry program) … In this form the given data structure has 15 elements, the perceptual productions add 78 more in 41 steps, and the geometry productions just 10 more in five steps." Search cost, same page: "an average of 48/2 = 24 tests." Its diagrammatic counterpart (p. 91) is a formula, not a measurement — `n*(48/2)` for a production spanning `n` locations against `N*(48/2)` for `N` elements sententially.

#### What the programme must change

Four edits in § B1 finding 1.

1. The computational-equivalence gloss reads "any inference in one is as easy and fast as in the other" and drops **"from the information given explicitly in"**. That clause is the whole point: the comparison runs over what each representation states outright, not over what is derivable. Restore it.
2. The informational-equivalence gloss drops the symmetry ("and vice versa"). Restore it.
3. The quote beginning "The advantage 'are computational — diagrams can be better representations…" stitches two sentences and drops "in our view". Replace with the p. 99 text above.
4. The note names no condition under which a diagram fails, leaving the title's "sometimes" unaccounted for. Add the missing-operators condition at minimum — it is the one that carries the note's own agent-versus-human reader split.

The relayed abstract fragment is otherwise sound; the exact text (p. 65) is "Diagrammatic representations also typically display information that is only implicit in sentential representations and that therefore has to be computed, sometimes at great cost, to make it explicit for use." The first-page header prints `COGNITIVE SCIENCE 11, 65-99 (1987)`, but the references run onto page 100, so `65–100` is the full extent.

#### Citation, ready for `rule-cards-provenance.md`

```
Larkin & Simon 1987, Cognitive Science 11(1):65-100 · p. 67 informational
  equivalence (mutual inferability) vs computational equivalence (mutual ease
  from what is stated EXPLICITLY); p. 68 sentential = single sequence,
  diagrammatic = indexed by two-dimensional location; p. 99 "The advantages of
  diagrams, in our view, are computational … not because they contain more
  information, but because the indexing of this information can support
  extremely useful and efficient computational processes"; p. 77 Table 2
  sentential pulley search = 138 elements (diagrammatic count not given); p. 90
  geometry: 40 perceptual elements vs 5 inferential, 48/2 = 24 tests per match
  · qualifiers: a diagram fails without the operators to read it (p. 71), when
  badly constructed (pp. 98-99), and when its easy inferences are irrelevant
  (p. 99) · first-hand, page images
```

### Source 2 — Cleveland & McGill (1984)

**Verdict: confirmed with correction.** The ordering is exact; calling it a *measured* ranking is not.

#### The ordering (p. 536, read as an image)

> "The following are the 10 elementary tasks in Figure 1, ordered from most to least accurate:
> 1. Position along a common scale
> 2. Positions along nonaligned scales
> 3. Length, direction, angle
> 4. Area
> 5. Volume, curvature
> 6. Shading, color saturation"

The programme's ordering matches item for item. Two naming corrections: rank 2 is plural, "Position**s** along **nonaligned** scales" (Figure 1's tile hyphenates it as "POSITION NON-ALIGNED SCALES"); rank 6 is spelled "color saturation". Ten tasks give six ranks because three are ties (p. 537): "Three of the ranks—3, 5, and 6—have more than one task; at the moment there is not enough information to separate the ties."

#### Measured or asserted — asserted, then tested in part

Section 3 is titled "THEORY: ORDERING THE ELEMENTARY PERCEPTUAL TASKS BY THE ACCURACY OF EXTRACTION" and opens (p. 536): "In this section we **hypothesize** an ordering of the 10 elementary perceptual tasks on the basis of the accuracy with which people can extract quantitative information by using them."

Sources of the ordering (p. 537): "The hypothesized ordering of the elementary tasks is based on information from a variety of sources: our own reasoning and experimentation with various graph forms, results of psychophysical experiments, and the theory of psychophysics. The following discussion attempts only a partial documentation." Ranks 3 > 4 > 5 rest on borrowed psychophysics (p. 537): "length judgments are hypothesized to be more accurate than area judgments, which in turn are hypothesized to be more accurate than volume judgments. This ordering is based on a combination of psychophysical theory and experimental results" — Stevens' power law plus Baird's (1970) review, where the exponent runs near 1 for length, below 1 for area, lower still for volume. Rank 2 > 3 rests on reasoning from Weber's Law and a framed-rectangle demonstration (p. 538): "there are additional visual cues on nonaligned scales to help in making judgments".

What the experiments cover (p. 538): "We began checking the hypothesized ordering by running two experiments. The experiments demonstrated very clearly that some judgments of position along a common scale are more accurate than some judgments of length and of angle. Strictly speaking we cannot do more than assert that the results hold for the particular types of graphs in the experiment." The measured span is therefore rank 1 against parts of rank 3, and ranks 4, 5 and 6 were never put in front of a subject in this paper.

#### The experiments (pp. 539–542)

Position-length: 55 subjects, 51 usable, five judgment types over five bar-chart forms, three position judgments and two length judgments; values `10 × 10^((i−1)/12)` for `i = 1..10`, spanning 10 to 56.2, ratios .18 to .83; 50 graphs per packet in random order; subjects told to make "a quick visual judgment and not try to make precise measurements". Position-angle: 54 subjects, 51 usable, pie chart against ordinary bar chart, ten sets of five numbers summing to 100, 20 graphs, 80 judged ratios spanning 10.0% to 99.7%.

Accuracy is `log2(|judged percent − true percent| + 1/8)`, summarised per unit by the midmean, with confidence intervals bootstrapped from 1,000 resamples of the 51 subjects. Results (p. 541): "the average errors for length judgments are 40%-250% larger than those for position judgments"; for angle, "The difference is .97 on the log scale, which is a factor of 2^.97 = 1.96". Gross errors (p. 542): 78% fell on length judgments, a rate 5.3 times the position rate; 88% fell on angle judgments, 7.3 times. All pairs of the five position-length means differ at .05 "except for Judgment Types 2 and 3". The experiments also revise the theory (p. 552): position should become a continuum, since horizontal separation rose 0 → 2.8 → 5.6 cm across Types 1–3 and errors rose with it.

#### The stated guideline (pp. 531, 544, 552)

Abstract: "The theory provides a guideline for graph construction: Graphs should employ elementary tasks as high in the ordering as possible." Section 5 restates it as "elementary perceptual tasks as high in the hierarchy as possible". The authors bound it (p. 552): "The ordering of the perceptual tasks does not provide a complete prescription for how to make a graph. Rather, it provides a set of guidelines that must be used with judgment in designing a graph."

#### Where colour sits

Colour **saturation** shares last place with shading, rank 6 of 6. Colour **hue** is not on the list at all (p. 532): "color hue and texture (Bertin 1973) are two elementary tasks excluded from the list because they do not have an unambiguous single method of ordering from small to large and thus might be regarded as better for encoding categories rather than real variables." Saturation was never shown to a subject either (p. 532): "(Color saturation is not illustrated, to avoid the nuisance and expense of color reproduction.)" Its rank is inherited from the shading argument, and the applied case against shading is a map critique (pp. 547–548), not an experiment.

#### What the programme must change

§ B2 finding 3 says the paper ranks the tasks "by measured accuracy". Replace with *hypothesized* ordering, partially validated: position beats length by 1.4–2.5× and angle by 1.96×, measured; the rest is psychophysical theory plus prior experiments. Its provenance line carries the same wording and needs the same fix.

The colour-redundancy card must not lean on Cleveland & McGill for hue — the paper excludes hue as categorical, ranks saturation, and measures neither. [WCAG 2.2 SC 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html) stays the load-bearing citation, with Cleveland & McGill a hypothesized second reason confined to saturation and shading. Card S-21 (a magnitude row carries its printed number) survives intact and gets stronger: bar length is rank 3, and the measured 40–250% error penalty with a 5.3× rate of gross errors is exactly why the printed number, not the bar, must carry the value. Check S-8 in the appendix may now cite the paper, with the ordering labelled as hypothesis.

#### Citation, ready for `rule-cards-provenance.md`

```
Cleveland & McGill 1984, JASA 79(387):531-554 · p. 536 HYPOTHESIZED ordering of
  10 elementary perceptual tasks in 6 ranks, most to least accurate: position
  along a common scale > positions along nonaligned scales > length/direction/
  angle > area > volume/curvature > shading/color saturation (ranks 3, 5, 6 are
  unbroken ties, p. 537) · p. 537 ordering sourced from "our own reasoning …,
  results of psychophysical experiments, and the theory of psychophysics", not
  from this paper's data · pp. 539-542 two experiments, 51 usable subjects each,
  measure only position vs length (errors 40%-250% larger; 5.3x rate of large
  errors) and position vs angle (1.96x; 7.3x rate) · p. 531 guideline "Graphs
  should employ elementary tasks as high in the ordering as possible", bounded
  at p. 552 as guidelines "used with judgment" · p. 532 color hue and texture
  EXCLUDED from the list as categorical encodings; color saturation ranked but
  never shown to a subject · first-hand, page images
```

### Sources

Read first-hand, as page images:

- Larkin, J. H. & Simon, H. A. (1987). Why a Diagram is (Sometimes) Worth Ten Thousand Words. *Cognitive Science* 11(1):65–100 — [PDF](https://mechanism.ucsd.edu/bill/teaching/F12/cs200/Readings/larkin.whyadiagramissometimesworth.1987.pdf) · [publisher](https://onlinelibrary.wiley.com/doi/10.1207/s15516709cog1101_4)
- Cleveland, W. S. & McGill, R. (1984). Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods. *JASA* 79(387):531–554 — [PDF](https://www.math.pku.edu.cn/teachers/xirb/Courses/biostatistics/Biostatistics2016/GraphicalPerception_Jasa1984.pdf) · [JSTOR](https://www.jstor.org/stable/2288400) · [publisher](https://www.tandfonline.com/doi/abs/10.1080/01621459.1984.10478080)

Named because Cleveland & McGill's ranks 3–5 rest on them, not fetched: [Stevens, S. S. (1975). *Psychophysics*](https://openlibrary.org/search?q=Stevens+Psychophysics+1975), Wiley — the power law; [Baird, J. C. (1970). *Psychophysical Analysis of Visual Space*](https://openlibrary.org/search?q=Baird+Psychophysical+Analysis+of+Visual+Space), Pergamon — the exponent review behind length > area > volume.

## Verification — Mayer's principles and speech transience

First-hand check of the two claim-sets that § B3 relays from secondary summaries.

### Verdicts

- **Claim-set 1 — redundancy and modality: `confirmed with correction`.** Both statements are Mayer's own words; 0.69 is
  Mayer's too, but it is a three-experiment transfer median from 2003, superseded by 0.86 across sixteen tests. The
  decisive correction is scope: Mayer names "the material lacks graphics" as a boundary condition where the redundancy
  effect "can be eliminated or even reversed", and a terminal assistant's spoken summary has no graphics.
- **Claim-set 2 — speech transience: mechanism `confirmed with correction`; the two rules it justifies, `not verified`.**
  Transience has measured consequences in competent adults, but the listening-versus-reading penalty for connected prose
  is null on average (g = 0.07, n.s.), and nothing measures forward references or claims-per-sentence in speech.

### Claim-set 1 — redundancy and modality

#### Mayer's own statements

[Mayer & Fiorella (2014), ch. 12, p. 279](https://edtechuvic.ca/wp-content/uploads/sites/11/2022/09/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles.pdf):

> The redundancy principle is that people learn more deeply from graphics and narration than from graphics, narration,
> and on-screen text. This principle was supported in 16 out of 16 experimental tests, yielding a median effect size
> of 0.86.

Page 299 names the outcome measure — "In all 16 tests, the nonredundant group outperformed the redundant group on tests
of problem-solving transfer, yielding a median effect size of d = 0.86" — and fixes the setting: the principle "involves
a specific situation in which the narration … and the on-screen text … are identical." Table 12.6 (p. 297) lists all
sixteen, ranging 0.19 to 1.91.

[Mayer & Pilegard (2014), ch. 13, p. 316](https://edtechuvic.ca/edci337/wp-content/uploads/sites/11/2022/09/principles-for-managing-essential-processing-in-multimedia-learning-segmenting-pre-training-and-modality-principles.pdf):

> The modality principle is that people learn more deeply from a multimedia message when the words are spoken rather
> than printed. This principle was supported in 53 out of 61 experimental tests, yielding a median effect size of 0.76.

Page 336 carries the form the programme paraphrased: "people tend to learn better from graphics and spoken text than
from graphics and printed text, with a median effect size of d = 0.76."

#### The 0.69 figure

It is Mayer's, it measures problem-solving **transfer**, and it aggregates **three** experiments — Table 3 of
[Mayer & Moreno (2003), *Educational Psychologist* 38(1), p. 46](https://www.uky.edu/~gmswan3/544/9_ways_to_reduce_CL.pdf)
reads "Redundancy effect: Better transfer when words are presented as narration rather narration and on-screen text.
0.69 (3)", and p. 49 names them: "In a series of three studies (Mayer et al., 2001, Experiments 1 and 2; Moreno & Mayer,
2002, Experiment 2) … The median effect size was .69". Those same three reappear in Table 12.6 of the 2014 chapter as
0.88, 1.21 and 0.72 — median 0.88 — so the number is version-dependent and must carry its year.

#### Boundary conditions Mayer states

Redundancy, ch. 12, p. 299: "Three important boundary conditions are that the redundancy effect can be eliminated or
even reversed when the learners are experienced, the on-screen text is short, or the material lacks graphics."
Experienced learners give expertise reversal. Short text next to the graphic reverses the sign on retention — Mayer &
Johnson (2008), d = 0.47 and d = 0.70 favouring the redundant group, with no transfer difference. Without graphics,
"adding on-screen text does not create split attention … because there is no other material to process in the visual
channel"; redundancy also "can hurt learning of a second language when the verbal material is lengthy" (p. 300).

Modality, ch. 13, p. 335: "some potentially important boundary conditions are that the modality principle might not
apply when the learners are knowledgeable, the lesson is self-paced, and the verbal segments are long." Page 337 adds
that "printed words might be helpful when the verbal material contains technical terms, is in the learner's second
language, or is presented in segments that are too large to be held in the learner's working memory."

#### Scope: the graphics-free case runs the other way

Mayer's own graphics-free evidence, ch. 12, p. 300: "students learned better from spoken and printed words than from
spoken words alone when there were no graphics in the lesson (d = 0.24), but not when there was a concurrent animation
along with the printed and spoken words (d = 0.06)." The primary experiment behind that direction is
[Moreno & Mayer (2002), *JEP* 94(1), 156–163](https://tecfa.unige.ch/tecfa/teaching/methodo/MorenoMayer2002.pdf).
Seventy-four college students aged 18–26 heard a lightning explanation as narration alone or as narration plus identical
on-screen text, with no concurrent animation. Adding the printed text helped: "the redundancy effect sizes were 0.78 for
the retention test, 1.62 for the transfer test, and 0.39 for the matching test" (p. 158), all favouring the redundant
presentation, "provided there was no other concurrent visual material" (abstract). The
[Adesope & Nesbit (2012) meta-analysis](https://rex.libraries.wsu.edu/esploro/outputs/journalArticle/Verbal-Redundancy-in-Multimedia-Learning-Environments/99900601157101842)
agrees across 57 studies of mostly postsecondary learners, moderated by "materials without pictures".

A `[SAY]` span is spoken while its own text is printed, with no graphics anywhere — the configuration Moreno & Mayer
tested and found favourable. The redundancy principle is therefore **outside** its scope here, and the evidence at that
boundary points the opposite way from the note's current reading.

#### What the programme must change

1. Delete the tension in § B3 finding 2: with no graphics competing for the visual channel,
   duplicating the conclusion across speech and screen is the measured-better arrangement, needing no condition.
2. Cite 0.86 (2014, sixteen transfer tests, range 0.19–1.91); keep 0.69 only as the 2003 three-study median, with its year.
3. Stop citing the modality principle as backing for the screen/speech split — four of its boundary conditions hold at
   once: knowledgeable learner, self-paced reader, technical terms, no graphics.
4. Say on the card that both principles are defined for multimedia instruction — words plus pictures scored by retention
   and transfer tests — and that the § Voice application rests on the graphics-free literature instead.

#### Citation lines for `references/rule-cards-provenance.md`

```
Mayer & Fiorella 2014 (Cambridge Handbook of Multimedia Learning 2nd ed., ch. 12, pp. 279–315, doi:10.1017/CBO9781139547369.015) · redundancy p. 279 (16/16 tests, median d=0.86 on problem-solving transfer, range 0.19–1.91, Table 12.6 p. 297); boundary conditions p. 299 (experienced learners / short on-screen text / material lacks graphics — "eliminated or even reversed"); no-graphics reversal p. 300 (d=0.24 vs 0.06, relaying Adesope & Nesbit)
Mayer & Moreno 2003 (Educational Psychologist 38(1), 43–52, doi:10.1207/S15326985EP3801_6) · Table 3 p. 46 "0.69 (3)", prose p. 49 · median transfer effect over 3 experiments; superseded by d=0.86 over 16 · always cite the year with the number; the Pittsburgh checklist the note cited carries no effect sizes, so 0.69 arrived via some other secondary summary
Mayer & Pilegard 2014 (Cambridge Handbook 2nd ed., ch. 13, pp. 316–344, doi:10.1017/CBO9781139547369.016) · modality p. 316 (53/61 tests, median d=0.76); boundary conditions p. 335 (knowledgeable learners, self-paced lesson, long verbal segments), p. 337 (technical terms, second language, oversized segments)
Moreno & Mayer 2002 (J. Educational Psychology 94(1), 156–163, doi:10.1037/0022-0663.94.1.156) · 74 college students 18–26; with no concurrent animation, narration + identical on-screen text beat narration alone (d=0.78 retention, 1.62 transfer, 0.39 matching) · primary support for the § Voice duplication rule
Adesope & Nesbit 2012 (J. Educational Psychology 104(1), 250–263, doi:10.1037/a0026147) · 57 studies, mostly postsecondary; spoken–written beats spoken-only, moderated by materials without pictures and system pacing · abstract + moderators verified; effect sizes read inside Mayer & Fiorella 2014
```

### Claim-set 2 — speech transience

Removing re-inspection lowers comprehension, measured in reading: [Schotter, Tran & Rayner (2014), *Psychological Science* 25(6), 1218–1226](http://faculty.cas.usf.edu/eschotter/papers/Schotter_Tran_Rayner_2014_PsychSci.pdf).
Forty native-English-speaking undergraduates read sentences normally or with a trailing mask that blanked each word once
the eyes left it. "There was also a main effect of display condition (b = −0.92, z = 5.09, p < .001); subjects were less
accurate at answering comprehension questions in the trailing-mask condition than during normal reading" (p. 1221); the
ambiguity interaction was only marginal (p = .06), read as the mask decreasing "comprehension globally". The authors
label their 84%-versus-56% comparison "only a speculative explanation", so it must not be quoted as the result.

Listening versus reading the same texts is on average a wash: [Clinton-Lisell (2022), *Review of Educational Research* 92(4), 543–582](https://eric.ed.gov/?id=EJ1347325). Across 46
studies and N = 4,687, "the overall difference between reading and listening comprehension was not reliably different
(g = 0.07, p = 0.23)". Reading wins only where the reader controls the pace (self-paced g = 0.13, p = .049;
experimenter-paced g = −0.32, n.s.) and where questions require inference (g = 0.36, p = .02; literal g = −0.01, n.s.).

Syntactic embedding costs accuracy in heard sentences: [Peelle, Troiani, Wingfield & Grossman (2010), *Cerebral Cortex* 20(4), 773–782](https://pmc.ncbi.nlm.nih.gov/articles/PMC2837088/).
Twenty adults aged 19–27 and twenty aged 60–77 heard six-word sentences with a centre-embedded relative clause. "There
was a main effect of Syntax, reflecting the extra difficulty of the object-relative sentences, F1,38 = 45.47,
MSE = 0.011, P < 0.001 (subject-relative: M = 0.935 proportion correct [SE = 0.007]; object-relative M = 0.843
proportion correct [SE = 0.016])" — nine accuracy points for one embedded clause, collapsed across age groups, worsening
at fast speech (0.867 against 0.918). Mayer states the mechanism at ch. 13, p. 335: "the transient nature of long verbal
segments may be problematic when the presented words exceed what can be held in working memory for a slide."

**What no source supports.** Nothing measures forward references in spoken prose, nor claims-per-sentence in an
assistant's spoken summary. The nearest measured constructs are syntactic embedding (Peelle 2010) and verbal segment
length, whose cognitive-load experiments use school-age samples. The strong form — speech comprehended worse because it
cannot be rewound — is refuted for connected prose in competent adults by the null g = 0.07.

#### What the programme must change

1. Restate transience as costly where integration is required and where the listener cannot set the pace, not as a
   general comprehension penalty for speech.
2. Keep "one claim per sentence, no nesting", cite Peelle et al. (2010) for the nesting half only, and attach no number.
3. Record "no forward references" as a **house convention** evidenced by the operator's own hook usage, and drop the
   two secondary transience sources now listed in the note.

#### Citation lines for `references/rule-cards-provenance.md`

```
Schotter, Tran & Rayner 2014 (Psychological Science 25(6), 1218–1226, doi:10.1177/0956797614531148) · 40 adult native speakers; blocking re-reading lowers comprehension globally (b=−0.92, z=5.09, p<.001; ambiguity interaction n.s., p=.06) · isolates the no-rewind cost, measured in reading rather than listening
Clinton-Lisell 2022 (Review of Educational Research 92(4), 543–582, doi:10.3102/00346543211060871) · 46 studies, N=4,687; listening vs reading g=0.07 (p=.23, n.s.); reading wins only when self-paced (g=0.13) and for inferential comprehension (g=0.36) · refutes a blanket "speech is harder"
Peelle, Troiani, Wingfield & Grossman 2010 (Cerebral Cortex 20(4), 773–782, PMC2837088) · 40 adults (20 aged 19–27); heard centre-embedded sentences, object-relative 0.843 vs subject-relative 0.935 proportion correct, F(1,38)=45.47, p<.001 · backs "no nesting" only
"no forward references" · house convention · evidence = operator's own hook usage; no primary source measures forward reference in spoken prose
```

## Verification — news structure, nominalisation, passive voice, comment drift

Four sources the programme relays from search summaries, each read first-hand from the PDF via PyMuPDF. Every number below was read in the source text, not in a summary of it.

| Source | Verdict |
|---|---|
| Lang (1989), cognitive processing of news as a function of structure | **not verified** |
| Wolfer (2016), nominalisations, Freiburg Legalese Reading Corpus | **confirmed with correction** |
| Ferreira (2021), *In Defense of the Passive Voice* | **confirmed with correction** |
| Wen et al. (2019), code-comment inconsistencies | **confirmed with correction** |

The single load-bearing figure — inconsistent changes ~1.5x more likely to lead to a bug-introducing commit — is **not in Wen et al. (2019)**. It belongs to a 2024 arXiv preprint, detailed in § 4.

---

### 1. Lang (1989) — news structure

**Verdict: not verified.** The candidate URL is a different document by a different author, and Lang (1989) itself is a broadcast-news study that the programme applies to printed text.

The PDF at [pdfs.semanticscholar.org/f2eb/…](https://pdfs.semanticscholar.org/f2eb/ad1fa4020d0647314314457ec2c003516087.pdf) is a 137-page 2008 PhD dissertation, not a 1989 journal article. Its title page reads: "COGNITIVE PROCESSING OF NEWS AS A FUNCTION OF STRUCTURE: A COMPARISON BETWEEN INVERTED PYRAMID AND CHRONOLOGY … by Miglena Sternadori … University of Missouri-Columbia … DECEMBER 2008" (p. 1). Lang (1989) is cited inside it but has no entry in its bibliography; the reference list jumps from Lang et al. (1999) to Lang (2000) (pp. 120–121).

Lang (1989) exists and is confirmed by Crossref: Annie Lang, "Effects of chronological presentation of information on processing and memory for broadcast news", *Journal of Broadcasting & Electronic Media* 33(4), 441–452, September 1989, [doi:10.1080/08838158909364093](https://doi.org/10.1080/08838158909364093). The article is paywalled and returns HTTP 403; I could not read it first-hand. OpenAlex holds only a truncated abstract: "This study shows that the order of information presentation in broadcast news stories influences recall and recognition of information contained in the newscast. Specifically, it was theorized that…" — 28 words, cut off mid-sentence.

The medium is **broadcast television, not print**. The dissertation states it twice: Lang (1989) "found in an exploratory study of television stories" (p. 18), and its own stimuli were built "in approach similar to the one Lang (1989) applied to broadcast news stories" (p. 37). Lang's stimuli were also topic-restricted to a single domain: "Lang (1989), who used only stories related to law enforcement" (p. 74).

The dissertation is the closest existing test of the transfer the programme wants to make — inverted pyramid versus chronology in **printed** text — and it does not support it. Design: 2 (Structure) x 2 (Story) x (Sex) mixed, four newspaper stories of ~300 words each rewritten into both structures, matched on Flesch score, sentence count and concept count (p. 37).

- Attention: chronological stories were read with *slower* secondary-task reaction times, F(1,44)=3.92, p=.05, partial η²=.08, means 412.7 ms chronological vs 396.4 ms inverted pyramid (p. 48, Table 1).
- Recognition memory: no effect, F(1,50)=.01, p=.94, partial η²<.01, means .82 inverted pyramid vs .81 chronology (p. 48, Table 2).
- Cued recall: no effect, F(1,50)=1.32, p=.26, partial η²=.03, means .57 inverted pyramid vs .54 chronology (p. 49, Table 3).
- Comprehension (Sentence Verification Technique): trended in the **opposite** direction to the programme's claim, F(1,49)=3.20, p=.08, partial η²=.06, "this effect was opposite the hypothesized direction such that inverted pyramid stories elicited higher SVT scores than chronological stories did" (p. 49, means .66 vs .64, Table 4).

The abstract summarises it: "No differences emerged for the memory and enjoyment measures, and a marginally significant difference favoring the inverted pyramid structure was observed on the text comprehension measure" (p. vii).

The "complex topics → chronological reading gives more accurate interpretations" claim is, in this literature, a *hypothesis* rather than a finding. The dissertation derives it from Kintsch's construction-integration model — "Assuming that most readers lack sufficient prior knowledge on complex topics in the news, it is likely that they can better derive accurate interpretations (measured through SVT) from reading chronological rather than inverted pyramid texts" (p. 24) — states it as H3, and then reports H3 disconfirmed.

#### What the programme must change

- Stop citing the semanticscholar PDF as Lang (1989). It is Sternadori (2008).
- Drop the counter-finding, or restate it with three qualifiers: broadcast television, law-enforcement stories only, exploratory.
- Remove the "complex topics → chronological" clause entirely. It is an unconfirmed hypothesis, and the only print-medium test of it came out marginally the other way.

#### Citation lines

```
- **R-??** · Lang 1989 (JoBEM 33(4):441–452, doi:10.1080/08838158909364093) · NOT read first-hand; paywalled; abstract truncated at 28 words · medium = broadcast TV, law-enforcement stories, exploratory; do not transfer to written text
- **R-??** · Sternadori 2008 (PhD diss., Univ. of Missouri-Columbia) p. vii, pp. 48–49 Tables 1–4 · print-medium test: STRT F(1,44)=3.92 p=.05 favouring inverted pyramid on resource use; recognition F(1,50)=.01 p=.94 null; cued recall F(1,50)=1.32 p=.26 null; SVT F(1,49)=3.20 p=.08 favouring inverted pyramid · counter-evidence to the relayed claim
```

---

### 2. Wolfer (2016) — nominalisations, Freiburg Legalese Reading Corpus

**Verdict: confirmed with correction.** The reading-time effect is real and strong. The word "comprehension" in the relay overstates what was measured.

Source: Sascha Wolfer, "The impact of nominalisations on the reading process: A case-study using the Freiburg Legalese Reading Corpus", in Hansen-Schirra & Grucza (eds.), *Eyetracking and Applied Linguistics*, 163–186, Language Science Press, 2016, [doi:10.17169/langsci.b108.298](https://doi.org/10.17169/langsci.b108.298) ([PDF](https://langsci-press.org/catalog/view/108/298/512-1)).

Method: eye-tracking while reading, not self-paced reading. "I used an SR Research EyeLink 1000 for data collection. The eye-tracker measured gaze position of the participants with a rate of 1000 Hz" (p. 171). Analysis is linear mixed-effects models in `lme4`, with word length, unigram/bigram/trigram frequency, orthographic familiarity, sentence position, embedding depth and screen-presentation factors regressed out first, and participant and text as random intercepts (pp. 174–175). Participants: "Reading data was collected from 80 human readers (40 for each corpus part)", all students at the University of Freiburg, "It was made sure that none of the participants had an educational background in law", 51 female (p. 171). Genre: German jurisdictional texts — court decisions, press releases and newspaper articles (12,769 tokens), plus 30 excerpts from decisions with moderately and strongly reformulated versions (2,898 tokens), reformulated with a legal expert who preserved semantic content (pp. 167–168).

Measured effects, Table 3 (p. 177), nominalisation versus other nouns:

| Reading variable | Estimate | SE | t/z |
|---|---|---|---|
| First-pass reading time | 0.063 | 0.012 | 5.243 |
| Total reading time | 0.131 | 0.015 | 8.911 |
| Regression path duration | 0.073 | 0.020 | 3.615 |
| Probability of being skipped | -0.536 | 0.033 | -16.087 (p < .0001) |
| Probability of a regressive saccade | 0.059 | 0.035 | 1.662 (p = 0.10) |

Effect magnitude against other word classes, on total reading time (pp. 178–179): nominalisations β=0.053, t=6.80; finite verbs β=0.016, t=2.55; nouns in general β=-0.066, t=-15.15. Nouns are read faster than other words; nominalisations reverse that.

Resolution by verbal transformation is confirmed but weaker than the relay implies. Under the full baseline model there is no significant effect: "If the reading times for the baseline models are used, no significant effects can be shown" (p. 179). Under a reduced model, first-pass reading time on nouns improves (β=-0.076, t=-2.05) while total reading time does not (β=-0.080, t=-1.22). Complexity does not shift onto the new verbs: no effect on first-pass (β=-0.011, t=-0.20) or total (β=-0.106, t=-1.65) reading times for verbs and participles. At text level, strong reformulations are read faster than originals (β=-0.157, t=-2.58); moderate reformulations are not (β=-0.109, t=-1.79).

**The correction.** Comprehension did not improve. "84% of all questions after original excerpts were answered correctly … this figure only rose marginally to 88% for moderately reformulated texts and 87% correctly answered questions for strongly reformulated texts" (p. 182). Wolfer says so himself in the conclusion: "Just because some parts of the texts are read considerably slower does not mean that they are not comprehended at all … if this is also associated with a better understanding of text content remains to be shown" (p. 182). He also failed to replicate the comprehension gain reported by Hansen et al. (2006) (85% vs 75% vs 78%).

#### What the programme must change

- Replace "slower comprehension" with "slower reading, measured by eye-tracking". The conclusion sentence in the paper uses "comprehension processes", but the paper's own comprehension test found no gain.
- Name the genre limit: German court decisions read by non-lawyers. Nothing here is about English or about technical prose.
- Keep "resolved by transforming into verbal structures", but attach the caveat that the noun-level gain survives only under the reduced model, and that the text-level gain reaches significance only for the strong reformulation.

#### Citation lines

```
- **R-??** · Wolfer 2016 (Eyetracking and Applied Linguistics 163–186, doi:10.17169/langsci.b108.298) Table 3 p. 177 (first-pass β=0.063 t=5.24; total β=0.131 t=8.91; skip β=-0.536 p<.0001), pp. 178–179 (nominalisation β=0.053 t=6.80 vs finite verbs β=0.016 t=2.55) · eye-tracking, EyeLink 1000, 80 non-law students, German court decisions · reading time only — comprehension unchanged (84%/88%/87%, p. 182)
```

---

### 3. Ferreira (2021) — *In Defense of the Passive Voice*

**Verdict: confirmed with correction.** The paper argues what the programme says it argues. It is a review essay, not a new empirical study, and its year and citation need fixing.

Source: Fernanda Ferreira, "In defense of the passive voice", *American Psychologist* 76(1), 145–153, January 2021, [doi:10.1037/amp0000620](https://doi.org/10.1037/amp0000620). The candidate URL is the [2020 accepted manuscript](https://psycnet.apa.org/manuscript/2020-19385-001.pdf); the version of record is 2021. Basis: **argument built on prior empirical work, with no new data.** The abstract names "Three motivations for the use of the passive voice based on findings from psycholinguistic research" (p. 1). The evidence cited is other people's: Ferreira (1994), four sentence-production experiments with undergraduates showing more passives with theme-experiencer verbs (p. 8); Haviland & Clark (1974) and V. Ferreira & Yoshita (2003) on the Given-New strategy (p. 15); Forster & Olbrei (1973) on animate-subject passives being as easy as their actives (p. 21); Pullum (2014) on prescriptivist misidentification (p. 12).

The four arguments, in the paper's order:

1. Given-New. "In individual sentences, writers and speakers tend to order words and phrases so that mutually known or established ideas precede new ones, an arrangement that facilitates comprehension" (p. 15), and "Conforming to the Given-New strategy, then, often necessitates the use of the passive voice" (p. 16).
2. Accessibility. A primed concept surfaces early, "and a passive form will emerge simply as a by-product of the need to accommodate that early placement" (p. 16).
3. Non-equivalence. "Passives, then, are not simply inferior versions of active sentences" (p. 19); the get-passive and the be-passive differ in meaning, and active paraphrases can distort.
4. Unenforceability. Writers cannot reliably spot passives: "none of the elements of the heuristic is necessary and all of them are jointly insufficient to reliably identify passives" (p. 12).

**On the programme's narrower scope.** Ferreira addresses the "hides who acts" charge directly and rejects it as a general test. "For some prescriptivists, the ability to leave out the by-phrase is one of the passive's evil features, as it is claimed that it permits agents and perpetrators of actions and events to be left unnamed (as in the classic *Mistakes were made*). However, sometimes the agent is not relevant or is unknown, and in these cases, a structure allowing it to be omitted may be useful" (p. 17). She gives *Stonehenge was built in several stages* as a case where "there is no agent to specify" (p. 11), and notes that for verbs like *impress*, *startle* and *please* the agentless passive *promotes* the human: "a short passive leaves the animate argument to occur alone (e.g., *The reviewers were pleased*), thus spotlighting it" (p. 18).

So the source supports the narrower scope only partially. It concedes the deliberate-evasion case by naming *Mistakes were made* without defending it. It does not endorse "hides who acts" as the trigger, because agent omission is, on her account, usually legitimate. Her prescription is a positive one: "when the expository circumstances call for the passive voice, then scientific writers should use it without embarrassment or apology" (p. 22).

#### What the programme must change

- Cite the version of record: *American Psychologist* 76(1), 145–153, 2021, not 2020.
- Label it a review essay grounded in psycholinguistics, not an experiment. It carries no measurement of its own.
- Narrow the rule further, or add an exemption. Under Ferreira, an agentless passive is the *preferred* form when the agent is unknown or irrelevant, so "hides who acts" cannot be applied as a mechanical trigger. The defensible residue is: flag an agentless passive only where the agent is known and material to the reader's decision.

#### Citation lines

```
- **R-??** · Ferreira 2021 (American Psychologist 76(1):145–153, doi:10.1037/amp0000620) p. 15 (Given-New), p. 16 (accessibility), p. 19 (non-equivalence), p. 12 (passives are unreliably identified) · review essay, no new data; cites Ferreira 1994, Haviland & Clark 1974, Forster & Olbrei 1973, Pullum 2014
- **R-??** · Ferreira 2021 p. 17 ("sometimes the agent is not relevant or is unknown, and in these cases, a structure allowing it to be omitted may be useful"), p. 18 (short passive spotlights the animate argument for impress/startle/please) · limits the "hides who acts" trigger to a known, material agent
```

---

### 4. Wen et al. (2019) — code-comment inconsistencies

**Verdict: confirmed with correction.** Two figures confirmed verbatim. The third is not in the paper.

Source: Fengcai Wen, Csaba Nagy, Gabriele Bavota, Michele Lanza, "A Large-Scale Empirical Study on Code-Comment Inconsistencies", *ICPC 2019*, 53–64, [doi:10.1109/ICPC.2019.00019](https://doi.org/10.1109/ICPC.2019.00019) ([preprint](https://csnagy.github.io/research/pdfs/2019/Wen2019-preprint.pdf)). Read from the 12-page preprint on disk.

**Figure 1 — confirmed.** Abstract, p. 1: "The study has been performed by mining 1.3 Billion AST-level changes from the complete history of 1,500 systems." Restated in Section III-A, p. 4: "Overall, we extracted 1.3 Billion AST-level changes, resulting in a 476 GB database (excluding indexes) we make publicly available". Scope qualifier the programme should carry: all 1,500 systems are **Java** projects on GitHub, each with ≥500 commits and ≥10 stars; Table I, p. 3, gives 1,599,323 Java files, 162,243,714 effective LOC and 3,323,198 commits analysed. The authors name the language limit themselves under threats to external validity (p. 10).

**Figure 2 — confirmed.** Section IV-A, p. 6: "according to our data, 13% to 20% of code changes trigger a comment change in the class and/or in the methods' comments: 13% in case there is complete overlap between the two sets of changes …, 20% in case they are completely disjointed." The RQ1 answer box on p. 7 repeats it: "We confirm previous findings in the literature [12], showing that between 13% and 20% of code changes trigger comment updates." The underlying per-target rates are 7% for method comments and 13% for class comments (p. 6). The paper adds a guard the programme should keep: "This does not imply that in the remaining ~80% of cases code-comment inconsistencies are introduced, but they represent a possibility" (p. 7).

**Figure 3 — not in this paper.** Wen et al. (2019) has two research questions, RQ1 (co-evolution rates) and RQ2 (a taxonomy of inconsistencies fixed by developers, 500 commits labelled, 362 non-false-positives). It contains no bug-proneness analysis, no SZZ, no odds ratio, and the string "1.5" appears only inside a quoted JDK version list. The nearest statement is in related work, Section II-A, p. 2, describing someone else's result: "Ibrahim et al. [14] studied the relationship between comment update practices and bug introduction. Their findings show that abnormal comment update behavior … leads to a higher probability of introducing bugs." No ratio is given.

I checked that upstream source too. [Ibrahim, Bettenburg, Adams & Hassan (2012)](https://sailresearch.github.io/sail-website/data/pdfs/JSS_OnTheRelationshipBetweenCommentUpdatePracticesAndSoftwareBugs.pdf), *JSS* 85(10), 2293–2304, contains no "1.5" figure and runs the opposite way on the headline: "Our findings suggest that inconsistent changes are not necessarily correlated with more bugs. Instead, a change in which a function and its comment are suddenly updated inconsistently, whereas they are usually updated consistently (or vice versa), is risky" (abstract, p. 1).

The 1.5x figure belongs to [Radmanesh, Imani, Ahmed & Moshirpour (2024)](https://arxiv.org/abs/2409.10781), "Investigating the Impact of Code Comment Inconsistency on Bug Introducing", arXiv:2409.10781. Its abstract carries the programme's sentence almost word for word: "Our findings reveal that inconsistent changes are around 1.5 times more likely to lead to a bug-introducing commit" (p. 1).

Exact figures from that paper:

- Section 4.2, p. 14: "inconsistent changes are approximately 1.5 times more likely to result in a bug-introducing commit than normal changes within a one-week window(RQ2), and 1.14 times more likely to do so within a two-week window." The Finding box on the same page states 1.52 and 1.14.
- "Bug-introducing" was determined by GitCProc for bug-fixing commits, then the **SZZ algorithm** to trace back to the introducing commit (Section 3.2.1, p. 10). Inconsistency was detected by a fine-tuned **GPT-3.5**, not by a deterministic analysis.
- Corpus: 32 Apache Java projects (p. 9). Sampling of bug-introducing commits at 90% confidence, 10% margin of error, with a matched non-bug-introducing baseline (p. 10).
- **No confidence intervals and no significance test are reported.** The 2x2 tables give the raw counts. Table 4 (7-day window): 2710 / 36672 / 2342 / 44907, which yields a pooled odds ratio of **1.417**, not 1.52. Table 5 (14-day): 7021 / 102076 / 6654 / 110542, yielding 1.143, matching the stated 1.14. The 1.52 comes from Table 6's per-repository "Total" row (1.5195), whose eight per-repository values range from 0.72 to 2.68 — one of them below 1.
- Status: **arXiv preprint, not peer-reviewed.** The page footer reads "Manuscript submitted to ACM"; OpenAlex records the only version as a 2024 arXiv preprint.

#### What the programme must change

- Keep both Wen figures, and add the Java-only and ≥500-commit/≥10-star selection qualifiers.
- Move the 1.5x claim off Wen entirely. As cited it is a misattribution.
- If the claim is kept, it must be re-cited to Radmanesh et al. 2024 and downgraded: preprint, LLM-based inconsistency labelling, SZZ-derived ground truth, 32 Apache Java projects, no confidence interval, pooled 7-day odds ratio 1.42 against a stated 1.52, and per-repository values crossing 1.0. That is weaker evidence than a rule card should rest on without a note.
- Do not route the claim through Ibrahim et al. 2012 instead. That paper explicitly declines the correlation.

#### Citation lines

```
- **R-??** · Wen 2019 (ICPC 2019:53–64, doi:10.1109/ICPC.2019.00019) Abstract + §III-A p. 4 (1.3 Billion AST-level changes, 476 GB, complete history of 1,500 systems), Table I p. 3 (1,599,323 Java files; 3,323,198 commits) · Java-only, ≥500 commits, ≥10 stars (external-validity threat named p. 10)
- **R-??** · Wen 2019 §IV-A p. 6 and RQ1 box p. 7 (13%–20% of code changes trigger a comment change; 7% method / 13% class) · authors' guard: the remaining ~80% are not thereby inconsistent
- **R-??** · Radmanesh 2409.10781 §4.2 p. 14 (7-day OR ≈1.52 stated / 1.417 pooled from Table 4; 14-day 1.14), §3.2.1 p. 10 (GitCProc + SZZ; GPT-3.5 inconsistency labelling; 32 Apache Java projects) · **arXiv preprint, not peer-reviewed**; no CI, no significance test; per-repo ORs 0.72–2.68 · REPLACES the misattribution of this figure to Wen 2019
- **R-??** · Ibrahim 2012 (JSS 85(10):2293–2304) abstract · counter-evidence: "inconsistent changes are not necessarily correlated with more bugs"; risk attaches to a *deviation* from a function's usual update pattern
```

## Appendix — a Stop hook for the finished answer

The hook is buildable and it ships to the operator's dotfiles, because a `Stop`
hook does receive the finished answer text and can feed a diagnostic the model
reads — but six of its eight checks encode one person's house conventions rather
than anything the marketplace's evidence rule would admit. Every capability
below is quoted from the four docs under Sources;
`docs.claude.com/en/docs/claude-code/hooks` 301-redirects to
[code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks).

### Verified capability

| Question | Doc answer, verbatim |
|--|--|
| `Stop` exists, fires when? | "When Claude finishes responding" |
| Gets the answer text? | Input carries `last_assistant_message` |
| Can block? | `Stop` \| Can block? **Yes** \| "Prevents Claude from stopping, continues the conversation" |
| Diagnostic reaches the model? | Exit 2 — "stderr text is fed back to Claude as an error message" |
| Can rewrite the answer? | No. Only `MessageDisplay`, and "Display-only: the transcript and what Claude sees keep the original" |
| Plugin hooks supported? | "**Location**: `hooks/hooks.json` in plugin root, or inline in plugin.json" |
| Context cost? | "Hooks (1)  SessionStart  (harness-only — no model context cost)" |
| Re-fire limit? | "Claude Code overrides a Stop hook after it blocks eight times in a row without progress" |

**Two blocking paths.** Exit 2 — "Claude Code ignores stdout and any JSON in it.
Instead, stderr text is fed back to Claude as an error message"; the "Claude
doesn't see it" caveat is scoped to "`SessionStart`, `Setup`, and
`SubagentStart`", not `Stop`. Exit 0 + JSON — "JSON output is only processed on
exit 0", and `Stop` takes the "Top-level `decision` field with
`decision: "block"` and `reason`". A warning that does *not* re-run the model is
`systemMessage`, "Warning shown to user". **Input schema**: `session_id`,
`transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `effort`,
`last_assistant_message`, `stop_hook_active` — and `speak.sh` already reads
`.last_assistant_message`, so that field is confirmed by doc and by live script.

**No hook rewrites the answer of record.** My prior assumption was that no hook
touches assistant output at all; the doc refutes it in one narrow place and
confirms it everywhere load-bearing. `MessageDisplay` fires "While assistant
message text is displayed" and `displayContent` "replaces the displayed text on
screen" — display only; other rewrite fields cover tool payloads alone
(`PreToolUse.updatedInput`, `PostToolUse.updatedToolOutput`). A silent repaint
would desynchronise the transcript from what the user read, so I reject that
path on those grounds, not on capability.

**Limits.** Command-hook timeout defaults to 600 s and `Stop` does not lower it.
`Stop` events "don't support matchers and always fire on every occurrence" and
"don't fire on user interrupts". "All matching hooks run in parallel", so this
hook and `speak.sh` run concurrently, neither seeing the other's result. Output
strings are "capped at 10,000 characters". Loop protection: parse
`stop_hook_active` "and exit early if it's `true`", with
`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` raising the eight. Plugin `hooks/` changes
need `/reload-plugins`; a settings edit is picked up by the file watcher. As
precedent, Anthropic's `security-guidance` plugin registers `Stop` for an
"End-of-turn diff review, run in the background" that "fires at most three times
in a row before yielding back to you".

Two things I could not confirm. Whether `additionalContext` on `Stop` re-runs
the model in the same turn or only seeds the next — "non-error feedback that
continues the conversation" reads either way, so the design uses only paths the
doc states unambiguously. And whether `last_assistant_message` is the final text
block or the whole final message when tool calls interleave; I assume the
former, which bounds what the hook sees.

### Accepted checks

Two tiers, split by one question: did the failure destroy a channel the reader
cannot recover by looking at the screen?

```
tier BLOCK  --> span integrity only  --> exit 2, stderr = diagnostic
                speak.sh already produced silence, so a re-answer adds no audio
tier WARN   --> everything else      --> exit 0, {"systemMessage": "…"}
                speak.sh already spoke, so a re-answer would speak twice
```

Every check is conditional — it fires only when the answer already contains the
construct it governs, so it never demands a diagram, a table, or a fence the
answer did not choose. The hook reads a finished string and holds no opinion
about how it was produced, keeping clear of the up-to-36.2 pp cost of
constraining shape before reasoning finishes
([2606.09410](https://arxiv.org/abs/2606.09410), B1). Nothing calls a model: a
`prompt`- or `agent`-type hook would gate on a judge reaching 71.0 % agreement,
κ = 0.549 ([2604.23178](https://arxiv.org/abs/2604.23178), D2). Preprocessing is
shared with `speak.sh` — strip fenced blocks, then inline code spans, before any
prose check, while fence-scoped checks read the unstripped text. Reusing that
exact regex keeps an answer *explaining* the `[SAY]` protocol from tripping the
span checks.

| ID | Tier | Trigger | Decision procedure | Source |
|--|--|--|--|--|
| S-1 | block | `[SAY` outside code | count of `[SAY` ≠ count of tempered-regex matches | § Voice hard rule 2 |
| S-2 | block | any finished answer | zero matched spans | § Voice hard rule 1 |
| S-3 | warn | a matched span body | body holds `` ` ``, ` ``` `, `**`, `](`, leading `- `/`* `/`#`, or `\|` | § Voice hard rule 4 |
| S-4 | warn | `^#{1,6} ` outside a fence | depth is 1 or ≥ 4 | § Screen |
| S-5 | warn | a fence with drawing glyphs | `├└─│┌┼▁█░` and `\|->`/`-->`/`+--`/`=>` both non-empty | § Screen |
| S-6 | warn | a fence with sprite glyphs | a codepoint of `east_asian_width` W, F or A, or an emoji | UAX #11 |
| S-7 | warn | a fence tagged `diff` | a non-empty body line opens with none of `+`, `-`, space | WCAG 2.2 SC 1.4.1 |
| S-8 | warn | a fence with ≥ 2 bar lines | a bar line carries no digit | Cleveland & McGill 1984, the measured position-versus-length pair |

**S-8 carries its citation, on a narrower claim than first drafted.** Cleveland &
McGill 1984 was read first-hand after this table was written — see
[§ Verification — Larkin & Simon, Cleveland & McGill](#verification--larkin--simon-1987-cleveland--mcgill-1984)
— so the block recorded here is lifted, and the check ships exactly as card S-21
does. The six-rank ordering is **hypothesized** (p. 536), not measured, and may be
cited only as such. What the experiments measure is position against length: average
errors for length judgments run 40%–250% larger than for position judgments, and
gross errors occur at 5.3 times the position rate. A bar is length. That measured
pair, not the ordering, is why the printed number carries the value.

What the table cannot show. **S-1** is the highest-value check because the
failure is silent: `speak.sh`'s tempered pattern refuses to match an unclosed
span, so the user hears nothing rather than something wrong. **S-3** covers a
bounded token set, not "markdown" — formulas in general are not decidable, so it
under-reports rather than guesses. **S-4** depends on stripping first, which
stops a shell comment from reading as an `h1`. **S-8**'s two-line floor stops a
single `█` used as a rule from firing; the number is required because bar length
ranks only third of six perceptual encodings (B2), and the printed value removes
the estimation task.

**S-6** tests presence, not width arithmetic, and that is the point: UAX #11
says the property "is not intended for use by modern terminal emulators without
appropriate tailoring", and ambiguous characters "require additional information
not contained in the character code to further resolve their width" (B2). Width
is not computable, so the sound rule excludes the characters whose width is
unresolvable. **S-7** is
[SC 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html)
(Level A) in its one decidable form here — the prefix is the redundant encoding
beside the green and red the terminal paints. Every emitted message names the
operation that fixes the finding rather than the defect alone, per
[2507.14241](https://arxiv.org/abs/2507.14241) on positive framing.

### Rejected candidates

| Candidate | Reason |
|--|--|
| Exactly one `[SAY]` span | Contradicts the rule it claims to enforce — § Voice hard rule 3: "extra spans are a choice, not a limit". Refined into S-2, presence. |
| A language tag on every code/config fence | "When the content is code or config" is a judgement, not a test: § Screen prescribes *untagged* fences for trees, chains and bar charts, and separating those from a config snippet is the semantic call D2 excludes. |
| Untagged fence with a code signature | Narrowed but still left out: firing on `#!/`, `import `, `package `, `def `, `<?xml` in the first non-blank line is high precision and low recall, and the yield does not justify another warning line per turn. |
| "Where colour carries meaning, a word carries it too", general form | The hook cannot see what the terminal paints, so the general criterion has no decision procedure. S-7 is all of it that is decidable. |
| Any semantic § Style rule — answer-first, one claim per sentence, dead openers | Not mechanically decidable; stays with the human-reviewed audit under D2's `needs_human` default. |
| A `prompt`- or `agent`-type hook running an LLM judge | Gates on κ = 0.549, and the judge shares the author's style prior, so it under-flags precisely Claude's native habits (D2 finding 4). |
| 100-column cap on aligned blocks | B2 located no source; a house number the evidence rule refuses. |
| `MessageDisplay` repairing the answer silently | Display-only, so the transcript would stop matching what the user read. |

### Worked example

The answer closes with a bar chart, a `diff`, and a span the model left open.
S-1 blocks, so only the blocking path emits — stderr, exit 2:

```
[style] S-1 span not closed
  An opening [SAY] at offset 1482 has no matching [/SAY].
  speak.sh matches only a closed, tempered span, so this reply is spoken as
  silence. Re-emit the reply with the conclusion in one closed [SAY]…[/SAY].
```

Had S-1 passed, the warn tier would print instead — stdout, exit 0, no re-answer:

```json
{"systemMessage": "[style] 2 findings\n  S-8 fence at line 34: bar rows 2 and 4 carry no number — print each row's value beside its bar.\n  S-7 diff fence at line 51: line 3 opens with a bare word — prefix every body line with +, -, or a space."}
```

### Failure modes and risks

**The user reads two answers.** Blocking leaves the first answer on screen with
a second below it. Bounded by scope: only S-1 and S-2 block, both are rare, and
both mean the first answer already failed to deliver its conclusion aloud.

**Double speech** is the sharpest risk in this operator's setup and the reason
for the tier split. `speak.sh` runs in parallel on the same `Stop`, so it has
already spoken by the time this hook decides. Blocking on a screen check would
make Claude re-answer, `Stop` would fire again, and the conclusion would be
spoken twice. Blocking on S-1 or S-2 is safe precisely because the first answer
produced silence.

**Revision loops.** The platform caps at eight consecutive blocks; the hook caps
at one by reading `stop_hook_active` and exiting 0 when true, since a second
failure on the same turn means the check is wrong, not the answer.

**Noise fatigue.** The warn tier prints at most three findings per turn, one
line each, in ID order, and drops the rest. Three lines of advice on every turn
train dismissal, and a dismissed warning is worse than none.

**Out of reach.** The hook sees `last_assistant_message` only, so prose in
earlier text blocks of the same turn goes unchecked, and an interrupted answer
is never checked. `SubagentStop` is deliberately not registered: a subagent's
output is read by a parent agent, and § Screen governs a terminal reader.

**False positives on legitimate prose**, with what bounds each:

| Class | Bound |
|--|--|
| An answer explaining the `[SAY]` protocol | Fence and inline-code stripping runs first, shared with `speak.sh` |
| A pasted log holding CJK or emoji | S-6 fires only inside a fence that already holds sprite glyphs |
| A single `█` used as a rule | S-8 needs two or more bar lines |
| A table's `\|` beside a drawn box | Unbounded — S-5 fires, and this is the one accepted false positive |
| An answer that is one code block by request | S-2 fires; § Voice still wants the conclusion spoken, so I read this as a true positive |

### Where it ships

**The operator's dotfiles** — `~/.claude/hooks/` plus a `Stop` entry in
`~/.claude/settings.json`, beside the existing `speak.sh` and
`tmux-status.sh stop` entries. The decisive reason is provenance of the rules,
not capability: six of the eight checks read the operator's private
`~/.claude/CLAUDE.md` — the `[SAY]` protocol, the sprite set, the two-level
heading ladder — which is one author's house style. Shipping them inside
`evidence-based-authoring` would impose them on every installer of a plugin
whose other components are read-time advisors a user invokes, not a turn-time
gate firing unasked on every reply. Only S-6 and S-7 trace to a standard, and
the repo's Evidence-Based Rule would admit exactly those two.

Two supporting reasons: the hook must share `speak.sh`'s span-parsing and
code-stripping regex or the two will disagree about what a span is, and plugin
`hooks/` changes need `/reload-plugins` where a settings edit is watched — the
wrong friction for a check tuned repeatedly in its first weeks. Cost does not
decide the location, since hooks are harness-only in either home, which is the
whole reason this enforcement layer can sit beside a small resident rule core
(D1). If S-6 and S-7 later earn a shared home, the shape is a separate opt-in
plugin with `userConfig` gates per check, not a fold into
`evidence-based-authoring`.

### Sources

Documentation, all fetched for this note:
[hooks reference](https://code.claude.com/docs/en/hooks) (events, `Stop`
contract, exit codes, input schema, limits),
[hooks guide](https://code.claude.com/docs/en/hooks-guide) (`stop_hook_active`,
the eight-block cap, `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`),
[plugins reference](https://code.claude.com/docs/en/plugins-reference)
(`hooks/hooks.json`, `${CLAUDE_PLUGIN_ROOT}`, zero context cost, `userConfig`)
and the [security-guidance plugin](https://code.claude.com/docs/en/security-guidance)
(Anthropic's own `Stop`-hook review, capped at three consecutive fires).

Research carried in: [D2](#d2--how-a-style-rule-is-verified) (the κ = 0.549
judge ceiling, binary decomposition, `needs_human` on semantic checks),
[B1](#b1--form-for-a-human-reader) (shape applied after reasoning, never as
a constraint on it), [B2](#b2--terminal-rendering-and-accessibility) (WCAG 2.2 SC 1.4.1;
UAX #11 on unresolvable width; Cleveland & McGill on bars — read first-hand, so
S-8 ships with the citation confined to the measured position-versus-length pair),
[B3](#b3--writing-for-the-ear) (the modality split § Voice implements)
and [D1](#d1--where-output-style-rules-must-live) (residency buys presence, not
obedience — enforcement is an audit over produced text).
