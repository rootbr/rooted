# Cluster 8 — Bounds of transfer and a moving system under test

## Findings

### F8.1 Tested models are retired after about a year, yet the method revises a standing only when a new test arrives; guideline medicine answers ageing evidence with a reassessment interval set from measured decay.

- Answers: 12, 13, 14; frontier 10
- Evidence:
  - Anthropic, Model deprecations — https://docs.anthropic.com/en/docs/about-claude/model-deprecations — full text — "Notifications"; table "Model status" — "providing at least 60 days’ notice before model retirement for publicly released models"; `claude-opus-4-20250514` Retired "June 15, 2026", `claude-opus-4-1-20250805` Retired "August 5, 2026"
  - Shekelle et al., 2001, Validity of the AHRQ clinical practice guidelines, JAMA — https://pubmed.ncbi.nlm.nih.gov/11572738/ — abstract — Results; Conclusions — "about half the guidelines were outdated in 5.8 years"; "As a general rule, guidelines should be reassessed for validity every 3 years."
  - Martínez García et al., 2014, The validity of recommendations from clinical guidelines, CMAJ — https://pubmed.ncbi.nlm.nih.gov/25200758/ — abstract — Interpretation — "Recommendations quickly become outdated, with 1 out of 5 recommendations being out of date after 3 years."
  - Elliott et al., 2017, Living systematic review: 1. Introduction, J Clin Epidemiol — https://pubmed.ncbi.nlm.nih.gov/28912002/ — abstract — "systematic reviews that are continually updated, incorporating relevant new evidence as it becomes available"
