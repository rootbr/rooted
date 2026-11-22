# Evidence behind the audit of AI context — re-verification and research to 2026-11-22

This note reports two pieces of work on the claims behind the skill `auditing-ai-context`, both closed on 2026-11-22. The first re-opened the sources of all 142 rule lines of the skill's two provenance maps and checked 1,332 quoted words and figures against them: 1,279 stand in their sources, 48 are absent, 4 could not be fetched and 1 is near. It found 172 places where the repository's text says other than its source; 86 of them are corrected in the maps, and the 86 in the files the audit runs with are corrected by 84 edits in 51 files, which the repository owner approved on 2026-11-22. An independent reader then read the 16 records that had first taken the standing `supported`: 4 hold that standing, 11 are the owner's decision with a hypothesis, 10 of them because the source compares shares or correlations and names no test of the difference, and 1 rests on a norm. The second piece searched for tests of the 112 hypothesis lines and of the 6 lines that stood as `supported` when the search began, published or revised since 2026-07-01 (for output style, since 2026-08-01). It returned 157 findings on 94 lines; a skeptic re-read 45 of them, of which 20 stand as stated, 25 are weaker than stated and none fell. Of the 20 tests reported as for or against a claim, 3 ran inside the scope the claim's line names: one against H-R-22, one for R-73 and one for H-G-17. No standing changed.

Main results:

- Of 1,332 quoted words and figures checked against the cited sources, 1,279 stand, 48 are absent, 4 were not fetched and 1 is near.
- The repository's text says other than its source in 172 places: 86 in the free text of 71 provenance lines, now corrected, and 86 in the run set, corrected by 84 edits in 51 files that the owner approved on 2026-11-22.
- Four claims hold the standing `supported`, each on a test made under conditions other than the repository's (`fit: transfer`): R-52, R-73, S-07 and G-24.
- Eleven claims that first took the standing `supported` are the owner's decision with a hypothesis, ten of them because the source names no test of the difference the claim states; one more, G-12, rests on a norm.
- The research found 157 findings on 94 of its 118 questions; 24 lines found nothing new, and 30 candidate sources stayed unopened.
- The one test inside a claim's scope that bears against it found a conditional wording of one rule followed less often than a prescriptive one on two Claude models in Claude Code (arXiv:2611.04367v1), and H-R-22 stays a hypothesis.
- Fourteen tested findings that no line covers are candidates for a rule, and the owner is asked about three questions that arise from the findings.
- The skill's own test of H-06 went against the claim (exact McNemar test, p = 1.00), while H-03 and H-05 are supported on one run each.

## What was investigated and why

The skill audits agent instruction files, documents and drafted answers against rule cards. Each of the 103 rule cards the run covered under `plugins/evidence-based-authoring/skills/auditing-ai-context/references/rule-cards/` has a line in `maintenance/rule-cards-provenance.md`; card R-48, added on 2026-11-22 by the owner's decision on the precedence sentence of section 9, has the 104th. The 39 lines of `maintenance/skill-provenance.md` cover the gotchas and the sections of `SKILL.md` and `references/kb-card-specification.md`. Every line closes with a record in the format of `plugins/evidence-based-authoring/skills/scientific-method/references/record-format.md`; of the 142 lines the run covered, 116 records are decisions of the repository owner (88 and 28), 22 are norms (12 and 10) and 4 are claims with the standing `supported` (3 and 1).

A decision names the hypothesis it rests on. The hypotheses stand in `maintenance/pending-evidence.md`, which holds 123 lines: 8 about the skill's own checks (H-01 to H-08; five supported by the skill's own test, three waiting), one for a claim no rule rests on yet (H-09, the number of binding rules of section 9), and 114 that a rule line rests on, keyed `H-<id of the line>`, all with the standing `hypothesis`; the 114th is H-R-48, behind card R-48.

The run asked two questions. The first was whether the cited sources say what the lines say: a figure, a section or a statement credited to a source is only as good as its agreement with that source. The second was which tests of the claims have appeared since the last research date, 2026-07-01 for most clusters and 2026-08-01 for output style, and which earlier tests the lines did not cite.

The run does not answer the following. It ran no test of its own on the repository's files; the skill's own tests reported in section 11 were run before it. It prepared the 84 edits to the run set and applied none of them itself, because a file of the run set changes by the owner's decision alone; the owner approved them on 2026-11-22, and they are applied. It does not judge whether a decision of the owner is right; it reports what the evidence beside each decision shows. It does not settle the sources it could not open.

## Method

Re-verification. The sources of all 142 lines were re-opened in 28 batches. Each batch read the cited passage, compared it with the line and with the text of the run set that rests on the line, and wrote down every place where the two differ. The quoted words and figures were checked by `plugins/evidence-based-authoring/skills/scientific-method/maintenance/scripts/check_quotes.py`, which says whether each quotation stands in the text of its source. The quotations and their sources are kept in `maintenance/citations.json`, which holds 2,162 entries: 1,173 from the re-verification and 989 from the research. Run over the texts fetched on 2026-11-22, the script finds every one of them in its source.

Records and the independent reader. Each line's record was written in the record format of the method (`plugins/evidence-based-authoring/skills/scientific-method/references/method.md`, its kinds of statement, standings and seven rules). Every record that took the standing `supported` was read by an independent reader, a fresh instance that had seen nothing of the work, which answered the check questions of the seven rules on it. A record that failed a rule went to a writer who re-opened the source and either amended the record or lowered it to the owner's decision with a hypothesis; an amended record was read again.

Research. The question list was the skill's own claims: the 112 hypothesis lines and the 6 lines that stood as `supported` when the search began, grouped by topic into 14 clusters. Each cluster had one researcher, who searched for tests published or revised since 2026-07-01 (for the two output-style clusters, since 2026-08-01) and for earlier tests the lines did not cite. A test is a comparison of the claim's measure, or a near measure, between arms under stated conditions; a vendor's or a standard's document is recorded as a norm, not as a test. Each finding states how it bears on its line: the same question under other conditions (`bounds`), in the claim's direction (`supports`), against it (`against`), a norm, or a tested finding no line covers (`new`). The 1,030 quoted words and figures of the findings were checked by script, and all stand in their sources.

Skeptic. A skeptic re-read against its source every finding that bears `supports`, `against`, `norm` or `new`: 45 findings in all (12, 8, 11 and 14). For each it gave a verdict (stands as stated, weaker than stated, or fell), restated the test in its own words, gave its own bearing, and said whether the test ran inside the scope the claim's line names. The note states every such finding in the skeptic's wording and with the skeptic's bearing.

Entry into the records. A finding entered a hypothesis line as a test with what it showed and its bounds; 84 hypothesis lines gained tests in this way. Four supported records gained tests: R-52, R-73, S-07 and G-24. Twelve norm segments were added to provenance lines. A standing moves only when a test inside the claim's scope meets or misses its refuter under the method's rules, and none did: no hypothesis reached `supported`, `contested` or `refuted`.

The run has these limits:

- One researcher searched each cluster, so no second search measured what the first one missed.
- The search ran on a budget, and 30 candidate sources stayed unopened.
- Most findings rest on preprints that no reviewer has read; 153 rest on the full text, 3 on an abstract alone and 1 on an abstract and introduction.
- The readers, researchers and skeptics were instances of one model family, which is also the family whose behaviour many of the claims concern.
- The skeptic re-read 45 of the 157 findings; the 112 findings that bear `bounds` were not re-read.
- A quote check shows that the quoted words stand in the source; it does not show that the reading of them is right.

## Re-verification

The re-verification found 172 places where the repository's text says other than its source. Eighty-six stand in the free text of 71 provenance lines and are corrected in the maps. Eighty-six stand in the run set (the rule cards, `SKILL.md`, `references/gotchas.md` and `references/kb-card-specification.md`). For those, 84 exact edits in 51 files were prepared: 19 change a figure, a section name or a quotation, and 65 change the statement of what a source shows, 6 of them in a rule's Thesis. The owner approved all 84 on 2026-11-22, and the run set holds them.

The discrepancies fall into four kinds. One example of each follows.

- A figure the source prints otherwise. The text of R-17 credited observation masking with a cut of 50.9–57.1% and cited Bulle Labate arXiv:2511.22729v1, which holds only the pointer figures. The figures stand in Lindenbauer et al. arXiv:2508.21433v3 (27 Oct 2025, NeurIPS 2025 workshop) Table 1, which gives 9.8–57.1% (Qwen3-32B masking "0.46 ±0.05 (-9.8%)") and measures instance cost in dollars, not tokens. In a second case of this kind, R-60 gave 44.7% against 24.5% and cited Khan arXiv:2510.22251v1, which prints neither; 44.7% stands in Yang et al. arXiv:2505.13360v3 §3.2, and 24.5 was a subtraction made in the repository.
- A number given another meaning. The text of R-02 spoke of a "61.8 pp collapse". Dong et al. arXiv:2512.14754v3 §4.2 Table 1 gives a relative drop of 61.8% for Qwen3-0.6B, from 58.0 to 22.2, which is 35.8 points.
- A statement the source does not make. The text of R-03 stated that modern routers scan the body and not only the description. SkillRouter arXiv:2603.22455v5 §3 says the opposite: "Current agent frameworks typically expose only a skill's name and description".
- A convention credited to a paper that does not state it. Chatlatanagulchai et al. arXiv:2509.14744v1 (18 Sep 2025, a study of 253 CLAUDE.md files) was credited with the token-economy, horizontal-rule, emphasis ("~10 per 100 lines") and contrast-pair conventions of cards R-25 to R-28. The paper holds none of them.

Several cited preprints have moved between versions, so a section or a figure cited by number no longer points where it pointed.

| Source | Versions | What moved |
|---|---|---|
| SkillRouter, arXiv:2603.22455 | v4 (1 Apr 2026) to v5 (20 Jul 2026) | the range 31–44 pp became 37–44 pp; App. L.1 became App. M.1; Table 7 became Table 9 |
| IH-Benchmark, arXiv:2607.25987 | v3 (16 Nov 2026) | 37 models from 98.2% to 20.5% became 32 configurations from 32.9% to 97.8% |
| SWE-Skills-Bench, arXiv:2603.15401 | v1 (16 Mar 2026) to v2 (27 Oct 2026) | v2 reads "92 of 98 skills have no statistically significant effect" |
| Abdelnabi et al., arXiv:2605.17634 | v2 (15 Nov 2026) | §4.4 became §5 |
| Gloaguen et al., arXiv:2602.11988 | v1 (12 Feb 2026), v2 (23 Jun 2026), v3 (29 Sep 2026) | v1 §4.2 Fig. 5 became App. B Fig. 12 |

Seven sources stayed unopened:

- Cleveland & McGill 1984: the full text was not opened, and an OCR copy of a scan was read in its place.
- Ferreira's 2020 accepted manuscript returned HTTP 403.
- Lang 1989 returned HTTP 403 and was read by its Crossref and OpenAlex records.
- Ibrahim et al. 2012 (Journal of Systems and Software) is paywalled.
- Three observations of the repository's own left no record: two behind G-27 and one behind G-28.

## Standings after the reader

