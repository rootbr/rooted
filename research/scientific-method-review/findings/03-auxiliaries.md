# Cluster 3 — Auxiliaries, refutation and revision

## Findings

### F3.1 A failed test refutes the claim together with its auxiliaries; error statistics and Bayesianism both indict the claim only as far as the auxiliaries were established on their own

- Answers: 6, 10; frontier 4
- Evidence:
  - SEP, "Underdetermination of Scientific Theory" (rev. 2023) — https://plato.stanford.edu/entries/scientific-underdetermination/ — full text — §2.1, quoting Duhem — "the experiment does not designate which one should be changed"
  - Mayo, 1996, *Error and the Growth of Experimental Knowledge* ch. 4 — https://errorstatistics.com/wp-content/uploads/2021/03/egek-pdf-red_chapter-4.pdf — full text — paragraph "An error-statistical description of the episode" — "Theory T is not shown to be in error as a result of anomaly e' unless the evidence warrants ruling out the possibility that an error in auxiliary hypothesis A is responsible. Evidence does not warrant ruling out an error in auxiliary A unless A has been shown to pass a sufficiently severe test."
  - Strevens, 2001, "The Bayesian Treatment of Auxiliary Hypotheses", BJPS 52 — https://www.strevens.org/research/prob/auxhyp.pdf — full text — paragraph "Second, δqd depends on the prior probabilities" — "The higher P (h), the less h is blamed when ha is refuted"
- Standing: two or more independent sources (Mayo reaches it against the Bayesian route)
- For the method (my inference): missing — method-provenance.md M-7 cites Duhem, yet the acceptance path sends "failed repeatably" straight to "refuted"; the step should require the record to name each auxiliary (prompt, measure, harness, model version, grader) and the check each passed, and otherwise record "the bundle failed" with the claim's standing unchanged.

### F3.2 In language-model evaluation the auxiliaries move scores and rankings, and locating the failing part is itself unreliable

- Answers: 6, 14; frontier 4
- Evidence:
  - Biderman et al., arXiv 2405.14782v3 — https://arxiv.org/pdf/2405.14782 — full text — §"“Minor” Implementation Details Matter" — "performance varies dramatically with the prompt (in some cases, > 20%), and which prompt style works best varies by model"
  - Mizrahi et al., 2024, arXiv 2401.00595v3 — https://arxiv.org/pdf/2401.00595 — full text — abstract — "different instruction templates lead to very different performance, both absolute and relative"
  - Thakur et al., 2024, "Judging the Judges", arXiv 2406.12624 — https://arxiv.org/abs/2406.12624 — abstract — "only the best (and largest) models achieve reasonable alignment with humans"
  - Zhang et al., 2025, arXiv 2505.00212 — https://arxiv.org/abs/2505.00212 — abstract — "The best method achieves 53.5% accuracy in identifying failure-responsible agents but only 14.2% in pinpointing failure steps"
- Standing: two or more independent sources
- For the method (my inference): missing — rule 3 should test a claim about a technique over several paraphrases of its prompt, with the grader checked against human labels, and rule 5's bounds should list these auxiliaries.

### F3.3 Popper's text, cited under M-7, requires reproducibility of any occurrence and makes a falsification a corroborated hypothesis; it fixes no count of two

- Answers: 1, 9
- Evidence:
  - Popper, *The Logic of Scientific Discovery*, selections — https://earthweb.ess.washington.edu/roe/Knowability_590/Week1/Popper.doc — full text (course copy) — paragraph "We say that a theory is falsified only if" — "non-reproducible single occurrences are of no significance to science"; "we only accept the falsification if a low-level empirical hypothesis which describes such an effect is proposed and corroborated"
- Standing: one source
- For the method (my inference): the text says otherwise, in part — method.md § Acceptance has "a rerun confirms a test of our own", so the asymmetry stands mainly for an opened external test. M-7 should mark "a second failure" as the repository's convention, not Popper's.

### F3.4 Counting failures is vote counting, which evidence synthesis rejects; a failure must exclude the claimed effect, and runs must be pooled

