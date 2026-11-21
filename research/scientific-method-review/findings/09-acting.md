# Cluster 9 — Acting before the evidence: decisions, costs and uncertainty

## Findings

### F9.1 Decision theory treats "what to do now on the evidence in hand" and "whether to get more evidence" as two separate decisions, and neither depends on whether a claim passed a test.

- Answers: 12, 13, 14; frontier 3
- Evidence:
  - Claxton 1999, "The irrelevance of inference", J Health Econ 18(3):341–364 — https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=10537899&rettype=abstract&retmode=text — abstract — "Decisions should be based only on the mean net benefits irrespective of whether differences are statistically significant"; "The distribution of net benefit is only relevant to deciding whether more information is required"
  - Manski 2019, "Statistical inference for statistical decisions" — https://arxiv.org/pdf/1909.06853 — full text — abstract — "An SDF need not perform statistical inference; that is, it need not use data to draw conclusions about the true state of nature."
  - ASA 2016, Statement on p-values — https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf — full text — principle 3 — "Scientific conclusions and business or policy decisions should not be based only on whether a p-value passes a specific threshold."
- Standing: two or more independent sources
- For the method (my inference): needs another procedure for decisions under uncertainty. The acceptance path decides whether a claim enters the rule list and says nothing about acting. method.md could state that a standing does not decide an action, and hand the action, with its costs and reversibility, to expected value or regret analysis plus the value of information.

### F9.2 GRADE keeps the certainty of evidence apart from the strength of a recommendation. It allows a strong recommendation on low-certainty evidence only in five situations of low regret, and panels often break that limit.

- Answers: 17, 14, 1; frontier 3
- Evidence:
  - Guyatt et al. 2008, "GRADE: going from evidence to recommendations", BMJ 336:1049 — https://www.cebma.org/assets/Uploads/Guyatt-From-evidence-to-recommendations-BMJ_2008.pdf — full text — table "Determinants of strength of recommendation" (balance of effects, quality of evidence, values and preferences, costs) — "The higher the quality of evidence, the higher the likelihood that a strong recommendation is warranted"
  - Andrews et al. 2013, "GRADE guidelines: 15", J Clin Epidemiol 66:726–735 — https://www.eu-patient.eu/contentassets/09e1058baccc4310ab0775353836c830/grade-guidelines_15_going-from-evidence-to-recommendation.pdf — full text — §2.3.1 — "These situations can be conceptualized as ones in which a panel would have a low level of regret if subsequent evidence showed that their recommendation was misguided."
  - Alexander et al. 2016, J Clin Epidemiol 72:98–106 — https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=25618534&rettype=abstract&retmode=text — abstract — "Of 160 discordant recommendations, 25 (15.6%) were judged consistent with one of the five paradigms"
- Standing: two or more independent sources.
- For the method (my inference): missing. "In force as a decision" is the method's only way to prescribe a rule before its test, and it records no grounds for how firmly. A second axis, firmness of prescription, carrying the balance of consequences, cost and regret, would sit beside the standing.

### F9.3 Setting error rates and sample size by the cost of an error is an established line, which asks that the costs and error rates be stated before the data. Its source, as cited in the provenance, is one side of a dispute.

- Answers: 2, 11, 16
- Evidence:
  - Rudner 1953, "The scientist qua scientist makes value judgments", Phil Sci 20:1–6 — https://www.joelvelasco.net/teaching/3330/rudner53-quascientist.pdf — full text — paragraph opening "But if this is so then clearly the scientist as scientist does make value judgments" — "How sure we need to be before we accept a hypothesiswill depend on how serious a mistake would be." (the missing space is the scan's)
  - Lakens et al. 2018, "Justify your alpha", Nat Hum Behav 2:168 — https://eprints.whiterose.ac.uk/128599/8/Justify%20Your%20Alpha.pdf — full text (accepted manuscript) — abstract — "justify their choice for an alpha level before collecting the data"
  - Mudge et al. 2012, PLoS One 7:e32734 — https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=22389720&rettype=abstract&retmode=text — abstract — "greater transparency concerning assumptions about relevant effect size(s) and the relative costs of Type I and II errors"
  - Manski 2026, "Systemic methodological dysfunction in statistical research for clinical decisions" — https://arxiv.org/pdf/2607.23660 — full text — §2 — "The theory of hypothesis testing gives no rationale to select these error probabilities."
  - SEP "Scientific Method" (rev. 8 Aug 2026) — https://plato.stanford.edu/entries/scientific-method/ — full text — §4 — "On Fisher's view, hypothesis testing was a methodology for when to accept or reject a statistical hypothesis"; "In contrast, on Neyman and Pearson's view, the consequence of error also had to play a role when deciding between hypotheses." The M-3 line of `maintenance/method-provenance.md` cites the second sentence and not the contrast.
