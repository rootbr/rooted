# The retelling measurement

Does a step-by-step retelling of the first part of an explanation mark a step the text leaves out, where answers to the reader's questions do not? The claim and its threshold stand in `../../maintenance/pending-evidence.md` as `H-Explaining-the-first-part-of-an-explanation-is-read-by-a-person-of-the-team-and-retold-cold-before-the-rest-is-written-a-retelling-marks-a-missing-step`.

## The texts

`plants.json` names four first parts, each an opening and one part that gives a mechanism whole in five steps, a sentence and a pseudocode line a step. Each has one variant, `no-step`: one step is taken out, its sentence and its line, while the sentences after it still use what the step produced. `python3 ../cold-read/plant.py plants.json` writes the variants; with `--blind DIR` it also writes copies whose names hide which is which.

## The arms

A fresh reader reads one text and one questions file. A reader is an agent of the type `brief-worker` that takes the instructions of the plugin's cold reader, copied to `runs/<iteration>/prompt.md`, as its own, opens the text and the questions file and nothing else, and writes its object to a file, where those instructions deliver it as the message. `runs/README.md` names the reader's model, its effort and the Claude Code version of every iteration. A rerun elsewhere gives `runs/<iteration>/prompt.md` to any agent that can read the two files and write `cold.json`.

- `retell`: `questions-retell.json`, four questions and the request to retell the mechanism by its steps;
- `questions`: `questions.json`, the same four questions alone.

Every text is read three times in each arm: 12 readings of a text with a step removed and 12 of an intact text in each arm, 48 in all.

## What counts

`python3 ../grade_retelling.py plants.json runs/<iteration>` checks every reading with `../../scripts/check_cold_read.py`, the `retell` arm against the five steps of its case.

- A removal is caught in the `retell` arm when the check of the retelling fails, fewer than five steps standing or a step with no sentence behind it, and passes on the intact text of that case in that round. Five is the number of steps of the author's rule: the text read has lost a step its author knows.
- A removal is caught in the `questions` arm when a question is left without a full answer that is answered in full on the intact text of that case in that round.
- A failed check of the retelling on an intact text, and a question left without a full answer on it, is a false alarm.
- The gaps a reader lists decide no outcome. The grader counts the readings that list one, with a step removed and intact, beside the outcomes: the skill's check prints the gaps and exits 0, and on a text outside this set a reader listed two gaps where no step was missing.

## The threshold, fixed before the first reading

The claim holds when the share of removals caught in the `retell` arm is at least 40 points above the share caught in the `questions` arm, by a one-sided Fisher exact test at p < 0.05, and the `retell` arm raises a false alarm on at most 3 of its 12 intact readings. Any other outcome goes against it.

## Runs

`runs/<iteration>/<arm>/round-<n>/<case>--<variant>/cold.json` holds each reader's answer, `runs/<iteration>/prompt.md` the reader's instructions as they stood, and `runs/<iteration>/grading.json` the grader's output.