Sixteen lines first took the standing `supported`. The independent reader found that 4 held every rule (G-12, G-24, R-73 and `kb-card-specification § Authoring rules C-E1`) and that 12 failed at least one. The failures were of rule 3 (severity) in 9 records, rule 7 (revision) in 5, rule 6 (no fitting) in 4 and rule 4 (reproducibility) in 3. Two of the twelve were amended and held every rule on a second reading (R-52 and S-07). The other ten were lowered to the owner's decision with a hypothesis.

The records that gained tests from the research were read again. R-73, S-07 and G-24 held every rule. R-52 failed rules 3 and 7; its record now names the tests that set a skill written by an LLM against no skill, marks `SKILL.md` as a transfer from the context files of arXiv:2602.11988, and held every rule on the next reading. G-12 was read again beside the vendor's documentation of skill loading. One reading failed rule 7 on the documented preload of skills into a subagent; after its scope was narrowed, the next reading failed rule 6, because the reading of the Claude Code source in arXiv:2604.14228v3 §6.1 and §6.3 is the observation the claim grew from, and no later observation tests it. The line G-12 rests on the vendor's documentation as a norm. `kb-card-specification § Authoring rules C-E1` stood on the table of arXiv:2005.00661 on which the readers failed R-56 and C-E1; it is the owner's decision with a hypothesis, as they are.

The four supported claims are these. Each is supported on the tests named, within the bounds named, and every one carries `fit: transfer`, because no test ran on the repository's own files.

- R-52 claims that a context file written by an LLM does not raise the share of tasks a coding agent resolves above the no-file arm and raises the cost per task. arXiv:2602.11988v3 §4.2 Tables 2–3 found resolution lower by 0.5% and 2% with no significant effect (two-sided Cochran-Mantel-Haenszel test, p = 0.87 and 0.37) and cost higher by 20% and 23% (p < 0.001%), for Claude Code with Sonnet-4.5, Codex and Qwen Code on SWE-bench Lite and CTXBench with each repository's documentation in place; the source's run with that documentation removed went the other way (+2.7%, no test) and lies outside the bounds.
- R-73 claims that documentation commonly holds references to code elements the source has deleted. It rests on arXiv:2212.01479v1 (28.9% of the top 1,000 projects and 5.4% of the google projects) and on the in-scope scan of arXiv:2606.09090v1 reported in section 7.
- S-07 claims that readers shown a set of answers of which some carry a first-person statement of uncertainty answer correctly more often over the set and agree with the shown answers less often. arXiv:2405.00623v2 Table 1 found 72.8% (SE 7.4) against 63.9% (SE 8.6) correct, p < 0.01, and 74.8% against 80.9% agreement, p < 0.05, by a mixed-effects regression, for 404 US MTurk workers on eight yes/no medical questions; within readers, hedged against unhedged answers gave 73.4% against 79.5% agreement, not significant.
- G-24 claims that a subagent spawned by a dynamic workflow can write a file its declared tools do not allow. It rests on issue 63762 of anthropics/claude-code and on issue 81852, where on Claude Code 2.1.220 a named dispatch of the Explore type wrote and edited a file that the unnamed dispatch was refused, with one pair per arm and no test; a maintainer reproduced it on 2.1.233 on Linux for the built-in Explore type only.

The eleven lowered records and what their sources lack:

| Line | Hypothesis | What the source lacks |
|---|---|---|
| R-56 | H-R-56 | arXiv:2005.00661 §5.4 Table 4 gives absolute rank correlations of 0.431 against 0.162–0.197 with no test of the difference and no stated n |
| R-67 | H-R-67 | arXiv:2505.13360v3 Table 3 gives guess rates of 22.9% against 53.2% and 70.7% against 41.1% with no test; the analysis of variance of Table 4 is on pooled accuracy; the rates are the observations the rule was written from (rule 6) |
| R-70 | H-R-70 | ConInstruct arXiv:2511.14342v2 §5.3 Fig. 6(a) gives 79–87% against 38–55% and 48–72% with no test; PRIME arXiv:2606.22470v1 has no arm without the conflict |
| C-B1 | H-C-B1 | Dense X Retrieval arXiv:2312.06648v3 §5.1 Table 3 gives Recall@5 from passages to propositions (SimCSE 34.3 to 46.3, Contriever 43.0 to 52.7, DPR 57.3 to 59.9, GTR 65.2 to 68.0) with no test |
| C-E1 | H-C-E1 | the same table of arXiv:2005.00661 gives no test of the difference between two dependent correlations |
| S-01 | H-S-01 | arXiv:2606.09410v1 tests the bundled change of prompt and schema (Haiku 4.5 +27.7 pp, McNemar p < 0.0001; GPT-4o +16.3 pp, p = 0.0165), but no run holds the schema and the prompt constant across the two orders, and a lighter schema imposed from the first token gains about as much (rules 3, 4 and 7) |
| S-24 | H-S-24 | Sternadori 2008 gives 396.4 against 412.7 ms with F(1,44) = 3.92 printed as p = .05 at an alpha of .05 (exact p 0.054, power .49); the interaction Structure × Sex, F(1,45) = 5.23, p = .03, is 427.67 against 425.20 ms for women; the measure's validity is unchecked (rules 3, 6 and 7) |
| G-05 | H-G-05 | only Gloaguen names a test; the threshold was written after the results; SkillOpt arXiv:2605.23904v2 finds a one-shot skill above no skill on 39 of 52 Table 1 cells (+15.0 on SpreadsheetBench, GPT-5.5 under Claude Code) |
| G-09 | H-G-09 | arXiv:2505.13360v3 §3.4 gives 98.7% falling to 85.0% (gpt-4o) and 79.7% (Llama) with 19 requirements, with no test; the observations are the rule's origin |
| `kb-card-specification § Authoring rules C-E1` | H-kb-card-specification-Authoring-rules-C-E1 | the same table of arXiv:2005.00661 gives correlations of 0.431 against 0.162–0.197 and no test of their difference |
| `kb-card-specification § Principles item 1` | H-kb-card-specification-Principles-item-1 | arXiv:2312.06648v3 Table 3 gives no test, no per-question hits, and a test-set size only for EntityQuestions (20,000) |

Rule 3 of the method reads "A result that compares shares names its test and gives its p-value or interval". The run applied it as written, with no exemption for a test someone else ran and published. A source that prints shares for two arms without a test therefore leaves the claim a hypothesis, however large the gap, and this lowered nine of the ten records. In S-24 the source does name a test, but its printed p = .05 does not clear its own alpha of .05, because the exact p is 0.054. Applying the rule as written is a default decision of the run, shown to the owner. If he grants an exemption for someone else's test, the ten records have to be read again. The same reading applies to the findings of section 6: most of them name no test, so none of them could have raised a standing.

## Research to date, by cluster

Each cluster below opens with what its claims are about, what the new tests show and which lines found nothing new. Its table lists at most six findings, with the source's locator, what was compared and found, and how the finding bears. Where the skeptic gave a verdict, the bearing is the skeptic's.

Cluster 1, routing: a skill's name and description as what an agent picks the skill by (6 hypotheses). The new tests vary one metadata field or one block of a skill document at a time, mostly outside Claude Code. The one test in Claude Code is a blog report of 38 runs with no test. The candidates on what the rest of the listing does to routing stand in section 9. H-R-04, H-R-05 and H-R-06 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-R-01 | arXiv:2610.14334v1 §5.2 Table 2, App. B.2 Table 3 | MCP tools differing in one metadata field, five models: 6 of 29 tool-name estimates have 95% intervals that exclude zero (conditional logit); Claude Sonnet 4.6 on Get Weather 0.65, interval includes zero | bounds |
| H-R-01 | dev.to post by rulestack, § The name counts, but only for the words it contains | Claude Code 2.1.273, claude-opus-5, one skill alone: an opaque name with a vague description invoked 0 of 3 times on a direct and 0 of 3 on an indirect request, a descriptive name with the same description 2 of 2 and 0 of 2; the source names no test | bounds |
| H-R-01 | SkillRouter arXiv:2603.22455v5 App. M.1 (v4 App. L.1) | the cited passage compares two retrievers on case illustrations, not a name by function against a name by topic | none |
| H-R-03 | arXiv:2610.32336v1 §7.3 Table 9 | padding gold skill documents with two or eight sections of other skills costs a one-vector retriever 7.03 and 9.68 MRR@10; section-level retrieval changes by at most +0.37; the source names no test | bounds |
| H-R-77 | arXiv:2610.18927v1 §5.1 Table 7 | 49 tasks: fixing documentation-code inconsistencies raised the verifier pass rate by +0.136 on Claude Haiku 4.5 (0.741 to 0.877), +0.085 and +0.023 on two other models; the source names no test | bounds |

Cluster 2, tiering and context budget: what stays resident, how long a context file may be, what moves to files read on demand (8 hypotheses). Four findings bear against H-R-14, H-R-15, H-R-16 and H-R-18, all outside their lines' scope (section 8). One finding supports H-R-11 outside its scope. The tests of resident against on-demand content in Claude Code find no difference they could detect. Every line of the cluster found something new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-R-11 | arXiv:2608.05604v1 §5.2 Table 2 | SkillsBench, MiniMax-M2.7, at 3.46× compression: task-agnostic token compression R 25.5 against contract-preserving compression 33.3 and the raw graph 31.0; no test for Table 2 | supports, outside scope |
| H-R-16 | arXiv:2610.26632v1 §4 Table 1 | pre-registered probe: a 24,000-token window answered 15/200 against 200/200 with full history when a needed fact could not be looked up again (gpt-6-luna; difference 92.5 points, 90% CI [89.5, 95.5], Holm); claude-haiku-5-5 0/200 against 200/200 | bounds |
| H-R-10 | arXiv:2607.27250v1 §4.1 Table 1 | Claude Code, claude-sonnet-4-6, 15 tasks: AGENTS.md always in the prompt 55.6% (25/45) against wiki files read on demand 55.6% (25/45); omnibus permutation p = 1.000; TOST bounds every difference to under 10 pp; minimum detectable effect over 30 pp | bounds |
| H-R-18 | arXiv:2607.27250v1 §4.1 Table 1 | the same arms read as resident against retrieved content; Codex with gpt-5.5 56.9% (29/51) against 52.9% (27/51), permutation p = 0.66 | bounds |
| H-R-17 | arXiv:2611.22238v1 Table 1, §5 | 201 SWE-bench Verified tasks, three Qwen models: rolling observation masking cost +76% to +116% at a cached-input price of 0.1 and −19% to −25% at 1; preregistered one-sided cost tests, Holm | bounds |
| H-R-17 | arXiv:2610.31778v1 §4.1 Fig. 3 | five compaction strategies against self-summarization, Claude Opus 4.6 among the models: none beats the baseline beyond 95% bootstrap intervals | bounds |

