# Model versions

The model versions that the field `review` of a record names, as `references/record-format.md` § Fields by kind gives it, and the date each is retired once its provider has announced it. `scripts/check_record.py` reads this file: a record whose version is retired on or before the day of the check is due to be read again, and a `supported` or `law` claim whose `scope` names a version of this list carries `review`.

One line per version: `- **<name>**`, then, separated by ` · `, `id: <the provider's identifier>`, and once the provider announces the retirement, `retired: <YYYY-MM-DD>` with `source: <the page that gives the date>`, the page written as code. A record names a version by its name or its `id`. Every other line of this file is free text.

- **Claude Opus 5.5** · id: claude-opus-5-5
- **Claude Sonnet 5.5** · id: claude-sonnet-5-5
- **Claude Sonnet 4.5** · id: claude-sonnet-4-5-20250929 · retired: 2026-11-30 · source: `https://platform.claude.com/docs/en/about-claude/model-deprecations`
