# Moving the limits into a config: deleting legacy_limits awaits an answer, the file location is chosen

**Risk:** high in one step: deleting `legacy_limits` erases 14 000 rows of limit history, and there is no database backup on the test bench.
**From the reader:** answer the question on `legacy_limits`; the location of the configuration file is chosen by default and is overturned by one edit.
**Not done:** the move of the limits and the migration have not started; I did not open the project code or the test-bench database, the numbers are taken from the task context.
**Wrong if:** the limits must travel inside the built jar rather than lie beside it; then the file location is `src/main/resources/limits.yaml`.
**Status:** not-run; no check was run, the migration awaits the answer to the question.

## Question

- The table `legacy_limits` is not read by the code after the move, but it holds 14 000 rows of limit history. The history covers the years 2019–2024. There is no database backup on the test bench, so deletion is irreversible. The answer changes the migration: with "keep" it adds the line `-- legacy_limits kept`, with "delete" it runs `DROP TABLE`. Only you know whether anyone outside the code needs this history. Delete the table with a migration or keep it?

| Option | What the migration does | Cost of error |
|--|--|--|
| Keep (recommended) | adds the line `-- legacy_limits kept`; 14 000 rows of history remain | an extra table in the schema; deleting it later is one separate migration |
| Delete | runs `DROP TABLE legacy_limits`; 0 rows of history remain | 14 000 rows are lost with no way back, there is nothing to restore them from |

Recommendation: keep. Basis: a kept table can be deleted later with one migration, a table deleted without a backup cannot be brought back.

If you choose deletion, I will repeat this consequence and run `DROP TABLE` only after a typed confirmation.

## Default decision

- The limits configuration file is `config/limits.yaml`. Basis: the three other configs of the project live in `config/`, while `src/main/resources/` holds only `logback.xml`. The decision is reversible: moving the file later costs one path edit and one commit. The decision is overturned by a requirement to keep the limits inside the jar, on the classpath.

## Internal

- How the three configs from `config/` are loaded, I did not check; the choice of location rests only on where they lie.
- The decision line on the file location and the answer to the question on `legacy_limits` go into the project's decision registry.
- The card for AskUserQuestion lies alongside, in `question.json`.
