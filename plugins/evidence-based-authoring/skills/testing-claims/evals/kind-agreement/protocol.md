# Kind agreement — protocol

The test of hypothesis `H-02` of `maintenance/pending-evidence.md`: two readers who work independently from the method's definitions give the same kind to at least 24 of 30 rules of this repository.

## What is tested

The four kinds of `references/method.md` are definitions. This test asks whether they can be applied: whether two readers who share only the text reach the same kind for the same rule. A lower agreement means the definitions, as worded, do not separate the kinds, and a run that labels the existing rules would label them by chance.

## Sample

Thirty rules drawn by `kind_agreement.py sample --seed <seed>`, stratified over the four card corpora: ten audit rule cards, ten universal craft cards, five Python craft cards, five Java craft cards. Within a corpus the ids are ordered by the SHA-256 of the seed and the id, and the first ones are taken, so the draw depends on nothing but the seed and the ids. A draw file holds the draw: for each rule its id, its corpus, the path of its card and the path of its provenance map. Section Runs names the seed and the draw file of each run; a draw is committed before its readers run.

## What a reader gets

One brief, built by `kind_agreement.py brief --wrap 1500`, which breaks the long provenance lines at a space so that a file reader shows them whole: the section "Kinds of statement" of the method, the reading rule below, and for each rule its card's title, its card's Thesis and its provenance line. A reader sees nothing else: no answer of the other reader, and no record, since the builder cuts a rule line before its record.

## Reading rule

The kind of a rule is the kind of what the rule rests on, as its provenance line shows it.

- `claim`: the line names a test of the claim that the rule's technique works — a study with a measurement, a benchmark, a run of our own. A line that names both such a test and a document is a `claim`.
- `norm`: the line's ground is a document that prescribes or describes the practice — a standard, a specification, official documentation, a style guide, a rule of a static analyser.
- `decision`: the line's ground is the project's own choice — a house convention, the owner's word, the repository's rule.
- `definition`: the rule fixes what a term means and asserts nothing about what works.

## Readers

Two agents on Claude Opus 5.5 at effort `xhigh`, each in its own context and started without the project's instruction files, each given the same brief. A reader's task is one message, kept with the run as `runs/<run>/reader-prompt.md`: read the brief, decide the kinds, write the answer file, check its form. The runs so far dispatched it to the agent type `brief-judge` of the owner's Claude Code configuration, whose definition lies outside this repository: it tells an agent to work from its brief alone, with read-only git and without sub-agents. Another person repeats a run with any agent given that message under those conditions. A run that counts also keeps what each reader did, taken from the harness transcript and never from the reader's own report: `reader-a.calls.txt` and `reader-b.calls.txt` list every tool call in order, and a call that opens anything but the brief voids the run. Each reader writes one file, `runs/<run>/reader-a.json` or `runs/<run>/reader-b.json`:

```json
{"answers": [{"id": "<rule id>", "kind": "claim", "why": "<one clause naming the ground it saw>"}]}
```

## Measure, threshold, refuter

The measure is the number of the thirty rules to which both readers give the same kind, printed by `kind_agreement.py score` with Cohen's kappa beside it. The threshold, fixed before the run, is 24 of 30. Fewer than 24 refutes the hypothesis. One pair of readers makes one run, and every run stays under `runs/`.

## Bounds

These thirty rules, readers on the named model and effort, and the definitions as committed with this protocol.

## Runs

Runs 1 and 2 were made in a working history of six commits, kept on the branch `pre-squash-scientific-method`: there the hypothesis was committed before run 1, and run 2 was registered before its draw. The main line holds that work as one commit, so its history does not show their order, and on the main line they do not count. Run 3 is registered in that same commit and made after it.

- Run 1: seed `20261120`, draw `sample.json`. The two readers gave the same kind to 30 of 30 rules (`runs/run-1/score.txt`). The reader of the record then held rules 1 to 4 and 7 and failed rules 5 and 6 (`runs/run-1/verdict-H-02.json`): the scope reaches past the thirty rules and past the definitions alone, since the readers also had the reading rule above; and the reading rule and the draw had entered that history in one commit.
- Run 2: a replication that answered the second failure. Its seed is `2abcbd4c4b137be74e9e9cdccdd10948ca9d5972`, the hash of the commit that registered it on that branch, a value nobody could know while the registration was written, so the reading rule and the threshold stood in that history before the draw existed. Its draw is `sample-run-2.json`. The readers gave the same kind to 29 of 30 rules (`runs/run-2/score.txt`), and a second reader of the record held all seven rules (`runs/run-2/verdict-H-02.json`).
- Run 3: the run that counts on the main line. Its seed is the full hash of the main-line commit that holds this section, a value nobody can know while the section is written, so the hypothesis, the reading rule and the threshold stand in the main line's history before the draw exists. Its draw is `sample-run-3.json`; the readers, the measure and the threshold are those of run 1. The readers gave the same kind to 30 of 30 rules (`runs/run-3/score.txt`).
