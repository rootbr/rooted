# Building a page with voice

A page with voice is built from the report's own story once that form is chosen (`references/media.md`). Nothing is written twice: the story of the text form is the text the voice speaks, and its pictures are the page's figures.

## Steps

1. **Write the story as it is spoken** into `story.txt`: the report's prose, one paragraph per part, in the report's order, with no heading, fence or list. Every part after the opening begins with the short phrase that announces it ("How it broke."); the text form shows that phrase as the part's heading. What the text form shows only as a picture is written out here in sentences, because the voice says it: the options of a decision become "The first: … Then … The second: … Then …". A period followed by a space ends a sentence for the voice, so the story writes out an abbreviation and an ordinal that carry one ("for example", "the third of May").
2. **Voice it.** One of:

   ```bash
   python3 <skill-dir>/scripts/voice_cues.py --voice-module <synthesiser.py> story.txt story.wav cues.json
   python3 <skill-dir>/scripts/voice_cues.py --tts-command '<command with {text} and {out}>' story.txt story.wav cues.json
   ```

   The module form takes a synthesiser that returns word timings and voices a paragraph in one call. The command form takes any program that writes a WAV for a text and runs it once per sentence. `cues.json` lists every sentence with its number `part.sentence` and its start and end in the audio. The script's own help names the options and the environment variables that stand in for them.
3. **Write the body** into `body.html` (§ The body). `assets/page-body-example.html` is a worked body.
4. **Build.**

   ```bash
   python3 <skill-dir>/scripts/build_page.py --body body.html --cues cues.json --report report.md \
     --root <repo> --title "<what the report is about>" --id <short-name> --voice <audio address> --out page.html
   ```

   The builder fills the sentences in, appends "Where to look" from the report with the lines around every anchor, and refuses the page (exit 1, one line per violation) when a spoken sentence lands on no element or is written out in two `data-say` elements, when the body names a sentence the voice does not say, or when a decision is malformed. Fix the body, never the check. The title is `--title`, else the body's first `h1`. The words the page itself shows (the player, the pick and copy controls) are English; `--strings <file>`, or `$XDG_CONFIG_HOME/handing-over-to-readers/page-strings.json`, gives them in the reader's language, as the lexicon file `$XDG_CONFIG_HOME/handing-over-to-readers/lexicon.json` gives the report's closing heading.
5. **Publish.** With a page publisher in the session: publish `page.html`, put the audio into the page's file store, build again with that file's address as `--voice`, publish again. A store that takes video and no audio gets the audio in a video container with a still frame:

   ```bash
   ffmpeg -f lavfi -i color=c=black:s=320x180:r=2 -i story.wav -shortest -c:v libx264 -tune stillimage \
     -pix_fmt yuv420p -c:a aac -b:a 64k -movflags +faststart story.mp4
   ```

   Without a publisher: build with `--standalone` and `--voice story.wav`, keep the audio beside the page, and give the reader the page's path.
