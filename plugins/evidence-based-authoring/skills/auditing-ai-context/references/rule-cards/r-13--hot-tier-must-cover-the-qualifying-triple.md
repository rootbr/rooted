---
title: A hot-tier file must cover the qualifying triple of conventions, architecture, and project description
rule_id: R-13
applies_to_target: [context-file]
check_kind: mechanical
severity_default: medium
---

# A hot-tier file must cover the qualifying triple of conventions, architecture, and project description

## Thesis
A hot-tier file (`CLAUDE.md` / `AGENTS.md` / `copilot-instructions.md`) must contain three classes of content: (i) conventions and best practices, (ii) architecture and project structure, (iii) project description.

## Rationale
This triple was used as the qualifying criterion in the study that measured a 20.08% mean output-token reduction; only files carrying all three classes showed that benefit. Partial triples were not tested — completeness of the triple is the only configuration with measured benefit.

## Example
```
bad:  CLAUDE.md lists lint rules only (no architecture, no project description)
good: CLAUDE.md has ## Conventions, ## Architecture, ## Project
```

## Limits
Applies only to hot-tier files. The measured benefit attaches to the complete triple; partial triples are untested, so a missing class is flagged as incomplete rather than as a measured regression.

## Validator
Classify each section of the file. Conventions: naming, formatting, tooling, lint rules, commit style. Architecture: data flow, layering, key components, integration points. Project description: what the repo is, who uses it, the goal. Any of the three classes missing → flag.

## Patch output
When a class of the triple is missing from a hot-tier file, emit one patch (`rule_id: R-13`, `location.tier: hot`, `current` = which class is missing, severity medium) proposing a section skeleton (heading plus a 3-line bullet skeleton) for the missing class.

## Source
Lulla 2601.20404 (qualifying triple = inclusion criterion; −20.08% output tokens; partial triples untested).
