# Critical thinking as a re-check layer over a research report

> Research note. Status: decision material — what to build into the `evidence-based-authoring` pipeline, and how. Implementation not started.
> Date: 2026-07-01. Scope: extending `/researching-topics` and `/discovering-subtopics` with critical appraisal of the finished report.
> Every method traces to a primary source (academic work, standard, or documented practice) per the repository's "Evidence-Based Rule" contract.

---

## 0. Summary

The task is to teach the research pipeline to ask four questions of its own report: **what data is it based on, what assumptions are hidden, what was overlooked, and who benefits from the recommendation?** This is not an extension of question generation (`discovering-subtopics` already does that *before* research) but a new layer — **critical appraisal of the finished conclusion** *after* synthesis.

Key findings:

1. **The gap is real and localized.** The pipeline rigorously verifies *facts and sources* (triangulation, "no recall without retrieval", a hallucination gate) and runs a coverage audit of the *question map*. But it nowhere critiques the *reasoning of the finished report*: it does not grade evidence quality on a scale, does not surface the conclusion's unstated premises, does not look for invisible alternatives, and does not analyze beneficiaries or source funding.

2. **Each of the four questions has a mature, checkable methodological apparatus.** "What data" → GRADE, the evidence hierarchy, lateral reading. "What assumptions" → the Toulmin model (warrant), the Key Assumptions Check, Walton's critical questions. "What was overlooked" → Analysis of Competing Hypotheses, premortem, red team, "consider the opposite". "Who benefits" → cui bono, Freeman's stakeholder analysis, the sponsorship-bias empirics (Lundh, Cochrane 2017: RR 1.27–1.34).

3. **The key implementation constraint (from the LLM literature).** Pure model self-reflection is unreliable and can *worsen* the result (Huang et al. 2023, ICLR 2024); it is distorted by sycophancy (Sharma et al. 2023) and self-preference bias (Zheng et al. 2023). Any automated critic must have an **external anchor**: an explicit rubric (the Constitutional AI pattern), a separate context/model with an adversarial framing, and fresh retrieval to check atomic claims (the RARR/FActScore pattern).

4. **Recommendation — a hybrid, not an either/or.** Move critical appraisal into a **separate critic sub-agent** (modeled on `verification-agent` from `reviewing-java`) that runs as a **gate phase after synthesis** in both `researching-topics` and the discovery path. The critic receives an explicit four-axis rubric, works in a clean context, is framed adversarially ("find the flaws", not "confirm it is good"), and relies on fresh retrieval rather than recalled memory. Small probe questions can, in passing, strengthen the existing `discovering-subtopics` methods (06-assumptions, 03-inversion, 09-meta-questions).

What follows is the step-by-step rationale: the gap (§2), the method landscape across the four axes (§3), the LLM implementation constraints (§4), integration options (§5), a draft rubric as a ready artifact (§6), risks and open questions (§7), and the bibliography (§8).

---

## 1. Framing

The user's four questions are not an arbitrary set but the classic framework of **critical appraisal** of an argument. Each targets a distinct vulnerability of the conclusion:

| User question | What it targets | Classical name |
|---|---|---|
| What is it based on? | Quality and provenance of the evidence base | Evidence appraisal / source criticism |
| What assumptions are hidden? | Unstated premises linking data to conclusion | Assumption surfacing / warrant analysis |
| What was overlooked? | Invisible alternatives, omitted evidence, blind spots | Blind-spot / competing-hypotheses analysis |
| Who benefits from the recommendation? | Interests, funding, conflicts of interest | Cui bono / stakeholder & funding analysis |

Crucially, these questions address the **finished report**, not the research topic. Their role is not to widen coverage (breadth) but to test the soundness of a conclusion already reached. That is what distinguishes the sought layer from what the pipeline already does.

---

## 2. What already exists in the pipeline, and what is missing

The analysis was done after reading `researching-topics/SKILL.md`, `discovering-subtopics/SKILL.md`, `methodology-inventory.md`, `validation-protocol.md`, `source-triangulation.md`, and a grep over all `*.md` in `plugins/`.

### 2.1. Already covered