- Standing: two or more independent sources (evidence decays and is reassessed on a schedule); one source (the retirement dates, the provider's own page)
- For the method (my inference): missing — rule 7 names no trigger but "a new test", so a rule bounded by a retired model keeps `supported` indefinitely; a `review` field (a date, or the bounded model leaving service, after which `fit` turns to `transfer` until a rerun) would move more standings within a year than any change to the seven rules. The interval would be measured here, not copied; I found no measurement for prompts.

### F8.2 A "same" model service changes behaviour without notice and prompts regress across versions, so a version change leaves the bounds even when the name does not change.

- Answers: 12, 15, 19 (in part); frontier 10
- Evidence:
  - Chen, Zaharia, Zou, 2023, How is ChatGPT's behavior changing over time? — https://arxiv.org/abs/2307.09009 — abstract — "GPT-4 (March 2023) was reasonable at identifying prime vs. composite numbers (84% accuracy) but GPT-4 (June 2023) was poor on these same questions (51% accuracy)"
  - Ma, Yang, Kästner, 2023, (Why) Is My Prompt Getting Worse? — https://arxiv.org/abs/2311.11123 — abstract — "LLM APIs are often updated silently and scheduled to be deprecated"; "regression testing LLMs requires fundamental changes to traditional testing approaches"
  - Yang et al., 2025 (v3 April 2026), What Prompts Don't Say — https://arxiv.org/abs/2505.13360 — abstract — "Under-specified prompts are 2x as likely to regress across model or prompt changes, sometimes with accuracy drops exceeding 20%"
- Standing: two or more independent sources
- For the method (my inference): missing — `scope` and `bounds` take "which version" as prose, so a family name passes; a pinned version id and harness version would close it, an unpinned service leaving the original run's record as the only fact. These papers are also reports of techniques failing to transfer (question 19).

### F8.3 Meaning-preserving edits — format, order of examples — move performance by large amounts, and the best variant for one model does not carry to another: a test supports one text read by one model.

- Answers: 2, 3, 4
- Evidence:
  - Sclar et al., 2023 (v2 2024), Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design — https://arxiv.org/abs/2310.11324 — abstract — "performance differences of up to 76 accuracy points when evaluated using LLaMA-2-13B"; "format performance only weakly correlates between models"
  - Lu et al., 2022, Fantastically Ordered Prompts — https://arxiv.org/abs/2104.08786 — abstract — "a given good permutation for one model is not transferable to another"
  - Mizrahi et al., 2024, State of What Art? — https://arxiv.org/abs/2401.00595 — abstract — "we comprehensively analyze the brittleness of results obtained via single-prompt evaluations across 6.5M instances"
- Standing: two or more independent sources (for few-shot and benchmark prompts; I found no measurement on instruction paragraphs of agent skills)
- For the method (my inference): missing — a synonym, a reordering, a translation or a new neighbouring paragraph is a new condition; if `bounds` named the tested text by hash and said whether paraphrases were sampled, any edit would turn `fit` to `transfer` mechanically, which settles who judges a small edit.

### F8.4 A claim ranges over a population of tasks, files and prompts while its test samples a few; the generalizability critique and audit sampling both require naming the population and the risk of concluding from the sample.

- Answers: 5, 6
- Evidence:
  - Yarkoni, 2022, The generalizability crisis, Behavioral and Brain Sciences — https://pmc.ncbi.nlm.nih.gov/articles/PMC10681374/ — full text — abstract; §3 — "the verbal and statistical expressions of a hypothesis being closely aligned – that is, that the two must refer to roughly the same set of hypothetical observations"; "Generalization to the broader class of stimuli like the ones used is not licensed."
  - IAASA, ISA (Ireland) 530 Audit Sampling, October 2022 — https://iaasa.ie/wp-content/uploads/2022/11/ISA-530_Oct_2022.pdf — full text — ¶5(c), ¶8 — "Sampling risk – The risk that the auditor’s conclusion based on a sample may be different from the conclusion if the entire population were subjected to the same audit procedure."; "each sampling unit in the population has a chance of selection"
- Standing: two or more independent sources; Yarkoni's random-effects remedy is disputed in the BBS commentaries ("There is no generalizability crisis"; secondary: search listing, not opened)
- For the method (my inference): missing — rule 2 asks for "conditions", but no field asks for the population the cases stand for, how they were drawn, or the sampling risk; a rule tested on twelve generated documents holds, strictly, for those twelve. Fields `population` and `sample`, and a rule-2 check question ("does the claim's 'always' range over the set the cases were drawn from?"), would catch a rule built on one prompt pair.

### F8.5 Transfer can be judged by structure, not a yes-or-no mark: transportability decides before data which differences matter, and "near" and "far" are judged one dimension at a time.

- Answers: 1, 2, 7, 9
- Evidence:
  - Pearl & Bareinboim, External Validity: From Do-Calculus to Transportability Across Populations (arXiv 2015) — https://arxiv.org/abs/1503.01603 — abstract — "graph-based procedures for deciding, prior to observing any data, whether causal effects in the target population can be inferred from experimental findings in the study population"
  - Deaton & Cartwright, 2018, Understanding and misunderstanding randomized controlled trials — https://pmc.ncbi.nlm.nih.gov/articles/PMC6019115/ — full text — §2.3 — "The operation of a cause generally requires the presence of support factors"; abstract — "justification is required to extend the results to other groups"
  - Barnett & Ceci, 2002, When and where do we apply what we learn? A taxonomy for far transfer, Psychological Bulletin — https://pubmed.ncbi.nlm.nih.gov/12081085/ — abstract — "a framework that describes 9 relevant dimensions"; "Estimation of a single effect size for far transfer is misguided in view of this complexity."
- Standing: two or more independent sources
- For the method (my inference): keeps: rule 5, with too coarse a field — `fit: transfer` with prose leaves the agent unable to tell whether its task lies in the bounds, and when nearly every rule is a transfer the mark says nothing. Fixed dimensions (model and version, harness, exact text, context, task family, readers), each marked same, near or far, would act as a showing of material difference. Bounds widen without fitting when each new condition is registered before its test (question 9), as `law` and the `PREDICTION` check already allow. M-5's two Deaton & Cartwright quotes stand verbatim in the source.

### F8.6 Moving from a curated set to real sessions is the efficacy-to-effectiveness step, and models detect test conditions, in measured cases changing behaviour because of it.

- Answers: 10, 18 (in part)
- Evidence:
  - Singal, Higgins, Waljee, 2014, A Primer on Effectiveness and Efficacy Trials — https://pmc.ncbi.nlm.nih.gov/articles/PMC3912314/ — full text — Introduction — "Efficacy can be defined as the performance of an intervention under ideal and controlled circumstances, whereas effectiveness refers to its performance under ‘real-world' conditions."
  - Needham et al., 2025, Large Language Models Often Know When They Are Being Evaluated — https://arxiv.org/abs/2505.23836 — abstract — "both AI models and humans are better at identifying evaluations in agentic settings compared to chat settings"
  - Schoen et al., 2025, Stress Testing Deliberative Alignment for Anti-Scheming Training — https://arxiv.org/abs/2509.15541 — abstract — "show causal evidence that this awareness decreases covert behavior, while unawareness increases it"
  - Nayan et al., 2026, Evaluation Awareness Is Not One Capability — https://arxiv.org/abs/2606.23583 — abstract — "compliance measured under test conditions becomes an optimistic upper bound"
- Standing: two or more independent sources (for safety behaviours; for instruction-following on skill rules, unmeasured in what I opened)
- For the method (my inference): missing — rule 5 names "who, what, which version" but not the setting; a field `setting: curated | live` would make a rule supported on generated cases a transfer for real sessions; the agentic finding bears on this repository's tests.

### F8.7 Instructions tested singly lose adherence in company, through density and position, so a single-rule test lies outside the bounds of the composed skill.

- Answers: 11
- Evidence:
  - Jaroslawicz et al., 2025, How Many Instructions Can LLMs Follow at Once? — https://arxiv.org/abs/2507.11538 — abstract — "even the best frontier models only achieve 68% accuracy at the max density of 500 instructions"; "bias towards earlier instructions"
  - Liu et al., 2023, Lost in the Middle — https://arxiv.org/abs/2307.03172 — abstract — "performance is often highest when relevant information occurs at the beginning or end of the input context"
  - Yang et al., 2025 (v3 2026) — https://arxiv.org/abs/2505.13360 — abstract — "simply specifying all requirements does not consistently help, as models have limited instruction-following ability and requirements can conflict"
- Standing: two or more independent sources
- For the method (my inference): needs another procedure for the composed skill — the method has no object "the skill"; a test of the skill against the skill minus one rule, rerun on each change, would stand beside single-rule records.

### F8.8 Models set to be deterministic still vary across runs, so "a rerun confirms" can mean only a result inside an interval fixed beforehand, and a standing is a claim about a distribution for one pinned version.

- Answers: 15, 16
- Evidence:
  - Atil et al., 2024 (v5 2025), Non-Determinism of "Deterministic" LLM Settings — https://arxiv.org/abs/2408.04667 — abstract — "We see accuracy variations up to 15% across naturally occurring runs"; "none of the LLMs consistently delivers repeatable accuracy across all tasks, much less identical output strings"
  - Ouyang, Zhang, Harman, Wang, 2023 (v2 2024), An Empirical Study of the Non-determinism of ChatGPT in Code Generation — https://arxiv.org/abs/2308.02828 — abstract — "setting the temperature to 0 does not guarantee determinism in code generation"
- Standing: two or more independent sources
- For the method (my inference): over-strict — read literally, rule 4's "see the same" asks for what no sampled run gives; a rerun confirms when its rate falls within a tolerance recorded beside `threshold` before the rerun. `supported` is then attainable per pinned version; `law` across versions rarely accumulates before retirement (F8.1).

### F8.9 For a high-risk AI system EU law requires dated, signed test reports, the characteristics of the test data, accuracy for intended groups, and lifetime monitoring; the record holds none of these, and nothing in the method watches a rule in use.

- Answers: 8, 17
- Evidence:
  - Regulation (EU) 2024/1689 (AI Act) — https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689 — full text — Annex IV 2(g) — "the validation and testing procedures used, including information about the validation and testing data used and their main characteristics"; "test logs and all test reports dated and signed by the responsible persons"; Annex IV 3 — "the degrees of accuracy for specific persons or groups of persons on which the system is intended to be used"; Article 72(2) — "The post-market monitoring system shall actively and systematically collect, document and analyse relevant data … on the performance of high-risk AI systems throughout their lifetime"
- Standing: one source (a norm, as published in 2024; whether later amendments such as the Digital Omnibus change these passages I did not check)
- For the method (my inference): needs another procedure for the technical documentation of a high-risk AI system — the record has no signer, date or test-data description; reports from use could open a hypothesis without moving a standing.

### F8.10 When a measure is optimised or a prediction shapes its outcome, the object under test stops being a fixed world; the acceptance path assumes a fixed one.

- Answers: 18
- Evidence:
  - Perdomo, Zrnic, Mendler-Dünner, Hardt, 2020 (v4 2021), Performative Prediction — https://arxiv.org/abs/2002.06673 — abstract — "When predictions support decisions they may influence the outcome they aim to predict"
  - Manheim & Garrabrant, 2018 (v4 2019), Categorizing Variants of Goodhart's Law — https://arxiv.org/abs/1803.04585 — abstract — "The importance of Goodhart effects depends on the amount of power directed towards optimizing the proxy"
  - Hua, Qin, Marks, Nanda, 2025 (v5 March 2026), Steering Evaluation-Aware Language Models to Act Like They Are Deployed — https://arxiv.org/abs/2510.20487 — abstract — "can sometimes detect when they are being evaluated and adjust their behavior to appear more aligned"
- Standing: two or more independent sources (for the phenomenon; its reach to a repository's rule loop is my inference)
- For the method (my inference): missing — rule 6 covers fitting a claim to data, not tuning the system or the rule's wording on the cases that later test it; a rule-3 check question ("could the system have learned the test rather than the claim?"), answered by cases drawn after the rule was fixed, would cover it.

## Open questions

- 8 (off-label owner; recording that the transfer, not the source, failed) — not searched within the budget.
- 14 (quarantine with an exit criterion) — Parry et al., A Survey of Flaky Tests, ACM TOSEM 2021 (https://dl.acm.org/doi/fullHtml/10.1145/3476105) returned a bot-check page; no other source opened.
- 13 (a carry-over test cheaper than a rerun) — Tripathi et al. 2025 (arXiv 2507.05573) recovers behaviour, gives no such test.
- 2 (courts distinguishing precedent) — legal literature not searched; F8.5 answers by analogy.
- 19 (practitioner communities) — blogs and forums excluded by the source rules; no peer-reviewed survey found.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| Anthropic, Model deprecations | https://docs.anthropic.com/en/docs/about-claude/model-deprecations | full text | as read 2026-11-21 |
| Shekelle et al. | https://pubmed.ncbi.nlm.nih.gov/11572738/ | abstract | 2001 |
| Martínez García et al. | https://pubmed.ncbi.nlm.nih.gov/25200758/ | abstract | 2014 |
| Elliott et al. | https://pubmed.ncbi.nlm.nih.gov/28912002/ | abstract | 2017 |
| Chen, Zaharia, Zou | https://arxiv.org/abs/2307.09009 | abstract | v3, Oct 2023 |
| Ma, Yang, Kästner | https://arxiv.org/abs/2311.11123 | abstract | v2, Feb 2024 |
| Yang et al. | https://arxiv.org/abs/2505.13360 | abstract | v3, Apr 2026 |
| Tripathi et al. | https://arxiv.org/abs/2507.05573 | abstract | Jul 2025 |
| Sclar et al. | https://arxiv.org/abs/2310.11324 | abstract | v2, Jul 2024 |
| Lu et al. | https://arxiv.org/abs/2104.08786 | abstract | v2, Mar 2022 |
| Mizrahi et al. | https://arxiv.org/abs/2401.00595 | abstract | v3, May 2024 |
| Yarkoni | https://pmc.ncbi.nlm.nih.gov/articles/PMC10681374/ | full text | 2022 |
| ISA (Ireland) 530 | https://iaasa.ie/wp-content/uploads/2022/11/ISA-530_Oct_2022.pdf | full text | Oct 2022 |
| Pearl & Bareinboim | https://arxiv.org/abs/1503.01603 | abstract | Mar 2015 |
| Deaton & Cartwright | https://pmc.ncbi.nlm.nih.gov/articles/PMC6019115/ | full text | 2018 |
| Barnett & Ceci | https://pubmed.ncbi.nlm.nih.gov/12081085/ | abstract | 2002 |
| Singal, Higgins, Waljee | https://pmc.ncbi.nlm.nih.gov/articles/PMC3912314/ | full text | 2014 |
| Needham et al. | https://arxiv.org/abs/2505.23836 | abstract | v3, Jul 2025 |
| Schoen et al. | https://arxiv.org/abs/2509.15541 | abstract | Sep 2025 |
| Nayan et al. | https://arxiv.org/abs/2606.23583 | abstract | Jun 2026 |
| Jaroslawicz et al. | https://arxiv.org/abs/2507.11538 | abstract | Jul 2025 |
| Liu et al. | https://arxiv.org/abs/2307.03172 | abstract | v3, Nov 2023 |
| Atil et al. | https://arxiv.org/abs/2408.04667 | abstract | v5, Apr 2025 |
| Ouyang et al. | https://arxiv.org/abs/2308.02828 | abstract | v2, Oct 2024 |
| Regulation (EU) 2024/1689 | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689 | full text | OJ, 12 Jul 2024 |
| Perdomo et al. | https://arxiv.org/abs/2002.06673 | abstract | v4, Feb 2021 |
| Manheim & Garrabrant | https://arxiv.org/abs/1803.04585 | abstract | v4, Feb 2019 |
| Hua et al. | https://arxiv.org/abs/2510.20487 | abstract | v5, Mar 2026 |

<!-- COMPLETE -->
