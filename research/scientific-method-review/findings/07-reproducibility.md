# Cluster 7 — Reproducibility and someone else's evidence

## Findings

### F7.1 Reading summary results misses most fabricated data; individual data or a trustworthiness check catches it, risk-of-bias appraisal does not

- Answers: 2, 4; frontier 8
- Evidence:
  - Carlisle, 2021, False individual patient data and zombie randomised controlled trials submitted to Anaesthesia — https://doi.org/10.1111/anae.15263 — abstract (Europe PMC) — abstract — "67/153 (44%) false vs. 6/373 (2%) false"
  - Wilkinson et al., 2024, Stage 2 of the INSPECT-SR project — https://doi.org/10.1101/2024.11.25.24316905 — abstract (Europe PMC) — Results and Conclusions — "No relationship was identified between trustworthiness assessment and Risk of Bias or GRADE"; "problematic studies do not appear to be flagged by Risk of Bias assessment"
  - Cochrane news, 2026-09-24, New tool helps researchers spot problematic trials — https://www.cochrane.org/about-us/news/new-tool-helps-researchers-spot-problematic-trials-they-distort-evidence — full text — "21 structured checks across four domains"
  - Richardson et al., 2025, The entities enabling scientific fraud at scale — https://doi.org/10.1073/pnas.2420092122 — full text (Europe PMC XML) — paragraph opening "To provide perspective" — "suspected paper mill products have been doubling every 1.5 y"
- Standing: two or more independent sources
- For the method (my inference): missing — rule 4 admits a test once "the comparison, the measure, the sample and the result are in view", which a fabricated trial also shows; method.md needs an authenticity step for an external test (post-publication notices, data access, INSPECT-SR checks where they apply) before it moves past hypothesis.

### F7.2 Published tests that would pass rule 4's visibility check replicate at about one half

- Answers: 2, 9; frontier 8
- Evidence:
  - Open Science Collaboration, 2015, Estimating the reproducibility of psychological science — https://doi.org/10.1126/science.aac4716 — abstract (Europe PMC) — abstract — "Ninety-seven percent of original studies had statistically significant results. Thirty-six percent of replications had statistically significant results"
  - Camerer et al., 2018, Evaluating the replicability of social science experiments — https://doi.org/10.1038/s41562-018-0399-z — full text (EUR repository PDF) — Fig. 4 caption — "This is similar to the actual replication rate of 61.9%"
  - Tyner et al., 2026, Investigating the replicability of the social and behavioural sciences, Nature 652:143–150 — https://www.nature.com/articles/s41586-025-10078-y — abstract — abstract — "151 of 274 claims (55.1% (95% confidence interval (CI) 49.2–60.9%))"; "an 82.4% (95% CI 67.8–88.2%) reduction in shared variance"
- Standing: two or more independent sources
- For the method (my inference): wrong at these base rates — rule 4 lets one opened, unreplicated external test give the standing `supported`; method.md could mark such a claim as resting on one unreplicated external test, as `law` already requires independent tests.

### F7.3 Opening a paper is not empty: readers forecast replication, and reported statistics can be recomputed

- Answers: 2, 5; frontier 8
- Evidence:
  - Camerer et al., 2018 — URL as above — full text — Fig. 4 caption — "The mean prediction market belief of replication is 63.4%"; "Spearman correlation coefficient: 0.842"
  - Center for Open Science, 2026, Large-scale collaboration releases new findings on research credibility — https://www.cos.io/about/news/large-scale-collaboration-releases-new-findings-on-research-credibility — secondary: COS summary of Mody et al. and Rajtmajer et al. — "human assessments are reasonably accurate at predicting replication outcomes (76% and 78% success rates by best performing metric"; "None of the three methods were consistently effective"
  - Nuijten et al., 2016, The prevalence of statistical reporting errors in psychology (1985–2013) — https://doi.org/10.3758/s13428-015-0664-2 — abstract — abstract — "half of all published psychology papers that use NHST contained at least one p-value that was inconsistent"; "One in eight papers contained a grossly inconsistent p-value"
- Standing: two or more independent sources
- For the method (my inference): missing — opening gives a forecast and an internal-consistency check, not a reproduction; method.md could name what reading checks (statistics recomputed from reported numbers) apart from what only data or a rerun checks.

### F7.4 For much of the literature the test is not fully in view

