# Cluster 2 — Kinds of statement and the logical form of claims

## Findings

### F2.1 "Exit status zero means success" is a constitutive convention: the standard defines what counts as success; whether a program conforms is a claim

- Answers: 1, 14
- Evidence:
  - The Open Group, POSIX.1-2024, Shell Command Language — https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html — full text — `break` utility, EXIT STATUS — "EXIT STATUS 0 Successful completion."
  - Rescorla, SEP "Convention" — https://plato.stanford.edu/entries/convention/ — full text — on Marmor and Searle — "a constitutive convention helps “constitute” a social practice, in the sense that it helps define what the practice is and how to engage in it correctly"
- Standing: two or more independent sources
- For the method (my inference): missing — the norm row should tell a constitutive norm from a regulative one; "this tool conforms" is a claim (S-3's one-run test).

### F2.2 Prescribed practices are often found to work no better; evidence grading keeps evidence and recommendation apart, but the method does not say which governs action when they conflict

- Answers: 14, 15
- Evidence:
  - Prasad et al., 2013, "A decade of reversal", Mayo Clin Proc 88(8) — https://pubmed.ncbi.nlm.nih.gov/23871230/ — abstract — Results — "Of the 363 articles testing standard of care, 146 (40.2%) reversed that practice"
  - Guyatt et al., 2008, "GRADE: an emerging consensus…", BMJ 336:924 — https://pmc.ncbi.nlm.nih.gov/articles/PMC2335261/ — full text — "What makes a good grading system?" — "High quality evidence doesn’t necessarily imply strong recommendations, and strong recommendations can arise from low quality evidence."
- Standing: two or more independent sources for the separation; which entry governs is my inference
- For the method (my inference): keeps: rule 1 ("whether the practice works better is a separate claim"); missing — when a mandated norm meets a refuted underlying claim, compliance is the owner's recorded decision and the refuted claim keeps its record.

### F2.3 A prescription is a technical norm, but whether it splits cleanly into a fixed goal and a means–end claim is disputed, and recommendation practice weighs many criteria

- Answers: 16, 17, 6
- Evidence:
  - Franssen, van de Poel, Klenk et al., SEP "Philosophy of Technology" (2026) — https://plato.stanford.edu/entries/technology/ — full text — §2.2, on Niiniluoto and von Wright — "It is far less clear whether technical norms can have truth values. Von Wright tended to deny this"
  - Anderson, SEP "Dewey's Moral Philosophy" — https://plato.stanford.edu/entries/dewey-moral/ — full text — §3.1 — "The point of inquiring into means, and into ends considered as means or causes of further consequences, is not merely to determine how to achieve an end, but to appraise the value of the end itself"
  - Alonso-Coello et al., 2016, GRADE EtD frameworks 1, BMJ 353:i2016 — https://ilcor.org/uploads/Tools-GRADE-guidelines-Evidence-to-Decision-Tables.pdf — full text (reprint) — on criteria — "the balance between desirable and undesirable effects, resource use, acceptability, and feasibility"
- Standing: disputed: von Wright and Niiniluoto keep the descriptive means–end (anankastic) statement as the part with a truth value; Dewey holds that testing the means revises the end
- For the method (my inference): over-strict — "two premises" should be "at least two": trading accuracy against cost adds a weighing, a decision recorded beside the claims it weighs (answering 17).

### F2.4 Law splits a mixed question into legal standard, historical facts and application; the acceptance path gives one statement one kind

- Answers: 6
- Evidence:
  - U.S. Bank v. Village at Lakeridge, 2018 — https://www.law.cornell.edu/supremecourt/text/15-1509 — full text — opinion, Part II — "What remains for a bankruptcy court, after all that, is to determine whether the historical facts found satisfy the legal test chosen for conferring non-statutory insider status."
- Standing: one source
- For the method (my inference): missing — not a fifth branch but a first step splitting "this technique meets the goal" into decision, definition, claim and application, each by its branch.

### F2.5 A definition used as a measure carries a hypothesis that the measure tracks the thing, and LLM benchmarks show it passing untested

- Answers: 5, 13
- Evidence:
  - Tal, SEP "Measurement in Science" (2020) — https://plato.stanford.edu/entries/measurement-science/ — full text — §7.3 — "A good fit between item responses and a statistical model does not yet determine what the questionnaire is measuring."
  - Bean et al., 2025, "Measuring what Matters", NeurIPS D&B — https://arxiv.org/pdf/2511.04703 — full text — §4 — "52.2% of these definitions are widely agreed upon, but 47.8% are contested"; "16.0% used uncertainty estimates or statistical tests to compare the results."
  - Rescorla, SEP "Convention" — https://plato.stanford.edu/entries/convention/ — full text — on Quine and Putnam — "Although that identity began as a stipulative definition in Newtonian mechanics, Einsteinian mechanics deems it false."
- Standing: two or more independent sources
- For the method (my inference): wrong as worded — a definition serving as a claim's measure (operational "defect", a judge rubric) adds a validity claim that rule 1 lets pass as agreement; rule 2 should list it among the conditions.

### F2.6 Thick terms such as "calm" may not split into taste and description; rule 1 sides with one party of an open dispute

- Answers: 5
- Evidence:
  - Väyrynen, SEP "Thick Ethical Concepts" (2025) — https://plato.stanford.edu/entries/thick-ethical-concepts/ — full text — §2.2 — Inseparability: "Thick terms and concepts are or represent irreducible fusions of evaluation and non-evaluative description which cannot be “disentangled”."
- Standing: disputed: Hare and Blackburn hold separability; Williams, Putnam and Kirchin inseparability
- For the method (my inference): keeps: rule 1 under separability, which its "calm figures" example assumes; the method should state that assumption as a decision.

### F2.7 Where fact ends and claim begins depends on the instrument: observation is theory-laden, data are used to infer facts, and a judge's agreement with people is reliability, not validity

- Answers: 2, 12
- Evidence:
  - Boyd and Bogen, SEP "Theory and Observation in Science" (2026) — https://plato.stanford.edu/entries/science-theory-observation/ — full text — introduction — "All observations and uses of observational evidence are theory laden in this sense"; §2.3 — "investigators use data to infer facts about phenomena"
  - Pita, 2026, arXiv:2606.28574 — https://arxiv.org/abs/2606.28574 — abstract — "Yet reliability leaves construct validity untouched."
- Standing: two or more independent sources (Pita a single-author preprint)
- For the method (my inference): missing — a fact should name its instrument: "the agent read the file", read off a log by a regex or judge, holds relative to an instrument whose validity is an auxiliary claim.

### F2.8 A universal claim falls to one reproducible counter-instance, a statistical one to a result its model makes too improbable; standings and rule 7 treat both alike

- Answers: 9, 10
- Evidence:
  - Gelman and Shalizi, 2013 (arXiv v4) — https://arxiv.org/pdf/1006.3868 — full text — on Popper — "This is plainly inadequate for statistical hypotheses"
  - Romeijn, SEP "Philosophy of Statistics" (2025) — https://plato.stanford.edu/entries/statistics/ — full text — §3 — "In classical procedures statistical hypotheses are discarded when they render the observed sample too improbable, which of course differs from discarding hypotheses that deem the observed sample impossible."
  - Popper, LSD §22, selections — https://earthweb.ess.washington.edu/roe/Knowability_590/Week1/Popper.doc — full text of selection — "We shall take it as falsified only if we discover a reproducible effect which refutes the theory."
- Standing: two or more independent sources
- For the method (my inference): missing — for a statistical claim, rule 2's refuting outcome must be a rejection region with its error rate fixed beforehand; for a universal claim, rule 7's repetition should mean reproducing the same counter-instance.

### F2.9 An existential claim is verified by one instance and refuted by none, so rule 2 turns "some prompt makes the model leak the secret" into an opinion

- Answers: 11
- Evidence:
  - Popper, LSD §15 — https://www.bu.edu/jostl/files/2016/05/BILLAUER_ART_MACROD_FINAL-FINAL4.25WEB.pdf — secondary: Billauer 2016, B.U. J. Sci. & Tech. L., n. 233 — "This is the reason why strictly existential statements are not falsifiable."; "Whenever it is found that something exists here or there, a strictly existential statement may thereby be verified, or a universal one falsified."
  - Thornton, SEP "Karl Popper" (2026) — https://plato.stanford.edu/entries/popper/ — full text — §4 — a basic statement "can serve as a premise in an empirical falsification and which takes the singular existential form"
- Standing: two or more independent sources for the asymmetry; the application is my inference
- For the method (my inference): over-strict — an existential claim should enter as supported when its instance is in the record and reruns (stored prompt and transcript), with no failure count lowering it.

### F2.10 Estimation claims ("the median run costs 40k tokens") are a procedure apart from testing, with no place among the kinds or in rule 2

- Answers: 7
- Evidence:
  - Romeijn, SEP "Philosophy of Statistics" — https://plato.stanford.edu/entries/statistics/ — full text — §3 — "an estimation function points to one element from a range of hypotheses, or perhaps to a set of them, as being in some sense the best fit with that sample"
  - Cumming, 2014, "The new statistics", Psychol Sci 25(1) — https://pubmed.ncbi.nlm.nih.gov/24220629/ — abstract — "we need to shift from reliance on NHST to estimation and other preferred techniques"
- Standing: two or more independent sources
- For the method (my inference): missing — the record should take an estimate with interval, sample and conditions as a claim's content, revised when a rerun's interval excludes it.

### F2.11 A proof settles a claim about a model a priori; only conformance of the running system is empirical, and the method knows only empirical tests

- Answers: 7, 8
- Evidence:
  - Angius, Primiero, Turner, SEP "Philosophy of Computer Science" (2025) — https://plato.stanford.edu/entries/computer-science/ — full text — §7.2 — "The former kind of correctness can in principle be proved mathematically, but the correctness of the execution LoA requires an empirical assessment."; §6.2, Dijkstra — "Program testing can be used to show the presence of bugs, but never to show their absence"
  - Rey, SEP "The Analytic/Synthetic Distinction" (2026) — https://plato.stanford.edu/entries/analytic-synthetic/ — full text — opening — "true by virtue of the meanings of their words alone"
- Standing: two or more independent sources
- For the method (my inference): missing — "this design cannot deadlock" is a mathematical claim about a model, settled by a checked proof or exhaustive enumeration with model and checker as its bounds, plus an empirical conformance claim; the inference sentence should also require validity (my inference, no source opened).

### F2.12 The repository's agreement test bounds less than "readers agree on the kinds": two instances of one model, no definitions drawn, and same-provider models share errors

- Answers: 4
- Evidence:
  - The repository, `evals/kind-agreement/runs/run-1/score.txt` and `protocol.md` — local — full text — "agreed: 30 of 30", the definition row all 0; § Readers — "Two agents on Claude Opus 5.5 at effort `xhigh`"
  - Kim et al., 2025, "Correlated Errors in Large Language Models", ICML — https://arxiv.org/abs/2506.07962 — abstract — "models agree 60% of the time when both models err"
  - Wilson and Wiebe, 2003, "Annotating Opinions in the World Press" — https://aclanthology.org/W03-2102.pdf — full text — agreement section — "The average pairwise Kappa for sentence-level agreement is 0.77"
- Standing: two or more independent sources
- For the method (my inference): keeps: rule 1 within H-02's bounds; transfer to people sorting free statements needs human or cross-provider readers and a draw with definitions.

### F2.13 In evidence appraisal, "the test was severe" is an algorithm's proposed judgement from answers read off the paper, overridable, and slight in agreement between experts

- Answers: 18
- Evidence:
  - Higgins et al., Cochrane Handbook v6.5, ch. 8 — https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-08 — full text — key points — "A judgement about the risk of bias arising from each domain is proposed by an algorithm, based on answers to the signalling questions."; "can be overridden by the review authors, with justification"
  - Minozzi et al., 2020, J Clin Epidemiol 126 — https://pubmed.ncbi.nlm.nih.gov/32562833/ — abstract — "IRR was slight for overall judgment (IRR 0.16, 95% confidence interval (CI) 0.08-0.24)"
- Standing: two or more independent sources
- For the method (my inference): needs another procedure for appraisal of someone else's research — a mixed statement, not a fifth kind; rule 4 should hand over to a structured tool with recorded answers.

## Open questions

- 3, do the kinds alone improve design documents and post-mortems — searched decision-record and post-mortem literature; found prescriptions only, no measured comparison.
- 17, Chang's pluralism and Kusch's critique — not opened; F2.3 places the weighing only.
- Opened, not cited: POSIX exit(), SEP Pseudo-Science, SEP Operationalism, Amrhein et al. 2019 (paywalled).
- 19, what would make the taxonomy obsolete — no source testing a statement taxonomy against machine-checked specifications or preference-inferred decisions.
- The page of Popper's §15 — the online LSD scan holds 22 pages; the quote is seen only through Billauer.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| POSIX Shell Command Language | https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html | full text | 2024 |
| SEP Convention | https://plato.stanford.edu/entries/convention/ | full text | 2024-02-22 |
| Prasad et al. | https://pubmed.ncbi.nlm.nih.gov/23871230/ | abstract | 2013 |
| Guyatt et al., GRADE | https://pmc.ncbi.nlm.nih.gov/articles/PMC2335261/ | full text | 2008 |
| Alonso-Coello et al., EtD | https://ilcor.org/uploads/Tools-GRADE-guidelines-Evidence-to-Decision-Tables.pdf | full text | 2016 |
| SEP Philosophy of Technology | https://plato.stanford.edu/entries/technology/ | full text | 2026-07-10 |
| SEP Dewey's Moral Philosophy | https://plato.stanford.edu/entries/dewey-moral/ | full text | 2023-01-28 |
| Lakeridge opinion | https://www.law.cornell.edu/supremecourt/text/15-1509 | full text | 2018 |
| SEP Measurement in Science | https://plato.stanford.edu/entries/measurement-science/ | full text | 2020-08-07 |
| Bean et al. | https://arxiv.org/pdf/2511.04703 | full text | 2025-11 |
| SEP Thick Ethical Concepts | https://plato.stanford.edu/entries/thick-ethical-concepts/ | full text | 2025-01-21 |
| SEP Theory and Observation | https://plato.stanford.edu/entries/science-theory-observation/ | full text | 2026-01-12 |
| Pita | https://arxiv.org/abs/2606.28574 | abstract | 2026-06-26 |
| Gelman and Shalizi | https://arxiv.org/pdf/1006.3868 | full text | v4 2011 |
| SEP Philosophy of Statistics | https://plato.stanford.edu/entries/statistics/ | full text | 2025-10-01 |
| Popper, LSD selections | https://earthweb.ess.washington.edu/roe/Knowability_590/Week1/Popper.doc | full text of selection | 1959 text |
| Popper, LSD scan | https://epistemologies.wordpress.com/wp-content/uploads/2007/09/the-logic-of-scientific-discovery-by-karl-popper.pdf | 22 pages | partial |
| Billauer | https://www.bu.edu/jostl/files/2016/05/BILLAUER_ART_MACROD_FINAL-FINAL4.25WEB.pdf | full text | 2016 |
| SEP Karl Popper | https://plato.stanford.edu/entries/popper/ | full text | 2026-07-31 |
| Cumming | https://pubmed.ncbi.nlm.nih.gov/24220629/ | abstract | 2014 |
| SEP Philosophy of Computer Science | https://plato.stanford.edu/entries/computer-science/ | full text | 2025-02-03 |
| SEP Analytic/Synthetic | https://plato.stanford.edu/entries/analytic-synthetic/ | full text | 2026-06-01 |
| Kim et al. | https://arxiv.org/abs/2506.07962 | abstract | 2025 |
| Wilson and Wiebe | https://aclanthology.org/W03-2102.pdf | full text | 2003 |
| Cochrane Handbook ch. 8 | https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-08 | full text | v6.5, 2024 |
| Minozzi et al. | https://pubmed.ncbi.nlm.nih.gov/32562833/ | abstract | 2020 |
| Repository kind-agreement | plugins/evidence-based-authoring/skills/scientific-method/evals/kind-agreement/ | full text | 2026-11-21 |

<!-- COMPLETE -->
