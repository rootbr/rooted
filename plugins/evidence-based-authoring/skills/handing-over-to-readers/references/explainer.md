# An explanation for several readers

An explanation tells several readers how a mechanism works and why it is built so. No decision of theirs closes it, and they come back to it to look things up. It is written by the rules of the story (`references/explaining.md`) and delivered as a page with voice (`references/media.md`, `references/page.md`); this file holds what differs from a report. The genre is drawn from one page of 319 spoken sentences in 20 parts, which its commissioner read and approved; how its readers used the tables and the questions is not measured.

## When a deliverable is an explanation

- **Three signs together.** The readers are several and want different things from the text: one builds on the mechanism, one reviews it, one needs the gist. Nothing in it waits for their decision. They return to it and search in it. One reader and a decision make a report.
- **What holds as in a report**: the registry of questions before any sentence, the opening of three to five sentences that gives the whole matter, a phrase that announces each part, one name per thing, a picture for each part that has something to show, the anchors and the cold read. On the page of 20 parts the five-sentence opening still gave the whole matter, and the announcing phrases served 20 parts as they serve four.
- **What differs**: the length is bounded per part; the readers enter by their question and by a route; the list "Where to look" follows the story without the bound of five lines; reference material stands as tables the voice does not read.

## The questions on the page

- **The registry becomes the first table.** Three of its fields go onto the page: the question in the reader's words, the answer in one sentence, a link to the part that answers it. The field that says what the reader believes now stays with the author and shapes the part (`references/explaining.md` § The story, the bullet on a wrong model). One list then serves as the plan of the text, its table of contents and the questions of the cold read.
- **Routes by time stand before the table**: what to read in five minutes, in twenty, in an hour. The five-minute route is the opening and the table.
- **The questions are the readers' own.** The record of the meeting where they discussed the work is the first source after the request (`references/explaining.md` § The reader's questions).

## The parts

- **A part answers named questions.** Before a part is written, name the questions of the registry it answers; a part that answers none leaves. Its length is what those questions need: the measure of a small report, twenty to thirty short sentences, is the measure of a part.
- **A part can be entered from the table.** A thing it uses is introduced in it or stands in the table of terms.
- **The table of terms stands before the first part**, three names to a term: the word on the page, the name in the code, the name in the literature. The word on the page is the reader's (`references/explaining.md` § The story, the bullet on the name).
- **Reference material is a table without voice**: constants, classes, terms. It stands in a figure, the place for what the voice does not say (`references/page.md` § The body).

## A question after a part

A part that explains how something works closes with a question the reader answers for himself before he opens the answer; a part of reference tables takes none.

- **The answer is hidden and says why.** It gives the cause and the number behind the verdict: as feedback in computer-based practice an explanation had an effect of 0.49, a bare right-or-wrong 0.05 (70 effect sizes from 40 studies).
- **The question asks to use the mechanism, on a number or a stage of the part.** Answering from memory raised delayed results over rereading, and quizzes on facts alone did not raise results on questions that ask to apply, while quizzes that ask to apply did. It takes one of four forms:
  - reconstruct why a step is needed;
  - predict what happens when one input changes;
  - name the cause from the signs;
  - say what of the source method is here and what is not.

  A question that asks a fact back is the other side of the line:
  - bad: "How long does a cache entry live?"
  - good: "A picture is uploaded a third time. Under which key is its thumbnail stored, and who still reads the entry under the second key?"
- **No count.** The reader marks for himself whether he had the answer, and the page lists the parts worth returning to. It shows no score: over a third of feedback interventions lowered performance, and feedback worked less the closer it drew attention to the person and away from the task. The marks stay in the reader's browser; the copied answer and the author never get them.

## Where to look

- The list follows the order of the story and names every place the story rests on; the bound of five lines is the report's.
- The list is given to the builder as data: what the line proves, the file, the fragment of the line. The builder finds the line and refuses a fragment that stands on no line or on several (`references/page.md` § Where to look as data), so the page is rebuilt after the code moves without an anchor retyped.

## Delivery

- **The page** is built by the steps of `references/page.md`.
- **The text in the chat** is the five-minute route: the opening, the table of questions with its one-sentence answers and the page's address, then under "Where to look" the five places the story turns on and the checks that ran. `scripts/check_report.py` checks that text as it checks a report.
- **The cold read** takes the page's text as the builder writes it (`scripts/build_page.py --text-out`) and the questions of the table without their answers (`SKILL.md` § 6).
- **What was not seen working** is said in one sentence at delivery, as for any page; whether the voice's pronunciation was checked, by what and for which language, belongs to that sentence.
