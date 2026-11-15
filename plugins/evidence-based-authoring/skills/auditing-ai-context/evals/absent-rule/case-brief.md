# Brief for the writer of one test case

You write one test case for a check of prose: two versions of a short design note and a list of the sentences you planted in the second version. This brief is all you read in the repository. You write exactly three files, all into the case directory the dispatch names.

## The two documents

The dispatch gives you a domain, for example "pagination of a public REST API".

1. Invent a team's internal design note in that domain, and one rule or design choice of it, **rule A**, that the team later replaces by **rule B**. Both are concrete: a reader could act on either.
2. `old.md` is the note while rule A was in force: 60 to 90 lines of Markdown with a title, several headed sections, paragraphs, lists and at most one table. It states rule A in two to four sentences in one section, and other sections rely on it.
3. `new.md` is the note after the team moved to rule B, of the same length. The sections that rested on rule A are written anew for rule B; the other sections may stay as they were. `new.md` is written for a reader who has never seen `old.md` and has never heard of rule A. Apart from the planted sentences described below, it says nothing of what rule A was, nothing of a change having happened, and uses none of rule A's own names.
4. Write each paragraph and each list item on one line. Write in English.

## The ten planted sentences

Plant ten sentences in `new.md`, each where it reads as a natural part of the note. Nothing marks them.

- **Three of the class `trace`.** A sentence that a hurried author, with `old.md` still in mind, leaves in `new.md`: it denies what rule A required, corrects rule A, excuses the reader from it or sets the present design against it, while `new.md` nowhere tells its reader what rule A was. Record the `form` of each. One is `named`: it uses a name that only rule A had — a term, a role, a number of its own. Two are `quiet`: they argue with rule A in the ordinary words that `new.md` also uses for its present subject, and use no name of rule A's own.
- **Two of the class `foil`.** A sentence that describes something of the present design by setting it against an alternative, a requirement or a misreading that neither `old.md` nor `new.md` presents anywhere: a contrast invented for emphasis.
- **Three of the class `licensed`.** A sentence that denies or contrasts something which `new.md` itself has told its reader about in an earlier sentence — an option some systems take, a rule in force elsewhere, a view someone holds, a fact that makes a reader expect it. That earlier sentence is the licence: ordinary text of `new.md`, standing before the planted sentence and not itself planted. Record it word for word.
- **Two of the class `plain`.** A sentence that says what the described thing does not do, must never do or does without, or what happens when something is absent: a guarantee, a prohibition, a limit or a default that a user of the thing relies on. It sets the thing against no other design, rule or view, and it touches nothing of rule A.

Every planted sentence:

- is one complete sentence of 8 to 35 words, begins with a capital letter and ends with a period;
- stands only in a paragraph or a list item, and the sentence before it in the same paragraph ends with a period;
- holds no colon, no semicolon, no question mark, no inline code and no abbreviation written with a period;
- stands in `new.md` exactly once, word for word as in `labels.json`, and nowhere in `old.md`.

Vary the wording from sentence to sentence, the way different authors would phrase such things.

## `labels.json`

```json
{
  "topic": "<the domain>",
  "old_rule": "<rule A in one sentence>",
  "new_rule": "<rule B in one sentence>",
  "planted": [
    {"id": "p01", "class": "trace", "form": "named", "text": "<the sentence, word for word>"},
    {"id": "p02", "class": "trace", "form": "quiet", "text": "<…>"},
    {"id": "p03", "class": "trace", "form": "quiet", "text": "<…>"},
    {"id": "p04", "class": "foil", "text": "<…>"},
    {"id": "p05", "class": "foil", "text": "<…>"},
    {"id": "p06", "class": "licensed", "text": "<…>", "licence": "<the earlier sentence of new.md, word for word>"},
    {"id": "p07", "class": "licensed", "text": "<…>", "licence": "<…>"},
    {"id": "p08", "class": "licensed", "text": "<…>", "licence": "<…>"},
    {"id": "p09", "class": "plain", "text": "<…>"},
    {"id": "p10", "class": "plain", "text": "<…>"}
  ]
}
```

## Check before you report

Run, from the repository root:

```
python3 -I plugins/evidence-based-authoring/skills/auditing-ai-context/evals/absent-rule/absent_rule_eval.py validate <case directory>
```

It prints one line per defect of form. Correct the files until it exits 0. Then report in at most five lines: the domain, rule A and rule B in a clause each, and the exit status of the check.
