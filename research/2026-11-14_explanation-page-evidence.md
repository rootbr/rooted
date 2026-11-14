# An explanation page for a team — evidence report

The operator of this repository had an agent explain one mechanism of a work project to the team that maintains it, as a page with voice built with `handing-over-to-readers`. He read the page and said it had turned out quite well. The page was a different thing from the report the skill describes: 319 spoken sentences in 20 parts, about 25 minutes of audio, six scenarios, two language versions, several readers and no decision at its end. What the skill lacked for it the agent wrote beside the page and then set down as 20 proposals. This note records what of that entered the skill, on what ground, and what the session checked by hand in the skill's own scripts. The evidence is one page, one reader's approval of it, the words of the team at one review meeting, and six opened sources that measure students; how the team read the page is unknown.

The skill takes eight things from it:

- a kind of deliverable, the explanation for several readers, with the registry of questions as the page's first table;
- the reader's name for a thing: a term of the trade stays as the trade says it aloud;
- a part that corrects a reader's wrong model in three steps;
- the record of a meeting as a source of the readers' questions;
- three more kinds of picture for a mechanism;
- one body as the source of a page's spoken text, with names for sentences;
- a voice cache, a silent build, warnings on text a voice misreads and a check of the built page in a browser;
- a question after a part with a hidden answer and no count.