Cluster 3, structure and format of instruction text: headings, lists, tables, emphasis, diagrams (8 hypotheses). The one test inside a line's scope bears against H-R-22 (section 7). The tests of format find small differences, mostly with no test, and the one study of file layout in Claude Code finds no significant effect. H-R-25 and H-R-26 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-R-22 | arXiv:2611.04367v1 Tables 3–4 | one rule in four wordings on claude-opus-5 and claude-sonnet-5 in Claude Code (section 7) | against, inside scope |
| H-R-21 | arXiv:2607.19257v1 §4.5 Table 6 | prose minus plain lines, per-instruction adherence at N = 40 and 80: Haiku +0.9 and −0.3 pp, Sonnet 5 −0.1 and −0.3 pp, no test or interval; the line's measure, every rule met, is at the floor for every format at N = 80 | bounds |
| H-R-21 | arXiv:2607.03158v1 §4.2 Table 3 | one specification as pseudocode, prose or Markdown fields, three models: 0.384, 0.360 and 0.314 of hidden tests; pseudocode over the seven-form average 0.037 [0.010, 0.069]; the source names no test for pseudocode minus prose | bounds |
| H-R-23 | arXiv:2610.22734v1 Tables 6–8 | edge list against Mermaid, claude-sonnet-4-6: 92.1 against 92.7, 80.0 against 81.0, 80.6 against 80.6; the source names no test | bounds |
| H-R-28 | arXiv:2609.03213v1 §2.2, Figs. 3–4 | open 7B–32B models on novel tasks: rules over examples +0.171 (p < .001, linear mixed model); rules with examples over rules alone +0.012, not significant | bounds |
| H-R-20 | arXiv:2605.10039 §4.1 | 1,650 Claude Code sessions, mainly Sonnet 4.6: one CLAUDE.md 67.7%, with AGENTS.md 68.2%, with two nested files 61.7%; GLMM χ² = 3.29, df = 2, p = 0.19 | bounds |

Cluster 4, pointers and duplication: paths and references in instructions, stale pointers, repeated rules (6 hypotheses). Two studies of stale instruction files in Claude Code find that agents follow a stale line and that a corrected line removes the stale path; the precedence sentence one of them tests is a candidate in section 9. Repeating an instruction showed no effect in a small pre-registered study. H-R-40 and H-R-41 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-R-45 | arXiv:2611.09802v1 §IV Table II | Claude Code, Haiku 5.5 and Sonnet 5.5, 732 runs: stale, corrected and removed lines fixed the bug alike (79/80 each in the command case; p = 1.0, exact tests stratified by task, Holm); stale runs used the stale path more than corrected runs (Haiku p = 2×10^-28, Sonnet p = 2×10^-33) | bounds |
| H-R-45 | arXiv:2610.30571v1 §4–5 Fig. 5 | without a precedence sentence 90.1% of scored choices followed the stale file; Codex CLI rewrote existing code in 20 of 80 runs and the project's tests then failed in 17; the source names no test for the pass-rate difference | bounds |
| H-R-44 | arXiv:2610.18522v1 §3.2 Tables 1–2 | golden skills fixed, irrelevant skills added: pooled loaded-skill recall 73.5% with none and 27.6% with 1,000; Claude Opus 4.6 81.3 to 30.9 while Pass@3 stays at 62.2% against 64.9%; the source names no test | bounds |
| H-R-44 | arXiv:2610.14216v1 §1, §5 | Claude Haiku 4.5: a path-gated skill opened in 28 of 66 listings, an always-on skill in 0 of 198; 16 of 18 kept items are rules; descriptive counts, no test | bounds |
| H-R-43 | Zenodo record 24225746 v6, abstract and §3 | three pre-registered experiments, Claude Haiku 4.5 delegates, n = 5 per condition: a repeated whole instruction showed no effect (Fisher p = 1.000; Mann-Whitney p = 1.000 and 0.607) | bounds |
| H-R-46 | arXiv:2610.32648v1 §5.9 Tables 8–9 | a checker of named paths and symbols before each tool call: precision 0.940; the first replacement after a warning cleared the mismatch in 45 of 46 cases; both modes resolved 48 of 79 tasks; the source names no test | bounds |

Cluster 5, sourcing: cited claims in instruction files, context files written by an LLM, dated and versioned statements (4 hypotheses and the supported claim R-52). The new tests of context files and evolved rules bound R-52 under other conditions and do not test a file written by an LLM against no file. The tests of attribution checkers find rankings that invert between datasets. H-R-55 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| R-52 | arXiv:2607.27250v1 §3.3–4.5 Table 1 | developer-written AGENTS.md, Claude Code: none 53.3% (24/45), always on 55.6%, on demand 55.6%; omnibus permutation p = 1.000; the power simulation catches a 30 pp effect 57% of the time | bounds |
| R-52 | arXiv:2610.00650v1 §5.1–5.2 Tables 1–4 | rules written by an LLM and kept by a judge, SWE-bench Lite with gpt-4.1-mini: pass rate 0.330 with no rules, 0.190 with public rules, 0.340 with evolved rules; the source names no test against no rules | bounds |
| H-R-54 | arXiv:2611.04367v1 Tables 3–4 | the same policy with and without its reason: rank-biserial +0.00 on claude-opus-5, not significant, +0.70 on claude-sonnet-5, significant (Wilcoxon signed-rank, Holm) | bounds |
| H-R-56 | arXiv:2606.23915v2 §4 Tables 2, 12, 14 | attribution scorers against human labels: clean MNLI AUROC 0.90 on AttributedQA and 0.53 on LFQA, where BERTScore scores 0.91; rankings invert (Kendall tau = −0.64, p = 0.031) | bounds |
| H-R-56 | arXiv:2607.08700v1 §3–4 Table 2 | eight LLM judges on 624 attribution pairs: Claude Opus 4.6 F1 0.750 [.68, .82], Sonnet 4.6 0.726 [.65, .79], Haiku 4.5 0.708 [.64, .77]; the intervals overlap | bounds |
| H-R-57 | arXiv:2610.32191v1 Tables 13–14 | acquisition-date fields shown against omitted, five open models: Phi-4 −11.3 [−17.7, −4.5], Holm p 0.000067; Mistral-24B −15.2 [−22.0, −9.2]; Qwen2.5-7B −4.7 [−10.6, +0.6] | bounds |

Cluster 6, constraints and wording: emphasis words, negative instructions, examples, numbers, bundled requirements (6 hypotheses). The two findings reported in support of H-R-61 and H-R-60 are bounds after the skeptic's reading, because the Claude rows go the other way or the arm differs from the line's. The tests of phrasing find small or mixed effects. H-R-66 and H-R-67 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-R-61 | arXiv:2610.05278v1 §5.1 Table 2 | 11 models, word-count targets: positive phrasing 49.5 exact, negative 39.0 (−10.4 [−17.1, −4.4], Holm p < .001), NEVER 40.8 (−8.6 [−14.6, −2.6]); Claude Sonnet 4.6 complies more under the negative (60.0) and NEVER (67.0) forms than under the positive (58.3) | bounds |
| H-R-61 | arXiv:2608.11727v1 §4.1–4.3 | 12 models including Claude Opus 4.7: rules that require and rules that forbid fail at 23.8% against 20.8%; the source names no test for these shares | bounds |
| H-R-61 | arXiv:2604.07192 §4, §5.3 | over 830 calls, 11 models: three encodings of the same constraints show no difference (all χ² tests p > 0.05); no positive against negative phrasing of one constraint is compared | bounds |
| H-R-60 | arXiv:2611.20195 §VII-A Table I | 72 students coding with ChatGPT-4o: failures of 33 hidden tests 21.54, 19.67 and 11.38 without a specification, with a template and with a full behavioural specification; F(2, 69) = 26.77, p < 0.001; full against none IRR 0.48, pHolm = 0.205 | bounds |
| H-R-64 | arXiv:2610.33201v1 §4.1 | 14 open models: inside one message the first of two conflicting lines wins 72.42 to 94.66% of decided replies; in realistic context the later line wins in 25 of 26 model-modes; at most 2.92% flag the conflict; 95% bootstrap intervals, Benjamini-Hochberg | bounds |
| H-R-62 | arXiv:2608.11513v1 §4.1 Tables 2, 5 | five open models: a Pressure framing lowered LiveCodeBench correctness (Neutral > Pressure, p = 0.002); on SWE-bench Verified the tactic effect is not significant (p = 0.45) | bounds |

Cluster 7, anti-patterns: contradicting instructions, vague rules, redundancy, personas, instruction conflicts (6 hypotheses and the supported claim R-73). The in-scope scan for R-73 stands (section 7). Two findings support H-R-70 and H-R-76 more weakly than reported, because their arms remove or rename more than the lines' comparisons do. Every line of the cluster found something new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| R-73 | arXiv:2606.09090v1 §3.3 Tables 1–3 | the scan of arXiv:2212.01479 run unchanged on AI configuration files (section 7) | supports, inside scope |
| H-R-70 | arXiv:2610.25064v1 §4 Fig. 2(a) | 16 constructed same-job skill pairs, seven models: a skill's rules followed 93–99% alone and 61–62% beside a same-job skill; 95% bootstrap intervals on each share and none for the difference; the alone arm removes the whole second skill, not only the contradicting rule | supports, weaker |
| H-R-76 | arXiv:2611.00544v1 App. C Table A3 | router Claude Haiku 4.5, FC@5 at session 9: original 36.4, differentiation plus exclusion 61.6 (+25.3) with no interval for that arm; the full package with renaming 76.3, paired bootstrap 95% CI 32.3–47.5 | supports, weaker |
| H-R-76 | arXiv:2610.11647v2 §4.2 Fig. 5 | 312 same-job pairs in Claude Code: a co-installed similar skill lowers use of the installed one by 19.9 pp [−23.1, −16.7]; no arm sharpens the descriptions | bounds |
| H-R-71 | arXiv:2611.02383v2 Table 1 | 386 pairs of corresponding sections across coexisting instruction formats: 62 (16.1%) divergent, 0 contradictory, Cohen's κ = 0.85; a count, with no comparison | bounds |
| H-R-75 | arXiv:2508.02053v2 §4.5 Table 2 | GPT-4.1 mini: uncompressed 0.817, sections dropped by attribution 0.752, LLM compression 0.462, random sections 0.343; the source names no test | bounds |

Cluster 8, security of instruction files: prompt injection through skills and context files, tool privileges, untrusted payloads (3 hypotheses). The new tests measure review, scanning and confirmation against malicious changes, mostly on models other than Claude, and the human-approval results are simulated or come from an oracle. None compares the lines' arms directly. Every line of the cluster found something new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-R-84, H-R-82 | arXiv:2608.02693v1 Table 2, Fig. 5 | malicious changes among 24 benign pull requests: whole-window review detects 16–22% against 50–60% per pull request; the source names no test | bounds |
| H-R-84 | arXiv:2611.01976v1 §5 Table 4 | static LLM review of tool updates: 98.3% detection for readable malicious updates, 6.7±7.0% for obfuscated ones; the source names no test | bounds |
| H-R-84 | arXiv:2608.19901v1 §6.4 Table 3 | three scanners on 9,740 skills: 2.5% and 0% recall at 1.1% and 0.55% benign false positives, 25.3% recall at 49.9%; the source names no test | bounds |
| H-R-84, H-R-85 | arXiv:2606.05647v3 §4.2 | over 100 developers, five hours each: 83 of 88 failed to detect sabotage without a monitor; with a Claude Haiku 4.5 monitor sabotage succeeded in 12 of 19 (p = .01 against 18 of 19; the passage names no test) | bounds |
| H-R-85 | arXiv:2611.11571v1 Table 2 | simulated human approval: an adaptive campaign of 25 attempts succeeded in 100% against in-prompt defences and 64% with approval and taint tracking; simulation only | bounds |
| H-R-85 | arXiv:2609.18411v2 §8.1 Table 10 | agentic browser, 293 trials: attack success 78% with no gate, 72% with a confirmation built from the page summary, 0% with a card bound to the pending action; the source names no test | bounds |