- Answers: 1, 12, 13
- Evidence:
  - Errington et al., 2021, Challenges for assessing replicability in preclinical cancer biology — https://doi.org/10.7554/eLife.67995 — abstract (Europe PMC) — abstract — "the data needed to compute effect sizes and conduct power analyses was publicly accessible for just 4 of 193 experiments"; "none of the 193 experiments were described in sufficient detail in the original paper"
  - Center for Open Science, 2026 — URL as above — secondary: summary of Miske et al. in Nature — "Data was available for only 24% of a sample of 600 assessed papers."
  - Hoyle et al., 2026, Read the Paper, Write the Code (arXiv 2604.21965v2) — https://arxiv.org/abs/2604.21965 — full text — abstract — "failures stem both from agent errors and from underspecification in the papers themselves"
  - Siddiq et al., 2025, LLMs for Software Engineering: A Reproducibility Crisis — https://arxiv.org/abs/2512.00651 — full text — results on smell prevalence — "only 13.3% of papers did not have any reproducibility smells"
- Standing: two or more independent sources
- For the method (my inference): missing — rule 4 has no outcome for a source opened with part of the test out of view; the record needs a field for what was not in view (data, code, prompts, model version) and a rule for the standing it allows; if the sample must be in view as data, about a quarter of SCORE's sample would qualify.

### F7.5 Who ran a test predicts its result beyond what the visible design shows

- Answers: 3, 4
- Evidence:
  - Lundh et al., 2017, Industry sponsorship and research outcome — https://doi.org/10.1002/14651858.MR000033.pub3 — abstract (Europe PMC) — Main results and Authors' conclusions — "Industry sponsored studies more often had favorable efficacy results, RR: 1.27 (95% CI: 1.17 to 1.37)"; "an industry bias that cannot be explained by standard 'Risk of bias' assessments"
  - Makel, Plucker & Hegarty, 2012, Replications in Psychology Research: How Often Do They Really Occur? — https://doi.org/10.1177/1745691612460688 — abstract (Europe PMC) — abstract — "replications were significantly less likely to be successful when there was no overlap in authorship between the original and replicating articles"
- Standing: two or more independent sources
- For the method (my inference): missing — "The support comes from the test itself, whoever its author" treats the author as uninformative, while sponsorship and self-replication predict results; the record could carry the tester's independence from the claim's author and their interest, which bears on the repository's own tests above all.

### F7.6 Appraisal tools rate a body of evidence on domains rule 4 does not name, and miss fabrication

- Answers: 6
- Evidence:
  - Balshem et al., 2011, GRADE guidelines: 3. Rating the quality of evidence — https://doi.org/10.1016/j.jclinepi.2010.07.015 — abstract (Europe PMC) — abstract — "applied to a body of evidence, not to individual studies"; "more than risk of bias and so may also be compromised by imprecision, inconsistency, indirectness of study results, and publication bias"
  - Wilkinson et al., 2024 — as in F7.1 — "No relationship was identified between trustworthiness assessment and Risk of Bias or GRADE"
- Standing: the domains, one source; the miss of fabrication, two
- For the method (my inference): needs another procedure for appraisal of research — inconsistency and publication bias exist only across tests, so appraisal needs a body-level step and a trustworthiness step (F7.1); for agent tests, "Randomized trials begin as high-quality evidence" would mislead, since a randomised prompt comparison on one model version is indirect for every other version.

### F7.7 Reading the right number is not reading it as the source meant

- Answers: 5
- Evidence:
  - Gigerenzer et al., 2007, Helping Doctors and Patients Make Sense of Health Statistics — https://www.stat.berkeley.edu/~aldous/157/Papers/health_stats.pdf — full text — section on relative risks in journals — "Sixty-eight percent of 222 articles failed to report the absolute risks for the first ratio measure (such as relative risks) in the abstract"
  - Boutron & Ravaud, 2018, Misrepresentation and distortion of research in biomedical literature — https://doi.org/10.1073/pnas.1710755115 — abstract (Europe PMC) — abstract — spin is "reporting that fails to faithfully reflect the nature and range of findings and that could affect the impression the results produce in readers"
- Standing: two or more independent sources
- For the method (my inference): missing — rule 4 asks whether another person would "see the same", not whether the measure, subgroup and adjustment were read as the source defined them; the record could require the effect with its interval, reference class and analysis population.

### F7.8 A court screening expert evidence asks for a known error rate and bars extrapolation

- Answers: 7
- Evidence:
  - Federal Rules of Evidence, Rule 702 with Advisory Committee Notes — https://www.law.cornell.edu/rules/fre/rule_702 — full text — 2000 note — "the known or potential rate of error of the technique or theory when applied"; "Whether the expert has unjustifiably extrapolated from an accepted premise to an unfounded conclusion"; 2023 note — "each expert opinion must stay within the bounds of what can be concluded from a reliable application of the expert's basis and methodology"
- Standing: one source (a norm; Daubert itself not opened)
- For the method (my inference): missing for rule 4, kept by rule 5 — rule 5 matches the bar on extrapolation, but nothing asks for the measure's error rate; for agent tests, often a model grader's agreement with human labels.

### F7.9 A benchmark result is not in view until its measure's validation and implementation are