- Answers: 5, 1
- Evidence:
  - McKenzie & Brennan, Cochrane Handbook v6.5 ch. 12 — https://training.cochrane.org/handbook/current/chapter-12 — full text — §12.2.2.1 — "underpowered studies that do not rule out clinically important effects are counted as not showing benefit"
  - Simonsohn, 2015, "Small Telescopes", *Psychological Science* 26(5) — https://urisohn.com/sohn_files/wp/wordpress/wp-content/uploads/2019/01/small-telescopes-detectability-published.pdf — full text — p. 565 — "a replication needs 2.5 times as many observations as the original study to have about 80% power to reject d33%"
  - Altman & Bland, 1995, BMJ 311:485 — https://www.acsu.buffalo.edu/~wdmccall/os512d/EvidAbs.html — full text (reproduction) — para. 2 — "usually all that has been shown is an absence of evidence of a difference"
- Standing: two or more independent sources
- For the method (my inference): wrong — "a second failure under the same conditions" should become: the pooled estimate of all recorded runs excludes the effect the claim names, at a threshold and sample size recorded beforehand; a run too small to exclude it is recorded as inconclusive.

### F3.5 The method sets the threshold for support by the cost of error but the threshold for refutation by a fixed count

- Answers: 4, 3
- Evidence:
  - Lakens et al., 2018, "Justify your alpha", *Nature Human Behaviour* 2 — https://eprints.whiterose.ac.uk/128599/8/Justify%20Your%20Alpha.pdf — full text (accepted version) — paragraph "Benjamin et al. stated" — "Ideally, the alpha level is determined by comparing costs and benefits against a utility function using decision theory"
  - Nissen, Magidson, Gross & Bergstrom, 2016, arXiv 1609.00494 — https://arxiv.org/abs/1609.00494 — abstract — "Unless a sufficient fraction of negative results are published, the scientific process will do a poor job at discriminating false from true claims"
- Standing: one source for each part; their conjunction is my inference
- For the method (my inference): wrong — rule 3 sets repetitions "by the cost of an error", rule 7 fixes two failures; the relative cost of a wrongly kept and a wrongly withdrawn rule should be the owner's recorded decision per rule; a rule with a costly failure should leave force at the first failure.

### F3.6 A test that fails by its own design needs a branch of its own; a redesign after seeing data is a new test

- Answers: 7
- Evidence:
  - Gelman & Shalizi, arXiv 1006.3868v4 (BJMSP 2013) — https://arxiv.org/pdf/1006.3868 — full text — §"Model checking" — "The goal of model checking, then, is not to demonstrate the foregone conclusion of falsity as such, but rather to learn how, in particular, this model fails"
  - Hennig, in Gelman et al., arXiv 1905.08876v2 — https://arxiv.org/pdf/1905.08876 — full text — "Severity of model misspecification tests" — "misspecification tests need to be severe in order to fulfill their purpose"
  - Rubin, 2025, *Synthese* 206:111, arXiv 2408.12347 — https://arxiv.org/pdf/2408.12347 — full text — abstract — "sample-based validity-enhancing deviations cause an unknown inflation of the test procedure’s Type I error rate"
- Standing: two or more independent sources
- For the method (my inference): missing — the acceptance path should add "the test failed its own checks": the run is recorded as invalid with the check it failed, the redesign is registered before its run, and rule 6's "what was recorded before the result was seen?" tells redesign from fitting.

### F3.7 Claims known to be false in detail are judged by how and where they fail

- Answers: 8
- Evidence:
  - Gelman & Shalizi, as above — §1 — "all models in use are wrong—not merely falsifiable, but actually false"
  - SEP, "Imre Lakatos" (rev. 19 June 2026) — https://plato.stanford.edu/entries/lakatos/ — full text — §2.2, quoting Lakatos — "All theories, in this sense, are born refuted and die refuted"
- Standing: two or more independent sources
- For the method (my inference): missing — a claim behind a rule should state the tolerance it is used within, so that "refuted" means the error left that tolerance, and the record names where it fails as the next hypothesis.

### F3.8 Lakatos appraises the series of claims and their patches, which no per-claim rule inspects

