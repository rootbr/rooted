# Run 2 — notes

The seed is the hash of the commit that registered this run on the branch `pre-squash-scientific-method`, `2abcbd4c4b137be74e9e9cdccdd10948ca9d5972`; the draw shares no rule with run 1.

```
python3 -I evals/kind-agreement/kind_agreement.py sample --root <repository> --seed 2abcbd4c4b137be74e9e9cdccdd10948ca9d5972 --out evals/kind-agreement/sample-run-2.json
python3 -I evals/kind-agreement/kind_agreement.py brief --root <repository> --sample evals/kind-agreement/sample-run-2.json --method references/method.md --protocol evals/kind-agreement/protocol.md --out evals/kind-agreement/runs/run-2/brief.md --wrap 1500
```

The draw holds `R-50`, whose provenance line carries a record since the audit rule was rewritten. After the draw and before the readers ran, the builder was changed to cut a rule line before its record, so no reader is handed a kind; the change removes an answer from the brief and adds nothing to it. The two readers were dispatched in one message, each in its own context, each given the path of `brief.md` and the path of its own answer file.

`score.txt` is the output of `kind_agreement.py score`: 29 of 30, kappa 0.94. The readers parted on `API-30`, whose line names local runs and calls them corroboration only: reader a took the runs for a test, reader b took the documents for the ground. Each reader also named the rules it found hardest — reader a: R-62, API-30, PY-152, TST-04, R-42, DSN-19; reader b: R-62, R-50, R-42, API-30, PY-152, TST-04, DSN-19.

`verdict-H-02.json` is the verdict of a second reader of the record on the hypothesis line as it stood on that branch with both runs and the standing `supported`: all seven rules hold. The main line holds the six commits of that branch as one, so there the line stands as a hypothesis. That reader was given the output of the record check, `0 error(s)`, for the order of hypothesis and result. The registering commit was made once; history cannot show that no earlier attempt at it was discarded, and that rests on the author's word.
