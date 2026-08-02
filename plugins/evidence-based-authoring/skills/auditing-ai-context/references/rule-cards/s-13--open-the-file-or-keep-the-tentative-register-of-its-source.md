---
title: A file is opened before its contents are stated, and a statement taken from elsewhere keeps the tentative register of its source
rule_id: S-13
applies_to_target: [answer, doc]
check_kind: semantic
severity_default: high
---

# A file is opened before its contents are stated, and a statement taken from elsewhere keeps the tentative register of its source

## Thesis
Open the file before stating what it contains. Where the statement comes from elsewhere and the source has not been opened, carry it in the tentative register the source had — "the reviewer proposes this", not "the spec states it" — and never in an evidential adverb such as "reportedly", which is read as a flat assertion rather than as a hedge.

## Rationale
What a later reader acts on is the confidence of the phrasing, not the credit attached to it. Across five models at temperature 0, a carried claim stated flatly ("Alice's clearance is admin") was acted on at a 0.81 grant rate on every model, and neither attributing it to a user nor forging a "system of record" moved that rate — four forged authorities each granted 0.83 on all five models. The register moved it: the same claim carried modally ("probably") fell to 0.00 on two of the five models and reached no higher than 0.40 on any. The working part of "the reviewer proposes this" is therefore its actor and its tentative verb, not the credit it hands out. The hedges are not interchangeable either. Ranked by mean grant, modality discounts hardest (0.00–0.13), explicit non-verification next (0.00–0.27), and the evidential register least (0.27–0.54): "Alice is reportedly an admin" granted 0.81 — the flat assertion's own rate — on four of the five models, and 0.68 on the fifth. Both repairs that suggest themselves fail: a passive "unverified" tag is ignored, and an active "do not trust this" instruction escalates even correct claims, so it is safe only by declining to decide. The upstream half is what leaves the register honest in the first place. Three statements of a source's content, each written without the source being opened, survived into citations inside an evidence-governed corpus: a PDF cited for years as a 1989 journal article is a 2008 dissertation by a different author, a defect-rate multiplier attributed to a 2019 study is in neither that study nor at the value quoted, and an obedience percentage traced back to no fetched source at all.

## Example
```
bad:  The lease bans subletting.              (nobody opened the lease)
bad:  The lease reportedly bans subletting.   (an evidential reads as a flat assertion)
good: The agent says the lease bans subletting; nobody has read the lease.
```

## Limits
Covers a statement about what a file, specification, message or other source contains, inside prose delivered to a reader. The register result is measured on language models deciding from carried memory in constructed access-control and budget-approval scenarios at temperature 0, where the rates are exact descriptions of those scenarios rather than statistical estimates and no base rate in live use is measured; the report is an unreviewed preprint. A human reader's response to the same register is not measured there, so a document read only by people carries this rule as an extrapolation. Keeping the tentative register does not make an unopened claim safe: the same work calls the phrasing discipline hygiene rather than a defense, holds that no single carried claim may be load-bearing, and finds that one redundant source restores correct decisions. The half requiring the file to be opened rests on recorded misattributions rather than on that experiment.

## Validator
For each statement asserting what a file, specification, message or other source contains, look for a locator the reader can open — a path, a section, a quoted line — and flag a statement of content that carries none. Where the statement is relayed from another party, check its register: an actor with a tentative verb ("the reviewer proposes", "the ticket claims") passes, while a flat assertion of the source's content passes only where the target shows the source was opened. Flag every evidential adverb — "reportedly", "apparently", "supposedly", "rumor has it" — as a flat assertion wearing a hedge, and flag a passive "unverified" tag left to do the work the phrasing should do. Validator question: does this sentence assert what a source contains, and does the target show that source was opened?

## Patch output
When auditing a target that states a source's content with nothing showing the source was opened, or that flattens a relayed statement into an assertion, emit one patch (`rule_id: S-13`, `location.section` + `line_hint`, `current` = the statement, severity high — the defect is a false statement of fact carried in the register that suppresses the reader's own check) proposing the actor-plus-tentative-verb restatement, or the removal of the evidential adverb. Whether the writer opened the source cannot be read off the text, so set `proposed: null` and `needs_human: true`.

## Source
Kwon 2026, *Manufactured Confidence: How Memory Consolidation Turns Hearsay into Confident Facts*, arXiv:2606.29279 [cs.CR], submitted 28 June 2026 — **an unreviewed preprint** — Table 1 (flat assertion 0.81 on all five models; attribution and a forged "system of record" unchanged; modal hedge 0.00 on two models, 0.40 at most), the cue decomposition (modality 0.00–0.13, explicit non-verification 0.00–0.27, hearsay 0.27–0.54; "reportedly" 0.81 on four of five models, 0.68 on the fifth), and the stated bound (a passive tag is ignored, an active distrust instruction only abdicates, and store-side phrasing is hygiene, not a defense). Verified hands-on experience for the opening half — three misattributions recorded in `research/2026-08-02_output-style-evidence.md` — § Verification — news structure (the PDF cited as a 1989 article is a 2008 dissertation), § E1 (the ~1.5× defect figure absent from the study it was attributed to) and § Method (the 63.8% obedience figure absent from every fetched source). Caveats: constructed scenarios, decision-shaped tasks, temperature 0, exact rates rather than estimates; no human-reader measurement of the same register.
