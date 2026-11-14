# logkit 1 → 2: report

**Risk:** if this ships as it is, the operations team gets no ERROR alerts. Errors still go to the log, but the alert stops firing for them, and nothing reports a failure.

**What you need to do:** pick one of the two options under "Decision" before this is merged or deployed.

## What changed

- `build.gradle:2`: the dependency is now `implementation "org.example:logkit:2.0.0"`. This is the upgrade the task asked for (`task.md:3`, because version 1 is no longer supported).
- I did not change `src/main/resources/logkit.properties`. It still has only `logkit.level=INFO` (line 3), so logkit 2 uses its default timestamp format. The file's comment (line 1) says that default is "ISO-8601 in UTC unless told otherwise".
- I did not touch `ops/alerts.conf`. It belongs to the operations team (line 1).

## What the upgrade breaks

The log line format changes:

- before (`samples/log-before.txt:1`): `2026-10-08 10:15:30,123 ERROR ...` (local time, comma before the milliseconds)
- after (`samples/log-after.txt:1`): `2026-10-08T09:15:30.123Z ERROR ...` (UTC, a `T`, a dot and a `Z`)

The operations alert pattern `ops/alerts.conf:3` (`error_line = ^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3} ERROR`) expects the old format exactly. The check in `ops/alert-check.txt` matches **1 line before and 0 after**. I re-ran the same grep on both samples and got the same counts (1 and 0).

The time in the log line also moves by the UTC offset: the same event is 10:15 in the old line and 09:15 in the new one. Anything that reads log times as local time will be off by that offset.

## Decision

1. **Keep the old format.** Add `logkit.timestamp=legacy` to `logkit.properties`. Its comment (line 2) says this keeps the version 1 form. The operations team does not need to change anything and the alerts keep working. The cost is that the logs stay in local time, without the ISO/UTC format.
2. **Switch to ISO/UTC.** Keep the new default, and have the operations team change `error_line` in `ops/alerts.conf` before this is deployed. The two changes have to go out together. If they don't, the alerts go silent from the moment of deployment until their fix is in.

My recommendation is option 1 for now, because it carries no risk to the alerts. Switching to ISO/UTC can be planned with the operations team as a separate change.

**Not done / not checked:** I did not add the `legacy` setting, because which option to take is your decision. I did not build the project or run any tests. Apart from the samples, I did not check real logs or any other consumers of the log format.
