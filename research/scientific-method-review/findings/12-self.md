# Cluster 12 — The method applied to itself: track record and running cost

## Findings

### F12.1 Of about 1,355 rule lines, 6 stand as supported claims, all six on tests of the repository's own; none stands on an opened external source, and 1,326 carry no record

- Answers: 2; frontier 2
- Evidence:
  - repository — `check_record.py --stats` — full text — output — "records by kind: claim 10, decision 17, definition 2, norm 0" / "claims by standing: contested 0, hypothesis 4, law 0, refuted 0, supported 6" / "rule lines without a record: 1326"
  - repository — both `maintenance/pending-evidence.md` files — full text — ten hypotheses (scientific-method H-01, H-02; auditing-ai-context H-01 to H-08); seven met a test that could refute them (scientific-method H-02, auditing-ai-context H-01 to H-06); auditing-ai-context H-07: "no test of this line exists yet"; every claim's `test` is `own`
  - repository — `git log` — 8 commits from `fa0bdaf` to `07c81e8`; S-2 states "commit dates are set by hand here", so no rate per unit of time is readable
- Standing: `two or more independent sources` (script count and file reading agree)
- For the method (my inference): `missing` — method.md gives no standing to the 1,326 lines that predate it, although an opinion "stays out of the rules" and NORECORD fires only on changed lines, so the share of rules resting on opinion cannot be counted.

### F12.2 Six of seven tested claims passed and none is refuted, while preregistered tests elsewhere fail about half the time

- Answers: 3; frontier 2
- Evidence:
  - Scheel, Schijen, Lakens 2021, "An excess of positive results" — https://osf.io/download/p6e9c/ — full text (author copy) — abstract — "we found 96% positive results in standard reports, but only 44% positive results in Registered Reports"; Discussion — "Registered Reports may be used for particularly risky hypotheses"
  - Allen and Mehler 2019, "Open science challenges, benefits and tips..." (PLoS Biology) — https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3000246&type=printable — full text — section on Registered Reports — "60.5% (see Fig 1) were not supported by the experimental data"; "in stark contrast to the estimated 5% to 20% of null findings in the traditional literature"
  - Kaplan and Irvin 2015, PLoS ONE — https://journals.plos.org/plosone/article/file?type=printable&id=10.1371/journal.pone.0132382 — full text — Discussion — "17 out of 30 (57%) reported significant benefit for their primary outcome"; "only 2 of 25 trials (8%) reported a significant benefit"
  - repository — auditing-ai-context H-06 — "went against the claim" (0.04 under a threshold of 0.15), the one failed run on record
- Standing: `two or more independent sources` for the failure rate under registration; applying it here is `my inference`
- For the method (my inference): `missing` — with registration (S-2) ruling out publication bias, the remaining explanations Scheel et al. name are hypotheses with a high prior (here formed after a pilot, `83f07f3`, and "a dry case", `97a86d6`) and the author's thresholds, so rule 3 should have the record state what the pilot showed beside the threshold.

### F12.3 The record check guards a failed result only once the standing is refuted or contested, so a hypothesis with one failed run can be deleted without a finding

- Answers: 3, 6
- Evidence:
  - repository — `references/record-format.md` § Findings of the record check — full text — "`ERASED` | an id whose record at the base revision had the standing `refuted` or `contested` and whose line is gone from its directory"; `PREDICTION` covers only "a claim with an `own` test and a standing other than `hypothesis`"
  - Claesen et al. 2021, "Comparing dream to reality" (R. Soc. Open Sci.) — https://pmc.ncbi.nlm.nih.gov/articles/PMC8548785/ — full text — abstract — "Two out of 27 preregistered studies contained no deviations from the preregistration plan."; "Nine studies disclosed none of the deviations."
