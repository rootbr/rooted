# Forms of delivery: text, page with voice

One story and one set of pictures serve both forms. The story is written once, for the ear (`references/explaining.md` § The story); each part that has something to show takes one picture, designed once (§ The pictures there). Each form draws the same pictures in its own way.

| Form | What the reader gets | Delivered by default when |
|--|--|--|
| text | the story under part headings, each picture as pseudographics, and the list "Where to look", in the chat | always: an ordinary report, a status, an answer the reader returns to |
| page with voice | the story on a page with a player; each picture drawn as a figure; the sentence being spoken and the element of the figure it names are lit; a switch where options differ; the decision answered on the page and a field for his words after every part; each proof opens in place | the report has a mechanism that a figure shows, or a decision among options that behave differently on one input |

## Who chooses

- The default follows the table: the text always goes out, and the page is added when its row applies.
- The reader's word overrides the default, for one deliverable or as a standing preference: "make a page here", "only the page", "text only". A standing preference is recorded with the reader's other decisions (`SKILL.md` § 7) and read before the next report.
- When the page cannot be built here (no synthesiser, no page publisher), the text says so and goes out alone.

## The page with voice

- **One text.** The page's prose is the story as it is spoken, sentence for sentence. A spoken sentence lands on exactly one place of the page: its own sentence, or the block of a picture that shows what it says, as an option's block shows the sentences about that option.
- **The page lights, the reader moves.** While the voice runs, the sentence being spoken and the element of the figure it names are lit a little brighter. The page scrolls nothing, switches nothing and plays nothing by itself: the reader scrolls, switches and opens. One control jumps to the lit place, and the parts of the story are buttons that start the voice from that part.
- **Calm figures.** A figure is drawn in the page's own palette: neutral lines, one accent, green and red only where they carry a verdict, one colour for what is lit. Each figure stands apart in its own frame. The opening has no figure.
- **A switch says what it changes.** Where options behave differently on one input, the figure shows that input and a switch names each behaviour in the reader's words ("the client repeats the payment", "the client does not repeat the payment"), never an option's number alone. An option that is not built is marked on the figure as how it would behave.
- **The decision is answered on the page.** Each option is a button the reader picks. A field under the options takes his words, typed or dictated. One control copies the answer for the chat: the picked option and his words. The page keeps the answer where the session can read it. The decisions stand at the end by default; one that rests on a single part may stand under that part.
- **Every part takes the reader's words.** After each part of the story a field takes his words on that part, typed or dictated, so he comments while he reads. The control that copies the decision's answer carries these words with it, one line a part, and the page keeps them with the answer. A part that holds a decision takes none of its own: the decision's field serves it.
- **Complete without the sound.** Everything is readable at rest; nothing waits for the player.
- **Proof in place.** Each line of "Where to look" opens the lines around its anchor, the proving line marked.
- **Built from the report.** `references/page.md` gives the steps: the story as it is spoken, the voice with the time of every sentence (`scripts/voice_cues.py`), the body, the build that refuses a page breaking these rules (`scripts/build_page.py`), the publication and the reading of the answer.
