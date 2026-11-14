The task was to upgrade the logging library to version 2. The old version is no longer supported. The build now takes the new version, and that is the whole change. You decide whether we keep the old time form on our side or the operations team changes its alert.

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
