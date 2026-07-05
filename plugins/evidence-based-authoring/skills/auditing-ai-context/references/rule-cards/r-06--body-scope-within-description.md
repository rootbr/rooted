---
title: The body claims no capability the description does not advertise
rule_id: R-06
applies_to_target: [skill, agent-prompt]
check_kind: semantic
severity_default: high
---

# The body claims no capability the description does not advertise

## Thesis
Every tool the body invokes, file it touches, or external call it makes must be advertised by the description. A skill whose description says "audits .md files" but whose body calls a network endpoint or writes outside the cwd violates the routing-and-consent contract.

## Rationale
The router and the user both rely on the description as the consent surface, and the frontmatter has no mechanism to verify the body stays inside the description's scope — a human must. Scope drift is invisible until the skill fires; by then the agent is already invoking the unexpected tool or path.

## Example
```
bad:  desc "Reviews .md files."   body "…posts results to a Slack channel…"
good: desc "Reviews .md files and posts findings to Slack when configured."
```

## Limits
Concerns capability scope — tools, network, file mutation, external calls — not wording quality. Reads both body prose and the frontmatter capability fields (`allowed-tools` / `disallowed-tools`, `context: fork`, model overrides, hook registrations), which grant capability just as prose does.

## Validator
Read the body for tool invocations (Bash, network calls, writes outside referenced paths), external integrations (MCP, APIs), and read-vs-mutate mode; read the frontmatter capability fields too. For each capability, check the description claims it. If not → narrow the body or widen the description.

## Patch output
When auditing a skill or agent-prompt, emit one patch (`rule_id: R-06`, severity high) either adding the capability to the description or removing it from the body; set `needs_human: true`, because widening versus narrowing is the author's decision.

## Source
Li 2604.02837 §3.1 (YAML frontmatter is not a contract; nothing verifies the body stays within description scope, so a human must).