- Standing: `one source`; the gap is read from the table, not run
- For the method (my inference): `missing` — rule 7 says a test that went against the claim "stays recorded", yet the script leaves H-06 (one failure, waiting) unguarded, and Claesen et al. show that registration without someone comparing plan and report misses deviations, so ERASED should cover any record whose `result` reports a run.

### F12.4 A script checks the form of the record; the substance of rules 2, 3, 5 and 7 rests on a model reader

- Answers: 6
- Evidence:
  - repository — `scripts/check_record.py` docstring — full text — codes "KIND, FIELD, STANDING, TEST, SUPPORT, OWN, FIT and DUP", plus PREDICTION, ERASED, NORECORD: presence, vocabulary, path existence, commit order
  - Claesen et al. 2021 — as in F12.3 — deviations were found by reading the plan beside the article
- Standing: `my inference`
- For the method (my inference): `keeps: rule 4` — S-5 requires an independent reader; method.md line 117 should say that severity, the match of bounds to use, and what a failure refutes are judged by that reader alone.

### F12.5 Testing the method by its own standard is a recognised but disputed position, and "withdrawn less often" alone points the wrong way

- Answers: 7, 8, 9, 10, 11; frontier 2
- Evidence:
  - Luetge, "Naturalized Philosophy of Science and Economic Method", 20th World Congress of Philosophy — https://www.bu.edu/wcp/Papers/Scie/ScieLuet.htm — full text; Laudan seen secondary through it — "categorical imperatives, but rather as hypothetical imperatives"; "We can actually investigate empirically whether certain rules lead to the attainment of the desired ends."
  - Knowles 2002, "What's really wrong with Laudan's normative naturalism" — https://api.openalex.org/works/doi:10.1080/02698590220145106 — abstract — "its conception of methodological rules--as hypothetical imperatives linking cognitive means to ends--is untenable"
  - SEP "Imre Lakatos" — https://plato.stanford.edu/entries/lakatos/ — full text — §3.5 — "naïve versions of Popper’s falsificationism are in a sense falsified by the history of science"
  - Kaplan and Irvin 2015 — as in F12.2 — "We cannot say that trend toward null trials to preregistration in ClinicalTrials.gov is causal."
  - repository — scientific-method H-01: "against: none"; method.md rule 3: "A claim about the benefit of a technique takes a comparison with the same work done without the technique"; before `fa0bdaf`, 49 commits, 5 `fix(` and none whose subject names a withdrawal
- Standing: `disputed: Laudan holds that a methodological rule is a means–ends claim open to empirical test; Knowles holds that such rules are not rules and that the means/ends split is ill-founded; Lakatos judges a methodology by the history of science`
- For the method (my inference): `the text says otherwise` — line 16 ("They hold what the main lines of the philosophy of science share") and H-01 are claims by the method's own table, H-01 lacks the comparison rule 3 demands, and since a working method raises early failures (F12.2), a self-test should register both the failure share of tests and the withdrawal share of rules against a before/after arm.

### F12.6 Repetitions are budgeted by the cost of an error, not by the cost of the test, and no run records its own cost

- Answers: 13, 14, 15
- Evidence:
  - Lakens 2022, "Sample Size Justification" (Collabra: Psychology) — https://osf.io/download/9d3yf/ — full text (author copy) — § Resource Constraints — "Resource constraint justifications are based on a trade-off between the costs of data collection, and the value of having access to the information the data provides."; "researchers are confronted with an optimization problem of how to spend resources across multiple research questions."
  - Kapoor et al. 2024, "AI Agents That Matter" — https://arxiv.org/pdf/2407.01502 — full text (v1) — §2 heading — "AI agent evaluations must be cost-controlled"
  - repository — `auditing-ai-context/evals/absent-rule/runs/run-1/notes.md` — about 158 agents in one run (12 writers, 12 checkers, 36 reviewers, 2 × 48 card sub-agents, 2 indexers) plus 18 reader verdicts; `07c81e8`: "67 sub-agents over five files"; no cost field in `record-format.md`, no tokens or time in the notes