- Answers: 8, 13
- Evidence:
  - Perlitz et al., 2024, Do These LLM Benchmarks Agree? (arXiv 2407.13696v2) — https://arxiv.org/abs/2407.13696 — full text — Introduction — "despite the wide application of BAT in recent years, there is a glaring absence of common methodology"; abstract — "there are no standardized procedures for such agreement testing"
  - Biderman et al., 2024, Lessons from the Trenches on Reproducible Evaluation of Language Models — https://arxiv.org/abs/2405.14782 — full text — §3.1 — "the precise string used for a given prompt, even down to whitespace usage, can significantly impact performance"; on closed APIs, evaluators must "simply trust the developer's self-reported numbers"
- Standing: two or more independent sources
- For the method (my inference): missing — an accepted benchmark test should name what its measure was validated against, by which procedure, and the exact prompt, harness and model version; contrary to question 8's premise, Perlitz et al. find agreement checks common but unstandardised.

### F7.10 A rerun that reproduces a result does not show the claim is true

- Answers: 11, 12
- Evidence:
  - Devezer et al., 2019, Scientific discovery in a model-centric framework — https://doi.org/10.1371/journal.pone.0216125 — full text — abstract — "the scientific process may not converge to truth even if scientific results are reproducible and that irreproducible results do not necessarily imply untrue results"; Discussion — "Reproducible false results may also arise due to bias in methods and instruments used"
  - Center for Open Science, 2026 — as in F7.3 — secondary: Abatayo et al. — "measures of repeatability and credibility are only weakly related with one another"
- Standing: two or more independent sources
- For the method (my inference): wrong — "a rerun confirms a test of our own" confirms the run, not the claim; "runs by a command" buys computational reproducibility (rare, per F7.4) and excludes untracked manual judgement, but a biased instrument reruns just as well.

### F7.11 The method names no kind of replication, and direct replications are rare

- Answers: 9
- Evidence:
  - Fidler & Wilcox, SEP, Reproducibility of Scientific Results (first published 2018-12-03) — https://plato.stanford.edu/entries/scientific-reproducibility/ — full text — §1.1 — "for Schmidt, direct replications control for sampling error, artifacts, and fraud"; "Conceptual replications help corroborate the underlying theory"
  - Laws, 2016, Psychology, replication & beyond — https://doi.org/10.1186/s40359-016-0135-2 — full text (Europe PMC XML) — paragraph opening "How often do direct and conceptual replications occur" — "They calculated an overall replication rate of 1.07 % and Makel et al. [ 40 ] found that only 18 % of those were direct rather than conceptual replications"
- Standing: two or more independent sources (18% of 1.07% is about 0.2%: my arithmetic)
- For the method (my inference): missing — `law` ("independent tests under varied conditions") points to conceptual replication, refutation "under the same conditions" to direct; method.md could say a direct repetition checks the test and a conceptual one the bounds.

### F7.12 A publication-bias correction cannot be a condition of accepting an opened test

- Answers: 10
- Evidence:
  - Kvarven, Strømland & Johannesson, 2020, Comparing meta-analyses and preregistered multiple-laboratory replication projects — https://doi.org/10.1038/s41562-019-0787-z — abstract (Europe PMC) — abstract — "meta-analytic effect sizes are almost three times as large as replication effect sizes"; "these methods do not substantively improve the meta-analytic results"
  - Good Science Project, 2026-09-24, Mandatory Reporting of Null Results — https://newsletter.goodscienceproject.org/p/mandatory-reporting-of-null-results — full text — opening — "The NIH and the White House have both signaled interest in a policy requiring biomedical researchers to report null results"
- Standing: one source
- For the method (my inference): keeps: rule 6 — the working defence sits before the result (registration, every run recorded), not in a later correction; nothing need wait on a mandate only signalled as of September 2026.

### F7.13 In 2026 a plausible paper costs a model little, so a visible design no longer filters

- Answers: 2, 3; frontier 8
- Evidence:
  - Lu et al., 2026, Towards end-to-end automation of AI research, Nature (published 2026-03-25) — https://www.nature.com/articles/s41586-026-10265-5 — abstract — abstract — "the manuscript generated by this AI system passed the first round of peer review for a workshop of a top-tier machine learning conference. The workshop had an acceptance rate of 70%"
  - Ma et al., 2026, Epistemic Infrastructures of Science in AI Era (arXiv 2605.10425) — https://arxiv.org/abs/2605.10425 — abstract — abstract — "generation cost itself served as a rough filter; AI weakens that filter without comparably lowering verification cost"
- Standing: two or more independent sources
- For the method (my inference): missing — with F7.1, "opened" needs backing a generator cannot cheaply produce: data, code, a prior registration, or an independent repetition.

## Open questions

