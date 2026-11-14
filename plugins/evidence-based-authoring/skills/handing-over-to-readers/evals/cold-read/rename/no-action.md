The task was to rename the server timeout setting so that its name shows milliseconds. That is done in the code and in our settings file, and both tests pass. One thing is left. The operations team's production file still sets the timeout under the old name. The code no longer reads that name, so after the release production waits three seconds instead of ten. 

## What changed

The code now reads only the new name. When the name is missing, it falls back to five seconds. Our settings file gives three seconds under the new name. The tests check both cases. They do not read the production file.

## The production file

Production loads our settings file and puts the operations file on top of it. I know this from a comment in the code; I did not see the loading itself. The operations file sets ten seconds under the old name. Nobody reads that name now. So production gets our three seconds. I left that file alone, because changes to it go through operations.

```
                    the code reads   the production file sets   timeout in production
before the rename   timeout          timeout = 10000            10 s
after the rename    timeoutMs        timeout = 10000            3 s, from our file   <-- silent drop
```

## Where to look

- the code reads only the new name: `src/main/java/app/ServerConfig.java:16` `properties.getProperty("server.timeoutMs")`
- the operations file overrides ours: `src/main/java/app/ServerConfig.java:5` `a deployment file overrides app.properties`
- the operations file still has the old name: `deploy/prod.properties:3` `server.timeout=10000`
- our file with the new name: `config/app.properties:3` `server.timeoutMs=3000`
- the tests: 2 of 2 passed, `./run-tests.sh` exit 0, `test.log:5` `exit code: 0`