| Mechanism | Where | What it does |
|---|---|---|
| Fact verification | `researching-topics` Phase 5 | Cross-check across ≥2 independent sources; distinguishes "confirmed fact / single source / opinion / speculation"; surfaces contradictions openly |
| Source triangulation | `source-triangulation.md` | Source ladders by topic type; "no recall without retrieval"; a ban on fabrication; practitioner + academic as disjoint layers |
| Multi-language search | `researching-topics` Phase 3 | Removes retrieval-language bias; canonical terminology vs. the user's phrasing |
| Assumption generation *before* research | `discovering-subtopics` method-06-assumptions | First principles, assumption mapping — but applied to the **topic**, producing questions, not to the report |
| Inversion / premortem *before* research | method-03-inversion | Munger-Jacobi, pre-mortem, reverse brainstorming — again at the question-generation stage |
| "Who benefits from the framing" | method-09-meta-questions | Rests on Paul & Elder Socratic and Ulrich critical heuristics — but about the *topic's framing*, not the report's recommendation |
| Coverage audit | method-10 + `coverage-gap-auditor` | Audits the completeness of the **question map**, not the report |
| Anti-hallucination gate | `validation-protocol.md` | Re-verifies every citation and expert in a separate final pass |

### 2.2. What is missing

| Gap | Why it is a gap |
|---|---|
| **Grading evidence quality** | The pipeline distinguishes "how many sources" but not "how strong". There is no scale like GRADE (High/Moderate/Low/Very Low) and no account of study design (systematic review vs. a single observation). Two independent blog posts count as "confirmation" even though that is a low tier. |
| **Surfacing the finished conclusion's premises** | assumption-mapping works on the topic before research. No one takes the report's final thesis and asks: *what general premise (warrant) must be true for this data to justify this conclusion?* |
| **Searching for invisible alternatives to the conclusion** | There is no ACH-like step: enumerate competing hypotheses and seek **disconfirming** evidence rather than confirmation of the favored one. |
| **Beneficiary and source-funding analysis** | meta-questions asks "who benefits from the topic's framing", but the report never checks: *who funded the cited study, and does the conclusion serve the sponsor's interest?* — even though sponsorship bias is measured and large (§3.4). |
| **Adversarial re-check of the synthesis** | `reviewing-java` has a dedicated `verification-agent` that re-checks reviewers' findings. `evidence-based-authoring` has no analog for the report — the synthesis never passes through a hostile opponent. |
| **Distinguishing correlation from causation** | There is no explicit check of causal claims (Bradford Hill / the false-cause fallacy). |

