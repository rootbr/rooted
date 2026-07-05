---
name: committing-changes
description: Review changes and create atomic commits following Conventional Commits. Use when the user asks to commit, wants help writing commit messages, or has staged/modified changes ready to land. NOT for rebasing, cherry-picking, amending, squashing, or other history rewriting; NOT for pushing or managing remotes.
---

# Commit Changes

Spec: https://www.conventionalcommits.org/en/v1.0.0/

Review staged and modified files. Split into atomic commits.

## Workflow

1. `git status` and `git diff --cached`
2. Group related changes into logical units
3. One commit per logical change

## Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types

| Type | Purpose |
|--|--|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation only |
| style | Formatting, whitespace |
| refactor | Neither fix nor feature |
| perf | Performance improvement |
| test | Tests |
| build | Build system, dependencies |
| ci | CI configuration |
| chore | Other |

Version bumps: `feat`→MINOR, `fix`→PATCH, `!` or `BREAKING CHANGE:` footer→MAJOR.

## Rules

- MUST: each commit atomic and functional (builds, tests pass) (Git project, *SubmittingPatches*: "make separate commits for logically separate changes"; "after any code change, make sure that the entire test suite passes")
- MUST: imperative mood, no trailing period (Beams, *How to Write a Git Commit Message*, cbea.ms/git-commit — rules 5 and 4); lowercase subject (Conventional Commits / Angular commit convention)
- SHOULD: subject ≤50 chars, body wrap at 72 (Beams, rules 2 and 6)
- Body explains WHAT and WHY, not HOW (Beams, rule 7)
- Footer references issues: `Fixes #123`, `Refs #456`

## Grouping

- Group: same bug, one feature, one module refactor
- Split: unrelated features, fix+feature mixed, different layers

## Examples

```
docs(readme): update installation instructions
```

```
fix(api): handle null user response

Add null check before accessing user.email to prevent NPE.

Fixes #456
```

```
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: All /api/v1/* endpoints removed.
Migrate to /api/v2/* which provides enhanced functionality.
```

## Gotchas

1. Pre-commit hook failure means the commit did NOT happen — fix and create a NEW commit, never `--amend`
2. AVOID `git add -A` / `git add .` — can leak `.env`, credentials, large binaries. Stage by name (house convention, hands-on)
3. Merge commits are exempt from format
4. Never `--no-verify` unless user explicitly asks
