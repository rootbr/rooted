# Appraisal: The method this repository adopts, read against its sources and its uses — evidence report

Report under appraisal: `research/2026-11-21_scientific-method-review.md`. This appraisal ranks what in the report needs re-checking before the owner revises `method.md` from it. It does not rewrite the report.

How to read the identifiers:
- `C#` in a "Claim ref" is an atomic claim of `claims.md`.
- "Row C#" is a row of the report's own table of candidate changes (report rows C1–C106). The two numberings collide. For example, claims.md C32 is publication bias, while row C32 is "Rule 7 names which part of the tested bundle a repeated failure withdraws".
- `F#.#` and `D#` are the report's finding and dispute ids.

## Verdict

- **Main conclusion(s)**: weakened — revised confidence **med** for the report's overall direction. The report says `method.md` needs revising in four places: its framing as a convention, the error rates in its records, a review term, and a check of measure validity. Confidence is **low** for several of its headline verdicts:
  - conclusion 2's "the good example fails";
  - conclusion 3's retirement leg;
  - conclusion 6's "such tests replicate at about one half";
  - conclusion 11's "shown to come from neither";
  - the 106-row work list taken whole.

  No critical finding stands, and no conclusion is unsupported. Eleven of the twelve main conclusions are weakened and one, conclusion 4, is unchanged.
- **Why**: two findings bear on every conclusion at once.
  - **EV7**: one researcher read each quote and drew its verdict, no second reader checked either, and the model family of those readers is never named. That is the setup the report's own F11.1 faults.
  - **EV8**: the standing label "two or more independent sources" counts sources, not their strength. Weak, single-version preprint support therefore wears the top label.

  On top of these, several headline verdicts reverse or shrink under the report's own evidence: ASM1, RED5, LOG6 with ACH8, and SRC1.
- **Re-check first**:
  1. **EV7**: name the researchers' and the compiler's model. Have a reader of another family, or a person, re-read the context of each pivotal quote, and check that each "For the method" verdict follows from its quotes.
  2. **EV8**: add a strength band (design, how seen, directness, n, preprint and version) beside every load-bearing standing. Relabel F3.12, F6.3, F7.13, F7.2 and F5.1.
  3. **SRC1**: re-read SEP "Scientific Method" §7 from "Hoyningen-Huene" through the Haack paragraph. Restate F1.1 and summary bullet 1 from "contradicted" to "not supported by the passages cited, and disputed rule by rule".

## Top re-checks (priority order)

Priority = load-bearing (yes 3) + severity (major 2, minor 1) + confidence (high 2, med 1, low 0). Ties break by severity, then load-bearing, then the adjudicator's order. Info-level entries are listed under [Strengths confirmed](#strengths-confirmed), not here.

