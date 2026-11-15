# A description that argues with a rule its reader never saw — evidence report on detecting it

A rewrite of this repository's method prose left sentences such as "The scientific method is neither a sequence of steps nor a demand for a citation". The text they argued with — the earlier rule that every rule cites a source — stood in the lines the rewrite deleted, so a reader of the new text met a denial of something the text never presented. The audit of the skill `auditing-ai-context` ran over one of the files and returned nothing. The question of this report: how is such a sentence detected reliably — by a script, by a model acting as a reviewer, by a human reader, or by a process?

What the readings and the pilot yield:

- The defect has a definition. A denial is in place where the denied proposition is stated in the text, expected by its reader or inferable from what the text says; the defect is a denial whose target is none of the three.
- By wording alone a script finds every candidate and rules on none: the seven rarest markers of denial stand in 24 of 35 ordinary commits of this repository.
- The judgement of licence is moderately reliable in people — agreement between trained annotators lies between 0.47 and 0.58 on the nearest published tasks — and weak in automatic judges.
- A model reviewer leans towards accepting. The measured gains come from handing it candidates a deterministic step proposed, from showing it the reference it lacks, from asking for evidence, and from combining several readings by a rule tilted towards flagging.
- Instructions to the author do little: models wrote reader-unavailable content into a third of their outputs under an explicit instruction to leave it out.
- No study, tool or benchmark found here measures the detection of this defect itself. The design at the end of this report is therefore a set of hypotheses, each with the outcome that would refute it.

