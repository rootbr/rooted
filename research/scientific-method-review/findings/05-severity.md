# Cluster 5 — Severity, measurement and statistical inference

## Findings

### F5.1 No check question asks whether the measure responds to what the claim is about, and 2025–2026 work shows a reliable measure that tracks something else.

- Answers: 6; frontier 6
- Evidence:
  - Chen, Chen, Lin, Vong, 2026, A Judge Should Know What Changed: Construct Validity for LLM-as-a-Judge Evaluation — https://arxiv.org/pdf/2608.24419 — full text — abstract — "At matched invariance S ≥ 0.90 judges sit at S = 0.945 against R = 0.319"; "a frozen family reading only surface form, given the same paired input the judge gets, reproduces 55%–67% of their labels"; "High judge agreement is therefore not evidence of valid evaluation."
  - Bean et al., 2025, Measuring what Matters: Construct Validity in Large Language Model Benchmarks (NeurIPS 2025 D&B) — https://arxiv.org/pdf/2511.04703 — full text — §2 Background — "Construct validity evaluates whether an empirical test measures the phenomenon it intends to measure"; §4 — "53.4% of articles presented evidence for the construct validity of their benchmark".
  - Ariño de la Rubia, Pafka, 2026, Identical Runs, Different Results — https://arxiv.org/pdf/2609.33812 — full text — abstract — "Fewer than one run in twenty broke the task's data rules, but those runs held the highest scores."
- Standing: two or more independent sources
- For the method (my inference): missing — a test against the wrong quantity answers the check questions of rules 2 and 3 well; a check question of its own (does the measure move when the construct changes and stay when it is preserved?), with a known-direction probe and a surface-only baseline, would catch what Chen et al. report.

### F5.2 The link from a proxy measure to the outcome its goal names is a claim of its own, tested separately in medicine and online experiments; the record has no place for it.

- Answers: 7, 5
- Evidence:
  - Fleming, 2005, Surrogate Endpoints And FDA's Accelerated Approval Process, Health Affairs 24(1) — https://courses.washington.edu/pharm309/FlemingArticle.pdf — full text — section "'A Correlate Does Not A Surrogate Make'" — "However, “validated surrogates” are required if one wants to use replacement endpoints in trials designed to reliably provide accurate estimates of the level of tangible benefit to patients."
  - Kohavi, Longbotham, 2023, Online Controlled Experiments and A/B Tests (Encyclopedia of ML and Data Science) — https://exp-platform.com/Documents/2023-03-11EncyclopeiaMLDSABTestingFinal.pdf — full text — paragraph "An OEC has to be defined" — "The hard part is finding metrics that are measurable in the short-term that are predictive of long-term goals."
  - Mayo, 2018, Statistical Inference as Severe Testing, §1.1 excerpt — https://assets.cambridge.org/97811076/64647/excerpt/9781107664647_excerpt.pdf — full text of excerpt — slogan list — "Statistical significance is not substantive significance."
- Standing: two or more independent sources
- For the method (my inference): missing — record H-03 in `references/record-format.md` measures "share of runs in which the agent reads the file before its first edit", not fewer bad edits; a field naming the goal's outcome and the test or decision linking the measure to it would expose the gap between the statistical and the substantive hypothesis.

### F5.3 Rule 3's check question takes Mayo's counterfactual sense of severity, while its body fixes only pre-test design; Mayo separates the pre-data property (power) from severity judged on the data obtained.

- Answers: 4
- Evidence:
  - Mayo, 2006, Critical Rationalism and Its Failure to Withstand Critical Scrutiny (Springer chapter) — https://errorstatistics.com/wp-content/uploads/2020/10/mayo2006_chapter_criticalrationalismanditsfailu.pdf — full text — (7.2) — "(ii) test T would (with very high probability) have produced a result that fits H less well than x does, if H were false or incorrect."
  - Mayo, 2018, §1.1 excerpt (as above) — "The term “severity” is Popper’s, though he never adequately defined it."; "pre-data, we devise methods that make it hard for claims to pass muster unless they are approximately true or adequately solve our problem. With data in hand, post-data, we scrutinize what, if anything, can be inferred."
- Standing: one source (two texts of one author)
- For the method (my inference): keeps: rule 3 — the check question states S-2, but the record holds only the design (comparison, runs), not how probable the observed agreement was had the claim been false; F5.4 and F5.5 show it is large for the method's own examples.

### F5.4 Rule 3's own good example, nine of ten against four of ten, misses the conventional two-sided level, and the method names no test or error rate that would show it.

