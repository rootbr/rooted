# Gotchas — auditing-ai-context

Symptom → cause → fix for skills and context files, each tied to the R-rule that owns it, where one does. Cold-tier reference (loaded on demand): read when a skill or context file misbehaves, or when the audit workflow is unavailable. Stable IDs — a retired entry keeps its number vacant rather than reusing it. Pointer in `SKILL.md` §Gotchas.

G-01. Skill fails to trigger? Check `description` first (negative triggers, third person, when-to-use). If solid but routing still misses — body is under-signaling (R-03). Routers usually see only name and description; even the longest descriptions leave a 31.8pp Hit@1 gap versus routing on the full text.

G-02. Agent ignores MUST / NEVER. Pair every caps marker with a one-sentence rationale — agents follow reasons better than edicts (R-62).

G-03. `description` pasted verbatim into system prompt. Third-person mandatory; an inconsistent point of view can cause discovery problems (R-02).

G-04. Positive framing holds for body (R-61); negative triggers belong in `description` only. Different contexts, different rules.

G-05. Self-generated SKILL.md / AGENTS.md regresses: below the no-Skills baseline on all three tested configurations — −8.1pp Claude Code+Opus 4.7, −11.3pp Codex+GPT-5.5, −11.5pp Gemini CLI+Gemini 3.1 Pro — while curated Skills add +18.2 to +24.8pp on the same configs; +20–23% inference cost for a −0.5% to −2% change in success that is not significant (two-sided p = 0.87 and 0.37). The failure mode is *ungated one-shot* generation — verification-gated iteration inverts it: CoEvoSkills reaches 71.1% pass vs 53.5% human-curated and 32.0% one-shot; SkillOpt's bounded edits accepted only on held-out validation improvement beat human-authored skills on all 52 cells. Curated gains are domain-dependent, not automatic: on end-to-end SWE tasks 39 of 49 public skills yielded zero pass-rate improvement (average +1.2%; three degraded, to −10%, from version-mismatched guidance; token overhead reached +451% with pass rates unchanged) — verify domain fit and version compatibility, not just skill quality. Validate with a fresh agent on real tasks; never ship ungated drafts.

G-06. ~26.1% of the 31,132 community skills analyzed (of 42,447 collected) contain at least one vulnerability — prompt injection, data exfiltration (13.3%), privilege escalation (11.8%), or supply chain; script-bundling skills 2.12× more vulnerable; ClawHavoc published at least 1,184 malicious skills. Before installing third-party skills, diff against last-consented version — trust binds to identity, not content (R-84).

G-07. Reference files two hops from SKILL.md may get partial reads — nested references may be previewed (`head -100`) rather than read in full. Keep references one level deep, linked directly from SKILL.md.

G-08. Constraint edits that make values more challenging (or reconfigure the task) typically score lower reliable@4 than rephrasing; even "at most 600" → "610" can fail many cases. Lock numerics; re-run reliable@10 after any constraint edit (R-64).

G-09. Bundling tax: rules average 98.7% in isolation → 85.0% on gpt-4o (79.7% on Llama-3.3-70B) when 19 are bundled; 37.5% lose > 5pp. If rule N breaks rule N−5 after addition, it is bundling interference — split or prune.

G-10. A constraint-heavy prompt (identity priming, prohibitions, format mandates) inverts on strong models — lifted GPT-4o 93→97% but dropped GPT-5 96.36→94%. The study tested OpenAI models only; treating Haiku/Sonnet → Opus as the same gradient is an extrapolation. Re-run evals before porting skills across model tiers.

G-11. YAML frontmatter is not a contract — routing has no mechanism to verify body stays within description claims. Read the body as an adversary during self-review (R-06).

G-12. Skill bodies lazy-load on activation — a cross-skill body reference is inert until that other skill fires. Descriptions must be self-contained (R-04, R-44).

G-13. When debugging a non-trigger, diagnose by running new cousin prompts rather than trusting the model's own forecast — on Qwen3-8B, confidence verbalized before generation scored AUROC 0.549 and prompt perplexity 0.497, both near-random.

G-14. Re-tune window-size / context-management hyperparameters on each new scaffold before reuse — tuning is scaffold-bound: the optimal masking window M=10 from SWE-agent degrades drastically when reused on OpenHands, where a retuned M=58 reproduces the results.

G-15. Long contexts fail in four modes: poisoning, distraction, confusion, clash. Splitting one intent across sequential turns drops quality 39% on average across six generation tasks in simulated sharded conversations — aptitude −15%, unreliability +112%, decomposed over 200,000 simulated conversations. Diagnose before compressing.

G-16. LLM-as-judge drifts on ambiguous correctness. For subjective scoring, prefer multi-round adversarial debate (d=3 rounds) over single-pass — as the fitness judge of a prompt-evolution loop, it gave the evolved prompts' outputs 81.7–95% win rates on subjective MT-Bench categories over the same loop judged single-pass.

