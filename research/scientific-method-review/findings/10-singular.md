# Cluster 10 — Singular, diagnostic and applied tasks beyond skill rules

## Findings

### F10.1 A claim about one past event is tested by traces that discriminate among rival hypotheses, and diagnosis infers the best of them; the method has no path for such claims, and how strong that inference is remains disputed

- Answers: 5, 6, 8; frontier 7
- Evidence:
  - Cleland, 2002, "Methodological and Epistemic Differences between Historical Science and Experimental Science" — https://joelvelasco.net/teaching/5330/cleland02-methodological_differences.pdf — full text — abstract; smoking-gun paragraph — "It rejects the claim that historical research is epistemically inferior."; "A smoking gun is a trace (or subcollection of traces) that (so-to-speak) cinches the case for a particular causal story."; "it is always possible that future observations or theoretical developments will depose a smoking gun"
  - Turner, 2005, "Local Underdetermination in Historical Science" — https://joelvelasco.net/teaching/5330/turner%2005%20-%20local%20underdetermination%20in%20historical%20science.pdf — full text — abstract — "there is at least one interesting sense in which historical science is epistemically inferior to experimental science, after all, because local underdetermination problems are more widespread in historical than in experimental science."
  - Douven, SEP "Abduction" (rev. 2025) — https://plato.stanford.edu/entries/abduction/ — full text — §1, paragraph "Many other examples"; §2 after ABD1 — "Abduction is also said to be the predominant mode of reasoning in medical diagnosis: physicians tend to go for the hypothesis that best explains the patient’s symptoms"; "it will not be a sound rule of inference in the strict logical sense"
- Standing: `disputed: Cleland — testing by smoking guns is not inferior; Turner — it is, because rivals stay underdetermined more often`; they differ on how often traces run out.
- For the method (my inference): `missing` — method.md needs a second path for singular claims: the named rivals, the discriminating trace and a standing "best of the named rivals" bounded to the one event, with rule 6 kept by letting a newly found trace count as "a later observation".

### F10.2 In an outage the field's procedure is hypothetico-deductive, but mitigation comes before diagnosis and tests are ordered by likelihood and risk; refutable guesses and a log fit in minutes, repetitions with a preset threshold do not

- Answers: 1, 3, 4
- Evidence:
  - Google, *Site Reliability Engineering*, ch. 12 — https://sre.google/sre-book/effective-troubleshooting/ — full text — "Theory"; "Triage"; "Test and Treat" — "we can think of the troubleshooting process as an application of the hypothetico-deductive method"; "Stopping the bleeding should be your first priority; you aren’t helping your users if the system dies while you’re root-causing."; "perform the tests in decreasing order of likelihood, considering possible risks to the system from the test"; "Some tests may not be definitive, only suggestive."; "Take clear notes of what ideas you had, which tests you ran, and the results you saw."
  - Zeller, *The Debugging Book*, "Introduction to Debugging" — https://www.debuggingbook.org/html/Intro_Debugging.html — full text — "Keep a Log" — "Writing these things down explicitly allow you to keep track of all your observations and hypotheses over time."
- Standing: `two or more independent sources`
- For the method (my inference): `needs another procedure for incident response` — rules 1, 2 and the log of rule 6 carry over, rule 3's repetitions and cost-set threshold break first, and method.md should state that a mitigation is a decision taken ahead of any diagnosis.

### F10.3 "The fix made the symptom go away once" shows at most causality, not incorrectness, and production rarely allows reproduction; it stays a probable cause

- Answers: 2
- Evidence:
  - Zeller, "Introduction to Debugging" — URL as in F10.2 — full text — "Checking Diagnoses" — "If you find that you can change some location to make the failure go away, but are not sure why this location is wrong, then your "fix" may apply only to the symptom rather than the source."
  - Google SRE, ch. 12 — URL as in F10.2 — full text — "Cure" — "often, we can only find probable causal factors"; "Reproducing the problem in a live production system may not be an option"
- Standing: `two or more independent sources`
- For the method (my inference): `missing` — the acceptance path has no standing for this case, and the singular path of F10.1 could take Zeller's two conditions, causality and incorrectness, as its check question.

### F10.4 Bisection and a minimal reproducer turn a singular defect into a repeatable intervention, when the test is deterministic and fast

- Answers: 3, 4
- Evidence:
  - Google SRE, ch. 12 — URL as in F10.2 — full text — "Diagnose" — "bisection, splits the system in half and examines the communication paths between components on one side and the other"
  - Zeller, "Reducing Failure-Inducing Inputs" — https://www.debuggingbook.org/html/DeltaDebugger.html — full text — complexity paragraph — "provided that the underlying test case is deterministic and runs quickly enough to warrant a number of experiments"