- Standing: two or more independent sources
- For the method (my inference): keeps: rule 3. Two changes would follow. `references/record-format.md` has `threshold` ("the size of difference fixed before the test") and `runs`, but no field for the cost of each error, the error rates accepted, or who set them, so a reader cannot check "decided before the test, by the cost of an error". And M-3 could record that rule 3 takes the Neyman–Pearson side.

### F9.4 Whose costs set the evidential threshold is disputed: Rudner and Douglas make the acceptable inductive risk a value judgement, while Jeffrey and Levi keep values out of acceptance.

- Answers: 3, 2
- Evidence:
  - SEP "Scientific Objectivity" (rev. 30 Oct 2020) — https://plato.stanford.edu/entries/scientific-objectivity/ — full text — §3, on Rudner — "Contextual values influence scientific methods by determining the acceptable amount of inductive risk (see also Douglas 2000)"; the rebuttals work "either by denying that scientists actually choose theories (Jeffrey), or by referring to community standards and restricting the VNT to the individual scientist (Levi)"
  - Andrews et al. 2013 as under F9.2 — §3.2 — "explicitly state the perspective they are taking, particularly when they are not taking a patient-centered perspective"
- Standing: disputed. Rudner and Douglas hold that accepting a claim weighs whose harms count. Jeffrey holds that the scientist assigns probabilities and the person who acts weighs the costs.
- For the method (my inference): missing. Rule 3 gives the cost of an error to the owner but does not say whose costs: the maintainer's, the users' or third parties'. On Jeffrey's side, the standing reports the test and the perspective is stated in the decision to act (F9.1), as GRADE asks of panels.

### F9.5 Panels that read the same evidence often disagree, and GRADE handles this by publishing each panel's judgements, not by a rule that picks one.

- Answers: 4, 2
- Evidence:
  - Andrews et al. 2013 as under F9.2 — §3.3 — "Disagreement between panels is common [39e41], and disagreement may be a result of variability in judgments about the domains or of how panels synthesize those judgments."
  - Tyree and Akerman 2005, "Architecture decisions: demystifying architecture", IEEE Software 22(2) — https://personal.utdallas.edu/~chung/SA/zz-Impreso-architecture_decisions-tyree-05.pdf — full text — template field Positions — "explicitly stating other opinions helps enroll their advocates in your decision"
- Standing: one source on panel disagreement
- For the method (my inference): missing. `owner` names one person or role, so two owners' conflicting goals cannot be recorded. On question 2: different owners do reach different decisions from the same data. If the standing stays a report of the test, only the decision differs, and recording each owner's goal and values shows where.

### F9.6 Design practice records an architecture choice made under a deadline as a decision with a status and stated assumptions, and a change in those assumptions reopens it.

- Answers: 5, 8
- Evidence:
  - Tyree and Akerman 2005 as under F9.5 — template — "The decision's status, such as pending, decided, or approved."; "Clearly describe the underlying assumptions in the environment in which you're making the decision—cost, schedule, technology"; later, "If the assumptions change, a decision would have to change as well."
- Standing: one source
- For the method (my inference): keeps: rule 1. A decision whose hypothesis waits fits an architecture choice. What is missing is a link from the refutation of that hypothesis back to the decision, so a refuted premise (question 8) leaves the decision in force.

### F9.7 Regulators that admit a practice before its evidence attach a mandated test, milestones and withdrawal. Adoption weakens the incentive to run that test, and practices adopted untested often fail when tested.

