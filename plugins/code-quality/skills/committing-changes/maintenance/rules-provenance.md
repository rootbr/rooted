# Provenance of the committing-changes rules

Maintainer record, read in no run. One line per rule of `SKILL.md`, keyed by its section and position; the run set states the rule alone, and a rule and its line here change together.

- **Format, Types, Version bumps** · Conventional Commits 1.0.0, https://www.conventionalcommits.org/en/v1.0.0/ — the `<type>(<scope>): <subject>` header, the type list, `!` or a `BREAKING CHANGE:` footer → MAJOR, `feat` → MINOR, `fix` → PATCH
- **Workflow 2–3, Rules 1 — atomic and functional, one commit per logical change** · Git project, *SubmittingPatches* (`Documentation/SubmittingPatches` in git.git, https://git-scm.com/docs/SubmittingPatches): "make separate commits for logically separate changes"; "after any code change, make sure that the entire test suite passes"
- **Rules 2 — imperative mood, no trailing period** · Beams, *How to Write a Git Commit Message*, https://cbea.ms/git-commit/, rules 5 and 4 · lowercase subject: Conventional Commits 1.0.0 examples and the Angular commit convention
- **Rules 3 — subject ≤50 chars, body wrap at 72** · Beams, rules 2 and 6
- **Rules 4 — what and why, not how** · Beams, rule 7
- **Rules 5 — footer references issues** · Conventional Commits 1.0.0 spec items 8–10 (a footer is `token: value` or `token #value`, one blank line after the body; examples `Refs: #123`, `Reviewed-by: Z`), fetched
- **Grouping** · the same *SubmittingPatches* sentence as Rules 1; the group / split examples are house convention, hands-on
- **Gotchas 1 — a failed hook means no commit, so a new commit and never `--amend`** · `githooks(5)` § pre-commit: "Exiting with a non-zero status from this script causes the git commit command to abort before creating a commit"; `git-commit(1)` `--amend`: "Replace the tip of the current branch by creating a new commit" — both https://git-scm.com/docs/, fetched
- **Gotchas 2 — stage by name** · house convention, hands-on: `git add -A` has staged `.env` files and build output
- **Gotchas 3 — merge commits exempt** · house convention, hands-on; the Conventional Commits 1.0.0 spec does not mention merge commits (fetched)
- **Gotchas 4 — never `--no-verify`** · `git-commit(1)` `-n` / `--no-verify`: "Bypass the pre-commit and commit-msg hooks" (https://git-scm.com/docs/git-commit, fetched); the prohibition itself is house convention
