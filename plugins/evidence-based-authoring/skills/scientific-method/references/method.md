# The method

## Contents

- Kinds of statement
- Standings of a claim
- The seven rules and their check questions
- A claim about one event
- Acceptance

The scientific method judges a claim about how the world works by its test. The claim is stated so that an observation could refute it. It is put to a test that would have found the error, had there been one. Anyone can repeat the test, or open its description, and see the same result. The claim is accepted to the degree, and under the conditions, that the test supports. A new test can revise it.

A claim of any origin is judged the same way: a paper, practice, a model and one's own guess are equal as origins, and a test made in this repository counts the same as a published one.

Three kinds of statement rest on grounds of their own. A decision says what we want. A definition says what we call a thing. A norm says what an accepted document prescribes. Each is presented as what it is. A rule of a skill is a prescription, and a prescription takes two premises: a goal, and the claim that the technique serves the goal. The goal is the owner's decision; the claim is what the method examines.

The seven rules below are a convention this repository adopts. They hold what the main lines of the philosophy of science share, and they apply to every statement alike.

## Kinds of statement

| Kind | What it is | What it rests on | Example |
|--|--|--|--|
| decision | a choice: a goal, a priority, a taste, a threshold | the owner's word | "figures on a page are calm" |
| definition | the name of a thing | agreement | "a card is one checkable rule" |
| norm | what an accepted document prescribes: a standard, a specification, a regulation | the document, opened, with its issuer and version | "exit status zero means success" |
| claim | a statement about how the world works | a test | "with this paragraph the agent reads the file before editing more often" |

A norm shows that a practice is accepted; whether the practice works better is a separate claim. A statute and an industry regulation are norms. A logical inference is worth what its premises are worth.

## Standings of a claim

| Standing | What it is | Where it goes |
|--|--|--|
| opinion | no observation is named that would refute it | stays out of the rules |
| hypothesis | the refuting outcome is named, and the claim awaits its test | the list of hypotheses |
| supported | it passed a test that could have refuted it | a rule, with the bounds of its test |
| law | independent tests under varied conditions support it | a rule with wide bounds |
| leading | for a claim about one event: a trace on record tells it from every named rival | a record that holds for that event and against those rivals |
| contested | the tests disagree and no tested condition separates them | the list of hypotheses, both sides recorded |
| refuted | a repeatable test within the same bounds went against it | withdrawn; the record stays |

A fact is the material of a test: an observation anyone can repeat or open. The result of a run is a fact; a conclusion drawn from it is a claim.

## The seven rules

### 1. Facts apart from decisions

Every statement names its kind: decision, definition, norm or claim. Each kind is presented as itself: a taste as a decision, a norm as accepted practice, and only a tested claim as a finding. Check question: is this about the world, about our choice, about a name, or about what a document prescribes?

- bad: the house taste "figures on a page are calm" written as "calm figures are read faster".
- good: the taste recorded as the owner's decision, and "calm figures are read faster" as a hypothesis.

### 2. Refutability

A claim names what is compared with what, by which measure and under which conditions, and the outcome that would refute it; a claim that names none is an opinion by the table of standings. Check question: which result would make us give it up?

- bad: "short functions are better".
- good: "functions under forty lines draw fewer defect reports per line than longer ones in the same repository; an equal or higher rate refutes it".

### 3. Severity of the test

Only a test that could have come out against the claim supports it. A test of a neighbouring question, with another comparison or another measure than the claim names, could not have come out against the claim, so it is kept beside the claim and supports nothing. A claim about the benefit of a technique takes a comparison with the same work done without the technique, and enough repetitions to tell the effect from chance. How many repetitions suffice is decided before the test, by the cost of an error. A result that compares shares names its test and gives its p-value or interval. A test supports a claim about a property only when its measure follows that property, and the record says what checked the measure: a probe changed in a known direction, labels made by a person, or the measure being the very quantity claimed. An experiment that intervenes is more severe than an observation of cases as they came. Check questions: had the claim been false, would the test have shown it? Does the measure move when what the claim is about changes?

- bad: "ten runs with the paragraph all passed" — the runs without it were never made.
- good: "nine of ten runs passed with the paragraph and four of ten without it; a one-sided exact test gives p = 0.03".
- bad: a study that compared closed with open questions about a consent form stands as the test of a claim that retelling a mechanism finds a missing step.
- good: the same study kept beside the claim as a neighbouring question, and the claim waiting for its test.

### 4. Reproducibility

Another person can repeat the test. A test of our own lives in the repository and runs by a command. Someone else's test is accepted without repeating it once the source is opened and the test is found in it: the comparison, the measure, the sample and the result are in view. A source that passed peer review is accepted by its abstract, and the record says that the abstract alone was seen. The support comes from the test itself, whoever its author; peer review settles only how much of the source is read. Check question: would another person, following the record, see the same?

- bad: "a paper at a major venue shows it", and the paper was never opened.
- good: the paper is open, and its two groups, its measure, its sample and its number are read from the results section.

### 5. Bounds of transfer

A supported claim holds for the conditions of its test: who, what, which version. Beyond those conditions it is a hypothesis again. Applying it more widely is a decision, marked as a transfer. Check question: does the place where the rule is applied match the place where it was tested?

- bad: a result on students reading pairs of sentences stands, with no mark, behind a rule for engineers reading reports.
- good: the same result stands there marked as a transfer, with the difference in readers and texts named.

### 6. No fitting

