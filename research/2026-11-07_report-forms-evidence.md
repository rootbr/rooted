# Report forms — evidence report

The operator of this repository reads and understands a report of `handing-over-to-readers` when it is a story written for the ear: an opening paragraph that gives the whole matter, parts that unfold it in the order of cause and effect, one picture for each part that has something to show, and a short list of where to look, delivered as text or as a page whose voice lights what it says while he scrolls and switches by himself. The labelled first page of the earlier form he skipped every time, and a report that opened on its result read to him as a dump of terms. The evidence is one reader and small fixture tasks, read in seven sittings; the literature beside it measures students in lessons and reaches a report by mechanism.

The skill takes five things from the readings:

- the story is written for the ear: one claim per sentence, under about twenty words, a phrase that opens each part;
- the opening paragraph of three to five sentences gives the task, how it ended, the problem with its cause and what is needed from the reader;
- a part that has something to show takes one picture, designed once and drawn in both forms;
- two forms of delivery, text and a page with voice, with defaults the reader's word overrides;
- on the page the spoken sentence and the figure element it names are lit, the reader moves, the figures are calm, and the decision is answered on the page.

[Sources](#sources) holds 27 entries: 9 opened in full text, 10 by their abstract alone, and 8 reused from entries of `README.md` §References that earlier programmes verified first-hand. This note is compiled from the records of the seven readings, the five findings files of the source search, the provenance lines of the reworked rules and the reports the readings used.

## What was investigated and why

The report form of `handing-over-to-readers` (`research/2026-10-21_reading-contract-evidence.md`) produced text its operator skipped. Its first page carried five labelled lines — the risk, the action expected of him, what is not done, the condition under which the conclusion is wrong, the status — followed by the claims with their evidence, the decisions, the questions and an internal block. The question was which form he reads and understands, and in which medium: written text, a page, audio or video.

The form was rebuilt step by step. After each reading the rules of a prototype of the skill changed, agents wrote the next reports under the changed rules, and the operator read again. The subject is the form of a report to the operator; the question card, the client question list and the evidence rules of the skill stayed outside it.

## Method

**Fixtures.** Six small Java tasks, each a task statement with source files and build or test logs recorded from real runs:

- case a: a test that fails about once in fifty CI runs, because a reader thread can see a pair of fields one writer updates half-written; the task asks for the cause only;
- case b: a client limited to 100 outgoing requests a second against a supplier's documented rules, where a token bucket and a sliding window behave differently;
- case c, to become the eval fixture `plugins/evidence-based-authoring/skills/handing-over-to-readers/evals/fixtures/retry`: a retry on timeout with a doubling pause and at most four attempts, where another team's test fails because a payment is repeated;
- case d, `…/rename`: a renamed timeout setting, where a deployment file keeps the old key, so production silently gets a shorter timeout;
- case e: an order list whose last page misses one order; the fix needs no decision from the reader;
- case f, `…/logformat`: a logging library upgraded to its next major version, which writes the time in another shape and silences another team's alert on errors.

Cases c, d and f carry a decision for the reader; case e carries none. Cases a, b and c made the first set and produced long reports; cases d, e and f were written for the second reading as smaller tasks.

**Who wrote the reports.** Agents following the skill's rules of the moment. Each agent received one case folder and one skill folder — the shipped skill for the `old` arm, the prototype for the `new` arm — returned the report as its reply and wrote no file. The arm's own check script ran on every report, and every report the readings used passed it with exit 0. One story-form report of case d stated a production value that contradicted the case's files and went back to its agent once.

**How the operator read them.** Three ways, in this order:

1. Blind pairs on a page published privately with stored answers. The page named no arm; which report stood first, or under letter A, was recorded apart. In the first reading the two reports of a pair followed each other, with recall questions between them; in the second both were shown at once as A and B, with one choice (A, B or the same) and one optional line of comment.
2. Reports pasted into the chat.
3. One report in several media on a page with tabs and a stored choice that recorded the seconds each tab stayed open, then pages with the forms the earlier reading had chosen, revised after each of his words.

**What a check script measured.** The prototype's `check_report.py --form story` warns about a story sentence of more than twenty words, an opening paragraph of fewer than three sentences and more than 300 words of prose, and rejects a `path:line` anchor whose line does not exist or does not carry the quoted fragment. `voice_cues.py` voices a story through a local speech synthesiser one paragraph at a time and records the start and end of every sentence, which the page uses to light the sentence being spoken.

**Limits.** One reader, the operator himself, who also commissioned the rework. Six small fixture tasks; most rules after the fourth reading were heard or read on case c alone and generated for one more case. The reports and the voice were Russian; the words quoted below are my translation. Every page was voiced by one local speech synthesiser.

## The readings

### Reading 1

**Shown.** Pair 1, case a: the `new` form of the prototype (1497 words, 156 seconds on screen), six recall questions, then the `old` form of the shipped skill (948 words, 108 seconds).

**What he said.** He left the six recall fields empty and passed that step in 25 seconds, stopped inside the first pair, and wrote in the chat: "definitely the second was better". The examples were too complex and the reports too long. He read at about 550 words a minute, that is, he skimmed both. The pair does not separate two influences: the second report was read with the case already understood from the first, and it was 1.6 times shorter.

**What changed.** A report of the new form may not be longer than one of the old; the next cases are smaller and the recall questions go.

### Reading 2

**Shown.** Three pairs of the small cases d, e and f, both reports of a pair at once. The `new` form was the prototype cut to one screen: an opening paragraph, five one-phrase labelled lines, at most one figure, an evidence line of at most three places.

**What he chose and said.**

| Pair | Case | Choice | Seconds to choose | His words |
|--|--|--|--|--|
| 1 | d, renamed setting | `new` | 100 | "This block annoys me everywhere. In the first it starts abruptly, and it is unclear what it is about at all. In the second the first paragraph does bring you up to date, but it essentially repeats the block, and it is unclear why the block is needed at all. I always skip it." |
| 2 | e, last page | `new` | 43 | "The first report has a claim. It spells out what, from where, when — that is more understandable. Still, the second is somehow better." |
| 3 | f, log time format | the same | 58 | "Both read as unclear. What is it even about. Some sort of dump right away … looks like a dump of terms and neuroslop." |

Before his first comment he had pasted the five labelled lines of report B into the comment field. "Neuroslop" is his word for generated text nobody wanted to read. In the chat after the reading: "something clearly needs fixing, because it is still neuroslop. It was better originally."

**What changed.** The labelled block goes: he skips it always, and after an opening paragraph it repeats it. The opening paragraph stays, the one element he called useful. A list of claims that says what and where is clearer to him than one dense evidence line. A report on a situation the reader does not know reads as a pile of terms when it opens on the result instead of the task and introduces several new things in one sentence. The prototype's third revision makes a report a story told from the task in the reader's words, followed by a list "Where to look"; it has no labelled block, no decisions list and no internal block.

### Reading 3

**Shown.** Cases d, e and f written by agents in the story form, pasted into the chat.

**What he said.** "These texts you gave, the three variants right here in the message … already look decent." He opened nothing beyond the chat. His next question was the medium: text, page, audio or video, and when each fits.

**What changed.** Case c, which he had not read, was written in the story form and prepared in four media for the next reading.

### Reading 4

**Shown.** Case c, the retry and the payments team's failing test, on one page with four tabs: the text of the story (313 words), a page with a switchable timeline, audio (86 seconds) and a narrated animated video (73 seconds).

**What he chose and said.** The stored answer: audio for a small answer, video for a large task. The tabs stayed open for 5242 seconds (text, the default tab, open while he was away), 146 (page), 129 (audio) and 79 (video). His comment: "All four variants are very decent. The text could perhaps be made a little shorter, as in the audio. In the audio everything is dictated just perfectly … four paragraphs and everything is said. … The text has a little excess and is a little more tangled. And the page is very good, it looks very visual. I would lay the audio over the page … on the page the piece being spoken would glow a little brighter, but you click yourself … I would let the user choose what he likes better." In the chat he settled three forms — text, audio with the page, and video alone — with a default chosen by rules and the reader's word above it.

**What changed.** The story is written for the ear: the text the author would read aloud to a colleague who was away, voiced as it stands. The prototype names the forms and the reader's override, warns about a story sentence of more than twenty words, and times the sentences of a voiced story; 80 unit tests pass.

### Reading 5

**Shown.** Case c on a page of three forms: the text assembled from the approved narration, a page with voice, and the video.

**What he said.** The text had become dry: it lacked structure and formatting, and "there are two ways: the first, the second" sat in one paragraph. The block of attempts and pauses did not look like a picture; the best picture was the video's frame of the timeline, where an attempt waits, a gap of 200 ms follows, the next attempt waits. The same picture belongs in every form: in pseudographics in the text, drawn on the page with voice where it can be clicked or switched, and in the video as it is generated. On the page he could not tell what "the first variant" of a switch meant. The video showed the red build's log better than the page, and its slides could move onto the page with text and voice.

**What changed.** A part of the story that has something to show takes one picture, designed once and drawn in every form. In the text a part stands under a heading, and the options of a decision stand in their picture, not in a paragraph. On the page a switch names what it changes in the reader's words. Case c was rebuilt: the text with four pictures in pseudographics, the page with the video's four frames as slides lit element by element with the voice, a run control on the timeline and a switch named by what the client does with the payment, and the video re-narrated with the page's story (88 seconds). An agent wrote case d under the picture rule: four parts, three pictures, check exit 0.

### Reading 6

**Shown.** The second version of the three forms of case c.

**What he said.** Better again. The video is superfluous: the page with its interaction works better, because he follows and switches by himself and the page lights what is spoken. The forms are the page with voice or the text. The opening had become two sentences and was better when longer: it should give the whole gist of the problem at once, and the parts then unfold it. The page should be less garish and simpler, the pictures a little further apart; he weighed showing only the current slide and preferred everything at once. The first picture — the client, a timeout, a retry, the server and three status boxes — he found unclear and disliked in substance. The second picture was fine, but the control under it that played the sequence showed nothing; the lighting with the narration worked better; one dictated word of this complaint was read by intent as that control's label. For the decision he asked for a field to dictate into, an option picked by a click, and a control that copies the choice with his words.

**What changed.** The video form is dropped, a finding of this reading: on the page he follows and switches by himself, and the video gives him nothing the page lacks. The prototype keeps two forms, text and page with voice. The opening paragraph gives the whole matter in three to five sentences and takes no picture. The page's figures are drawn in the page's own palette, each in its own frame; no control plays a figure; the decision is answered on the page. The check warns about an opening of fewer than three sentences; 81 unit tests pass. Case c was voiced again with the fuller opening (27 sentences, 100 seconds). An agent wrote case f under these rules; its opening has five sentences that name the task, the outcome, the problem and the decision.

### Reading 7

**Shown.** The third version: case c with the fuller opening, calm figures and the decision answered on the page.

**What he said.** "Now everything is very good." He asked for a summary of what the skill has to do, what else can be improved or researched, and a plan.

**What changed.** The plan was written in the text form (check exit 0 with one warning: 308 words of prose) and published as a page with voice: 62 sentences, 3 minutes 37 seconds, two figures, four decisions with an option pick and a words field each, and one control that copies the whole answer. He approved the plan and answered its four decisions: the old five-line report form is removed entirely; the voice comes from a synthesiser module or from any command, one sentence per call; the agent draws a page's figures from ready parts and examples; one release carries the text form and the page with voice.

## Measurements

**Length of the pairs.** In the first set the `new` arm ran longer than the `old`: 1497 against 948 words for case a, 1191 against 974 for case b, 1329 against 807 for case c. In the second set it ran shorter: 328 against 378 words (case d), 189 against 262 (case e), 372 against 406 (case f). Before the first reading the session checked whether each report carried the six answers the recall questions asked for: the three `new` reports carried every answer as one statement, while two `old` reports scattered the first answer across places, one of them gave the third without its mechanism, and one spread the fifth over two questions.

**Sentence length, narration against written story.**

| Text | Sentences | Words per sentence, mean | Longest |
|--|--|--|--|
| case c, the narration he called ideal | 24 | 8.4 | 16 |
| case c, the written story of the same case | 14 | 16.9 | 40 |
| case f, written by an agent under the earlier rules | 16 | 14.9 | 34 |
| case f, written by an agent under the ear rule | 28 | 7.6 | 14 |

The ear rule doubled the number of sentences and halved their length for the same matter. A recount with a plain splitter on full stops reproduces the narration's row exactly and the others within one sentence and 0.2 words a sentence. The twenty-word warning sits above the longest sentence of the approved narration.

**The opening.** The story-form report of case c that he read in the fourth reading opened with two sentences, as did the version he found too thin in the sixth; the check of the sixth revision warns on it ("the opening paragraph has 2 sentence(s)"). Case c rewritten under the opening rule opens with five sentences, and case f written by an agent under it with five; both pass the check with 0 errors and 0 warnings. An earlier report of case f under the ear rule opened with four.

**Time per medium in the fourth reading.** Page 146 seconds, audio 129, video 79; the text tab, open by default, stayed open 5242 seconds while he was away and measures nothing. The audio ran 86 seconds and the video 73; the record holds the time a tab stayed open, not playback, so how much of each he played is not recorded. The voiced versions of case c ran 86 seconds (24 sentences), 88 seconds (the re-narrated video) and 100 seconds (27 sentences, with the fuller opening); the plan's page ran 3 minutes 37 seconds for 62 sentences.

**Seconds to a choice in the second reading.** 100, 43 and 58 seconds for pairs of 706, 451 and 778 words.

**Unit tests and checks.** The prototype's tests grew with its rules: 56 at the second revision, 71 at the third, 80 at the fourth and fifth, 81 at the sixth, and the 81 pass on a rerun for this note. Every report an agent wrote for a reading passed its arm's check with exit 0, the 15 saved check outputs of cases a to f included; the plan passed with one length warning.

### The eval run of the story form

Six evals ran once with the skill and once without it, in English, on worker agents (`plugins/evidence-based-authoring/skills/handing-over-to-readers/evals/runs/iteration-2/benchmark.md`): four operator reports on the fixtures `repo`, `retry`, `rename` and `logformat`, a client question list and a question card. With the skill 52 of 52 expectations passed, without it 20 of 52; a run with the skill took 81 s and 65,000 tokens on average against 29 s and 45,100. Three bounds: one run per configuration; the baseline agents carried the report shape of the earlier version in their own definition, so the comparison is against the earlier habit and not against an agent without guidance; seven checks of the grader tested a wording instead of the expectation and were corrected before the recorded grading, and a first grading had failed eight of the skill's expectations for that reason alone. It is the first run of the story form in English: each of the four reports written with the skill opened with 5 to 6 sentences, had no sentence past twenty words and closed on one question.

### The cold read on planted omissions

A fresh agent that saw nothing of the work read a report alone and answered the reader's questions from it; a script counted an answer only when a sentence it quoted stood in the report (`plugins/evidence-based-authoring/skills/handing-over-to-readers/evals/cold-read/`). The reports were the four operator reports of the eval run above, written with the skill. Each was read intact and with one of three omissions planted: the reader's decision, the cause of the problem, a sentence that introduces a thing used later. The texts went out under names that hide the kind of omission, one run a cell, sixteen reads an iteration. With the shipped instructions and six questions (`runs/iteration-3`) the read marked the missing decision in 4 of 4 and the missing cause in 4 of 4, marked nothing on the 4 intact reports, and noticed none of the 4 removed introducing sentences; the iteration before it, which differs by the wording fixes of the context audit, came out the same in all sixteen cells (`runs/iteration-2`). With the first instructions and five questions (`runs/iteration-1`) it marked a question on 2 of the 4 intact reports and listed 3 to 6 terms as unexplained on every intact report; the instructions then gained three rules (a stated unknown is an answer, the question is judged as asked, a thing named by its role is left out) and the terms stopped deciding the result. Two other reader models then read the same sixteen texts with the shipped instructions, one run a cell each (`runs/iteration-4`, Sonnet; `runs/iteration-5`, Haiku): both marked the missing decision in 4 of 4 and the missing cause in 4 of 4, noticed 1 of the 4 removed introducing sentences, and marked one intact report, the same one, on the question about what is unverified: the report names what was not verified, and the reader asked whether there was more. Bounds: one run a cell for each model and two for the first under near-identical instructions; reports of about 400 words; omissions planted by the session, which also wrote the instructions between the first iterations.

### The cold read on real reports

The planted omissions were the session's own, so a second measurement took messages the operator had really received. Of his stored replies to an agent's closing message, 298 that hold a question were classified by a model: in 141 he asked back about the message itself. Thirty of those messages, and thirty that ended in a question he answered with approval alone, were each read once by a fresh agent on the Sonnet model with the shipped instructions and all six default questions; the reader did not know the group. The script checked each read as above. A second model then compared, for the thirty asked-back cases, what the operator had asked with what the read had marked.

| | asked back (30) | approved (30) |
|--|--|--|
| questions left without a full answer, mean a report | 3.43 | 2.43 |
| the same without the question about the decision | 2.60 | 2.07 |
| reports with at least one such question | 30 | 28 |
| reports with a question found wholly unanswered | 17 | 10 |
| terms listed as unexplained, mean a report | 2.10 | 2.00 |

Of the thirty things the operator asked back about, a mark of the read named 8, touched the same area in 11 and concerned none of it in 11. Of the 166 marks on those thirty reports, 25 carried a match: 17 questions and 8 terms.

On these reports the read marks almost every text in either group, so its exit code does not tell a report its reader will question from one he will accept. It names about a quarter of what he then asked and touches another third, among five to six marks a report. The groups differ by one question a report (permutation test on the means, p = .003) and by half a question without the question about the decision (p = .09); that question is confounded, since an approved message is by selection one that put a decision to him.

Bounds: one operator; messages written before the story form, many without the parts the six questions ask for; all six questions put to every message, where the skill puts the questions of the report's own registry; one reader model and one read a message; the classification of the replies and the match judged by one model each, the match from the first 1,500 characters of the reply; a reply that asks back may ask for more than a report of that task owed. The texts, the reads and the judgements stay outside the repository; this section holds counts alone.

### Pages built by an agent

Two worker agents each took a fixture case (`rename`, `logformat`, in Russian), read the skill, and produced the text form, the spoken story with its sentence timings, the page body and the built page, without help. Both text checks, both voice runs and both page builds exited 0. One page has 25 sentences, 95 s of audio and two tables as figures; the other 26 sentences, 106 s and one table. The runs took 154 s and 123 s and 81,400 and 72,100 tokens, against about 60,000 tokens and 56 to 98 s for a report in the text form alone in the eval run. The agents did not open their pages; the session rendered both once and found the figures inside their frames and the decision and the closing list in place. Neither page has been read by the operator at the time of writing.

## What the literature adds

The source search opened what it could within a budget; a figure seen only in a search summary is `relay` and carries nothing here. A citation in brackets resolves in [Sources](#sources).

### The opening and given before new

A sentence whose antecedent is already given is understood faster than one that opens on something new: 835 against 1016 ms (Haviland & Clark 1974 [1]; undergraduates and two-sentence pairs). A report that opens on its result puts the new before the given at the scale of the whole text, which is what the operator met in case f. Developers in one company's field study preferred an AI-generated summary of a change delivered before the review, especially for large or unfamiliar pull requests, and asked for short, scannable output with file and line references; some feared the summary would narrow their attention (Aðalsteinsson et al. 2025 [6], full text; 7 interviewees, then 10 participants reviewing two pull requests each, no time or accuracy measures).

Two sources point the other way for labels and bound the summary. Readers searched abstracts with labelled parts more easily than plain ones (Hartley, Sydes & Blurton 1996 [2]; N = 52 with an electronic and 56 with a printed database, abstract only, no times in it), and labelled abstracts are longer and "judged to be more informative and accessible" (Hartley 2004 [3], abstract only). Those readers searched many abstracts for retrieval; the operator reads one report once, and he skipped the labels. A redesigned plain-language summary was understood by 53 % of readers against 18 % for the old format (Santesso et al. 2015 [4]; N = 143, abstract only), but both arms received a summary, so the trial tests a format, not a summary placed before the full text. The position effect behind the earlier "riskiest first" stays where the rework keeps it, inside the list of places: a defect in the file shown last had 64 % lower odds of being found, for one of two seeded defects (Fregnan et al. 2022 [5]).

### A picture beside text

Text with graphics was understood better than the same text alone, g = 0.39, 95 % CI [0.26, 0.51], over 39 studies with 2,103 participants, and 0.28 after trim-and-fill (Guo et al. 2020 [7], full text). Pictures, pictorial diagrams and flow diagrams did not differ, grade level did not moderate the effect, and the corpus excluded narrated visuals; it is mostly school-age readers. In Mayer's corpus of 92 articles, 181 studies and 591 effects, the principles tested within text with diagrams averaged g = 0.45, with "large, consistent effects … across factual, inferential, and transfer outcomes", and adult samples g = 0.74 (Cromley & Chen 2025 [8], full text); it is one group's corpus with a significant Egger's test, and it does not contrast text alone with text and a diagram.

Animation gains little over a static picture where the content is notation. Animation against static pictures gave d = 0.37 [0.25, 0.49] over 26 studies and 76 comparisons, larger for realistic content and procedural-motor skills (Höffler & Leutner 2007 [9], abstract as paraphrased by the fetch tool, no verbatim quote). A later meta-analysis found g = 0.226 [0.12, 0.33] over 61 studies, N = 7036, with iconic representations ahead of abstract ones, which include "formal notation, symbols, charts, diagrams, graphs" (Berney & Bétrancourt 2016 [10]): the case closest to a code explainer gets the weakest benefit. That fits the static pictures the rules keep and the run control the operator found empty, as a transfer and not a test.

### Listening against reading, and the length of spoken text

Listening and reading comprehension do not differ overall, g = 0.07 (p = .23), over 46 studies with N = 4,687; reading wins when self-paced (g = 0.13) and for inferential comprehension (g = 0.36) (Clinton-Lisell 2022 [13]). In spoken air-traffic messages read-back errors doubled from 0.7 % to 1.4 % as clearances grew from three elements to four (Cardosi 1993 [11]), and rose once a message carried two or more topics (Prinzo, Hendrix & Hendrix 2009 [12]); both measure listening under workload, and they carry the one-claim sentence of the ear rule.

Long spoken text loses to the same text written, and shortening it brings the spoken advantage back. With a long text and a diagram, written text beat spoken (N = 24, primary school); with shorter texts, audio with visuals beat visuals with written text (N = 64) (Leahy & Sweller 2011 [14], abstract only). A later study reports "a modality by text length interaction" (Leahy & Sweller 2016 [15], abstract only), and segmenting text into smaller sections helped both modalities, spoken most (Singh, Marcus & Ayres 2012 [16]; grade 10, abstract only). None of the opened sources gives the length in words or seconds where speech stops helping, and every sample is school students; the twenty-word limit is not drawn from them.

### The same text spoken and shown

Without graphics, narration with identical on-screen text beats narration alone, d = 0.78 for retention and 1.62 for transfer (Moreno & Mayer 2002 [17]; 74 college students). With graphics, identical on-screen text hurts in 16 of 16 tests, median d = 0.86 (Mayer & Fiorella 2014 [18]). In Mayer's corpus the modality principle, narration without captions against with captions, averaged g = 0.82 (Cromley & Chen 2025 [8]). The page with voice shows the spoken sentence beside a figure, the arrangement these lessons found harmful. The lessons ran at the system's pace with the sound always on; on the page the reader starts the sound, reads at rest and may never play it. Whether the harm holds there is untested.

### Reader-paced presentation

Segmenting a lesson helps, mostly when the system sets the pace. Over the segmenting literature, retention d = 0.32 [0.20, 0.43] and transfer 0.36 [0.24, 0.48], at the cost of learning time (−0.92); system-paced segmentation gave retention 0.42 and transfer 0.35, learner-paced retention 0.19 (not significant) and transfer 0.45 (Rey et al. 2019 [19], full text; mean age 19.71, mean segment 75.49 s, unsegmented material about 19 minutes; the learning-time results show publication bias). In the classic learner-started case, a 140-second narrated animation in 16 segments, learners did better on transfer and not on retention, d = −0.31 and 1.15 by Rey et al.'s table (Mayer & Chandler 2001 [20], abstract). In a study of learner control over an animated lesson for primary pupils, the play and pause buttons "were rarely used", and the gain the abstract reports appeared on the difficult questions (Hasler, Kersten & Sweller 2007 [21], abstract only). For animation, system-paced presentation beat learner-paced (g = 0.309; Berney & Bétrancourt 2016 [10]). The reader's control on the page therefore rests on his stated preference; the literature supports it for transfer and not for retention.

### Video against text for developers

In the one controlled study, 42 undergraduates learned a software tool from a text or a video tutorial. The text form was faster on the scenario tutorial (p = .0005, d = 3.14, a mean difference of 242.6 s), the final task showed no difference (p = .793), and participants looked up more in the text (p = .0067, d = 1.274; with both tutorials available, p = .0029, d = 1.7); they preferred video to learn and text to look things up, and their stated preference was not significant (6 video only, 4 equal, 3 text only, p = .065) (Käfer, Kulesz & Wagner 2017 [22], full text; lookup counts self-reported). Developers interviewed about screencasts named the lack of searchability as a barrier, and "explicit and formal knowledge is easier to codify in a written form" (MacLeod, Bergen & Storey 2017 [23], full text; 34 videos and 10 interviews, qualitative). Of 48 participants given a media-rich document, "experts largely ignored multi-media and primarily utilized text", while multimedia helped novices' reading time, time on task and comprehension (p = .0427, .0156, .0161) (Song et al. 2023 [24], abstract only; domain not stated). These fit the operator's choice to drop the video once the page did what it did: a report is something he returns to and looks things up in.

### Interactive articles

A review of interactive articles finds "limited empirical evaluation of the effectiveness of interactive articles"; it reports that only a fraction of a newspaper's readers interact with non-static content, and that readers preferred step or scroll layouts with no significant difference in engagement (Hohman et al. 2020 [25], full text; a review, not a trial). Interactive simulations against instruction without them gave g+ = 0.62 over 46 effect sizes, scaffolded simulations g+ = 0.49 over plain ones, and reasoning skills g+ = 0.26 (p = .17) from six effects (D'Angelo et al. 2014 [26], the report overview in full; 59 studies, K–12). The comparison there is with instruction lacking a simulation, not with a static figure of the same content. The source search found no randomised test of comprehension with an explorable explanation in adults, so the page's switch rests on the operator's reading.

## Rules and data

The table puts each reworked rule beside the readings behind it and the research beside it. Fit follows the older note: `direct` (the claim's own setting), `transfer` (another setting with the same mechanism) or `weak`; `practice` marks a rule resting on the operator's readings.

| Rule | Reading(s) behind it | Research beside it | Fit and caveat |
|--|--|--|--|
| The story is written for the ear: one claim per sentence, under about twenty words, a phrase that opens each part | 4 (the narration called ideal, the written story longer and more tangled); 2 and 3 for the story itself | Cardosi [11] and Prinzo et al. [12] for one item per spoken message; Clinton-Lisell [13]: listening against reading g = 0.07; Leahy & Sweller [14, 15] and Singh et al. [16]: long spoken text loses, short wins | `practice`: one reader, one case heard and one more generated; `research` transfer for the one-claim sentence. The twenty-word limit is the approved sample's longest sentence with headroom, not a tested threshold, and it was measured on Russian text |
| The opening gives the whole matter in three to five sentences: the task, how it ended, the problem with its cause, what is needed from the reader | 2 (the opening paragraph the one useful element; a report that opens on its result reads as a dump of terms); 6 (two sentences too thin) | Haviland & Clark [1]: given before new, 835 against 1016 ms; Aðalsteinsson et al. [6]: a summary before the review preferred; bounds: Hartley [2, 3] found labelled abstracts easier to search, Santesso et al. [4] tested a summary's format, not its place | `practice`: one reader, two cases; `research` transfer. Three sentences is the count below which he found the opening thin, in a text of one-claim sentences; agents under the rule opened with five |
| One picture for each part that has something to show, designed once and drawn in both forms | 5 (the text dry; the video's frame the best picture, wanted in every form; the unnamed switch unclear); 6 (the status-box picture unreadable) | Guo et al. [7]: g = 0.39 for text with graphics; Cromley & Chen [8]: text with diagrams g = 0.45; Höffler & Leutner [9] and Berney & Bétrancourt [10]: animation adds little for notation | `practice`: one reader, one case; `research` transfer for a picture beside its text. How many pictures a report needs is untested, and the kinds of picture are those that occurred in two cases |
| Two forms, text and page with voice; the text always, the page where a figure shows a mechanism or options behave differently; the reader's word overrides | 4 (audio onto the page, the choice left to the reader); 5; 6 (the video dropped) | Käfer et al. [22]: text for lookup, d = 1.274; MacLeod et al. [23]: video lacks searchability; Song et al. [24]: experts used text; Guo et al. [7], Cromley & Chen [8] for the figure | `practice` for the forms and the override; `research` transfer for the defaults. Students and instructional material throughout; no study compares these forms for an engineer reading a report |
| The page lights the sentence being spoken and the element of the figure it names; the reader scrolls, switches and starts the voice | 4 ("the piece being spoken glows a little brighter, but you click yourself"); 6 (the lighting better than a control that plays) | Rey et al. [19]: learner-paced segments help transfer (0.45), not retention (0.19 n.s.); Moreno & Mayer [17] and Mayer & Fiorella [18]: identical text helps narration without graphics and hurts it with them; Berney & Bétrancourt [10]: system-paced animation ahead (g = 0.309) | `practice`; `research` transfer with a bound. The page shows the spoken text beside a figure, the arrangement found harmful in lessons; whether it harms when the reader starts the sound is untested, so the reader's control rests on his preference |
| Calm figures: the page's own palette, one accent, each figure in its own frame, no picture for the opening, nothing that plays by itself | 6 (too garish, the pictures too close, the play control empty) | no study opened | `practice`: one reader, one page; which palette reads as calm is his judgement of one page |
| The decision is answered on the page: an option picked by a click, his words typed or dictated, one control that copies both for the chat | 6 (his request); 7 (the plan's page carried four decisions in this design) | consistent only: Menold 2020 [27], one question at a time | `practice`, untested: the provenance of the rule records that he had not yet used the copy control |

The skill's numbered rules carry three of these results. Rule 24 opens the operator's report with the paragraph that gives the whole matter; the five labelled lines are gone, by Reading 2 and the operator's first answer to the plan in Reading 7, and the checks with their exit codes stand in the list "Where to look". Rule 22 orders a report's parts by the order in which he needs the ideas, the cause before its effect, and keeps the riskiest place first only inside a list of places, where the position effect of Fregnan et al. [5] applies. Rule 18 opens the operator's decision card with one or two plain sentences that say what the matter is, with one concrete instance, before any identifier — the opening rule applied to a card; the records hold no reading of a decision card on its own.

## Open questions

- A large real report: every reading used a small fixture task, and the plan was the longest text he heard (62 sentences).
- A report without a decision, and one with several: case e, the only case without one, was read before the opening, picture and page rules existed, and the plan's four decisions were the only report with more than one.
- English text: every report and voice was Russian, so the twenty-word warning and the sentence counts are untested in English, where the same matter takes a different number of words.
- A voice without the operator's local speech synthesiser: one synthesiser voiced every page.
- The spoken text beside a figure when the reader starts the sound: the lessons that found it harmful ran at the system's pace.
- The twenty-word limit and the three-sentence bound as thresholds: the first is the approved narration's maximum with headroom, the second the count below which one reader found an opening thin.
- How many pictures a report needs, and which palette reads as calm.
- A client reader, or any reader other than the operator: no one else read these forms.
- Whether the page's copy control carries his answer back as intended: built, not yet used by him when the rules were written.
- The cold read on reports written in the story form and questioned by their real reader: the sixty real messages predate the form. A thing used before it is introduced: the read noticed two of twelve removed introducing sentences.

## Sources

Each line gives the citation, the locator, what was opened, and the narrowing. An entry reused from `README.md` §References names its number there; those were verified first-hand by the output-style programme or by the reading-contract note.

1. Haviland & Clark — What's New? Acquiring New Information as a Process in Comprehension — 1974 · doi:10.1016/S0022-5371(74)80003-4 · `README.md` no. 36 — 835 against 1016 ms for a sentence whose antecedent is given; undergraduates, two-sentence pairs.
2. Hartley, Sydes & Blurton — Obtaining information accurately and quickly: are structured abstracts more efficient? — Journal of Information Science 22(5), 1996 · doi:10.1177/016555159602200503 · abstract (ERIC EJ532829); the co-authors are verified on Crossref — structured abstracts easier to search, N = 52 and 56; no times or accuracy in the abstract.
3. Hartley — Current findings from research on structured abstracts — J Med Libr Assoc 92(3), 2004 · https://pmc.ncbi.nlm.nih.gov/articles/PMC442180/ · abstract — structured abstracts longer and "judged to be more informative and accessible"; a review by an advocate of the format.
4. Santesso et al. — A summary to communicate evidence from systematic reviews to the public improved understanding and accessibility of information: a randomized controlled trial — J Clin Epidemiol 68(2), 2015 · doi:10.1016/j.jclinepi.2014.04.009 · abstract — 53 % against 18 % understood, N = 143; both arms had a summary, so placement is not tested.
5. Fregnan, Braz, D'Ambros, Çalikli & Bacchelli — First Come First Served: The Impact of File Position on Code Review — 2022 · arXiv:2208.04259 · `README.md` no. 98 — 64 % lower odds of finding a defect in the file shown last, for one of two seeded defects.
6. Aðalsteinsson, Magnússon, Milicevic, Davidsson & Cheng — Rethinking Code Review Workflows with LLM Assistance: An Empirical Study — 2025 · arXiv:2505.16339 · full text — a summary before the review preferred for large or unfamiliar pull requests; qualitative, one company, 7 then 10 participants, a preprint.
7. Guo, Zhang, Wright & McTigue — Do You Get the Picture? A Meta-Analysis of the Effect of Graphics on Reading Comprehension — AERA Open 6(1), 2020 · doi:10.1177/2332858420901696 · full text — g = 0.39 [0.26, 0.51], 39 studies, 2,103 participants; no difference among picture types; mostly school-age readers.
8. Cromley & Chen — A meta-analysis of Richard Mayer's multimedia learning research: Searching for boundary conditions of design principles across multiple media types — Educational Research Review 49, 2025 · doi:10.1016/j.edurev.2025.100730 · full text (accepted manuscript) — text with diagrams g = 0.45, the modality principle g = 0.82, adult samples g = 0.74; one group's corpus, a significant Egger's test.
9. Höffler & Leutner — Instructional animation versus static pictures: A meta-analysis — Learning and Instruction 17(6), 2007 · doi:10.1016/j.learninstruc.2007.09.013 · abstract, as paraphrased by the fetch tool — d = 0.37 [0.25, 0.49], 26 studies, 76 comparisons; studies from 1973–2003, mostly physical processes.
10. Berney & Bétrancourt — Does animation enhance learning? A meta-analysis — Computers & Education 101, 2016 · doi:10.1016/j.compedu.2016.06.005 · full text of the authors' three-page conference paper and the journal abstract — g = 0.226 [0.12, 0.33], N = 7036; iconic ahead of abstract representations; system-paced ahead of learner-paced, g = 0.309.
11. Cardosi — An Analysis of En Route Controller-Pilot Voice Communications — DOT/FAA/RD-93/11, 1993 · https://rosap.ntl.bts.gov/view/dot/8659/dot_8659_DS1.pdf · `README.md` no. 83 — read-back errors 0.7 % to 1.4 % from three to four elements; listening under workload.
12. Prinzo, Hendrix & Hendrix — The Outcome of ATC Message Length and Complexity on En Route Pilot Readback Performance — DOT/FAA/AM-09/2, 2009 · https://libraryonline.erau.edu/online-full-text/faa-aviation-medicine-reports/AM09-02.pdf · `README.md` no. 88 — read-back errors rise from two topics per message.
13. Clinton-Lisell — Listening Ears or Reading Eyes: A Meta-Analysis of Reading and Listening Comprehension Comparisons — 2022 · doi:10.3102/00346543211060871 · `README.md` no. 48 — g = 0.07 overall; reading ahead only when self-paced and for inference.
14. Leahy & Sweller — Cognitive load theory, modality of presentation and the transient information effect — Applied Cognitive Psychology 25(6), 2011 · doi:10.1002/acp.1787 · abstract — long spoken text lost to written (N = 24), shorter spoken text won (N = 64); primary school, lengths not in the abstract.
15. Leahy & Sweller — Cognitive load theory and the effects of transient information on the modality effect — Instructional Science 44(1), 2016 · doi:10.1007/s11251-015-9362-9 · abstract — a modality by text length interaction; no numbers in the abstract.
16. Singh, Marcus & Ayres — The Transient Information Effect: Investigating the Impact of Segmentation on Spoken and Written Text — Applied Cognitive Psychology 26(6), 2012 · doi:10.1002/acp.2885 · abstract — segmenting helped both modalities, spoken most; grade 10.
17. Moreno & Mayer — Verbal Redundancy in Multimedia Learning: When Reading Helps Listening — 2002 · doi:10.1037/0022-0663.94.1.156 · `README.md` no. 40 — without graphics, narration with identical text ahead of narration alone, d = 0.78 retention.
18. Mayer & Fiorella — Principles for Reducing Extraneous Processing in Multimedia Learning — 2014 · doi:10.1017/CBO9781139547369.015 · `README.md` no. 43 — with graphics, identical on-screen text hurts, median d = 0.86 over 16 tests.
19. Rey, Beege, Nebel, Wirzberger, Schmitt & Schneider — A Meta-analysis of the Segmenting Effect — Educational Psychology Review 31(2), 2019 · doi:10.1007/s10648-018-9456-4 · full text — learner-paced segmenting: transfer 0.45, retention 0.19 n.s.; students, publication bias in the learning-time results.
20. Mayer & Chandler — When learning is just a click away: Does simple user interaction foster deeper understanding of multimedia messages? — Journal of Educational Psychology 93(2), 2001 · doi:10.1037/0022-0663.93.2.390 · abstract; the design and effect sizes read in Rey et al. [19] — learner-started segments helped transfer, not retention.
21. Hasler, Kersten & Sweller — Learner control, cognitive load and instructional animation — Applied Cognitive Psychology 21(6), 2007 · doi:10.1002/acp.1345 · abstract — "higher test performance with relatively lower cognitive load" across four conditions, on the difficult questions; the play and pause buttons rarely used; primary school.
22. Käfer, Kulesz & Wagner — What Is the Best Way For Developers to Learn New Software Tools? An Empirical Comparison Between a Text and a Video Tutorial — The Art, Science, and Engineering of Programming 1(2), 2017 · arXiv:1704.00074 · full text — text for lookup (d = 1.274), video preferred to learn; 42 undergraduates.
23. MacLeod, Bergen & Storey — Documenting and sharing software knowledge using screencasts — Empirical Software Engineering 22(3), 2017 · doi:10.1007/s10664-017-9501-9 · full text — video lacks searchability; qualitative, 34 videos and 10 interviews.
24. Song, Healey, Siu, Wigington & Stasko — Experts prefer text but videos help novices: an analysis of the utility of multi-media content — CHI '23 Extended Abstracts, 2023 · arXiv:2304.11565 · abstract — experts used the text, novices gained from multimedia; 48 participants.
25. Hohman, Conlen, Heer & Chau — Communicating with Interactive Articles — Distill, 2020 · doi:10.23915/distill.00028 (https://distill.pub/2020/communicating-with-interactive-articles) · full text; the DOI was resolved on Crossref for this note — limited empirical evaluation of interactive articles; a review.
26. D'Angelo, Rutstein, Harris, Haertel, Bernard & Borokhovski — Simulations for STEM Learning: Systematic Review and Meta-Analysis (Report Overview) — SRI International, 2014 · https://www.sri.com/wp-content/uploads/2021/12/simulations-for-stem-learning-brief.pdf · full text of the overview — g+ = 0.62 against instruction without simulations; K–12, researcher-designed tests.
27. Menold — Double Barreled Questions: An Analysis of the Similarity of Elements and Effects on Measurement Quality — 2020 · doi:10.2478/jos-2020-0041 · `README.md` no. 97 — a double question loses one part silently; consistent only for the decision on the page.
28. Lentz & De Jong — The evaluation of text quality: expert-focused and reader-focused methods compared — IEEE Transactions on Professional Communication 40(3), 1997 · doi:10.1109/47.649557 · abstract — experts "predicted less than 15% of the reader problems"; one government brochure. It backs the rule that the reader's questions are collected from the reader before the author's guess.
29. Wittwer, Nückles & Renkl — Is underestimation less detrimental than overestimation? The impact of experts' beliefs about a layperson's knowledge on learning and question asking — Instructional Science 36(1), 2008 · doi:10.1007/s11251-007-9021-x · full text, opened by a reader of the lead pass recorded in `research/2026-11-07_reader-intake-and-question-gate.md` [81] — 45 expert–layperson dyads; the layperson's knowledge gain was 8.47 of 18 when the expert held a valid estimate of his knowledge, 6.23 with a raised and 6.37 with a lowered one; the study tested valid against the two pooled and never raised against lowered. It backs the rule that the text skips what the reader holds and tells what he has not seen.
30. McNeil & Fyfe — "Concreteness fading" promotes transfer of mathematical knowledge — Learning and Instruction 22(6), 2012 · doi:10.1016/j.learninstruc.2012.05.001 · abstract — concrete images faded into symbols transferred better than symbols alone, concrete images alone did not; undergraduates, N and effect sizes not in the abstract. It stands beside the rule that a part's picture shows one concrete instance with its values.
