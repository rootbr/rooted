# The reader record and the intake

A long explanation fits its reader only when the author holds valid information about what that reader knows. With such information experts' written explanations taught about half again as much (1.52 against 0.99 on a scale of 0 to 3) and drew half the follow-up questions; with random information they gained no more than with none (0.80). So before a deliverable that takes the page form the skill looks the reader up, asks when the record is empty, and never guesses.

## The reader record

- **One private file a person, outside every project** (`scripts/records.py reader`). The script refuses a file that a repository would track. The record is never copied into a project file, the project's ledger of answers or a deliverable for another addressee.
- **What a record holds**: a topic, what the reader holds about it, what he lacks, what he does with a result (`decide`, `defend`, `build`, `know`), the depth he wants (`mechanism`: the whole thing step by step; `change`: what changed and what is his to decide), the basis and the date.
- **Per topic.** Knowledge is recorded for a topic, never as one level for a person: outside their own field, experts searched the web like laymen, their differences generally under a tenth of a standard deviation.
  - bad: "reader: senior engineer, expert"
  - good: "topic: HTTP caching; holds: cache keys, expiry times; lacks: purge requests"
- **Dated.** Over five or more weeks of search logs, 31 to 49 % of non-experts used a field's vocabulary in a growing share of their queries. A record is read with its date, and an old one is confirmed by one question before a long deliverable rests on it.
- **Knowledge and use, no style.** Matching a presentation to the form a person says he prefers found no support in adequate tests; the record keeps what he knows and what he will do with the result.

## When the reader is unknown

- **The detector is the record.** Before a deliverable that takes the page form, that is, a report with a mechanism a figure shows or a decision among options, or an explanation for several readers (`references/media.md`), run `records.py reader find --topic "<the topic in the reader's words>"`. What the session's instructions say about its reader counts before the file. A record answers; no record (exit 1) means the reader is unknown for this topic, and the intake dialogue follows.
- **No inference from the wording, no self-rating.** An agent that inferred expertise from one request was right about one time in five, and a pasted jargon-heavy request fakes expertise; a person's own rating of his ability tracks his real ability at about r = .29. Tutors free to ask in a tutoring dialogue still detected none of their students' false beliefs.
- **A deliverable that goes out as text alone, and a sub-agent's hand-back, take no intake.** There the text is written for a professional reader and explains in full, in parts he can skip: withholding help from a novice cost more (d = 0.505) than redundant help cost an expert (d = −0.428), and an answer pitched below the reader's level went with lower satisfaction on complex tasks.

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

## After an intake

- **The evidence stays whole.** People who had answered an assistant's clarifying questions accepted more of its wrong answers afterwards (52 % against 39 %), most of all in what the questions had covered. The list "Where to look" is not shortened for a reader who was asked, and what is unverified in a topic the intake covered is said in the story.
- **A later question corrects the record.** What the reader asks after the deliverable goes under `lacks` for that topic (`records.py reader add`), beside its line in the project's record of his questions (`SKILL.md` § 7).
