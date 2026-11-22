# An explanation for several readers

An explanation tells several readers how a mechanism works and why it is built so. No decision of theirs closes it, and they come back to it to look things up. It is written by the rules of the story (`references/explaining.md`) and delivered as a page with voice (`references/media.md`, `references/page.md`); this file holds what differs from a report. The genre is drawn from one page of 319 spoken sentences in 20 parts, which its commissioner read and approved. Four of its readers reviewed that page at one meeting: they could not rebuild the algorithm from it and went to the code, while at least six of the questions they asked had their answer on the page. Whether readers rebuild a mechanism from a page built by this file is not measured.

## When a deliverable is an explanation

- **Three signs together.** The readers are several and want different things from the text: one builds on the mechanism, one reviews it, one needs the gist. Nothing in it waits for their decision. They return to it and search in it. One reader and a decision make a report.
- **What holds as in a report**: the registry of questions before any sentence, the opening of three to five sentences that gives the whole matter, a phrase that announces each part, one name per thing, a picture for each part that has something to show, the anchors and the cold read. On the page of 20 parts the five-sentence opening still gave the whole matter, and the announcing phrases served 20 parts as they serve four.
- **What differs**: the first part gives the mechanism whole, and a later part holds only what can be understood apart from it; the length is bounded per part; the readers enter by the first part, by their question and by the map of the page; a claim about code opens its code where it stands; reference material stands as tables the voice does not read.

## The first part: the mechanism whole

- **One part gives the whole mechanism, right after the opening.** It answers what a newcomer asks, in his order: which signals the mechanism has, how each is measured and what each gives; what it estimates from them; by which steps it turns the estimates into its result. It holds, in this order:
  - what the mechanism keeps within which bound, said in physical terms, and what makes a simpler mechanism fall short, one or two sentences each;
  - the signals, each with what is measured and what that tells;
  - the estimates the mechanism makes from the signals;
  - the rule that recomputes the result, as pseudocode of a few steps (`references/explaining.md` § The pictures);
  - the states and what switches them, as a figure of boxes and arrows with the condition on each arrow, when the mechanism switches states.
- **On this level a thing is named by its role.** A line of the first part names what a later part will unfold in words that explain themselves, and links to that part (`references/explaining.md` § The story, the bullet on introducing a thing).
- **What a line needs stands at the line.** A definition, a reason or a condition without which a signal, an estimate or a step cannot be understood stands with it in the first part: in its sentence, in its row of the table, in the caption of its figure. Sources that could not be understood apart taught better joined than set apart, and joining made no difference for sources that could.
- **The opening and this part stand alone.** A reader who stops after them can retell the mechanism by its steps, without the author and without the code.
- **It is read before the rest is written**, by a person of the team and cold (`SKILL.md` § 6).

## The parts

- **A later part holds what can be understood apart from the first**: a derivation with its figure, a recorded run with its stages, the case that shows why an input is needed, the costs and the limits of the design. It unfolds one named line of the first part: a signal, an estimate, a step of the rule or a state. Its heading carries the words of that line, with the line's number in brackets where the pseudocode numbers its lines ("The key (line 2)"). A part that unfolds no line of the first part leaves, or the first part lacks a line; a part that only says again what the first part says leaves, and what it adds to one line moves to that line.
- **A fact stands in one place.** A value, a condition or a definition is stated once, where the reader first needs it, and every other place links to it. A sentence whose whole content the page already says leaves, and so does a sentence at the end of a part that only says what the next part will tell; the phrase that opens a part and names its subject stays (`references/explaining.md` § The story), and so do the words that join one sentence to the next. In an industrial training setting, explanatory material the learners did not need could harm learning even where it was worked into the instructions, and of the thousand most popular projects of one code host 28.9 % held in their documentation a reference to a code element that had been deleted. One sentence said twice has no measured cost.
- **Every sentence of the page is about the mechanism.** The structure of the page is carried by its headings, its table of questions and its map (`references/media.md`). Manuals for computer systems cut to what the learner needs, the introductions of the system among the cuts, taught better than the full ones (d = 0.89 over three studies).
- **A part answers named questions.** Before a part is written, name the questions of the registry it answers; a part that answers none leaves. Its length is what those questions need: the measure of a small report, twenty to thirty short sentences, is the measure of a part.
- **A term enters in the part that first needs it.** It is derived there from what is measured and stands on that part's figure (`references/explaining.md` § The story, the bullet on a word's one meaning). Its name in the code and its name in the literature open at the term (§ Where to look).
- **The need for each input is shown**, by one case in which the mechanism without it fails (`references/explaining.md` § The story, the bullet on why this way), where the input is introduced or in a part of its own.
- **A part entered from the table of questions or from the map is read with the first part**: a thing the part uses is introduced in the part or named by its role in the first part.
- **Reference material is a table without voice**: constants, measurements with the commands that repeat them. It stands in a figure, the place for what the voice does not say (`references/page.md` § The body).

