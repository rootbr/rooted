The task was to upgrade the logging library to version 2. The old version is no longer supported. The build now takes the new version, and that is the whole change. But the new version writes the time of each log line in a new form. So the operations team's alert on errors no longer sees our error lines. You decide whether we keep the old time form on our side or the operations team changes its alert.

## How the alert works

The pattern expects the old time form: local time, a space, a comma before the milliseconds. The new version writes the time in UTC, with a letter T and a dot. I ran their pattern on one error line written each way. It matched the old line and missed the new one.

```
before   2026-10-08 10:15:30,123 ERROR OrderService - payment declined    alert fires
after    2026-10-08T09:15:30.123Z ERROR OrderService - payment declined   no alert
                   ^           ^   ^
```

So if this ships as it is, our errors raise no alert at all. I did not touch the operations team's file. I did not build the project or run any tests.

## What to decide

There are two ways.

```diff
  1. Keep the old time form with one setting in our config
+ the alert keeps firing, and nobody else has to change anything
- our logs stay in local time; I have not checked that the setting gives exactly the old line

  2. The operations team changes its pattern to the new form
+ logs move to UTC, which the new version intends
- until their change is live, errors raise no alert, so our release waits for them
```

I did not choose by default, because the second way is the operations team's file and their timing. I would take the first now and offer them the second later.

Keep the old time form, or ask the operations team to change the alert?

## Where to look

- the library version: `fixtures/logformat/build.gradle:2` `logkit:2.0.0`
- the setting that keeps the old form, not set: `fixtures/logformat/src/main/resources/logkit.properties:2` `logkit.timestamp=legacy`
- the alert pattern: `fixtures/logformat/ops/alerts.conf:3` `,[0-9]{3} ERROR`
- the alert pattern on the samples: old line 1 match, new line 0 matches; on the new line alone grep exit 1
