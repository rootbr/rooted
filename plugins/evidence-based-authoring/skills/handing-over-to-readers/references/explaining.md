# Explaining: the reader's questions, the story, where to look, the cold read

A deliverable explains when its reader, after one reading, can retell what the task was, what happened and what is needed from him.

## The reader's questions

1. The questions come from the reader before they come from the author's guess. Technical writers and subject or audience experts asked to predict where readers of one brochure would stumble predicted under 15 % of the problems its readers reported.
2. Sources, in this order: the request (every question his words name); the record of a meeting where the readers discussed this work; the reader record (`references/intake.md`); the records the project keeps of him (a review rehearsal journal, review comments on this work, what he asked or complained about after earlier reports); for ground none of them covers, the defaults: what was the task, how did it end, what happened and why, what is unverified, what is his to decide. A question from a meeting is read in the record itself, with the remarks around it: they show what the reader believes now, which is the second field of his registry line. What the meeting decided is the last thing said on the matter. A digest of the meeting points to the place in the record and is never the source: in one case a work item taken from a digest had been postponed at the end of the same meeting, and a question there rested on a model of the mechanism that only the remarks around it showed.
3. Skip what he holds, tell what he has not seen. What an engineer holds without help: his language, the standard library, the patterns of his trade. What he does not hold after being away: the state of this task, the things this work touched, a term coined during the work. An explainer who overestimated the recipient's knowledge, and one who underestimated it, both taught him less than one who held a valid estimate (6.2 and 6.4 against 8.5 on a test of 18); the two errors were not tested against each other.
4. A question whose answer cannot be said in one plain sentence marks a gap in the author's own understanding; it is closed by reading, running or computing before any text is written.

## The story

The story is written for the ear: it is the text the author would read aloud to a colleague who was away, and its sentences are what the voice speaks when the report goes out with sound (`references/media.md`); the bullets on the parts and on the decision name the two places where the text shows a heading or a picture for what the voice says. In one case read by one reader, the narration he found clear ran 8 words a sentence on average and 16 at most; the written story of the same case, which he found tangled, ran 17 on average, with a sentence of 40.

- **The opening gives the whole matter.** The first paragraph says, in three to five sentences, what the reader needs to place everything after it: the task in his words with its terms, how it ended, the problem with its cause in one sentence, and what is needed from him, the options named. The parts after it unfold what the opening named. A sentence whose antecedent is already given is understood faster (835 against 1016 ms to the press of a button on understanding; students reading pairs of sentences), and a report that opens on its result leaves the reader asking what it is about.
- **A sentence the ear can hold.** One claim per sentence, no clause nested inside another, under about twenty words. A second claim starts a new sentence: "The test waited for one attempt. It saw four." `scripts/check_report.py` warns past twenty words.
- **Parts announced.** A short phrase opens each part and says what it is about: "How it works.", "Now the red build.", "There are two ways." A small change takes four parts: the opening, how the thing works, what went wrong, what is his to decide. In the text and on the page each part after the opening stands under a heading of one to four words in the reader's words; the voice says the phrase.
- **Then what happened, in the order of cause and effect.** Each sentence opens on something the earlier ones gave and ends on the new thing. The relation between neighbours is a word: because, so, but, otherwise. A list of facts leaves that relation to the reader.
- **Introduce a thing before using it.** A thing new to the reader is first said as what it is ("the operations team has an alert on errors; it finds the error lines by a pattern") and only then named or used. A computed quantity is first said as what it is for and what happens without it, and only then given as its formula. One new thing per sentence, one name per thing for the whole text.
- **The name is the reader's.** Before a thing gets a name, look for the one it already has: first in the reader's trade, then in the code, taken as the word its authors say ("the retry policy") while the identifier itself stays under "Where to look"; a coined word stays only where neither has one. A term of the trade is written the way an engineer of that trade says it aloud to a colleague in the language of the text. An abbreviation or a word he says in English stays in Latin letters in a Russian or a German text, gets its expansion and one sentence of meaning at its first mention, and takes no native substitute and no literal translation. Terms of one series are written alike: where one stays in English, so do the others. A thing with a living native word keeps it ("queue", "window"). In text for the voice the term stands as it is written, and the synthesiser's pronunciation dictionary sets how it sounds. In one case a text called the round-trip time by a coined native word 52 times against two mentions of RTT, while its readers said RTT; the same readers replaced two more coined words with their own.
- **Plain words, no code.** A thing is named by its role: "requests that only read", "the payment", "the payments team's test"; a term of the reader's trade is one of his plain words. No path, identifier, file name, command or exit code; a number only when the story turns on it, one to a sentence; no label, no bold, no bullet.
- **A wrong model is named before it is corrected.** Where the registry says the reader's present answer does not hold, the part goes in three steps: his model in his words; how the mechanism differs from it; what the thing he asked about really gives or costs. A yes or a no to a question asked from the wrong model stands after the first step, because a bare answer is read inside the model the question came from. Texts that state a common misconception, refute it and then explain taught more than texts that only explain (g = 0.41 over 44 comparisons, most of them students reading one short science text).
- **A picture for each part that has something to show**: a mechanism with its values, a failure, a choice (§ The pictures). The opening takes none: its sentences carry the state. The sentences of a part stay whole without its picture, so the voice skips it. A concrete case that fades into the general statement transferred better than the general statement alone, which a concrete case by itself did not.
- **Why this way** is answered with what happens without it: the input or the state under which the alternative fails, with the number.
- **What was not done or not verified** is a sentence, and only when it changes what the reader does or trusts: "I did not check that."
- **A value the story states is one the author can point at.** It stands on a line under "Where to look", or the story says in the first person that it was computed or not verified. Before writing the consequence of a change, trace it through every file behind the things the story names: a story reads smoothly whether or not its numbers are right.
- **The reader's decision closes the story.** The voice counts the options aloud: "The first: … Then … The second: … Then …", one sentence for what the option is and one for what it gives and costs. The text and the page show the options as the choice picture (§ The pictures) in place of those sentences. The author's choice follows with its reason; one question stands last. A decision that rests on one part alone may stand under that part, its options counted there; the end of the story is the default.
- **Length.** As many sentences as the reader needs to retell the matter and no more. Before a sentence goes in, name the question it answers; a sentence that answers none leaves. A small change takes twenty to thirty short sentences, about two hundred words, a minute and a half aloud.

