# Cluster 6 — Pre-recording, exploration and fitting

## Findings

### F6.1 Rule 6's sources make pre-recording public, dated and frozen; the method says "recorded before", and S-2 orders commits in a history its author can rewrite

- Answers: 1, 2
- Evidence:
  - Fidler & Wilcox 2018, SEP "Reproducibility of Scientific Results" §4.2 (cited by M-6) — https://plato.stanford.edu/entries/scientific-reproducibility/ — full text — "pre-registration involves making a public, date-stamped statement of predictions and/or hypotheses"
  - Nelson, Simmons, Simonsohn 2018, Annu. Rev. Psychol. — https://faculty.wharton.upenn.edu/wp-content/uploads/2017/05/Nelson-Simmons-Simonsohn-2018.pdf — full text — section Preregistration — "Preregistrations are time-stamped plans for data analysis written before any data are analyzed."
  - OSF Support, Registrations — https://help.osf.io/article/330-welcome-to-registrations — full text — "A registration is a frozen version of your project that can never be edited or deleted"
  - local `man git-commit`, git 2.54.0 — full text — `GIT_COMMITTER_DATE` sets a commit's date by hand
- Standing: two or more independent sources
- For the method (my inference): the text says otherwise — rule 6 drops "public" and "dated" from its source; method.md should name what counts as recorded (a commit another party holds, a third-party registration) or call ancestry a chosen, weaker substitute.

### F6.2 Author-designed, partly reported plans buy little: plain preregistration showed no fall in positive results, result-blind review a large one

- Answers: 6, 7
- Evidence:
  - Little, Montgomery, Schnakenberg 2026, "Preregistration as Cheap Talk" — https://osf.io/preprints/socarxiv/v7cgj_v1 — full text — abstract: "preregistration — when researchers control plan design — can produce higher false positive rates than an unrestrictive plan"; discussion: "Preregistered analyses should be specified clearly, kept few, followed closely, and reported completely."
  - van den Akker et al. 2024, Behav. Res. Methods — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11335781/ — full text — abstract: "we did not find that preregistered studies had a lower proportion of positive results"
  - Scheel, Schijen, Lakens 2021, AMPPS — https://research.tue.nl/en/publications/an-excess-of-positive-results-comparing-the-standard-psychology-l-2/ — abstract — "we found 96% positive results in standard reports but only 44% positive results in RRs"
  - Simmons, Nelson, Simonsohn 2020, "Pre-registration: Why and How" — https://people.duke.edu/~jch8/bio/Papers/J%20Consum%20Psychol%20-%202020%20-%20Simmons%20-%20Pre%E2%80%90registration%20%20Why%20and%20How.pdf — full text — "How to Review a Pre-registration" — "Pre-registration can only work to reduce p-hacking if those pre-registrations are followed."
- Standing: two or more independent sources; the RR cause is my inference
- For the method (my inference): missing — the PREDICTION check freezes measure, comparison, scope, refuter and threshold, not the analysis (exclusions, scoring script), and no reader sees the hypothesis before its result. A registered-report analogue: the reader's verdict and the scoring script's hash go into the registering commit.

### F6.3 A reader cannot confirm "every run" from an author-curated record; 2026 proposals move the record into the harness

- Answers: 2, 16
- Evidence:
  - Vaccaro 2026, arXiv 2606.11217 — https://arxiv.org/pdf/2606.11217 — full text — §4.2: "how many prompt iterations were explored"; §4.6: "we encourage archiving complete input–output logs"
  - Bisht et al. 2026, arXiv 2605.08956v3 — https://arxiv.org/pdf/2605.08956 — full text — "register hypotheses in a structured, machine-readable repository before any simulation or automated laboratory test is initiated"
- Standing: two or more independent sources (proposals, untested)
- For the method (my inference): missing — "the record holds every run" binds only the author's honesty; a log the harness writes per invocation would let a third party count runs.

### F6.4 Trials and agent benchmarks report runs lost to the apparatus apart from outcomes, with reasons; the record format has no run status