- Answers: 6, 10, 18
- Evidence:
  - FDA, draft guidance "Expedited Program for Serious Conditions — Accelerated Approval of Drugs and Biologics", Dec 2024 — https://www.fda.gov/media/184120/download — full text — §II–III — conditions "may include enrollment targets, the study protocol, and milestones, including the target date of study completion"; withdrawal "(1) if the sponsor fails to conduct any required postapproval study with due diligence … (2) if a required confirmatory study fails to verify clinical benefit"
  - Fenwick et al. 2020, ISPOR VOI Task Force Report 1, Value Health 23(2):139–150 — https://ris.utwente.nl/ws/files/179932151/PIIS1098301520300279.pdf — full text — "Reimbursement and Coverage With Evidence Development Decisions" — "Use of a premature evidence base for decision making carries substantial risk and uncertainty for patient outcomes but also creates a disincentive to invest in further research"; practices "which, once adopted, are difficult to eliminate"
  - Prasad et al. 2013, "A decade of reversal", Mayo Clin Proc 88(8):790–798 — https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=23871230&rettype=abstract&retmode=text — abstract — "Of the 363 articles testing standard of care, 146 (40.2%) reversed that practice, whereas 138 (38.0%) reaffirmed it." (one journal, 2001–2010)
- Standing: two or more independent sources. (the reversal rate: one source; its use for skill rules is a transfer)
- For the method (my inference): missing. A rule in force as a decision has no term, no milestone and no default at expiry, so "decision" can become a permanent entrance (question 6). The decision record could carry a review date and say what happens when the test has not run by then.

### F9.8 Value-of-information analysis answers when a test costs more than the error it prevents, which hypothesis to test first, and how to weigh the cost of waiting.

- Answers: 7, 11, 15
- Evidence:
  - Fenwick et al. 2020 as under F9.7 — "How Can VOI Be Used?" — "VOI analysis can inform a variety of healthcare decisions including: (1) research prioritization, (2) efficient research design"; Box 4 and after — "If the population EVPI is less than the estimated cost of research, this provides a sufficient condition for establishing that future research is not of value to the decision maker. In this circumstance, the VOI process should stop."; "the gain from waiting for more evidence (in terms of reduced uncertainty) should be weighed against the losses associated with a delay in adopting the technology"
  - Claxton 1999 as under F9.1 — abstract — research "is designed efficiently"
- Standing: one source (one tradition: a task-force consensus built on Claxton)
- For the method (my inference): missing. Rule 3 sets the number of repetitions by the cost of an error. It does not say when a test is not worth running, which entry of a long waiting list goes first, or what delay costs. A decision record of the form "left untested: expected loss below the cost of the test", with its figures, would carry this. The computation belongs to decision analysis.

### F9.9 Active adaptive management adopts actions for what they teach and openly postpones its objectives to do so, and its preconditions include being able to adjust the action.

- Answers: 18, 13
- Evidence:
  - Williams, Szaro and Shapiro 2009, DOI "Adaptive Management" technical guide — https://www.doi.gov/sites/default/files/uploads/TechGuide-WebOptimized-2.pdf — full text — "Active adaptive management" — "Decision making involves the active pursuit of learning"; "contributions to resource objectives are temporarily postponed so that understanding can be attained as quickly as possible"; checklist — "No – adaptive management is not possible without the flexibility to adjust management strategies."
- Standing: one source
- For the method (my inference): missing. Putting a rule in force in order to test it fits rule 3, since it is an intervention, but the acceptance path has no branch for it, and the record has no place for what is traded for the information. Reversibility, the guide's precondition, is never named in method.md.

### F9.10 For catastrophic or irreversible outcomes, maximising expected utility is itself contested, and precautionary and regret rules compete with it.

- Answers: 13, 15, 16
- Evidence:
  - SEP "Decision Theory" (rev. 20 Aug 2025) — https://plato.stanford.edu/entries/decision-theory/ — full text — §5.3 — "The standard approach in economics and policy analysis is to use expected utility theory to decide in the face of catastrophic risks"; "There is disagreement on what type of principle the precautionary principle is."
  - Manski 2019 as under F9.1 — abstract — "as-if maximin and minimax-regret decisions"
- Standing: disputed. One side applies expected utility to every risk; the other uses precautionary or regret rules under severe uncertainty. They differ on whether probabilities can be assigned and whether a catastrophe can be weighed against an ordinary loss.
- For the method (my inference): needs another procedure for decisions with irreversible harm or unknown probabilities. method.md should name these as outside the acceptance path, and not leave them silently to "the owner's word".

### F9.11 Product experimentation treats an experiment as one input to a launch decision, and its 2026 literature finds that "no significant harm" is often misread as "harmless".

