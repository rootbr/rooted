# Gotchas — reviewing-java

Symptom → cause → fix for the card-dispatched review, each tied to the file that owns the behaviour. Cold-tier reference: read when a review misfires — a shallow report, a finding that verification should have rejected, a workflow that dies on its first agent, a card that never triggers. Stable IDs: a retired entry keeps its number vacant rather than reusing it (house convention). Pointer in `SKILL.md` §Gotchas.

G-01. Finders produce shallow, generic findings, and the same diff reads as style in one repo and correctness in another? The pre-pass found no `.claude/reviewing-java/config.md`, so every finder prompt carries "(no project context was given)". Ask the author for the project's invariants and tolerances and write them into `config.md` before re-running the pre-pass; a review without them cannot reject a finding on a documented tolerance, and cannot run a single `PROJ-N` card.

G-02. A skeptic confirms a finding the surrounding code plainly handles? It read the finding's quoted snippet and stopped. The skeptic prompt (`scripts/review-workflow.js`, `skepticPrompt`) requires opening the whole method at HEAD and the diff of the file; a verdict whose `evidence` names neither is a verdict to distrust. Re-run that finding's verification by hand with the same prompt.

G-03. A finder returned an empty array: the run is fine. "No findings" is the expected outcome for most (card × slice) jobs — a card triggers on a lexical net far wider than its defect. Never re-dispatch a quiet finder hoping for findings; the empty result is data.

G-04. A finding's location no longer matches after a rebase or a follow-up commit? Findings anchor by `file` + `symbol` (`Class#method`) + the verbatim `code` fragment, never by line number; the render script prints the symbol, and the skeptic re-anchors by the fragment. A finding that carries only a line number came from a prompt that was edited — restore the `symbol` requirement.

G-05. (Retired — it governed the batch-of-four dispatch cap of the hand-driven agents; the workflow runtime paces its own concurrency. The number stays vacant.)

G-06. A finding with no anchor in the diff? Speculation. The finder discipline (`plugins/code-quality/agents/review-finder.md`) and the skeptic's false-positive check both require the quoted `code` to be an added line of `git diff <base> <head>`; a skeptic that cannot find it rejects the finding, and "conceptually similar to existing issues" is not an anchor.

G-07. A resumed verify stage rejects findings as "not in the diff", or confirms code that has since changed? The checkpoint `review/findings.json` carries the pre-pass inventory with `base_sha` and `head_sha`. If HEAD moved after the find stage, the findings describe code that no longer exists: re-run the pre-pass and the find stage rather than verifying stale findings against a new HEAD.

G-08. Logic-pass slices cut across a module, or one slice holds an unrelated mix? The pre-pass groups files by the package prefix one segment below the changed files' common root, which assumes package ≈ module. Where logical modules span packages, name them in `config.md` frontmatter — `modules: [{name, packages: [..]}]` — and the pre-pass slices by module instead.

G-09. (Retired — it warned against working around the batch cap with extra background tasks; the cap no longer exists. The number stays vacant.)

G-10. The workflow dies on its first agent with "agent type 'code-quality:review-finder' not found"? The two agent types are declared by this plugin and resolve only where the plugin is installed, as `code-quality:review-finder` and `code-quality:review-verifier`. In a repository checkout, or any session that lists only the built-in types, omit `agentTypes` from the args: every prompt carries the read-only prohibition and the injection stance, and the integrity check after the run is the backstop.

G-11. A file under the repository changed during the review? The dynamic-workflow runtime grants `Write`/`Edit` to sub-agents regardless of their `tools:` allowlist (claude-code#63762), so inside a run the prompt's prohibition is the only barrier. Treat a mutated tree as a compromised review: discard the findings, restore the tree, and re-run through the Agent-tool fallback, which does enforce the allowlist.

G-12. The audit of a card flags a "backslash path" in its frontmatter? A trigger written as `Files\.lines\(` reads as a Windows path to the audit's static pre-pass. Write a literal dot as `[.]` — `Files[.]lines\(` — which the card validator enforces; the two patterns match the same text.

G-13. `node --check` rejects `scripts/review-workflow.js` with "Illegal return statement"? The workflow runtime wraps the script body in an async function, so the script's top-level `return` is legal there and illegal in a bare module. Check the syntax as the runtime sees it: wrap the file in `async function __workflow(args, agent, parallel, pipeline, phase, log) { … }` in a temporary copy, with the `export` keyword removed, and run `node --check` on the copy.

G-14. Finders search files the plan never matched, or a card's trigger list looks truncated in the run? The `plan` argument was retyped into the tool call instead of pasted from `review/plan.json`. Pass the plan verbatim — the pre-pass output is the contract — and pass `root` as an absolute path.

G-15. A control that a documented tolerance covers still reaches the report? The tolerance sits in a code comment the skeptic never opened, or in `project_context` phrased so that no card's Limits recognise it. Tolerances that reject a finding are stated in `config.md` in the vocabulary of the card's Limits — "approximate counter, lost increments accepted", "map confined to one thread", "debug-only path" — and the fixture's `Stats#sample` control is the regression test for that path.