- Answers: 3
- Evidence:
  - Hopewell et al. 2025, CONSORT 2025 E&E — https://pmc.ncbi.nlm.nih.gov/articles/PMC11995452/ — full text — item 22b: "For each group, losses and exclusions after randomisation, together with reasons"; 23b: "If relevant, why the trial ended or was stopped"
  - Group of Skills, arXiv 2605.06978v2, App. E.8 — https://arxiv.org/pdf/2605.06978 — full text — infrastructure-failure runs "are excluded from aggregate reward, token, and runtime computation and are not imputed"; "agent timeouts are retained as valid task-level outcomes"
  - Dastidar et al. 2026, arXiv 2607.17044v1 — https://arxiv.org/pdf/2607.17044v1 — full text — "a SpreadsheetBench run interrupted by API downtime and its completed re-run disagreed on 11 of 400 tasks (10 attributable to the infrastructure failures)"
- Standing: two or more independent sources
- For the method (my inference): missing — `result` needs a run status (`completed`, `aborted: <reason>`), with the rule sorting outcomes (timeout a failure, outage not) recorded before the test; an aborted run moves no standing.

### F6.5 Rerunning a model-based test needs the exact model id, access date, settings, prompts, code and archived outputs

- Answers: 4
- Evidence:
  - Vaccaro 2026 §4.1 — https://arxiv.org/pdf/2606.11217 — full text — "Researchers specify exact model identifiers and version checkpoints"; "include the API version and access date"
  - Biderman et al., arXiv 2405.14782v3 — https://arxiv.org/pdf/2405.14782 — full text — "Always share your exact prompts."
  - Atil et al. 2024 — https://arxiv.org/pdf/2408.04667 — full text — "We see accuracy variations up to 15% across naturally occurring runs"
- Standing: two or more independent sources
- For the method (my inference): missing — `scope` and `bounds` are free text; a model-run test should require model id, access date, decoding settings, budget, harness commit and case-set hash, and archived outputs, without which a failed rerun cannot tell refutation from drift.

### F6.6 Rule 6 restates de Groot (1956) nearly clause by clause; its provenance reaches him only through later texts

- Answers: 8
- Evidence:
  - de Groot 1956/2014, trans. Wagenmakers et al., Acta Psychologica 148 — https://www.ejwagenmakers.com/inpress/DeGroot1956_TA.pdf — full text — PDF p. 2: the testing procedure must "have been registered in advance"; PDF p. 3: "it is not allowed to “adjust” this threshold to the findings"; PDF p. 1: tests in exploratory research "do not have evidential impact"
  - method-provenance.md M-6 (opened) cites SEP popper, lakatos, scientific-reproducibility and Mayo; a grep of the skill's files finds no de Groot.
- Standing: one source, plus my repository check
- For the method (my inference): keeps: rule 6 — but M-6 should cite de Groot 1956, whose split, not only its later form, rule 6 inherits. Greenwald and Meehl: not checked.

### F6.7 The literature gives exploration reporting rules; the method gives it no record and no standing

- Answers: 9, 10
- Evidence:
  - Scheel, Tiokhin, Isager, Lakens 2021 (preprint) — https://osf.io/preprints/psyarxiv/vekpu_v1 — full text — "we believe the confirmatory-exploratory distinction to be a false dichotomy"
  - Devezer et al. 2021, RSOS §4 — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8101540/ — full text — "it may not be possible to derive some minimum standards all exploratory studies need to meet"
  - Vaccaro 2026 §4.3 — https://arxiv.org/pdf/2606.11217 — full text — "Researchers declare which analyses are hypothesis-testing (confirmatory) versus hypothesisgenerating (exploratory), and commit to reporting each as such."
- Standing: two or more independent sources that exploration must be labelled; disputed whether it can meet a standard (Devezer et al.: perhaps not)
- For the method (my inference): missing — pilots, trace analyses and prompt iterations have no place in the record; an origin record without standing (what was looked at, variants tried, what was seen) would admit them as declared origins, never as tests.

### F6.8 "Origin, then a later observation as test" is a use-novelty rule; its necessity is disputed, and severity is what it serves

- Answers: 11, 12
- Evidence:
  - Barnes, SEP "Prediction versus Accommodation" §6.4 — https://plato.stanford.edu/entries/prediction-accommodation/ — full text — "Here novelty and severity appear to coincide—but Mayo observes that there are cases in which they come apart."
  - Devezer et al. 2021 §3 — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8101540/ — full text — "one can use the data many times in a valid statistical procedure"; "The problem arises if proper conditioning on prior information or decisions is skipped."
  - Rubin 2020 — https://arxiv.org/pdf/2010.10513 — full text — the time at which hypotheses are deduced from a priori theory "does not affect the credibility of hypothesis tests"
  - against: Simmons et al. 2020 — "will almost inevitably end in p-hacking"; de Groot as in F6.6