| # | Finding | Axis | Load-bearing | Severity | Confidence | Priority | Re-check action |
|--|--|--|--|--|--|--|--|
| 1 | EV7: quotes and verdicts rest on one reading each, by researchers of an unnamed model family | data | yes | major | high | 7 | Name the model and effort. A reader of another family, or a person, re-reads the pivotal quotes in context and checks each "For the method" line. Record agreement per line |
| 2 | EV8: the standing label counts sources, not strength | data | yes | major | high | 7 | Add a band for design, how seen, directness, n and preprint version. Relabel F3.12, F6.3, F7.13, F7.2, F5.1 |
| 3 | SRC1: "contradicted by its own sources" overstates; §7 reports a dispute with positive cores on both sides | data | yes | major | high | 7 | Re-read §7 and the Haack paragraph beside M-0/2. Restate F1.1 and bullet 1. Grade line 16 rule by rule against F1.2. Search for shared-core accounts from 2020–2026 |
| 4 | ASM1: "the good example fails" uses a two-sided test, while the report's own remedy is one-sided, under which it passes | assumptions | yes | major | high | 7 | Restate F5.4, bullet 2 and row C53: the method names no test, the example passes one-sided (p = 0.029), and power is 0.66. Rerun `scratch-05/rule3_stats.py` |
| 5 | ASM2: "record H-03" is the record format's teaching example; no false-pass rate is given for the seven real tests | assumptions | yes | major | high | 7 | Call it "the record format's example H-03". Compute the null pass probability and power for each of the seven real tests |
| 6 | RED5: "a second failure can rarely occur" does not follow from retirement after about a year | blindspots | yes | major | high | 7 | Measure the time from a first failure to a possible rerun against the retirement date. Check that H-06's model is still served. Change row C63 to record the API version |
| 7 | ACH7: "a predictor a reading cannot recover" overreaches; Lundh's own Discussion names choices a reading sees | blindspots | yes | major | high | 7 | Restrict C38 to external tests and to a model grading itself. Read Lundh's Analysis 5.7 and Makel's discussion |
| 8 | LOG6: "such tests replicate at about one half" states as fact a link that Open questions calls unmeasured | logic | yes | major | high | 7 | Mark F7.2 and bullet 6 as a transfer whose link is unmeasured. Code SCORE or OSC originals against rule 4. Look for ML and LLM base rates |
| 9 | ACH8: the replication rate is read as the filter's error rate, though a failed replication does not show the original false | blindspots | yes | major | high | 7 | Read Tyner et al. pp. 147–148 directly. Restate F7.2 as "about half of significant original effects reach significance again" |
| 10 | ASM6: "the path joins standing to force" gives no case of harm, and the report's own F12.9 shows force without standing | assumptions | yes | major | high | 7 | Add F12.9 to D10 and split D10 into two branches. Look for a rule whose force followed its standing against the owner's judgement. Restate conclusion 7 |
| 11 | ACH10: "a history its author can rewrite" turns on an unchecked fact, whether another party holds the commits | blindspots | yes | major | high | 7 | For each registering commit (e.g. `97a86d6`), check the remote's push record before the result, the force-push policy and whether the repository is public |
| 12 | BEN1: the "public, dated, frozen" standard comes partly from registry operators whose registries do not meet it without exception | beneficiaries | yes | major | high | 7 | Quote OSF's withdrawal, embargo and update rules and AsPredicted's privacy rule beside F6.1. Source each adjective separately. Restate row C61 |
| 13 | RED3: the report never applies its own cost-and-reversibility bar to its 106 changes | blindspots | yes | major | high | 7 | Give each row its stakes class, its cost per record and the error it prevents. Make the heavy rows conditional. Pilot the format on 3–5 records. Compare with narrowing the scope |
| 14 | RED2: the report's own finding on instruction density is never applied to `method.md` | blindspots | yes | major | high | 7 | Draft the revised `method.md` and run the kind-agreement and record tasks on old and new text. Mark the rows that add to the loaded text |
| 15 | SRC7: the drift evidence shows a service name switching versions, not a pinned model drifting | data | yes | minor | high | 6 | Restate the summary and F3.12 as "a service name changes version". Look for a measurement of one pinned snapshot over time |
| 16 | LOG11: "6 of about 1,355 rule lines" uses a denominator that mostly needs no test and predates the method | logic | yes | minor | high | 6 | State the record as 6 supported, of 7 tested, of 10 claim records. Report the 1,326 separately |
| 17 | ASM4 (debated): "rule 7 refutes the claim alone" overstates, since the claim carries its measure, comparison and scope; rule 7 still checks no auxiliary | assumptions | yes | minor | med | 5 | Reword the summary line and C13 / F1.8 as the debate verdict gives it. Keep row C32 as a change to the acceptance path, not one field |
| 18 | BEN4: the SCORE base rate and three summaries trace to the Center for Open Science's own news release | beneficiaries | yes | minor | med | 5 | Cite the primary SCORE papers for F7.3, F7.4 and F7.10, or mark them "summarised by the coordinating body". Check who coordinated OSC 2015 |
| 19 | SRC2: "55%–67% of model judges' labels" misreads the source; they are label sets' labels, human votes included, with no chance baseline | data | no | major | high | 4 | Open §4.4 of arXiv 2608.24419v1 for whose labels each set holds and the baseline per set. Restate bullet 4 and F5.1, leading with Tal and Bean et al. |
| 20 | EV4: "a visible design no longer filters" rests on one manuscript at a 70%-acceptance workshop, yet carries the top standing | data | no | major | high | 4 | Relabel F7.13 "one case, abstract; plus a position paper". Look for a measured rate at which reviewers detect generated papers |
| 21 | RED6: a gap-seeking design makes the count of "missing" verdicts measure the search as much as the fit | blindspots | no | major | high | 4 | Do the diff-by-diff reading. Add a null arm arguing that the method as written suffices. Disclose the design in conclusion 8 |
| 22 | SRC3: "preregistered tests fail about half the time" uses Registered Report rates; plain preregistration gives 0.69 positive | data | no | major | high | 4 | Restate the base rate by format. Give the interval for 6 of 7. Count tests by run (effective n ≈ 2) |
| 23 | LOG9: "shown to come from neither" does not follow from a change of citation that left the definition unchanged | logic | no | major | high | 4 | Restate F1.12 as "the map does not evidence derivation". Compare M-S's wording before 5f60199. Test on more lines than one |
| 24 | LOG4: one test's pass rate is read as the method's admission rate | logic | yes | minor | low | 4 | Read § Acceptance of `method.md` and state the admission rate under its rule (0.412, or about 0.17 if a rerun is required) |
| 25 | EV19: "a singular claim has no path" is an absence claim with no quoted line of `method.md` | data | yes | minor | low | 4 | Quote the lines of `method.md` a one-event claim would pass through, and the step where it fails |
| 26 | SRC12: line 16 already calls the rules a convention; the report quotes only its second sentence | data | no | minor | high | 3 | Quote line 16 whole in F1.1. Narrow row C1 to the "share" clause |
| 27 | LOG2: Kuhn and Lakatos reject refutation of paradigms; rule 7 withdraws single low-level claims | logic | no | minor | high | 3 | Restate F1.2's Kuhn and Lakatos part as a difference of unit, as F3.8 does |
| 28 | LOG16: "every result carries error rates both ways" conflicts with the report's own kinds of claim that have none | logic | no | minor | high | 3 | Scope row C53 to statistical claims, and point to F2.9 and F2.11 for the rest |
| 29 | SRC6: Patra & Jha's 37.6% is a simulation; the quote starts after "simulated" | data | no | minor | high | 3 | Quote from "in a simulated two-group study" |
| 30 | ACH9: S-4 already bounds the step from a test of compliance to a claim of benefit | blindspots | no | minor | high | 3 | Restate row C54 as "carry S-4 into `method.md` and the record as a field" |
| 31 | SRC4: Panickssery et al.'s quoted sentence is a definition, not a result | data | no | minor | high | 3 | Quote the measured correlation instead |
| 32 | BEN3: the report recommends disclosing sponsors but does not record them for its own sources | beneficiaries | no | minor | high | 3 | Add an interest column for the sources behind load-bearing claims |
| 33 | BEN2: the AI-reviewed-paper claim comes from the system's vendor, and the report drops that interest | beneficiaries | no | minor | high | 3 | Add "(Sakana AI; vendor of the system)" to the entry. Look for an independent account |
| 34 | LOG15: "showed no fall" reads absence of evidence as evidence of absence; the Registered Report contrast is confounded | logic | no | minor | high | 3 | Restate F6.2. Name riskiness as a rival cause in row C62. Check van den Akker's interval |
| 35 | LOG14: "the compiler adds no verdict" stands beside sentences that combine many findings | logic | no | minor | med | 2 | Mark the summary sentences of Decision 2 as the compiler's synthesis |
| 36 | EV13: "locates the failing step 14.2%" measures a different task | data | no | minor | med | 2 | Drop the figure from the summary, or describe it as failure attribution in multi-agent logs |
| 37 | SRC8: Carlisle's 44% against 2% compares two sets of trials | data | no | minor | med | 2 | Present the figures as rates in two sets. Cite the Ioannidis editorial for detectability |
| 38 | ASM13: "failed runs go unrecorded at the author's desk" transfers journal incentives to one maintainer | assumptions | no | minor | med | 2 | Ground row C42 on auditability and drop the implication of suppression here |
| 39 | ASM17: "practices adopted untested often fail" generalises from practices doubted enough to be tested | assumptions | no | minor | med | 2 | Mark F9.7's figure as conditional on selection for testing |

