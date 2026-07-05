---
title: Static inventories of project state must be replaced by discovery commands
rule_id: R-45
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# Static inventories of project state must be replaced by discovery commands

## Thesis
Anything that enumerates project structure — directory trees, plugin catalogs, environment-variable dumps, dependency lists — must be replaced by a command or script that returns current state. The inventory rots on every change to the underlying state, and the file cannot detect the rot.

## Rationale
Context files that duplicate repository documentation are redundant. With all repo docs removed (`.md` files, `docs/`, examples), generated context files flip from net-negative to a +2.7% gain — the file only helps once it is the sole source instead of a stale copy. The same applies to any list the filesystem already answers: the enumeration rots on every state change, silently.

## Example
```
bad:
  ## Plugins
  - plugin-a
  - plugin-b
  - …17 more lines…
good:
  ## Plugins
  Run `./overview.sh plugins` to list current plugins.
```

## Limits
A *short* list is exempt when the file is the system-of-record for it — a single canonical README that nothing else generates. If the proposed discovery command does not yet exist, the patch must set `needs_human: true` and note that the command must be created and allow-listed in `.claude/settings.json`.

## Validator
Flag any sequence of ≥ 3 lines that enumerates files, directories, plugins, skills, env vars, ports, or dependencies. Validator question: is this list the system-of-record, or a cached copy of something the filesystem or build system already knows? If it is the system-of-record and short, keep it. If it is a cached copy, propose a discovery command that returns the current state.

## Patch output
When auditing an enumeration of project state that the filesystem or build already answers, emit one patch (`rule_id: R-45`, location of the enumeration, severity medium) replacing it with "Run `<command>` to view current <thing>"; set `needs_human: true` when the command must first be created and allow-listed.

## Source
Gloaguen 2602.11988 App. B Fig. 12 (with repo docs removed, generated context files flip to +2.7%; anchor moved from §4.2 in v2).