- Answers: 9, 16
- Evidence:
  - SEP "Imre Lakatos", as above — §2.2 — "the unit of scientific evaluation is no longer the individual theory (as with Popper), but the sequence of theories, the research programme"; "he clearly thinks it a mistake to give up on a progressive research programme, unless there is a better one to shift to"
- Standing: one source (an encyclopedia's reading; Lakatos 1970 not opened)
- For the method (my inference): missing — rule 7 asks a reproducible failure, Popper's methodological falsification, yet withdraws a claim with no rival in view; a periodic review could mark as degenerating a family of rules whose rule-6 patches predict nothing new that passes.

### F3.9 Whether two tests "disagree" turns on whether their conditions differ, which the replication literature disputes

- Answers: 10
- Evidence:
  - Van Bavel et al., 2016, PNAS 113(23) — https://doi.org/10.1073/pnas.1521897113 — abstract (Europe PMC) — "the contextual sensitivity of the research topic was associated with replication success, even after statistically adjusting for several methodological characteristics"
  - Inbar, 2016, PNAS letter — https://pmc.ncbi.nlm.nih.gov/articles/PMC5003252/ — `recall, not opened` (title only, from search results)
- Standing: disputed: context explains failed replications (Van Bavel) against a confound of subdiscipline (Inbar, not opened); they part on whether the association holds within a subdiscipline
- For the method (my inference): over-strict — tests on disjoint populations never met "the same bounds", so neither is contested; each holds within its bounds, and the difference enters as a moderator hypothesis with a test that crosses it.

### F3.10 Keeping rival rules in force side by side has a defence

- Answers: 11
- Evidence:
  - Chang, 2016, "A History and Philosophy of Science in the Service of Scientific Pluralism" (Fernando Gil Prize lecture) — https://www.hps.cam.ac.uk/files/chang-scientific-pluralism.pdf — full text — §4.1 — "all theories with non-negligible prior probabilities should be monitored for signs of life"
- Standing: one source
- For the method (my inference): needs another procedure for a contested rule in use — which rival is in force meanwhile is a decision under uncertainty; the method should name who designs the separating test and record the interim rule as the owner's decision.

### F3.11 A refutation does not reach what relied on the claim unless something carries it

- Answers: 12, 13
- Evidence:
  - Hsiao & Schneider, 2021, *Quantitative Science Studies* 2(4) — https://doi.org/10.1162/qss_a_00155 — abstract (Europe PMC) — "among the 13,252 postretraction citation contexts, only 722 (5.4%) citation contexts acknowledged the retraction"
  - "Do links to retracted papers predict future retractions?", arXiv 2611.10474 (7 Nov 2026) — https://arxiv.org/abs/2611.10474 — abstract — "Among 10.5 million biomedical papers published 2015-2023, 2.1% cited a paper already retracted"
- Standing: two or more independent sources (both biomedicine)
- For the method (my inference): missing — a record should list its dependants (rules, skills, records using the claim as a premise), and a change of standing should trigger a check of each.

### F3.12 The "same conditions" rule 7 needs expire within about a year, and the "same" model drifts within months

- Answers: 14, 3
- Evidence:
  - Anthropic, "Model deprecations" (read 2026-11-21) — https://docs.anthropic.com/en/docs/about-claude/model-deprecations — full text — status table — "claude-sonnet-4-20250514 Retired April 14, 2026 June 15, 2026"; "Requests to retired models fail."
  - Chen, Zaharia & Zou, 2023, arXiv 2307.09009v3 — https://arxiv.org/pdf/2307.09009 — full text — abstract — "the behavior of the “same” LLM service can change substantially in a relatively short amount of time"
- Standing: two or more independent sources
- For the method (my inference): missing — once a version retires no second failure under the same conditions can occur, so refutation rarely fires while support outlives its model; the record should carry the retirement date, after which the rule stands as a decision with its hypothesis waiting for a retest.

### F3.13 Failed runs go unrecorded at the author's desk, so "the record holds every run" needs a mechanism

- Answers: 2, 15
- Evidence:
  - Franco, Malhotra & Simonovits, 2014, *Science* 345 — https://doi.org/10.1126/science.1255484 — abstract (Europe PMC) — "Strong results are 40 percentage points more likely to be published than are null results and 60 percentage points more likely to be written up"; "Authors do not write up and submit null findings."
  - Nissen et al., 2016, as under F3.5 — abstract — "false claims often can be canonized as facts"
- Standing: two or more independent sources
- For the method (my inference): keeps: rule 6 — the rule is right; the test command should append every run to the record itself, so recording a failure takes no decision by the maintainer.

## Open questions

- 2, the maintainer's relief or dread — F3.13 shows what authors do; no source found measures the feeling.
- 7, Mayo-Wilson's reading — his review of Mayo (2018), *Philosophical Review* 130(1), returned HTTP 403; F3.6 rests on other sources.
- 9, Lakatos's own definition of naive falsificationism and "ocean of anomalies" — absent from the SEP text searched; Lakatos 1970 not opened.
- 13, stare decisis and the cost of withdrawing a relied-upon rule — no legal source searched within the budget.
- 16, the number of claims at which one maintainer's work becomes a research programme — no source found that sets one.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| SEP, Underdetermination | https://plato.stanford.edu/entries/scientific-underdetermination/ | full text | rev. 4 Apr 2023 |
| SEP, Imre Lakatos | https://plato.stanford.edu/entries/lakatos/ | full text | rev. 19 Jun 2026 |
| Mayo, EGEK ch. 4 | https://errorstatistics.com/wp-content/uploads/2021/03/egek-pdf-red_chapter-4.pdf | full text | 1996 |
| Strevens | https://www.strevens.org/research/prob/auxhyp.pdf | full text | 2001 |
| Popper, selections | https://earthweb.ess.washington.edu/roe/Knowability_590/Week1/Popper.doc | full text | course copy, 2005 |
| Biderman et al. | https://arxiv.org/pdf/2405.14782 | full text | v3, 31 May 2026 |
| Mizrahi et al. | https://arxiv.org/pdf/2401.00595 | full text | v3, 6 May 2024 |
| Thakur et al. | https://arxiv.org/abs/2406.12624 | abstract | 2024 |
| Zhang et al. | https://arxiv.org/abs/2505.00212 | abstract | 2025 |
| Chen, Zaharia, Zou | https://arxiv.org/pdf/2307.09009 | full text | v3, 31 Oct 2023 |
| Anthropic, Model deprecations | https://docs.anthropic.com/en/docs/about-claude/model-deprecations | full text | read 2026-11-21 |
| Cochrane Handbook ch. 12 | https://training.cochrane.org/handbook/current/chapter-12 | full text | v6.5; chapter Oct 2019 |
| Simonsohn | https://urisohn.com/sohn_files/wp/wordpress/wp-content/uploads/2019/01/small-telescopes-detectability-published.pdf | full text | 2015 |
| Altman & Bland | https://www.acsu.buffalo.edu/~wdmccall/os512d/EvidAbs.html | full text, reproduction | 1995 |
| Lakens et al. | https://eprints.whiterose.ac.uk/128599/8/Justify%20Your%20Alpha.pdf | full text, accepted version | 2018 |
| Nissen et al. | https://arxiv.org/abs/1609.00494 | abstract | 2016 |
| Gelman & Shalizi | https://arxiv.org/pdf/1006.3868 | full text | v4, 2011 |
| Gelman et al. (Hennig) | https://arxiv.org/pdf/1905.08876 | full text | v2, 2019 |
| Rubin | https://arxiv.org/pdf/2408.12347 | full text | 2025 |
| Van Bavel et al. | https://doi.org/10.1073/pnas.1521897113 | abstract (Europe PMC) | 2016 |
| Chang | https://www.hps.cam.ac.uk/files/chang-scientific-pluralism.pdf | full text | Apr 2016 |
| Hsiao & Schneider | https://doi.org/10.1162/qss_a_00155 | abstract (Europe PMC) | 2021 |
| Retraction-link test | https://arxiv.org/abs/2611.10474 | abstract | 7 Nov 2026 |
| Franco et al. | https://doi.org/10.1126/science.1255484 | abstract (Europe PMC) | 2014 |

<!-- COMPLETE -->
