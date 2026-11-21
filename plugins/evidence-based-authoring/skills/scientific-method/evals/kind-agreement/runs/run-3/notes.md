# Run 3 — notes

The run that counts on the main line. The seed is the hash of the main-line commit that registered it, `fa0bdaf4f8d6bbd16b8987834eb8efe2d4ed6706`.

```
python3 -I evals/kind-agreement/kind_agreement.py sample --root <repository> --seed fa0bdaf4f8d6bbd16b8987834eb8efe2d4ed6706 --out evals/kind-agreement/sample-run-3.json
python3 -I evals/kind-agreement/kind_agreement.py brief --root <repository> --sample evals/kind-agreement/sample-run-3.json --method references/method.md --protocol evals/kind-agreement/protocol.md --out evals/kind-agreement/runs/run-3/brief.md --wrap 1500
```

The two readers were dispatched in one message, each in its own context, each given the path of `brief.md` and the path of its own answer file.

`score.txt` is the output of `kind_agreement.py score`: 30 of 30, kappa 1.00. Each reader named the rules it found hardest — reader a: D-04, D-06, C-E2, C-F3, META-09, DOC-01; reader b: D-04, D-06, DOC-01, C-E2, C-F3, META-09, ERR-09, R-76.

`reader-prompt.md` is the instruction reader a was dispatched with, taken from its harness transcript, with its closing block on the dispatching session's completion marker replaced by one line; reader b got the same text with its own file names. In the two call lists the call that wrote that marker is named and its command left out. `reader-a.calls.txt` and `reader-b.calls.txt` are the tool calls of each reader, in order, taken from the same transcripts: two reads of `brief.md`, one write of the answer file, the form check, the completion marker and the hand-back, and no other file opened. `verdict-H-02.json` is the verdict of the reader of the record: it held six rules and failed rule 4, because the readers' instruction and the list of what they opened were not kept; the three files above were added in answer, and `verdict-H-02-second.json` is the verdict of a fresh reader on the record with them.

The second reader of the record held all seven rules and asked one thing it could not see: under which agent definition the readers ran. They ran as the agent type `brief-judge` of the owner's Claude Code configuration; the protocol's section Readers and the record's `transfer` now say so. That reader also found the Bash calls of the two lists cut short; the lists were taken again with every command whole.