- Standing: `two or more independent sources`
- For the method (my inference): `missing` — rule 3 should weigh the cost of the test beside the cost of an error, because once hypotheses outgrow a fixed budget the repetitions per claim follow from the allocation across the whole list, which only a cost line in each record would let anyone audit.

### F12.7 GRADE separates certainty of evidence from strength of recommendation and downgrades for reporting bias; the method has the first split, not the second

- Answers: 14, 17
- Evidence:
  - Guyatt et al. 2008, "GRADE: an emerging consensus on rating quality of evidence and strength of recommendations" (BMJ) — https://pmc.ncbi.nlm.nih.gov/articles/PMC2335261/ — full text — "Evidence based on randomised controlled trials begins as high quality evidence, but our confidence in the evidence may be decreased for several reasons, including: Study limitations Inconsistency of results Indirectness of evidence Imprecision Reporting bias."; Box 1 — "Explicit acknowledgment of values and preferences"
- Standing: `one source`
- For the method (my inference): `missing` — the decision "in force" while its hypothesis waits plays GRADE's recommendation on low certainty, which answers question 14 (a cheap, reversible rule may enter on low certainty), but rule 4 accepts an opened external test with nothing like GRADE's checks for reporting bias and inconsistency.

### F12.8 Assurance cases measure confidence by the doubts eliminated and name a defeater of the inference, which the check questions do not list

- Answers: 17
- Evidence:
  - Goodenough, Weinstock, Klein 2013, "Eliminative Induction: A Basis for Arguing System Confidence" (SEI) — https://www.sei.cmu.edu/documents/1426/2013_021_001_88010.pdf — full text — abstract — "we use the principle of eliminative induction to provide a justified basis for assessing how much confidence one should have in an assurance case argument"; §II — "There are only three types of defeaters: rebutting, undermining, and undercutting."
- Standing: `one source`
- For the method (my inference): `needs another procedure for engineering and design assurance` — rule 3 covers rebutting and undermining evidence, but the undercutting defeater (true premises that do not license the conclusion) and residual doubts serve decisions that cannot wait for a repeatable test.

### F12.9 One traced acceptance: the trace pass entered as the owner's decision after its comparison with the cheaper technique failed its one run

- Answers: 4, 5, 1
- Evidence:
  - repository — `git log` — `97a86d6` registers H-01 to H-07; `f708cac`: "H-06 keeps the standing of a hypothesis with one failed run recorded"; `07c81e8`: "the trace pass enters the audit as a step, by its owner's decision"
  - repository — `auditing-ai-context/maintenance/skill-provenance.md`, line `SKILL.md § Trace pass` — "H-06, the comparison with the audit's cards given the statements a change deleted, failed its one run on generated notes" · "kind: decision"
- Standing: `my inference` (on repository facts)
- For the method (my inference): `missing` — method.md line 115 lets a rule enter as a decision "before its test exists" but says nothing of a decision taken after the comparative test went against it, so the path should require such a decision to name the failed hypothesis and its own reason (the record here did both, by choice).

### F12.10 Records stay out of what an agent loads, which matches evidence that models use long contexts poorly

- Answers: 16
- Evidence:
  - repository — `scientific-method/maintenance/README.md` — first paragraph — "Nothing under `maintenance/` is read or executed in a run of the skill."
  - Liu et al., "Lost in the Middle" (TACL 2024; arXiv v3 2023) — https://arxiv.org/pdf/2307.03172 — full text — abstract — "performance can degrade significantly when changing the position of relevant information"
- Standing: `one source` (2023 models; I have not checked current ones)
- For the method (my inference): `keeps: rule 7` — the archive grows outside the loaded context, but only the maintenance README says so; method.md should carry it.

### F12.11 A fast-moving field is re-searched on a cycle set by decision needs, the pace of evidence and feasibility, commonly monthly; the record has no re-test term

