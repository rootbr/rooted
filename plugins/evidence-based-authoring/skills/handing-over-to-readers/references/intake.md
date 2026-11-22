# The reader record and the intake

A long explanation fits its reader only when the author holds valid information about what that reader knows. With such information experts' written explanations taught about half again as much (1.52 against 0.99 on a scale of 0 to 3) and drew half the follow-up questions; with random information they gained no more than with none (0.80). So before a long deliverable the skill looks the reader up, reads what the records hold of him, asks when they leave the matter open, and never guesses.

A deliverable is long when it explains a mechanism, carries a decision among options or runs past the length bound of the form check (300 words of prose), in whichever form it goes out (`references/media.md`); an explanation for several readers is always long. A sub-agent's hand-back reaches the reader through the agent that launched it and is never long in this sense.

## The reader record

- **One private file a person, outside every project** (`scripts/records.py reader`). The script refuses a file that a repository would track. The record is never copied into a project file, the project's ledger of answers or a deliverable for another addressee.
- **What a record holds**: a topic, what the reader holds about it, what he lacks, his own words for its things and the words he rejected or misread, what he does with a result (`decide`, `defend`, `build`, `know`), the depth he wants (`mechanism`: the whole thing step by step; `change`: what changed and what is his to decide), the basis and the date.
- **Per topic.** Knowledge is recorded topic by topic, each topic with what he holds and lacks in it: outside their own field, experts searched the web like laymen, their differences generally under a tenth of a standard deviation. `records.py reader show` lists every topic kept for him, which is the whole of what is known of the reader.
  - bad: "reader: senior engineer, expert"
  - good: "topic: HTTP caching; holds: cache keys, expiry times; lacks: purge requests"
- **Dated.** Over five or more weeks of search logs, 31 to 49 % of non-experts used a field's vocabulary in a growing share of their queries. A record is read with its date, and an old one is confirmed by one question before a long deliverable rests on it.
- **Knowledge and use, no style.** Matching a presentation to the form a person says he prefers found no support in adequate tests; the record keeps what he knows and what he will do with the result.

## What the records give before a question

- **The records are read before the reader is asked**, in this order:
  1. what the session's instructions say about its reader;
  2. the reader record;
  3. the project's ledger of his answers and its record of his questions after earlier deliverables;
  4. the records of the meetings and reviews where he spoke;
  5. the documents he wrote.

  A question whose answer stands there is not asked (rule 3 of `references/rules.md`).
- **Taken from them: what he said and what he asked.** His own word for a thing; what he asked or corrected after an earlier deliverable; what he said he works with; what he decided and on what basis. Each goes into the reader record with its basis: `records.py reader add --topic ... --lacks ... --words ... --basis "his question after the report on the cache"`. Writing students who had read records of readers thinking aloud over a text predicted more of the next readers' problems afterwards (5.25 a text against 3.25 before), while students taught by other methods, audience-analysis heuristics among them, predicted fewer than before (2.46 against 3.04).
- **A level enters the record from his own answer or question.** How a person writes, and what he has written, do not show what he lacks: a baseline that read a user's earlier dialogue inferred his expertise correctly in 16 to 20 % of cases, and a model handed a researcher's own publications marked the terms he did not know at F1 64.2 against 63.1 with nothing about him, a difference inside the spread of the measure. So a level is written from his answer to a probe (§ The intake dialogue) or from what he asked.

## When the reader is unknown

- **The detector is the record.** Before a long deliverable run `records.py reader find --topic "<the topic in the reader's words>"`. A record answers; no record (exit 1) means the reader is unknown for this topic, and the intake dialogue follows for what the other records leave open.
- **No inference from the wording, no self-rating.** An agent that inferred expertise from one request was right about one time in five, and a pasted jargon-heavy request fakes expertise; a person's own rating of his ability tracks his real ability at about r = .29. Tutors free to ask in a tutoring dialogue still detected none of their students' false beliefs.
- **Asking beats imagining.** Of 20 ratings their partner gave, people who had asked him predicted 8.60 correctly, people left to a strategy of their own 4.90, and people told to imagine his point of view 3.95.
- **A short deliverable, and a sub-agent's hand-back, take no intake.** There the text is written for a professional reader and explains in full, in parts he can skip: instruction with much assistance raised the learning of novices (d = 0.505) and lowered that of experts (d = −0.428), its authors advise giving the help when in doubt, and an answer pitched below the reader's level went with lower satisfaction on complex tasks.

## The intake dialogue

At most three turns, each one question card in the card form (`SKILL.md` § 5), asked at the start of the task, before any work on the deliverable.

1. **The probe.** Name four to six concrete things of the topic (a mechanism, a tool, a term) and ask which of them he already works with; he may mark several. Things and not levels: a self-rating is weak evidence (§ When the reader is unknown), while a probe on the first step of a task ranked knowledge almost as well as a full test (r up to .92).
   - bad: "How well do you know HTTP caching: beginner, intermediate or expert?"
   - good: "Which of these do you already work with: cache keys, expiry times, purge requests, edge rules?"
2. **The use, by what the probe showed.** He marked at least half: ask what he will do with the result. He marked fewer than half: ask what he has to be able to do after reading, with the same four uses as options.
3. **The depth, only when turns 1 and 2 leave it open**: the whole mechanism step by step, or what changed and what is his to decide.

- Stop as soon as the answers settle what to explain and how deep: one or two probing turns recovered a reader's level in most cases.
- Every option says what the deliverable will then contain: "then I leave out how the cache is keyed", where a bare label such as "expert" says nothing of it. A question whose answer would not change the deliverable is not asked (rule 4 of `references/rules.md`).
- Record the answers before writing: `records.py reader add --topic ... --holds ... --lacks ... --use ... --depth ... --basis "intake dialogue" --turns <cards asked>`.

## After the deliverable

- **The evidence stays whole.** People who had answered an assistant's clarifying questions accepted more of its wrong answers afterwards (52 % against 39 %), most of all in what the questions had covered. The list "Where to look" is not shortened for a reader who was asked, and what is unverified in a topic the intake covered is said in the story.
- **A later question corrects the record.** What the reader asks after the deliverable goes under `lacks` for that topic (`records.py reader add`), beside its line in the project's record of his questions (`SKILL.md` § 7). The word he used for a thing goes under `words`, and a word of the text he rejected or took in another sense under `barred`; the next list of terms reads both first (`references/explaining.md` § The terms).
- **Each long deliverable leaves a record of its exchange**, in the reader's private store beside the reader record, written in two steps:
  1. when it goes out, `records.py exchange add --topic ... --form text|page --opening said-back|accepted|corrected|none`, the last option saying how its opening was confirmed (`references/explaining.md` § The story);
  2. after the reader's first reply to the whole deliverable, `records.py exchange note <id> --reply acted|asked|corrected --asked "<what he asked>"`.

  The reply is one of three:
  - `acted`: he decided, answered or went on with no question about what the text says;
  - `asked`: he wanted to know what something in it means or what it left out;
  - `corrected`: he had taken another meaning than the one meant.

  `records.py exchange count` prints his counts, among them how often the first reply was `acted` after a confirmed opening and after none: the figures by which the owner of a session judges these rules on his own reading.
