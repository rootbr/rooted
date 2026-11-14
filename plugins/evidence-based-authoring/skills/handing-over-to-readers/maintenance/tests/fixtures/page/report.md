The task was to stop a re-uploaded picture from showing its old thumbnail. That is fixed: a re-uploaded picture now gets a fresh thumbnail, and the tests pass. One thing is left. Thumbnails cached before the change stay wrong until they expire, for up to a day. You decide whether we purge the cache now or let them expire.

## How it broke

A thumbnail is stored in the cache under a key. The key was the picture's number alone. A re-uploaded picture keeps its number. So the cache answered with the thumbnail of the old file. Now the key also carries a version, and the version grows with every upload.

```
picture 42, uploaded twice     key before      key now
upload 1                       thumb:42        thumb:42:v1
upload 2                       thumb:42        thumb:42:v2   <-- a new key, so a fresh thumbnail
```

## What is left

Thumbnails cached before the change still sit under the old keys. They stay wrong until they expire. That takes up to a day. About three pictures in a hundred were re-uploaded during the last day. The load test was not run, so I do not know what the new key costs at peak load.

## What to decide

There are two ways.

```diff
  1. Purge the cache now
+ the wrong thumbnails are gone at once
- every gallery page is slow for about twenty minutes

  2. Let the old entries expire
+ nothing slows down
- re-uploaded pictures show an old thumbnail for up to a day
```

I would purge at night, when twenty slow minutes cost least.

Purge now or let them expire?

## Where to look

- the key with the version: `src/cache/ThumbKey.java:23` `":v" + version`
- how long an entry lives: `config/cache.yaml:8` `ttl: 24h`
- the test that fails when the change is reverted: `ThumbCacheTest#reuploadMissesCache`
- the tests: 9 of 9 passed, `./gradlew test` exit 0
