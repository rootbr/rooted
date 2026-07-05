---
title: The skill body carries concrete routing-signal vocabulary, not abstract phrasing
rule_id: R-03
applies_to_target: [skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# The skill body carries concrete routing-signal vocabulary, not abstract phrasing

## Thesis
Modern routers scan the body, not just the description. The body should name the tools the agent uses, trigger verbs, file types, and negative cases in concrete tokens; a body of abstract phrasing forfeits routing signal.

## Rationale
Removing the body from routing costs 31–44 pp Hit@1, and a body with no concrete vocabulary forfeits the same signal. The router's encoder matches concrete tokens (`gradle`, `pytest`, `.docx`, `RFC 2119`), not abstractions like "optimize agent behavior". The catalog-wide median body is 704 words against a 21-word description — the body is where the routing signal lives.

## Example
```
bad:  "helps the agent reason carefully and provides high-quality guidance."
good: "Operates on CLAUDE.md, SKILL.md, .md files in .claude/; tools: Read, Grep, Glob."
```

## Limits
Concerns the body's routing vocabulary, not the frontmatter (a separate check). The ~30-concrete-token floor is a working heuristic, not a measured threshold.

## Validator
Inventory concrete tokens in the body — tool names, file extensions, framework / spec names, command names, function verbs, error names. Fewer than ~30, or they appear only in headings → flag. Test: does the body carry at least one concrete token for each of tools, file types, framework / spec names, and the trigger verbs a user would type?

## Patch output
When auditing a skill or agent-prompt body, emit one patch (`rule_id: R-03`, severity medium) adding concrete tool / file / framework tokens to the abstract passage; set `needs_human: true` when the real tools and files cannot be inferred from the file alone.

## Source
SkillRouter 2603.22455 §3, Fig 1 (31–44 pp Hit@1 from body ablation); App. A, Table 7 (catalog-wide median body 704 words vs 21-word description).