[Sources](#sources) holds 64 entries. Six source searches opened them; the compiler of this note re-opened ten of the load-bearing ones. Each entry says how it was seen.

## What was investigated and why

The owner of the repository read the rewritten `README.md` and named the defect in his own words: the text is written as an argument with some rule, and a reader cannot tell with which. The audit had read the method file once per card and flagged nothing, although two cards cover the neighbouring ground: D-06, on an alternative named as the foil of a decision, and R-61, on prohibitions addressed to an agent.

Three things were unknown: whether the defect is a known object with a criterion, which detectors exist and how reliable they are, and what would make a reviewer — a model or a person — find it dependably.

## Method

**The pilot.** Before the source search, the audit was run again on the text as it stood with the sentences in it, under seventeen combinations of card, file and inventory, and a probe counted what a script finds by wording in this repository's history. The material, the predictions written before the runs, their outcomes and the commands are in `plugins/evidence-based-authoring/skills/auditing-ai-context/evals/absent-rule-pilot/protocol.md`.

**The source search.** Six searches, each by a separate reader with one question: the pragmatics of denial; the NLP tasks nearest to the defect; research on writers and readers; the contrast construction in model output and its detectors; the reliability of a model as a judge; inspections of documents in software engineering. Each reader opened its sources, quoted them and marked how each was seen: `full text`, `abstract only` or `relay` — a text reporting another. Most pages were read through a fetch tool that returns extracts written by a small model, so a quote is the tool's extract of the page unless an entry says the text was read directly.

**Verification.** The compiler re-opened ten sources on which the conclusions lean: the encyclopedia entry on negation, the study of the Mandarin construction, the evaluation of questions under discussion, the comparison of experts with readers, the documentation style rule, three papers on model judges, one inspection experiment and one proofreading study. Nine were read through the same extracting fetch tool and the inspection experiment as the text of its PDF. Every re-opening agreed with the reader's account.

**Limits.** No source tests the defect on expository documents or on rewritten texts: the experiments use single sentences, pictures, narratives, news, questions or translations, and the transfer to a design note is this report's own step. The pilot read each combination once and is fitted to the one case it grew from. The searches ran in English.

## What the defect is

### The licence of a denial

The encyclopedia entry on negation states the ordinary use: "the prototypical use of negation is indeed as a denial of a proposition attributable to, or at least considered by, someone relevant to the discourse context", and reports that negation is easier to process when the denied proposition is in the discourse model or is a plausible addition to it [1], a result the entry takes from Wason's experiment on the contexts of plausible denial [4]. Givón's example, relayed by two sources, is "my wife is not pregnant": odd out of the blue, natural once the pregnancy has been discussed [2].

The experiments agree on the direction. Reading times of negative sentences fall when the negated proposition was mentioned earlier or can be inferred from the text, while affirmative sentences are unaffected [5]. A negation that rejects what "plausibly may have been true" is integrated as fast as an affirmative; one that rejects what no reader would have thought is not [6]. A context made of discourse markers alone leaves the cost in place, and an extended context that builds the denied expectation removes it [7]; in a verification task a simple induced context likewise left the effect of negation, and an enriched one diminished it [13].

A reader of a denial with no context supplies the missing question. In an eye-tracking study, readers of a plain negative looked to the picture of the positive state shortly after the verb, and a cleft sentence that carried its own question removed the effect [8]. In Roberts's theory of discourse a supplied question is accepted only when it belongs to the line of inquiry already under way [9]. A denial whose question comes from an earlier version of the document meets neither condition: the reader builds the foil and then finds no line of inquiry for it.

Linguists have a diagnostic for content that a sentence takes for granted. A hearer may answer "Hey, wait a minute — I had no idea that …" to presupposed content that was never established, and cannot give that answer to what the sentence asserts [10]. The test responds to any content outside the point at issue [11], so it marks a foil taken for granted and marks legitimate background as well.

The licence has three sources, and a stated counterpart is only one of them. In Tottie's conversation data, relayed by a handbook chapter, denials of something merely expected outnumber denials of something asserted [3]; facilitation appears for inferred propositions as for mentioned ones [5]; accommodation of an unstated presupposition is described as the rule [12]. The defect is therefore the narrow case: the denied thing is stated nowhere in the document, the document's reader has no reason to expect it, and nothing the document says implies it.

The style norm on the matter is a century old and cites no study: "the reader is dissatisfied with being told only what is not; he wishes to be told what is", with one allowance, the antithesis that names both sides [19].

### Why the author misses it

Flower's account of writer-based prose names the mechanism. Such prose "reflects the associative, narrative path of the writer's own confrontation with her subject" and uses "shifting but unexpressed contexts for her statements"; its fragments "are perfectly adequate for the writer" [14]. A denial aimed at the text the writer has just replaced is an unexpressed context of exactly this kind — an inference of this report from Flower's description.

The writer's own reading does not repair it. Writers of every level of experience evaluate their own texts worse than texts by others [15]. People who know a term overestimate how many others know it [18]. Better-informed agents fail to reproduce the judgement of less-informed ones even when paid to; market incentives halved that bias and left the other half [17].

### Why a model writes it

The construction is a measured habit of model output. Five commercial models writing Mandarin use "not X, but Y" 2.5 to 9.2 times as densely as a human reference; in an annotated sample, 24.1% of 307 model uses reject an X for which the context gives no cue, against 12.1% of 33 human uses [21]. In English creative writing "It's not X, it's Y" runs up to 6.3 times the human rate in some models [22]. The density is low in base checkpoints and rises with supervised fine-tuning and with preference optimisation, and three of five reward models prefer the construction whether or not the correction is needed [21]. Editors of an encyclopedia list the construction among the signs of machine writing and describe its effect: the text "may seem as though it is clearing up a common misconception" [24].

Models also write in what their reader lacks. Asked to generate the question a sentence answers, and told to use nothing first introduced in that sentence, three models did so in 31% to 34% of their questions; crowd workers did in 11% [29].

For an author that is a model the same sentence therefore has two origins: a habit of emphasis, and a trace of the superseded text or of the working conversation. One practitioner count, unreviewed, puts comments that narrate the edit or the chat at 13.8% of 400 commits co-authored by a coding agent against 0.5% of 400 commits of 2021 [27].

## What detects it, and how reliably

### By wording alone

Cue and scope of a negation are found by sequence models at 91 to 96 token-level F1 within a domain [32], and the focus of a negation — what exactly is denied — at 76 F1 on newswire [31]. Open tools match the contrast construction by regular expression: a sampler that backtracks on a match [22], a score that gives the pattern a quarter of its weight [23], several rule packs for a prose linter [26]. None of their sources reports a precision, a recall or a false-alarm rate, and none looks for the denied thing elsewhere in the document; one of them says so: "An alert says a line matched a pattern, and the line may still be right" [26]. A review of model tics reaches the same point: surface matching requires contextual annotation [25]. A rule set for sentences that lean on missing context — a pronoun, a connective, a sentence that opens on "but" — reached 0.76 precision on Swedish corpus sentences [37]; a sentence of the form "X is neither A nor B" carries none of those marks. A style guide for documentation names the harm — text that assumes "the reader is familiar with earlier versions of the product" — and checks for it by a list of time words, which a sentence such as "X is neither A nor B" does not contain [20].

The probe on this repository agrees. Over the 35 earlier commits that add up to 700 lines of design prose, twelve markers of denial and contrast nominate a sentence in 30, and the seven least frequent of them in 24. On the commit in question they nominate 29 sentences, of which the later rewrite changed 26. A marker separates nothing: an ordinary commit carries more of them per line than the commit in question.

Picking the deleted rule's own terms automatically, by their rarity in the repository, failed on this case: the word that mattered, "citation", stands throughout the repository's reference lists. With the terms named by hand, the list of added sentences that name a term or carry a strict marker held 36 sentences in 8 files and every sentence the owner later named.

### The judgement of licence: people

The nearest published judgements are made by trained annotators with moderate agreement. On the Mandarin construction two annotators with a linguistics background agreed on substantive, optional or defective in 77% of 100 cases, κ = 0.58, and on seven finer labels at κ = 0.52 [21]. On whether a question uses only what the prior context gives, three annotators reached α = 0.48 [29]. On whether a sentence can be made to stand alone, experts reached κ = 0.51 and crowd workers 0.30 [30]. On implicit relations between sentences, contrast and concession among them, published expert agreement lies between 0.47 and 0.58 [36]. None of the sources opened reports agreement above about 0.6 on whether something in a sentence is supported by the text before it.

Experts reading for the reader do worse than readers. Technical writers and subject experts asked to predict the problems readers had reported in a brochure predicted under 15% of them and agreed little with one another [16].

### The judgement of licence: models

Automatic judges of the nearest criteria sit near chance. For the givenness of a question the best classifier scores 0.37 macro-F1 against 0.32 for a random baseline, and a model used as a scorer rated model-written questions above human ones [29]. On detecting a false or unverifiable assumption in a question, the best models of 2022 and 2023 reached 64% where chance is 50% [34], and 67 macro-F1 where a question-only baseline reaches 67 [33]. Two current judges asked to rate answers with a general rubric preferred the "not X, but Y" wording to an affirmative one and showed no difference between licensed and unlicensed uses: all four intervals of that difference include zero [21].

A model reviewer accepts more readily than it rejects. Fourteen models judging the validity of feedback on student programs accepted valid items at above 96% and rejected invalid ones at below 25% [45]. In span-level error detection in translation the best system of 2025 recovered 11% of the error characters people had marked, at 28% precision, where a second person recovered 48% at 47% [41]. A prompted model listing error spans found 25% to 75% of the major errors at 10% to 25% precision [42], models lag people most on minor and rare errors [43], and in reasoning traces the best model of 2023 located the first mistake in 53% of cases [44]. Model code reviewers found about a quarter of seeded and real bugs and "largely detect the same bugs" [50]. One comparison is more favourable: on span annotation of data-to-text output three models "mostly reach or surpass human agreement" [53].

Run-to-run flips concentrate on hard items: the fifteen questions that flipped most averaged 24% flips and the rest 3%, and switching sampling off lowered the mean flip rate from 13% to between 3% and 8% [40]. With sampling on, three judges agreed with themselves across runs at α between 0.27 and 0.79 [38]. A judge that repeats its verdict can repeat a wrong one [39].

The pilot fits this picture. The headline sentence was flagged in 12 of 12 readings and had been passed in the one reading of the first audit; six quieter sentences were flagged in 0 to 2 of 6 readings each. A draft card with a second question — does the file itself present the denied thing — did no better than the shipped one, and handing the reviewer the 20 nominated sentences, with a request for a verdict on each, brought flags on 5.

### What raises a model reviewer's reliability

- **A deterministic step proposes, the model classifies, and a dismissal needs evidence.** Models adjudicating the alerts of static analysers reached at least 98% recall and 94.8% specificity on three suites, with each query run ten times, agreement below 80% returned as "uncertain", and uncertain treated as a weak positive because a miss costs more than a false alarm [49]. The domain has an executable ground truth that prose lacks.
- **The judge is shown what it lacks.** With a reference answer a judge's grading failures on 20 mathematics questions fell from 14 to 3 [48]. A study of seven benchmarks, seen by its abstract, reports that what a judge is shown mattered more than which judge was used [52]. In the pilot the shipped card flagged four sentences per file with the deleted lines beside it and one without them.
- **Readings are combined by a rule tilted towards flagging.** Marking an item invalid when 4 of 14 judges said so rejected 30.9% of invalid items where a majority vote rejected 19.2% [45]. A majority vote over three runs of one judge adds 1 to 2.5 points of accuracy [38], and a panel of three models beats its best member by at most 0.015 κ [46].
- **Checklists buy agreement between judges.** Yes-or-no questions raised agreement among twelve judges from α = 0.09 to 0.48 and their correlation with people by about 0.10 [47].
- **A formal check beats a reviewer where the defect can be formalised.** Deterministic detectors caught 27 of 27 seeded defects of the classes they were built for; a single-prompt model reviewer caught 11 [51].

No source found here isolates the effect of asking a judge to quote its evidence, gives a judge the difference between two versions of a document, or measures the union of repeated readings by one model on a span task.

### Readers and inspections

Software engineering has measured for decades how well readers find defects in documents, and four of its results bear on the design.

A single reader finds a minority of the defects. Professional developers reading requirements documents alone found 21% to 32% of the known defects [54]; three-person teams of graduate students found 24% to 57% [55], and teams of professionals 15% to 43% on the same material [56]. The team's meeting added nothing net: what it gained was offset by what it lost [55].

Independent readers add up. Nine teams of three that inspected one requirements document separately found 78% of its injected faults together where one team found 35%, with little overlap between the teams — the figures of a 1992 experiment as two later texts relay them [57][58][64]. Under independence every added reader raises the expected coverage [58]. Estimates of what remains, made by capture and recapture, run low and are inaccurate with fewer than four readers [61].

A focused question per reader is a contested gain. Readers each given one class of fault to look for found about 35% more than readers with a checklist or with none, in the laboratory that devised the method [55][56]; an independent replication found no difference [60], and an aggregation of the experiments on perspective-based reading found such teams better than unstructured readers and worse than checklist readers, with signs of researcher bias [59].

What is absent is found least. In a code-reading experiment with 32 professionals, five of eight faults of omission were found by fewer than a quarter of the readers, while nine of twenty faults of commission were found by three quarters or more [62]. Proofreaders told to look for errors caught 84% of misspellings and 57% of omitted words; told to read for the content, they caught 71% and 34% [63]. A denial whose target is missing asks the reader for the same act — to notice what the page does not hold — and the instruction under which the reader reads decides how often that happens.

### Instructions to the author

An instruction is a weak barrier. The models of the question-generation study leaked reader-unavailable content under an explicit instruction against it [29]. A reporter on a coding agent's tracker writes that "a clear, mandatory rule" in the instruction file "does not reliably suppress" comments that narrate the edit; a commenter's hook that blocks added comments containing "now uses", "changed from", "previously" or "no longer" brought them from 15 lines to 2 in its author's demonstration [27]. One vendor's guidance asks for instructions that say what to do [28]. In this repository the two style rules that forbid the defect stood in the author's standing instructions throughout.

## The design that follows

Every source gives a part, and no source gives the whole. The parts, each with its ground:

1. **A script lists; it does not judge.** For a commit, the list holds every added sentence that carries a marker of denial or contrast, and every added sentence that names a term of the statements the commit deleted. Ground: cue detection is close to solved [32]; the probe's list held every sentence in question; markers fire on ordinary commits, so the list is a worklist.
2. **The terms of the deleted statements are named by a reader of those statements.** Ground: the automatic choice failed in the probe; naming the subject of a deleted rule is a reading task of the kind models do well when shown the reference [48].
3. **A listed sentence stays only with its licence quoted.** The reviewer answers the question the literature gives — who holds, or would expect, the thing this sentence denies, and where does this document say so — and a kept sentence carries the quoted sentence of the document that presents the denied thing, or the named expectation of its reader. A script checks that the quote stands in the document, before the kept sentence, in a sentence the list does not hold. A listed sentence with no checked licence is rewritten as what the subject does. Ground: the licence condition [1][5][6]; the question form [10][21]; the reviewer's lean towards accepting [45]; evidence for a dismissal and uncertain as a weak positive [49]; the cost of a wrong rewrite is small where the positive statement carries the content.
4. **Several independent readings, and one flag is enough.** Ground: independent teams together found 78% where one found 35% [57]; flips concentrate on borderline items [40]; the tilted rule [45]; the pilot's 12 of 12 beside 0 of 1.
5. **A reader who holds only the document reads what is kept, and is told what to look for.** Ground: experts predict under 15% of readers' problems [16]; writers judge their own text worst [15]; a reader told to look for errors finds 57% of omissions and a reader told to read for content 34% [63].
6. **The owner decides what the rest of the list keeps.** Whether a word belongs in a description is a matter of taste, and in this repository's method a taste is its owner's decision.

Stated as hypotheses, with the outcome that refutes each:

- H-a: on documents with seeded sentences of this kind, the list of step 1 holds at least 95% of them. A lower share refutes it.
- H-b: with step 3, a model reviewer leaves fewer seeded sentences in place than the same reviewer asked to find defects; an equal or higher share left in place refutes it.
- H-c: the union of three readings removes more seeded sentences than one reading at the same false-alarm cost per kept licensed denial; no gain refutes it.
- H-d: licensed denials — controls whose target the document presents — are kept with a checked licence in at least 80% of cases; a lower share means the design rewrites sound prose.

A test of these needs material the design was not made from: documents with planted sentences and with licensed denials as controls, since a benchmark of negated sentences can be scored by the negation word alone [35].

## Open questions

- No measurement exists of the defect's detection by any method; every reliability figure above comes from a neighbouring task.
- The licence by a reader's expectation has no script form. Agreement between people on such judgements is moderate, so step 3 will rewrite some sound denials; H-d measures how many.
- Whether a judge shown the difference between two versions finds more than a judge shown the new version alone is untested outside the pilot's single comparison.
- How much repeated readings by one model overlap on this defect is unmeasured. Where readings share a blind spot, more of them add little: two code-review models found largely the same bugs [50].
- Whether a marker check at the moment a file is written would be read by its author or dismissed is unmeasured; the tracker thread gives one demonstration, for code comments [27].
- The studies of the contrast construction separate licensed from unlicensed uses in Mandarin; the English counts give density alone.

## Sources

How each was seen: `full` — full text read by the search's reader, through an extracting fetch tool unless the entry says "directly"; `abstract` — the abstract alone; `relay` — reported by another text, which the entry names. `re-opened` marks the ten entries the compiler opened again.

1. Horn & Wansing. "Negation", §1.2. *Stanford Encyclopedia of Philosophy*, 2015, revised 11 March 2025. [plato.stanford.edu/entries/negation](https://plato.stanford.edu/entries/negation/) — `full`, the page text searched directly; `re-opened`. Denial as the prototypical use of negation; the denied proposition in the discourse model or a plausible addition to it. The entry warns against reducing every negation to a denial.
2. Givón (1978). "Negation in language: pragmatics, function, ontology", in *Syntax and Semantics 9*. [doi:10.1163/9789004368873_005](https://doi.org/10.1163/9789004368873_005) — `relay` through [1] and through Miestamo, "Negation", a handbook chapter, [pp. 211–212](https://www.mv.helsinki.fi/home/matmies/publications/12mie.pdf). A negative assumes a hearer who has heard of, believes or is familiar with the affirmative.
3. Tottie (1991). *Negation in English Speech and Writing.* Academic Press — `relay` through Miestamo, p. 212. In conversation, denials of the merely expected outnumber denials of the asserted; the counts were not seen.
4. Wason (1965). "The contexts of plausible denial." *Journal of Verbal Learning and Verbal Behavior* 4(1). [doi:10.1016/S0022-5371(65)80060-3](https://doi.org/10.1016/S0022-5371(65)80060-3) — `relay` through [1] and [7]; the publisher page was closed. A context that makes the denied item an exception speeds a true negative.
5. Lüdtke & Kaup (2006). "Context effects when reading negative and affirmative sentences." *Proceedings of the 28th Annual Meeting of the Cognitive Science Society* — `abstract`. Shorter reading of negatives after explicit mention and after inference; short narratives.
6. Nieuwland & Kuperberg (2008). "When the truth is not too hard to handle." *Psychological Science* 19(12). [doi:10.1111/j.1467-9280.2008.02226.x](https://doi.org/10.1111/j.1467-9280.2008.02226.x) — `full`, author manuscript. 24 readers; licensed negation integrated like an affirmative. Single sentences of world knowledge, licensing set by naturalness ratings.
7. Albu, Tsaregorodtseva & Kaup (2021). "Contrary to Expectations: Does Context Influence the Processing Cost Associated with Negation?" *Journal of Psycholinguistic Research* 50(6). [doi:10.1007/s10936-021-09799-8](https://doi.org/10.1007/s10936-021-09799-8) — `full`. Six experiments, 61 to 79 participants each; marker-only context no help, extended denial context removes the cost in one experiment.
8. Tian, Ferguson & Breheny (2016). "Processing negation without context — why and when we represent the positive argument." *Language, Cognition and Neuroscience* 31(5). [doi:10.1080/23273798.2016.1140214](https://doi.org/10.1080/23273798.2016.1140214) — `abstract`. Spoken single sentences with pictures.
9. Roberts (2012). "Information structure in discourse: Towards an integrated formal theory of pragmatics." *Semantics and Pragmatics* 5(6). [doi:10.3765/sp.5.6](https://doi.org/10.3765/sp.5.6) — `full`, read directly. A theory with constructed examples.
10. von Fintel (2004). "Would you believe it? The King of France is back!", in *Descriptions and Beyond*, OUP. [web.mit.edu/fintel/fintel-2004-kof.pdf](https://web.mit.edu/fintel/fintel-2004-kof.pdf) — `full`, read directly. The "Hey, wait a minute" test, after Shanon 1976; introspective judgements on dialogues.
11. Cummins, Amaral & Katsos (2012). "Backgrounding and accommodation of presuppositions: an experimental approach." [semanticsarchive.net](https://semanticsarchive.net/sub2012/CumminsAmaralKatsos.pdf) — `full`, pp. 202–203 read directly. The test responds to any content outside the point at issue.
12. Beaver, Geurts & Denlinger (2021). "Presupposition", §5. *Stanford Encyclopedia of Philosophy.* [plato.stanford.edu/entries/presupposition](https://plato.stanford.edu/entries/presupposition/) — `full`, read directly; Karttunen 1974 relayed through it. Accommodation as the ordinary repair, with triggers that resist it.
13. Dale & Duran (2011). "The cognitive dynamics of negated sentence verification." *Cognitive Science* 35(5). [doi:10.1111/j.1551-6709.2010.01164.x](https://doi.org/10.1111/j.1551-6709.2010.01164.x) — `abstract`.
14. Flower (1979). "Writer-Based Prose: A Cognitive Basis for Problems in Writing." *College English* 41(1). [doi:10.2307/376357](https://doi.org/10.2307/376357) — `full`, pp. 19–24 and 27–32. Case analysis and classroom experience; no detection rate.
15. Schriver (1990). "Evaluating Text Quality: The Continuum from Text-Focused to Reader-Focused Methods." Technical Report 41, Center for the Study of Writing; also *IEEE Transactions on Professional Communication* 32(4), 1989. [ERIC ED318009](https://files.eric.ed.gov/fulltext/ED318009.pdf) — `full`, pp. 1–6. A review; the studies behind the own-text claim were not opened.
16. Lentz & de Jong (1997). "The evaluation of text quality: expert-focused and reader-focused methods compared." *IEEE Transactions on Professional Communication* 40(3). [doi:10.1109/47.649557](https://doi.org/10.1109/47.649557) — `abstract`; `re-opened`. One government brochure.
17. Camerer, Loewenstein & Weber (1989). "The Curse of Knowledge in Economic Settings." *Journal of Political Economy* 97(5). [doi:10.1086/261651](https://doi.org/10.1086/261651) — `abstract`. Forecasts of others' estimates, not writing.
18. Hayes & Bajzek (2008). "Understanding and Reducing the Knowledge Effect: Implications for Writers." *Written Communication* 25(1). [doi:10.1177/0741088307311209](https://doi.org/10.1177/0741088307311209) — `abstract`. The outcome of the feedback tutor in its second study was not seen.
19. Strunk (1918). *The Elements of Style*, Rule 12. [wikisource](https://en.wikisource.org/wiki/The_Elements_of_Style/Principles) — `full`. A norm; it cites no study.
20. Google developer documentation style guide. "Timeless documentation." [developers.google.com/style/timeless-documentation](https://developers.google.com/style/timeless-documentation), read 2026-11-20 — `full`; `re-opened`. A norm; it cites no study.
21. Peng, Jing, Liu, Meng & Liu (2026). "Not X, but When: Diagnosing a Mandarin LLM Writing Tic through Contextual Appropriateness." [arXiv:2610.22249](https://arxiv.org/abs/2610.22249) — `full`; `re-opened`. Mandarin, five commercial models, 307 annotated model uses and 33 human ones; the human labels were produced automatically; local context, not a whole document.
22. Paech, Roush, Goldfeder & Shwartz-Ziv (2025). "Antislop: A Comprehensive Framework for Identifying and Eliminating Repetitive Patterns in Language Models." [arXiv:2510.15061](https://arxiv.org/abs/2510.15061) — `full`. English creative writing; the models behind the 6.3 figure and the human baseline for it are not named.
23. Paech. slop-score. [github.com/sam-paech/slop-score](https://github.com/sam-paech/slop-score) — `full`, the README and the live page. A tool; no validation published.
24. Wikipedia contributors. "Wikipedia:Signs of AI writing", § Negative parallelisms. [en.wikipedia.org](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), read 2026-11-20 — `full`, the first 200,000 characters. Editors' observations without counts.
25. Wu, Li, Wang, Liu, Cai, Su & Wang (2026). "Verbal tics in frontier language models: A critical review." [arXiv:2604.19139](https://arxiv.org/abs/2604.19139) — `full`. No measured rate for contrast constructions.
26. Kato (2026). "Introducing Voices: AI writing skills as Vale rules." [vale.sh/blog/voices](https://vale.sh/blog/voices); dteirney, vale-agent-prose, [README](https://github.com/dteirney/vale-agent-prose) — `full`. Rule packs with fixture tests and no precision.
27. Issue 65961, "Claude verbose code comments by default — ignores instructions to stop", anthropics/claude-code, opened 2026-06-07. [github.com](https://github.com/anthropics/claude-code/issues/65961) — `full`. A tracker thread; the commit count is one commenter's, unreviewed, and concerns code comments.
28. Anthropic. "Prompting best practices." [platform.claude.com](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) — `full`. Vendor guidance.
29. Wu, Mangla, Durrett & Li (2023). "QUDeval: The Evaluation of Questions Under Discussion Discourse Parsing." EMNLP 2023. [aclanthology.org/2023.emnlp-main.325](https://aclanthology.org/2023.emnlp-main.325/) — `full`, read as page images; `re-opened`. 2,190 questions on news; models of 2023.
30. Choi, Palomaki, Lamm, Kwiatkowski, Das & Collins (2021). "Decontextualization: Making Sentences Stand-Alone." *TACL.* [arXiv:2102.05169](https://arxiv.org/abs/2102.05169) — `full`, read directly. Wikipedia; the missing context is taken to lie inside the document.
31. Hossain, Hamilton, Palmer & Blanco (2020). "Predicting the Focus of Negation: Model and Error Analysis." ACL 2020. [aclanthology.org/2020.acl-main.743](https://aclanthology.org/2020.acl-main.743/) — `full`, read directly. Verbal negations in newswire.
32. Khandelwal & Sawant (2020). "NegBERT: A Transfer Learning Approach for Negation Detection and Scope Resolution." LREC 2020. [arXiv:1911.04211](https://arxiv.org/abs/1911.04211) — `full`. In-domain figures.
33. Yu, Min, Zettlemoyer & Hajishirzi (2022). "CREPE: Open-Domain Question Answering with False Presuppositions." [arXiv:2211.17257](https://arxiv.org/abs/2211.17257) — `full`, read directly. Forum questions; a presupposition false in the world, not absent from a text.
34. Kim, Htut, Bowman & Petty (2023). "(QA)²: Question Answering with Questionable Assumptions." ACL 2023. [arXiv:2212.10003](https://arxiv.org/abs/2212.10003) — `full`, read directly. Models of 2022 and 2023.
35. Niven & Kao (2019). "Probing Neural Network Comprehension of Natural Language Arguments." ACL 2019. [aclanthology.org/P19-1459](https://aclanthology.org/P19-1459/) — `full`, read directly. The word "not" alone predicted the answer in 61% of the cases it covered.
36. Yung, Ahmad, Scholman & Demberg (2024). "Prompting Implicit Discourse Relation Annotation." [arXiv:2402.04918](https://arxiv.org/abs/2402.04918) — `full`, read directly; the agreement figures of Hoek et al. 2021 and Zikánová et al. 2019 are relayed through it.
37. Pilán (2016). "Detecting Context Dependence in Exercise Item Candidates Selected from Corpora." [arXiv:1605.01845](https://arxiv.org/abs/1605.01845) — `full`, read directly. Swedish; recall 0.63 on average.
38. Haldar & Hockenmaier (2025). "Rating Roulette: Self-Inconsistency in LLM-As-A-Judge Frameworks." Findings of EMNLP 2025. [arXiv:2510.27106](https://arxiv.org/abs/2510.27106) — `full`; abstract `re-opened`. Three open models, item-level labels and scores.
39. Norman, Rivera & Hughes (2026). "Reliability without Validity." [arXiv:2606.19544](https://arxiv.org/abs/2606.19544) — `full`, the first 100,000 characters. Pairwise preferences at temperature 0.
40. Yagubyan (2026). "The Coin Flip Judge? Reliability and Bias in LLM-as-a-Judge Evaluation." [arXiv:2606.13685](https://arxiv.org/abs/2606.13685) — `full`. One author, two judges of one vendor, 29 questions.
41. Lavie et al. (2025). "Findings of the WMT25 Shared Task on Automated Translation Evaluation Systems." WMT 2025. [statmt.org](https://www2.statmt.org/wmt25/pdf/2025.wmt-1.23.pdf) — `full`, read directly. Translation errors; agreement between people on spans is itself low.
42. Fernandes et al. (2023). "The Devil is in the Errors: Leveraging Large Language Models for Fine-grained Machine Translation Evaluation." WMT 2023. [arXiv:2308.07286](https://arxiv.org/abs/2308.07286) — `full`. Models of 2023, one run.
43. Almaghout, Federmann & Gao (2026). "Large Language Models for Machine Translation Quality Annotation: Humans and Models Are Both Challenged." [arXiv:2610.10918](https://arxiv.org/abs/2610.10918) — `full`.
44. Tyen, Mansoor, Cărbune, Chen & Mak (2024). "LLMs cannot find reasoning errors, but can correct them given the error location." Findings of ACL 2024. [arXiv:2311.08516](https://arxiv.org/abs/2311.08516) — `full`. Models of 2023 and 2024.
45. Jain, Ahmed, Sahai & Leong (2025). "Beyond Consensus: Mitigating the Agreeableness Bias in LLM Judge Evaluations." [arXiv:2510.11822](https://arxiv.org/abs/2510.11822) — `full`; abstract `re-opened`. 366 student programs; the veto threshold was tuned on labelled data.
46. Verga et al. (2024). "Replacing Judges with Juries: Evaluating LLM Generations with a Panel of Diverse Models." [arXiv:2404.18796](https://arxiv.org/abs/2404.18796) — `full`. Answer correctness against a known answer.
47. Lee et al. (2025). "CheckEval: A reliable LLM-as-a-Judge framework for evaluating text generation using checklists." EMNLP 2025. [arXiv:2403.18771](https://arxiv.org/abs/2403.18771) — `full`. Agreement between judges, not with the truth about defects.
48. Zheng et al. (2023). "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena." NeurIPS 2023. [arXiv:2306.05685](https://arxiv.org/abs/2306.05685) — `full`. Twenty questions for the reference result.
49. Klieber, Svoboda, Flynn & Martins (2026). "Using LLMs to Adjudicate Static-Analysis Alerts with Error Reduction Techniques." [arXiv:2607.09979](https://arxiv.org/abs/2607.09979) — `full`, the first 100,000 characters; abstract `re-opened`. Small and partly synthetic suites; programs have an executable ground truth.
50. Kumar, Bararia & Raj (2026). "Bigger Isn't Always Better: A Comparative Evaluation of LLMs for Automated Code Review." [arXiv:2606.15689](https://arxiv.org/abs/2606.15689) — `full`. 150 samples, one run.
51. Nam, Jeong & Kim (2026). "Deterministic Integrity Gates for LLM-Assisted Clinical Manuscript Preparation." [arXiv:2606.09500](https://arxiv.org/abs/2606.09500) — `abstract`. Defects seeded in the classes the detectors were built for.
52. Kumar, Pothuneedi & Bandak (2026). "The Anatomy of a Blind Spot: What an LLM Judge Must Be Shown, and How Much." [arXiv:2610.15938](https://arxiv.org/abs/2610.15938) — `abstract`. The authors report that most of their quantitative predictions failed.
53. Kasner, Zouhar, Schmidtová et al. (2025–2026). "LLMs as Span Annotators: A Comparative Study of LLMs and Humans." [arXiv:2504.08697](https://arxiv.org/abs/2504.08697) — `full`, up to the appendices.
54. Basili, Green, Laitenberger, Lanubile, Shull, Sørumgård & Zelkowitz (1996). "The Empirical Investigation of Perspective-Based Reading." *Empirical Software Engineering* 1(2). [cs.umd.edu](https://www.cs.umd.edu/~mvz/handouts/emp_pbr.pdf) — `full`. 12 and 14 professionals; nominal teams.
55. Porter, Votta & Basili (1995). "Comparing Detection Methods for Software Requirements Inspections: A Replicated Experiment." *IEEE Transactions on Software Engineering* 21(6). [cs.umd.edu](https://www.cs.umd.edu/~basili/publications/technical/T101.pdf) — `full`; `re-opened`, the text of the PDF read directly. 48 graduate students in sixteen teams; formal specifications.
56. Porter & Votta (1998). "Comparing Detection Methods For Software Requirements Inspections: A Replication Using Professional Subjects." *Empirical Software Engineering* 3(4) — `full`. Six teams of professionals; a replication by the originating group.
57. Schneider, Martin & Tsai (1992). "An experimental study of fault detection in user requirements documents." *ACM TOSEM* 1(2). [doi:10.1145/128894.128897](https://doi.org/10.1145/128894.128897) — `abstract`; the figures are a `relay` through [58] and [64].
58. Boodoo, El Emam, Laitenberger & Madhavji (2000). "The Optimal Team Size for UML Design Inspections." NRC/ERB-1081 — `full`, the abstract and §2.
59. Ciolkowski (2009). "What do we know about perspective-based reading? An approach for quantitative aggregation in software engineering." ESEM 2009. [doi:10.1109/ESEM.2009.5316026](https://doi.org/10.1109/ESEM.2009.5316026) — `abstract`.
60. Fusaro, Lanubile & Visaggio (1997). "A replicated experiment to assess requirements inspection techniques." *Empirical Software Engineering* 2. [doi:10.1023/A:1009742216007](https://doi.org/10.1023/A:1009742216007) — `relay` through [64].
61. Briand, El Emam, Freimut & Laitenberger (1997). "Quantitative Evaluation of Capture-Recapture Models to Control Software Inspections." ISSRE 1997, ISERN-97-22 — `full`. The truth is the defects known to the experimenters.
62. NASA Software Engineering Laboratory (1985). *A Comparison of Software Verification Techniques.* SEL-85-001. [ntrs.nasa.gov](https://ntrs.nasa.gov/api/citations/19860010494/downloads/19860010494.pdf) — `full`, §3 and §5. Code, eight faults of omission.
63. Harris & Perfetti (2016). "Lexical Stress and Linguistic Predictability Influence Proofreading Behavior." *Frontiers in Psychology* 7:96. [doi:10.3389/fpsyg.2016.00096](https://doi.org/10.3389/fpsyg.2016.00096) — `full`; `re-opened`. Missing words, not missing content.
64. Aurum, Petersson & Wohlin (2002). "State-of-the-Art: Software Inspections after 25 Years." *Software Testing, Verification and Reliability* 12(3). [wohlin.eu](https://www.wohlin.eu/stvr02-2.pdf) — `full`. The survey through which [57] and [60] are relayed.
