# An explanation for several readers

An explanation tells several readers how a mechanism works and why it is built so. No decision of theirs closes it, and they come back to it to look things up. It is written by the rules of the story (`references/explaining.md`) and delivered as a page with voice (`references/media.md`, `references/page.md`); this file holds what differs from a report. The genre is drawn from one page of 319 spoken sentences in 20 parts, which its commissioner read and approved. Four of its readers reviewed that page at one meeting: they could not rebuild the algorithm from it and went to the code, while at least six of the questions they asked had their answer on the page. Whether readers rebuild a mechanism from a page built by this file is not measured.

## When a deliverable is an explanation

- **Three signs together.** The readers are several and want different things from the text: one builds on the mechanism, one reviews it, one needs the gist. Nothing in it waits for their decision. They return to it and search in it. One reader and a decision make a report.
- **What holds as in a report**: the registry of questions before any sentence, the opening of three to five sentences that gives the whole matter, a phrase that announces each part, one name per thing, a picture for each part that has something to show, the anchors and the cold read. On the page of 20 parts the five-sentence opening still gave the whole matter, and the announcing phrases served 20 parts as they serve four.
- **What differs**: the first part gives the mechanism whole, and every later part unfolds one line of it; the length is bounded per part; the readers enter by the first part, by their question and by a route; the list "Where to look" names every place the story rests on; reference material stands as tables the voice does not read.

## The first part: the mechanism whole

- **One part gives the whole mechanism, right after the opening.** It answers what a newcomer asks, in his order: which signals the mechanism has, how each is measured and what each gives; what it estimates from them; by which steps it turns the estimates into its result. It holds, in this order:
  - what the mechanism keeps within which bound, said in physical terms, and what makes a simpler mechanism fall short, one or two sentences each;
  - the signals, each with what is measured and what that tells;
  - the estimates the mechanism makes from the signals;
  - the rule that recomputes the result, as pseudocode of a few steps (`references/explaining.md` § The pictures);
  - the states and what switches them, as a figure of boxes and arrows with the condition on each arrow, when the mechanism switches states.
- **On this level a thing is named by its role.** A line of the first part names what a later part will unfold in words that explain themselves, and links to that part (`references/explaining.md` § The story, the bullet on introducing a thing).
- **The opening and this part are the five-minute route.** A reader who stops after them can retell the mechanism by its steps, without the author and without the code.
- **It is read before the rest is written**, by a person of the team and cold (`SKILL.md` § 6).

## The parts

- **Every later part unfolds one named line of the first part**: a signal, an estimate, a step of the rule or a state. Its heading and its first sentence repeat the words of that line. The part gives the line as a small algorithm of its own: what comes in, the steps, what goes out. A part that unfolds no line of the first part leaves, or the first part lacks a line.
- **A part answers named questions.** Before a part is written, name the questions of the registry it answers; a part that answers none leaves. Its length is what those questions need: the measure of a small report, twenty to thirty short sentences, is the measure of a part.
- **A term enters in the part that first needs it.** It is derived there from what is measured and stands on that part's figure (`references/explaining.md` § The story, the bullet on a word's one meaning).
- **The need for a part is shown inside it**, by one case in which the simpler scheme fails (`references/explaining.md` § The story, the bullet on why this way).
- **The table of terms closes the page as a reference**, three names to a term: the word on the page, the name in the code, the name in the literature. The word on the page is the reader's (`references/explaining.md` § The story, the bullet on the name). A part entered from the table of questions is read with it: a thing the part uses is introduced in the part, named by its role in the first part, or looked up in that table.
- **Reference material is a table without voice**: constants, classes, terms. It stands in a figure, the place for what the voice does not say (`references/page.md` § The body).

## The questions on the page

- **The registry holds the newcomer's questions always**, beside the readers' own (`references/explaining.md` § The reader's questions): the first part answers them.
- **The registry becomes a table after the first part.** Three of its fields go onto the page: the question in the reader's words, the answer in one sentence, a link to the part that answers it. The field that says what the reader believes now stays with the author and shapes the part (`references/explaining.md` § The story, the bullet on a wrong model). One list then serves as the plan of the text, its table of contents and the questions of the cold read.
- **Routes by time stand with that table**: what to read in five minutes, in twenty, in an hour.
- **The questions are the readers' own.** The record of the meeting where they discussed the work is the first source after the request (`references/explaining.md` § The reader's questions).

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

- The list on the page follows the order of the story and names every place the story rests on; the bound of five lines is the report's.
- The list is given to the builder as data: what the line proves, the file, the fragment of the line. The builder finds the line and refuses a fragment that stands on no line or on several (`references/page.md` § Where to look as data), so the page is rebuilt after the code moves without an anchor retyped.

## Delivery

- **The page** is built by the steps of `references/page.md`. The builder refuses an explanation whose first part holds no pseudocode, or whose table of questions or of terms stands before the end of the first part (`references/page.md` § The blocks of an explanation).
- **The text in the chat** is the five-minute route: the opening, the first part with its pseudocode as a fenced block, and the page's address, then under "Where to look" the five places the story turns on and the checks that ran. `scripts/check_report.py` checks that text as it checks a report.
- **The cold read** of the finished page takes the page's text as the builder writes it (`scripts/build_page.py --text-out`) and the questions of the table without their answers (`SKILL.md` § 6).
- **What was not seen working** is said in one sentence at delivery, as for any page; whether the voice's pronunciation was checked, by what and for which language, belongs to that sentence.