- Standing: disputed: inspiring data cannot test (de Groot, Simmons et al.) versus reuse is valid when inference conditions on the selection (Mayo per SEP, Devezer et al., Rubin); the latter needs the selection stated formally.
- For the method (my inference): over-strict, cheaply so where fresh runs are cheap (agent tests), costly for one-off incidents and appraisal. Rule 6 could admit a post-hoc claim on its own data when a procedure accounts for the selection (conditioning, a held-out set), and let rule 3 decide.

### F6.9 Sequential and adaptive designs keep error control by fixing the procedure in advance rather than the sample size

- Answers: 10, 12, 16
- Evidence:
  - Johari, Pekelis, Walsh, arXiv 1512.04922v3 — https://arxiv.org/pdf/1512.04922 — full text — p-values and intervals "are wholly unreliable if users endogenously choose samples sizes by continuously monitoring their tests"
  - Huang et al. 2025, arXiv 2502.09858 — https://arxiv.org/pdf/2502.09858 — full text — "A novel sequential testing framework ensures strict Type-I error control"
  - Dwork et al. 2015, arXiv 1506.02629 — https://arxiv.org/pdf/1506.02629 — full text — "Reusing a holdout set adaptively multiple times can easily lead to overfitting to the holdout set itself."
- Standing: two or more independent sources
- For the method (my inference): missing — rule 6 reads as a fixed design; for product experiments, prompt tuning and agent loops the stopping rule or error-control procedure, and a held-out case set tuning never touches, are what is recorded first. method.md should say so.

### F6.10 The saving-condition clause is Lakatos's theoretical progress; the acceptance path supplies empirical progress; M-6 credits him

- Answers: 14
- Evidence:
  - Musgrave & Pigden, SEP "Imre Lakatos" (rev. 19 Jun 2026) — https://plato.stanford.edu/entries/lakatos/ — full text — "it must predict novel and hitherto unexpected facts"; "Secondly it must be empirically progressive."
  - M-6 cites SEP lakatos §2.2; its quote "all cooked up after the event" stands in the 2026 revision.
- Standing: one source
- For the method (my inference): keeps: rule 6 — "predicts something new" is the first condition; "is itself a hypothesis" sends it down the acceptance path, which supplies the second.

### F6.11 Pre-recording guards a test, not the making of a hypothesis worth testing

- Answers: 13
- Evidence:
  - Szollosi et al. 2020 (preprint) — https://osf.io/preprints/psyarxiv/x36pz_v1 — full text — "statistical problems become irrelevant because theories, not random selection, dictate what comparisons are necessary"
  - Scheel et al. 2021, as in F6.7 — "Forcing researchers to prematurely test hypotheses" without a sound derivation chain "is counterproductive."
- Standing: disputed: redundant under good theory (Szollosi et al.) versus needed for transparency (Simmons et al. 2020; Nelson et al. 2018)
- For the method (my inference): keeps: rule 6 — it blocks fitting only; groundwork (valid measure, named auxiliaries) belongs with rule 2.

### F6.12 Others' unseen runs cannot be checked; the sources offer disclosure items or result-blind formats instead

- Answers: 15
- Evidence:
  - Simonsohn 2016, Data Colada [55] — https://datacolada.org/55 — full text — "authors disclose how sample size was set & all measures, conditions, and exclusions"; registries "fall short of fixing an inconsequential problem, the file-drawer"
  - Scheel, Schijen, Lakens 2021, as in F6.2 — "the reduction of publication bias and/or Type I error inflation in the RR literature"
- Standing: disputed: Simonsohn holds that dropped whole studies are rare and disclosure suffices; the RR comparison points to large underreporting. Their units differ: analyses versus studies.
- For the method (my inference): missing — rule 4 asks for comparison, measure, sample and result only; adding how the sample size was set, whether all measures, conditions and exclusions are reported, and whether the study was registered would carry rule 6 to external tests.

### F6.13 A moved record keeps its history in the record check; a lost record of a supported rule is caught only under `--require`