Conclusion: the pipeline is strong at *verifying the input* (sources) and *question coverage*, but weak at *critiquing the output* (the report's reasoning). That is exactly where the four questions land.

---

## 3. The method landscape across the four axes

Every method below traces to a primary source. Format: **what it does → the concrete checkable question/move → source**. At the end of each axis: what feeds directly into the rubric.

### 3.1. "What is it based on?" — grading evidence quality

**GRADE** (Guyatt et al., *BMJ* 2008;336:924–926). Grades the *certainty* of the evidence base into four levels: High / Moderate / Low / Very Low. An RCT starts as High, an observational study as Low, then it shifts by factors. **Five downgrade factors**: (1) risk of bias, (2) inconsistency (unexplained heterogeneity), (3) indirectness (data not about the population/intervention/outcome in question), (4) imprecision (wide intervals, few events), (5) publication bias. **Three upgrade factors** for observational data: large effect size, dose-response, residual confounding working against the effect. → Move: *grade each key conclusion of the report on this scale and name the downgrade factors.*

**Hierarchy of evidence** (OCEBM Oxford 2011). Systematic reviews > RCTs > cohort > case-control > case series > expert opinion / mechanistic reasoning. → Move: *what design stands behind the claim, and where is it on the ladder?*

**Cochrane risk-of-bias** — RoB 2 for RCTs (5 domains: randomization, deviations from the intervention, missing data, outcome measurement, selective reporting of the result; Sterne et al., *BMJ* 2019;366:l4898) and ROBINS-I for non-randomized studies (7 domains including confounding; *BMJ* 2016;355:i4919). → Move: *is a given result biased on one of the domains?* (Version flag: ROBINS-I has a V2, November 2025, with restructured domains — by default use the 2016 list.)

**SIFT and lateral reading** (Caulfield 2019; Wineburg & McGrew, Stanford HEG, 2017/2019). Empirics: professional fact-checkers judge a site's credibility **more accurately and faster** by reading *laterally* — immediately leaving the page to see what independent sources say about the publisher, its funding, and its authors — whereas historians and students read *vertically* and are fooled by design and self-description. SIFT: **S**top, **I**nvestigate the source, **F**ind better coverage, **T**race claims to origin. → Move: *never judge a source by its own "About" page; first confirm the publisher externally; trace the quote/statistic to the original in context.* The most direct transfer to how an AI should verify a web source.

**Argument from Expert Opinion — Walton's critical questions** (Walton, Reed & Macagno, *Argumentation Schemes*, CUP 2008). Six CQs: (1) how credible is E as an expert; (2) is E an expert in field F specifically; (3) what exactly did E assert; (4) is E personally reliable (bias); (5) is it consistent with other experts; (6) is the assertion backed by evidence. → Move: *apply these six questions to every "experts say…" in the report.*

**Quality of Information Check** (Heuer & Pherson, *Structured Analytic Techniques*). Assess the completeness, source reliability, and currency of each key report; flag those that would overturn the conclusion if they proved false.

*Feeds the rubric:* the GRADE scale (level + downgrade factors), position on the design hierarchy, lateral verification of the publisher, the six CQs for an expert citation.

### 3.2. "What assumptions are hidden?" — surfacing premises

**The Toulmin model** (Toulmin, *The Uses of Argument*, CUP 1958). Six elements: claim, data/grounds, **warrant** (the inference license — the general rule linking data to the thesis), backing, qualifier, rebuttal. The warrant is usually left *unstated*. Diagnostic move: *given data D and conclusion C — what general rule must be true for D to justify C?* The answer is the hidden assumption; then test it for contestability. → The most precise instrument for this question.

**Key Assumptions Check** (Pherson 2005; Heuer & Pherson). Procedure: (1) write out every assumption on cards; (2) round them out with the journalist's Who/What/When/Where/Why/How; (3) sort into **supported / caveated / unsupported**, delete the unsupported; (4) for each survivor ask *under what circumstances would this NOT hold?* Pherson's observation: about one assumption in four collapses under written scrutiny, turning from a Key Assumption into a Key Uncertainty.

**Socratic questioning, type 2 — "probe assumptions"** (Paul & Elder 2006). "What are you assuming? What could you assume instead? How do you justify taking that for granted?"

**RED — Recognize Assumptions** (Watson-Glaser, Pearson TalentLens). "What is taken for granted? How likely is the assumption to be true? What if it is false?" (Flag: wording from a reproduced Pearson text; the direct page returned 403.)

**First principles** (Aristotle, *Posterior Analytics*; Descartes 1637). Strip each claim down to bedrock (axioms, physical constants, definitional invariants) and rebuild upward; mismatches with the field's standard decomposition are hidden assumptions. (Already in `methodology-inventory` §6.)

**False cause / Bradford Hill** (Hill, *Proc. R. Soc. Med.* 1965;58:295–300). A specific but frequent class of hidden assumption — the silent leap from correlation to causation. Hill's nine "viewpoints" (strength, consistency, specificity, **temporality**, dose-response, plausibility, coherence, experiment, analogy; Hill himself warned against treating them as a checklist). → Move: *does the report assert causation or only association? Does the cause precede the effect? Are confounders and reverse causation ruled out?*

**Consider the opposite** (Lord, Lepper & Preston, *JPSP* 1984;47:1231–1243). The instruction "consider the opposite" ("would I have made the same judgment had the evidence pointed the other way?") reduces bias — and *more strongly* than the weak instruction "be unbiased".

*Feeds the rubric:* warrant reconstruction for the main thesis; sorting assumptions supported/caveated/unsupported + the "under what conditions does it fail" test; the correlation-vs-causation check.

### 3.3. "What was overlooked?" — invisible alternatives and blind spots

**Analysis of Competing Hypotheses** (Heuer, *Psychology of Intelligence Analysis*, CIA 1999, ch. 8). Eight steps; the core is the **inversion of the burden**: "the most probable hypothesis is the one with the least evidence against it, not the most evidence for it… the analyst should seek *disconfirming* rather than only confirming evidence". **Diagnosticity**: evidence consistent with *all* hypotheses has no value and is discarded; what discriminates is what counts. → Move: *enumerate competing explanations/recommendations, not just the report's conclusion; for each, look for what disconfirms it.*

**Premortem** (Klein, *HBR* 2007; empirics — Mitchell, Russo & Pennington 1989: prospective hindsight raises the ability to correctly name reasons for a future outcome by **30%**). Procedure: announce that "the project has already failed spectacularly", and in a few minutes independently write down every reason — *especially the ones normally left unsaid out of politeness*. → Move: *imagine the report's recommendation has already led to failure — why?*

**Devil's Advocacy / Red Team / "What If?"** (Heuer & Pherson). Devil's Advocacy — build the strongest case *against* the consensus (necessarily a fresh viewpoint: "an analyst cannot be their own devil's advocate"). Red Team — adopt the opponent's cognitive frame against mirror-imaging. What If — assume an unexpected event *has already occurred* and reason backward.

**Structured Self-Critique** (Pherson). A fixed list: sources of uncertainty (puzzle or mystery?), the process, critical assumptions (how recent and documented are they?), *reversing an assumption* in favor of an alternative, diagnosticity, information gaps, potential for deception, the changed-mind test ("what would make you change the conclusion?"). Principle: change the incentive — analysts are "judged by their ability to find weaknesses" in their own thinking.

**Bloom (Analyze/Evaluate/Create)** (Anderson & Krathwohl 2001). The Create subcategory → *Generating* = propose an alternative hypothesis explaining the same data. Evaluate → *Checking* = search for internal contradictions/errors.

**WYSIATI** (Kahneman 2011). "What You See Is All There Is": System 1 builds a coherent story from the *available* information and ignores what is absent, breeding overconfidence when there are gaps. → Move: *what information is NOT in the report, and is confidence inflated given those gaps?*

**Classes of error** yielding direct probe questions (Walton 2006; Tindale 2007; SEP "Fallacies"): cherry-picking / suppressed evidence (*what contradictory evidence is uncited?*); hasty generalization (*is the sample representative, or an anecdote?*); base-rate neglect (Tversky & Kahneman, *Science* 1974); survivorship bias (Wald; *which cases were filtered out before the data was collected?*).

*Feeds the rubric:* the list of competing hypotheses + search for disconfirmation; a premortem pass over the recommendation; explicit search for suppressed evidence and survivorship/base-rate issues; the question about missing information (WYSIATI).

### 3.4. "Who benefits from the recommendation?" — beneficiaries and funding

**Cui bono** (Cicero, attributing it to L. Cassius Longinus Ravilla). The oldest form of "follow the money": whose interests does the conclusion serve? → Move: *who benefits if the reader follows the report's recommendation, and does that coincide with the source of the recommendation?*

**Stakeholder analysis** (Freeman, *Strategic Management*, 1984). A stakeholder is "any group or individual who can affect or is affected by the achievement of the organization's objectives". Procedure: enumerate all affected parties → mark each one's interest → who gains and who loses → surface the conflict of interest (is the source of a claim also its beneficiary?). (Already in `methodology-inventory` §2 for question generation; here applied to the conclusion.)

**Sponsorship bias — the empirical backbone** (Lundh et al., Cochrane 2017, MR000033). A review of 75 papers: industry-sponsored studies significantly more often report favorable results — **RR 1.27 (95% CI 1.17–1.37)** — and favorable conclusions — **RR 1.34 (95% CI 1.19–1.51)**; restricting to low-risk-of-bias studies *strengthened* the association. Historical illustration: Kearns, Schmidt & Glantz (*JAMA Intern. Med.* 2016) — the Sugar Research Foundation secretly funded a 1967 *NEJM* review that shifted blame for coronary heart disease from sugar to fat. Oreskes & Conway (*Merchants of Doubt*, 2010) — the "doubt is our product" playbook. → Move: *who funded the cited study? Does the conclusion serve the sponsor's interest? Was the sponsor involved in design/analysis? Does the conclusion outrun the data?*

**ICMJE disclosure**. The standard for disclosing financial ties for the **36 months** before submission. → Move: *is there a conflict-of-interest statement at all? Its absence is itself a red flag.*

**CRAAP — Purpose** (Blakeslee, *LOEX Quarterly* 2004). "Why does the source exist — to inform, sell, or persuade?" Important flag: CRAAP inspects a source *in isolation*, and a polished site passes on surface features (Wineburg et al. 2020) — use only together with lateral reading (§3.1), not instead of it.

*Feeds the rubric:* a beneficiary map of the recommendation; a check of key sources' funding against the direction of the conclusion; presence/absence of disclosure.

### 3.5. Cross-cutting foundation (serves all four axes)

- **Paul-Elder** (Paul & Elder, *Miniature Guide*). 8 elements of thought (Purpose, Question, **Assumptions**, Point of View, **Data/Evidence**, Concepts, Inferences, **Implications**) and universal intellectual standards with ready questions: Accuracy ("Is that really so? How to check?"), Depth, Breadth ("Do we need another perspective?"), Logic ("Does it follow from the evidence?"), Fairness ("Do I have a vested interest? Am I representing others' views fairly?"). (Flag: the number of standards varies 8/9/10 across Foundation publications; the Significance questions are reconstructed, not verbatim.)
- **Heuer** (CIA 1999). Awareness of bias by itself does not correct it — an *external structured procedure* is needed. Traps: satisficing, mirror-imaging, premature closure. The rationale for making the critic a *procedure with a rubric* rather than an exhortation to "be critical".
- **Kahneman & Tversky** (*Science* 1974; *Thinking, Fast and Slow* 2011). Base-rate neglect, anchoring, availability, confirmation bias, WYSIATI — the concrete biases the rubric must catch.
- **Tetlock** (*Superforecasting*, 2015). Outside view / base rate first, incremental updating, active open-mindedness. (Flag: "~30% more accurate than intelligence officers" is a journalistic/GJP framing, not a controlled effect size.)

---

## 4. How to implement this in an AI pipeline

The LLM literature gives both recipes and a hard constraint. The constraint matters more than the recipes.

### 4.1. The hard constraint: self-reflection without an external anchor is unreliable

- **LLMs cannot reliably self-correct reasoning** (Huang et al., "Large Language Models Cannot Self-Correct Reasoning Yet", arXiv:2310.01798, ICLR 2024). Under *intrinsic self-correction* — the model revises using only its own knowledge, with no external signal and no oracle — the result often **does not improve and sometimes degrades**. Apparent gains in earlier work are explained by leaked oracle information. → A critic on pure self-reflection can make the report *worse*.
- **Sycophancy** (Sharma et al., arXiv:2310.13548, Anthropic). Models prefer answers matching the user's stated position; they shift off a *correct* answer under pushback; and both human raters and preference models sometimes prefer a convincingly-written sycophantic answer over a correct one. → A critique framed as "confirm the report is good" will agree.
- **Self-preference / self-enhancement bias** (in Zheng et al., arXiv:2306.05685; corroborated by arXiv:2410.21819). A model rates text in its own style / that it produced more highly. → The critic must be *a different model, or at minimum a separate clean context*.

**Three constructive conclusions:** the critic needs (a) an explicit rubric, (b) a separate adversarial context, (c) fresh retrieval.

### 4.2. Recipes that yield durable gains (all with an external anchor)

| Technique | Mechanism | What we take for the re-check layer |
|---|---|---|
| **Constitutional AI** (Bai et al., arXiv:2212.08073, Anthropic) | Critique-and-revise against an explicit set of principles (a "constitution") | The "rubric as constitution" pattern: an externally authored list of critical questions is what makes self-critique steerable and reliable |
| **RARR** (Gao et al., arXiv:2210.08726, ACL 2023) | After generation: produce research questions, **retrieve**, post-edit claims toward verifiability while preserving the original text | The archetype of "re-checking a finished report": runs *after* synthesis, grounded on live search, edits toward verifiability rather than rewriting |
| **Chain-of-Verification** (Dhuliawala et al., arXiv:2309.11495, Meta) | Draft → plan verification questions → **independent** answers → revision | "Factored" checking: answer a question without access to the draft, so as not to re-endorse one's own error |
| **LLM-as-a-judge** (Zheng et al., arXiv:2306.05685) | A strong model judges at the level of human agreement (>80%) | But: position/verbosity/self-enhancement bias → randomize order, normalize length, judge a foreign context against a rubric rather than by "like/dislike" |
| **Multi-agent debate** (Du et al., arXiv:2305.14325; Irving et al., arXiv:1805.00899) | Several instances argue and converge | Two adversarial critics (defender of the thesis vs. attacker) supply the "separate context" that introspection lacks |
| **Self-consistency / SelfCheckGPT** (Wang et al., arXiv:2203.11171; Manakul et al., arXiv:2303.08896) | Sample several paths/answers; divergence = a flag | A cheap triage: which claims diverge when resampled → send only those into the expensive retrieval |
| **FActScore** (Min et al., arXiv:2305.14251) | Decompose into **atomic facts**, score the fraction supported | Scoring granularity: split a paragraph into atomic claims and check each, not the report as a whole |

### 4.3. Recommended critic architecture

Combine the three anchors:

1. **Rubric (constitution)** — explicit critical questions across the four axes (§6). It sets *what* to check and makes the critique reproducible and auditable.
2. **A separate adversarial context** — the critic runs as a separate sub-agent (modeled on `verification-agent` in `reviewing-java`), in a clean context, framed as "find the flaws and give the refutation", *without seeing* cues about the desired conclusion. Against sycophancy and self-preference. Optionally — two critics (defend/attack) in debate mode.
3. **Fresh retrieval** — atomic claims and evidence-quality grades are checked by new search (RARR/FActScore), not by re-narrating the context. Triage via self-consistency: first cheaply flag the diverging claims, then expensively check only those.

The critic's output is not a rewritten report but a **structured addendum**: per axis, a list of findings with a confidence level, plus edits/caveats to the original text (preserving wording, as in RARR).

---

## 5. Integration options

| Option | What we do | Pros | Cons |
|---|---|---|---|
| **A. Fold into existing skills** | Add a critical-appraisal phase to `researching-topics` (Phase 5.5 between Verification and Synthesis) and probe questions into `discovering-subtopics` method-06/03/09 | Small surface increase; reuses the flow; nothing new to "sell" | The critic shares context with the author → self-preference/sycophancy (§4.1); a phase inside the same pass violates the "separate context" requirement; risk of bloating SKILL.md |
| **B. A new critic skill as a gate** | A separate `/appraising-research` (or `research-critic` sub-agent) invoked after synthesis; clean context, rubric, retrieval | Honors the "separate context"; reused on both the direct and discovery paths; audited separately; consistent with the `verification-agent` pattern | More surface; needs its own eval; one more step in the pipeline (token/time cost) |
| **C. Hybrid (recommended)** | The core is the critic sub-agent from option B, invoked as a gate phase from `researching-topics` (both paths). Plus lightweight probe questions from §3 strengthen the existing discovery method-agents | Splits responsibility correctly: question generation (discovery) ≠ conclusion critique (critic); the external context is honored; touches existing files minimally | Double documentation work; requires aligning the critic's interface with both paths |

**Rationale for C.** The §4.1 requirement of a separate context effectively rules out pure option A for the *core* of the critique. At the same time, small moves (e.g. "consider the opposite", warrant reconstruction) organically strengthen the discovery methods and need no separate pass — reasonable to add there (partly A). The in-repo precedent is `reviewing-java` with a dedicated `verification-agent` that re-checks findings; the same pattern carries over to a research report.

**Note on the repository contract.** CLAUDE.md: "MUST run `/auditing-ai-context` on every SKILL.md or agent prompt change before committing." This report changes no code — the gate does not apply. But *any* subsequent implementation (a new skill, a sub-agent, or edits to method prompts) must pass `/auditing-ai-context` and, for the discovery skill, `validation-protocol.md` (reliable@10 + coverage ≥0.90, hallucination ≤0.02).

---

## 6. Draft rubric (a ready artifact for the decision)

Below is a draft "constitution" for the critic: critical questions across the four axes. Each item carries a source (per the repository contract: every rule cites a primary source) and a failure signal (what counts as a red flag). This is what would become the core of the skill/sub-agent if an implementation is chosen.

### Axis 1 — What is it based on?
1. What **level of evidence** does each key conclusion have on the High/Moderate/Low/Very Low scale, and what factors downgrade it (risk of bias, inconsistency, indirectness, imprecision, publication bias)? — GRADE, Guyatt et al. 2008. *Failure: a conclusion presented as firm while resting on Low/Very Low.*
2. What **study design** stands behind the claim, and where is it on the hierarchy (systematic review → RCT → cohort → case series → opinion)? — OCEBM 2011. *Failure: opinion/anecdote presented as the equivalent of data.*
3. Is the **source's publisher confirmed externally** (lateral reading), rather than from its own "About" page? Is the quote/statistic traced to the original in context? — Wineburg & McGrew 2017/2019; Caulfield SIFT. *Failure: authority taken from the source's self-description.*
4. For every "experts say…" citation — do the six CQs pass (expertise, field, what exactly was said, reliability/bias, agreement with others, evidence)? — Walton et al. 2008. *Failure: an appeal to an authority outside its field or without data.*

### Axis 2 — What assumptions are hidden?
5. What is the **warrant** of the main thesis — what general rule must be true for the data to justify the conclusion? Does it survive being stated? — Toulmin 1958. *Failure: a warrant that, once stated, turns out to be contestable.*
6. A list of the report's assumptions, sorted **supported / caveated / unsupported**; for each survivor — under what conditions does it fail? — Pherson Key Assumptions Check. *Failure: the conclusion rests on an unsupported assumption.*
7. Does the report assert **causation** where the data give only correlation (temporality, dose-response, confounders, reverse causation)? — Bradford Hill 1965. *Failure: post hoc / cum hoc.*

### Axis 3 — What was overlooked?
8. Which **competing hypotheses/recommendations** explain the same data, and what evidence *disconfirms* each one (rather than confirming the favorite)? — Heuer ACH 1999. *Failure: a single hypothesis considered, confirmation sought.*
9. **Premortem**: if the recommendation has already led to failure — why? — Klein 2007. *Failure: not a single plausible failure path named.*
10. What **contradictory evidence** is uncited (suppressed evidence)? Are we looking only at "survivors" (survivorship)? Is the base rate accounted for? — Walton 2006; Wald; Tversky & Kahneman 1974. *Failure: systematic omission of inconvenient data.*
11. What information is **not** in the report, and is confidence inflated given those gaps (WYSIATI)? — Kahneman 2011. *Failure: a confident tone despite obvious gaps.*

### Axis 4 — Who benefits?
12. Who **benefits** if the reader follows the recommendation, and does the beneficiary coincide with the source of the recommendation? — cui bono; Freeman 1984. *Failure: the source of the recommendation is also its beneficiary, and this is undisclosed.*
13. Who **funded** the key cited studies; does the conclusion serve the sponsor's interest; was the sponsor involved in design/analysis; does the conclusion outrun the data? — Lundh et al. 2017 (RR 1.27–1.34). *Failure: a sponsored source, a conclusion favoring the sponsor, no caveat.*
14. Is there a **conflict-of-interest statement**; what is the source's purpose (inform/sell/persuade)? — ICMJE; CRAAP-Purpose. *Failure: no disclosure where one is expected.*

### Cross-cutting pass
15. Paul-Elder standards on the report as a whole: Accuracy, Logic ("does the conclusion follow from the evidence?"), Breadth ("another perspective?"), Fairness ("are opposing positions represented fairly?"). — Paul & Elder.
16. Changed-mind test: **what would make you change the conclusion?** If there is no answer — the conclusion is unfalsifiable and therefore suspect. — Pherson Structured Self-Critique.

---

## 7. Risks and open questions

**Implementation risks**
- *Cost.* Another pass with retrieval doubles part of the work. Mitigate with self-consistency triage (expensively check only the diverging claims) and by running the critic only on the discovery path and on explicit request on the direct path.
- *Sycophancy/self-preference.* If the critic sees the desired conclusion or shares context with the author, it will agree (§4.1). A clean context and an adversarial framing are mandatory.
- *False rigor.* GRADE/RoB are tuned for medicine; transferring to arbitrary topics (consumer, technical) requires an adapted, not literal, scale. Otherwise the critic will stamp "Low evidence" on topics where an RCT is inherently inapplicable.
- *Bloat.* A 16-item rubric on every report is tiring. Ranking is possible: start with the axes of greatest risk for the given topic (consumer → axis 4 beneficiaries; scientific → axes 1–2).

**Open questions for the decision**
1. Core — a separate skill (`/appraising-research`) or a sub-agent inside `researching-topics` (e.g. `research-critic` alongside the phases)? This determines the surface and the eval.
2. The critic — the same model in a clean context, or an explicitly different/cheap one for triage + a strong one for the verdict?
3. Run the critic always, only on the discovery path, or by flag? (G-09 warns: discovery is not cheap; the critic adds more.)
4. Is a debate mode (two critics) needed, or is one adversarial pass enough? Debate is more expensive but stronger against self-preference.
5. How to adapt a GRADE-like scale to non-medical topics without losing discipline or fabricating rigor?
6. Output format: an addendum to the report, a separate appraisal file, or inline caveats in the RARR style?

**Verification flags** (carried from the research, to be quoted with caution): Walton's CQs for ad populum and cause-to-effect — not confirmed verbatim from an open source; Paul-Elder — the number of standards varies 8/9/10, the Significance questions are reconstructed; the RED wording — from a reproduced Pearson text (direct page 403); Herzog & Hertwig 2009 — the effect is given as a task figure (130.8→123.2), not universal; "superforecasters 30% better" — a journalistic framing; ROBINS-I — by default the 2016 domains, not V2 (2025); Mitchell/Russo/Pennington 1989 — the volume/pages (JBDM 2:25–38) not checked against the journal directly.

---

## 8. Bibliography

**Classic critical-thinking frameworks**
- Paul, R. & Elder, L. *The Miniature Guide to Critical Thinking: Concepts and Tools*. Foundation for Critical Thinking. — criticalthinking.org/pages/the-elements-of-reasoning-and-the-intellectual-standards/480 ; /universal-intellectual-standards/527
- Paul, R. & Elder, L. (2006). *The Thinker's Guide to the Art of Socratic Questioning*. — criticalthinking.org/files/SocraticQuestioning2006.pdf
- Toulmin, S. (1958). *The Uses of Argument*. Cambridge University Press. DOI:10.1017/CBO9780511840005
- Walton, D., Reed, C. & Macagno, F. (2008). *Argumentation Schemes*. Cambridge University Press. ISBN 978-0-521-72374-9
- Walton, D. (2006). *Fundamentals of Critical Argumentation*. Cambridge University Press.
- Tindale, C. (2007). *Fallacies and Argument Appraisal*. Cambridge University Press.
- Anderson, L.W. & Krathwohl, D.R. (Eds.) (2001). *A Taxonomy for Learning, Teaching, and Assessing*. Longman. — Krathwohl (2002), *Theory Into Practice* 41(4).
- Watson-Glaser Critical Thinking Appraisal / RED model. Pearson TalentLens. — talentlens.com/watson-glaser
- Stanford Encyclopedia of Philosophy, "Fallacies". — plato.stanford.edu/entries/fallacies/

**Structured analytic apparatus and decision science**
- Heuer, R.J. Jr. (1999). *Psychology of Intelligence Analysis*. CIA Center for the Study of Intelligence.
- Heuer, R.J. Jr. (2005/2007). *Improving Intelligence Analysis with ACH*. Pherson Associates. — pherson.org
- Heuer, R.J. Jr. & Pherson, R.H. (2011/2020). *Structured Analytic Techniques for Intelligence Analysis*. CQ Press/SAGE.
- Pherson, R. (2005). *Overcoming Analytic Mindsets: Five Simple Techniques*. — pherson.org
- Klein, G. (2007). "Performing a Project Premortem". *Harvard Business Review* 85(9):18–19.
- Mitchell, D.J., Russo, J.E. & Pennington, N. (1989). "Back to the future: Temporal perspective in the explanation of events". *J. Behavioral Decision Making* 2(1):25–38.
- Lord, C.G., Lepper, M.R. & Preston, E. (1984). "Considering the Opposite". *JPSP* 47(6):1231–1243.
- Herzog, S.M. & Hertwig, R. (2009). "The Wisdom of Many in One Mind". *Psychological Science* 20(2):231–237.
- Freeman, R.E. (1984). *Strategic Management: A Stakeholder Approach*. Pitman.
- Cicero, *Pro Roscio Amerino*; *Pro Milone* (cui bono / L. Cassius Longinus Ravilla).
- Tetlock, P.E. & Gardner, D. (2015). *Superforecasting*. Crown.
- Tversky, A. & Kahneman, D. (1974). "Judgment under Uncertainty". *Science* 185(4157):1124–1131.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

**Evidence and source appraisal**
- Guyatt, G.H. et al. (2008). "GRADE: an emerging consensus…". *BMJ* 336(7650):924–926.
- OCEBM Levels of Evidence Working Group (2011). "The Oxford 2011 Levels of Evidence". — cebm.ox.ac.uk
- Sterne, J.A.C. et al. (2019). "RoB 2". *BMJ* 366:l4898. / Sterne et al. (2016). "ROBINS-I". *BMJ* 355:i4919.
- Blakeslee, S. (2004). "The CRAAP Test". *LOEX Quarterly* 31(3):6–7.
- Caulfield, M. (2019). "SIFT (The Four Moves)". *Hapgood*. — hapgood.us
- Wineburg, S. & McGrew, S. (2017/2019). "Lateral Reading". Stanford HEG WP 2017-A1; *Teachers College Record* 121(11).
- Hill, A.B. (1965). "The Environment and Disease: Association or Causation?". *Proc. R. Soc. Med.* 58(5):295–300.
- Lundh, A. et al. (2017). "Industry sponsorship and research outcome". *Cochrane* MR000033.pub3.
- Kearns, C.E., Schmidt, L.A. & Glantz, S.A. (2016). *JAMA Internal Medicine* 176(11):1680–1685.
- Oreskes, N. & Conway, E.M. (2010). *Merchants of Doubt*. Bloomsbury.
- ICMJE. "Recommendations… Conflicts of Interest". — icmje.org
- Ioannidis, J.P.A. (2005). "Why Most Published Research Findings Are False". *PLoS Medicine* 2(8):e124.
- Simmons, J.P., Nelson, L.D. & Simonsohn, U. (2011). "False-Positive Psychology". *Psychological Science* 22(11):1359–1366.
- Rosenthal, R. (1979). "The File Drawer Problem". *Psychological Bulletin* 86(3):638–641.

**LLM self-critique and verification**
- Dhuliawala, S. et al. (2023). "Chain-of-Verification Reduces Hallucination". arXiv:2309.11495.
- Madaan, A. et al. (2023). "Self-Refine". arXiv:2303.17651.
- Shinn, N. et al. (2023). "Reflexion". arXiv:2303.11366.
- Bai, Y. et al. (2022). "Constitutional AI". arXiv:2212.08073.
- Zheng, L. et al. (2023). "Judging LLM-as-a-Judge with MT-Bench". arXiv:2306.05685.
- Du, Y. et al. (2023). "Improving Factuality… through Multiagent Debate". arXiv:2305.14325.
- Irving, G., Christiano, P. & Amodei, D. (2018). "AI safety via debate". arXiv:1805.00899.
- Wang, X. et al. (2022). "Self-Consistency Improves CoT". arXiv:2203.11171.
- Gao, L. et al. (2022/2023). "RARR: Researching and Revising What Language Models Say". arXiv:2210.08726.
- Min, S. et al. (2023). "FActScore". arXiv:2305.14251.
- Manakul, P. et al. (2023). "SelfCheckGPT". arXiv:2303.08896.
- Huang, J. et al. (2023). "Large Language Models Cannot Self-Correct Reasoning Yet". arXiv:2310.01798.
- Sharma, M. et al. (2023). "Towards Understanding Sycophancy in Language Models". arXiv:2310.13548.