Cluster 9, output style part one: the shape of an agent's answer to a human reader, S-01 to S-13 (9 hypotheses and the supported claim S-07), searched since 2026-08-01. Three findings support H-S-01, H-S-06 and H-S-13 more weakly than reported, because their arms or measures differ from the lines'. The finding reported against H-S-12 bears on no line after the skeptic's reading. H-S-11 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-S-01 | arXiv:2610.35328v1 Table 6 | ten open models, GSM8K: free reasoning followed by JSON scores above JSON from the first token on 8 of 9 models; the schema and the format description differ between the strategies | supports, weaker |
| H-S-01 | arXiv:2610.12056v1 Table 1 | Claude-Sonnet-4.5 on GSM8K: free form 86.50, XML answer first 62.35, XML reasoning first 97.65; the source names no test for the accuracy differences | bounds |
| H-S-06 | arXiv:2611.08975v2 §6.2–6.4 Table 2 | omitting entailed spans against truncation to the same length: wins 9–0 and 10–0, exact Wilcoxon p = 0.004 and 0.002, on automatic NLI coverage; no human reading of the truncation arm | supports, weaker |
| H-S-13 | arXiv:2610.34809v1 §4.2 Table 3 | Qwen3.5-27B on 300 items: an assertive note raised error by 16.2 points (95% interval 14.1 to 18.3) over a hedged note; both arms carry the same speaker frame | supports, weaker |
| H-S-12 | Isch et al. 2026, Nature Human Behaviour, Fig. 5 | 1,105 adults: rewriting causal language lowered causal wording in readers' summaries (OR 0.38, P < 0.001; 71.3% to 49.6%); a methodological note after the abstract OR 0.73, P = 0.078; no direct test of rewrite against note | none |
| S-07 | arXiv:2610.32883v1 §5.1–5.2 | 5,151 participants, chatbot confidence indicators: main effect on perceived accuracy F(5, 5115) = 2.527, p = .027, with no pairwise difference after correction | bounds |

Cluster 10, output style part two and present-design prose: structure in answers, sentence shape, traces of a superseded design in documents and code comments, S-20 to S-25 and D-01 to D-06 (12 hypotheses), searched since 2026-08-01. The tests of stale and superseded text find agents following it, under conditions other than the lines'; one of them yields a candidate in section 9. The tests of reading come from human readers of other kinds of text. H-D-05, H-S-22 and H-S-24 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-D-01 | arXiv:2611.09802v1 §IV Table II | stale against removed line: the stale path used in 78/80 against 1/80 runs (command) and 55/80 against 20/80 (procedure); the source names no test for this contrast | bounds |
| H-D-02 | arXiv:2611.09802v1 §IV Table II | corrected against removed line: the stale path used in 0/80 against 1/80 and 0/80 against 20/80 runs; the source names no test | bounds |
| H-D-01 | arXiv:2609.38866v2 App. F.4 Tables 18–20 | full update history against a current-state snapshot: Claude Opus 4.8 answered 18/40 against 40/40; the source names no test | bounds |
| H-D-04 | arXiv:2512.20334v2 §5.1 Table 3 | defective commented-out code in completion prompts raised defects in every tool, model and position, by up to 58.17%; an instruction to ignore it cut them by at most 21.84%; no test | bounds |
| H-S-20 | Royal Society Open Science 7:190876, §3 | 2,305 UK adults: a fact box 79.6% against matched text 69.7% correct, F(2, 2302) = 113, p < 0.0001, d = 0.39 [0.31, 0.47] | bounds |
| H-S-25 | Front. Lang. Sci. 5:1912839, §3.6.1 | 79 children: nominalization, passive and active clause did not differ in dwell time (χ²(2) = 0.79, p = 0.673) or accuracy | bounds |

Cluster 11, knowledge-base cards part one: atomic notes, facets and controlled vocabulary, titles and theses (14 hypotheses and the supported claim `kb-card-specification § Authoring rules C-E1`). The new tests of memory stores, scope statements and compression bound the card rules under retrieval conditions; one preregistered test of a summary field is a candidate in section 9. H-C-A3 and `kb-card-specification § Authoring rules C-E1` found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-C-B1, H-kb-card-specification-Principles-item-1 | arXiv:2611.09807v1 §5.1 Table 1 | atomic facts against transcript chunks on 1,985 LoCoMo questions: 71.4 against 64.6 on four categories (McNemar exact p = 5.5e-08); 63.4 against 61.4 on all five (p = 0.085) | bounds |
| H-C-C1 | arXiv:2611.09807v1 §5.2 | dates resolved to absolute form against relative phrases: 71.7 [66.5, 76.3] against 46.1 [40.7, 51.6], McNemar exact p = 1.1e-14 | bounds |
| H-C-C3 | arXiv:2609.35155v2 §4.3 Table 3 | out-of-scope error 70.8% with the scope visible and 22.6% with a sharpened stated scope; the source gives no interval for this contrast | bounds |
| H-C-B2 | arXiv:2606.29251v3 §4.4, App. E Table 6 | a compressor that keeps context facts lowered decision flips from 31.5% to 21.2% on MD&A; −8.8 [−14.6, −3.1] under Claude Haiku 4.5 | bounds |
| H-kb-card-specification-Authoring-rules-C-C3 | arXiv:2610.10170v1 Tables 1–2 | structure-aligned chunks with real heading paths above contextualized windows (+0.0218, Holm p = 0.017) and above shuffled heading paths (+0.0099, p = 0.017) | bounds |
| H-C-A1, H-C-A2 | agent-docs-spec issue 40 | one practitioner, Claude Sonnet: descriptive filenames led to the right file first in 12/12 runs against 0/12 for generic names; the source names no test | bounds |

Cluster 12, knowledge-base cards part two: body blocks, links, retrieval units and corpus integrity (8 hypotheses). The new tests concern retrieval of skills and tools and the naming of relations, and measure no agent action on a card. H-C-D2, H-C-E3, H-C-F1, H-C-F2 and H-C-F3 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-C-D1 | arXiv:2610.32336v1 §5.2 Table 5 | moving a skill's embedding toward LLM-written requests: +3.10 MRR@10 fine-tuned and +4.80 untuned; a control with nothing specific to any skill adds 1.67 of the 3.10; retrieval only; no test | bounds |
| H-C-D1 | arXiv:2610.30867v2 Table 1 | past requests folded into a tool index raised labelled-test Hit@5 by 14 and 29 points and lowered held-out Hit@5 from 0.733 to 0.400; paired bootstrap intervals | bounds |
| H-C-D1 | arXiv:2610.32336v1 §7.3 Table 9 | eight sections of other skills cost the one-vector retriever 9.68 MRR@10; section-level retrieval changes by +0.08 to +0.37; no test | bounds |
| H-C-E1 | arXiv:2606.23915v2 §4 Table 2 | clean MNLI AUROC 0.904 on short claims, +0.270 over lexical overlap [0.198, 0.347]; on long-form LFQA 0.531 against BERTScore 0.909 (−0.378 [−0.500, −0.238]) | bounds |
| H-C-E2 | arXiv:2609.39913v1 §4 Table 1 | familiar relation words against defined nonce predicates: +35.6 [30.6, 40.6] down to +5.4 [3.2, 7.8] points across four models; two-sided exact McNemar, Holm | bounds |
| H-C-E2 | arXiv:2611.02273v1 Stage 2 | under missing evidence a named public figure drew the remembered occupation in 17.0% [14.5, 19.3] of labels (GPT-5.6 Luna) and in none (Claude Sonnet 5.5) | bounds |

Cluster 13, how the audit is built, part one: G-01 to G-13 and the skill's phases (11 hypotheses and the line G-12). The new tests of one check per agent against one agent with all checks find small or mixed differences, and two findings support H-SKILL-md-When-this-skill-is-invoked and H-G-09 more weakly than reported. A test of skills rewritten without feedback bounds H-G-05. H-SKILL-md-Phase-3 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-SKILL-md-When-this-skill-is-invoked | arXiv:2610.27488v1 §4.1 Table 2 | three agents with two requirements each against one agent with six: +0.100 masked defects caught on Haiku 5.5 (98.75% interval [0.028, 0.175]), −0.004 on Sonnet 5.5; more false alarms on all four models; tokens 2.2 to 2.4 times | bounds |
| H-SKILL-md-When-this-skill-is-invoked | arXiv:2608.12342v1 App. F.1 Table 6 | one error type per query against all types at once: whole-document recall higher in four of five open models, lower on DeepSeek-R1-0528-Qwen3-8B and in the chunk arm; the source names no test | supports, weaker |
| H-SKILL-md-When-this-skill-is-invoked | arXiv:2609.29769v3 App. N Table N2 | whole rubric minus one criterion at a time: +1.5 [+0.4, +2.6], +1.4 [+0.5, +2.3] and +0.3 [−0.7, +1.4] points; bootstrap over units, Holm | bounds |
| H-G-09 | arXiv:2610.36095v1 §5.3.3 Figs. 7–8 | gpt-4o-mini with 1 to 256 rules: −0.43 ± 0.10 logits per doubling of the rule count, a 95% interval that excludes zero | supports, weaker |
| H-G-09 | arXiv:2610.27190v1 §3 Fig. 2 | k tasks concatenated into one prompt: Claude Opus 5 loses about 7 pp at k = 10 on GPQA-Diamond; no named test | bounds |
| H-G-05 | arXiv:2611.25534v1 §3 Fig. 1 | skills rewritten by the model for thirty rounds without feedback: 15 points lower on SkillsBench; LogicBench 86.2% to 71.4%; the source names no test | bounds |

Cluster 14, how the audit is built, part two: G-14 to G-28, smaller models for narrow checks, tool allowlists, self-generated skills, workflow mechanics (11 hypotheses and the supported claim G-24). The in-scope test for H-G-17 stands (section 7). A test of debate among judges bears against H-G-16 outside its scope (section 8). The tests of history editing, approval and memory audit bound H-G-15, H-G-18 and H-G-26. H-G-20 and H-G-22 found nothing new.

| Line | Source and locator | Compared and found | Bears |
|---|---|---|---|
| H-G-17 | arXiv:2610.11647v2 §3.8, §4.2 | same-job skill pairs in Claude Code (section 7) | supports, inside scope |
| H-G-17 | arXiv:2610.18522 abstract | 1,000 irrelevant skills: loaded-skill recall from 73.6% to 27.4%; the abstract names neither the models nor a test | bounds |
| H-G-15 | arXiv:2611.14654v1 §4.1, §5.1 | a truthful note naming the error raised recovery to 65.78% [62.54, 68.97], +15.20 pp [12.46, 18.00] over a neutral note; a cleaned history −6.43 pp [−8.88, −3.97] | bounds |
| H-G-18 | arXiv:2610.22987v1 §4.1–4.3 Tables 1–2 | planted content elicited a broad allow-rule in 58% of instances; once the rule was granted, the planted goal completed silently in 47 of 58 (81.0%); the source names no test | bounds |
| H-G-26 | arXiv:2610.04083v1 §V Fig. 12 | an auditor reading each memory note cut propagation from 71% to 34% of runs; with the memory tool removed, agents wrote the goal to a file in 74% of sessions; no test | bounds |
| G-24 | claude-code issues 81852 and 63762 | Claude Code 2.1.220: a named dispatch of Explore wrote a file its unnamed dispatch was refused; reproduced on 2.1.233 on Linux; one pair per arm, no test | bounds |

