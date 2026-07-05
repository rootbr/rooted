---
title: Sub-skills must receive attenuated privileges, not full inheritance
rule_id: R-83
applies_to_target: [skill, agent-prompt]
check_kind: mechanical
severity_default: medium
---

# Sub-skills must receive attenuated privileges, not full inheritance

## Thesis
When a skill spawns sub-agents or delegates to sub-skills, each must be granted the smallest slice of tools, paths, and secrets it needs. The dispatch must name those tools explicitly; "inherits all tools" or an unspecified tool set is a violation.

## Rationale
Default inheritance hands the child the parent's full privilege set, which violates least-privilege: a compromised or injected child can then mutate, exfiltrate, or escalate using capabilities it never needed. A declarative restriction — a frontmatter allowlist on the agent type — survives paraphrase, whereas a prose instruction can be argued away by an injected prompt. A shell counts as write: `sed -i` / `>` mutate and `curl` exfiltrates, so a read-only child excludes `Bash` too.

## Example
```
bad:  "Spawn an audit sub-agent."              (child inherits all tools)
good: dispatch an agent type whose frontmatter pins tools: Read, Grep, Glob;
      prose fallback: "tools = [Read, Grep, Glob]; no Write/Edit/Bash, no network."
```

## Limits
Applies to dispatches that spawn sub-agents or delegate to sub-skills. A skill that performs all work in its own context with no delegation is out of scope. Prefer the declarative form (a frontmatter `tools` allowlist, or `disallowed-tools` on a skill or slash command) where the runtime supports it. Enforcement is dispatch-path-dependent: a Task/Agent-style dispatcher honors the child's `tools:` allowlist, while a workflow-style runtime may grant write tools regardless of the declaration — so the declarative form layers on top of the prose prohibition, never replaces it, and a post-run diff of the touched files is the backstop. Fall back to prose alone only when no agent type is available.

## Validator
Search the body for sub-agent dispatch instructions. For each, check whether the dispatch explicitly names the tools the child receives. If it says "inherits all tools" or leaves the tool set unspecified, flag and prefer a declarative frontmatter restriction over prose. Validator question: does each delegation pin a minimal, explicit tool set rather than inheriting the parent's full surface? A child described as read-only that still lists `Bash` (or another shell/exec tool) is itself a violation — a shell mutates and exfiltrates, so it breaks the read-only claim.

## Patch output
When auditing a sub-agent dispatch with full inheritance, emit one patch (`rule_id: R-83`, `location.section` = heading, severity medium) proposing the dispatch with an explicit minimal tool set, declarative where the runtime allows.

## Source
OWASP Agentic Skills Top 10 v1.0 AST03 (least privilege). Caveat: not every dispatcher enforces a declared allowlist — Claude Code dynamic workflows grant `Write`/`Edit` regardless of `tools:` (claude-code#63762, disk-verified 2026-05).
