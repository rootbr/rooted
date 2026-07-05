---
title: Cross-file path references must be repo-relative with forward slashes; absolute paths must not appear
rule_id: R-42
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: high
---

# Cross-file path references must be repo-relative with forward slashes; absolute paths must not appear

## Thesis
Any path inside instruction prose ("see <file>", "edit <file>", "located at <file>") must be relative to the repo root or to the file the rule is written in, with forward slashes as separators — agents navigate the skill directory like a filesystem, and backslash paths break outside Windows. Absolute paths (`/Users/...`, `/home/...`, `C:\Users\...`) leak machine state into a portable artifact and break for every other user.

## Rationale
Skills and CLAUDE.md propagate across machines, branches, and contributors. An absolute path is a leaked constant — it cannot survive a `git clone` to a different `$HOME`. The same logic applies to a `~/projects/...` form when the rest of the file is repo-portable: prefer the form callers can copy verbatim into their own checkout.

## Example
```
bad:  Read /Users/dev/projects/rooted/skills/auditing/SKILL.md
good: Read plugins/evidence-based-authoring/skills/auditing-ai-context/SKILL.md

bad:  Settings: /Users/dev/.claude/settings.json
good: Settings: ~/.claude/settings.json   (only inside user-global CLAUDE.md)

bad:  Read reference\guide.md
good: Read reference/guide.md
```

## Limits
A `~/.claude/...` path is acceptable only inside a user-global CLAUDE.md, where the user's home is the intended target; elsewhere it is a leak and must be flagged. A path appearing inside a literal block that demonstrates a different concept (not an instruction to read or edit) is out of scope.

## Validator
Grep for `/Users/`, `/home/`, `/opt/`, `C:\`, and `~/`. For each hit inside instruction prose: if the path is inside the same repo as the file being audited, propose the repo-relative form; if it points at the user's home or another machine, flag it and ask whether the rule belongs in a user-level CLAUDE.md instead. Also grep for backslash-separated relative paths (`scripts\helper.py`) and propose the forward-slash form. Validator question: could this path be checked into git and still resolve correctly on a fresh clone in another developer's `$HOME` — on any OS?

## Patch output
When auditing a path in instruction prose that is absolute or machine-bound, emit one patch (`rule_id: R-42`, location of the path, severity high) proposing the repo-relative or symbol-based equivalent.

## Source
Verified hands-on experience: portable skills and CLAUDE.md files break on clone when they embed absolute paths. Anthropic, Agent Skills best practices — anti-pattern "Avoid Windows-style paths" (always forward slashes, even on Windows; agents navigate the skill directory like a filesystem).
