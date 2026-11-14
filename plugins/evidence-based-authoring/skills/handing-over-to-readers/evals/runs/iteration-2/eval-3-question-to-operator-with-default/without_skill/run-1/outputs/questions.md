# Moving the limit settings into a config file: one question before I continue

## Already decided, no answer needed

**Config file location: `config/limits.yaml`.** I chose this because the project's other 3 configs are in `config/`, and `resources/` holds only `logback.xml`. This is easy to undo: moving the file later takes one path edit and one commit. If you want it in `src/main/resources/limits.yaml`, say so and I'll move it.

## Your decision needed: the `legacy_limits` table

**Fact:** After the move, the code no longer reads `legacy_limits`. The table still holds 14 000 rows of limit history for 2019–2024. The test bench has no database backup, so deleting the table there can't be undone.

**What your answer changes:**
- **Keep it:** the migration gets one line, `-- legacy_limits kept`. All 14 000 rows stay, and we can still drop the table later.
- **Delete it:** the migration runs `DROP TABLE legacy_limits`. The 14 000 rows are gone for good and 0 rows of history remain.

**I didn't decide this myself because** deleting it is permanent. I'd suggest keeping it for now. That costs one comment line, and dropping the table stays possible later.

**Should the migration delete `legacy_limits` (14 000 rows of 2019–2024 history, no backup on the test bench) or keep it?**
