# Moving the limits into a config: one decision is yours

I chose the location of the configuration file myself, and the deletion of the legacy table `legacy_limits` I leave to you, because on the test bench it is irreversible.

## Decided without you: `config/limits.yaml`

I put the limits file in `config/limits.yaml`. The three other configs of the project already live there, while `src/main/resources/` holds only `logback.xml`. If you want it in `resources/`, the move costs one path edit and one commit.

## Your answer is needed: whether to delete `legacy_limits`

After the move the code does not read the table. It holds 14 000 rows of limit history for the years 2019–2024. There is no database backup on the test bench, so `DROP TABLE` erases this history with no way to bring it back.

| Option | What the migration does | What remains on the test bench |
|--|--|--|
| Keep (recommended) | adds one line `-- legacy_limits kept` | the table and 14 000 rows of history |
| Delete | `DROP TABLE legacy_limits` | 0 rows of history, nothing to restore from |

The cost of error is asymmetric. An extra table costs one migration later, when the history has been saved or turns out to be unneeded. A deletion by mistake loses five years of history for good.

Until there is an answer, I continue with the option "keep". I will run the deletion only on your explicit answer.