- Answers: 1, 15
- Evidence:
  - my computation, `scratch-05/rule3_stats.py` — Fisher exact test on 9/10 vs 4/10: one-sided p = 0.0286, two-sided p = 0.0573; power of a one-sided test at 0.05 with ten runs per arm against true rates 0.9 and 0.4 = 0.659.
  - Miller, 2024, Adding Error Bars to Evals — https://arxiv.org/pdf/2411.00640 — full text — §1 recommendations — "Using power analysis to determine whether an eval (or a random subsample) is capable of testing a hypothesis of interest".
  - JCGM 100:2008 (GUM) — https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf — full text — 0.1 — "it is obligatory that some quantitative indication of the quality of the result be given so that those who use it can assess its reliability."
- Standing: two or more independent sources for the requirement; the p-values are my computation
- For the method (my inference): wrong — the example presented as good fails a two-sided test at 0.05; every `result` should carry its test, error rate and interval, as the GUM requires an uncertainty for a measured value.

### F5.5 A threshold on the observed difference is not a refuting outcome with controlled error: the H-03 record's "under ten points above" with ten runs per arm lets a technique with no effect pass about two times in five.

- Answers: 8, 9, 1
- Evidence:
  - my computation, `scratch-05/rule3_stats.py` — with equal true shares 0.5 (0.8) in both arms and ten runs each, P(the with-arm share is at least ten points above) = 0.412 (0.388).
  - Lakens, McLatchie, Isager, Scheel, Dienes, 2018, Improving Inferences about Null Effects with Bayes Factors and Equivalence Tests (accepted manuscript) — https://eprints.lancs.ac.uk/id/eprint/125346/1/2018.05.18_Lakens_McLatchie_Isager_Scheel_Dienes_Improving_Inferences_About_Null_Effects_With_Bayes_Factors_And_Equivalence_Tests_R1.pdf — full text — section on equivalence tests — "To perform an equivalence test, researchers first have to determine a 'smallest effect size of interest', the smallest effect they deem meaningful.".
  - ASA, 2016, Statement on Statistical Significance and P-Values (press release) — https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf — full text — principle 5 — "A p-value, or statistical significance, does not measure the size of an effect or the importance of a result."