- Standing: `two or more independent sources`
- For the method (my inference): `keeps: rules 3, 4 once a reproducer exists` — method.md could say that a diagnosis with a deterministic reproducer leaves the singular path for the ordinary one.

### F10.5 One unit with no parallel copy still admits a controlled comparison: an n-of-1 randomised crossover or a before-after-control-impact design, whose verdict moves with the number of post-impact periods

- Answers: 7, 8
- Evidence:
  - Daza, 2019, "Person as Population" — https://arxiv.org/pdf/1901.03423 — full text — §1 — "N-of-1 randomized trials (N1RTs) do not generally require causal inference methods due to their simple randomized crossover design."
  - Smokorowski and Randall, 2017, "Cautions on using the Before-After-Control-Impact design", FACETS 2 — http://piat.org.nz/uploads/PIAT_content/pdfs/Smokorowski%20and%20Randall_2017.pdf — full text — abstract — "the BACI design was able to detect effects from the impact that the two suboptimal designs failed to detect"; "the BACI design demonstrated different conclusions depending on the number and configuration of post-impact years included in the analysis"
- Standing: `two or more independent sources` that one unit admits a comparison; each design rests on one source here, and Daza predates recent n-of-1 work.
- For the method (my inference): `missing` — rule 3 should name these designs for a rule used in one repository, with the number of periods fixed in advance under rule 6.

### F10.6 Live product experiments need validity checks none of the seven rules names: sample-ratio mismatch, optional stopping and learning effects

- Answers: 9, 10
- Evidence:
  - Fabijan et al., 2019, "Diagnosing Sample Ratio Mismatch in Online Controlled Experiments" — https://exp-platform.com/Documents/2019_KDDFabijanGupchupFuptaOmhoverVermeerDmitriev.pdf — full text — abstract; §3 — "Just like fever is a symptom for multiple types of illness, an SRM is a symptom for a variety of data quality issues."; "approximately 6% of experiments at Microsoft exhibit an SRM"
  - Johari, Pekelis, Walsh, 2019, "Always Valid Inference" — https://arxiv.org/pdf/1512.04922 — full text — abstract — "wholly unreliable if users endogenously choose samples sizes by continuously monitoring their tests"
  - Hohnhold, O'Brien, Tang, 2015, "Focusing on the Long-term" — https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43887.pdf — full text — abstract — "the short-term effect is not always predictive of the long-term effect"
- Standing: `two or more independent sources`, one per practice
- For the method (my inference): `missing` — peeking partly falls under rule 6 and learning effects under rule 5, but sample-ratio mismatch has no rule, and for a test that cannot be rerun "opening the description" under rule 4 reproduces nothing unless the description carries these checks.

### F10.7 A with-and-without comparison in an evaluation buys a paired, item-level difference and a power calculation; one held-out run gives a score, not an effect

- Answers: 11
- Evidence:
  - Miller, 2024, "Adding Error Bars to Evals" — https://arxiv.org/pdf/2411.00640 — full text — abstract; recommendations in §1 — "Fundamentally, evaluations are experiments"; "Using power analysis to determine whether an eval (or a random subsample) is capable of testing a hypothesis of interest"
- Standing: `one source`
- For the method (my inference): `keeps: rule 3` — power analysis is the concrete form of "decided before the test, by the cost of an error", and whether the paired design repays the doubled cost depends on a score correlation I found no measurement of.

### F10.8 Contamination corrupts the test input; leaderboard overfitting selects among runs; rule 6 covers the second, nothing covers the first, and sources disagree on how much adaptivity matters

- Answers: 12
- Evidence:
  - Sainz et al., 2023, "NLP Evaluation in trouble" — https://arxiv.org/pdf/2310.18018 — full text — abstract — "Contamination causes an overestimation of the performance of a contaminated model in a target benchmark"
  - Oren et al., 2023, "Proving Test Set Contamination in Black Box Language Models" — https://arxiv.org/pdf/2310.17623 — full text — abstract — "find little evidence for pervasive contamination"
  - Singh et al., 2025, "The Leaderboard Illusion" — https://arxiv.org/pdf/2504.20879 — full text — abstract — "the ability of these providers to choose the best score leads to biased Arena scores due to selective disclosure of performance results"
  - Dwork et al., 2015, "Generalization in Adaptive Data Analysis and Holdout Reuse" — https://arxiv.org/pdf/1506.02629 — full text — abstract — "Reusing a holdout set adaptively multiple times can easily lead to overfitting to the holdout set itself."
  - Recht et al., 2019, "Do ImageNet Classifiers Generalize to ImageNet?" — https://arxiv.org/pdf/1902.10811 — full text — abstract — "the accuracy drops are not caused by adaptivity"