## Where to look

The proof follows the story as a short list, so the story stays readable and every claim stays checkable.

- At most five lines in a report; an explanation for several readers lists every place its story rests on (`references/explainer.md` § Where to look). Each names in plain words what is there, then gives the `path:line` anchor, and the fragment of the line when the line proves a claim; the fragment is the shortest piece that identifies the line.
- The checks that ran stand here with their counts and exit codes, taken from their output. A claim about behaviour takes a check; a claim about code takes an anchor (`references/evidence.md`).
- The order is the order of the story.

## The cold read

Before a report with a decision goes out, a reader with no context answers the reader's questions from the text alone (`SKILL.md` § 6).

- **Questions without answers.** The cold reader gets the questions of the registry and never the author's answers. Its answer counts only with a sentence of the report behind it, so an answer from the model's own knowledge is set aside.
- **What it shows.** A question left without a full answer points at something the report may not say. On four reports with planted omissions the read marked the missing decision in four of four and the missing cause in four of four, with each of three reader models.
- **What it does not show.** It noticed at most one of four removed sentences that introduced a thing: the sentences around the gap let it rebuild the thing. Introducing a thing before its use stays the author's own check (§ The story). Whether the text is easy to read is outside it too.
- **A mark is weighed, and a clean read proves nothing.** Two of the three models marked one intact report on the question about what is unverified: the report named it, and the reader asked whether there was more. On 60 real reports written before this form, read against all six default questions, the read left a question open in 58; of the 30 things their reader then asked back about, it named 8 and touched 11 more, among five to six marks a report. Compare each mark with the text: add what the text does not say, and leave a mark the text already answers.
- **A stated unknown is an answer.** "I could not tell whether the value came with this change" answers the question about it.

## The pictures

Each part the story's picture bullet names (§ The story) takes one picture. The picture is designed once and drawn in both forms of delivery (`references/media.md`): in the text as pseudographics, on the page as a figure whose elements light with the voice.

| The part says | The picture shows | In the text |
|--|--|--|
| it was one way and is now another | two rows, before and after, the differing part aligned | a plain fence |
| a sequence in time | the steps as boxes on one line, to scale, the gaps labelled | a plain fence drawn with box glyphs |
| who sends what to whom, and how often | the actors joined by an arrow, one row per step, the wrong rows marked | a `diff` fence: the actors on an unmarked line, `+` the step that is right, `-` the steps that are wrong |
| a choice among options | one block per option: what it gives, what it costs | a `diff` fence: the option on an unmarked line, `+` a gain, `-` a cost |
| a recorded run passes through stages | a chart with the stages numbered and a table under it: the number, the time, what the participant sees, which rule fired, the value; a row is lit on its sentence | a table, the stage number in its first column |
| two causes give a similar picture | a table: the causes in rows, the observable signs in columns | a table |
| where a decision of the design comes from | a table: what the mechanism has, its source, what was changed and why, where it stands in our material; under it what was not taken and why; a link the author added himself is marked as his | a table |

- A picture states one thing and marks the row or the element the story turns on.
- A value in the picture of a recorded run is read from the run: a stage is declared once, and its row and its mark on the chart take the same record. In one case stage values typed twice, into the table and into the chart's labels, were reconciled by eye.
- A picture adds what the sentences cannot carry: the instance with its values, the scale, the comparison side by side. One that restates the sentences in boxes is deleted.
- In the text a picture stays within 100 columns and draws its lines from one glyph source; in a `diff` fence the `+` and `-` carry the verdict that the colour repeats.
