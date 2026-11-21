# Cluster 11 — Independence, authority and whose knowledge counts

The method defines its reader by context alone: `method-provenance.md` S-5, "a record is read by a reader that saw nothing of the work"; neither text names the reader's model family, interests or calibration.

## Findings

### F11.1 Models of one provider, and strong models generally, share their errors, so a reader that "saw nothing of the work" but shares the author's family is not independent in its errors.

- Answers: 2, 5, 9; frontier 5
- Evidence:
  - Kim et al., 2025, Correlated Errors in Large Language Models (ICML) — https://arxiv.org/pdf/2506.07962 — full text — paragraph opening "Our work complements this analysis" — "are different LLMs more correlated with each other than they are with ground truth? We find that they are, and that this is worse among models within the same model company and larger models"
  - Goel et al., 2025, Great Models Think Alike and this Undermines AI Oversight (ICML) — https://arxiv.org/abs/2502.04313 — abstract — "model mistakes are becoming more similar with increasing capabilities, pointing to risks from correlated failures."
- Standing: two or more independent sources
- For the method (my inference): missing — S-5 should require a reader that differs from the author in its source of errors (another family, a human, or ground truth) and the record should name the reader's model; a fresh context removes knowledge of the work, not shared blind spots.

### F11.2 When one model family writes the cases, labels them and judges the outputs, the test inflates that family's own score, and the bias compounds across roles.

- Answers: 5, 8, 9; frontier 5
- Evidence:
  - Xu et al., 2025 (v3 2026; EMNLP 2026), When LLMs Benchmark Themselves — https://arxiv.org/abs/2509.26600 — abstract — "LLM-generated benchmarks systematically favor the model that created them" … "self bias arises from two compounding sources, LLM as a testset and LLM as an evaluator, and their combination amplifies the effect."
  - Silencer, 2025 — https://arxiv.org/abs/2505.20738 — abstract — self-bias attributed "to sub-biases arising from question domain, language style, and wrong labels".
- Standing: two or more independent sources (both on benchmarks of model capability; transfer to tests of instruction documents is my inference)
- For the method (my inference): missing — rule 3 should name the case where cases, labels and judge come from the family under test: such a run measures the family's agreement with itself until labels from outside it are added.

### F11.3 A judge's repeatability is not its validity: high self-consistency coexists with low agreement with humans, and whether model judges match humans depends on the task, the expertise of the humans and who wrote the text.

- Answers: 3, 7, 9; frontier 5
- Evidence:
  - When Consistency Does Not Mean Reliability, 2026 — https://arxiv.org/abs/2609.13824 — abstract — Pearson 0.275 and 0.340 with human raters, yet consistency of 97.3% and 92.3%: "high self-consistency does not necessarily indicate high agreement with human judgments." (two 7–8B judges; small)
  - Bavaresco et al., 2025, LLMs instead of Human Judges? (ACL) — https://arxiv.org/abs/2406.18403 — abstract — "We conclude that LLMs should be carefully validated against human judgments before being used as evaluators."
  - Zheng et al., 2023, Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena — https://arxiv.org/abs/2306.05685 — abstract — "achieving over 80% agreement, the same level of agreement between humans."
- Standing: disputed: Zheng (judges match humans on chat preference) vs Bavaresco (wide variance over 20 tasks); separated by the task, the humans' expertise and who wrote the text.
- For the method (my inference): missing — a rerun of a model reader (rule 4) shows repeatability only; a record resting on a model's reading should carry its agreement with an outside reference.

### F11.4 What turns a model-judged run back into a test is a set of labels made outside the models; statistics stretch a small set, but at most twofold when the judge is no better than what it judges.