- Standing: `disputed: Dwork, Singh — adaptive reuse and selective disclosure inflate scores; Recht — on ImageNet the drop came from harder images, not adaptivity`; Recht measured published models, Singh private variants with retraction. The contamination sources predate 2026 work.
- For the method (my inference): `missing` — rule 6 ("the record holds every run") already catches selective disclosure, but rule 5 should name exposure of the test items to the system under test as a condition of the bounds.

### F10.9 An assurance case records doubts about the evidence and the inference, not only about the claim; "acceptably safe" is a risk acceptance by a named post, not a standing

- Answers: 14
- Evidence:
  - Goodenough, Weinstock, Klein, 2015, *Eliminative Argumentation*, CMU/SEI-2015-TR-005 — https://insights.sei.cmu.edu/documents/1248/2015_005_001_434813.pdf — full text — §1; §2.4.1 — "confidence in a hypothesis (or claim) increases as reasons for doubting its truth are identified and eliminated"; "rebutting defeaters state reasons why a claim could be false, undermining defeaters state reasons why evidence could be invalid, and undercutting defeaters identify deficiencies in an inference rule"
  - Bloomfield, Netkachova, Rushby, 2024, "Defeaters and Eliminative Argumentation in Assurance 2.0" — https://www.csl.sri.com/~rushby/papers/defeaters24.pdf — full text — §1 — "defeaters play a dialectical rôle in argument that is similar to falsification in science"
  - UK MOD, Def Stan 00-56 Part 1 Issue 6, 2015 — https://s3-eu-west-1.amazonaws.com/s3.spanglefish.com/s/22631/documents/safety-specifications/def-stan-00-056-pt1-iss6-02apr15.pdf — full text — 13.2.1; note to 1.3 — "a compelling, comprehensible and valid case that a system is safe for a given application in a given environment"; "the designated posts who can accept risks as being tolerable and ALARP"
- Standing: `two or more independent sources` (SEI and SRI are distinct teams in one tradition; Def Stan is a norm)
- For the method (my inference): `missing` — the record would gain a list of undermining and undercutting defeaters with what eliminated each, while "acceptably safe" already splits into supported claims plus an owner's decision by method.md's two premises of a prescription.

### F10.10 A forecaster's track record predicts the next forecasts' accuracy beyond luck; calibration can rank authors of hypotheses but tests no claim

- Answers: 15
- Evidence:
  - Mellers et al., 2015, "Identifying and Cultivating Superforecasters" — https://stanford.edu/~knutson/nfc/mellers15.pdf — full text — results, Years 2–3 — "the superforecaster intervention from Year 2 was cleanly replicated in Year 3"; "top-team individuals and all others showed regression effects"
- Standing: `one source`
- For the method (my inference): `keeps: the clause that a claim of any origin is judged the same way` — a Brier score could order which hypotheses are tested first, but counting it as evidence would let origin stand in for a test.

### F10.11 Whether one method fits all fields is open, with the literature leaning to a middle pluralism; method.md states universality without saying whether its scope is a decision or a claim

- Answers: 16, 17
- Evidence:
  - Andersen and Hepburn, SEP "Scientific Method" (rev. 8 Aug 2026) — https://plato.stanford.edu/entries/scientific-method/ — full text — introduction — "Some middle degree of pluralism regarding the methods embodied in scientific practice seems appropriate."
  - Scheel et al., 2021, "Why Hypothesis Testers Should Spend Less Time Testing Hypotheses" — https://pmc.ncbi.nlm.nih.gov/articles/PMC8273364/ — full text — section on the derivation chain — "judging the quality of these inputs will depend on the specifics of a research area and require an open discourse within the research community"
- Standing: `two or more independent sources`
- For the method (my inference): `over-strict` — "they apply to every statement alike" should be marked as the owner's decision, with the field-specific input checks of F10.4, F10.6, F10.8 and F10.9 listed per task as transfers.

### F10.12 An architecture decision record already holds a decision resting on an untested claim, with a status that moves, as the acceptance path's "in force as a decision" does

- Answers: 13
- Evidence:
  - Nygard, 2011, "Documenting Architecture Decisions" — https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions — full text — "Status"; "Consequences"; paragraph "Blindly change it" — "A decision may be "proposed" if the project stakeholders haven't agreed with it yet, or "accepted" once it is agreed."; "All consequences should be listed here, not just the "positive" ones."; "(E.g., the decision supported a non-functional requirement that hasn't been tested yet.)"
