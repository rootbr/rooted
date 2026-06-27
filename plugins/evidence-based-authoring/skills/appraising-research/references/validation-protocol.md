# Validation Protocol

> The critic is useful only if it finds the flaws that genuinely matter, ranks them so the load-bearing ones surface first, and does not flood the author with false positives. Unlike `discovering-subtopics` there is no expert "reference map" to recall against — a good appraisal is defined by *catching planted defects* and *rejecting unfounded findings*. Success = ≥ 90% recall on seeded load-bearing defects in the top-ranked band, ≤ 0.05 false-positive rate, and 0 fabricated sources.

## Contents
- §Eval corpus (seeded-defect method)
- §Metrics
- §reliable@10 description-trigger evals
- §Iteration loop
- §Quality gate before commit
- §Regression watch

---

## Eval corpus (seeded-defect method)

There is no ground-truth appraisal to compare against, so build the ground truth by **planting** known defects into otherwise-sound short reports, one defect per axis, and checking the critic recovers them. The corpus mixes domains so appraisal is not tuned to one field.

| Eval report | Planted defects (one per axis) | Domain |
|--|--|--|
| Espresso-machine buyer's guide | BEN: a "best pick" sourced only to a vendor's affiliate page · SRC: a review quote misattributed · c01: a durability claim from a single forum post stated as fact | Consumer |
| "Intermittent fasting improves longevity" brief | ASM: correlation-as-causation on observational data · ACH: ignores the calorie-restriction confounder · RED: omits null replication studies | Factual/scientific |
| "Adopt technology X for our service" memo | c04: a simpler status-quo alternative never considered · LOG: conclusion does not follow from the benchmark cited · SRC: a benchmark link that does not say what is claimed | Technical |
| Local tax-relief eligibility summary | SRC: cites a stale regulation superseded last year · c01: a threshold stated without the official source · ASM: assumes a category applies without checking | Local/bureaucratic |
| A genuinely sound 1-page report (control) | none — must return few/zero findings and verdict "strengthened/unchanged" | Mixed (false-positive test) |

Keep a separate key file per report listing the planted defects and which finding IDs should catch them. Do not give the key to the critic.

## Metrics

For each eval report:
1. Run `/appraising-research` on the bare report path.
2. **Defect recall** = (planted defects caught by a confirmed finding) / (planted defects). Target ≥ 0.90.
3. **Top-band recall** = (planted *load-bearing* defects appearing in the top-priority band) / (planted load-bearing defects). Target ≥ 0.90 — ranking, not just detection, is the product.
4. **False-positive rate** = (confirmed findings that are not real defects, judged against the report) / (confirmed findings). Target ≤ 0.05.
5. **Fabrication rate** = (findings citing a source that fails verification) / (findings citing a source). Target 0.
6. **Control behaviour** = the sound report yields no `critical`/`major` confirmed findings and a "strengthened/unchanged" verdict.

Misses cluster by axis → the corresponding method prompt is the edit candidate. A high false-positive rate → tighten the adjudicator's anchor / already-addressed checks.

## reliable@10 description-trigger evals

### should-trigger (all 10 must route to `appraising-research`)
1. Critique this research report and tell me what to re-check.
2. How solid is the conclusion in this document?
3. Pressure-test / red-team this recommendation.
4. What assumptions am I making in this analysis?
5. Poke holes in this report.
6. Who benefits from the recommendation in this memo?
7. Is the evidence in this brief strong enough to act on?
8. Fact-check the sources in this analysis.
9. What did I miss in this report?
10. I just finished this report — stress-test it before I send it.

### should-not-trigger (all 10 must NOT route to `appraising-research`)
1. Research X and write me a report. → `researching-topics` (generation, not appraisal)
2. Map out the questions I should ask about X. → `discovering-subtopics`
3. Review this Java branch for bugs. → `reviewing-java`
4. Find the config file in this repo. → Grep/Glob
5. What's the LD50 of X? → single factual lookup (`researching-topics` direct)
6. Summarize this article for me. → summarization, not appraisal
7. Fix the typo in this document. → editing, not appraisal
8. Is Y worth buying in 2026? → opinion query (`researching-topics`)
9. Write a rebuttal to this essay. → composition, not appraisal
10. Explain what GRADE is. → single definition

Failure modes to watch: false-trigger on #1/#5/#8 (generation/lookup asks) and #6 (summarize), overlap with `reviewing-java` on #3.

## Iteration loop

1. Run all eval reports — one background invocation each.
2. Score against each key file: recall, top-band recall, false-positive, fabrication, control.
3. Each miss category → one targeted edit to the offending method prompt or the adjudicator; avoid global rewrites (token-economy evidence shows full-rewrite compression drops accuracy).
4. Re-run until all reports hit targets, OR 3 iterations (whichever first).
5. On stall, document residual misses in `SKILL.md §Gotchas` rather than over-fit.

## Quality gate before commit

Per the repo `CLAUDE.md`:
- Run `/auditing-ai-context` on `SKILL.md`, every `agents/*/prompt.md`, and every `references/*.md`.
- MUST pass the self-review checklist and the reliable@10 description eval above.
- Every method in every file MUST cite a primary source (`references/appraisal-methodology.md`); brainstormed-only rules MUST be cut or marked provisional.

Fail any of the above → block commit, iterate, re-run gate.

## Regression watch

Re-run the eval when:
- A new method agent or axis is added — verify recall improves rather than merely shifts, and the false-positive rate does not rise.
- A user reports a real appraisal that missed an obvious flaw or raised a false one — add that report (with a key) to the corpus.
- On every model upgrade — pin the model version in eval runs; unspecified requirements regress ~2× more often across models (Yang 2505.13360 §3.3).
