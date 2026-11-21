# Cluster 4 — The ladder of standings: grades, degrees and stakes

## Findings

### F4.1 "Law" asks for independent, varied tests, but the record format counts only "two tests or more", and nothing checks whether the tests could have failed together

- Answers: 2, 3
- Evidence:
  - method.md § Standings — local — full text — "independent tests under varied conditions support it"; record-format.md § Fields a standing adds — "the fields of `supported`, with two tests or more"
  - Crupi, SEP "Confirmation", 2025 — https://plato.stanford.edu/entries/confirmation/ — full text — §3, "Indeed, the variety…" — "the variety of evidence is a fairly central issue in the analysis of confirmation"; "higher variety is readily captured by lower probability"
  - Kim et al., 2025, "Correlated Errors in Large Language Models" — https://arxiv.org/abs/2506.07962 — abstract — "models agree 60% of the time when both models err"
- Standing: two or more independent sources
- For the method (my inference): missing — a `law` record should name what differed between its tests (model family, task, reader, grader, data) and what they shared. Tests count as independent only when, were the claim false, passing all of them would have been improbable.

### F4.2 IPCC and GRADE treat "robust" and "independent" as a documented judgement, not a count

- Answers: 2
- Evidence:
  - Mastrandrea et al., 2010, IPCC AR5 Guidance Note on Uncertainties — https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf — full text — ¶8–9 — "evidence is most robust when there are multiple, consistent independent lines of high-quality evidence"; "Provide a traceable account"
  - Guyatt et al., 2008, "GRADE: an emerging consensus…", BMJ — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2335261/ — full text — "What is 'quality of evidence'" — "Quality of evidence is a continuum; any discrete categorisation involves some degree of arbitrariness."
- Standing: two or more independent sources
- For the method (my inference): missing — under rule 1, the boundary between `supported` and `law` is a definition. "These tests share no source of error" is a claim, so the record should give a short traceable account of it for the independent reader to challenge.

### F4.3 Readers misread a verbal grade on its own; scales that work pair the word with numbers and define each grade by what it means for the reader

- Answers: 1
- Evidence:
  - Budescu, Por, Broomell, 2012, Climatic Change 113:181–200 — https://storm.colorado.edu/~whan/ATOC4800_5000/Spring_2018/Materials/Effective_communication_of_unc.pdf — full text — Abstract — "the public consistently misinterprets the probabilistic statements in the IPCC report in a regressive fashion"; "using a dual (verbal—numerical) scale would be superior"
  - Guyatt et al., 2008 (F4.2) — Box 2 — "High quality — Further research is very unlikely to change our confidence in the estimate of effect"
- Standing: two or more independent sources
- For the method (my inference): missing — the table of standings defines each standing by the procedure behind it, not by its strength. A report should print runs per arm, result against threshold and bounds beside the word.

### F4.4 Rule 3 is Mayo's weak severity requirement used as a yes-or-no gate; in Mayo's account severity comes in degrees

- Answers: 5
- Evidence:
  - Mayo, 2018, *Statistical Inference as Severe Testing*, publisher's excerpt — https://assets.cambridge.org/97811076/64647/excerpt/9781107664647_excerpt.pdf — full text of excerpt — §1.1 — "Severity Requirement (weak): One does not have evidence for a claim if nothing has been done to rule out ways the claim may be false."
  - Romeijn, SEP "Philosophy of Statistics", 2025 — https://plato.stanford.edu/entries/statistics/ — full text — §3.3.2 — "a concept that can be characterized by reference to the significance and power of the statistical tests involved"
  - Gelman and Shalizi, 2013 — https://arxiv.org/abs/1006.3868 — full text — §4.2 — "a model being severely tested if it passes a probe which had a high probability of detecting an error if it is present"
- Standing: two or more independent sources
- For the method (my inference): missing — under rule 3 a test that could barely have failed still passes. The record should state how likely the test was to fail had the effect been below `threshold`, as power at the threshold or as an interval.

### F4.5 Rule 6 takes the error-statistical side of the stopping-rule dispute; Gelman's falsificationist Bayesianism keeps most rules, strict likelihoodism does not

