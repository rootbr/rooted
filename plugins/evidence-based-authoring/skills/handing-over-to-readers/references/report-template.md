# Report template for the operator

A report is a story, its pictures and a short list of where to look. Its opening paragraph gives the whole matter. The story tells a colleague who was away what the task was, what happened and what is needed from him; it is written for the ear, so the same text is read in the chat and voiced on a page (`references/media.md`). Each part that has something to show carries one picture, drawn here as pseudographics. The list lets him check it. `scripts/check_report.py --profile operator` checks this form.

````markdown
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
````

Rules of the form:

- **The story** is plain prose written for the ear (`references/explaining.md` § The story): short sentences of one claim, a phrase that opens each part. It carries no path, identifier, file name, command or exit code, no labels and no bold.
- **The opening** is one paragraph of three to five sentences without a heading and without a picture: the task in the reader's words, how it ended, the problem with its cause, what is needed from him. Every later part stands under a heading of one to four words in the reader's words.
- **A picture** follows the sentences of a part that has something to show (`references/explaining.md` § The pictures): the mechanism with its values, the failure, the options. It is the picture the page draws, here in pseudographics, within 100 columns.
- **A decision that is the reader's** closes the story: a sentence that counts the options, their picture with one block per option, the author's choice with its reason, one question last.
- **What was not done or not verified** is a sentence of the story or a cost line of an option, and only when it changes what the reader does or trusts.
- **Where to look** is the last part: at most five lines, each a plain name of what is there and its `path:line` anchor, with the fragment of the line when the line proves something. The checks that ran stand here with their exit codes, taken from their output and never from memory.
- **Nothing else.** A decision taken by default that he may want to overturn is one sentence of the story; the decision registry (`SKILL.md` § 7) holds the rest.
- **Length.** A small change takes twenty to thirty short sentences, about two hundred words, and two or three pictures; the check script warns about an opening of fewer than three sentences, past twenty words in a sentence and past 300 words of prose.
