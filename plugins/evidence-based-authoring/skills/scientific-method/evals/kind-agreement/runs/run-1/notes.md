# Run 1 — notes

The brief of this run was built from the committed draw and then re-flowed, so that a file reader shows every line whole:

```
python3 -I evals/kind-agreement/kind_agreement.py brief --root <repository> --sample evals/kind-agreement/sample.json --method references/method.md --protocol evals/kind-agreement/protocol.md --out evals/kind-agreement/runs/run-1/brief.md
```

Lines longer than 1500 characters were broken at a space; the text is otherwise the builder's output, character for character apart from that white space. The two readers were dispatched in one message, each in its own context, each given the path of `brief.md` and the path of its own answer file and nothing else of the run.

`score.txt` is the output of `kind_agreement.py score` on the two reader files. `verdict-H-02.json` is the verdict of the reader of the record on the hypothesis line as it was first written after this run, with the standing `supported` and `fit: direct`; that form of the line was never committed, because the verdict failed it on rules 5 and 6. The builder has since taken the option `--wrap`, which breaks a line at its last space at or before the width; the brief of this run was broken by hand at the last space before 1500, so its line breaks may differ by a character from a rebuilt one.