- Answers: 6, 7
- Evidence:
  - Romeijn, SEP "Philosophy of Statistics" (F4.4) — §3.2.3 "Excursion: optional stopping" — "the impact of data on the hypotheses should depend on the stopping rule or protocol that is followed in obtaining it" (Mayo's side); against it: "the likelihoods of hypotheses for the observed data completely fix the evidential impact of those data on the hypotheses"
  - Gelman and Shalizi, 2013 (F4.4) — §1, §4.4 — "crucial parts of Bayesian data analysis, such as model checking, can be understood as “error probes” in Mayo’s sense"; "falsification is about plots and predictive checks, not about Bayes factors or posterior probabilities of candidate models"
- Standing: disputed. Error statisticians hold that the protocol and the stopping rule change what the data show; likelihoodists and subjective Bayesians hold that only the likelihoods count. The likelihood principle is what separates them.
- For the method (my inference): the text says otherwise — method.md says the rules hold "what the main lines of the philosophy of science share", yet under error statistics, "recorded before the test" bears on the evidence; under the likelihood principle it only guards against fitting. So a Bayes-factor reading of a test stopped early could give a different standing. Method.md should name the side it takes.

### F4.6 When the prior is low or the study small, a single pass leaves a claim more likely false than true

- Answers: 10
- Evidence:
  - Ioannidis, 2005, PLoS Med 2:e124 — https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.0020124 — full text — "Modeling the Framework…", Corollaries — "A research finding is thus more likely true than false if (1 - β) R > α"
  - Colquhoun, 2014, R. Soc. Open Sci. — https://pmc.ncbi.nlm.nih.gov/articles/PMC4448847/ — full text — Abstract — "If you use p =0.05 to suggest that you have made a discovery, you will be wrong at least 30% of the time."
- Standing: two or more independent sources
- For the method (my inference): missing — `supported` ignores prior odds and power. Rule 3 ("decided before the test, by the cost of an error") sets the sample size but does not weigh how implausible the claim was. The record should state prior plausibility (a decision); a surprising claim should need a repeated pass.

### F4.7 Treating every origin as equal throws away information: sponsor bias survives a reading of the test, and LLM judges favour their own outputs

- Answers: 11
- Evidence:
  - Lundh et al., 2017, Cochrane MR000033.pub3 — https://findresearcher.sdu.dk/ws/files/145419585/Industry_sponsorship_and_research_outcome.pdf — full text — Abstract — "Industry sponsored studies more often had favorable efficacy results, RR: 1.27 (95% CI: 1.17 to 1.37) (25 papers)"; "the existence of an industry bias that cannot be explained by standard"
  - Ioannidis, 2005 (F4.6) — Corollary 5 — "The greater the financial and other interests and prejudices in a scientific field, the less likely the research findings are to be true."
  - Panickssery, Bowman, Feng, 2024 — https://arxiv.org/abs/2404.13076 — abstract — "an LLM evaluator scores its own outputs higher than others' while human annotators consider them of equal quality"
- Standing: two or more independent sources
- For the method (my inference): wrong in part — equal origins holds for where a hypothesis comes from. It fails for weighing a test: "whoever its author" (rule 4) throws away a predictor that a reading of the results cannot recover. The record should name the test's sponsor and say whether the author, the system under test and the grader share a model.

### F4.8 Discrete standings read as thresholds on a degree of belief, but no fixed threshold stays consistent across many rules, and GRADE keeps discrete grades because they are easier to use

- Answers: 8, 9
- Evidence:
  - Genin and Huber, SEP "Formal Representations of Belief", 2020 — https://plato.stanford.edu/entries/formal-belief/ — full text — §4.2.2 — "Perhaps full belief corresponds to partial belief above some threshold falling short of certainty."; "no matter how high we set the threshold, there is some Lottery for which an agent must either violate the Lockean thesis or violate deductive cogency"
  - Guyatt et al., 2008 (F4.2) — "Nevertheless, advantages of simplicity, transparency, and vividness outweigh these limitations."
- Standing: two or more independent sources
- For the method (my inference): missing — discrete standings are kept, but a caveat is not. A skill holds many `supported` rules: each one may well be true while the set probably contains a false one. Discrete standings suit the question of whether a rule is in force; the degree (F4.4, F4.6) belongs beside them in the record.

### F4.9 Since Rudner, accepting a hypothesis has been held to depend on the cost of each error; law, GRADE and health-technology appraisal set the bar by the stakes and keep the evidence grade apart from the force of the action

- Answers: 14, 9
- Evidence:
  - Reiss and Sprenger, SEP "Scientific Objectivity", 2020 — https://plato.stanford.edu/entries/scientific-objectivity/ — full text — §3.2 — Rudner: "the scientist as scientist accepts or rejects hypotheses", a decision weighing "of making a mistake in accepting or rejecting a hypothesis"; Jeffrey: "So she should just refrain from the essentially pragmatic decision to accept or reject hypotheses."
  - Addington v. Texas, 441 U.S. 418 (1979) — https://www.law.cornell.edu/supremecourt/text/441/418 — full text — Part II — "The standard serves to allocate the risk of error between the litigants and to indicate the relative importance attached to the ultimate decision."
  - Guyatt et al., 2008 (F4.2) — "High quality evidence doesn’t necessarily imply strong recommendations, and strong recommendations can arise from low quality evidence."
  - Claxton et al., 2005, Health Econ 14:339–347 — http://eprints.gla.ac.uk/4164/1/Briggs4164.pdf — full text — "Dealing with uncertainty" — "rather than the traditional and arbitrary rules of inference"; value of information addresses "the appropriate length of time until the reconsideration of the guidance and the implications of irreversibility"
- Standing: two or more independent sources; Jeffrey dissents
- For the method (my inference): needs another procedure for decisions under uncertainty. The branch "yes, it held ► enters as a rule" joins a claim's standing to a rule's force. If the two were split, the standing would stay a claim under the seven rules. Putting a rule in force would become the owner's decision, with a bar set by reversibility and the cost of an error, by value of information where estimable, and fixed before the result, since the owner is also the author.

### F4.10 Norms admit a claim on a cheaper, indirect test under a provisional status that requires a confirmatory test

- Answers: 12
- Evidence:
  - 21 CFR § 314.510 (FDA accelerated approval), LII — https://www.law.cornell.edu/cfr/text/21/314.510 — full text — "has an effect on a surrogate endpoint that is reasonably likely, based on epidemiologic, therapeutic, pathophysiologic, or other evidence, to predict clinical benefit"; "subject to the requirement that the applicant study the drug further, to verify and describe its clinical benefit"
  - Guyatt et al., 2008 (F4.2) — "Although observational studies (for example, cohort and case-control studies) start with a “low quality” rating, grading upwards may be warranted"
- Standing: two or more independent sources
- For the method (my inference): missing — "in force as a decision, its hypothesis waits" covers a rule with no test at all. A rule backed by a simulation, an adversarial review or a surrogate measure needs a standing of its own between hypothesis and supported, naming its confirmatory test and when it is due.

### F4.11 Auditing and the IPCC keep "no sufficient evidence could be obtained" apart from "the evidence went against it", a difference the single standing `hypothesis` erases

- Answers: 13
- Evidence:
  - IAASB, ISA 705, 2009 Handbook — https://www.kacr.cz/Data/Metodika/Auditing/Handbook%202009/ISA_705.pdf — full text — ¶9 — "The auditor shall disclaim an opinion when the auditor is unable to obtain sufficient appropriate audit evidence on which to base the opinion"; contrast ¶8, adverse opinion: "having obtained sufficient appropriate audit evidence, concludes that misstatements"
  - Mastrandrea et al., 2010 (F4.2) — ¶11 A) — "Confidence should not be assigned; assign summary terms for evidence and agreement"