- Answers: 7, 9; frontier 5
- Evidence:
  - Angelopoulos et al., 2023, Prediction-Powered Inference (Science 382) — https://arxiv.org/abs/2301.09633 — abstract — valid inference "without making any assumptions on the machine-learning algorithm that supplies the predictions."
  - Dorner et al., 2024 (ICLR 2025), Limits to scalable evaluation at the frontier — https://arxiv.org/abs/2410.13341 — abstract — "when the judge is no more accurate than the evaluated model, no debiasing method can decrease the required amount of ground truth labels by more than half."
  - SEP, Experiment in Physics (rev. 2023) — https://plato.stanford.edu/entries/physics-experiment/ — full text — paragraph opening "Hacking's answer is correct as far as it goes" — "Experimental checks and calibration, in which the experimental apparatus reproduces known phenomena."
- Standing: two or more independent sources; the regress itself is disputed in the same SEP entry: Collins (broken by negotiation) vs Franklin's strategies.
- For the method (my inference): missing — the regress stops at known cases: a judge's reliability is a hypothesis of its own, supported on labels made outside the models, and the record names that set and its size.

### F11.5 A model checking its own answer without outside feedback does not improve and can degrade it; a sound external verifier helps.

- Answers: 2, 6
- Evidence:
  - Huang et al., 2023 (ICLR 2024), Large Language Models Cannot Self-Correct Reasoning Yet — https://arxiv.org/abs/2310.01798 — abstract — "LLMs struggle to self-correct their responses without external feedback, and at times, their performance even degrades after self-correction."
  - Stechly et al., 2024, On the Self-Verification Limitations… — https://arxiv.org/abs/2402.08115 — abstract — "We observe significant performance collapse with self-critique and significant performance gains with sound external verification."
- Standing: two or more independent sources; both predate 2025 reasoning models, and neither tests a fresh-context instance.
- For the method (my inference): keeps: rule 3 — support must come from outside the author; that a same-model fresh reader suffices is an untested hypothesis, not settled by S-5.

### F11.6 Model evaluators prefer their own outputs, and stronger models keep the harmful part when wrong, so a model that is both origin and judge is not one origin among equals.

- Answers: 6, 2
- Evidence:
  - Panickssery et al., 2024 (NeurIPS), LLM Evaluators Recognize and Favor Their Own Generations — https://arxiv.org/abs/2404.13076 — abstract — "we discover a linear correlation between self-recognition capability and the strength of self-preference bias"
  - Chen et al., 2025, Do LLM Evaluators Prefer Themselves for a Reason? — https://arxiv.org/abs/2504.03846 — abstract — "Harmful self-preference persists when evaluator models err as generators, and stronger models display more pronounced harmful self-preference bias when they do err"
- Standing: disputed: how much self-preference is bias (Panickssery, subjective summaries) vs earned quality (Chen, verifiable tasks); both find a harmful part.
- For the method (my inference): missing — `method.md` makes "a model" an equal origin and says nothing of a model that also grades; origin and judge of a test need separate rules.

### F11.7 Auditing defines independence by five threats, and the self-review threat extends to colleagues of the same firm; the reader rule covers one.

- Answers: 1, 2, 10
- Evidence:
  - IESBA, 2018, Handbook of the International Code of Ethics — https://www.icam.mw/wp-content/uploads/2019/01/IESBA-Handbook-Code-of-Ethics-2018.pdf — full text — 120.6 A3(b) — "Self-review threat – the threat that a professional accountant will not appropriately evaluate the results of a previous judgment made; or an activity performed by the accountant, or by another individual within the accountant's firm"; the others: self-interest, advocacy, familiarity, intimidation.
- Standing: one source (a norm, 2018 edition; later editions renumbered, not opened)
- For the method (my inference): missing — a same-family reader is the analogue of "another individual within the accountant's firm"; the record could state per threat why it is acceptable.

### F11.8 Who runs and pays for a test shifts its result beyond what checks of method detect, which is why journals require disclosure of interests.

