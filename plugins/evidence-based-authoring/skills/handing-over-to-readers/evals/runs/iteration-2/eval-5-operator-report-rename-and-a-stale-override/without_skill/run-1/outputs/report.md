# Rename `server.timeout` → `server.timeoutMs`: report

**Risk:** if this ships as it is, production loses its 10000 ms timeout. `deploy/prod.properties:3` still sets `server.timeout=10000`, and the code no longer reads that key. Nothing fails. The server just runs with a shorter timeout.
**What you do:** pick one of the two options at the end. The production file belongs to the operations team, so I didn't change it.
**Not done:** `deploy/prod.properties`. There is also no test that loads the deployment file.
**Wrong if:** something outside `ServerConfig` still reads `server.timeout`. I only checked the files in this fixture.

Status: tests pass. `test.log`: `Tests run: 2, Failures: 0, Errors: 0, Skipped: 0`, `BUILD SUCCESS`, `exit code: 0`.

## What changed
- `src/main/java/app/ServerConfig.java:16`: the code reads the new key, `properties.getProperty("server.timeoutMs")`. If the key is missing it uses `DEFAULT_TIMEOUT_MS = 5_000` (line 7).
- `config/app.properties:3`: `server.timeoutMs=3000`.
- `src/test/java/app/ServerConfigTest.java`: one test reads the new key (3000) and one checks the default (5000). Neither test touches the deployment file. That's why the tests pass while production would break.

## What happens in production
- `deploy/prod.properties:1` says `# Managed by the operations team. Changes go through them.` Line 3 still has `server.timeout=10000`.
- The class comment (`ServerConfig.java:5`) says the deployment file overrides `app.properties`. After the rename, the 10000 is ignored, and production gets either 3000 (from `app.properties`) or the 5000 default. I didn't check which one, because the code that merges the two files isn't in this fixture. Either way, the timeout is no longer 10000.

## Your decision
The fact: the production timeout drops from 10000 ms to 3000 or 5000 ms unless the old key is still read or the operations team renames it before this release.

The options:
- **A. Read the old key as a fallback.** `ServerConfig` reads `server.timeoutMs` first and falls back to `server.timeout`, with a test for that. Consequence: deploying is safe whatever order things happen in. The cost is a temporary fallback that someone has to remove after the operations team renames the key.
- **B. Ask the operations team to rename the key in `deploy/prod.properties` first.** Consequence: the code stays clean. But this change can't be released until their edit is live, and if the order slips, production silently gets the shorter timeout.

**Should I add the fallback to the old key (A), or will you have the operations team rename it before the release (B)?**