## The questions on the page

- **The registry holds the newcomer's questions always**, beside the readers' own (`references/explaining.md` § The reader's questions): the first part answers them.
- **The registry becomes a table after the first part.** Two of its fields go onto the page: the question in the reader's words and a link to the place that answers it. The answer stands once, at that place (§ The parts, the bullet on a fact). The fields that say what the reader believes now and what the answer is stay with the author and shape the part (`references/explaining.md` § The story, the bullet on a wrong model). One list then serves as the plan of the text, an entry by question and the questions of the cold read.
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

- **A claim about code opens its code where it stands.** In a table, a caption or a line of pseudocode, the name of a class, a method or a constant is a reference. It shows the lines around its declaration when the reader points at it or moves the keyboard focus to it, and opens them in a panel at his click; a term taken from the literature shows the same way what its paper calls the thing, with a link to the paper. Readers of a machine-learning paper, most of them students, answered questions on its terms 45 s faster, and no more correctly, with a reader that showed a definition at each use among its aids than with a plain one (27 readers); engineers reading an explanation were not tested.
- **Each line of the pseudocode names the method that carries it out**, in a second column beside the line.
- **A preview answers the keyboard as it answers the pointer.** It opens on focus, stays while the pointer rests on it and closes on Escape: the accessibility standard asks that content shown on hover can be dismissed and can be hovered, and the document that explains it names the keyboard focus and the Escape key. On a screen whose pointer cannot hover, the reference is an ordinary link that opens the panel.
- **The builder resolves every reference.** A reference is given as data: the file and a fragment of its line. The builder finds the line and refuses a fragment that stands on no line or on several (`references/page.md` § References as data), so the page is rebuilt after the code moves and cannot keep a name the code has dropped. Documentation tools for three languages offer the same refusal of a reference that does not resolve.
- **The closing list holds what has no place in the text**: the checks that ran, with their counts and exit codes, and a place the story rests on that no table, caption or line of pseudocode names. It follows the order of the story; the bound of five lines is the report's.
- **A link into the reader's editor** stands beside a reference only on a page built for the author's own machine: it carries a path of that machine, and a page shown inside another site's frame may refuse it (`references/page.md` § References as data).

## Delivery

- **The page** is built by the steps of `references/page.md`. The builder refuses an explanation whose first part holds no pseudocode, whose table of questions stands before the end of the first part, or whose figure has no name for the map of the page (`references/page.md` § The blocks of an explanation); it refuses any page that holds a barred word of the list of terms (`references/explaining.md` § The terms).
- **The text in the chat** is the opening, the first part with its pseudocode as a fenced block, and the page's address, then under "Where to look" the five places the story turns on and the checks that ran. `scripts/check_report.py` checks that text as it checks a report.
- **The cold read** of the finished page takes the page's text as the builder writes it (`scripts/build_page.py --text-out`) and the questions of the registry without the author's answers (`SKILL.md` § 6).
- **What was not seen working** is said in one sentence at delivery, as for any page; whether the voice's pronunciation was checked, by what and for which language, belongs to that sentence.