- Answers: 5
- Evidence:
  - record-format.md, "Findings of the record check" (opened) — "A map that git reports as renamed is compared with its text under the earlier name"; `ERASED` covers only an id whose record "had the standing `refuted` or `contested`"; `NORECORD` fires "under `--require`, or on an added or changed line".
- Standing: my inference; the script was not run
- For the method (my inference): missing — method.md is silent on where records live; a rule whose record is lost could fall back to a decision.

## Open questions

- Which audit standard sets retention and tamper evidence for run logs (Q2)? — not searched within budget; candidates: RFC 3161, ICH E6, ISO/IEC 17025.
- At what run volume does a human-readable record become unenforceable (Q16)? — Bisht et al. and Vaccaro give no threshold; PNAS 2026 "The more you automate, the less you see" did not download as text.
- Choi 2024, "Preregistration and predictivism" (Synthese), for Q11 — login redirect, no abstract on Crossref; not opened.

## Sources opened

| Source | URL | How seen | Date or version |
|--|--|--|--|
| SEP Reproducibility | https://plato.stanford.edu/entries/scientific-reproducibility/ | full text | 3 Dec 2018, older than the 2019–2026 evidence |
| SEP Prediction vs Accommodation | https://plato.stanford.edu/entries/prediction-accommodation/ | full text | rev. 23 Sep 2022 |
| SEP Lakatos | https://plato.stanford.edu/entries/lakatos/ | full text | rev. 19 Jun 2026 |
| de Groot 1956/2014 | https://www.ejwagenmakers.com/inpress/DeGroot1956_TA.pdf | full text | in-press PDF, 2014 |
| Devezer et al. | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8101540/ | full text | 2021 |
| Rubin | https://arxiv.org/pdf/2010.10513 | full text | 2020 |
| Scheel, Tiokhin et al. | https://osf.io/preprints/psyarxiv/vekpu_v1 | full text, preprint | 2020 |
| Szollosi et al. | https://osf.io/preprints/psyarxiv/x36pz_v1 | full text, preprint | 2019 |
| Scheel, Schijen, Lakens | https://research.tue.nl/en/publications/an-excess-of-positive-results-comparing-the-standard-psychology-l-2/ | abstract | 2021 |
| van den Akker et al. | https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11335781/ | full text | 2024 |
| Little et al. | https://osf.io/preprints/socarxiv/v7cgj_v1 | full text | 20 Oct 2026 |
| Simmons et al. | https://people.duke.edu/~jch8/bio/Papers/J%20Consum%20Psychol%20-%202020%20-%20Simmons%20-%20Pre%E2%80%90registration%20%20Why%20and%20How.pdf | full text | 2020 |
| Nelson et al. | https://faculty.wharton.upenn.edu/wp-content/uploads/2017/05/Nelson-Simmons-Simonsohn-2018.pdf | full text | 2018 |
| Data Colada [55] | https://datacolada.org/55 | full text | 2016, upd. 2020 |
| OSF Registrations | https://help.osf.io/article/330-welcome-to-registrations | full text | upd. 16 Nov 2026 |
| git man pages (local) | `man git-commit` | full text | git 2.54.0 |
| Vaccaro | https://arxiv.org/pdf/2606.11217 | full text | v1, May 2026 |
| Bisht et al. | https://arxiv.org/pdf/2605.08956 | full text | v3, Nov 2026 |
| CONSORT 2025 E&E | https://pmc.ncbi.nlm.nih.gov/articles/PMC11995452/ | full text | 2025 |
| Group of Skills | https://arxiv.org/pdf/2605.06978 | full text | v2, Nov 2026 |
| Dastidar et al. | https://arxiv.org/pdf/2607.17044v1 | full text | v1, 2026 |
| Biderman et al. | https://arxiv.org/pdf/2405.14782 | full text | v3, May 2026 |
| Atil et al. | https://arxiv.org/pdf/2408.04667 | full text | 2024 |
| Johari et al. | https://arxiv.org/pdf/1512.04922 | full text | v3, 2019 |
| Huang et al. | https://arxiv.org/pdf/2502.09858 | full text | 2025 |
| Dwork et al. | https://arxiv.org/pdf/1506.02629 | full text | v2, 2015 |

<!-- COMPLETE -->