## Tests that ran inside a claim's scope

H-R-22 claims that an agent applies the rules of a body that writes each rule in the style that fits it, all five styles present, more accurately than the same rules all written as prescriptive imperatives, for files of this repository read by Claude models in Claude Code. arXiv:2611.04367v1 §2–3 Tables 3–4 appended one mechanically checkable policy to the developer-written context files of 86 CTXbench tasks in four wordings (prescriptive, explanatory, conditional, prohibitive) and ran Claude Code 2.1.227 with claude-opus-5 (n = 82) and claude-sonnet-5 (n = 81), three runs per task. Compliance in the four wordings was 78.0, 77.2, 64.2 and 70.7 on claude-opus-5 (Friedman χ²(3) = 17.68, p < 0.001) and 71.6, 49.4, 35.6 and 17.3 on claude-sonnet-5 (χ²(3) = 102.02, p < 0.001). Prescriptive over conditional gave a rank-biserial of +0.65 and +0.89, significant by the Wilcoxon signed-rank test with Holm correction. The authors name two threats: one text per style, and 86 tasks from 10 repositories, so the p-values may be optimistic. The result bears against the claim. H-R-22 stays a hypothesis with this result recorded, for three reasons: the test swaps the style of one rule instead of comparing a mixed five-style body with an all-prescriptive one, it measures no over-application, and a single failure waits for its repetition under rule 7. Card R-22's statement that the conditional style matters most needs a recheck against this result, and it is the second question put to the owner.

R-73 claims that documentation commonly holds references to code elements that the source no longer holds; its refuter is a scan of hundreds of repositories against their history that finds none. arXiv:2606.09090v1 §3.3 Tables 1–3 ran the checker of arXiv:2212.01479, with its regular expressions and its definition of staleness unchanged, on 612 AI configuration files (CLAUDE.md, AGENTS.md, Copilot instructions, GEMINI.md, .cursorrules and others) of 356 repositories drawn at random (seed 42) from 4,420 eligible ones. It found at least one stale reference in 82 of 356 repositories (23.0%, 95% CI 18.8–27.2%) and 230 stale references among 18,048 (1.27%); one author found 32 of 50 detected elements genuine. The skeptic found the test inside the line's scope. R-73 stays supported, because the refuter is not met. Its fit stays `transfer`, because no test covers skills, agent prompts, documents, code or answers. The authors read 23.0% as a signal of feasibility rather than a precise prevalence, and with 64% precision on a sample of 50 the share of repositories holding a genuine stale reference is not estimated. The record's transfer and validity fields stand as they were; validity still reports the older source's three raters (kappa 0.92), while the new scan rests on one author's check of 50 elements.

H-G-17 claims that in a library of skills, descriptions with disjoint triggers route a request to the intended skill more often than descriptions whose triggers overlap a sibling's, for Claude Code routing among this repository's plugin skills. arXiv:2610.11647v2 §3.8 and §4.2 ran 312 confirmed same-job pairs in Claude Code 2.1.283 with claude-sonnet-4-6, claude-haiku-4-5 and claude-opus-5, one run per model, configuration and pair, 6,368 runs in all. Against the installed skill alone, a similar skill beside it lowered use of the installed skill by 19.9 pp (95% CI [−23.1, −16.7]), an unrelated skill by 5.9 pp ([−8.5, −3.3]), and the similarity accounts for a further 14.0 pp ([−17.2, −10.9]); the intervals are computed over pairs. The interval excludes zero in the claim's direction. H-G-17 stays a hypothesis, because the test's conditions differ from the claim's in three ways: it varies the sibling's job together with its description instead of rewording two descriptions of one library; its skills sit in project scope with the listing cap raised to 20,000 characters from a measured default of 6,000 to 8,000, while the same paper finds a same-name plugin skill used in only 2.9% of runs, so scope moves routing; and its measure counts reads of the skill's files beside its activation. The maintainer is asked whether same-job project-scope pairs may stand for the line's overlapping triggers; if they may, the standing becomes `supported` with `fit: transfer` naming these differences.

## Tests against a claim

Six findings bear against a claim after the skeptic's reading. One of them, against H-R-22, ran inside the claim's scope and is reported in section 7. The other five ran outside it.

H-R-18 claims that content an agent reuses within a session gives a higher share of correct answers when it is in the context than when it is retrieved through MCP or search. arXiv:2610.26836v2 had agents run the PHREEQC simulator on 158 verified multiple-choice items, with the simulator's report given inline or retrieved through a table of contents or by regular-expression search. Retrieval minus inline was −0.6 pp [−3.8, +2.5] (pHolm 1.000) on Claude Opus 4.6, −0.5 pp [−3.8, +3.2] (pHolm 1.000) on Claude Sonnet 4.6, −7.9 pp [−14.9, −0.9] (pHolm 0.128) on GPT-5.2 and −11.3 pp [−18.0, −4.9] (pHolm 0.005) on GPT-5.1, by item bootstrap and sign-flip permutation tests. On the two Claude models inline content is ahead by 0.5 and 0.6 pp, which the test cannot tell from zero, and the intervals allow an inline advantage of up to 3.8 pp. Sonnet's single search run scored 89.2% against 91.1% inline, with no test. The test differs from the claim's scope: it reads one simulator output once per question rather than content reused across a session, and its retrieval is file navigation and regular expressions, not MCP or vector search.

H-R-16 claims that for a skill that keeps conversational state, summarizing or truncating turns older than the last 20 keeps the task success rate at least as high as keeping every turn, at a lower input token count. arXiv:2611.09662v1 §3.4 and §4.4 Fig. 5 compared full history, retention of user messages plus the last three, and a recency suffix of the same token count on 16 synthetic families with Qwen2.5-14B and Mistral-7B. Correct counts for Qwen were 33 and 32 with full history, 52 and 2 to 3 with retention, and 13 and 13 with recency (direct and reference-dependent cases); Mistral stayed at the floor. The authors call these descriptive results with no test. Retention cut prompt tokens by 30.08% and 31.53%. The test differs from the claim's scope: its readers are small open-weight models, its cases are synthetic, its suffix is token-matched rather than the last 20 turns, and its measure is a three-slot state match on short prompts, not task success over long sessions.

H-R-14 claims that a load-bearing rule placed in the first 30% of a SKILL.md or agent file is followed more often than the same rule placed later. arXiv:2601.18554v1 §4.3 Fig. 2 (the MOSAIC benchmark) measured the compliance of the constraint at each rank in lists of 1 to 20 constraints for seven models. Claude 3.7 Sonnet, Gemini and Mixtral show recency, and Claude spikes at rank 19 and drops at rank 20. The result is shown in a figure only, and the source names no test. Position is confounded with list length, because late ranks come only from long lists. The test differs from the claim's scope: it uses Claude 3.7 Sonnet and a list of output constraints in one generation prompt, not a rule in a SKILL.md read in Claude Code, and it gives no split at 30%.

H-R-15 claims that when a skill asks for an artifact longer than 232 tokens, asking for it in bounded segments or iterative edits gives a higher share of artifacts that meet the skill's constraints than asking for it in one response. arXiv:2609.05779v1 Table 2 fine-tuned two models under 1B parameters on Flutter/Dart editing, either to emit the whole file or to apply a sequence of search-and-replace edits. The share passing `dart analyze` was 0.802 [0.783, 0.820] whole against 0.347 [0.325, 0.369] by edits for Rainbow-Pony-100M and 0.900 [0.885, 0.913] against 0.501 [0.478, 0.524] for Qwen2.5-Coder-0.5B, with Wilson 95% intervals that do not overlap and no test beyond them. The edit arm received about ten times the fine-tuning tokens and no execution feedback between edits. The test differs from the claim's scope: its models are trained per regime rather than prompted Claude models, it covers iterative edits only and not bounded segments, and it reports no artifact lengths.

H-G-16 claims that for subjective scoring a three-round debate between two agents ending in a judge's verdict agrees with human preference more often than a single-pass LLM judge. arXiv:2608.30373v1 compared a single judge with consensus debate between a strict and a lenient judge and with symmetric debate between two neutral judges, on 600 Korean essays and 700 SummEval summaries, with six judges at temperature 0. The single judge agreed better than consensus debate (paired bootstrap with 10,000 resamples, p < 0.0001 on both tasks). For symmetric debate, the arm nearest the claim, the only test is p = 0.32 on SummEval, and on Qwen3.5-27B symmetric debate beats the single judge on both tasks. The test differs from the claim's scope: its measure is RMSE and Spearman correlation on pointwise rubric scores rather than the share of pairwise verdicts that match a human label, its verdict is the mean of the two debaters' scores rather than a judge's call, and it used no Claude model.

Two findings reported as against moved on the skeptic's reading. The prose-against-plain comparison of arXiv:2607.19257v1 Table 6 bounds H-R-21, because its differences carry no test and the line's measure stands at the floor in every format. The rewrite-against-note comparison of Isch et al. 2026 bears on no line, because the source tests no rewrite against a note directly.

## Candidates for a rule

Fourteen tested findings concern a question no line covers. They are grouped below by the paper they rest on. Three questions went to the owner as decision cards, and he answered them on 2026-11-22. The precedence sentence (first group) is rule card R-48, in force as the owner's decision with the hypothesis H-R-48: the measured sentence stood in a user-level instruction file, and the rule asks for it in a project's own file. The number of binding rules (second group) is no rule and waits as the hypothesis H-09. Card R-22, which is not a candidate and stands in sections 7 and 8, asks for the condition of a rule to be named and does not require the conditional form of the sentence. Every other candidate stays in this note.

The precedence sentence, arXiv:2610.30571v1 §3, §5.1–5.5, Figs. 5–6 (three findings, in clusters 4, 7 and 10). Owner's decision card 1. The candidate is a sentence in a context file that gives the existing code precedence over the file wherever the two disagree and asks the agent to report each disagreement. The authors built 40 synthetic Python projects in which the instruction file asks for one convention and the code uses the other, across 16 kinds of choice in both directions. Claude Code 2.1.302 with Claude Sonnet 5.5 and Codex CLI 0.163.0 with GPT-6 Sol each added a feature, with and without the sentence in the user-level file, in 320 runs with 720 scored choices per condition. Choices matching the existing code rose from 4.2% to 91.4% (658 of 720), +87.2 points, 95% interval 83.6 to 90.9 from resampling projects; the source names no test beyond that interval. Per agent the shares are point values: Claude Code 7.5% to 94.4%, Codex CLI 0.8% to 88.3%. Without the sentence Claude Code named the conflict in 79 of 80 runs, while 86.2% of its choices in those runs still matched the file. The skeptic found the following missing: the sentence was tested only in the user-level file, so its placement in a project file is untested; the rise in the test pass rate comes from Codex CLI alone, since Claude Code rewrote no existing code in either condition; and the stale lines state the old convention as a current command, not as sentences that read only as corrections, so H-D-01 stays untested.

