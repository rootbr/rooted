The task was to upgrade the logging library to version 2. The old version is no longer supported. The build now takes the new version, and that is the whole change. But the new version writes the time of each log line in a new form. So the operations team's alert on errors no longer sees our error lines. 

## How the alert works

The operations team has an alert on errors. It fires for every log line that matches a pattern in their file. The pattern expects the old time form: local time, a space, a comma before the milliseconds. The new version writes the time in UTC, with a letter T and a dot. I ran their pattern on one error line written each way. It matched the old line and missed the new one.

```
before   2026-10-08 10:15:30,123 ERROR OrderService - payment declined    alert fires
after    2026-10-08T09:15:30.123Z ERROR OrderService - payment declined   no alert
                   ^           ^   ^
```

So if this ships as it is, our errors raise no alert at all. I did not touch the operations team's file. I did not build the project or run any tests.

## Where to look

- the library version: `fixtures/logformat/build.gradle:2` `logkit:2.0.0`
- the setting that keeps the old form, not set: `fixtures/logformat/src/main/resources/logkit.properties:2` `logkit.timestamp=legacy`
- the alert pattern: `fixtures/logformat/ops/alerts.conf:3` `,[0-9]{3} ERROR`
- the alert pattern on the samples: old line 1 match, new line 0 matches; on the new line alone grep exit 1