[Sources](#sources) holds six entries: two opened in full text through a summarising fetch, three by their abstract, one by the abstract on the first page of the scanned article.

## What was investigated and why

The report form of the skill was read on small fixture tasks, and the longest text its reader had heard was a plan of 62 sentences (`research/2026-11-07_report-forms-evidence.md` § Open questions: a large real report; a reader other than the operator). The explanation page is the first large text built with the skill and the first written for readers other than the operator. The question was which of the things written for that one page belong in the skill, and on which ground each stands.

## Method

**The page.** An agent in another project built it with the skill at version 6.0.1 and wrote, beside the page, what the skill did not give: the extraction of the spoken story from the body, anchors resolved by fragment, a silent build, a translation dictionary with a check of two language bodies, a capture of the page's parts in a browser, a collapsed player, questions with hidden answers and charts of recorded runs. The page, its texts and that code stay outside this repository; this note holds counts and the words said about the page.

**The proposals.** The same agent wrote 20 proposals, each as what the skill says now, what to change, what happened on the page, and what was not verified. The session checked every "now" against the skill's files and scripts, ran the scripts where a proposal named a failure, and opened a source where a proposal named a research finding from memory.

**Limits.** One page and one reader's judgement of the whole of it. The team's words come from one review meeting as the agent recorded them. No reader's behaviour on the page was counted. The page's text and voice were Russian, with an English version read by the agent in four paragraphs.

## The reading

**Shown.** The explanation page in its second version, after a review meeting of the team on the first.

**What the operator said.** The page "turned out quite well". On the term for the round-trip time, which the first version called by a coined native word: in the industry RTT is written as RTT even in Russian or German, and of an earlier coined phrase for it: nobody says that even in Russian. He had asked for the stages of a recorded run as a numbered table himself. He corrected one error: a work item the agent had taken from a digest of the meeting had been postponed at the end of that meeting.

**What the team said at the review.** They said RTT. They replaced two more of the agent's coined words with their own. Of one computed quantity they said it was given by its formula and not by its meaning. One of their questions rested on a model of the mechanism that the remarks around the question showed and the question alone did not.

**What held without change.** The opening of five sentences gave the whole matter on a page of 20 parts. The phrase that announces a part and lights its heading worked with 20 parts as with four. What the voice does not say stood only in figures and captions, reference tables included. The cold read by the readers' own questions answered 15 of 15 from the text and listed no unexplained term. One sentence at delivery said what on the page had not been seen working.

## Measurements

**The page.** 319 spoken sentences, 20 parts, about 25 minutes of audio, six scenarios of which four are told by numbered stages, 20 code anchors under "Where to look", a table of 20 terms, 22 questions with hidden answers, 241 texts in the translation dictionary.

**The questions.** The table of readers' questions has 14 rows, every one taken from the record of the review meeting. The four kinds of picture written for the page — the stages of a run, causes against signs, where a decision comes from, a calculator — closed five of the 14, by the agent's count.

**The name.** The first version called the round-trip time by a coined native word 52 times and by RTT twice.

**The cost of the tooling as it was.** An edit of one sentence voiced all 25 minutes again. The body named sentences by number, so an inserted sentence shifted every number after it within its part. The agent's own page script failed in a way seen only in a browser, and two captions of the English version ran out of their frames, found on screenshots.

**Not counted.** Whether the readers used the table of questions or the routes; whether a part read alone is understood; any answer to the 22 questions; how many of the team's later questions the page already answered.

## Hands-on checks of the skill's scripts

The session ran these on the skill at version 6.0.1, with the skill's own example body and fixtures.

- **A stale sentence number lights the wrong element.** A sentence was inserted before sentence 2.5 of the example's story and the text paragraph's list of numbers was extended, as an author would do; the table cell marked "the old thumbnail" kept `data-lit="2.5"`. `build_page.py` built the page with exit 0 (24 sentences, no violation), and the cell now lit on the inserted sentence. The builder checks that a named number exists, and a shifted number still exists.
- **A module synthesiser without word timings yields cues of zero length.** A module that returned audio and an empty list of word timings made `voice_cues.py` write five sentences whose start equals their end, with exit 0.
- **A dangling internal link passes the build.** A link to an id the page does not have built with exit 0.
- **A page cannot be built without a voice run.** `build_page.py` requires the cues, which only a synthesis produces, so a body could not be looked at before paying for the voice.
- **The anchor check does not say where a moved fragment stands.** When the fragment is neither on its line nor within two lines, `check_report.py` reports only that it is not on that line.

## What the literature adds

**A text that names a misconception and refutes it.** Refutation texts, which state a common misconception, refute it and explain the correct conception, taught more than texts with the same content that only explain: g = 0.41, 95 % CI [0.30, 0.51], over 44 independent comparisons with 3,869 participants (Schroeder & Kucera 2022 [1], full text through a summarising fetch). Most comparisons used post-secondary samples and scientific concepts; the studies were "primarily one-time interventions with relatively short text passages", and learners' prior misconceptions were not analysed as a moderator. It reaches a part of an explanation for engineers as a transfer.

**Questions that ask to apply.** Retrieval practice raised delayed test performance over rereading or no quizzes, and "higher order and mixed quizzes improved higher order test performance, but fact quizzes did not" (Agarwal 2019 [2], abstract; middle school and college students).

**A prediction.** Predicting — a response given with some confidence and followed by immediate feedback — is argued to be a learning strategy in its own right, working through surprise at an incorrect prediction; the review covers simple declarative material and reports no pooled effect (Brod 2021 [3], full text through a summarising fetch). It bounds the question "what happens when one input changes": the answer has to follow at once, and a mechanism is beyond what was studied.

**A comparison.** Comparing cases led to more learning than studying them one by one or than traditional instruction, d = 0.50, 95 % CI [0.44, 0.56], over 57 experiments and 336 tests, more with prompts to find similarities, with the principle given after the comparison and with an immediate test (Alfieri, Nokes-Malach & Schunn 2013 [4], abstract).

**An answer that explains.** As feedback in computer-based practice, an explanation had an effect of 0.49, the correct answer alone 0.32 and a bare right-or-wrong 0.05, over 70 effect sizes from 40 studies; the explanation was "particularly more effective … for higher order learning outcomes" (Van der Kleij, Feskens & Eggen 2015 [5], abstract).

**No count.** Over 607 effect sizes and 23,663 observations feedback interventions improved performance on average (d = .41), while over a third of them decreased it, and "effectiveness decreases as attention moves up the hierarchy closer to the self and away from the task" (Kluger & DeNisi 1996 [6], abstract). A count of one's own right answers is feedback of that kind; no study of a private self-kept count was opened.

## Rules and data

`practice` marks a clause that rests on the operator's reading of the page or on the team's words; `hands-on` one that rests on a check above.

| Clause or tool | Behind it | Research beside it | Fit and caveat |
|--|--|--|--|
| The name is the reader's: the trade's term as said aloud, then the code's name, a coined word last | the operator's words on RTT; the team said RTT and replaced two coined words; 52 against 2 | Metzing & Brennan 2003 (`README.md` no. 85) for one name per thing | `practice` with a transfer; where a native word is alive stays the author's judgement |
| A computed quantity is said by its purpose before its formula | the team's remark on one quantity | none opened | `practice`: one remark; an instance of "introduce a thing before using it" |
| A wrong model is named before it is corrected | the page's part on one such question, answered in full by the cold reader | Schroeder & Kucera [1]: g = 0.41 | `research` transfer: students, short science texts, one reading |
| A meeting's record is a source of questions; its digest only points | the postponed work item taken from a digest; the question whose model only the remarks showed | none opened | `practice`: one meeting |
| Three kinds of picture: stages of a run, causes against signs, where a decision comes from; a run's values are read from the run | the operator asked for the stages; four of six scenarios; five of 14 questions closed with the calculator among the four kinds; values typed twice and reconciled by eye | Guo et al. 2020 and Cromley & Chen 2025 (`README.md` nos. 126, 130) for a picture beside its text | `practice`: one page; the calculator is held out, since its formula was written a second time and the build did not compare it with the code |
| The explanation for several readers: its signs, the table of questions, routes, a part per named questions, tables without voice, the list in story order | the page as a whole and the operator's judgement of it | Käfer et al. 2017 and MacLeod et al. 2017 (`README.md` nos. 123, 124) for text that is looked things up in | `practice`: one page, one reader; no reader's use of any element was counted |
| A question after a part: hidden answer that explains, questions that ask to use the mechanism, no count | 22 questions on the page, none answered yet; the page's own count line, which the reading methodology forbids for a dialogue | Agarwal [2]; Van der Kleij et al. [5]; Kluger & DeNisi [6]; Brod [3] and Alfieri et al. [4] for two of the kinds | `research` transfer for the three properties; the block itself is untested |
| One body with names for sentences | the stale-number check above; the agent's extraction of the story from the body | none | `hands-on`: one reproduction on the skill's example |
| A silent build; a refusal on missing word timings; a voice cache; warnings on spoken text | the checks above; 25 minutes voiced again per edit; the abbreviation and ordinal run already recorded for the page rules | none | `hands-on`; the four warnings come from one synthesiser's reading of Russian text |
| A check of the built page in a browser; an internal-link check | the script error and the two captions seen only in a browser; the dangling-link check above | none | `hands-on`: one page; the dark theme was not captured there |
| The part buttons behind one control past six parts | 20 buttons filled the top of the page | none | `practice`: one page; six is a house default |

Held out, each for its stated reason: page scripts of the author's own (the operator's earlier decision that figures are drawn from ready parts, and the one script error of this page); a second language version (one case); the chart of a recorded run (written for one data set); the calculator; a cold read part by part (one agent run a part, never done); a table of terms for the reading companion (it keeps the book's term in the original); the page as material for the reading companion (never read so).

## Open questions

- How many of the team's questions after the second version the page already answered: the one count that would confirm the genre.
- Whether a part entered from the table of questions is understood without the parts before it.
- Whether readers use the table of questions, the routes and the questions with hidden answers.
- A second explanation page, of another mechanism, built with the skill alone.
- The explanation in English: the page's text was Russian, and the warnings on spoken text were met there.

## Sources

1. Schroeder & Kucera — Refutation Text Facilitates Learning: a Meta-Analysis of Between-Subjects Experiments — Educational Psychology Review 34(2), 2022 · doi:10.1007/s10648-021-09656-z · full text at https://pmc.ncbi.nlm.nih.gov/articles/PMC8784251/ through a summarising fetch that read the first 100,000 characters — g = 0.41 [0.30, 0.51], 44 comparisons, n = 3,869; mostly post-secondary samples and science; short passages read once.
2. Agarwal — Retrieval Practice & Bloom's Taxonomy: Do Students Need Fact Knowledge Before Higher Order Learning? — Journal of Educational Psychology 111(2), 2019 · doi:10.1037/edu0000282 · abstract (ERIC EJ1205208) — higher order and mixed quizzes raised higher order test performance, fact quizzes did not; no effect size in the abstract.
3. Brod — Predicting as a learning strategy — Psychonomic Bulletin & Review 28(6), 2021 · doi:10.3758/s13423-021-01904-1 · full text at https://pmc.ncbi.nlm.nih.gov/articles/PMC8642250/ through a summarising fetch — a theoretical review of simple declarative learning; the benefit runs through surprise at an incorrect prediction; no pooled effect.
4. Alfieri, Nokes-Malach & Schunn — Learning Through Case Comparisons: A Meta-Analytic Review — Educational Psychologist 48(2), 2013 · doi:10.1080/00461520.2013.775712 · abstract (ERIC EJ1000186) — d = 0.50 [0.44, 0.56], 57 experiments, 336 tests.
5. Van der Kleij, Feskens & Eggen — Effects of Feedback in a Computer-Based Learning Environment on Students' Learning Outcomes: A Meta-Analysis — Review of Educational Research 85(4), 2015 · doi:10.3102/0034654314564881 · abstract (ERIC EJ1081708) — elaborated feedback 0.49, knowledge of correct response 0.32, knowledge of results 0.05; 70 effect sizes, 40 studies.
6. Kluger & DeNisi — The Effects of Feedback Interventions on Performance: A Historical Review, a Meta-Analysis, and a Preliminary Feedback Intervention Theory — Psychological Bulletin 119(2), 1996 · doi:10.1037/0033-2909.119.2.254 · the abstract on the first page of the scanned article — 607 effect sizes, 23,663 observations, d = .41, over a third of interventions decreased performance.

Not opened: Butler 2010, doi:10.1037/a0019902, on transfer from repeated testing, seen in a search summary alone and carrying nothing here.
