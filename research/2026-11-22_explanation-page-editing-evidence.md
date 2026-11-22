# Editing an explanation page: terms, lists, definitions, structure, figures, worked cases, references, controls and navigation — evidence report

A literature search asked how a long technical explanation, delivered as a page whose sentences are also spoken, is written and edited for engineers: its terms, its lists and marked statements, where its definitions stand, its structure, its figures, its worked cases, its references to code, its controls and its navigation. Nine units searched one question each and returned 232 findings, which the units labelled as 128 read first-hand, 98 by the abstract alone and 6 by relay. No source tests a practice on engineers reading an explanation; every result reaches such a page by transfer from students, apprentices, lay readers, developers or researchers, or stands as a norm.

Main results:

- Words placed beside the picture or the text they belong to taught better than the two set apart, g = 0.63 over 58 comparisons of learners with text and pictures [61]; joining helped only where the parts could not be understood apart [58], and notes worked into a text turned against readers who already knew it [87].
- Navigation kept behind a button was used in 27 % of desktop cases against 48 % and 50 % for navigation in view, and tasks took at least 39 % longer, in tests of site navigation on six consumer websites [154]; this goes against a map of the page closed behind a button in a wide window.
- Worked examples helped learners of mathematics, g = 0.48 [108], and assistance turned into a cost as knowledge of the taught domain grew, d = 0.505 for low against −0.428 for high prior knowledge over 60 studies of students and trainees [110]; this goes against a worked case for a reader who already knows the mechanism.
- Material that repeats what the learner holds cost learners as their expertise grew [62], and software manuals cut to what the reader needs, their introductions among the cuts, taught better, d = 0.89 over three studies [73]; skilled readers with high knowledge gained from a cohesive text [48], so the cost falls on restated content, not on the words that join sentences.
- Animation gave no gain over a still picture for abstract representations, g = 0.006 (k = 26), and no reliable gain with written text, g = 0.105 [94]; embellished charts were described as accurately as plain ones and recalled better after two to three weeks by 20 participants [90], which goes against removing every decoration from a chart.
- 28.9 % of the most popular GitHub projects held in their README or wiki a reference to a deleted code element at the time of the scan, and 82.3 % had held one at some point [68]; three documentation tools offer a build that fails on an unresolved reference, and the effect of such a check is untested.
- Synchronised highlighting of the spoken text gave no comprehension gain in three experiments, all with impaired readers [151] [152] [153]; an automatic copy of a selection goes against the desktop clipboard specification, under which a selection without a command to copy never sets the clipboard [143].
- Lists raised recall of the listed items in three of five studies of functional texts and lowered recall of the surrounding text in two [14]; broad voice menus beat deep ones [39], against a fixed cap on the length of a list; tests after each part of a video lecture raised a final test to 90 % against 68 % without them [79], while a replication with 195 students found no effect on learning [80], so the place of self-test questions is contested.

## What was investigated

Each question put a practice of writing or building such a page under test and asked what the sources say for it, what they say against it, and what they leave untested.

- **Q1 Terms.** Before the first sentence, the author collects the words the readers' team already uses for the things explained, from its code, its documents and its meetings, and writes with those words alone, names on the page matching names in the code; the notation of units and a script that enforces the list belong to the same practice.
- **Q2 Lists and a marked statement.** A paragraph that announces a count of parallel items sets them as a list, each item opening with its name, and the few sentences that carry the gist of a part stand in a visually marked block; both are also spoken by a synthesised voice.
- **Q3 Where a definition stands.** A term is defined in the sentence that first uses it and briefly again where it returns after a long gap, no sentence leans on a later one, and explanations that open at the term take the place of a table of terms at the end.
- **Q4 Structure.** After an opening part that gives a mechanism whole, either a part per line of its rule repeats the line and unfolds it, or the first part holds what each line needs and later parts hold only what can be understood apart, with no text on how to read the page.
- **Q5 Figures.** A figure stands at the first use of what it shows, its unused labels removed, a path drawn as a still line in place of a looping animation, a label on each arrow, one numbering across figure, pseudocode and prose, and a compound condition joined by a written "and" or "or".
- **Q6 Worked cases and the need for an input.** An exchange or a rule in words is followed by one worked case with numbers, a block a step; a derivation goes in steps in the order of its figure; an outcome comes with its causal step; and each input of a mechanism gets a case in which the mechanism without it fails.
- **Q7 References that open in place.** A name of the code in the text previews its declaration on hover or focus, opens it in a panel and links into the reader's editor; each line of the pseudocode names its method; the build fails on a name not found in the code; a term from the literature shows its paper.
- **Q8 Controls of a page read, heard and commented on.** A selection shows a small button and opens no comment window by itself; the selection is copied to the clipboard without a command; each part has its own play button in place of one player at the top; the voice pauses by a control and the Space key, not by a click on the text; the spoken sentence is lit.
- **Q9 Navigation.** A panel at the left lists every part with its figures, tables, pseudocode and questions, marks the item in view and filters by name; it stands open beside the text in a wide window and over the text on a narrow screen; each figure carries a short name written for the panel.

## Method

**Units.** Nine units searched one question each. A question file named the practice under test, its sub-questions and a list of leads marked as unverified recall, to be checked before use. A unit opened the source itself, the paper's page or PDF, the standard or the official documentation; nothing entered from memory, and what a unit could not open it listed apart.

**Findings.** Each finding names its source with the URL fetched and a locator inside it, a quote of at most 40 words, the design (who, what material, what comparison, what measure), the result, the bounds and its reading. A quote is copied character for character from the fetched text, and a script checks each quote that a clause carries against the text it fetches again from the source. Of 257 such quotes, the script found 149 word for word and 13 nearly so; it could not read 91, whose sources came as PDF (58) or JSON (33); 2 sources refused the fetch with HTTP 403; and for 2 it found no matching passage, a quote from Berney & Bétrancourt 2016 fetched at its repository page and one from the Material Design 1 selection pattern. The check covers quotes; a number in this report stands as the unit read it in the source. The reading says how the source was read, and a unit never raised it:

- `first-hand`: the unit fetched the source and saw in it the comparison, the measure, the sample and the result, or, for a norm, the prescribing text;
- `abstract`: a peer-reviewed paper read by its abstract alone; such a finding gives only what the abstract states;
- `relay`: the source was read about in another, opened document; such a finding is called a relay wherever this report uses it.

A figure a unit saw only in a search summary carries nothing here.

**Kinds of source.** An experiment, a meta-analysis or a field measurement counts as a test: 138 findings, of them 97 experiments, 26 meta-analyses and 15 field measurements. A standard or specification, a style guide or a piece of official documentation counts as a norm: 76 findings, 37, 17 and 22; a norm prescribes and measures nothing. A practice report, a review without a pooled measure, a design guide or observations without a count, counts as neither: 18 findings. Some narrative reviews of experiments were filed by their units under the kind of the experiments they review; this report gives no pooled number for them.

**Counts.**

| Question | Findings | First-hand | Abstract | Relay |
|--|--|--|--|--|
| Q1 Terms | 19 | 14 | 5 | 0 |
| Q2 Lists and a marked statement | 28 | 11 | 16 | 1 |
| Q3 Where a definition stands | 19 | 8 | 10 | 1 |
| Q4 Structure | 35 | 8 | 27 | 0 |
| Q5 Figures | 34 | 14 | 18 | 2 |
| Q6 Worked cases | 18 | 7 | 10 | 1 |
| Q7 References in place | 24 | 17 | 7 | 0 |
| Q8 Controls | 19 | 16 | 3 | 0 |
| Q9 Navigation | 36 | 33 | 2 | 1 |
| All | 232 | 128 | 98 | 6 |