- Answers: 19
- Evidence:
  - Cochrane Handbook v6.5.1, Chapter 21 — https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-21 — full text — §21.2.2 — "The frequency with which new evidence should be sought for each LSR should be determined by considering the needs of decision-makers, the expected frequency of publication of new evidence, and feasibility. LSRs commonly use a monthly review cycle"; "An LSR is appropriate when the research field is moving quickly and new evidence is likely to impact on review conclusions."
  - Cochrane 2019, living systematic review guidance — https://resources.cochrane.org/sites/resources.cochrane.org/files/uploads/inline-files/Transform/201912_LSR_Revised_Guidance.pdf — full text — "LSRs include active, ongoing evidence surveillance (i.e. monthly searches and monitoring of"
- Standing: `one source` (two documents of one body)
- For the method (my inference): `missing` — `record-format.md` has no field saying when a scan or test is due again, and by this norm the map's field scan would repeat monthly while the area moves fast.

### F12.12 By the method's own table, a model-generated coverage map is an origin of hypotheses, not a finding

- Answers: 18
- Evidence:
  - repository — `references/method.md` — opening: "a paper, practice, a model and one's own guess are equal as origins"; rule 6: "The observation a hypothesis grew from is its origin, and a later observation is its test."
- Standing: `my inference`
- For the method (my inference): `keeps: rule 6` — a question of the map holds no standing until a measure and a refuter are attached to it.

## Open questions

- 1 (which past errors the seven questions would have caught) — commit subjects before `fa0bdaf` (49, 5 `fix(`) name no withdrawal; without a record of withdrawn rules this needs a diff-by-diff reading beyond the budget
- 2, tail (who would be embarrassed by a published share) — not searched; the files do not answer it.
- 12 (provenance tracking or review culture alone) — my searches found no study comparing review-only with test-based admission.
- 4 (process tracing or ethnography as a method of study) — not searched; F12.9 is one trace only.

## Sources opened

| Source | URL | How seen | Date or version of the source |
|--|--|--|--|
| Scheel et al. | https://osf.io/download/p6e9c/ | full text | 2021 (AMPPS 4(2)) |
| Allen, Mehler | https://journals.plos.org/plosbiology/article/file?id=10.1371/journal.pbio.3000246&type=printable | full text | 2019 |
| Kaplan, Irvin | https://journals.plos.org/plosone/article/file?type=printable&id=10.1371/journal.pone.0132382 | full text | 2015 |
| Claesen et al. | https://pmc.ncbi.nlm.nih.gov/articles/PMC8548785/ | full text | 2021 |
| Luetge | https://www.bu.edu/wcp/Papers/Scie/ScieLuet.htm | full text | 20th WCP (year: recall, not opened) |
| Knowles | https://api.openalex.org/works/doi:10.1080/02698590220145106 | abstract | 2002 |
| SEP, Imre Lakatos | https://plato.stanford.edu/entries/lakatos/ | full text | rev. 2026-06-19 |
| Lakens | https://osf.io/download/9d3yf/ | full text | 2022 |
| Kapoor et al. | https://arxiv.org/pdf/2407.01502 | full text | v1, 2024-07-01 |
| Guyatt et al. (GRADE) | https://pmc.ncbi.nlm.nih.gov/articles/PMC2335261/ | full text | 2008 |
| Goodenough et al. | https://www.sei.cmu.edu/documents/1426/2013_021_001_88010.pdf | full text | 2013 |
| Liu et al. | https://arxiv.org/pdf/2307.03172 | full text | v3, 2023-11-20 |
| Cochrane Handbook, Chapter 21 | https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-21 | full text | v6.5.1, 2026 |
| Cochrane LSR guidance | https://resources.cochrane.org/sites/resources.cochrane.org/files/uploads/inline-files/Transform/201912_LSR_Revised_Guidance.pdf | full text | 2019-12 |

<!-- COMPLETE -->