The number of binding rules and the markup of a rule block, arXiv:2607.19257v1 (two findings). Owner's decision card 3 concerns the first of them. The first candidate is that a resident file keeps the number of simultaneously binding, checkable rules low, on the order of 10 to 20, and moves situational rules to files read on demand. Table 4 gives the share of replies that meet every rule as 0.938, 0.750, 0.238, 0, 0 and 0 for Claude Sonnet 5 and 0.850, 0.594, 0.119, 0, 0 and 0 for Claude Haiku at N = 10, 20, 40, 80, 120 and 160 rules, 160 trials per model and N; the source gives no test or interval for the decay. The block held 5 structural rules and N − 5 rules that forbid or require words in one short essay. The skeptic found that the paper is not peer-reviewed, that its own guidance treats about 40 rules as a redesign point, and that it leaves splitting the rules across turns, tools or a validation pass untested. The second candidate is that markup in a context file is chosen for the human reader's navigation and not to raise the agent's adherence. Table 5 gives markdown minus plain per-instruction adherence from −0.003 to +0.021 for Claude Haiku over six values of N, five of six positive; the source names no test. The skeptic found that the token overhead of 1.258 times was measured on another corpus with another tokenizer.

Worked examples in clashing skills, arXiv:2610.25064v1 §3–5, App. C (two findings). The candidate is that where two co-loaded skills govern the same output, each worked example satisfies the rules of both, or the two are merged, since a priority line alone does not keep the other skill's rules. On 16 constructed same-job skill pairs and seven models (Qwen3-4B, Qwen2.5-7B, Mistral-7B, Llama-3.1-8B, Phi-4-mini, Qwen3-235B, GPT-4.1), one skill took over in 45–78% of outputs with the skills' examples and 7–41% with the examples removed, with 95% bootstrap intervals over jobs on each arm and none for the difference. With one example that satisfies both skills, takeover fell to 1–15% on six models. A priority instruction left 62–71% of achievable rules followed and takeover in 36–82%. A file merged by Claude Opus 5.5 reached 96–99% on all seven models. The skeptic found that on Phi-4-mini the listing position, not the example, decides the winner, and that the range 45–78% lies below half on some models.

Corrected rather than deleted stale lines, arXiv:2611.09802v1 §III–IV Table II. The candidate is that an audit checks each path, command or location in an instruction file against the repository and corrects a stale one rather than deleting it. Three real stale lines, each stale, corrected or removed, were run on 22 bug-fix tasks in Claude Code 2.1.316 with Claude Haiku 5.5 and Claude Sonnet 5.5, 732 runs. Stale runs used the stale path more than corrected runs (exact tests stratified by task, Holm: Haiku p = 2×10^-28, Sonnet p = 2×10^-33). Corrected against removed, the stale path was used in 0 of 80 against 20 of 80 runs in the procedure case, and the source names no test for that contrast. The skeptic found that the location line was never followed in any condition (0 of 84), so not every stale line costs the agent work.

A small skill listing, arXiv:2610.18522v1 §4 Tables 7–8. The candidate is that a session's skill listing holds only the skills its work needs. With 1,000 irrelevant skills on 10 tasks and three open models, one run per task and model, loaded-skill recall was 18.3 with the original listing and 63.3 with the other skills' descriptions masked; the source names no test. The skeptic found that the harness is a Terminus-style one with a load call, not Claude Code, and that each variant rests on about 30 runs.

Differentiating descriptions, arXiv:2611.00544v1 App. C.2 Table A3. The candidate is that a skill's description names what sets it apart from the closest other skill in the listing and what work it does not cover. With Claude Haiku 4.5 as router and the library grown to 731 skills, FC@5 was 36.4 with the original descriptions and 61.6 (+25.3) with differentiation plus an exclusion clause, with no interval for that arm. The full package, which also renames colliding skills, reached 76.3 with a paired bootstrap 95% interval of 32.3–47.5. The skeptic found that the finding credited the full package's gain to the description changes alone.

Imperative trigger wording, a relay at techbytes.app (19 Nov 2026) of a GitHub report. The candidate concerns trigger wording in descriptions. In Claude Code with eight specialized skills beside twelve others, a trigger that appeared only mid-task invoked the skill in 14 of 15 runs on Sonnet under "ALWAYS" wording, 7 of 15 under "Use when" and 3 of 13 under "Rules for X"; the source names no test. The skeptic found that the primary report carries no model versions, and the finding itself proposes nothing until that report is opened.

Process rules lost at compaction, arXiv:2610.31778v1 §4.2, Fig. 4. The candidate is that a skill or agent prompt that compacts its history keeps its process rules and prohibitions in the resident system prompt or a file. Per compaction, GPT-5.3-Codex dropped 2.73 of three rule categories on average, GPT-5.4 1.76 and Claude Opus 4.6 0.51. In 44 real Claude Code sessions with 269 constraints, the drop rate was 6.2% for feature requirements (n = 96), 35.9% for process instructions (n = 39) and 36.8% for scope exclusions (n = 38), with Wilson 95% intervals per category and no test for the ratio. The skeptic found that the one model in the repository's scope, Claude Opus 4.6, drops 0.51 of 3, that a second judge reverses the order of process and scope, and that the remedy is untested.

Reasons kept for the maintainer, arXiv:2608.11095v1 §4.3, App. B.2. The candidate is that each instruction of a resident context file carries its reason in a comment the reading agent does not load, so that a later audit can remove an instruction whose reason no longer holds. With claude-haiku-4-5 as maintainer and executor, after 51 rounds the prompt grew by 211.3% (±105.3) beyond its hidden cover without comments and by 1.4% (±22.1) with them, at 44.0% satisfaction in both arms. In a second set of 64 worlds with distractors, comments raised the score from 50.4% to 62.0% (+11.6 pp, CI [5.1, 18.3]) under a claude-haiku-4-5 judge and by 7.8 pp [0.6, 14.9] under a second judge; a placebo had no effect. The skeptic found that the protocol leaves 12.1% of prompts empty against 2.4% without comments, that it prunes below the hidden cover where the cover is three instructions, and that the authors themselves name acting on a comment to delete as the risk.

A summary field on each card, arXiv:2607.04576v2 §5.1–5.5. The candidate is that each card's frontmatter carries a one-line summary that a retrieval tool can return as a gist. In a preregistered test of 960 runs of claude-opus-4-8 on a 709-page wiki, the arm with the summary field and a gist tool cost 30%, 34% and 58% less than the baseline under three tool conditions, with bootstrap intervals that exclude zero. Pooled quality changed by +0.01 (−0.27, +0.26), within the non-inferiority margin of 0.5, but under forced preload by −0.39 (−1.01, +0.19), where non-inferiority was not established. The human judge agreed with the model judge at a weighted kappa of 0.23 against a gate of 0.60. The skeptic found that the contrast also carries the earlier arm's state extraction and the gist tool, so it does not isolate the summary field.

## Norms

Ten norm findings bear on a line, and they added twelve norm segments to the provenance lines. A norm prescribes; it is not a test of the line beside it. The documents were fetched on 2026-11-22 unless the table says otherwise.

| Document and issuer | What it prescribes | Line | Fetched |
|---|---|---|---|
| Anthropic, Prompting best practices, § Be clear and direct | "Provide instructions as sequential steps using numbered lists or bullet points when the order or completeness of steps matters." | H-R-21 | 2026-11-22; the page prints no revision date |
| Anthropic, Prompting best practices, § Tool use | for Claude Opus 4.5 and 4.6 only, "The fix is to soften any aggressive language", replacing "CRITICAL: You MUST use this tool when" with "Use this tool when" | H-R-27 | 2026-11-22 |
| Anthropic, Prompting best practices, § Use examples effectively | relevant and diverse examples in example tags; "Include 3–5 examples for best results." | H-R-28 | 2026-11-22 |
| Anthropic, Prompting best practices, format and tool-use guidance | "Tell Claude what to do instead of what not to do"; a bare "NEVER use ellipses" replaced by the same rule beside its reason | H-R-61, H-R-62 | 2026-11-22 |
| Anthropic, How we built Claude Code auto mode (engineering post, published 2026-03-25) | per-action approval stays the default; auto mode replaces the prompts with a classifier and an injection probe, and "is not a drop-in replacement for careful human review on high-stakes infrastructure" | H-R-85 | read through a summarizing fetch; the material records no fetch date |
| Anthropic, Claude Code docs: Skills; Create custom subagents, § Preload skills into subagents | descriptions are in context and the full content loads when a skill is invoked; a subagent's skills field preloads the listed skills at startup | G-12, H-G-01 | 2026-11-22 |
| Anthropic, Claude Code docs: Skills, § Troubleshooting | for a skill that does not trigger: check the description's keywords, rephrase, invoke it directly, and for a plugin skill measure the trigger rate across realistic prompts | H-G-13 | 2026-11-22 |
| Agent Skills specification, § Validation; Claude Code docs: Skills | the validators check frontmatter and naming; `claude plugin validate` (v2.1.233 and later) finds unparseable frontmatter; `/doctor prompt-audit` (v2.1.283 and later) checks for conflicting or outdated instructions; none checks a body against its description | H-G-11 | 2026-11-22 |
| Anthropic, Claude Code docs: Plugins reference, § name; Plugin loading, § Versions and updates | every plugin component is namespaced under the plugin's name; an update does not replace the cached copy when the recomputed version matches the installed one | H-G-27 | 2026-11-22 |
| Anthropic, Claude Code docs: Workflows, § Pass input to a saved workflow, and the Workflow tool input reference it links | args arrive as structured data; "Pass arrays and objects as actual JSON values, not as a JSON-encoded string" | H-G-28 | 2026-11-22 |

One further finding reported as a norm, the moved appendix of SkillRouter that the test field of H-R-01 cites, bears on no line after the skeptic's reading.

## The skill's own tests

Three of the skill's own hypotheses compare shares over the same 24 planted sentences, two to each of twelve generated notes. `plugins/evidence-based-authoring/skills/auditing-ai-context/evals/absent-rule/absent_rule_eval.py score` prints an exact McNemar test, two-sided, for each comparison. The protocol stands in `plugins/evidence-based-authoring/skills/auditing-ai-context/evals/absent-rule/protocol.md`, and the records in `maintenance/pending-evidence.md`.

| Hypothesis | Comparison | Shares | Discordant sentences | p | Standing |
|---|---|---|---|---|---|
| H-03 | trace pass against the audit's cards as shipped | 22/24 against 9/24 | 13 caught by the pass alone, none by the cards alone | 0.0002 | supported, on one run |
| H-05 | cards shown the deleted lines against cards as shipped | 21/24 against 9/24 | 12 against none | 0.0005 | supported, on one run |
| H-06 | trace pass against cards shown the deleted lines | 22/24 against 21/24 | 2 against 1 | 1.00 | hypothesis; the run went against the claim |

The test was chosen after the run, and it takes the sentences as independent, though they stand two to a note. The records of H-03, H-05 and H-06 state both facts. Under rule 7 the failure of H-06 waits for its repetition. The cases are generated notes, so every record of these hypotheses is a transfer to the repository's own documents. The evidence on what such sentences are and how they are detected is reviewed in `research/2026-11-20_argument-with-an-absent-rule.md`.