The counts give the readings as the units labelled them. Each source a clause rests on was then compared with its opened text, statement by statement, and the comparison lowered the reading of nine sources: [4] in Q6, [9], [13], [57], [103], [107], [123], [155] and [176]. [Sources](#sources) gives each reading as it stands after the comparison.

Every finding is used below; a source that carries several findings appears once in [Sources](#sources).

**What could not be opened.** Each unit listed what it could not open, and none of it carries a claim here. The one experiment on synonyms against a repeated word in prose (Oversteegen & van Wijk 2003), ISO 704, ISO 1087 and the ISO/IEC Directives Part 2 returned 403. The signalling meta-analyses of Richter, Scheiter & Eitel 2016 and Schneider et al. 2018, Abraham's 2008 meta-analysis of glosses, DeStefano & LeFevre's 2007 review of hypertext reading and Bailey & Konstan 2006 on interruptions were blocked or had their abstracts withheld. Wright & Reid 1973 on alternatives to prose for contingencies, Potelle & Rouet 2003 on content maps and prior knowledge, the EARS paper, ISO/IEC/IEEE 29148, ANSI Z535, Inbar et al. 2007 and Gillan & Richman 1994 on minimalism in graphs, Aghajani et al. 2019 on documentation issues, and the controlled studies of recorded design rationale (Bratthall et al. 2000, Falessi et al. 2013, Karsenty 1996) were not opened. The web guidelines of Material 3 render by script and could not be read. Cuddihy & Spyridakis 2012 is closed and enters only as a relay. A pooled number that a unit saw only in a search summary, for a meta-analysis it could not open, is not given.

## Q1. Terms settled before the first sentence

Norms prescribe the core of the practice: the term the readers' company or field has approved, and one term for one concept throughout. The evidence on readers comes from names inside code, where whole words sped professional developers' defect finding by 19 % in one experiment and did not beat abbreviations in another. No source measures a list of terms made before the first sentence, a term linter on its own, or English trade terms against translated ones for engineers.

- ASD-STE100 Issue 9 [1] (first-hand), a controlled-language specification for aerospace maintenance procedures and readers with limited English. Rule 1.8: where the "company, industry, or subject field, has an approved technical noun", use it; such nouns stand "in official parts information and in company documentation". Rule 1.11 forbids a different technical noun for an item already named. It names the source of a term, not a step of collecting terms before drafting, and says nothing of meetings or code; the naming rules carry no condition of their genre.
- The Microsoft Writing Style Guide [2] (first-hand) prescribes "one term consistently to represent one concept" without a stated reason. Google's developer documentation style guide [3] (first-hand) asks for the exact same term, its capitalisation included, with translation as its reason, and forbids inflecting a code element's name in prose. Vendor norms for product and developer content; neither cites evidence.
- Lawrie et al. 2006 [5] (first-hand): over 100 programmers, students and professionals, described twelve functions whose identifiers were single letters, abbreviations or full words. Full words gave the best descriptions but never differed significantly from abbreviations, and beat single letters significantly in three of the twelve questions. It bears on the quality of names inside code, not on prose names matching code names.
- Hofmeister et al. 2017 [6] (first-hand): 72 professional C# developers with 14.0 ± 5.8 years of experience searched snippets for defects under three naming styles; words gave 19 % more defects found per minute than letters and abbreviations, which did not differ from each other. The developers were German speakers reading English identifiers, like part of the readers this report has in view; the material was snippets, not an explanation.
- Fakhoury et al. [7] (abstract; an author manuscript received in 2018): 25 undergraduate and graduate students localised bugs under fNIRS and eye tracking; lexical inconsistencies in the source code significantly raised cognitive load, and both lexical and structural inconsistencies lowered time performance and success. No effect sizes in the abstract. A mismatch between prose and code is the nearest analogue, a transfer.
- Vale's documentation [8] (first-hand) specifies the mechanism of a term list: entries of `accept.txt` must match exactly, case included, entries of `reject.txt` are flagged as errors, and a substitution check maps an observed variant to the expected term. It says nothing of readers. Doherty 2012 [9] (relay; the abstract of a submitted doctoral thesis): technical support documentation machine-translated from controlled-language input gave readers significantly higher recall and higher fixation count, fixation length and regressions, with slight non-significant increases in readability indices and human evaluations; the rule set is a bundle, so the share of its terminology rules is not isolated, and the readers read machine-translated output.
- The SI Brochure [10] (first-hand): prefix symbols "can neither stand alone nor be attached to the number 1"; a space separates the number from the unit; SI prefixes mean powers of ten only, and binary multiples take kibi, mebi and gibi. Where a descriptive term stands for counted entities, "the definitions of such terms and the conventions for their use must be clearly documented". Google's page on units [3] keeps the SI forms for units and adds a lowercase `k` with a noun for thousands ("55k download operations"). Together they allow a house convention for counts beside the SI, documented in a list.
- Guo 2018 [11] (first-hand): 840 survey responses from learners of programming in 86 countries; some found translated explanations more confusing "since syntax is in English anyway", others asked for bilingual terms. Coded self-reports with no outcome measure. Dasgupta & Hill 2017 [12] (abstract): longitudinal data on over 15,000 Scratch users in five countries; novices whose keywords and environment were localised demonstrated programming concepts at a faster rate than users of the same countries working in English. The users were young novices.
- Özkan et al. 2025 [13] (relay; the abstract of its preprint): a systematic review of 36 peer-reviewed studies of Domain-Driven Design closes that "More empirical evaluations and open discussions on challenges are needed"; the abstract does not name the ubiquitous language.

Against or mixed:

- Full words against abbreviations: Hofmeister et al. found a 19 % gain, Lawrie et al. no significant difference.
- McNamara et al. 1996 [4] (abstract): students, junior high school ones in the first of two experiments, gained from a minimally coherent science text where they knew much of the domain and from a coherent one where they knew little. Whether its manipulation touched the repetition of terms was not opened; it bounds how far explicitness helps knowledgeable readers, not which term a text uses.
- Dasgupta & Hill 2017 goes against English terms for novices and says nothing of engineers.

Untested:

- A list of terms made before the first sentence against terms aligned in an edit after the draft.
- A term list enforced on its own, apart from a bundle of controlled-language rules.
- English trade terms against translated or coined native words in German or Russian text read by engineers.
- Synonyms against a repeated term in expository prose: the one experiment the search found could not be opened.

## Q2. Counted enumerations as lists, and a marked key statement

Parallel items set as a list were recalled better than the same items in a paragraph in most comparisons with lay readers, students and web users, but the gain shrank for items of different kinds and the surrounding text was recalled worse in two of five studies. Signals raise memory for what they cue, d = 0.38 across multimedia studies; a mark on the wrong content harmed, and for learners with high prior knowledge added signals harmed. A spoken outline with ordinal words raised transfer in one relayed experiment; no study compares numbered with bulleted lists or tests an item that opens with its name, and none used a synthesised voice.

Lists:

- Jansen 2014 [14] (abstract): five studies with health flyers, direct-mail letters and recipes compared a bulleted list with the same series run into a paragraph. Item recall was higher in three studies, the gain "mitigated if the components are heterogeneous"; recall of the surrounding text was lower in two, and the evaluation higher in two. Functional texts rather than an explanation, their readers not described; no samples or effect sizes in the abstract.
- Karreman & Loorbach 2007 [15] (first-hand): 347 students used a 20-page website whose instructions stood in numbered lists or in paragraphs. The list version led to more pages visited (t = 2.65, p < 0.01) and higher appreciation (t = 2.85, p < 0.01); content knowledge differed at p = 0.07 and time on the site at p = 0.11. Procedural content, with list and numbering confounded.
- Morrow et al. 1998 [16] (abstract): younger and older adults understood and recalled list-formatted medication instructions better than paragraphs, and the lists reduced age differences; category headers inside paragraphs hurt readers with low working-memory span. Medication instructions whose list format stressed the order of the information.
- Morkes & Nielsen 1997 [17] (first-hand): 51 experienced web users, about ten a condition; a "scannable" version of a promotional site, with bulleted lists, bold keywords, captions, more headings and shorter sections, scored 147 against 100 on a combined usability measure. Five changes in one bundle and one-tailed tests; its Table 2 lists memory at 94 against 100 while its text calls memory significantly better.
- Lyngo Lab [18] (first-hand; self-published, not peer-reviewed): 400 crowd workers recalled 1.98 of three grocery items shown as a list against 1.48 shown in a paragraph (p < 0.001). Three trivial items in one vignette.
- Garner & Alley 2013 [19] (first-hand): 110 engineering students heard a narrated talk on MRI; slides with a sentence headline and visual evidence beat topic headlines with bullet lists on essay comprehension, d = 0.81. The two conditions differ in six design principles, so the list's own share is unknown, and the authors' claim that a bulleted list constrains the relations between items is argument, not measurement. The only study in the search with engineering readers; its medium is a talk with slides.

Marking:

- Lorch 1989 [20] (abstract; a narrative review): "Virtually all types of signals produce better memory for information they cue in a text, whereas memory for unsignaled information often is unaffected"; it finds little evidence on comprehension. In the same line of work with college students, typographical cues raised attention and memory only for the signalled content (204 students; Lorch, Lorch & Klusewitz 1995 [21], abstract), numbering target sentences directed attention to them (Lorch & Chen 1986 [22], abstract), and headings, overviews and summaries organised recall by topic (285 students; Lorch, Lorch & Inman 1993 [23], abstract).
- Alpizar et al. 2020 [24] (abstract): over 44 effect sizes from 29 experiments with 2,726 participants, signalling in multimedia learning went with better outcomes, d = 0.38, the benefit found in studies of high quality that used a pretest and controlled prior knowledge. Multimedia materials rather than a text.
- Gier et al. 2009 [25] (abstract): 180 undergraduates; inappropriate highlighting impaired comprehension and metacognitive accuracy, and readers' confidence then correlated negatively with their scores. The abstract reports no gain of appropriate highlighting over none. Silvers & Kreiner 1997 [26] (abstract): inappropriate highlighting interfered with a reading test, and a warning beforehand did not remove the effect.
- Google's page on notices [27] (first-hand): "When you use multiple notices on a page, they begin to lose their visual distinctiveness", and a warning means "Don't do this" or a step that might be irreversible. OSHA 29 CFR 1910.145 [28] (first-hand): caution signs "shall be used only to warn against potential hazards or to caution against unsafe practices"; physical signs, carried to a page by analogy. Hunt 1995 [29] (abstract; a review): an item is remembered better when it differs from otherwise similar items; that a mark loses force when overused is an inference from it, untested.
- WCAG 2.2 [30] (first-hand): colour is not the only visual means of conveying information (SC 1.4.1), and structure conveyed by presentation can be determined by a program or is available in text (SC 1.3.1).

Speech:

- Titsworth & Kiewra 2004 [31] (abstract): spoken organisational cues in a lecture raised the organisational points students noted by 39 % and the details by 35 %, and test achievement by 15–45 %. A human voice; the form of the cues is not in the abstract.
- Mayer 2002 [32] (relay of Mautone & Mayer 2001, Experiment 3, reported by its co-author): a narrated animation on how airplanes achieve lift, signalled by a spoken outline of the main steps in ordinal words, item headings spoken in a deeper voice, pointer words and louder key words, raised transfer, effect size 0.74, which the chapter says needs further research to confirm. One experiment with students, four spoken signals in one bundle, no sample size in the chapter.
- SSML 1.1 [33] (first-hand): `break` and `emphasis` are author controls, and "The synthesis processor determines how to render emphasis". It defines the means, not their effect.

Norms on lists:

- The HTML standard [34] (first-hand) gives `ol` to items whose order carries meaning, `ul` to items whose order does not, and `dl` to name–value groups. Google's page on lists [27] (first-hand) prescribes numbered lists for sequences, bulleted lists otherwise, a description list for terms each with its explanation, the same syntax for all items and a complete introductory sentence. The federal plain-language guideline [35] (first-hand) prescribes a lead-in sentence and parallel items, warns that lists can be overused and limits nesting to two or three levels, citing no study. Frazier et al. 2000 [36] (abstract): parallel conjuncts inside one sentence were read faster in four studies; a transfer to list items.

Against or mixed:

- Richter et al. 2018 [37] (abstract): with 8th graders, colour coding and deictic references between text and pictures helped learners with low prior knowledge and harmed learners with high prior knowledge, who reported more extraneous load. Yeari et al. 2017 [38] (abstract): proficient readers processed and recalled the central information the same whatever was highlighted, and highlighting peripheral information drew rereading to it.
- Jansen 2014: the text around a list was recalled worse in two studies; Garner & Alley 2013 for related content set in bullets.
- Commarford et al. 2008 [39] (abstract): broad voice menus beat deep ones on performance and satisfaction, more so for users with low working memory, against the practice of five items or fewer; menus to choose from, not explanatory enumerations. Cowan 2001 [40] (abstract; a review): about four chunks when items cannot be grouped or rehearsed, a limit a reader who can reread does not meet.

Untested:

- Numbered against bulleted lists: every study compared a list with a paragraph.
- An item that opens with its name, apart from other signals.
- A synthesised voice reading a count, ordinal words or a marked block.
- How much marked text is too much: the claims of overuse are norms.
- A list or a marked block in a technical explanation read by engineers.

## Q3. Where a definition stands

One test on technical text bears on a definition placed at the term: researchers answered term questions about a paper 45.4 s faster with definitions shown at each use, and no more correctly. In lessons for novices, the names and states of a system's parts taught before an explanation beat the same taught after it. No study tests a definition said again where a term returns after a gap, or the cost of a term used before its definition in expository text.

- Head et al. 2021 [41] (first-hand): 27 participants who had read machine-learning papers, most of them students, answered questions on one paper under a plain PDF reader, a decluttering view and the full tool with definition tooltips, equation diagrams and a priming glossary. Against the plain reader, the full tool cut the time per question by 45.4 s (p = 0.0001) and the area of the paper viewed by 25 percentage points, and raised ease by 1.70 on a five-point scale; correctness did not change (0 points, p = 1.000). In 15–20 minutes of free reading, readers opened term tooltips a median of 5 times and symbol tooltips 10 times, while the priming glossary was "the least-used feature", consulted for 10 s or more by 6 of 27. On one question about a symbol the paper used inconsistently, readers with the tool almost always answered wrong, because its extracted definitions missed a sense. In the pilot studies of its prototypes, two readers did not want a tooltip that repeated the definition they were already reading. A PDF with tooltips, one timed question of up to four minutes per interface and several features in one bundle; researchers stand close to engineers in expertise.
- Mayer, Mathias & Wetzell 2002 [42] (abstract): students pre-trained on the parts of a car brake or a tire pump and their possible states did better on transfer in all three experiments, against post-training as well in the third. Mayer & Moreno 2003 [43] (relay; the authors' review of their own experiments) give a median d = 1.00 against no pre-training, and d = .48 in one study for on-screen text integrated with an animation against text set apart. Short narrated animations for novices; the pre-training was a block before the lesson, not a definition inside a sentence.
- Kester et al. 2004 [44] (first-hand): 72 students without prior statistics practised 24 tasks of a chi-square course; the conceptual information the theory calls supportive was more efficient given during practice than before it (transfer efficiency 0.28 against −0.30; F(1, 68) = 6.07, η² = 0.082), with no difference in raw test scores, the opposite of the theory's prediction. Kester et al. 2005 [45] (abstract): procedural information integrated in a circuit diagram beat a separate source on transfer problems, not on equivalent ones.
- O'Brien, Plewes & Albrecht 1990 [46] (abstract): readers of passages with an early and a late possible antecedent reinstated a late antecedent faster than an early one, and an elaborated antecedent faster than a bare one. O'Brien, Duffy & Myers 1986 [47] (abstract): an anaphoric reference in the last line brought a backgrounded item back to mind. Antecedents within one passage; neither tests a restated definition.
- O'Reilly & McNamara 2007 [48] (abstract): 143 college students; the benefit of a low-cohesion text was confined to less skilled readers with high knowledge, and skilled readers with high knowledge gained from high cohesion. It narrows McNamara et al. 1996, where readers with high knowledge gained from a minimally coherent text.
- van Gompel & Liversedge 2003 [49] (abstract): in three eye-tracking experiments, reading was disrupted where gender or number information contradicted the referent readers preferred for a cataphoric pronoun, which the authors read as coreference computed before that information is used. Gernsbacher & Shroyer 1989 [50] (abstract): in spoken narratives, a concept introduced with "this" was more accessible later. Pronouns and short narratives, not a technical term used sections before its definition.
- Yanagisawa et al. 2020 [51] (abstract): 359 effect sizes from 42 studies (N = 3,802) of second-language reading; glossed reading led to 45.3 % immediate learning of the glossed words against 26.6 % without glosses, and in-text glosses and glossaries were the least effective gloss types. Vocabulary learning in a second language, not comprehension of technical text.
- Norms. WCAG 2.2's explanation of SC 3.1.3 [52] (first-hand) accepts a definition at the first occurrence, or a mechanism such as a glossary link at each occurrence, and asks for a definition at each occurrence where a word carries several meanings on one page. Google's pages on jargon and abbreviations [53] (first-hand) prescribe a brief description of a term on first reference, or a link to a definition, and the bare term after it. WCAG 2.2 SC 1.4.13 [30] requires content shown on hover or focus to be dismissible, hoverable and persistent.

Against or mixed:

- Head et al. 2021: speed and effort changed, correctness did not, and an incomplete definition in place misled.
- Kester et al. 2004 goes against the advance placement of conceptual information that pre-training favours.
- McNamara et al. 1996 [4] for readers with high knowledge, narrowed by O'Reilly & McNamara 2007.
- Kalyuga, Chandler & Sweller 2004 [54] (abstract): in the third of three experiments, with 25 technical apprentices, technical text spoken and shown at once was less efficient than the spoken text alone. A cost of two modes at once, not of a reminder after a gap; it bears on a page that speaks the text it shows more than on a restated definition.

Untested:

- A definition said again at a distant return, for any reader.
- A term used before its definition in expository text.
- A glossary at the end against glosses in place, for first-language readers of technical text.

## Q4. One whole part, or an overview with a part per element

No study compares the two designs. By transfer from students, apprentices and trainees, the sources bear on four of their pieces: an overview first has a small positive effect that does not shrink for stronger learners; a reason beside the row that needs it helps where the parts cannot be understood apart (g = 0.63 over 58 comparisons); material that repeats what the learner holds cost learners as their expertise grew; and manuals cut to what the reader needs taught better (d = 0.89 over three studies). Skilled readers with high knowledge gained from a cohesive text, reading-time labels and reading routes have no test on comprehension, and questions after each part are contested.

Overview first:

- Luiten, Ames & Ackerson 1980 [55] (abstract): over 135 studies, "Advance organizers were shown to have a small facilitative effect." Their conference version [56] (first-hand, an OCR scan) reports that high-ability subjects "had an average effect size almost twice that of low ability subjects", with ability defined differently across studies. Stone 1982 [57] (relay; the ERIC record of a conference paper): a "lack of special facilitation for low ability, or low knowledge learners", and lower effects for older learners. School and college learners; an organiser is a bridging passage before the material, not an overview of a mechanism.
- Lorch, Lorch & Inman 1993 (Q2): with signals, students "remembered more topics but recalled less about each accessed topic".

A reason beside its row:

- Chandler & Sweller 1991 [58] (abstract): six experiments with electrical engineering and biology material, one a three-month industrial training study. Integrated instructions won where the material was "unintelligible without mental integration" and were "no better than split-source information" where it was not; "seemingly useful but nonessential explanatory material" harmed "even when presented in integrated format" (Experiments 3–5).
- Chandler & Sweller 1992 [59] (abstract): students reading empirical research reports, whose mutually referring segments are conventionally set apart, spent less time on them integrated and still scored higher. The nearest material to a table above with its reason far below.
- Ginns 2006 [60] (abstract): over 50 studies, contiguity brought "substantial learning gains", "for complex learning materials in particular", in research on novices. Schroeder & Cenkci 2018 [61] (abstract): integrated against split designs, g = 0.63 over 58 comparisons (n = 2,426), across many moderators. Words with pictures; the abstract reports no moderation by prior knowledge.

Repetition and expertise:

- Kalyuga, Chandler & Sweller 1998 [62] (abstract): with learners using a diagram and its text, the best design moved, as expertise grew, from text integrated with the diagram to the text removed. Kalyuga, Chandler & Sweller 2000 [63] (abstract): after further training, a diagram alone beat a diagram with spoken text. Kalyuga, Ayres, Chandler & Sweller 2003 [64] (abstract): techniques highly effective with inexperienced learners "can lose their effectiveness and even have negative consequences" with experienced ones.
- Yue, Bjork & Bjork 2013 [65] (abstract): on-screen text identical to the narration impaired learning in two experiments, slightly different wording helped, and learners preferred the identical text all the same. A page that speaks the text it shows is the identical case.
- Cepeda et al. 2006 [66] (abstract): over 839 assessments in 317 experiments, the gap between study sessions that gave the most retention grew with the retention interval. Rawson & Kintsch 2005 [67] (abstract): 423 college students; rereading at once helped only on an immediate test. A repetition within one page read in one sitting is massed.
- O'Reilly & McNamara 2007 (Q3) against McNamara et al. 1996: skilled readers with high knowledge gained from cohesion.

One place for a fact:

- Tan, Wagner & Treude 2023 [68] (first-hand): README and wiki pages of over 3,000 GitHub projects. At the time of the scan, 28.9 % of the most popular projects (265 of 918) held at least one reference to a deleted code element, and 82.3 % had held one at some point; 3.9 % of references and 19.2 % of documents were outdated. It detects deleted names only, and measures documentation against code, not two places of one document.
- Wen et al. 2019 [69] (abstract): 1.3 billion AST-level changes in 1,500 systems; types of code change trigger updates of the related comments at different rates, which the abstract does not give.
- Google's page on procedures [70] (first-hand): "Avoid repeating procedures. Instead, reference those procedures and link to them", and no introductory sentence that only repeats its heading. GitLab's style guide [71] (first-hand): its single-source-of-truth policy "Does not mean that content cannot be duplicated in multiple places". DITA 1.3 [72] (first-hand) defines content references as a mechanism of reuse.

Text on how to read the page:

- Ginns, Hollender & Reimann [73] (first-hand): minimalist against system-centred training material, d = 1.12 over 13 effects; the heuristic "slash the verbiage", whose cuts include system introductions, d = 0.89, 95 % CI 0.36–1.42, over three studies with 120 participants. Adults learning software from manuals, measured on time, errors and performance; three studies give a wide interval.
- Lazonder & van der Meij 1993 [74] (abstract): 64 first-year students learned a word processor faster and better from a minimal manual, with no interaction with prior computer experience. Carroll et al. 1987 [75] (abstract): the Minimal Manual gave more efficient learning progress than a commercial manual in two experiments.
- Galesic & Bosnjak 2009 [76] (abstract): the longer the stated length of a web questionnaire, 10, 20 or 30 minutes, the fewer respondents started and completed it. Villar et al. 2013 [77] (abstract): over 32 experiments, a constant progress indicator did not reduce drop-off. Survey respondents and their uptake, a neighbouring question.

Segmenting:

- Rey et al. 2019 [78] (abstract): over 56 investigations and 88 comparisons, segmenting helped retention and transfer, and learners with high prior knowledge gained more on retention. Multimedia against continuous presentation; a web page is already paced by its reader.

Questions after each part:

- Szpunar et al. 2013 [79] (first-hand): a 21-minute statistics video in four segments. With a test after each segment, Experiment 1 (n = 32) gave 84 % against 59 % on the fourth segment (d = 1.03), and Experiment 2 (n = 48) gave 90 % on the final cumulative test against 76 % for restudy and 68 % without tests (d = 1.38); mind wandering fell to 19 % of probes from about 40 %.
- Welhaf et al. 2022 [80] (abstract): 195 undergraduates with a narrated statistics slideshow; no effect of interpolated tests on learning against interpolated restudy.
- Hamaker 1986 [81] (abstract): adjunct questions strongly help repeated test items and less so related ones; factual questions harmed unrelated items when study time was controlled; the effect did not depend on the distance between a question and its text. Roediger & Karpicke 2006 [82] (abstract): testing beat restudy on delayed tests. Adesope et al. 2017 [83] (abstract): practice tests beat restudy and every other comparison condition.

Against or mixed:

- Mayer & Chandler 2001 [84] (abstract): a lightning animation seen first in learner-paced parts and then whole beat the reverse order on transfer, not on retention; a counterpoint to whole-first for novices.
- O'Reilly & McNamara 2007: skilled experts gain from cohesion, so the expert cost falls on restated content, not on joining words.
- Welhaf et al. 2022 against Szpunar et al. 2013; both used video lectures, neither a page read at the reader's pace.
- The GitLab policy permits duplication within one body of documentation.

Untested:

- The two designs compared on one explanation.
- Drift between two places of one document.
- The cost of a single restated sentence for an expert reader.
- Reading routes by available time, and a stated reading time, on comprehension.
- Questions after each part against one section at the end, on a page read at the reader's pace.

## Q5. Figures of a mechanism

Contiguity of words and pictures has the strongest evidence, g = 0.63 over 58 comparisons, and a lag of 2 s between narration and animation already harmed pupils' recall; integration aids turned against readers with prior knowledge. Animation gave no gain over a still picture for abstract representations or with written text. Interesting material off the goal harms learning, while embellished charts were read as accurately and recalled better, so strict minimalism has no ground; labels on arrows, one numbering and written connectives rest on norms and on transfer.

Contiguity:

- Ginns 2006 and Schroeder & Cenkci 2018 (Q4).
- Porte et al. 2026 [85] (abstract): 227 pupils about 12 years old in a desktop VR lesson on soil decomposition, with narration–animation offsets of −6, −2, 0, +2 and +6 s; "Temporal gaps, even -2 s had a significant negative effect on recall and comprehension." Liu, Lin & Paas 2022 [86] (abstract): 99 undergraduates; key points that appeared as the narration reached them beat the whole slide shown during the narration and the narration played before the visuals. The nearest analogues to lighting an element as the voice names it, with children and students.
- Oksa, Kalyuga & Chandler 2010 [87] (abstract): modern-English notes integrated line by line in Shakespearean text lowered load and raised comprehension for novices, and "a reverse effect occurred" with Shakespearean experts, whose protocols called the notes redundant. Literary text, not diagrams.

Coherence and decoration:

- Rey 2012 [88] (abstract): over 39 effects, seductive details, interesting material off the learning goal, harmed retention (small to medium) and transfer (medium). Sundararajan & Adesope 2020 [89] (abstract): seductive details "can hinder learning", with design moderators; no number in the abstract. An unused label is irrelevant but not seductive, so the transfer to it is indirect.
- Bateman et al. 2010 [90] (first-hand): 20 students; embellished charts were described "no worse" than plain ones and recalled significantly better after two to three weeks. Simple charts with one trend and imagery about their topic; the authors are cautious about recommending the style for all charts.

Labels and arrows:

- Huestegge & Philipp 2011 [91] (abstract): in four eye-tracking experiments, a legend ordered like the data cut comprehension time, retrieval time and gaze shifts between data and legend; no condition put labels on the elements. Its introduction states, relaying design guides it cites and the search did not open, that direct labelling in dense graphs "cannot be considered a panacea" (relay).
- Heiser & Tversky 2006 [92] (abstract): people described mechanical diagrams without arrows as structure and with arrows as function, and drew arrows themselves to show a process. No comparison of a label on the arrow with a label elsewhere.

Animation:

- Höffler & Leutner 2007 [93] (abstract): 26 studies and 76 comparisons of animation against static pictures, d = 0.37 (95 % CI 0.25–0.49); representational animation 0.40, realistic video 0.76, procedural-motor knowledge 1.06.
- Berney & Bétrancourt 2016 [94] (first-hand): 61 studies, N = 7,036, 140 comparisons; g = 0.226 overall; iconic representations g = 0.245 and abstract ones g = 0.006 (k = 26); with written commentary g = 0.105 (k = 58, not significant), with narration 0.320, without text 0.886; cueing did not change the effect. Diagrams of software mechanisms fall among the abstract representations of this coding; text and voice together are not isolated.
- Tversky, Morrison & Bétrancourt 2002 [95] (first-hand; a review): where animation seemed superior, the animated and static versions often differed in content or procedure, and "Animations are often too complex or too fast to be accurately perceived."
- Abrams & Christ 2003 [96] (abstract): in visual search, moving letters among static ones drew no advantage, letters that had just started to move did. A loop that restarts makes repeated onsets; whether they disrupt reading is untested.
- Norms. WCAG 2.2 SC 2.2.2 (Level A): moving content that starts automatically, lasts more than five seconds and stands beside other content needs a mechanism to pause, stop or hide it; it asks for control, not for a still figure. Its explanation [97] (first-hand) names distraction: "Some people with cognitive disabilities and attention deficits are distracted by continuous movement." Media Queries Level 5 [98] (first-hand; a working draft): `prefers-reduced-motion: reduce` means the user prefers motion removed or replaced. The explanation of SC 2.3.3 [99] (first-hand; Level AAA): motion triggered by interaction can be disabled unless essential.

Several representations:

- Ozcelik et al. 2009 [100] (abstract): 52 participants; colour coding the corresponding parts of text and picture raised retention and transfer, and the eye data located the gain in finding corresponding information. Seufert 2003 [101] (abstract): 87 college students; directive help in relating representations aided recall. Ainsworth 2006 [102] (abstract; a framework): many studies show that the promise of multiple representations "is not always achieved". Colour and directive help, not shared numbering.
- Richter et al. 2018 (Q2): the same kind of integration signal harmed learners with high prior knowledge.

Compound conditions:

- Holland & Rose 1981 [103] summarise an earlier experiment of theirs (relay; its numbers were not seen): an "or" carried by commas ("A, B, C, or D") was harder to follow than a repeated "or" ("A or B or C or D"), a series of three or more "or"s harder than paired ones ("A or B, and C or D, and E or F"), and strings of "or" harder than strings of "and", which they attributed "to the potential ambiguity of "ors" expressed implicitly in commas"; instructions of the form "If you are ..., press button A", its subjects not described. In their own experiment (relay; the ERIC abstract of a technical report whose review is not known), subjects neither counted nor described there followed complex conditional instructions more easily as algorithms (lists, flowcharts) than as prose once they had practised with feedback, while on the first exposure the advantage "drastically reversed" in speed and accuracy.
- Berry, Kamsties & Krieger 2003 [104] (first-hand), a handbook of ambiguity in contracts and requirements: a sentence that mixes "and" with "or" is ambiguous, and "physical structure or enumeration" shows precedence; "either ... or" marks an exclusive and "either ... or ... or both" an inclusive or; a well-placed comma can group written connectives. NASA's checklist for requirements [105] (first-hand) lists "and/or" among ambiguous terms.

Captions and references to a figure:

- Kim, Setlur & Agrawala 2021 [106] (first-hand): crowd workers (219, then 2,168) reading single-line charts took a caption's feature as their takeaway when the chart made it prominent; "when the caption describes a low-prominence chart feature, readers rely on the chart". Zhu, Cheng & Wu 2022 [107] (relay; a preprint read by its abstract): with a caption present, many readers recalled y-axis values, and the best caption level depended on the chart. Line charts and lay readers, not diagrams of a mechanism.
- The HTML standard's section on `figure` (first-hand): referring to a figure by its relative position, "in the photograph above", ties it to its place, while a reference by number or caption lets it move.

Against or mixed:

- Oksa et al. 2010 and Richter et al. 2018: integration aids harmed readers with prior knowledge, which engineers are for the parts of a system they know.
- Bateman et al. 2010 against strict minimalism; the harm of seductive details concerns content off the goal.
- Höffler & Leutner's d = 0.37 against Berney & Bétrancourt's g = 0.226 and its null for abstract representations.
- Holland & Rose: algorithm formats lost on the first exposure, and a reader meets each condition of a page once.
- Berry et al.: a comma that groups written connectives does no harm; the harm found is a comma in place of a connective.

Untested:

- A label on an arrow against one in a legend or a caption.
- One numbering across figure, pseudocode and prose, and a reference to a numbered line before the reader has seen the numbers.
- Unused labels on a mechanism diagram.
- A looping trace against a still line on a page with written text and voice.

## Q6. Worked cases, and the case that shows an input is needed

Worked examples help learners with little knowledge of a procedure (g = 0.48 in mathematics), and the help turns into a cost as knowledge of the taught domain grows (d = 0.505 for low against −0.428 for high prior knowledge over 60 studies). That knowledge is of the taught domain, so an engineer meets an unfamiliar mechanism as a novice in it; no study tests engineers. Labels on groups of steps raised transfer, a single example transferred poorly, and the case without an input rests on a review of how people ask for explanations and on a norm of machine-learning papers, with no test on readers.

- Barbieri et al. 2023 [108] (abstract): 55 studies and 181 effect sizes in mathematics from elementary to post-secondary level; worked examples had a medium average effect, g = 0.48; correct examples alone did best, and self-explanation prompts lowered the effect.
- Kalyuga, Chandler, Tuovinen & Sweller 2001 [109] (abstract): trade apprentices; "With more experience in the domain, worked examples became redundant and problem solving proved superior." Kalyuga et al. 2003 (Q4; first-hand here): "inexperienced learners benefitted most from an instructional procedure that placed a heavy emphasis on guidance" in every experiment the review describes.
- Tetzlaff et al. 2025 [110] (first-hand): 176 effect sizes from 60 experimental studies with 5,924 participants; learners with low prior knowledge learned better from high assistance, d = 0.505, and learners with high prior knowledge from low assistance, d = −0.428. Prior knowledge is domain-specific; the samples run from primary school to vocational training.
- Fyfe et al. 2014 [111] (abstract; a review that argues a recommendation, with no pooled number): begin with concrete material and fade to the abstract; concrete means objects and materials. Trninic, Kapur & Sinha 2020 [112] (abstract): improved concrete examples did as well as or better than abstract ones, in a replication of a reported advantage of abstract examples. Xie, Nelson & Ko 2018 [113] (abstract): 24 novice programmers taught to trace a program line by line while updating an external representation of memory scored 15 % higher on tracing problems; the learner traced, the text did not trace for him.
- Catrambone 1998 [114] (first-hand): "Across 4 experiments it was found that a label for a group of steps in examples helped participants form subgoals"; Experiment 1 had 150 college students solve probability problems, and learners with the stronger background given abstract labels were more likely to form representations free of misleading surface features. Margulieux, Morrison & Decker 2020 [115] (abstract): 265 students of an introductory programming course; subgoal-labelled examples improved weekly quizzes and lowered withdrawal and failure, not exam scores.
- McNamara et al. 1996 (Q1; here a relay, the summary ERIC wrote in place of the authors' abstract): coherence improved comprehension, and readers with enough background knowledge given a text that forced them to infer unstated relations understood it more deeply. Britton & Gülgöz 1991 [116] (relay; the opening of its abstract): Kintsch's model located the places of a 1,000-word expository text where inferences were called for, and each was repaired to make a principled revision; the result was not on the opened page.
- Gick & Holyoak 1983 [117] (first-hand): 98 students; two analogs gave 45 % spontaneous transfer to the radiation problem against 21 % for one (80 % against 53 % in all, a hint included), and statements and diagrams that did not help with one analog helped with two. Atkinson et al. 2000 [118] (first-hand; a review): "transfer is enhanced when there are at least two examples presented for each type of problem taught". Alfieri, Nokes-Malach & Schunn 2013 [119] (abstract): 336 tests from 57 experiments; comparing cases led to more learning than single or sequential cases, d = 0.50, 95 % CI [0.44, 0.56], with the learner asked to compare. Schwartz & Bransford 1998 [120] (abstract): analysing contrasting cases before a lecture or a text led to more accurate predictions than reading or summarising before it.
- Miller 2019 [121] (first-hand; a review of philosophy and psychology): "people do not ask why event P happened, but rather why event P happened instead of some event Q". Lipton & Steinhardt 2018 [122] (first-hand; a position paper): without ablations a paper "misleads readers to believe that all of the proposed changes are necessary", and ablation "is neither necessary nor sufficient for understanding a method". Meyes et al. 2019 [123] (relay; a preprint read by its abstract): ablating parts of neural networks showed some representations redundant, so taking one part away need not cause a failure.

Against or mixed:

- The expertise reversal (Kalyuga et al. 2001 and 2003, Tetzlaff et al. 2025) goes against a worked case for a reader who already knows the mechanism.
- McNamara et al. 1996 goes against stating every causal step for knowledgeable readers who make the inferences themselves; for readers with low knowledge it points the other way.
- Gick & Holyoak 1983 and Atkinson et al. 2000: one example underdetermines the rule it illustrates.
- Margulieux et al. 2020: the subgoal gain did not reach the exams.
- Barbieri et al. 2023: self-explanation prompts lowered the effect, while subgoal labels raised transfer; whether the difference lies in a label given against a prompt to generate one was not checked.

Untested:

- A worked case for experienced engineers reading an unfamiliar mechanism.
- A derivation in the order of its figure's blocks against a chained line of equalities.
- A text that traces a run with its values for a reader who does not trace it himself.
- A case with and without an input against a stated reason, on a reader's answer to why the input is needed.
- Recorded design rationale for later readers: its controlled studies could not be opened.

## Q7. References that open in place

No study tests references to code that open in place on engineers reading an explanation. Two experiments bear on it by transfer: definitions in place let 27 researchers answer 45.4 s faster with equal correctness, and trace links made 71 maintainers 24 % faster with 50 % more correct solutions. Link previews cut page views by 3–5 % and raised the distinct pages reached by about 21 %; hover content, keyboard access and devices without hover are settled by norms, and three documentation tools refuse an unresolved reference, a failure that is common in documentation.

- Fitzsimmons, Weal & Drieghe 2019 [124] (first-hand): eye tracking of undergraduates (30, then 32) reading sentences and web-like passages; coloured links did not disrupt reading, and a link on an uncommon word drew rereading of its sentence. The links could not be clicked, so the cost of deciding to follow one was not measured.
- Head et al. 2021 (Q3): definitions shown at each use, 45.4 s faster, correctness unchanged; 15 of 27 expected to use the term tooltips "always" and 9 "often". The definitions came from the same paper, and the features came in one bundle.
- Wikimedia Foundation 2018 [125] (first-hand): previews randomised by session on English and German Wikipedia, with about 53 million English sessions in the second test; page views per session fell by 5 % and 3 %, the distinct pages reached rose by 21 % on both, and about 0.01 % of sessions turned previews off. General readers and engagement only, no measure of comprehension.
- Ko et al. 2006 [126] (abstract): developers working on an unfamiliar program for 70 minutes spent on average 35 % of their time on "the mechanics of navigation within and between source files". Bragdon et al. 2010 [127] (abstract): fragments of code shown side by side cut understanding time and navigation against a common IDE in two controlled tasks; no figures in the abstract.
- Mäder & Egyed 2015 [128] (abstract): 71 subjects on real maintenance tasks of two projects; with traceability links between requirements and code they were on average 24 % faster and produced 50 % more correct solutions. Requirement-to-code links, with solutions sketched on paper.
- An EASE 2025 experiment [129] (abstract): 56 participants; code annotated with the algorithm it implements raised comprehension by a median of 6 points (about 23 %, p = 0.040) without changing completion time (p = 0.991). The mapping runs from code to an algorithm's name, the reverse of a method name on a line of pseudocode.
- Schroeder & Cenkci 2018 (Q4): related information placed beside its text, g = 0.63. Kalyuga et al. 2003 (Q4): the same aids can cost experienced readers.
- Tan et al. 2023 (Q4): 28.9 % of the most popular projects held an outdated reference to code, references "typically outdated for years" before a fix. Hata et al. 2019 [130] (abstract): "Almost 10% of the links included in source code comments are dead", over about 9.6 million links.
- Tool documentation (first-hand): Sphinx's `nitpicky` mode warns "about all references where the target cannot be found", and `-W` exits with status 1 on any warning [131]; rustdoc's `broken_intra_doc_links` lint "detects when an intra-doc link fails to be resolved" and can be denied into an error [132]; javadoc's DocLint group `reference` checks that references in `@see` and `{@link}` resolve, and `-Werror` turns warnings into errors [133].
- Links into an editor. VS Code documents `vscode://file/{full path to file}:line:column` [134] (first-hand), an absolute path on the reader's machine. JetBrains has no official documentation of `jetbrains://` [135] (first-hand; statements of its staff in the issue tracker, a practice report): staff gave a format handled by the Toolbox App and wrote that with two versions installed "it works unpredictably. A random IDE is selected". The HTML standard's hand-off to external software [34] lets a sandboxed frame refuse the hand-off, and without transient activation "the user agent should not invoke the external software package without prior user confirmation".
- Norms on hover (first-hand). WCAG 2.1 [136] SC 1.4.13 requires content shown on hover or focus to be dismissible, hoverable and persistent, and SC 2.1.1 all functionality to be operable through a keyboard. The HTML standard discourages relying on the `title` attribute, since many user agents do not expose it accessibly. Media Queries Level 4 [137] tells authors to "design layouts that do not depend on hovering to be fully usable", with `hover` and `any-hover` to detect pointers that cannot hover.

Against or mixed:

- Kalyuga et al. 2003: aids that help novices can harm experts; a reader of an engineering explanation is expert in the domain and a novice in the code explained.
- Head et al. 2021: speed and effort changed, correctness did not.
- Wikimedia 2018: fewer page views is a gain only if the preview carried what the reader needed, which stays unmeasured.
- Fitzsimmons et al. 2019: whether the rereading a link draws costs or helps comprehension was not measured.

Untested:

- References to code opened in place, read by engineers.
- A method name on each line of pseudocode.
- The effect of a build check on the rate of outdated references: the failure is measured, the check is not.
- Footnotes, endnotes and sidenotes compared in one reading study.
- Whether a viewer that shows the page in a sandboxed frame lets a link into the editor through.

## Q8. Controls of a page that is read, heard and commented on

Platform guidelines place the commands for a selection beside it, and one annotation tool opens its editor only from a button. An automatic copy of a selection goes against the desktop clipboard specification and is named a security concern by the Clipboard API. A play button per part rests on segmenting research, where segments the learner starts raised transfer (d = 0.45) and not retention; synchronised highlighting showed no comprehension gain in three experiments, all with impaired readers.

- Apple's guidelines for edit menus [138] (first-hand): "Depending on available space, the default menu position is above or below the insertion point or selection", revealed by interactions people already know, with short labels. Material Design 1 [139] (first-hand): actions appear in a menu "positioned immediately above, but not overlapping, the selection"; the quote check found no matching passage in the page it fetched. Hypothesis [140] (first-hand): selecting text pops up a small menu with Annotate and Highlight, and the editor opens on a click on Annotate. Native and touch platforms and one tool; none measures a window that opens unasked.
- WCAG 2.2's explanation of SC 3.2.2 [141] (first-hand) counts opening a window as a change of context, while the criterion governs changing a component's setting, which selecting text is not; it bears by analogy. Nielsen's third heuristic [142] (first-hand; its derivation from a factor analysis is relayed and was not checked): "Users often perform actions by mistake."
- The freedesktop.org clipboards specification [143] (first-hand): "selecting but with no explicit copy should only set PRIMARY, never CLIPBOARD", and it rejects the older model in which "selecting anything overwrites the clipboard". An X11 desktop convention; a web page cannot set PRIMARY. The W3C Clipboard API [144] (first-hand; a working draft) gates a script's write on transient activation or a permission, and names among its security concerns "an automated copy of something that was never selected". MDN [145] (first-hand): Firefox and Safari require transient activation and do not implement the clipboard-write permission.
- Rey et al. 2019 (Q4; the full text first-hand here): learner-paced segmentation raised transfer, d = 0.45 [0.24, 0.66] over 16 comparisons, and not retention, d = 0.19 [−0.04, 0.45], or cognitive load; system-paced segmentation raised retention (0.42) and transfer (0.35); learning time rose with segmentation (d = −0.92). Students with narrated animations, segments ended by a control to continue.
- Hasler, Kersten & Sweller 2007 [146] (first-hand): 72 boys aged 9–11 watched a short animation in four versions. The two learner-paced versions, 11 segments that stopped until the child pressed Play and free stop and play buttons, gave higher test performance with lower load than the two system-paced ones, on questions of high element interactivity. In the free-button group "11 out of 18 students did not use the 'stop' and 'play' buttons at all", and in the segmented group 10 children had to be told to press Play after the first stop.
- Pointer and keyboard norms (first-hand). The explanation of SC 2.5.2 [147] aims "to make it easier for users to prevent accidental or erroneous pointer input", though a toggle on the up-event that a second click undoes passes the criterion. The ARIA Authoring Practices [148] bind Space to a button "When the button has focus". YouTube's help [149] binds Space to play and pause "when the seek bar is selected" and uses `k` across the player. The explanation of SC 2.1.4 [150] covers shortcuts of printable characters only, so a page-wide Space handler falls outside it, and notes that in a screen reader's browse mode Space and Enter still reach the page.
- Abrams & Christ 2003 (Q5): motion onset captures attention even when it carries no information; a control that jumps to each spoken sentence makes an onset at every sentence. The explanation of SC 2.2.2 (Q5) treats moving content beside other content as a distraction, but only motion the user did not start.
- Keelor et al. 2020 [151] (first-hand): 10 children with reading difficulties and six passages of about 110 words; text-to-speech raised comprehension over reading without it (7.2 against 5.7 questions, p = 0.04), and the three text-to-speech conditions, without highlighting, with it, and with it at 225 words a minute, had identical means. Keelor et al. 2023 [152] (abstract): children aged 8–12 with dyslexia or language impairment; no difference between text-to-speech with and without highlighting. Brown et al. 2021 [153] (abstract): 25 adults with aphasia comprehended equally with sentence, word and no highlighting, and preferred highlighting.

Against or mixed:

- Hasler et al. 2007: free controls went unused, and a stop at the end of each segment left children waiting for a prompt; a stop needs an evident way to go on.
- Rey et al. 2019: segments the learner starts left retention where it was.
- A Space key that pauses the voice across the page departs from the convention of a focused control (the ARIA Authoring Practices, YouTube) and takes Space from scrolling while the voice runs; WCAG neither permits nor forbids it, and no measurement was found.
- The highlighting experiments found a preference for highlighting beside no gain in comprehension.

Untested:

- One player at the top of the page against a button at each part.
- The cost of a window that opens on every selection.
- How often a click on the text meant to select it or follow a link toggles the voice.
- A control that moves with the spoken sentence, on a page that is read.
- Synchronised highlighting with unimpaired adult readers.
- Whether a write to the clipboard on `mouseup` after a long drag still holds transient activation.

## Q9. Navigation of a long explanation page

Hidden navigation has a measured cost: on desktop sites it was used in 27 % of cases against 48 % and 50 % for navigation in view, and tasks took at least 39 % longer; one platform's guidelines say not to hide a sidebar by default. Overviews of a text raised memory for its topics and helped readers with low prior knowledge, with no gain for readers with high prior knowledge and none on comprehension in a video. A panel that pushes the text in a wide window and overlays it on a narrow one follows platform norms, and the browser's scroll anchoring does not hold the reading place when a panel narrows the column by width, margin or padding.

Hidden against visible:

- Pernice & Budiu 2016 [154] (first-hand): 179 participants in remote tests on six live websites, on desktop and phone. On desktop, hidden menus were used in 27 % of cases against 48 % for visible and 50 % for combined navigation, and tasks took at least 39 % longer; over both devices, discoverability fell by more than 20 % and rated difficulty rose by 21 % against visible navigation; on phones tasks were 15 % slower than with combined navigation. Global site navigation on consumer sites, with pages that differed between conditions; the authors note that hiding mostly affects content not reachable by an in-page link, and that desktop sites have no settled place for hidden navigation.
- Nielsen Norman Group's guide to tables of contents [155] (relay; a practice report whose testing is not described): "many users failed to notice the sticky table of contents" where a mobile layout collapsed it into a sticky bar, with no count given, and it recommends highlighting the current section. Its study of in-page links [156] (first-hand; qualitative, 11 participants): readers skipped the links while exploring and used them for a specific need; only 2 of 11 never engaged with them. Its article on anchors [157] (first-hand; a practice report): a list of in-page links that stays in place "should show users' current location".
- Apple's guidelines for sidebars [158] (first-hand): "Avoid hiding the sidebar by default to ensure that it remains discoverable"; succinct labels, and no more than two levels of hierarchy.

Push and overlay:

- Material Components for Android [159] (first-hand): a standard drawer for tablet and desktop that leaves the content usable, and a modal drawer with a scrim for mobile; "The navigation drawer is being deprecated in the Material 3 expressive update" in favour of an expanded navigation rail; the top app bar puts its navigation button at the leading edge. Android's window size classes [160] (first-hand): compact below 600dp, medium to 840dp, expanded from 840dp.
- The CSS Scroll Anchoring draft [161] (first-hand) keeps the view stable by tracking an anchor node, but suppresses the adjustment on any change of `width`, `margin`, `padding`, `position` or `transform` on the path from the anchor to the scroller, the usual way a pushing panel narrows a column. MDN's compatibility data [162] (first-hand): Safari has `overflow-anchor` from version 27. web.dev on layout shift [163] (first-hand): shifts within 500 ms of a user input are excluded from the metric, and readers "lose their place while reading if the text moves suddenly".
- WCAG 2.2 (Q2): content reflows at 320 CSS px without scrolling in two dimensions (SC 1.4.10), and a component with keyboard focus is not entirely hidden by author content (SC 2.4.11); SC 2.4.5 and 2.4.8 concern locating a page within a set of pages, not an item within one page.

Names and the current item:

- WCAG 2.2 SC 2.4.6: headings and labels describe topic or purpose. WAI-ARIA 1.2 [164] (first-hand): "Authors SHOULD only mark one element in a set of elements as current with aria-current." The Authoring Practices on landmarks [165] (first-hand): a second navigation landmark on a page needs its own label. HTML-AAM [166] (first-hand; a working draft): a `figcaption` takes no part in its figure's accessible name unless the author references it.

Overviews:

- Dee-Lucas & Larkin 1995 [167] (abstract): a structured overview and a plain content listing of an electronic text both "produced better memory for text topics and better breadth of recall" than continuous text; without study goals the listing led to a more fragmented knowledge structure. Cojean & Jamet 2021 [168] (abstract): 57 students; a table of contents added to an instructional video raised topic recall and not memorisation or comprehension, and learners hardly used the interactive one, navigating by the timeline.
- Amadieu, Tricot & Mariné 2009 [169] (first-hand): future biology teachers learning a virus cycle through a conceptual map; structure interacted with prior knowledge on free recall (F(1, 50) = 5.11, Cohen's f = 0.32): readers with low prior knowledge recalled more with a hierarchical map, readers with high prior knowledge showed no effect (F < 1). Two maps compared, not a map against none.
- Cuddihy & Spyridakis 2012 [170] (relay, through a law review's account): in a web article of about 8,500 words spread over eight web pages, a graphically distinct table of contents in the left-hand menu raised comprehension by about 10 %. Salmerón & García 2012 [171] (first-hand; the author's manuscript): sixth graders with low sustained attention scored higher on integration questions in a hypertext with a navigable overview.

Figures and other objects:

- Hubbard & Dunbar 2017 [172] (first-hand): a survey in biological sciences at one UK university; postgraduate researchers ranked figures and tables the most important section and undergraduates the abstract, and only 6 respondents advised starting with figures against 16 with the abstract. Shiely, Gallagher & Millar 2024 [173] (first-hand): of 139 science and health researchers, 98.6 % read the abstract first, and only 15 read the results second. Self-reports.
- Kim, Hoque, Kim & Agrawala 2018 [174] (first-hand): 14 adults matched sentences to table cells 26.4 % more accurately and spent 22.9 % less time with a reader that highlighted the cells a sentence refers to than with a baseline reader; each trial showed one sentence with its table, so the reader's side panel was not tested apart. Wang et al. 2021 [175] (first-hand; one blind participant, a practice report): reaching figures by navigating away cost the reader his place. Head et al. 2021 (Q3): researchers used a sidebar list of usages as a guide for non-linear reading.

A filter field:

- Katz & Byrne 2003 [176] (abstract): in an exploratory study, site search made locating products neither faster nor more accurate, and in a second experiment with novel e-commerce sites, browsing depended on both the breadth and the information scent of the menus; the abstract gives no figures. Bailly et al. 2014 [177] (first-hand): search time in a menu grew with its length over 8–16 items. Site search and menus, not a filter over a visible list.

Against or mixed:

- Cojean & Jamet 2021: a table of contents raised topic recall and not comprehension.
- Amadieu et al. 2009: no gain for readers with high prior knowledge.
- Shiely et al. 2024 and Hubbard & Dunbar 2017: researchers value figures but enter a paper by its abstract, so figures as the common entry are not shown.
- Material's own drawer is being deprecated, while its window classes stand.

Untested:

- A list of figures, tables and questions as navigation.
- Marking the item in view: guides recommend it and ARIA exposes it, but no controlled test was found.
- A filter field over an in-page list.
- Remembering whether the panel is open: neither a norm nor a study was found.
- The cost to reading of a pushing panel's reflow against an overlay.
- A short name written for the panel against the first sentence of a caption.

## Where the sources go against a practice

- **An automatic copy of a selection to the clipboard.** The desktop clipboard specification says a selection without an explicit copy never sets the clipboard [143], the Clipboard API names an automated copy of something never selected among its security concerns [144], and Firefox and Safari write only under transient activation [145]. The clause writes the clipboard only at the reader's copy button.
- **Navigation closed behind a button in a wide window.** Hidden desktop navigation was used in 27 % of cases against about half for navigation in view, with tasks at least 39 % slower [154]; one platform says not to hide a sidebar by default [158], and collapsed sticky tables of contents went unnoticed by many test users [155]. The clause opens the map beside the text in a wide window and keeps the button for a narrow one.
- **Removing every decoration from a chart.** Embellished charts were described as accurately as plain ones and recalled better after two to three weeks [90]; the measured harm of irrelevant material concerns interesting content off the goal [88]. The clause removes from a mechanism's figure only labels no sentence uses, which no source tests.
- **A fixed cap on the length of a list.** Broad voice menus beat deep ones, against a guideline of five items or fewer [39], and the limit of about four chunks holds only where items cannot be grouped or reread [40]. The clause sets a floor of three items and no cap.
- **Synchronised highlighting as an aid to comprehension.** Three experiments found no comprehension gain from highlighting the spoken text, and one found a preference for it [151] [152] [153]; all three tested impaired readers. The lighting of the spoken sentence rests on a hypothesis of its own, and these three tests stand beside it as evidence against it under other conditions.
- **A worked case for a reader who already knows the mechanism.** Assistance hurt learners with high prior knowledge, d = −0.428 over 60 studies [110], and worked examples became redundant with experience [109]. The clause gives one worked case on the ground that a reader meets an unfamiliar mechanism as a novice in it; for a reader who knows the mechanism, the sources go against the case.
- **Restated content for a knowledgeable reader.** As expertise grew, text integrated with a diagram turned into a cost [62] [63], notes that helped novices reversed for experts [87], nonessential explanation harmed even when integrated [58], and text identical to its narration impaired learning [65]. Skilled readers with high knowledge gained from a cohesive text [48], so the evidence reaches restated content, not the words that join one sentence to the next.
- **The place of self-test questions.** Tests after each segment of a video lecture raised the final score to 90 % against 68 % without tests [79], a replication with 195 students found no effect on learning against restudy [80], and the effect of adjunct questions did not depend on their distance from the text [81]. Neither lecture study used a page read at the reader's own pace, so a question at the close of each part rests on a contested placement.

## Rules and data

Each clause of `handing-over-to-readers` in the table is in force as the decision of the repository's owner, and the claim behind it waits as a hypothesis for a test of its own; PN1 and PN2 are norms a standard prescribes. In the last column, `transfer` names a source with the same mechanism under other readers or material, `norm` a standard or guide that prescribes the clause, and `practice` a part with neither a test nor a norm.

| Clause | Ground | Research beside it | Fit and caveat |
|--|--|--|--|
| P1 · The terms are collected before the first sentence as a list of the readers' own words, and a script holds the page to the list | `decision, hypothesis` | ASD-STE100 2025 [1]: the approved term, no second noun for one item; Microsoft [2] and Google [3]: one term per concept; Hofmeister 2017 [6]: whole-word identifiers, 19 % more defects found per minute; SI Brochure 2019 [10]: the prefix on the unit; Vale [8]: barred variants flagged | `norm` for one approved term and for unit notation; `transfer` for the reader's benefit, from developers reading names in code; `practice` for a list made before the first sentence and for the script. Against: Lawrie 2006 [5], full words no better than abbreviations; Dasgupta 2017 [12], novices faster in a localised environment |
| P2 · A counted enumeration stands as a list, and the gist of a part may stand in one marked block | `decision, hypothesis` | Jansen 2014 [14]: item recall higher in 3 of 5 studies, surrounding text lower in 2; Alpizar 2020 [24]: signalling d = 0.38; Gier 2009 [25]: wrong marks impaired comprehension, 180 students; Mayer 2002 [32] (relay): a spoken outline, transfer 0.74 | `transfer` from lay readers of functional text and from students; `norm` for a lead-in, parallel items and a warning sign kept for a risk (Google [27], OSHA [28]). Against: Richter 2018 [37], signals harmed learners with high prior knowledge; Yeari 2017 [38], proficient readers unaffected. No test of an item that opens with its name or of a synthesised voice |
| P3 · A term returns with what it is, and a numbered thing is pointed at after it is shown | `decision, hypothesis` | O'Brien 1990 [46]: distant and bare antecedents reinstated more slowly; Head 2021 [41]: definitions at each use, 45.4 s faster, correctness unchanged, 27 readers; O'Reilly 2007 [48]: skilled readers with high knowledge gained from cohesion | `transfer` from readers of experimental passages and researchers reading a paper; `norm` for a definition at first use (WCAG 3.1.3 [52], Google [53]). A definition said again at a return and the order of numbers before references are untested. Against: McNamara 1996 [4], readers with high knowledge gained from a minimally coherent text; two pilot readers did not want a definition repeated where it stood in view [41] |
| P4 · The terms of a compound condition are joined by written connectives | `decision, hypothesis` | Holland 1981 [103] (relay of an earlier experiment): an "or" carried by commas harder to follow than a repeated "or"; Berry 2003 [104]: layout or enumeration shows precedence; NASA [105]: "and/or" ambiguous | `norm` from handbooks of requirement writing; `transfer` from readers of conditional instructions, both experiments known only by relay. Against: Holland 1981, algorithm formats lost on a first exposure; Berry 2003, a comma that groups written connectives is no harm |
| P5 · An exchange and a rule in words get one worked case, a derivation its labelled steps, an outcome its step, and each input its case | `decision, hypothesis` | Barbieri 2023 [108]: g = 0.48; Tetzlaff 2025 [110]: d = 0.505 for low against −0.428 for high prior knowledge; Catrambone 1998 [114]: subgoal labels across 4 experiments; Gick 1983 [117]: 45 % against 21 % transfer from two analogs over one; Miller 2019 [121]: people ask why P instead of Q | `transfer` from students of mathematics and programming; `practice` for a derivation in the order of its figure and for the case without an input. Against: the reversal for a reader who knows the mechanism; McNamara 1996 for stated steps with knowledgeable readers; one case underdetermines transfer (Atkinson 2000 [118]: at least two); Meyes 2019 [123]: a removal need not fail |
| P6 · A picture stands at the first use of what it shows, a label on its thing, one numbering across figure, pseudocode and sentences, and a path as a still line | `decision, hypothesis` | Schroeder 2018 [61]: g = 0.63 over 58 comparisons; Berney 2016 [94]: abstract representations g = 0.006 (k = 26); Kim 2021 [106]: a caption's message taken only when the chart stresses it; Ozcelik 2009 [100]: colour coding eased finding correspondences | `transfer` from learners with text and pictures and crowd workers with line charts; `norm` for control of motion (WCAG 2.2.2 [30]) and for a reference by number (HTML [34]). Against: Oksa 2010 [87] and Richter 2018, integration aids harmed expert readers; Bateman 2010 [90], embellished charts as accurate and better recalled. Labels on arrows and one numbering untested |
| P7 · A later part holds what can be understood apart, what a line needs stands at the line, a fact stands in one place, and the page says nothing about how to read it | `decision, hypothesis` | Chandler 1991 [58]: integration helped only for material unintelligible apart; Kalyuga 1998 [62]: with expertise the best design removed the text; Ginns (ED491708) [73]: cut verbiage, d = 0.89 over 3 studies; Tan 2023 [68]: 28.9 % of top projects with an outdated reference to code | `transfer` from trainees, apprentices and learners of software manuals; drift measured between documentation and code, not within one document. Against: O'Reilly 2007, skilled experts gain from cohesion (the clause keeps joining words); GitLab [71] permits duplication; Mayer 2001 [84], parts before the whole better on transfer. Reading routes and a stated time untested on comprehension |
| P8 · A claim about code opens its code where it stands, each line of the pseudocode names its method, and the builder resolves every reference | `decision, hypothesis` | Head 2021: 45.4 s faster, equal correctness; Mäder 2015 [128]: trace links, 24 % faster and 50 % more correct, 71 subjects; Wikimedia 2018 [125]: previews, −3 to −5 % page views and +21 % distinct pages; Tan 2023: 28.9 %; Sphinx [131], rustdoc [132], javadoc [133]: an unresolved reference refused | `transfer` from researchers reading a paper and maintainers with requirement links; `norm` from tool documentation for the build check, whose own effect is untested. A method name on a pseudocode line untested (the EASE 2025 experiment [129] tested the reverse mapping, +6 points median). Against: Kalyuga 2003 [64], aids cost readers who hold the material. A link into the editor needs an absolute local path [134], and a sandboxed frame may refuse it [34] |
| P9 · The voice by part, the pause a button and the Space key, the tools of a selection | `decision, hypothesis` | Rey 2019 [78]: learner-paced segments, transfer d = 0.45, retention 0.19 n.s.; Hasler 2007 [146]: free stop and play buttons unused by 11 of 18 children, 10 needed a prompt after a stop; Apple [138], Material 1 [139], Hypothesis [140]: commands beside the selection | `transfer` from students and children with narrated animations; `norm` from platform guidelines for the selection. No study of one player against a button per part, nor of a window opened unasked. Against: the ARIA Authoring Practices [148] and YouTube [149] bind Space to a focused control, and a page-wide Space while the voice runs takes Space from scrolling; WCAG 2.1.4 does not cover Space [150] |
| P10 · A map of the page lists every part with its figures and stands open beside the text in a wide window | `decision, hypothesis` | Pernice 2016 [154]: hidden navigation used in 27 % against 48–50 %, tasks at least 39 % slower; Apple [158]: a sidebar not hidden by default; Amadieu 2009 [169]: a hierarchical overview helped readers with low knowledge, F < 1 for high; Cuddihy 2012 [170] (relay): +10 % comprehension | `transfer` from site navigation on consumer sites and students with hypertexts; `norm` for push and overlay by width (Material [159], Android [160], WCAG 1.4.10) and for `aria-current` [164]. Against: Cojean 2021 [168], topic recall without comprehension; Shiely 2024 [173], 98.6 % enter by the abstract; scroll anchoring suppressed by changes of width, margin or padding [161]. A filter and a remembered state untested |
| P11 · The table of questions after the first part with each question and its place, a part per named questions, reference tables without voice | `decision, hypothesis` | Head 2021: the priming glossary the least-used feature, 6 of 27; Yanagisawa 2020 [51]: glossaries among the least effective gloss types; Ginns (ED491708): d = 0.89; Galesic 2009 [76]: a longer stated length, fewer starts; Google [70]: link to a procedure, do not repeat it | `transfer` from researchers and second-language learners for the glossary, from manual users for cut text; `practice` for the table of questions. Against: GitLab permits duplication. No test of a table of questions, of routes by time or of a stated reading time on comprehension |
| PN1 · Content shown on hover or focus opens on focus as on hover, stays under the pointer and closes on Escape | `norm`: WCAG 2.2, SC 1.4.13 Content on Hover or Focus, with its document Understanding SC 1.4.13 (W3C) | WCAG 2.2 and 2.1 [136]: dismissible, hoverable, persistent; Understanding SC 1.4.13 [178]: content that hover brings up also opens on keyboard focus, and the Esc key as a way to dismiss it; SC 2.1.1: operable through a keyboard; HTML [34]: relying on `title` discouraged; Media Queries 4 [137]: layouts that do not depend on hover | `norm`. The criterion asks for a way to dismiss the content without moving pointer or focus and names no key; its Understanding document names the Esc key and the opening on keyboard focus, which the clause follows; whether a preview changes how many references a reader opens is untested |
| PN2 · The clipboard is written only at a command of the reader | `norm`: freedesktop.org Clipboards specification | freedesktop.org [143]: a selection without an explicit copy never sets CLIPBOARD; Clipboard API [144]: an automated copy of something never selected is a security concern; MDN [145]: Firefox and Safari write only under transient activation | `norm` written for X11 desktops; a web page cannot set PRIMARY, so the norm reaches a page as the expectation of a desktop reader, and the browser norms gate the write |

## Open questions

- No source tests any of the nine practices on engineers reading a technical explanation.
- Whether a list of terms made before the first sentence leaves fewer variants than terms aligned in an edit after the draft.
- Whether a term list enforced by a linter, apart from a bundle of controlled-language rules, changes the quality of a text.
- Whether engineers understand an English trade term inside German or Russian text better than a translated or native word.
- Whether an item that opens with its name, or a numbered list against a bulleted one, changes recall.
- Whether a synthesised voice carries a spoken count and ordinal words as a human narrator did.
- How much marked text a page holds before marking loses its effect.
- Whether a definition said again at a distant return helps a reader or slows an expert.
- Whether a term used before its definition costs a reader of expository text.
- Whether a label on an arrow beats one in a legend or a caption on a mechanism diagram.
- Whether one numbering across figure, pseudocode and prose speeds the mapping between them.
- Whether a looping trace distracts from reading more than a still line.
- Whether a worked case helps an experienced engineer who reads an unfamiliar mechanism, and whether one case is enough.
- Whether a derivation in the order of its figure's blocks beats a chained line of equalities.
- Whether a case without an input explains why the input is needed better than a stated reason.
- Whether a fact kept in two places of one generated page drifts.
- Whether reading routes or a stated reading time change comprehension.
- Whether questions after each part beat one section at the end on a page read at the reader's pace.
- Whether a pseudocode line labelled with its method lets a reader find the code faster.
- Whether a build check lowers the rate of outdated references to code.
- Whether one player at the top and a button at each part differ in what readers understand.
- Whether a window that opens on every selection costs readers more than a button beside it.
- How often a click on the text toggles the voice by accident.
- Whether synchronised highlighting helps unimpaired adult readers.
- Whether readers of a technical page navigate by a list of its figures.
- Whether marking the item in view, a filter field or a remembered open state helps readers of an in-page panel.
- Whether a pushing panel's reflow costs a reader his place more than an overlay does.

## Sources

Each line gives the authors, the year, the title, the venue, a URL or DOI and the reading in brackets. A source cited under several questions stands under the first; the later groups name it.

**Q1. Terms**

1. ASD (AeroSpace and Defence Industries Association of Europe), 2025. ASD-STE100 Simplified Technical English, Issue 9, Part 1, rules 1.8 and 1.11. https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf [first-hand]
2. Microsoft. Microsoft Writing Style Guide, "Use simple words, concise sentences". https://learn.microsoft.com/en-us/style-guide/word-choice/use-simple-words-concise-sentences [first-hand]
3. Google. Google developer documentation style guide, "Write for a global audience", "Code in text" and "Units of measurement". https://developers.google.com/style/translation, https://developers.google.com/style/code-in-text, https://developers.google.com/style/units-of-measure [first-hand]
4. McNamara, Kintsch, Songer & Kintsch, 1996. Are good texts always better? Interactions of text coherence, background knowledge, and levels of understanding in learning from text. Cognition and Instruction 14(1), 1–43. https://asu.elsevierpure.com/en/publications/are-good-texts-always-better-interactions-of-text-coherence-backg/, doi:10.1207/s1532690xci1401_1 [abstract; in Q6 a relay, the summary ERIC wrote in place of the authors' abstract, https://eric.ed.gov/?id=EJ520492]
5. Lawrie, Morrell, Feild & Binkley, 2006. What's in a Name? A Study of Identifiers. ICPC 2006, 3–12. https://www.cs.loyola.edu/~binkley/papers/icpc06-name.pdf, doi:10.1109/ICPC.2006.51 [first-hand]
6. Hofmeister, Siegmund & Holt, 2017. Shorter Identifier Names Take Longer to Comprehend. SANER 2017, 217–227. https://brains-on-code.github.io/shorter-identifier-names.pdf [first-hand]
7. Fakhoury, Roy, Ma, Arnaoudova & Adesope. Measuring the Impact of Lexical and Structural Inconsistencies on Developers' Cognitive Load during Bug Localization. Empirical Software Engineering, author manuscript received 2018. https://par.nsf.gov/servlets/purl/10135165 [abstract]
8. Vale documentation, "Vocabularies" and "substitution". https://docs.vale.sh/keys/vocabularies.md, https://docs.vale.sh/checks/substitution.md [first-hand]
9. Doherty, 2012. Investigating the Effects of Controlled Language on the Reading and Comprehension of Machine Translated Texts: A Mixed-Methods Approach. PhD thesis, Dublin City University. https://aclanthology.org/www.mt-archive.info/10/Doherty-2012.pdf [relay]
10. BIPM, 2019. The International System of Units (SI Brochure), 9th edition, version 4.01, chapter 3 and § 5.4.7. https://www.bipm.org/documents/20126/41483022/SI-Brochure-9-EN.pdf, doi:10.59161/AUEZ1291 [first-hand]
11. Guo, 2018. Non-Native English Speakers Learning Computer Programming: Barriers, Desires, and Design Opportunities. CHI 2018. https://pg.ucsd.edu/publications/non-native-english-speakers-learning-programming_CHI-2018.pdf [first-hand]
12. Dasgupta & Hill, 2017. Learning to Code in Localized Programming Languages. L@S 2017, 33–39. https://mako.cc/academic/dasgupta_hill-learning_code_localization-L@S2017.pdf [abstract]
13. Özkan, Babur & van den Brand, 2025. Domain-Driven Design in Software Development: A Systematic Literature Review on Implementation, Challenges, and Effectiveness. Journal of Systems and Software. https://arxiv.org/abs/2310.01905 (the preprint), doi:10.1016/j.jss.2025.112537 [relay]

**Q2. Lists and a marked statement**

14. Jansen, 2014. How bulleted lists and enumerations in formatted paragraphs affect recall and evaluation of functional text. Information Design Journal 21(2), 146–162. https://research-portal.uu.nl/en/publications/how-bulleted-lists-and-enumerations-in-formatted-paragraphs-affec/, doi:10.1075/idj.21.2.06jan [abstract]
15. Karreman & Loorbach, 2007. Paragraphs or Lists? The Effects of Text Structure on Web Sites. IEEE International Professional Communication Conference. https://ris.utwente.nl/ws/files/5538163/Karreman07paragraphs.pdf, doi:10.1109/ipcc.2007.4464091 [first-hand]
16. Morrow, Leirer, Andrassy, Hier & Menard, 1998. The Influence of List Format and Category Headers on Age Differences in Understanding Medication Instructions. Experimental Aging Research. https://api.openalex.org/works/doi:10.1080/036107398244238, doi:10.1080/036107398244238 [abstract]
17. Morkes & Nielsen, 1997. Concise, SCANNABLE, and Objective: How to Write for the Web. Nielsen Norman Group. https://www.nngroup.com/articles/concise-scannable-and-objective-how-to-write-for-the-web/ [first-hand]
18. Lyngo Lab, undated. Can a Bulleted List Aid Recall of Key Details? Self-published. https://www.lyngolab.com/bulleted-lists-memory.html [first-hand]
19. Garner & Alley, 2013. How the design of presentation slides affects audience comprehension: A case for the assertion–evidence approach. International Journal of Engineering Education 29(6). https://writing.engr.psu.edu/ae_comprehension.pdf [first-hand]
20. Lorch, 1989. Text-signaling devices and their effects on reading and memory processes. Educational Psychology Review 1(3), 209–234. https://scholars.uky.edu/en/publications/text-signaling-devices-and-their-effects-on-reading-and-memory-pr/, doi:10.1007/BF01320135 [abstract]
21. Lorch, Lorch & Klusewitz, 1995. Effects of Typographical Cues on Reading and Recall of Text. Contemporary Educational Psychology. https://eric.ed.gov/?id=EJ502398 [abstract]
22. Lorch & Chen, 1986. Effects of Number Signals on Reading and Recall. Journal of Educational Psychology. https://eric.ed.gov/?id=EJ339569 [abstract]
23. Lorch, Lorch & Inman, 1993. Effects of signaling topic structure on text recall. Journal of Educational Psychology 85(2), 281. https://eric.ed.gov/?id=EJ466316, doi:10.1037/0022-0663.85.2.281 [abstract]
24. Alpizar, Adesope & Wong, 2020. A Meta-Analysis of Signaling Principle in Multimedia Learning Environments. Educational Technology Research and Development. https://eric.ed.gov/?id=EJ1269127, doi:10.1007/s11423-020-09748-7 [abstract]
25. Gier, Kreiner & Natz-Gonzalez, 2009. Harmful effects of preexisting inappropriate highlighting on reading comprehension and metacognitive accuracy. Journal of General Psychology 136(3). https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=19650523&rettype=abstract&retmode=text, doi:10.3200/GENP.136.3.287-302 [abstract]
26. Silvers & Kreiner, 1997. The Effects of Pre-Existing Inappropriate Highlighting on Reading Comprehension. Reading Research and Instruction. https://eric.ed.gov/?id=EJ547175 [abstract]
27. Google. Google developer documentation style guide, "Notes, cautions, warnings, and other notices" and "Lists". https://developers.google.com/style/notices, https://developers.google.com/style/lists [first-hand]
28. OSHA. 29 CFR 1910.145, Specifications for accident prevention signs and tags, (c)(2)(i). https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.145 [first-hand]
29. Hunt, 1995. The subtlety of distinctiveness: What von Restorff really did. Psychonomic Bulletin & Review 2(1), 105–112. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=24203592&rettype=abstract&retmode=text, doi:10.3758/BF03214414 [abstract]
30. W3C, 2023. Web Content Accessibility Guidelines (WCAG) 2.2, Recommendation: SC 1.3.1, 1.4.1, 1.4.10, 1.4.13, 2.2.2, 2.4.5, 2.4.6, 2.4.8 and 2.4.11. https://www.w3.org/TR/WCAG22/ [first-hand]
31. Titsworth & Kiewra, 2004. Spoken Organizational Lecture Cues and Student Notetaking as Facilitators of Student Learning. Contemporary Educational Psychology. https://eric.ed.gov/?id=EJ735631 [abstract]
32. Mayer, 2002. Cognitive Theory and the Design of Multimedia Instruction: An Example of the Two-Way Street Between Cognition and Instruction. New Directions for Teaching and Learning 89, 68–69, reporting Mautone & Mayer 2001, Experiment 3. https://nschwartz.yourweb.csuchico.edu/Mayer%20Multimedia%20Learning%202002.pdf [relay]
33. W3C, 2010. Speech Synthesis Markup Language (SSML) Version 1.1, Recommendation, § 3.2.2 and § 3.2.3. https://www.w3.org/TR/speech-synthesis11/ [first-hand]
34. WHATWG. HTML Living Standard: § 4.4.5 `ol`, § 4.4.6 `ul`, § 4.4.9 `dl`, § 4.5.3 `strong`, § 4.4.12 `figure`, § 3.2.6.1 the `title` attribute, and the hand-off to external software. https://html.spec.whatwg.org/multipage/ [first-hand]
35. Plain Language Action and Information Network. Federal Plain Language Guidelines, "Use lists". https://raw.githubusercontent.com/GSA/plainlanguage.gov/main/_pages/guidelines/organize/use-lists.md [first-hand]
36. Frazier, Munn & Clifton, 2000. Processing coordinate structures. Journal of Psycholinguistic Research 29(4), 343–370. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=10953824&rettype=abstract&retmode=text, doi:10.1023/a:1005156427600 [abstract]
37. Richter, Scheiter & Eitel, 2018. Signaling Text-Picture Relations in Multimedia Learning: The Influence of Prior Knowledge. Journal of Educational Psychology. https://eric.ed.gov/?id=EJ1178409 [abstract]
38. Yeari, Oudega & van den Broek, 2017. The Effect of Highlighting on Processing and Memory of Central and Peripheral Text Information: Evidence from Eye Movements. Journal of Research in Reading. https://eric.ed.gov/?id=EJ1155946 [abstract]
39. Commarford, Lewis, Smither & Gentzler, 2008. A comparison of broad versus deep auditory menu structures. Human Factors 50(1), 77–89. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=18354973&rettype=abstract&retmode=text, doi:10.1518/001872008X250665 [abstract]
40. Cowan, 2001. The magical number 4 in short-term memory: a reconsideration of mental storage capacity. Behavioral and Brain Sciences 24(1). doi:10.1017/s0140525x01003922 [abstract]

**Q3. Where a definition stands**

41. Head, Lo, Kang, Fok, Skjonsberg, Weld & Hearst, 2021. Augmenting Scientific Papers with Just-in-Time, Position-Sensitive Definitions of Terms and Symbols. CHI 2021. https://arxiv.org/abs/2009.14237 [first-hand]
42. Mayer, Mathias & Wetzell, 2002. Fostering understanding of multimedia messages through pre-training: Evidence for a two-stage theory of mental model construction. Journal of Experimental Psychology: Applied 8(3), 147–154. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=12240927&rettype=abstract&retmode=text [abstract]
43. Mayer & Moreno, 2003. Nine ways to reduce cognitive load in multimedia learning. Educational Psychologist 38(1), 43–52. https://www.uky.edu/~gmswan3/544/9_ways_to_reduce_CL.pdf [relay: the authors' review of their own experiments]
44. Kester, Kirschner & van Merriënboer, 2004. Timing of information presentation in learning statistics. Instructional Science 32, 233–252. https://dspace.library.uu.nl/server/api/core/bitstreams/773543c2-c1b6-4e43-8dbc-ab3ae8bec8df/content, doi:10.1023/B:TRUC.0000024191.27560.e3 [first-hand]
45. Kester, Kirschner & van Merriënboer, 2005. The management of cognitive load during complex cognitive skill acquisition by means of computer-simulated problem solving. British Journal of Educational Psychology 75(1), 71–85. https://pubmed.ncbi.nlm.nih.gov/15831182/ [abstract]
46. O'Brien, Plewes & Albrecht, 1990. Antecedent retrieval processes. Journal of Experimental Psychology: Learning, Memory, and Cognition 16(2), 241–249. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=2137863&rettype=abstract&retmode=text [abstract]
47. O'Brien, Duffy & Myers, 1986. Anaphoric inference during reading. Journal of Experimental Psychology: Learning, Memory, and Cognition 12(3), 346–352. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=2942624&rettype=abstract&retmode=text [abstract]
48. O'Reilly & McNamara, 2007. Reversing the reverse cohesion effect: Good texts can be better for strategic, high-knowledge readers. Discourse Processes 43(2), 121–152. https://eric.ed.gov/?id=EJ772185, doi:10.1080/01638530709336895 [abstract]
49. van Gompel & Liversedge, 2003. The influence of morphological information on cataphoric pronoun assignment. Journal of Experimental Psychology: Learning, Memory, and Cognition 29(1), 128–139. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=12549589&rettype=abstract&retmode=text [abstract]
50. Gernsbacher & Shroyer, 1989. The cataphoric use of the indefinite this in spoken narratives. Memory & Cognition 17(5), 536–540. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=2796738&rettype=abstract&retmode=text [abstract]
51. Yanagisawa, Webb & Uchihara, 2020. How Do Different Forms of Glossing Contribute to L2 Vocabulary Learning from Reading? A Meta-Regression Analysis. Studies in Second Language Acquisition 42(2), 411–438. doi:10.1017/S0272263119000688 [abstract]
52. W3C. Understanding WCAG 2.2, Success Criterion 3.1.3 Unusual Words. https://www.w3.org/WAI/WCAG22/Understanding/unusual-words.html [first-hand]
53. Google. Google developer documentation style guide, "Jargon" and "Abbreviations". https://developers.google.com/style/jargon, https://developers.google.com/style/abbreviations [first-hand]
54. Kalyuga, Chandler & Sweller, 2004. When redundant on-screen text in multimedia technical instruction can interfere with learning. Human Factors 46(3), 567–581. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=15573552&rettype=abstract&retmode=text [abstract]

Also cited here: [30], [4].

**Q4. Structure**

55. Luiten, Ames & Ackerson, 1980. A Meta-analysis of the Effects of Advance Organizers on Learning and Retention. American Educational Research Journal 17(2), 211–218. https://eric.ed.gov/?id=EJ233231, doi:10.3102/00028312017002211 [abstract]
56. Luiten, Ames & Ackerson, 1979. The Advance Organizer: A Review of Research Using Glass's Technique of Meta-Analysis. Conference paper, ERIC ED171803. https://files.eric.ed.gov/fulltext/ED171803.pdf [first-hand, an OCR scan]
57. Stone, 1982. A Meta-Analysis of Advance-Organizer Studies. ERIC ED220476. https://eric.ed.gov/?id=ED220476 [relay]
58. Chandler & Sweller, 1991. Cognitive Load Theory and the Format of Instruction. Cognition and Instruction 8(4), 293–332. https://api.openalex.org/works/doi:10.1207/s1532690xci0804_2, doi:10.1207/s1532690xci0804_2 [abstract]
59. Chandler & Sweller, 1992. The split-attention effect as a factor in the design of instruction. British Journal of Educational Psychology 62, 233–246. https://api.openalex.org/works/doi:10.1111/j.2044-8279.1992.tb01017.x, doi:10.1111/j.2044-8279.1992.tb01017.x [abstract]
60. Ginns, 2006. Integrating information: A meta-analysis of the spatial contiguity and temporal contiguity effects. Learning and Instruction 16(6), 511–525. https://eric.ed.gov/?id=EJ747512, doi:10.1016/j.learninstruc.2006.10.001 [abstract]
61. Schroeder & Cenkci, 2018. Spatial Contiguity and Spatial Split-Attention Effects in Multimedia Learning Environments: A Meta-Analysis. Educational Psychology Review 30, 679–701. https://eric.ed.gov/?id=EJ1186641, doi:10.1007/s10648-018-9435-9 [abstract]
62. Kalyuga, Chandler & Sweller, 1998. Levels of Expertise and Instructional Design. Human Factors 40(1). https://api.openalex.org/works/doi:10.1518/001872098779480587, doi:10.1518/001872098779480587 [abstract]
63. Kalyuga, Chandler & Sweller, 2000. Incorporating learner experience into the design of multimedia instruction. Journal of Educational Psychology 92(1), 126. https://api.openalex.org/works/doi:10.1037/0022-0663.92.1.126, doi:10.1037/0022-0663.92.1.126 [abstract]
64. Kalyuga, Ayres, Chandler & Sweller, 2003. The Expertise Reversal Effect. Educational Psychologist 38(1), 23–31. https://api.openalex.org/works/doi:10.1207/S15326985EP3801_4, https://mrbartonmaths.com/resourcesnew/8.%20Research/Explicit%20Instruction/The%20Expertise%20Reversal%20Effect.pdf, doi:10.1207/S15326985EP3801_4 [abstract in Q4 and Q7, from its OpenAlex record; first-hand in Q6, from the PDF]
65. Yue, Bjork & Bjork, 2013. Reducing Verbal Redundancy in Multimedia Learning: An Undesired Desirable Difficulty? Journal of Educational Psychology. https://eric.ed.gov/?id=EJ1007931 [abstract]
66. Cepeda, Pashler, Vul, Wixted & Rohrer, 2006. Distributed practice in verbal recall tasks: A review and quantitative synthesis. Psychological Bulletin 132(3), 354. https://api.openalex.org/works/doi:10.1037/0033-2909.132.3.354, doi:10.1037/0033-2909.132.3.354 [abstract]
67. Rawson & Kintsch, 2005. Rereading Effects Depend on Time of Test. Journal of Educational Psychology 97(1), 70. https://api.openalex.org/works/doi:10.1037/0022-0663.97.1.70, doi:10.1037/0022-0663.97.1.70 [abstract]
68. Tan, Wagner & Treude, 2023. Detecting outdated code element references in software repository documentation. Empirical Software Engineering. doi:10.1007/s10664-023-10397-6, arXiv:2212.01479 [first-hand]
69. Wen, Nagy, Bavota & Lanza, 2019. A Large-Scale Empirical Study on Code-Comment Inconsistencies. ICPC 2019. https://api.openalex.org/works/doi:10.1109/ICPC.2019.00019, doi:10.1109/ICPC.2019.00019 [abstract]
70. Google. Google developer documentation style guide, "Procedures". https://developers.google.com/style/procedures [first-hand]
71. GitLab. Documentation Style Guide, "Documentation is the single source of truth (SSoT)". https://docs.gitlab.com/development/documentation/styleguide/ [first-hand]
72. OASIS. DITA Version 1.3, Part 3, § 2.4.2 Content reference (conref). https://docs.oasis-open.org/dita/dita/v1.3/os/part3-all-inclusive/archSpec/base/conref.html [first-hand]
73. Ginns, Hollender & Reimann, year not recorded by the unit. Meta-Analysis of the Minimalist Training Model. ERIC ED491708. https://files.eric.ed.gov/fulltext/ED491708.pdf [first-hand]
74. Lazonder & van der Meij, 1993. The minimal manual: is less really more? International Journal of Man-Machine Studies 39(5), 729–752. https://research.utwente.nl/en/publications/f811580e-953a-4312-a1ee-9916b3f98e05 [abstract]
75. Carroll, Smith-Kerker, Ford & Mazur-Rimetz, 1987. The Minimal Manual. Human-Computer Interaction 3(2). https://api.openalex.org/works/doi:10.1207/s15327051hci0302_2, doi:10.1207/s15327051hci0302_2 [abstract]
76. Galesic & Bosnjak, 2009. Effects of Questionnaire Length on Participation and Indicators of Response Quality in a Web Survey. Public Opinion Quarterly. https://api.openalex.org/works/doi:10.1093/poq/nfp031, doi:10.1093/poq/nfp031 [abstract]
77. Villar, Callegaro & Yang, 2013. Where Am I? A Meta-Analysis of Experiments on the Effects of Progress Indicators for Web Surveys. Social Science Computer Review. https://api.openalex.org/works/doi:10.1177/0894439313497468, doi:10.1177/0894439313497468 [abstract]
78. Rey, Beege, Nebel, Wirzberger, Schmitt & Schneider, 2019. A Meta-analysis of the Segmenting Effect. Educational Psychology Review 31(2), 389–419. https://eric.ed.gov/?id=EJ1217373, https://maria-wirzberger.de/wp-content/uploads/2019/01/Rey2019_Article_AMeta-analysisOfTheSegmentingE.pdf, doi:10.1007/s10648-018-9456-4 [abstract in Q4, from its ERIC record; first-hand, the authors' copy, in Q8]
79. Szpunar, Khan & Schacter, 2013. Interpolated memory tests reduce mind wandering and improve learning of online lectures. PNAS 110(16). https://pmc.ncbi.nlm.nih.gov/articles/PMC3631699/ [first-hand]
80. Welhaf, Phillips, Smeekens, Miyake & Kane, 2022. Interpolated Testing and Content Pretesting as Interventions to Reduce Task-Unrelated Thoughts during a Video Lecture. Cognitive Research: Principles and Implications. https://eric.ed.gov/?id=EJ1331359 [abstract]
81. Hamaker, 1986. The Effects of Adjunct Questions on Prose Learning. Review of Educational Research 56(2), 212–242. doi:10.3102/00346543056002212 [abstract]
82. Roediger & Karpicke, 2006. Test-Enhanced Learning. Psychological Science 17(3). doi:10.1111/j.1467-9280.2006.01693.x [abstract]
83. Adesope, Trevisan & Sundararajan, 2017. Rethinking the Use of Tests: A Meta-Analysis of Practice Testing. Review of Educational Research. https://eric.ed.gov/?id=EJ1141817 [abstract]
84. Mayer & Chandler, 2001. When learning is just a click away: Does simple user interaction foster deeper understanding of multimedia messages? Journal of Educational Psychology 93(2), 390. https://api.openalex.org/works/doi:10.1037/0022-0663.93.2.390, doi:10.1037/0022-0663.93.2.390 [abstract]

Also cited here: [23], [4], [48].

**Q5. Figures**

85. Porte, Boucheix, Argon & Rougeot, 2026. Continuous Temporal Contiguity Narration-Animation for Learning in Virtual Reality. Journal of Computer Assisted Learning. https://eric.ed.gov/?id=EJ1500453 [abstract]
86. Liu, Lin & Paas, 2022. A New Application of the Temporal Contiguity Effect in Designing Narrated Slideshows. Educational Technology Research and Development. https://eric.ed.gov/?id=EJ1329871 [abstract]
87. Oksa, Kalyuga & Chandler, 2010. Expertise Reversal Effect in Using Explanatory Notes for Readers of Shakespearean Text. Instructional Science. https://eric.ed.gov/?id=EJ880290 [abstract]
88. Rey, 2012. A Review of Research and a Meta-Analysis of the Seductive Detail Effect. Educational Research Review. https://eric.ed.gov/?id=EJ986386 [abstract]
89. Sundararajan & Adesope, 2020. Keep It Coherent: A Meta-Analysis of the Seductive Details Effect. Educational Psychology Review 32, 707–734. https://eric.ed.gov/?id=EJ1263249 [abstract]
90. Bateman, Mandryk, Gutwin, Genest, McDine & Brooks, 2010. Useful Junk? The Effects of Visual Embellishment on Comprehension and Memorability of Charts. CHI 2010, 2573–2582. https://sites.stat.columbia.edu/gelman/communication/Bateman2010.pdf, doi:10.1145/1753326.1753716 [first-hand]
91. Huestegge & Philipp, 2011. Effects of spatial compatibility on integration processes in graph comprehension. Attention, Perception, & Psychophysics 73(6), 1903–1915. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=21678020&rettype=abstract&retmode=text, https://www.uni-wuerzburg.de/fileadmin/06020330/Methoden/Publikationen/Effects_of_spatial..._APP.pdf [abstract; the statement of its introduction on direct labels a relay]
92. Heiser & Tversky, 2006. Arrows in Comprehending and Producing Mechanical Diagrams. Cognitive Science 30(3). https://eric.ed.gov/?id=EJ747083 [abstract]
93. Höffler & Leutner, 2007. Instructional Animation versus Static Pictures: A Meta-Analysis. Learning and Instruction. https://eric.ed.gov/?id=EJ780451 [abstract]
94. Berney & Bétrancourt, 2016. Does animation enhance learning? A meta-analysis. Computers & Education 101, 150–167. https://access.archive-ouverte.unige.ch/access/metadata/75bf6876-cb91-4e2c-8ac6-9d0767449449/download, doi:10.1016/j.compedu.2016.06.005 [first-hand]
95. Tversky, Morrison & Bétrancourt, 2002. Animation: can it facilitate? International Journal of Human-Computer Studies 57, 247–262. https://hci.stanford.edu/courses/cs448b/papers/Tversky_AnimationFacilitate_IJHCS02.pdf [first-hand]
96. Abrams & Christ, 2003. Motion onset captures attention. Psychological Science 14(5), 427–432. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=12930472&rettype=abstract&retmode=text, doi:10.1111/1467-9280.01458 [abstract]
97. W3C. Understanding WCAG 2.2, Success Criterion 2.2.2 Pause, Stop, Hide. https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html [first-hand]
98. W3C. Media Queries Level 5, Working Draft, § 12.1 prefers-reduced-motion. https://www.w3.org/TR/mediaqueries-5/ [first-hand]
99. W3C. Understanding WCAG 2.2, Success Criterion 2.3.3 Animation from Interactions. https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html [first-hand]
100. Ozcelik, Karakus, Kursun & Cagiltay, 2009. An Eye-Tracking Study of How Color Coding Affects Multimedia Learning. Computers & Education. https://eric.ed.gov/?id=EJ842989 [abstract]
101. Seufert, 2003. Supporting Coherence Formation in Learning from Multiple Representations. Learning and Instruction. https://eric.ed.gov/?id=EJ672419 [abstract]
102. Ainsworth, 2006. DeFT: A Conceptual Framework for Considering Learning with Multiple Representations. Learning and Instruction. https://eric.ed.gov/?id=EJ737858 [abstract]
103. Holland & Rose, 1981. A Comparison of Prose and Algorithms for Presenting Complex Instructions. Document Design Project Technical Report No. 17, American Institutes for Research, ERIC ED213027. https://files.eric.ed.gov/fulltext/ED213027.pdf, https://eric.ed.gov/?id=ED213027 [relay: for its own experiment the ERIC abstract of a report whose review is not known, for the earlier experiment the report's summary]
104. Berry, Kamsties & Krieger, 2003. From Contract Drafting to Software Specification: Linguistic Sources of Ambiguity, A Handbook. University of Waterloo. https://cs.uwaterloo.ca/~dberry/handbook/ambiguityHandbook.pdf [first-hand]
105. NASA. Systems Engineering Handbook, Appendix C "How to Write a Good Requirement". https://www.nasa.gov/reference/system-engineering-handbook-appendix/ [first-hand]
106. Kim, Setlur & Agrawala, 2021. Towards Understanding How Readers Integrate Charts and Captions: A Case Study with Line Charts. CHI '21. https://arxiv.org/pdf/2101.08235, doi:10.1145/3411764.3445443 [first-hand]
107. Zhu, Cheng & Wu, 2022. How Do Captions Affect Visualization Reading? arXiv:2205.01263 [relay]

Also cited here: [60], [61], [37], [30], [34].

**Q6. Worked cases**

108. Barbieri, Miller-Cotto, Clerjuste & Chawla, 2023. A Meta-analysis of the Worked Examples Effect on Mathematics Performance. Educational Psychology Review 35(1). https://eric.ed.gov/?id=EJ1364058 [abstract]
109. Kalyuga, Chandler, Tuovinen & Sweller, 2001. When Problem Solving Is Superior to Studying Worked Examples. Journal of Educational Psychology 93(3), 579–588. https://eric.ed.gov/?id=EJ640537 [abstract]
110. Tetzlaff, Simonsmeier, Peters & Brod, 2025. A cornerstone of adaptivity – A meta-analysis of the expertise reversal effect. Learning and Instruction 98, 102142. https://www.pedocs.de/volltexte/2026/34113/pdf/Learn_and_Instr_2025_Tetzlaff_u.a._A_cornerstone_of_adaptivity.pdf [first-hand]
111. Fyfe, McNeil, Son & Goldstone, 2014. Concreteness Fading in Mathematics and Science Instruction: A Systematic Review. Educational Psychology Review 26(1), 9–25. https://eric.ed.gov/?id=EJ1036777 [abstract]
112. Trninic, Kapur & Sinha, 2020. The Disappearing 'Advantage of Abstract Examples in Learning Math'. Cognitive Science 44(7), e12851. https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=32588486&rettype=abstract&retmode=text, doi:10.1111/cogs.12851 [abstract]
113. Xie, Nelson & Ko, 2018. An Explicit Strategy to Scaffold Novice Program Tracing. SIGCSE '18, 344–349. https://api.semanticscholar.org/graph/v1/paper/DOI:10.1145/3159450.3159527?fields=title,year,authors,abstract,venue, doi:10.1145/3159450.3159527 [abstract]
114. Catrambone, 1998. The Subgoal Learning Model: Creating Better Examples So That Students Can Solve Novel Problems. Journal of Experimental Psychology: General 127(4), 355–376. https://mrbartonmaths.com/resourcesnew/8.%20Research/Problem%20Solving/The%20Subgoal%20Learning%20Model.pdf [first-hand]
115. Margulieux, Morrison & Decker, 2020. Reducing Withdrawal and Failure Rates in Introductory Programming with Subgoal Labeled Worked Examples. International Journal of STEM Education 7, 19. https://eric.ed.gov/?id=EJ1253101 [abstract]
116. Britton & Gülgöz, 1991. Using Kintsch's computational model to improve instructional text: Effects of repairing inference calls on recall and cognitive structures. Journal of Educational Psychology 83(3), 329–345. https://api.openalex.org/works/doi:10.1037/0022-0663.83.3.329, doi:10.1037/0022-0663.83.3.329 [relay]
117. Gick & Holyoak, 1983. Schema Induction and Analogical Transfer. Cognitive Psychology 15, 1–38. https://gwern.net/doc/psychology/1983-gick.pdf [first-hand]
118. Atkinson, Derry, Renkl & Wortham, 2000. Learning from Examples: Instructional Principles from the Worked Examples Research. Review of Educational Research 70(2), 181–214. https://assess.ucr.edu/sites/default/files/2019-02/atkinsonderryrenklwortham_2000.pdf [first-hand]
119. Alfieri, Nokes-Malach & Schunn, 2013. Learning Through Case Comparisons: A Meta-Analytic Review. Educational Psychologist 48(2), 87–113. https://eric.ed.gov/?id=EJ1000186 [abstract]
120. Schwartz & Bransford, 1998. A Time for Telling. Cognition and Instruction 16(4), 475–522. https://aaalab.stanford.edu/papers/time_for_telling.pdf [abstract]
121. Miller, 2019. Explanation in Artificial Intelligence: Insights from the Social Sciences. Artificial Intelligence 267. https://arxiv.org/abs/1706.07269 [first-hand]
122. Lipton & Steinhardt, 2018. Troubling Trends in Machine Learning Scholarship. ICML 2018 Debates. https://arxiv.org/abs/1807.03341 [first-hand]
123. Meyes, Lu, Waubert de Puiseau & Meisen, 2019. Ablation Studies in Artificial Neural Networks. arXiv:1901.08644 [relay]

Also cited here: [64], [4].

**Q7. References in place**

124. Fitzsimmons, Weal & Drieghe, 2019. The impact of hyperlinks on reading text. PLoS ONE 14(2): e0210900. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0210900 [first-hand]
125. Wikimedia Foundation, 2018. Page Previews/2017-18 A/B Tests. https://www.mediawiki.org/wiki/Page_Previews/2017-18_A/B_Tests [first-hand]
126. Ko, Myers, Coblenz & Aung, 2006. An Exploratory Study of How Developers Seek, Relate, and Collect Relevant Information during Software Maintenance Tasks. IEEE Transactions on Software Engineering 32(12). doi:10.1109/TSE.2006.116 [abstract]
127. Bragdon, Zeleznik, Reiss, Karumuri, Cheung, Kaplan, Coleman, Adeputra & LaViola, 2010. Code Bubbles: a working set-based interface for code understanding and maintenance. CHI 2010. doi:10.1145/1753326.1753706 [abstract]
128. Mäder & Egyed, 2015. Do developers benefit from requirements traceability when evolving and maintaining a software system? Empirical Software Engineering 20(2). https://link.springer.com/article/10.1007/s10664-014-9314-z [abstract]
129. Authors not recorded by the unit, 2025. Providing Information About Implemented Algorithms Improves Program Comprehension: A Controlled Experiment. EASE 2025. arXiv:2504.19225 [abstract]
130. Hata, Treude, Kula & Ishio, 2019. 9.6 Million Links in Source Code Comments: Purpose, Evolution, and Decay. ICSE 2019. arXiv:1901.07440 [abstract]
131. Sphinx documentation, "Configuration", option `nitpicky`, and "sphinx-build", option `-W`. https://www.sphinx-doc.org/en/master/usage/configuration.html, https://www.sphinx-doc.org/en/master/man/sphinx-build.html [first-hand]
132. The rustdoc book, "Lints", `broken_intra_doc_links`. https://doc.rust-lang.org/rustdoc/lints.html [first-hand]
133. Oracle. The javadoc Command, JDK 21: DocLint group `reference` and option `-Werror`. https://docs.oracle.com/en/java/javase/21/docs/specs/man/javadoc.html [first-hand]
134. Visual Studio Code documentation, Command Line Interface, "Opening VS Code with URLs". https://code.visualstudio.com/docs/configure/command-line [first-hand]
135. JetBrains YouTrack, issue TBX-3965 "Documentation for Toolbox Reference URL Scheme", comments of JetBrains staff 2019–2025. https://youtrack.jetbrains.com/projects/TBX/issues/TBX-3965 [first-hand; a practice report]
136. W3C. Web Content Accessibility Guidelines (WCAG) 2.1: SC 1.4.13 Content on Hover or Focus and SC 2.1.1 Keyboard. https://www.w3.org/TR/WCAG21/ [first-hand]
137. W3C. Media Queries Level 4, § 7.2 hover and § 7.3 any-hover. https://www.w3.org/TR/mediaqueries-4/ [first-hand]
178. W3C. Understanding SC 1.4.13: Content on Hover or Focus, updated 12 July 2026. https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html [first-hand; a norm's explanatory document, opened for the record of the clause, outside the nine units]

Also cited here: [41], [61], [64], [68], [34].

**Q8. Controls**

138. Apple. Human Interface Guidelines, "Edit menus", read through the data behind the page. https://developer.apple.com/design/human-interface-guidelines/edit-menus [first-hand]
139. Google. Material Design 1, "Selection" pattern, "Text selection toolbar". https://m1.material.io/patterns/selection.html [first-hand]
140. Hypothesis. Annotation Basics in the Hypothesis LMS App. https://web.hypothes.is/help/annotation-basics-in-the-hypothesis-lms-app/ [first-hand]
141. W3C. Understanding WCAG 2.2, Success Criterion 3.2.2 On Input. https://www.w3.org/WAI/WCAG22/Understanding/on-input.html [first-hand]
142. Nielsen. 10 Usability Heuristics for User Interface Design, #3 User Control and Freedom. Nielsen Norman Group. https://www.nngroup.com/articles/ten-usability-heuristics/ [first-hand; its derivation a relay]
143. freedesktop.org. Clipboards specification. https://wiki.freedesktop.org/Specifications/ClipboardsWiki/ [first-hand]
144. W3C. Clipboard API and events, Working Draft, § 9.2.1 and § 10. https://www.w3.org/TR/clipboard-apis/ [first-hand]
145. MDN Web Docs. Clipboard API, "Security considerations". https://developer.mozilla.org/en-US/docs/Web/API/Clipboard_API [first-hand]
146. Hasler, Kersten & Sweller, 2007. Learner control, cognitive load and instructional animation. Applied Cognitive Psychology 21, 713–729. https://www.runi.ac.il/media/j2jbwbjw/learnercontrolcognitiveloadandinstructional.pdf, doi:10.1002/acp.1345 [first-hand]
147. W3C. Understanding WCAG 2.2, Success Criterion 2.5.2 Pointer Cancellation. https://www.w3.org/WAI/WCAG22/Understanding/pointer-cancellation.html [first-hand]
148. W3C. ARIA Authoring Practices Guide, Button Pattern. https://www.w3.org/WAI/ARIA/apg/patterns/button/ [first-hand]
149. YouTube Help. Keyboard shortcuts. https://support.google.com/youtube/answer/7631406?hl=en [first-hand]
150. W3C. Understanding WCAG 2.2, Success Criterion 2.1.4 Character Key Shortcuts. https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html [first-hand]
151. Keelor, Creaghead, Silbert & Horowitz-Kraus, 2020. Text-to-Speech Technology: Enhancing Reading Comprehension for Students with Reading Difficulty. Assistive Technology Outcomes and Benefits 14, 19–35. https://www.atia.org/wp-content/uploads/2020/06/ATOB-V14-A2-Keelor_etal.pdf [first-hand]
152. Keelor, Creaghead, Silbert, Breit & Horowitz-Kraus, 2023. Impact of text-to-speech features on the reading comprehension of children with reading and language difficulties. Annals of Dyslexia 73, 469–486. https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:37119436%20AND%20SRC:MED&resultType=core&format=json, doi:10.1007/s11881-023-00281-9 [abstract]
153. Brown, Knollman-Porter, Hux, Wallace & Deville, 2021. Effect of Digital Highlighting on Reading Comprehension Given Text-to-Speech Technology for People with Aphasia. Aphasiology 35(2). doi:10.1080/02687038.2020.1787728 [abstract]

Also cited here: [78], [96], [97].

**Q9. Navigation**

154. Pernice & Budiu, 2016. Hamburger Menus and Hidden Navigation Hurt UX Metrics. Nielsen Norman Group. https://www.nngroup.com/articles/hamburger-menus/ [first-hand]
155. Nielsen Norman Group. Table of Contents: The Ultimate Design Guide. https://www.nngroup.com/articles/table-of-contents/ [relay; a practice report]
156. Nielsen Norman Group. In-Page Links for Content Navigation. https://www.nngroup.com/articles/in-page-links-content-navigation/ [first-hand; a practice report]
157. Nielsen Norman Group. Anchors OK? Re-Assessing In-Page Links. https://www.nngroup.com/articles/in-page-links/ [first-hand; a practice report]
158. Apple. Human Interface Guidelines, "Sidebars", read through the data behind the page. https://developer.apple.com/design/human-interface-guidelines/sidebars [first-hand]
159. Material Components for Android, docs/components/NavigationDrawer.md and docs/components/TopAppBar.md. https://raw.githubusercontent.com/material-components/material-components-android/master/docs/components/NavigationDrawer.md [first-hand]
160. Android Developers. Use window size classes. https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes [first-hand]
161. W3C CSS Working Group. CSS Scroll Anchoring Module Level 1, Editor's Draft, § 2 and § 2.2.2. https://drafts.csswg.org/css-scroll-anchoring/ [first-hand]
162. MDN browser-compat-data, css/properties/overflow-anchor.json. https://raw.githubusercontent.com/mdn/browser-compat-data/main/css/properties/overflow-anchor.json [first-hand]
163. web.dev. Cumulative Layout Shift (CLS). https://web.dev/articles/cls [first-hand]
164. W3C, 2023. Accessible Rich Internet Applications (WAI-ARIA) 1.2, Recommendation, `aria-current`. https://www.w3.org/TR/wai-aria-1.2/ [first-hand]
165. W3C. ARIA Authoring Practices Guide, Landmark Regions. https://www.w3.org/WAI/ARIA/apg/practices/landmark-regions/ [first-hand]
166. W3C. HTML Accessibility API Mappings 1.0, Working Draft, § 4.1.9. https://www.w3.org/TR/html-aam-1.0/ [first-hand]
167. Dee-Lucas & Larkin, 1995. Learning From Electronic Texts: Effects of Interactive Overviews for Information Access. Cognition and Instruction 13(3). https://api.openalex.org/works/doi:10.1207/s1532690xci1303_4, doi:10.1207/s1532690xci1303_4 [abstract]
168. Cojean & Jamet, 2021. Does an interactive table of contents promote learning from videos? A study of consultation strategies and learning outcomes. British Journal of Educational Technology. https://api.openalex.org/works/doi:10.1111/bjet.13164, doi:10.1111/bjet.13164 [abstract]
169. Amadieu, Tricot & Mariné, 2009. Prior knowledge in learning from a non-linear electronic document: Disorientation and coherence of the reading sequences. Computers in Human Behavior 25(2), 381–388. https://pmc.ncbi.nlm.nih.gov/articles/PMC7126386/ [first-hand]
170. Cuddihy & Spyridakis, 2012. Computers in Human Behavior 28(4), 1399–1409, doi:10.1016/j.chb.2012.03.002, as reported by Benoliel & Becher, 2024, Messy Contracts, University of Illinois Law Review, p. 908. https://illinoislawreview.org/wp-content/uploads/2024/07/Benoliel.pdf [relay]
171. Salmerón & García, 2012. Children's Reading of Printed Text and Hypertext with Navigation Overviews: The Role of Comprehension, Sustained Attention, and Visuo-spatial Abilities. Journal of Educational Computing Research, author manuscript. https://www.uv.es/lasalgon/papers/2012_JECR.pdf [first-hand]
172. Hubbard & Dunbar, 2017. Perceptions of scientific research literature and strategies for reading papers depend on academic career stage. PLoS ONE 12(12): e0189753. https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0189753 [first-hand]
173. Shiely, Gallagher & Millar, 2024. How, and why, science and health researchers read scientific (IMRAD) papers. PLoS ONE 19(1). https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0297034 [first-hand]
174. Kim, Hoque, Kim & Agrawala, 2018. Facilitating Document Reading by Linking Text and Tables. UIST 2018. https://hci.stanford.edu/publications/2018/text-table-ref/paper.pdf [first-hand]
175. Wang, Cachola, Bragg et al., 2021. Improving the accessibility of scientific documents. arXiv:2105.00076 [first-hand; a practice report]
176. Katz & Byrne, 2003. Effects of Scent and Breadth on Use of Site-Specific Search on E-Commerce Web Sites. ACM Transactions on Computer-Human Interaction 10(3). https://api.openalex.org/works/doi:10.1145/937549.937551 [abstract]
177. Bailly, Oulasvirta, Brumby & Howes, 2014. Model of Visual Search and Selection Time in Linear Menus. CHI 2014. https://discovery.ucl.ac.uk/id/eprint/1431982/1/Brumby_model_of_visual_search_and_selection.pdf [first-hand]

Also cited here: [30], [41].