- Standing: two or more independent sources
- For the method (my inference): wrong — `threshold` already holds the smallest effect worth acting on (the auditor's materiality), but the refuter must be a test against it with stated error rates both ways (a one-sided test for support, an equivalence test for refutation), or a small test passes null effects and fails real ones.

### F5.6 Requiring a falsifying threshold where no theory supplies one yields arbitrary values unless the inputs of a test — concepts, valid measures, relations, boundary conditions, auxiliaries — come first.

- Answers: 10
- Evidence:
  - Scheel, Tiokhin, Isager, Lakens, 2021, Why Hypothesis Testers Should Spend Less Time Testing Hypotheses, Perspectives on Psychological Science 16(4) — https://pure.tue.nl/ws/files/175344254/1745691620966795.pdf — full text — paragraph opening "First, even preregistered hypothesis tests" — "forcing researchers to specify what would falsify their hypotheses when they have no theoretical basis for doing so can lead to testing against arbitrary values (Kruschke, 2018) and runs the risk of replacing one mindless ritual with another."; section "The Inputs to Informative Hypothesis Tests" — "(a) concept formation, (b) developing measures, (c) establishing relationships between concepts, (d) specifying boundary conditions and auxiliary assumptions, and (e) deriving statistical predictions".
- Standing: one source
- For the method (my inference): missing — the acceptance path asks only whether a refuting outcome is named; a threshold with no basis should be marked as the owner's decision on cost (rule 3 already sets repetitions "by the cost of an error"), and a valid measure (F5.1) should be an input before a claim becomes a hypothesis.

### F5.7 The method records every run of one claim but does not count the variants tried or control the false "supported" standings expected across many claims scored on the same runs.

- Answers: 19, 20
- Evidence:
  - Wasserstein, Lazar, 2016, The ASA's Statement on p-Values: Context, Process, and Purpose (accepted manuscript) — https://sciences.ucf.edu/biology/d4lab/wp-content/uploads/sites/23/2017/03/WassersteinLazar2016.pdf — full text — principle 4 — "Researchers should disclose the number of hypotheses explored during the study, all data collection decisions, all statistical analyses conducted and all p-values computed."
  - Bailey, Borwein, López de Prado, Zhu, 2015, The Probability of Backtest Overfitting (revised version) — https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf — full text — §1 — "Backtests published in academic or practitioners’ publications almost never declare the number of trials involved in a discovery."
  - Patra, Jha, 2026, Claims, Designs, and Guarantees (arXiv 2603.22594v3) — https://arxiv.org/pdf/2603.22594 — full text — list of guarantees — "Multiple-testing control: the false discovery rate (the expected share of false positives among reported findings) or the family-wise error rate (the chance of any false positive) stays below a set level."
- Standing: two or more independent sources
- For the method (my inference): missing — rule 6 should record the variants tried before the tested one and the family of hypotheses scored on one run set, and state which error rate (per claim, family-wise or false discovery) the standings control.

### F5.8 Recording the threshold before the test does not fix when it stops; repeated looks inflate false positives, which anytime-valid designs, used in 2025 for agentic falsification, control.

- Answers: 21
- Evidence:
  - Patra, Jha, 2026 (as above) — abstract — "with 100 interim looks, repeatedly applying an unadjusted p < 0.05 rule produced false positives in 37.6% of studies, whereas the particular anytime-valid e-value procedure we used produced 2.2%".
  - Huang, Jin, Li, Li, Candès, Leskovec, 2025, Automated Hypothesis Validation with Agentic Sequential Falsifications (arXiv 2502.09858v1) — https://arxiv.org/pdf/2502.09858 — full text — abstract — "A novel sequential testing framework ensures strict Type-I error control while actively gathering evidence from diverse observations".
- Standing: one source for the inflation figure; two for anytime-valid control
- For the method (my inference): missing — rule 6 should require the stopping rule (fixed `runs` or a named sequential procedure) recorded with the threshold, and rule 3 may admit anytime-valid designs as severe.

### F5.9 Gains over weak baselines often vanish over strong ones, and when the technique changes the course of the work, the comparison that keeps randomisation is by assigned arm, not by path taken.

- Answers: 2, 3
- Evidence:
  - Lin, 2019, The Neural Hype and Comparisons Against Weak Baselines, SIGIR Forum — https://sigir.org/wp-content/uploads/2019/01/p040.pdf — full text — section on additivity — "Techniques that yield improvements over weak baselines often do not show similar improvements over strong baselines."; quoting Armstrong et al. 2009 (secondary: Lin) — "selection of weak baselines that can create an illusion of incremental improvement".
  - CONSORT 2025 explanation and elaboration, BMJ 2025;389:e081124 — https://eprints.gla.ac.uk/350055/1/350055.pdf — full text — item on analysis populations — "all randomised participants are included in the analysis and retained in the group to which they were allocated. Meeting these two conditions defines an intention-to-treat analysis".
- Standing: one source on baselines (with a secondary report of a second); one norm on assignment
- For the method (my inference): missing — the comparison should be the alternative a practitioner would otherwise use, chosen before the test, with every run compared by its assigned arm whatever files the agent then opened.

### F5.10 Trial reporting and 2026 agent evaluation measure adherence apart from effect; the method does not, so a rule ignored looks like a rule that failed when obeyed.

- Answers: 12
- Evidence:
  - CONSORT 2025 E&E (as above) — item on interventions — "fidelity209 (ie, the extent to which the intervention/comparator were implemented as planned in the protocol by care providers) or adherence209 (ie, the extent to which trial participants implement the intervention/comparator as planned in the protocol)".
  - Ariño de la Rubia, Pafka, 2026 (as above) — abstract — "Agents and models should be evaluated as pairings, over repeated attempts, with compliance reported beside quality."
- Standing: two or more independent sources
- For the method (my inference): missing — a record of a claim about an instruction should carry the share of runs that followed it beside the effect, and a refutation should say which of the two failed.

### F5.11 Run-to-run variance, clustered items and segment effects can exceed the differences tested; an A/A run checks that the harness reports chance at its stated rate.

- Answers: 11, 13
- Evidence:
  - Ariño de la Rubia, Pafka, 2026 (as above) — §1 result 1 — "Three-run comparisons put the weaker pairing ahead 28 to 44 percent of the time, and for the agent differences observed here the usual approximation calls for roughly 39 to 113 runs per arm."
  - Miller, 2024 (as above) — §2.2, Table 4 caption — "Analyzing the same data, clustered standard errors can be over 3X larger than naive standard errors."
  - Kohavi, Longbotham, 2023 (as above) — "To validate an experimentation system, we recommend that A/A tests be run regularly"; "(the Null hypothesis should be rejected about 5% of the time when a 95% confidence level is used)"; "The treatment effect may not be uniform and there may be segments that are impacted differently."
- Standing: two or more independent sources
- For the method (my inference): missing — rule 3 should ask for an A/A run of a new harness before its first comparison, and for results by task segment where the scope spans several.

### F5.12 A comparison with one arm without the technique leaves the diagnosticity of evidence among rival explanations unmeasured.

- Answers: 14
- Evidence:
  - Heuer, 1999, Psychology of Intelligence Analysis (CIA Center for the Study of Intelligence) — https://www.cia.gov/resources/csi/static/Pyschology-of-Intelligence-Analysis.pdf — full text — ch. 4, "Failure To Consider Diagnosticity of Evidence" — "In the absence of a complete set of alternative hypotheses, it is not possible to evaluate the “diagnosticity” of evidence."
- Standing: one source
- For the method (my inference): needs another procedure for debugging and appraisal — a diagnosis of one failure is a choice among rival causes, where a competing-hypotheses matrix, not a two-arm comparison, judges the evidence.

## Open questions

- Q16–18, whether the intervention ranking undervalues mechanism, process tracing or qualitative evidence — Cartwright 2007 was not opened (Springer and PhilPapers refused, the Durham copy sits behind a challenge page); SEP "Philosophy of Medicine" says only "there is no universally accepted hierarchy" and that case series have "potential usefulness", which does not settle it.
- Q13, mutation testing as a model for planting false claims — Jia and Harman 2011 found, not opened; the A/A test (F5.11) and Chen et al.'s known-direction interventions (F5.1) are the nearest opened analogues.
- Q1, the practitioners' "100–200 labelled examples per failure mode" — not searched within budget.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| Chen et al., A Judge Should Know What Changed | https://arxiv.org/pdf/2608.24419 | full text | arXiv v1, 25 Aug 2026 |
| Bean et al., Measuring what Matters | https://arxiv.org/pdf/2511.04703 | full text | arXiv v1, 3 Nov 2025 (NeurIPS 2025) |
| Ariño de la Rubia, Pafka, Identical Runs, Different Results | https://arxiv.org/pdf/2609.33812 | full text | arXiv v1, 27 Sep 2026 |
| Mayo, Statistical Inference as Severe Testing, excerpt | https://assets.cambridge.org/97811076/64647/excerpt/9781107664647_excerpt.pdf | full text of excerpt | CUP 2018 |
| Mayo, Critical Rationalism and Its Failure to Withstand Critical Scrutiny | https://errorstatistics.com/wp-content/uploads/2020/10/mayo2006_chapter_criticalrationalismanditsfailu.pdf | full text | Springer 2006 |
| Fleming, Surrogate Endpoints And FDA's Accelerated Approval Process | https://courses.washington.edu/pharm309/FlemingArticle.pdf | full text | Health Affairs 2005 |
| Kohavi, Longbotham, Online Controlled Experiments and A/B Tests | https://exp-platform.com/Documents/2023-03-11EncyclopeiaMLDSABTestingFinal.pdf | full text | 2023 version |
| Miller, Adding Error Bars to Evals | https://arxiv.org/pdf/2411.00640 | full text | arXiv 2024 |
| JCGM 100:2008 (GUM) | https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf | full text | first edition Sep 2008 |
| Lakens et al., Improving Inferences about Null Effects | https://eprints.lancs.ac.uk/id/eprint/125346/1/2018.05.18_Lakens_McLatchie_Isager_Scheel_Dienes_Improving_Inferences_About_Null_Effects_With_Bayes_Factors_And_Equivalence_Tests_R1.pdf | full text | accepted manuscript 2018 |
| ASA, Statement on p-values (press release) | https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf | full text | 7 Mar 2016 |
| Wasserstein, Lazar, The ASA's Statement on p-Values | https://sciences.ucf.edu/biology/d4lab/wp-content/uploads/sites/23/2017/03/WassersteinLazar2016.pdf | full text | accepted manuscript 2016 |
| Scheel et al., Why Hypothesis Testers Should Spend Less Time Testing Hypotheses | https://pure.tue.nl/ws/files/175344254/1745691620966795.pdf | full text | PPS 16(4), 2021 |
| Bailey et al., The Probability of Backtest Overfitting | https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf | full text | revised Feb 2015 |
| Patra, Jha, Claims, Designs, and Guarantees | https://arxiv.org/pdf/2603.22594 | full text | arXiv v3, 11 Oct 2026 |
| Huang et al., Agentic Sequential Falsifications | https://arxiv.org/pdf/2502.09858 | full text | arXiv v1, 14 Feb 2025 |
| Lin, The Neural Hype and Comparisons Against Weak Baselines | https://sigir.org/wp-content/uploads/2019/01/p040.pdf | full text | SIGIR Forum 2019 |
| CONSORT 2025 explanation and elaboration | https://eprints.gla.ac.uk/350055/1/350055.pdf | full text | BMJ 2025;389:e081124 |
| Heuer, Psychology of Intelligence Analysis | https://www.cia.gov/resources/csi/static/Pyschology-of-Intelligence-Analysis.pdf | full text | CSI 1999 |
| SEP, Philosophy of Medicine | https://plato.stanford.edu/entries/medicine/ | full text | first published 6 Jun 2016 |

<!-- COMPLETE -->