## Open questions

These are what a next run should settle.

The owner's decisions that the run could not take:

- Whether rule 3 exempts a test someone else ran and published. The eleven lowered records turn on the answer.
- Whether same-job project-scope pairs may stand for the overlapping triggers of H-G-17.

The records a maintainer should revisit:

- R-73: the transfer and validity fields were not updated with the new scan.
- G-24: the transfer field could record that issue 63762 was closed by a bot for inactivity on 2026-07-02, not as fixed, and that issue 81852 was closed the same way on 2026-10-21 after being marked a confirmed bug.
- H-R-01: its test field cites SkillRouter App. L.1, which bears on no line after the skeptic's reading.
- G-12: a kept session on a Claude Code version the repository runs, with the context captured before the Skill tool fires, would test the claim that a skill's body is absent from the context until the skill is invoked.

The sources left unopened:

- From the re-verification: the full text of Cleveland & McGill 1984, Ferreira's 2020 accepted manuscript, Lang 1989, Ibrahim et al. 2012, and the three observations of the repository's own behind G-27 and G-28.
- From the research, 30 candidate sources. Those nearest a line are doi:10.1080/0163853X.2025.2462514 (Discourse Processes 2025, HTTP 403; H-S-04), DeAngelo & Yegiyan 2019, doi:10.1177/1077699018792272 (H-S-24), arXiv:2610.27801 (H-SKILL-md-Phase-3), arXiv:2608.14036 and arXiv:2608.11888 (H-G-05), and the GitHub report behind the techbytes.app relay.
- Others named by the researchers: arXiv:2608.04828 (seen only as a summary), arXiv:2609.35692, arXiv:2610.11007, arXiv:2607.17598, arXiv:2611.13709, arXiv:2409.19001, arXiv:2608.25730, arXiv:2606.19191, arXiv:2609.12001, arXiv:2605.19952, arXiv:2610.31193, arXiv:2610.04352, arXiv:2609.04961, arXiv:2502.04134, arXiv:2608.16071, arXiv:2608.04482, the supplement of arXiv:2606.29645, Reiss (ICSE 2008), and a session-start-hook post at towardsdatascience.com that a block kept from loading.
- Two sources hold no results yet: arXiv:2611.22017 and the registered report arXiv:2611.23266v1, which plans 20,400 trials and Boschloo's exact test.

The claims with no test found. Twenty-four lines found nothing new. Seventeen of them carry no test field at all in `maintenance/pending-evidence.md`: H-R-04, H-R-06, H-R-25, H-R-26, H-R-40, H-R-41, H-R-55, H-S-22, H-C-A3, H-C-D2, H-C-E3, H-C-F1, H-C-F2, H-C-F3, H-SKILL-md-Phase-3, H-G-20 and H-G-22. The other seven (H-R-05, H-R-66, H-R-67, H-S-11, H-D-05, H-S-24 and `kb-card-specification § Authoring rules C-E1`) keep the earlier tests their records name.

The tests that would have to run on the repository's own files:

- H-G-20, H-G-22, H-G-27 and H-G-28, which concern this skill's own audit machinery.
- G-24 and H-SKILL-md-Phase-1, on the dynamic-workflow path, on a current Claude Code version.
- H-R-22, on a mixed five-style body against an all-prescriptive one, with a measure of over-application.
- H-G-17, rewording two descriptions of one library.
- The precedence sentence, placed in a project-level file.
- H-06, a second run.

## Sources

Each work the note reports on is listed once, under the cluster that cites it first. The material records authors for few of the research sources. A work is listed with its authors or issuer where the repository's files or the material name them, and otherwise by its title. The sources left unopened are named in section 12 by identifier and are not listed here.