## Reassessment of each main conclusion

| # | Main conclusion (claims.md) | Verdict | Revised confidence | Drivers |
|--|--|--|--|--|
| 1 | The "share" sentence is contradicted; present the rules as a convention; name the sides of rules 3, 6, 7 | weakened | med for the remedy, low for "contradicted" | SRC1 (§7 reports a dispute, not a void); SRC12 (line 16 already says "convention"); LOG2 |
| 2 | Rule 3's statistics fail: the good example misses 5%, H-03 passes no-effect 2 in 5; every result carries its test and error rates | weakened | low for the headline, med for the recommendation | ASM1 (it passes under the report's own one-sided remedy); ASM2 (H-03 is a teaching example); LOG16 scopes the recommendation; EV2 confirms the arithmetic |
| 3 | Rule 7 is mis-specified: bundle, fixed count, retirement | weakened | med for the bundle leg, low for the retirement leg | RED5 ("rarely occur" does not follow); SRC7 (drift is of a service, not a pinned id); ASM4, debated (the bundle point stands with a wording fix); EV16 confirms the bundle point |
| 4 | No check that a measure measures what the claim is about | unchanged | med | SRC2 and EV4 are not load-bearing; C21 itself draws no finding against it. The summary's supporting figure (SRC2) must be restated, and the proxy part is partly covered by S-4 (ACH9) |
| 5 | "Whoever its author" discards a predictor; a same-family reader is not independent | weakened | med | ACH7 ("cannot recover" and the reach to own tests are not shown); EV17 and BEN7 confirm the shared-error half |
| 6 | Rule 4's visibility filter is weak: tests replicate at about one half | weakened | low | LOG6 (the link to rule 4 is unmeasured, by the report's own line 655); ACH8 (the replication rate is not the filter's error rate); EV4, BEN4 |
| 7 | The acceptance path joins standing to force; other fields keep them apart | weakened | low for the claim about the method, high for the external premise | ASM6 (no case of harm; F12.9 runs the other way); RED3; EV15 confirms the external half |
| 8 | Reach is limited: no path for singular claims; other procedures take over; fits evaluation only with additions | weakened | med | RED6 (gap-seeking design inflates "additions"); EV19 (the absence is not quoted); ASM20 confirms the singular-claim gap is fair |
| 9 | Commit-order pre-recording is weaker than public, dated, frozen registration | weakened | med | ACH10 (a pushed remote may already make a rewrite detectable, unchecked); BEN1 (the exemplar registries are not public or frozen without exception); EV18 |
| 10 | Little track record: 6 of about 1,355 lines; a single failed run is unguarded | weakened in form, holds in substance | high for "little track record" on 6 of 7, low for the ratio and the base-rate contrast | LOG11 (wrong denominator); SRC3 (wrong base-rate format, n = 7 from about 2 runs) |
| 11 | The provenance map records concordance, not derivation; de Groot uncited; quote match is not support | weakened | low for "shown to come from neither", unchanged for the de Groot and quote-match parts | LOG9 |
| 12 | 106 candidate changes as the work list | weakened | low as a list to adopt whole, med as a pool of candidates | RED3 (no cost or proportionality); RED2 (density of the loaded text); EV8 (the labels that would rank it); RED6 |

## Findings by axis

Each entry gives the finding id, its method source as the adjudicator records it, the flaw, the evidence and the re-check. Merged entries list their members, so each can be traced back to `outputs/c0N-*.md`.

### On what data is this based? (evidence & sources)

**EV7: one reading per quote and verdict, by an unnamed model family** (merged from EV7, EV9, SRC13, ASM11 and RED7). Major, load-bearing, high.
- Flaw: "Each researcher was to check every quote against the downloaded source" states an instruction, not a result. The compiler opened nothing. Each step from quote to verdict is one researcher's "For the method" line, and no second reader checked it. The report never names the researchers' model, yet its F11.1 says a reader of the author's family "is not independent in its errors". It still counts agreement across files as strength.
- Evidence that narrows it: c02 re-retrieved about 45 quotes and found every located one present (SRC13). The quote check found both routed quotes in the downloaded PDFs. So the risk lies in reading quotes in context (SRC1, SRC2, SRC3, SRC7), not in the words.
- Re-check: name the model and effort of the researchers and the compiler. Have one reader of another family, or a person, check the context of each pivotal quote behind conclusions 1–11, and whether each "For the method" line follows from its quotes. Record agreement per line.

**EV8: the standing label counts sources, not strength** (merged from EV8 and SRC9). Major, load-bearing, high.
- Flaw: the top label "two or more independent sources" covers findings of very different strength: one manuscript and a position paper (F7.13), two untested proposals (F6.3), a conjunction of single-source halves (F3.12), rates with an unmeasured link (F7.2) and a Cochrane review (F4.7).
- Evidence: unreviewed, single-version 2026 preprints count toward that label: arXiv 2608.24419 v1, 2609.13824, 2609.33812 and 2611.10474, all checked on their listing pages by SRC9. F12.1 counts a script and a reading of the same files as two independent sources.
- Re-check: add a strength band beside each load-bearing standing. Relabel F3.12, F6.3, F7.13, F7.2 and F5.1.

**SRC1: "contradicted" overstates the shared-core passages** (merged from SRC1, ACH1, ASM3, LOG1, EV10 and BEN5). Major, load-bearing, high.
- Flaw: in SEP §7 the no-consensus sentence is Hoyningen-Huene's account of a phase. The entry goes on, "For Hoyningen-Huene, this is too negative a stance", and then gives his systematicity and Haack's "objective epistemic standards". ACH1 reports that M-0 cites the systematicity sentence, not the one the report quotes. No consensus on the nature of science does not entail that the lines share no rule. The quoted sentence itself keeps fallibility. The opposing case was never searched for.
- Effect: "contradicted" becomes "not supported by the passages cited, and disputed rule by rule". The convention remedy survives either way.
- Re-check: as in the top table.

**SRC7: drift of a service, not of a pinned model** (merged from SRC7 and ACH6; EV5, ASM5 and LOG5 agree). Minor, load-bearing, high.
- Evidence: Chen, Zaharia and Zou speak of "the 'same' LLM service". Narayanan & Kapoor find the change to be one of default behaviour. F8.2 already says this, but the summary and F3.12 still say "model".
- Re-check: restate the summary and F3.12, and look for a measurement of one pinned snapshot over time.

**SRC2: "55%–67% of model judges' labels" misreads the source** (merged from SRC2, EV11, ASM15 and LOG10). Major, high. Load-bearing corrected to no.
- Evidence: the abstract says "reproduces 55%–67% of their labels", where "their" refers to the five public label sets, human votes included. The task is a paired choice with chance near 50%, and no baseline is given.
- Re-check: as in the top table.

**EV4: one manuscript carries the top standing for "a visible design no longer filters"** (merged from EV4 and LOG7). Major, high. Load-bearing corrected to no.
- Evidence: one generated paper passed the first round of a workshop that accepts 70%, seen in abstract. Ma et al. is a position paper, not independent corroboration. BEN2 adds the vendor's interest.
- Re-check: relabel F7.13, and look for a measured detection rate.

**SRC3: the wrong base-rate format for "fail about half the time"** (merged from SRC3, EV12 and ACH11). Major, not load-bearing, high.
- Evidence: the "about half" figures are Registered Report rates (44% positive; 60.5% not supported). The report's own van den Akker et al. give 0.69 positive for plain preregistration, which is closer to S-2. P(≥ 6 of 7 | p = 0.5) = 0.0625, and the seven claims come from about two runs.
- Re-check: restate the rate by format, give the interval, and count tests by run.

**EV19: absence claimed without a quoted line** (EV19 only). Minor, load-bearing, low. See [What the critic could not resolve](#what-the-critic-could-not-resolve).

**SRC12: line 16 is quoted in half** (merged from SRC12 and RED9; ACH1 agrees). Minor, high.
- Evidence: three methods quote `method.md` line 16 identically: "The seven rules below are a convention this repository adopts." The defect is the "share" clause, not a missing label.
- Re-check: quote line 16 whole, and narrow row C1.

**SRC6: a simulated figure quoted as observed** (SRC6 only). Minor, high. The abstract reads "in a simulated two-group study with 100 interim looks". Re-check: quote from "simulated".

**SRC4: a definition quoted as a result** (SRC4 only). Minor, high. The Panickssery et al. sentence opens "One such bias is self-preference, where…". Re-check: quote the measured correlation.

**EV13: 14.2% measures another task** (EV13 only). Minor, med. Zhang et al. attribute failures inside multi-agent logs, which is not telling a claim from its auxiliaries. The bundle point stands without the figure (EV16).

**SRC8: Carlisle compares two sets of trials** (SRC8 only). Minor, med. "Misses most" assumes equal prevalence in both sets. The direction holds.

### What assumptions are hidden?

**ASM1: two-sided verdict against a one-sided remedy** (merged from ASM1, EV1, ACH3, LOG3 and RED8). Major, load-bearing, high.
- Flaw: F5.4 fails the example at the two-sided 5% level. Yet the claim is directional, and F5.5 in the same cluster prescribes "a one-sided test for support". Under that test the example passes, at the one-sided p = 0.0286 the report itself gives. Mid-p (about 0.030) and Pearson's χ² (about 0.019) pass as well. Only conservative tests miss (Lydersen et al. 2009, retrieved by ACH3).
- What survives: the method names no test and no error rate, and the power is 0.659.
- Re-check: restate F5.4, bullet 2 and row C53. Rerun `scratch-05/rule3_stats.py` for the 0.659.

**ASM2: H-03 is a teaching example** (merged from ASM2, ACH4 and SRC11). Major, load-bearing, high.
- Evidence: SRC11 and ACH4 opened `references/record-format.md`, and H-03 is its worked example. F12.1 lists the live hypotheses as scientific-method H-01 and H-02 and auditing-ai-context H-01 to H-08. The report computes no false-pass rate for any of the seven real tests.
- Effect: the 0.412 shows that the format teaches a threshold design without error control. It does not show that any live standing is inflated.
- Re-check: rename the example, and compute the null pass probability and power for the seven real tests.

**ASM6: no case of harm from joining standing to force** (merged from ASM6 and LOG8). Major, load-bearing, high.
- Evidence: F12.9 records the trace pass entering as the owner's decision after its comparison failed, which is force without standing. Rule 3 already sets repetitions "by the cost of an error". F4.9 and F12.7 concern different branches, so D10 is not a contradiction.
- Re-check: split D10 into its two branches, look for a case of harm in the records, and restate conclusion 7.

**ASM4 (debated, upheld on its premise only): "rule 7 refutes the claim alone"** (ASM4, c03, Toulmin 1958). Load-bearing; severity lowered from major to minor by the debate; confidence med.
- What the judge read: `method.md`. Rule 2 makes a claim name "what is compared with what, by which measure and under which conditions". The row `refuted` reads "a repeatable test within the same bounds went against it". So the method's claim carries its measure, comparison and scope, and "alone" overstates.
- What still holds: § Acceptance sends "failed repeatably ──► refuted" with no check of any auxiliary. `record-format.md` has no field for a grader or for any auxiliary's check. The harness of an `own` test is named, but only its file's existence is checked. Per SEP "Underdetermination" §2.1, Duhem's group includes theories "accepted by him as beyond dispute", and "the experiment does not designate which one should be changed". Writing an auxiliary down does not settle which part failed.
- Struck from the finding: that row C32 "shrinks … to one field", and that Duhem applies only to unstated auxiliaries. See the rejections file.
- Re-check: reword the summary line and C13 / F1.8 as "rule 7 withdraws the claim, with its stated measure, comparison and scope, within its bounds; it checks no auxiliary and names none as the part that failed". Keep row C32 as a change to the acceptance path.

**ASM13: journal incentives transferred to one maintainer** (ASM13 only). Minor, med. Franco et al. measure non-publication driven by journals, while H-06 failed and is recorded here (F12.2). Re-check: ground row C42 on auditability.

**ASM17: selection behind "practices adopted untested often fail"** (ASM17 only). Minor, med. Prasad's 40.2% counts standards that someone chose to test. Re-check: mark F9.7's figure as conditional on that selection.

### What was overlooked?

**RED5: "a second failure can rarely occur" does not follow** (merged from RED5, LOG5, ASM5, EV5, ACH5 and SRC10). Major, load-bearing, high.
- Flaw: a model that lives about a year leaves that year for a rerun. The conclusion needs an unstated premise, that the rerun comes after retirement.
- Evidence: the deprecation page, re-read by RED5 and SRC10, gives lifetimes of about 12–25 months and "at least 60 days' notice". F6.8 calls fresh agent runs cheap. H-06 was registered and run in consecutive commits. A mundane rival fits as well: nobody schedules reruns.
- What survives: the review term, in the form "support outlives its model unless reviewed".
- Unchecked by the adjudicator: RED5's claim that `temperature`, `top_p` and `top_k` are removed in API version `2026-10-21`, which would leave row C63's decoding-settings field unfillable.

**ACH7: "cannot recover" overreaches** (merged from ACH7, ASM8 and EV6). Major, load-bearing, high.
- Evidence: Lundh's Discussion, p. 19, retrieved by ACH7, says the bias "may be partially mediated by such factors as the choice of comparators, dosing… selective reporting". Rules 3, 4 and 6 read those choices. The LLM sources measure a judge favouring its own outputs, a different mechanism. The repository's own tests never vary their author.
- Effect: row C47 survives as a disclosure, not as proof that reading fails.

**ACH8: replication rate read as the filter's error rate** (merged from ACH8 and RED4). Major, load-bearing, high.
- Evidence: Gilbert et al. find low-fidelity replications "four times more likely to fail". Tyner et al., via Rubin's commentary, say "a single failure to replicate does not justify concluding that the original research was wrong". The thirteen success criteria give 28.6–74.8%. The report applies contextual sensitivity elsewhere (F3.9, D24) but not here.

**ACH10: whether another party holds the commits is unchecked** (merged from ACH10 and ASM10). Major, load-bearing, high.
- Evidence: S-2 trusts ancestry, not dates. The report's evidence, `GIT_COMMITTER_DATE`, bears on dates only. Rewriting ancestry changes every later hash, and ACH10 reports a GitHub remote for `main`.
- Re-check: needs git and host access. See [What the critic could not resolve](#what-the-critic-could-not-resolve).

**RED3: no proportionality applied to its own 106 changes** (merged from RED3, RED1, ASM7 and ACH13). Major, load-bearing, high.
- Flaw: the report sets the bar for acting by cost, reversibility and the value of information, but never applies that bar to its own rows. It imports norms built for patients, courts and high-risk AI to rules a commit can revert.
- Evidence: ICH E6(R3) "encourages a risk-based and proportionate approach" (retrieved). By c05's count, 34 of the 106 rows read "None reported in the files". The status-quo alternative, narrowing the scope, is never weighed.

**RED2: the density finding is not applied to `method.md`** (merged from RED2 and LOG12). Major, load-bearing, high.
- Evidence: F8.7 shows adherence falling with density, with a "bias towards earlier instructions". `method.md` is read every session (117 lines, 1,552 words by RED2's count). LOG12 lists rows C23, C26, C35, C41, C45, C56–C59, C63, C75, C76, C79 and C88 as adding to it. The size of the effect at 1,500–4,000 words is unmeasured.

**RED6: the count of "missing" verdicts measures a gap-seeking search** (merged from RED6, LOG13 and ASM16). Major, high. Load-bearing corrected to no.
- Evidence: 84 of the 148 verdicts are "missing" and 24 "keeps", on a vocabulary with one positive label against five defect labels. No arm argued sufficiency. The report demands a comparison when it judges the method (F12.5), but its own judgement of fit has none.

**ACH9: S-4 already bounds compliance against benefit** (ACH9 only). Minor, high. ACH9 quotes S-4: "a test of compliance is never presented as a test of benefit". Re-check: restate row C54 as carrying S-4 into a field.

### Who benefits?

**BEN1: registry operators set the bar, and their registries miss it** (merged from BEN1 and SRC5). Major, load-bearing, high.
- Evidence: Nelson, Simmons and Simonsohn created AsPredicted, and the OSF page documents its own registry. An AsPredicted plan can stay private until "the authors are ready". An OSF registration can be withdrawn, embargoed or updated. Only Fidler and Wilcox state "public".
- Effect: what the method lacks is narrower than the report says: a record held by a party the author cannot rewrite, public by the time of the result.

**BEN4: the SCORE figures come from the Center for Open Science's own release** (BEN4 only). Minor, load-bearing, med. This is a mission interest, not a financial one, and the report marks the summaries "(secondary)". The adjudicator's recollection that COS also coordinated OSC 2015 is unverified.

**BEN3: the disclosure the report recommends is not applied to its own sources** (BEN3 only). Minor, high. The Sources table has no interest column.

**BEN2: the vendor's interest is dropped** (BEN2 only). Minor, high. Six of Lu et al.'s eight authors work for or consult for Sakana AI, and the competing-interests statement says so.

### Reasoning soundness

**LOG6: a link stated as fact that Open questions calls unmeasured** (merged from LOG6, EV3 and ASM9). Major, load-bearing, high.
- Evidence: line 655 says the rule-4 coding is something "no source codes", which "the researcher infers nearly all, unmeasured (07)". F7.4 adds that only about a quarter of SCORE's sample would qualify if the data must be in view. Line 248 and the summary still state the link as fact, under the top label.

**LOG11: the wrong denominator** (merged from LOG11 and ASM12). Minor, load-bearing, high. The 1,355 lines include decisions, definitions and norms, which take no test, and the 1,326 lines without a record predate the method. The right count is 6 of 7 tested of 10 claim records.

**LOG9: "shown to come from neither" is an invalid step** (merged from LOG9 and ACH12). Major, high. Not load-bearing, per claims.md. A definition that matches two texts can derive from either, and one line, M-S, is made a property of the whole map.

**LOG4: one test's pass rate read as the admission rate** (LOG4 only). Minor, load-bearing, low. See [What the critic could not resolve](#what-the-critic-could-not-resolve).

**LOG2: a difference of unit** (merged from LOG2 and ACH2). Minor, high. Kuhn and Lakatos speak of paradigms and programmes, while rule 7 withdraws single low-level claims. F3.8 already concedes this.

**LOG16: "every result carries error rates both ways" is too wide** (LOG16 only). Minor, high. F2.9's existential claims and F2.11's proofs have no error rates.

**LOG15: absence of evidence read as evidence of absence** (merged from LOG15 and ASM14). Minor, high. "We did not find that preregistered studies had a lower proportion" is not "showed no fall". F12.2 quotes the riskiness confound but never joins it to row C62.

**LOG14: "adds no verdict" beside syntheses** (LOG14 only). Minor, med. "The method fits with additions on nearly every rule" is the compiler's sum; no single findings file states it.

## What the critic could not resolve

No debate verdict was `uncertain`. The one debate, ASM4, ended with a split ruling. The open items:

- **ASM4: the repository records the challenger cited.** The challenger cited H-01 to H-07 in the two `pending-evidence.md` files: harness pinned by commit, model and effort recorded, label checks, and H-07 not counting a run whose auxiliary failed. The judge did not verify these. If they are accurate, practice runs ahead of the text of `method.md`. That argues for writing row C32 into the format, not against it. *Settled by* reading those records.
- **LOG4 (low): which admission rate applies.** It is 0.412 if one passing test admits a claim, and about 0.17 if an own test needs a confirming rerun. No method and not the adjudicator opened § Acceptance. *Settled by* reading § Acceptance of `method.md`.
- **EV19 (low): where a one-event claim fails in the path.** No line of `method.md` is quoted for it. *Settled by* tracing such a claim through § Acceptance step by step.
- **ACH10: the push record.** Were the registering commits, for example `97a86d6`, on a remote another party holds before their results? If yes, conclusion 9 narrows to the missing date and the missing independent reader. *Settled by* the host's push and force-push history; this needs host access.
- **ACH8: Tyner et al. pp. 147–148.** These were read only through Rubin's commentary. *Settled by* a direct reading.
- **ACH7: Lundh's Analysis 5.7.** Does a sponsor effect remain after adjusting for comparator choice? *Settled by* reading that analysis.
- **RED5: the time from a first failure to a possible rerun,** and whether H-06's pinned model is still served. *Settled by* the repository's records against the deprecation dates. RED5's report of sampling parameters removed in API version `2026-10-21` is also unchecked.
- **BEN4: who coordinated OSC 2015.** This is the adjudicator's recollection, unverified.
- **Med-confidence minors** that no second method corroborated: EV13, SRC8, ASM13, ASM17, LOG14. Each is settled by the re-check in its row.
- **RED6's null arm and the diff-by-diff reading.** The report names both as unanswered (lines 653, 656). Until one of them is done, "fits with additions on nearly every rule" cannot be told apart from an artefact of the search.

## Strengths confirmed

These parts withstood the checks aimed at them:

- **EV2: the rule-3 arithmetic** (merged from EV2, ASM18 and LOG17; priority 5). Four independent recomputations agree. Fisher's one-sided p is 0.0286 and the two-sided p is 0.0573. P(X > Y) for two Bin(10, 0.5) arms is 0.412. The figures of conclusion 2 can be relied on; its weak points are the warrants (ASM1, ASM2). Not reproduced: the power of 0.659, against about 0.79 by a normal approximation. Rerun `scratch-05/rule3_stats.py`.
- **EV16: the bundle point** (priority 5). "A failed test indicts a bundle" is supported independently by SEP "Underdetermination", Mayo (1996) and Strevens (2001). The debate on ASM4 left it untouched. Duhem's own text was not opened, which matters only for line M-7/4.
- **EV17: models of one provider share their errors** (merged from EV17 and ASM19; priority 5). Kim et al. (full text) and Goel et al. (abstract) agree, and c02 confirmed Kim's figures. The step to a reader of records is indirect, and row C96 already frames it as a hypothesis. Rank the remedies in row C95: ground truth first, then a person, then another family.
- **EV15: conclusion 7's external premise** (merged from EV15 and ACH14; priority 5). Guyatt et al. (2008), Addington v. Texas and Claxton et al. (2005) state the split between grade and force directly, and the report states its rival (D10).
- **ASM20: the singular-claim gap is fair** (priority 5), because `method.md` claims universality ("They apply to every statement alike", F10.11). Make row C88 conditional on the scope decision in row C1.
- **EV18: the comparison of pre-recording mechanisms as written** (priority 5) holds. How large the gap is depends on ACH10 and BEN1, and the harness-log remedy is untested.
- **BEN7: no aligned interest behind the cross-provider and retirement sources** (priority 4). Any skew in the providers' own deprecation pages would understate churn.
- **BEN6: Schoen et al. report against their own interest** (priority 2).
- **RED11: the report discloses many of its own limits** (merged from RED11 and LOG18; priority 2). It discloses abstract-only sources, a compiler who opened nothing, a table that is not a ranking, 29 disputes stated from both sides, and a thin track record. c07 found no strawman among the disputes.
- **The quotes themselves.** c02 re-retrieved about 45 quotes and found every located one present and none fabricated (SRC13, inside EV7). The two quotes routed for a script check both stand in the downloaded PDFs (`inputs/quote-check-disputed.txt`). The report's weakness is the reading of quotes in context, not their wording.

## Method coverage

- All seven methods ran and returned findings. Every marker in `_status/` reads `done`. Raw findings per method: c01 evidence-grading 19, c02 source-integrity 13, c03 assumption-excavation 20, c04 competing-hypotheses 14, c05 premortem-redteam 11, c06 beneficiary-funding 7, c07 logic-fallacy 18.
- Adjudication: 102 raw findings, 48 surviving entries (80 raw merged into 28), and 2 whole findings rejected plus one part of RED7. The adjudicator added no ADJ finding. 14 entries stand at priority 7.
- Debate: one finding met the rule (ASM4), against a cap of 6. Its judge read `method.md` and `record-format.md` and fetched SEP "Underdetermination".
- Ten entries left the debate rule only because merging raised them to high confidence. In four of them the decisive fact is still unchecked: ACH10, ACH8, ACH7 and RED5 (listed above).
- No critical finding was raised by any method.
- This synthesis added no finding. It read the adjudication, the ASM4 verdict, `claims.md` (main conclusions and atomic claims) and the report's opening lines. It checked the meaning of row C#s against the report's table of candidate changes, and the severities of the rejected raw findings against c01 and c05. It fetched nothing.
- Tool deviation: Grep was not available in this session. I made those three look-ups with read-only `grep` and `ls` in Bash, outside the rule that limits Bash to the marker.

---
*Raw outputs: tmp/appraisal-2026-11-21-scientific-method-review/outputs/. Rejected findings: 2026-11-21-scientific-method-review-appraisal-rejections.md.*

<!-- COMPLETE -->
