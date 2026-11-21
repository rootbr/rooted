# Appraisal — Rejected & Refuted Findings

Report: `research/2026-11-21_scientific-method-review.md`. Every finding or part of a finding filtered out of the appraisal is listed here with its grounds, so the author can challenge it. The raw findings are in `outputs/c0N-*.md`. The adjudicator's grounds are in `outputs/adjudication.md` § Rejected findings, and the debate's grounds are in `outputs/debate/ASM4.md`.

## Summary
- Confirmed (in appraisal): 48 entries (39 ranked findings and 9 confirmed strengths)  ·  Rejected at adjudication: 2 whole findings, plus 1 part of a finding  ·  Refuted in debate: 0 whole findings, plus 1 part of a finding (ASM4's consequence)

## Rejected at adjudication

### ~~EV14: "A review term would move more standings within a year than any change to the seven rules" has no measurement behind it~~
- **Original severity**: minor (load-bearing no)  ·  **Method**: c01 evidence-grading
- **Anchor**: "by the researcher's inference a review term would move more standings within a year than any change to the seven rules"
- **Reason**: the report already addresses it.
  - The summary sentence carries its own hedge, "by the researcher's inference" (line 13).
  - F8.1 says "the interval would be measured here, not copied, and the researcher found no measurement for prompts" (line 134).
  - Row C41 states the test that would refute it: "refuted if a count over the records shows fewer moves" (line 539).
  - c03 read it the same way. EV14's own recheck action, counting the records that name a retired model, is the refuting test row C41 already names.

### ~~RED10: The work list contains mutually exclusive changes with no reconciled sequence~~
- **Original severity**: minor (load-bearing no)  ·  **Method**: c05 premortem-redteam
- **Anchor**: "rows that propose the same change are merged and carry every finding id"
- **Reason**: the report already addresses it. Each conflicting row names its opposite in "What speaks against it":
  - row C34: "F3.4 would refute only when pooled runs exclude the effect (D6)";
  - row C52: "F4.1, F4.2 and F7.11 would keep `law` and tighten it";
  - row C73: "The two findings read the clause in opposite directions (D14)";
  - row C49: "F12.7 reads "in force as a decision" as already making the split (D10)".

  The table declines to rank, and says so: "The order follows the clusters and is not a ranking." A dependency order would improve the table, but its absence is not a defect in what the report states. RED3, in the appraisal, keeps the related point that no cost or minimal subset is given.

### ~~RED7, its spot-check part only: the Chen et al. quote "does not match its labelled abstract"~~
- **Original severity**: major (the whole of RED7; load-bearing yes)  ·  **Method**: c05 premortem-redteam
- **Anchor**: "the compiler of this report re-opened none of them and took every quoted word from the findings files."
- **Reason**: refuted by the quote check in `inputs/quote-check-disputed.txt`.
  - "High judge agreement is therefore not evidence of valid evaluation." stands in the downloaded PDF as the last sentences before "1 Introduction", that is, in the PDF's abstract.
  - The report's source is that PDF: "full text", "arXiv v1, 25 Aug 2026" (line 697).
  - RED7 compared against the arXiv listing page, which does not hold the sentence (best similarity 0.520).
  - The same check found Kim et al.'s quote in its PDF, in the paragraph "Our work complements this analysis".

  The rest of RED7, that the report does not apply its own independence findings to itself, survives inside EV7.

## Refuted in debate

No debated finding was refuted whole. The one debate, ASM4, upheld the finding's premise and refuted its consequence. That refuted part is recorded here. The upheld premise stays in the appraisal at minor, med.

### ~~ASM4, its consequence only: row C32 "shrinks … to one field", and Duhem applies only to auxiliaries the record does not state~~
- **Verdict**: refuted (confidence med; the split between premise and consequence is the judge's own judgement on a mixed finding, while the textual facts behind it are certain)
- **Decisive evidence**:
  - The residue ASM4 itself names, "the check each passed", has no field in `record-format.md` § Fields by kind for any of the five auxiliaries (prompt, measure, harness, model version, grader), not only the grader.
  - § Acceptance sends "yes, it failed repeatably ──► refuted: the record stays" with no exit for a test whose auxiliary failed its check. Row C32's "or else records that the bundle failed" therefore changes the acceptance path, not one field. The challenger's move of that branch to F3.6 relocates the change without making it smaller.
  - SEP "Underdetermination of Scientific Theory" §2.1, fetched by the judge, puts in Duhem's group "a whole group of theories accepted by him as beyond dispute", and says that "the experiment does not designate which one should be changed". So Duhem's point applies to auxiliaries that are stated but unchecked, not only to those left unstated.
  - For an `own <path>` test, `record-format.md` § Tests asks only that "that file exists". The harness is named, but its correctness is neither part of the claim nor checked. So the harness is not "part of what is refuted" in the sense ASM4 meant. The measure (`measure`) and the model version (`scope`, `bounds`) are.
- **Note on ids**: ASM4's "C32" is the report's candidate change, row C32 ("Rule 7 names which part of the tested bundle a repeated failure withdraws …"). It is not claims.md C32, which is publication bias (F3.13).

<!-- COMPLETE -->