- Answers: 12; frontier 3
- Evidence:
  - Kohavi, Tang and Xu 2020, *Trustworthy Online Controlled Experiments*, ch. 1 — https://experimentguide.com/wp-content/uploads/TrustworthyOnlineControlledExperiments_PracticalGuideToABTesting_Chapter1.pdf — full text of the chapter — "a decision should be made with many sources of data, including controlled experiments, surveys, estimates of maintenance costs for the new code"
  - Alcain et al. (Meta) 2026, "Neutral Is Not Free" — https://arxiv.org/pdf/2610.10223 — full text — §1 — the confidence-interval overlap rule "conflates the absence of evidence with evidence of harmlessness" and is "dangerously permissive when data is scarce"
- Standing: two or more independent sources
- For the method (my inference): needs another procedure for product launches. "Supported" does not mean "ship it" (F9.1), and a claim of no harm takes, as its refuter, a harm margin fixed beforehand. The `threshold` field could hold that margin, and rule 2 could say so.

## Open questions

- Question 8, on burden: when a classification is challenged, does the challenger or the owner carry the burden? I searched no further than the SEP "Decision Theory" §5.3 material on precaution, which addresses decision rules, not burden of proof.
- Question 9: whether a "taste" recorded under the owner's name hides a claim a test would fail. I made no search beyond the inductive-risk material of F9.4, which does not address it.
- Question 10, as behaviour: reluctance to run the arm without a rule that is working. F9.7 gives the reversal rate and the disincentive at the level of the system, but no measure of individual reluctance.
- How agent and prompt evaluation separates an evaluation result from a deployment decision. One arXiv search (2025–2026) returned adjacent papers (arXiv 2608.08709, 2604.03216); none opened.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| Claxton, The irrelevance of inference | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=10537899&rettype=abstract&retmode=text | abstract | 1999 |
| Manski, Statistical inference for statistical decisions | https://arxiv.org/pdf/1909.06853 | full text | Sept 2019 |
| Manski, Systemic methodological dysfunction | https://arxiv.org/pdf/2607.23660 | full text | July 2026 |
| ASA Statement on p-values | https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf | full text | 2016 |
| Guyatt et al., GRADE: going from evidence to recommendations | https://www.cebma.org/assets/Uploads/Guyatt-From-evidence-to-recommendations-BMJ_2008.pdf | full text | May 2008 |
| Andrews et al., GRADE guidelines 15 | https://www.eu-patient.eu/contentassets/09e1058baccc4310ab0775353836c830/grade-guidelines_15_going-from-evidence-to-recommendation.pdf | full text | 2013 |
| Alexander et al., WHO strong recommendations | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=25618534&rettype=abstract&retmode=text | abstract | 2016 |
| Rudner, The scientist qua scientist | https://www.joelvelasco.net/teaching/3330/rudner53-quascientist.pdf | full text | 1953 |
| Lakens et al., Justify your alpha | https://eprints.whiterose.ac.uk/128599/8/Justify%20Your%20Alpha.pdf | full text (manuscript) | 2018 |
| Mudge et al., Setting an optimal α | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=22389720&rettype=abstract&retmode=text | abstract | 2012 |
| SEP, Scientific Objectivity | https://plato.stanford.edu/entries/scientific-objectivity/ | full text | rev. 30 Oct 2020 |
| SEP, Decision Theory | https://plato.stanford.edu/entries/decision-theory/ | full text | rev. 20 Aug 2025 |
| SEP, Scientific Method | https://plato.stanford.edu/entries/scientific-method/ | full text | rev. 8 Aug 2026 |
| Tyree and Akerman, Architecture decisions | https://personal.utdallas.edu/~chung/SA/zz-Impreso-architecture_decisions-tyree-05.pdf | full text | 2005 |
| FDA, Accelerated Approval draft guidance | https://www.fda.gov/media/184120/download | full text | Dec 2024, draft |
| Fenwick et al., ISPOR VOI Report 1 | https://ris.utwente.nl/ws/files/179932151/PIIS1098301520300279.pdf | full text | 2020 |
| Prasad et al., A decade of reversal | https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=23871230&rettype=abstract&retmode=text | abstract | 2013 |
| Williams, Szaro, Shapiro, Adaptive Management guide | https://www.doi.gov/sites/default/files/uploads/TechGuide-WebOptimized-2.pdf | full text | 2009 ed., updated |
| Kohavi, Tang, Xu, ch. 1 | https://experimentguide.com/wp-content/uploads/TrustworthyOnlineControlledExperiments_PracticalGuideToABTesting_Chapter1.pdf | full text of chapter 1 | 2020 |
| Alcain et al., Neutral Is Not Free | https://arxiv.org/pdf/2610.10223 | full text | 7 Oct 2026 |

<!-- COMPLETE -->