The prediction, the measure and the threshold are recorded before the test. The record holds every run, the failed ones included. The observation a hypothesis grew from is its origin, and a later observation is its test. A condition added to save a refuted claim is itself a hypothesis, and it predicts something new. Check question: what was recorded before the result was seen?

- bad: after a failed run the claim becomes "it works except on long files" and keeps its standing.
- good: "it fails on long files" enters as a new hypothesis with a refuting outcome of its own.

### 7. Revision

A standing follows the tests and moves in both directions; the strongest standing is still open to a new test. A test that went against the claim is recorded and stays recorded. A claim is refuted by a repeatable result; a single failure is recorded and waits for its repetition. A run whose prompt, stand or judge failed the check made of it tested its apparatus and not the claim: it is recorded as a run, with the check it failed, and the standing stays where it was. Whether a run failed its checks is judged for each claim it is offered to: one run can test one claim and leave another untested. Check question: what changes in the record if a new test goes the other way?

- bad: after one failed run the rule is deleted together with its record.
- good: the failed run is recorded, and a second failure under the same conditions moves the standing to refuted.
- bad: a run whose judge read no reply, its parser failing on every one, is counted as the second failure, and the claim becomes refuted.
- good: that run is recorded with the check its judge failed, the standing stays, and the next run that passes its checks counts.

A claim about a model's behaviour — its measure is what a language model, or an agent running on one, does — at the standing `supported` or `law` also carries the term at which its record is read again: the retirement of the model version its test or bounds name, or, where they name none, a date twelve months after the latest run of its tests, the source's date standing in for runs it leaves undated. The term comes whether or not a new test arrives. It is no test, so its coming moves no standing by itself: the record is read again with the check questions of rules 5 and 7 against the versions in service, and leaves the reading with a new term, the version of a new test or a date twelve months after the reading.

## A claim about one event

The seven rules above are written for a claim about what happens whenever its conditions hold, the first path of the acceptance below. A claim about one event — what caused one failure, what one change did, what one observed result means — takes the second path. The event happened once, so its test is a trace the event left, and the rules apply to it in this form.

- Rule 2. The claim names the event, the rival explanations it is weighed against, each by name, the trace that tells them apart — an observation the claim predicts and a rival forbids, or the reverse — and the outcome that would refute it.
- Rule 3. A trace supports the claim only when it would have looked different had a named rival been true; a trace every rival predicts as well supports none of them. Check question: had a named rival been true, would this trace look the same?
- Rule 4. The trace is kept where another person can open it — a log, a dump, a commit, a recording — and the record names the file.
- Rule 5. The claim holds for that event and against the named rivals. A rule drawn from one event is a new claim on the first path, a hypothesis until its own test.
- Rule 6. The observation that suggested the explanation is its origin. Its test is a trace looked for after the rivals and the prediction were written down: the hypothesis is committed before the result, by the same check as on the first path. Every rival considered and every trace examined stay in the record.
- Rule 7. A trace on record that tells the claim from every named rival gives it the standing `leading`. A new rival that the trace does not exclude returns it to `hypothesis`; a trace on record that goes against it makes it `refuted`.

The claim leaves this path once a script reproduces the event deterministically, its exit status differing with the cause and without it: it is then a claim about how a program behaves, and a test of one run gives it `supported`. An action taken to stop the damage before the cause is known is a decision, with its owner and its goal.

- bad: "the outage was caused by the queue overflow", recorded as a finding because the queue was full at the time.
- good: the same explanation recorded with its rival, "the database lock", and the trace that tells them apart, the lock wait time in the database log during the outage: the overflow predicts it at its usual level, the lock predicts it high before the queue filled.

## Acceptance

Every new statement takes one path.

```
a new statement: which kind is it?
├── decision ────► enters under its owner's name
├── definition ──► enters as an agreement
├── norm ────────► enters as a norm
└── claim about the world
    ├── about what happens whenever the conditions hold
    │   └── are the measure, the comparison, the conditions and the refuting outcome named?
    │       ├── no ───► opinion: stays out
    │       └── yes ──► hypothesis
    │           └── is there a test that could have refuted it, ours or someone else's?
    │               ├── no ──────────────────────────────► waits in the list of hypotheses
    │               ├── yes, the run failed its checks ──► the run recorded, the standing kept
    │               ├── yes, it held ────────────────────► enters as a rule with the bounds of its test
    │               ├── yes, it failed once ─────────────► waits, the failure recorded
    │               ├── yes, the tests disagree ─────────► contested: waits, both sides recorded
    │               └── yes, it failed repeatably ───────► refuted: the record stays
    └── about one event
        └── are the rivals, the trace that tells them apart and the refuting outcome named?
            ├── no ───► opinion: stays out
            └── yes ──► hypothesis
                └── is the trace on record, where another person can open it?
                    ├── no ─────────────────────────────► waits in the list of hypotheses
                    ├── yes, only the claim fits it ────► leading: holds for that event
                    ├── yes, a rival fits it as well ───► waits, the trace recorded
                    └── yes, it goes against the claim ─► refuted: the record stays
```

A claim tested in this repository passes through a hypothesis, a test of our own and a record in the repository. An opinion enters after it is recast: a test is named for it and it becomes a hypothesis, or the owner takes it as a decision and it is presented as a choice. A rule needed before its test exists enters the same way: it is in force as a decision, and its hypothesis waits in the list for its test.

The record of an accepted claim carries the statement with its measure, the refuting outcome, the test, its result, the bounds and the standing, and for a claim about a model's behaviour the term at which it is read again; `references/record-format.md` gives the fields. An independent reader answers the check questions of the seven rules, and a rerun confirms a test of our own.