- Answers: 10, 11
- Evidence:
  - Lundh et al., 2017, Industry sponsorship and research outcome (Cochrane MR000033.pub3) — https://findresearcher.sdu.dk/ws/files/145419585/Industry_sponsorship_and_research_outcome.pdf — full text — Main results / Authors' conclusions — "favorable efficacy results, RR: 1.27 (95% CI: 1.17 to 1.37) (25 papers)"; "Our analyses suggest the existence of an industry bias that cannot be explained by standard 'Risk of bias' assessments."
  - ICMJE, Recommendations, Author Responsibilities — Conflicts of Interest (page © 2026) — https://www.icmje.org/recommendations/browse/roles-and-responsibilities/author-responsibilities--conflicts-of-interest.html — full text — "The potential for conflict of interest and bias exists when professional judgment concerning a primary interest (such as patients' welfare or the validity of research) may be influenced by a secondary interest"
- Standing: two or more independent sources (drug and device trials; transfer to a skill author's tests is my inference)
- For the method (my inference): missing — the seven questions act as a risk-of-bias tool, which Lundh shows blind to sponsorship; a field naming who designed, ran and gains from the test is needed.

### F11.9 On the social account, a method is objective as far as criticism can transform it: avenues, shared standards, uptake and equal authority — the method has the first two.

- Answers: 1, 3, 11
- Evidence:
  - SEP, Scientific Objectivity (rev. 2020) — https://plato.stanford.edu/entries/scientific-objectivity/ — secondary: SEP on Longino 1990 — paragraph opening "A classical representative of such efforts" — "objective to the degree that it permits transformative criticism" … "uptake of criticism: criticism must be able to transform scientific practice in the long run; equality of intellectual authority: intellectual authority must be shared equally among qualified practitioners."
  - Same, quoting Popper 1934 — "the objectivity of scientific statements lies in the fact that they can be inter-subjectively tested"
- Standing: one source (secondary, an encyclopedia's account)
- For the method (my inference): missing — nothing says how a reader's objection is taken up or how author and reader disagreeing is settled except by the owner's word, which concentrates authority Longino wants shared.

### F11.10 Evidence-based medicine and the psychology of expertise treat expert judgement as neither opinion nor proof: it decides whether evidence applies, and is reliable only where the environment is regular and feedback exists.

- Answers: 12, 13, 14
- Evidence:
  - Sackett et al., 1996, Evidence based medicine: what it is and what it isn't (BMJ 312:71) — https://www.dcscience.net/sackett-BMJ-1996.pdf — full text — "it is this expertise that decides whether the external evidence applies to the individual patient at all"; expertise includes use of "patients' predicaments, rights, and preferences".
  - Kahneman, Klein, 2009, Conditions for intuitive expertise (American Psychologist 64) — http://bear.warrington.ufl.edu/brenner/mar7588/Papers/kahneman-klein-2009.pdf — full text — "Two conditions must be satisfied for skilled intuition to develop: an environment of sufficiently high validity and adequate opportunity to practice the skill".
- Standing: two or more independent sources (1996 and 2009; not checked against later EBM revisions)
- For the method (my inference): over-strict — "opinion: stays out" files expert judgement with a guess; rule 5 already makes transfer a decision, where Sackett places expertise, and an expert's reliability is testable by the two conditions; users' reports have no field.

### F11.11 Written records lose tacit knowledge and review is mostly understanding, so a reader who "saw nothing of the work" and a successor depend on what the record makes explicit.

- Answers: 1, 4, 16
- Evidence:
  - Collins, 2001, Tacit Knowledge, Trust and the Q of Sapphire (Social Studies of Science 31:71–85) — https://api.crossref.org/works/10.1177/030631201031001004 — abstract — "Shortfalls in tacit knowledge have been partly responsible for this delay." … "the reproduction of scientific findings could be aided by a small addition to the information contained in experimental reports."
  - Bacchelli, Bird, 2013, Expectations, outcomes, and challenges of modern code review (ICSE) — https://www.zora.uzh.ch/server/api/core/bitstreams/9d246a0d-fb01-495a-a493-3e2e78e73aed/content — full text — abstract — "code and change understanding is the key aspect of code reviewing".
- Standing: one source each, on different points; the link is my inference
- For the method (my inference): keeps: rule 4 — its "following the record" assumes a complete record; a rerun by a successor from the record alone would test that, and none is named.

### F11.12 Providers change and retire models within months and say retirement ends comparative studies, so a standing bound to a model version can lose its rerun.

- Answers: 17
- Evidence:
  - Anthropic, Model deprecations (docs, fetched 2026-11-21) — https://docs.anthropic.com/en/docs/about-claude/model-deprecations — full text — "providing at least 60 days' notice before model retirement for publicly released models"; "Researchers lose access to models for ongoing and comparative studies."
  - OpenAI, Deprecations (docs, fetched 2026-11-21) — https://platform.openai.com/docs/deprecations — full text — "Generally available models: At least 6 months." … preview models "may be retired with much shorter notice, such as 2 weeks."
  - Chen et al., 2023, How is ChatGPT's behavior changing over time? — https://arxiv.org/abs/2307.09009 — abstract — "the behavior of the 'same' LLM service can change substantially in a relatively short amount of time"
- Standing: two or more independent sources
- For the method (my inference): missing — rules 4 and 7 should say what a record becomes when its model is retired: no rerun, and a test on the successor is a new test, marked as a transfer.

### F11.13 Model-run research risks a "monoculture of knowers" with an illusion of objectivity.

- Answers: 9, 11
- Evidence:
  - Messeri, Crockett, 2024, Artificial intelligence and illusions of understanding in scientific research (Nature 627) — https://static1.squarespace.com/static/538ca3ade4b090f9ef331978/t/65f071f8fd3e3b478a4f4b86/1710256633821/Messeri&Crockett_2024_Nature.pdf — full text — "scientists falsely believe that AI tools do not have a standpoint or are able to represent all possible standpoints, whereas AI tools actually embed the standpoints of their training data and developers"
- Standing: one source (a Perspective)
- For the method (my inference): missing — rule 4's "another person" is what Popper's intersubjective test needs; the method should say whether a model counts as one.

### F11.14 Content analysis ties the agreement readers must reach to the cost of a wrong conclusion, customarily α ≥ 0.800, and 0.667 for tentative conclusions.

- Answers: 3
- Evidence:
  - Wikipedia, Krippendorff's alpha — https://en.wikipedia.org/wiki/Krippendorff%27s_alpha — secondary: Wikipedia citing Krippendorff 2004, pp. 241–243 — "consider data with 0.800 > α ≥ 0.667 only to draw tentative conclusions, and discard data whose agreement measures α < 0.667."
- Standing: one source (secondary; Krippendorff's own PDFs were blocked to download)
- For the method (my inference): missing — readers who split are noise until their agreement is measured; "contested" should require reader agreement above a threshold set beforehand.

## Open questions

- 4 (cost of being the reader; rubber-stamping) — one code-review search; found Bacchelli and Bird only, no study of reviewer load.
- 15 (who pays for a contributor's test) — not searched within budget.
- 18 (who benefits from the hypothesis-testing framing) — not searched within budget.
- 14, rhetorical half — not searched; F11.10 covers the substance.
- 11 in full — F11.8 and F11.9 give a frame only.
- 5, its premise — whether this repository's reader and author are one model family: S-5 names no model, and I did not open the reader's agent definition (outside my brief).

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| Kim et al., Correlated Errors in LLMs | https://arxiv.org/pdf/2506.07962 | full text | 2025-06-09 (ICML 2025) |
| Goel et al., Great Models Think Alike | https://arxiv.org/abs/2502.04313 | abstract | 2025-02-06 (ICML 2025) |
| Xu et al., When LLMs Benchmark Themselves | https://arxiv.org/abs/2509.26600 | abstract | v1 2025-09-30, latest 2026-08-30 |
| Silencer | https://arxiv.org/abs/2505.20738 | abstract | 2025-05-27 |
| When Consistency Does Not Mean Reliability | https://arxiv.org/abs/2609.13824 | abstract | 2026-09-12 |
| Bavaresco et al., JUDGE-BENCH | https://arxiv.org/abs/2406.18403 | abstract | 2024-06-26 (ACL 2025) |
| Zheng et al., MT-Bench | https://arxiv.org/abs/2306.05685 | abstract | 2023-06-09 |
| Angelopoulos et al., Prediction-Powered Inference | https://arxiv.org/abs/2301.09633 | abstract | 2023-01-23 (Science 2023) |
| Dorner, Nastl, Hardt, Limits to scalable evaluation | https://arxiv.org/abs/2410.13341 | abstract | 2024-10-17 (ICLR 2025) |
| SEP, Experiment in Physics | https://plato.stanford.edu/entries/physics-experiment/ | full text | rev. 2023-06-02 |
| Huang et al., Cannot Self-Correct Reasoning Yet | https://arxiv.org/abs/2310.01798 | abstract | 2023-10-03 |
| Stechly et al., Self-Verification Limitations | https://arxiv.org/abs/2402.08115 | abstract | 2024-02-12 |
| Panickssery et al., LLM Evaluators Favor Their Own | https://arxiv.org/abs/2404.13076 | abstract | 2024-04-15 (NeurIPS 2024) |
| Chen et al., Do LLM Evaluators Prefer Themselves | https://arxiv.org/abs/2504.03846 | abstract | 2025-04-04 |
| IESBA Handbook 2018 | https://www.icam.mw/wp-content/uploads/2019/01/IESBA-Handbook-Code-of-Ethics-2018.pdf | full text | 2018 edition |
| Lundh et al., Industry sponsorship (Cochrane) | https://findresearcher.sdu.dk/ws/files/145419585/Industry_sponsorship_and_research_outcome.pdf | full text | 2017, Issue 2 |
| ICMJE, Conflicts of Interest | https://www.icmje.org/recommendations/browse/roles-and-responsibilities/author-responsibilities--conflicts-of-interest.html | full text | page © 2026 |
| SEP, Scientific Objectivity | https://plato.stanford.edu/entries/scientific-objectivity/ | full text | rev. 2020-10-30 |
| Sackett et al., EBM: what it is and what it isn't | https://www.dcscience.net/sackett-BMJ-1996.pdf | full text | 1996-01-13 |
| Kahneman, Klein, Conditions for intuitive expertise | http://bear.warrington.ufl.edu/brenner/mar7588/Papers/kahneman-klein-2009.pdf | full text | 2009 |
| Collins, Q of Sapphire (Crossref record) | https://api.crossref.org/works/10.1177/030631201031001004 | abstract | 2001 |
| Bacchelli, Bird, Modern code review | https://www.zora.uzh.ch/server/api/core/bitstreams/9d246a0d-fb01-495a-a493-3e2e78e73aed/content | full text | 2013 (ICSE) |
| Anthropic, Model deprecations | https://docs.anthropic.com/en/docs/about-claude/model-deprecations | full text | fetched 2026-11-21 |
| OpenAI, Deprecations | https://platform.openai.com/docs/deprecations | full text | fetched 2026-11-21 |
| Chen, Zaharia, Zou, ChatGPT behaviour over time | https://arxiv.org/abs/2307.09009 | abstract | 2023-07-18 |
| Messeri, Crockett, Illusions of understanding | https://static1.squarespace.com/static/538ca3ade4b090f9ef331978/t/65f071f8fd3e3b478a4f4b86/1710256633821/Messeri&Crockett_2024_Nature.pdf | full text | 2024-03-06 |
| Wikipedia, Krippendorff's alpha | https://en.wikipedia.org/wiki/Krippendorff%27s_alpha | secondary: Wikipedia | fetched 2026-11-21 |

<!-- COMPLETE -->