- Standing: `one source` (the format's originator)
- For the method (my inference): `keeps: rule 1 and the last paragraph of Acceptance` — which rules teams would reject as too costly stays open.

### F10.13 Optimising behaviour end to end against a metric moves the rule-level claims into one: that the metric and its items measure the goal

- Answers: 18
- Evidence:
  - Khattab et al., 2023, "DSPy" — https://arxiv.org/pdf/2310.03714 — full text — abstract — "We design a compiler that will optimize any DSPy pipeline to maximize a given metric."
- Standing: `one source`; the step to irrelevance is `my inference`
- For the method (my inference): `keeps: rules 5, 6` — acceptance would move to the metric's validity and to holdout reuse (F10.8) rather than become irrelevant; the source predates 2026 optimisers.

## Open questions

- Q5, historians' source criticism — not searched within budget; only Cleland and Turner were opened.
- Q4, value of information within one session — no decision-theory source opened.
- Q10, guardrail metrics and long-term holdouts — Kohavi et al. not opened.
- Q13, rules teams reject as too costly — no empirical ADR study found.
- Q17, how to study fit to other tasks — no comparative source found.
- CENT 2015 and Stewart-Oaten et al. 1986 — downloads blocked; one host served unrelated content, discarded.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| Cleland | https://joelvelasco.net/teaching/5330/cleland02-methodological_differences.pdf | full text | Phil. Sci. 69, 2002 |
| Turner | https://joelvelasco.net/teaching/5330/turner%2005%20-%20local%20underdetermination%20in%20historical%20science.pdf | full text | Phil. Sci. 72, Jan 2005 |
| SEP Abduction | https://plato.stanford.edu/entries/abduction/ | full text | rev. 18 Jun 2025 |
| SEP Scientific Method | https://plato.stanford.edu/entries/scientific-method/ | full text | rev. 8 Aug 2026 |
| Google SRE ch. 12 | https://sre.google/sre-book/effective-troubleshooting/ | full text | web edition, undated as fetched |
| Zeller, Intro to Debugging | https://www.debuggingbook.org/html/Intro_Debugging.html | full text | web edition, fetched 2026-11-21 |
| Zeller, Delta Debugger | https://www.debuggingbook.org/html/DeltaDebugger.html | full text | web edition, fetched 2026-11-21 |
| Daza | https://arxiv.org/pdf/1901.03423 | full text | arXiv v3, Jan 2019 |
| Smokorowski, Randall | http://piat.org.nz/uploads/PIAT_content/pdfs/Smokorowski%20and%20Randall_2017.pdf | full text | FACETS 2, 2017 |
| Fabijan et al. | https://exp-platform.com/Documents/2019_KDDFabijanGupchupFuptaOmhoverVermeerDmitriev.pdf | full text | KDD'19 authors' version |
| Johari et al. | https://arxiv.org/pdf/1512.04922 | full text | arXiv v3, Jul 2019 |
| Hohnhold et al. | https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/43887.pdf | full text | KDD 2015 |
| Miller | https://arxiv.org/pdf/2411.00640 | full text | arXiv v1, Nov 2024 |
| Sainz et al. | https://arxiv.org/pdf/2310.18018 | full text | arXiv v1, Oct 2023 |
| Oren et al. | https://arxiv.org/pdf/2310.17623 | full text | arXiv v2, Nov 2023 |
| Singh et al. | https://arxiv.org/pdf/2504.20879 | full text | arXiv v2, May 2025 |
| Dwork et al. | https://arxiv.org/pdf/1506.02629 | full text | arXiv v2, Sep 2015 |
| Recht et al. | https://arxiv.org/pdf/1902.10811 | full text | arXiv v2, Jun 2019 |
| Goodenough et al. | https://insights.sei.cmu.edu/documents/1248/2015_005_001_434813.pdf | full text | SEI TR-005, 2015 |
| Bloomfield et al. | https://www.csl.sri.com/~rushby/papers/defeaters24.pdf | full text | SRI-CSL-2024-01, May 2024 |
| Def Stan 00-56 Pt 1 | https://s3-eu-west-1.amazonaws.com/s3.spanglefish.com/s/22631/documents/safety-specifications/def-stan-00-056-pt1-iss6-02apr15.pdf | full text | Issue 6, Apr 2015 |
| Koopman et al. (not cited) | https://arxiv.org/pdf/2404.16768 | full text | arXiv 2024 |
| Mellers et al. | https://stanford.edu/~knutson/nfc/mellers15.pdf | full text | Persp. Psych. Sci., 2015 |
| Scheel et al. | https://pmc.ncbi.nlm.nih.gov/articles/PMC8273364/ | full text | 2021 |
| Nygard | https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions | full text | 15 Nov 2011 |
| Khattab et al. | https://arxiv.org/pdf/2310.03714 | full text | arXiv v1, Oct 2023 |
| Haulk et al. (not cited) | https://arxiv.org/html/2609.01973v1 | abstract | arXiv v1, Sep 2026 |

<!-- COMPLETE -->
