The task was to rename the server timeout setting so that its name shows milliseconds. That is done in the code and in our settings file, and both tests pass. One thing is left. The operations team's production file still sets the timeout under the old name. The code no longer reads that name, so after the release production waits three seconds instead of ten. You decide whether operations rename their line first, or the code keeps reading the old name for a while.

## What changed

The code now reads only the new name. When the name is missing, it falls back to five seconds. Our settings file gives three seconds under the new name. The tests check both cases. They do not read the production file.

## The production file

The operations file sets ten seconds under the old name. Nobody reads that name now. So production gets our three seconds. I left that file alone, because changes to it go through operations.

```
                    the code reads   the production file sets   timeout in production
before the rename   timeout          timeout = 10000            10 s
after the rename    timeoutMs        timeout = 10000            3 s, from our file   <-- silent drop
```

## What to decide

There are two ways.

```diff
  1. Operations rename their line to the new name before the release
+ one name everywhere, nothing to clean up later
- the release waits for the operations team

  2. The code also reads the old name, and the old name wins while it is set
+ the release can go now, and production keeps ten seconds
- two names live in the code until operations rename their line and I remove the old one
```

I would ask operations first: it is one line for them, and nothing is left to remove later.

Do you ask operations to rename their line, or do I make the code read the old name too?

## Where to look

- the code reads only the new name: `src/main/java/app/ServerConfig.java:16` `properties.getProperty("server.timeoutMs")`
- the operations file still has the old name: `deploy/prod.properties:3` `server.timeout=10000`
- our file with the new name: `config/app.properties:3` `server.timeoutMs=3000`
- the tests: 2 of 2 passed, `./run-tests.sh` exit 0, `test.log:5` `exit code: 0`