G-17. Multi-skill orchestration — conflict resolution, resource sharing, failure recovery — remains underdeveloped. Design descriptions with disjoint triggers; audit for near-duplicate siblings (R-76).

G-18. Direct prompt injection remains an open problem. One analysis argues that no fixed policy can block all context-based attacks without also blocking legitimate flows. The Untrusted Input Handling rules (G8) reduce risk, not eliminate. Pair with human review for high-trust operations (R-85).

G-19. (Retired — it restated the Phase 1 sub-agent dispatch; folded into Phase 1 and R-83. IDs are stable, so the number is left vacant rather than reused.)

G-20. If two sub-agents disagree about line counts or code-ref classification, the Phase 0 inventory wins (see §Phase 0) — re-run Phase 0 if it looks stale. The inventory is itself audit-worthy: Phase 0 errors propagate to every sub-agent context simultaneously, so verify counts with deterministic tools (`wc`, `grep -c`, Python `len()`) rather than visual estimate: an inventory once misreported a description length by counting its YAML prefix.

G-21. Misclassifying a KB card as a skill in Phase 0 cascades into wrong patches from every group, because every sub-agent reads the same `target_type` from the shared inventory.

G-22. The audit workflow needs dynamic workflows enabled — off by default on Pro (the Dynamic workflows row in `/config`), disableable org-wide (`disableWorkflows`). When it is unavailable, fall back to manual parallel dispatch (Phase 1): same reference files, same patch format, aggregation done by the main agent instead of in JS.

G-23. (Retired — restated the Phase 1 read-only / apply-in-Phase-3 contract; folded into Phase 1 and R-83. IDs are stable, so the number is left vacant rather than reused.)

G-24. A target file changed during Phase 1 — the read-only phase? The dynamic-workflow runtime ignores agent `tools:` allowlists: workflow sub-agents run with `Write`/`Edit` granted and edits auto-approved, i.e. declared ∪ {Write, Edit}. The Task tool does enforce `tools:`, so the manual fallback keeps the hard barrier. Treat a mutated target as a compromised run: discard its patches, restore the target from git, re-run via manual dispatch (R-83, R-85). PreToolUse deny-hooks still fire inside workflows — a coarse hard stopgap where configured.

G-25. Skill regresses after a model *upgrade* — not bundling (G-09), not tier porting (G-10)? Newer Claude generations follow instructions more literally and over-trigger on aggressive wording: skills authored for prior models are often too prescriptive for the newest tier and can degrade output — try *removing* scaffolding (forced interim summaries, enumerated behaviors) and dialing "CRITICAL: You MUST…" down to "Use … when…" before adding anything. On Claude Fable 5, echo-/explain-your-reasoning instructions can trigger the `reasoning_extraction` refusal category, which server-side fallback does not retry — audit for show-your-thinking wording when migrating. Effort names are calibrated per model — the same level is not the same value across models (R-60).

G-26. Instructions appear in a context file that nobody wrote, or misbehavior persists across fresh sessions? Persistent context is an injection *persistence* vector: product memory, CLAUDE.md files, mounted workspaces, and the state directories of scheduled and long-running agents are all reloaded each session, so an injection that lands in any of them re-arms indefinitely. Diff persistent context files after agent runs; treat an unexplained addition as a compromise to remove and investigate, not as drift to merge (R-52, R-84).

G-27. The audit run dies on its first agent, before a single card is read, with an unresolvable agent type? Two causes, checked in this order. (1) Namespacing: `audit-subagent` and `audit-indexer` are declared by this plugin, so they resolve only as `<plugin>:<name>` — `evidence-based-authoring:audit-subagent` — and a bare name matches nothing: the session agent registry lists both types namespaced. `scripts/audit-workflow.js` re-derives the prefix from `cardsDir`, so a bare name still runs, but pass it qualified. (2) Stale plugin cache: the copy that runs is `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, extracted from the marketplace clone of the *remote* repo, not from the local working tree — so a fix reaches the runtime only after commit → push → marketplace update, and the cache directory is keyed by the version in `.claude-plugin/marketplace.json`, so bump it to force a re-extract. Until then an already-fixed skill keeps failing identically. When a fix does not take effect, `diff -rq` the cached copy against the repo before re-diagnosing.

G-28. The run dies in milliseconds with `TypeError: workflow() expects a workflow name (string) or {scriptPath: string}` — zero agents, empty logs? The main agent authored an inline wrapper workflow that re-invokes the shipped script via the in-script `workflow()` hook, and passed the Workflow tool's `args` as a JSON-encoded string. The wrapper reads its `args` raw, so every field resolves to `undefined`, and the inner `workflow({scriptPath: undefined}, …)` throws before the first agent: the persisted run record stores `args` as one JSON string, and the wrapper crashes at its first field access. The shipped `scripts/audit-workflow.js` parses string `args` itself, so the same stringified call survives a direct invocation — a wrapper stands in front of that defense while adding no capability the tool call lacks. Fix: re-invoke the Workflow tool with `scriptPath` pointing straight at the shipped script and `args` as a JSON object — the Phase 1 invocation verbatim.