- Standing: two or more independent sources
- For the method (my inference): missing — a hypothesis record should say whether its test is pending or unaffordable. An unaffordable one stands as a decision with a disclaimer and a named trigger for testing.

### F4.12 For prompt and agent techniques, "law" with wide bounds is rarely reachable: the "same" model drifts within months, and prompt effects carry poorly from one model to another

- Answers: 4, 3
- Evidence:
  - Chen, Zaharia, Zou, 2023 — https://arxiv.org/abs/2307.09009 — abstract — "the behavior of the "same" LLM service can change substantially in a relatively short amount of time"
  - Sclar et al., 2023 — https://arxiv.org/abs/2310.11324 — abstract — "performance differences of up to 76 accuracy points"; "format performance only weakly correlates between models"
- Standing: two or more independent sources (both from 2023; I opened no newer measure)
- For the method (my inference): over-strict in name only. Dropping `law` would change the standing vocabulary and the `TEST` count in record-format.md. The distinction that does work is the width of `bounds` (rule 5). Neither GRADE nor the IPCC has a top grade named "law".

## Open questions

- Q7, Gelman calling his falsificationist Bayesianism underdeveloped — Gelman and Shalizi (arXiv v4, full text) searched for "underdevelop", "incomplete" and kin: no such statement; the source was not found.
- Q3, a historian's rule for counting dependent witnesses — no source-criticism text opened; F4.1 rests on confirmation theory and LLM error correlation instead.
- Q9, discrete standings derived as a special case of value of information — none found; Claxton 2005 gives only the position.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| method.md, record-format.md, method-provenance.md | local | full text | working tree 2026-11-21 |
| SEP Confirmation | https://plato.stanford.edu/entries/confirmation/ | full text | rev. 2025-08-04 |
| SEP Philosophy of Statistics | https://plato.stanford.edu/entries/statistics/ | full text | rev. 2025-10-01 |
| SEP Formal Representations of Belief | https://plato.stanford.edu/entries/formal-belief/ | full text | rev. 2020-11-13 |
| SEP Scientific Objectivity | https://plato.stanford.edu/entries/scientific-objectivity/ | full text | rev. 2020-10-30 |
| IPCC AR5 Uncertainty Guidance Note | https://www.ipcc.ch/site/assets/uploads/2017/08/AR5_Uncertainty_Guidance_Note.pdf | full text | 2010 |
| Budescu, Por, Broomell | https://storm.colorado.edu/~whan/ATOC4800_5000/Spring_2018/Materials/Effective_communication_of_unc.pdf | full text | 2012 |
| Guyatt et al., GRADE | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2335261/ | full text | 2008 |
| Mayo, SIST excerpt | https://assets.cambridge.org/97811076/64647/excerpt/9781107664647_excerpt.pdf | full text of excerpt | 2018 |
| Gelman and Shalizi | https://arxiv.org/abs/1006.3868 | full text | v4 2011, publ. 2013 |
| Ioannidis | https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.0020124 | full text | 2005 |
| Colquhoun | https://pmc.ncbi.nlm.nih.gov/articles/PMC4448847/ | full text | 2014 |
| Lundh et al., Cochrane | https://findresearcher.sdu.dk/ws/files/145419585/Industry_sponsorship_and_research_outcome.pdf | full text | 2017 |
| Panickssery et al. | https://arxiv.org/abs/2404.13076 | abstract | 2024 |
| Kim et al. | https://arxiv.org/abs/2506.07962 | abstract | 2025 |
| Chen, Zaharia, Zou | https://arxiv.org/abs/2307.09009 | abstract | 2023 |
| Sclar et al. | https://arxiv.org/abs/2310.11324 | abstract | 2023 |
| Addington v. Texas | https://www.law.cornell.edu/supremecourt/text/441/418 | full text | 1979 |
| 21 CFR 314.510 | https://www.law.cornell.edu/cfr/text/21/314.510 | full text | LII, read 2026-11-21 |
| IAASB ISA 705 | https://www.kacr.cz/Data/Metodika/Auditing/Handbook%202009/ISA_705.pdf | full text | 2009 Handbook |
| Claxton et al. | http://eprints.gla.ac.uk/4164/1/Briggs4164.pdf | full text | 2005 |

<!-- COMPLETE -->