- What share of OSC 2015 and Many Labs originals would have passed rule 4 — tried the OSC abstract and the SEP entry; no source codes the originals for it; I infer nearly all, unmeasured.
- Direct replications as "about 0.2%" — the 18% share is from a secondary review (Laws 2016); Makel et al.'s results section is paywalled, not opened; the base is the 100 highest-impact psychology journals.
- How historical source criticism maps onto rule 4 — no text of historical method opened; F7.1 and F7.5 give the empirical side.
- A shared registry for prompt-technique tests — searches found proposals only (lm-eval task sharing, Biderman et al.; a Reproducibility Maturity Model, arXiv 2512.00651; "blueprints", arXiv 2605.10425).
- What standing a paywalled source takes — no source treats paywalls apart from data access (F7.4).
- Whether NIH or OSTP finalised a null-results mandate after September 2026 — only the "signaled interest" report found.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| Fidler & Wilcox, SEP Reproducibility of Scientific Results | https://plato.stanford.edu/entries/scientific-reproducibility/ | full text | first published 2018-12-03 |
| Devezer et al., PLOS ONE | https://doi.org/10.1371/journal.pone.0216125 | full text | 2019-05-15 |
| Perlitz et al., BenchBench | https://arxiv.org/abs/2407.13696 | full text | v2, 2024-09-12 |
| Biderman et al., Lessons from the Trenches | https://arxiv.org/abs/2405.14782 | full text | 2024 |
| Ioannidis, PLOS Medicine | https://doi.org/10.1371/journal.pmed.0020124 | full text | 2005 |
| Federal Rules of Evidence 702 with notes | https://www.law.cornell.edu/rules/fre/rule_702 | full text | as amended 2023 |
| Gelman & Loken, The garden of forking paths | http://www.stat.columbia.edu/~gelman/research/unpublished/p_hacking.pdf | full text (read; no finding rests on it) | 2013 |
| Camerer et al., Nature Human Behaviour | https://doi.org/10.1038/s41562-018-0399-z | full text | 2018-08-27 |
| Carlisle, Anaesthesia | https://doi.org/10.1111/anae.15263 | abstract | 2021 |
| Errington et al., eLife | https://doi.org/10.7554/eLife.67995 | abstract | 2021 |
| Makel, Plucker & Hegarty | https://doi.org/10.1177/1745691612460688 | abstract | 2012 |
| Open Science Collaboration, Science | https://doi.org/10.1126/science.aac4716 | abstract | 2015 |
| Tyner et al. (SCORE), Nature 652 | https://www.nature.com/articles/s41586-025-10078-y | abstract | 2026-04-01 |
| Center for Open Science, SCORE news | https://www.cos.io/about/news/large-scale-collaboration-releases-new-findings-on-research-credibility | full text | 2026 |
| Hoyle et al., Agentic Reproduction | https://arxiv.org/abs/2604.21965 | full text | v2, 2026-09-29 |
| Cochrane news on INSPECT-SR | https://www.cochrane.org/about-us/news/new-tool-helps-researchers-spot-problematic-trials-they-distort-evidence | full text | 2026-09-24 |
| Wilkinson et al., INSPECT-SR Stage 2 | https://doi.org/10.1101/2024.11.25.24316905 | abstract | 2024 preprint |
| Good Science Project, null results | https://newsletter.goodscienceproject.org/p/mandatory-reporting-of-null-results | full text | 2026-09-24 |
| Richardson et al., PNAS | https://doi.org/10.1073/pnas.2420092122 | full text | 2025 |
| Boutron & Ravaud, PNAS | https://doi.org/10.1073/pnas.1710755115 | abstract | 2018 |
| Lu et al., Nature (AI Scientist) | https://www.nature.com/articles/s41586-026-10265-5 | abstract | 2026-03-25 |
| Epistemic Infrastructures position paper | https://arxiv.org/abs/2605.10425 | abstract | 2026 |
| Reproducibility crisis in LLM-for-SE | https://arxiv.org/abs/2512.00651 | full text | 2025 |
| Balshem et al., GRADE guidelines 3 | https://doi.org/10.1016/j.jclinepi.2010.07.015 | abstract | 2011 |
| Lundh et al., Cochrane MR000033 | https://doi.org/10.1002/14651858.MR000033.pub3 | abstract | 2017 |
| Gigerenzer et al., PSPI | https://www.stat.berkeley.edu/~aldous/157/Papers/health_stats.pdf | full text | 2007 |
| Kvarven et al., Nature Human Behaviour | https://doi.org/10.1038/s41562-019-0787-z | abstract | 2020 |
| Nuijten et al., Behavior Research Methods | https://doi.org/10.3758/s13428-015-0664-2 | abstract | 2016 |
| Laws, BMC Psychology | https://doi.org/10.1186/s40359-016-0135-2 | full text | 2016-06-01 |

<!-- COMPLETE -->