6. **Deliver** the text form in the chat with the page's address after the opening paragraph. Say in one sentence what of the page you did not see working.
7. **Read the answer.** The reader answers a decision on the page, writes his words under any part, comments on any piece of the text, and copies the answer into the chat: a numbered line for each decision, then a line `<part title>: <words>` for each part he commented, then one line for each comment on a piece: the piece in quotation marks, the title of the part it stands in, his comment. A page with a document store also keeps it as the document `answers/<id>` (`choices`, `words`, `remarks` by the part's number, `notes` with each piece as `quote`, its `part` and the comment as `text`, and the whole copied `text`). When he says he answered on the page, read that document.

## The body

The body is the article: HTML without scripts and without colours of its own.

- **A spoken sentence shown as text**: an empty element with the sentence numbers, which the builder fills.

  ```html
  <p data-say="1.1 1.2 1.3 1.4"></p>
  <h2 data-lit="2.1">How it broke</h2>
  <p data-say="2.2 2.3 2.4 2.5 2.6"></p>
  ```

  The announcing phrase of a part (`2.1`) lights the part's heading; the heading's words are the reader's, one to four of them.
- **A spoken sentence shown by a picture**: `data-lit` on the element that shows what the sentence says: a box of a figure, a row of a table, an option of a decision. An element may list several sentences.
- **Every sentence of `cues.json` appears** in exactly one `data-say`, or in no `data-say` and at least one `data-lit`.
- **What the voice does not say** may stand on the page only inside a figure, its caption or an option of a decision: a label, a scale, a note on what was computed, an option's heading with its gains, costs and reason.

## Figures from ready parts

A figure is the part's picture (`references/explaining.md` § The pictures), drawn with the parts of the page template `assets/page-template.html`. Each stands in its own `<figure>`; an SVG takes `class="fig"`, a `viewBox` 720 wide, and sits in `<div class="figscroll">`.

| Part | What it is | Lit by |
|--|--|--|
| `rect.box` | an actor or a step | the sentence that names it |
| `rect.attempt`, `rect.pause` | a span of time and the gap after it, drawn to one scale | the sentence about that span |
| `rect.ok`, `rect.no` | an outcome that is right or wrong; it keeps its colour while lit | the sentence that gives the verdict |
| `line.arr` with `path.arrh` | a message or a step from one box to the next | the sentence about the sending |
| `rect.codebg` with `text.mono` lines and `rect.hl` | a window of code with the lines that matter framed | the sentence about that code |
| `text` with `.dim`, `.bad`, `.good`, `.small`, `.lane`, `.mono` | a label, a failure, a success, a small label, a lane's name, a literal | the sentence that says it |
| `<figure class="twocol">` with `li.plus`, `li.minus` | what is there and what is missing | the sentence about each item |
| an HTML table inside `<figure>` | before and after, the differing cell in its own row | the sentence about each row |

Group the shapes and the label of one thing in a `<g data-lit="…">`, so they light together:

```html
<figure>
  <div class="figscroll"><svg class="fig" viewBox="0 0 720 96" role="img" aria-labelledby="h-how">
    <g data-lit="2.2"><rect class="attempt" x="40" y="30" width="136" height="48"/><text x="108" y="59" text-anchor="middle">attempt 1</text></g>
    <g data-lit="2.3"><rect class="pause" x="176" y="30" width="14" height="48"/><text class="mono dim" x="183" y="22" text-anchor="middle">200 ms</text></g>
    <g data-lit="2.3"><rect class="attempt" x="190" y="30" width="136" height="48"/><text x="258" y="59" text-anchor="middle">attempt 2</text></g>
  </svg></div>
  <figcaption>To scale: an attempt lasts 2 s.</figcaption>
</figure>
```

- A figure states one thing, in the palette of the page; green and red appear only where they carry a verdict.
- Sizes are computed: one scale for every span of a time line, text of 14 px that fits its box with room on both sides.
- The opening has no figure.
- **A switch** belongs to a figure that shows how options differ on one input. The group names what changes in the reader's words; the elements of one behaviour carry `only-now`, of the other `only-safe`; an option that is not built says so on the figure.

  ```html
  <div class="controls"><span class="muted" id="sw-label">What the client does with a payment after a timeout:</span>
    <div class="seg" role="group" aria-labelledby="sw-label" data-switch="fig-fail">
      <button type="button" data-mode="now" aria-pressed="true">repeats it, as now</button>
      <button type="button" data-mode="safe" aria-pressed="false">does not repeat it, the first option</button>
    </div></div>
  ```

## A decision

```html
<h2 data-lit="4.1">What to decide</h2>
<section class="decision" data-decision="cache" data-title="Old thumbnails">
  <div class="options">
    <div class="option" data-option="purge the cache now" data-mine="1" data-lit="4.2 4.3">
      <h4>Purge the cache now</h4>
      <ul><li class="plus">the wrong thumbnails are gone at once</li><li class="minus">every gallery page is slow for about twenty minutes</li></ul>
      <p class="why">Why: twenty slow minutes at night cost least.</p>
    </div>
    <div class="option" data-option="let the old entries expire" data-lit="4.4 4.5">
      <h4>Let the old entries expire</h4>
      <ul><li class="plus">nothing slows down</li><li class="minus">an old thumbnail for up to a day</li></ul>
    </div>
  </div>
</section>
<p data-say="4.6"></p>
<p class="ask" data-say="4.7"></p>
```

- `data-option` is the option in the words the copied answer will carry; `data-title` names the decision there.
- The author's choice carries `data-mine="1"` and its reason in `.why`, so the reason is readable without the sound.
- Several decisions are several sections, each with a heading of its own lit by the sentence that names it; the question that closes the story stands after the last. A decision that rests on one part may stand inside that part; the control that copies the answer follows the last field of the page.
- The page adds the pick controls, the field for the reader's words under each decision and under each part without one, the pause beside the spoken sentence, the window for a comment on a piece of the text and the control that copies the answer; the body writes none of them.

## Before delivery

- The builder exits 0.
- Open the page once where the session can: every figure inside its frame, no text over an edge, both themes readable.
- The text form passed `python3 -I <skill-dir>/scripts/check_report.py --profile operator --root <repo> report.md` with no error (`SKILL.md` § 6); the page is built from that text.