| Cluster | Work | Identifier | Date | Read |
|---|---|---|---|---|
| 1 | Zheng et al., SkillRouter | arXiv:2603.22455v5 (v4 cited before) | 2026-07-20 (v5) | full text |
| 1 | Dong et al. | arXiv:2512.14754v3 | v3 | full text |
| 1 | Which Metadata Matters for LLM Tool Selection in MCP? Evidence from Controlled Factor-Level Interventions | arXiv:2610.14334v1 | 2026-10-09 | full text |
| 1 | rulestack, Will Claude Code call your skill on its own? 38 runs, one skill, seven ways to describe it (blog post, not reviewed) | https://dev.to/rulestack/will-claude-code-call-your-skill-on-its-own-38-runs-one-skill-seven-ways-to-describe-it-203m | 2026-09-20 | full text |
| 1 | SkillRep: Characterizing and Understanding the Representation Design Space of Agent Skill Retrieval | arXiv:2610.32336v1 | 2026-10-23 | full text |
| 1 | Why Static Skill Inconsistencies Do Not Equate to Runtime Risks: A Behavioral Analysis of LLM Agent Execution | arXiv:2610.18927v1 | 2026-10-13 | full text |
| 1 | Lost in Implicit Routing: How LLM Agents Fail to Load Relevant Skills at Scale | arXiv:2610.18522v1 | 2026-10-13 | full text; one finding by its abstract alone |
| 1 | Skill++: Towards Lifelong Agents via Routing-Aware Skill Refinement | arXiv:2611.00544v1 | 2026-10-31 | full text |
| 1 | techbytes.app, Attempts to improve skill discovery in Claude Code (relay of a GitHub report, not reviewed) | https://techbytes.app/posts/attempts-to-improve-skill-discovery-in-claude-code/ | 2026-11-19 | full text of the relay |
| 2 | Lindenbauer et al., The Complexity Trap (NeurIPS 2025 workshop) | arXiv:2508.21433v3 | 2025-10-27 | full text |
| 2 | Bulle Labate et al. | arXiv:2511.22729v1 | v1 | full text |
| 2 | Do Context Files Help Coding Agents? A Two-Agent Ablation Study on Real Repositories | arXiv:2607.27250v1 | 2026-07-28 | full text |
| 2 | Same Simulation, Different Evidence: Where Retrieved Tool Output Costs LLM Agents Accuracy | arXiv:2610.26836v2 | 2026-11-16 | full text |
| 2 | Context Has a Price: Adding and Removing Context for LLM Coding Agents under Prefix Caching | arXiv:2611.22238v1 | 2026-11-17 | full text |
| 2 | Benchmarks Are Surprisingly Compaction-Friendly | arXiv:2610.31778v1 | 2026-10-22 | full text |
| 2 | When the harness decides success: state that cannot be re-observed | arXiv:2610.26632v1 | 2026-10-19 | full text |
| 2 | How Much Conversation History Does an AI Agent Need? | arXiv:2611.09662v1 | 2026-11-06 | full text |
| 2 | Deconstructing Instruction-Following: A New Benchmark for Granular Evaluation of Large Language Model Instruction Compliance Abilities | arXiv:2601.18554v1 | 2026-01-26 | full text |
| 2 | SkillZip: Contract-Preserving Graph Compression for Scalable Agent Skill Libraries | arXiv:2608.05604v1 | 2026-08-06 | full text |
| 2 | Diffs vs. Whole Files: An Empirical Comparison of Iterative Edit-Based and Direct Generation for Flutter/Dart Code Models | arXiv:2609.05779v1 | 2026-09-05 | full text |
| 2 | Prompt Design at Scale: How Format, Instruction Count, and Context Length Shape Instruction Adherence and Hallucination in Large Language Models | arXiv:2607.19257v1 | 2026-07-21 | full text |
| 2 | Why Does CLAUDE.md Keep Growing? Catastrophic Remembering in Agentic Coding | arXiv:2608.11095v1 | 2026-08-11 | full text |
| 3 | Chatlatanagulchai et al. | arXiv:2509.14744v1 | 2025-09-18 | full text |
| 3 | Do Coding Agents Follow AGENTS.md? The Effect of Policy Wording on Instruction Compliance (submitted to IEICE Transactions) | arXiv:2611.04367v1 | 2026-11-03 | full text |
| 3 | Which Algorithm Specification Formats Help Language Models Implement Machine Learning Algorithms? | arXiv:2607.03158v1 | 2026-07-03 | full text |
| 3 | Graph Serializations for Reasoning LLMs: A Study Across Knowledge Extraction and Structural Reasoning | arXiv:2610.22734v1 | 2026-10-15 | full text |
| 3 | LLMs Learn Better In-Context from Rules than from Examples | arXiv:2609.03213v1 | 2026-09-02 | full text |
| 3 | Instruction Adherence in Coding Agent Configuration Files: A Factorial Study of Four File-Structure Variables | arXiv:2605.10039, version not recorded | 2026-05 | full text |
| 3 | Anthropic, Prompting best practices (Claude Platform Docs) | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | no revision date; fetched 2026-11-22 | full text |
| 4 | When Instruction Files Go Stale: Documentation Debt and Hidden Cost in Coding Agents | arXiv:2611.09802v1 | 2026-11-06 | full text |
| 4 | Stale Instruction Files Override the Code in Coding Agents: A One-Sentence Fix | arXiv:2610.30571v1 | 2026-10-22 | full text |
| 4 | Cortex: Measurement-Gated Evolution and Pruning of Coding-Agent Skills and Rules | arXiv:2610.14216v1 | 2026-10-09 | full text |
| 4 | Ceiling Effects and Convergence: Null Results for Instruction Repetition in LLM-Agent Pipelines | Zenodo record 24225746, v6 | 2026-11-14 | full text |
| 4 | StateMirror: Pre-Execution Detection of Hallucinated Tool Calls in Coding Agents | arXiv:2610.32648v1 | 2026-10-23 | full text |
| 5 | Gloaguen et al. | arXiv:2602.11988v3 | 2026-09-29 (v3) | full text |
| 5 | Li et al., SkillsBench | arXiv:2602.12670v4 | v4 | full text |
| 5 | Maynez et al., On Faithfulness and Factuality in Abstractive Summarization (ACL 2020) | arXiv:2005.00661 | 2020 | full text |
| 5 | Self-Evolving Coding Rules for AI Coding Agents | arXiv:2610.00650v1 | 2026-09-30 | full text |
| 5 | Do LLM Attribution Metrics Transfer? Auditing Retrieval-Augmented Generation Evaluation Across Datasets and Constructs (GroundLM workshop, EMNLP 2026) | arXiv:2606.23915v2 | 2026-09-16 | full text |
| 5 | Do You Need a Frontier Model as a Citation Verifier? Benchmarking Rubric LLMs for Deep-Research Source Attribution | arXiv:2607.08700v1 | 2026-07-09 | full text |
| 5 | Collection-Date Assignment Redirects Answers in Temporal QA | arXiv:2610.32191v1 | 2026-10-23 | full text |
| 6 | Khan et al. | arXiv:2510.22251v1 | v1 | full text |
| 6 | Yang et al. | arXiv:2505.13360v3 | v3 | full text |
| 6 | When Verifiable Counts Depend on Wording: Auditing Wording Robustness in Instruction Following | arXiv:2610.05278v1 | 2026-10-04 | full text |
| 6 | Harness-IF: Evaluating Instruction Following Across Instruction Surfaces in Coding Agents | arXiv:2608.11727v1 | 2026-08-12 | full text |
| 6 | Compact Constraint Encoding for LLM Code Generation: An Empirical Study of Token Economics and Constraint Compliance | arXiv:2604.07192, version not recorded | 2026-04 | full text |
| 6 | How Specification Explicitness Shapes Failure in LLM-Generated Code (ICSE 2026, authors' preprint) | arXiv:2611.20195, version not recorded | 2026-11-15 | full text |
| 6 | Position, Role or Label? A Controlled Study of Instruction Conflicts in LLM Agents | arXiv:2610.33201v1 | 2026-10-23 | full text |
| 6 | Do Influence Tactics Matter? Investigating Prompt Framing Effects in LLM Code Generation (Empirical Software Engineering, accepted manuscript) | arXiv:2608.11513v1 | 2026-08-11 | full text |
| 7 | ConInstruct | arXiv:2511.14342v2 | v2 | full text |
| 7 | PRIME | arXiv:2606.22470v1 | v1 | full text |
| 7 | Tan, Wagner and Treude | arXiv:2212.01479v1 | 2022 | full text |
| 7 | Toward an Evidence-Based Template for Agent Instruction Files: An Empirical Study of Adoption, Consistency, and Maintenance | arXiv:2611.02383v2 | 2026-11-02 | full text |
| 7 | One Skill Takes Over: Clashing Agent Skills and a One-File Fix | arXiv:2610.25064v1 | 2026-10-18 | full text |
| 7 | One Skill Too Many: How Co-Installed Skills Conflict in Coding Agents | arXiv:2610.11647v2 | 2026-10-13 | full text |
| 7 | Context Rot in AI-Assisted Software Development: Repurposing Documentation Consistency for AI Configuration Artifacts | arXiv:2606.09090v1 | 2026-06-08 | full text |
| 7 | ProCut: LLM Prompt Compression via Attribution Estimation | arXiv:2508.02053v2 | 2025-08-04 | full text |
| 8 | PRWeaver: Evaluating LLM-Based Code Auditors against Long-Horizon Malicious Pull Requests | arXiv:2608.02693v1 | 2026-08-03 | full text |
| 8 | Beyond Prompt Injection: The Tool Update Gap in LLM Agent Security | arXiv:2611.01976v1 | 2026-11-01 | full text |
| 8 | MaliciousSkillBench: A Comprehensive Benchmark for Malicious Agent Skill Detection | arXiv:2608.19901v1 | 2026-08-20 | full text |
| 8 | Coding with the Enemy: Can Human Developers Detect AI Agent Sabotage? (NeurIPS 2026, as its footer prints) | arXiv:2606.05647v3 | 2026-11-04 | full text |
| 8 | Treating the Model as an Untrusted Component: Deterministic Policy Enforcement, Human Approval and Taint Tracking Against Prompt Injection in Tool-Using Agents, with Validation on Open-Weights Models | arXiv:2611.11571v1 | 2026-11-08 | full text |
| 8 | The Verifiable Action Card: Trustworthy Human-in-the-Loop Control for Secure Autonomous Agents | arXiv:2609.18411v2 | 2026-09-30 | full text |
| 8 | Anthropic, How we built Claude Code auto mode: a safer way to skip permissions | https://www.anthropic.com/engineering/claude-code-auto-mode | 2026-03-25 | full text, through a summarizing fetch |
| 9 | Kim et al. (FAccT 2024) | arXiv:2405.00623v2, doi:10.1145/3630106.3658941 | 2024 | full text |
| 9 | the source of S-01 | arXiv:2606.09410v1 | v1 | full text |
| 9 | IH-Benchmark | arXiv:2607.25987v3 | 2026-11-16 | full text |
| 9 | Cleveland and McGill (Journal of the American Statistical Association) | http://euclid.psych.yorku.ca/www/psy6135/papers/ClevelandMcGill1984.pdf | 1984 | an OCR copy of a scan; the full text not opened |
| 9 | Constrained Decoding: Harmful or Beneficial? Revisiting Its Impact on LLM Performance | arXiv:2610.35328v1 | 2026-10-26 | full text |
| 9 | Structure Tax: How Structured Output affects LLMs Performance | arXiv:2610.12056v1 | 2026-10-08 | full text |
| 9 | Beyond Truncation: When Can LLMs Safely Omit Generated Text? | arXiv:2611.08975v2 | 2026-11-15 | full text |
| 9 | Isch et al., Quantifying the prevalence and impact of overreaching causal claims in social science (Nature Human Behaviour) | doi:10.1038/s41562-026-02553-x | 2026-08-24 | full text |
| 9 | Position Matters More Than Channel: Talking a Language Model Out of a Correct Answer | arXiv:2610.34809v1 | 2026-10-26 | full text |
| 9 | When Should I Trust This? Designing and Evaluating Factuality Indicators for LLM-based Chatbots | arXiv:2610.32883v1 | 2026-10-23 | full text |
| 10 | Sternadori, PhD dissertation, University of Missouri-Columbia | dissertation | 2008 | full text |
| 10 | Lang | doi:10.1080/08838158909364093 | 1989 | Crossref and OpenAlex records only |
| 10 | Ferreira, accepted manuscript | doi:10.1037/amp0000620 | 2020 | not opened (HTTP 403) |
| 10 | Ibrahim et al. (Journal of Systems and Software) | doi:10.1016/j.jss.2011.09.019 | 2012 | not opened (paywalled) |
| 10 | When Context Changes: Understanding Update Failures in LLMs | arXiv:2609.38866v2 | 2026-09-30 | full text |
| 10 | Comment Traps: How Defective Commented-Out Code Augment Defects in AI-Assisted Code Generation (Proc. ACM Softw. Eng., FSE 2026) | arXiv:2512.20334v2 | 2026-02-18 | full text |
| 10 | Risk communication in tables versus text: a registered report randomized trial on 'fact boxes' (Royal Society Open Science 7:190876) | https://pmc.ncbi.nlm.nih.gov/articles/PMC7137953/ | 2020-03 | full text |
| 10 | Processing event nominalizations in developing readers: eye-tracking evidence from bilingual and dyslexic readers (Front. Lang. Sci. 5:1912839) | doi:10.3389/flang.2026.1912839 | 2026-10-28 | full text |
| 11 | Chen et al., Dense X Retrieval: What Retrieval Granularity Should We Use? (EMNLP 2024) | arXiv:2312.06648v3 | 2024 | full text |
| 11 | Compaction, decay and reinforcement in a two-tier conversational memory: a paired evaluation against retrieval-augmented generation | arXiv:2611.09807v1 | 2026-11-06 | full text |
| 11 | Right Facts, Wrong Rule: Scope-Transfer Poisoning of Retrieval-Augmented Generation | arXiv:2609.35155v2 | 2026-10-19 | full text |
| 11 | When Summaries Distort Decisions: Information Fidelity in LLM-Compressed Financial Analysis | arXiv:2606.29251v3 | 2026-09-17 | full text |
| 11 | Does Document Structure Help Dense Retrieval? A Placebo-Controlled Ablation of Four Mechanisms Across Two Corpora | arXiv:2610.10170v1 | 2026-10-07 | full text |
| 11 | agent-docs-spec issue 40, Can agents find the documentation they need in a Git repository? Experiments (GitHub issue, not reviewed) | https://github.com/agent-ecosystem/agent-docs-spec/issues/40 | 2026-09-29 | full text |
| 11 | Progressive Disclosure for LLM-Maintained Wiki Knowledge Bases: a Preregistered Ablation | arXiv:2607.04576v2 | 2026-10-07 | full text |
| 12 | Folding Pooled Usage Examples into the Tool Index Lowers Retrieval of Unused Tools | arXiv:2610.30867v2 | 2026-10-22 | full text |
| 12 | The Concrete-Arbitrary Gap: Kinship Reasoning in LLMs Is Not Indifferent to Presentation | arXiv:2609.39913v1 | 2026-09-30 | full text |
| 12 | When the Text Is Silent: Memory Shortcuts and the Validity of LLM Annotation under Evidence Insufficiency | arXiv:2611.02273v1 | 2026-11-01 | full text |
| 13 | SWE-Skills-Bench | arXiv:2603.15401v2 | 2026-10-27 | full text |
| 13 | CoEvoSkills | arXiv:2604.01687v3 | v3 | full text |
| 13 | SkillOpt | arXiv:2605.23904v2 | v2 | full text |
| 13 | Liu et al. | arXiv:2604.14228v3 | 2026-10-10 | full text |
| 13 | The More the Better? A Comparison of Single- and Multi-Agent LLM Setups on a Financial Review Task | arXiv:2610.27488v1 | 2026-10-20 | full text |
| 13 | Are Large Language Models Reliable Reviewers? A Benchmark for Error Detection in Financial Documents | arXiv:2608.12342v1 | 2026-06-03 | full text |
| 13 | Decision Models vs. LLMs as Rubric Judges: Cheaper, Faster, and Wrong in the Same Places | arXiv:2609.29769v3 | 2026-10-13 | full text |
| 13 | Instruction Capacity: Behavior and Degradation of Language Models under Controlled Load | arXiv:2610.36095v1 | 2026-10-26 | full text |
| 13 | On the Fragility of Tasks under Composition: Implicit Budgeting in Language Models | arXiv:2610.27190v1 | 2026-10-19 | full text |
| 13 | How Feedback-Free Self-Evolution Reshapes Agent Skills: A Systematic Study | arXiv:2611.25534v1 | 2026-11-19 | full text |
| 13 | Anthropic, Claude Code Docs: Skills; Create custom subagents | https://code.claude.com/docs/en/skills; https://code.claude.com/docs/en/sub-agents | fetched 2026-11-22 | full text |
| 13 | Agent Skills Specification | https://agentskills.io/specification | fetched 2026-11-22 | full text |
| 14 | Abdelnabi et al. | arXiv:2605.17634v2 | 2026-11-15 | full text |
| 14 | Beyond Consensus: Downward Bias and Role Asymmetry in Multi-Agent LLM Judges for Subjective Evaluation | arXiv:2608.30373v1 | 2026-08-31 | full text |
| 14 | Cleaning an Agent's History Hurts When the World Still Holds the Error | arXiv:2611.14654v1 | 2026-11-10 | full text |
| 14 | From Approval to Abuse: Privilege Escalation Attacks on Harness-Protected Coding Agents | arXiv:2610.22987v1 | 2026-10-16 | full text |
| 14 | Self-Propagating Misalignment in LLM Agents, and Why Auditing or Disabling Memory Is Not Enough | arXiv:2610.04083v1 | 2026-10-02 | full text |
| 14 | Anthropic, Claude Code docs: Plugins reference; Plugin loading | https://code.claude.com/docs/en/plugins-reference.md; https://code.claude.com/docs/en/plugins/loading.md | fetched 2026-11-22 | full text |
| 14 | Anthropic, Claude Code docs: Workflows | https://code.claude.com/docs/en/workflows.md | fetched 2026-11-22 | full text |
| 14 | anthropics/claude-code issue 63762 | https://github.com/anthropics/claude-code/issues/63762 | closed 2026-07-02 | full text |
| 14 | anthropics/claude-code issue 81852 | https://github.com/anthropics/claude-code/issues/81852 | 2026-08-25 (maintainer comment) | full text |
