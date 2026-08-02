# Gotchas — auditing-ai-context

Symptom → cause → fix for skills and context files, each tied to its source and R-rule. Cold-tier reference (loaded on demand): read when a skill or context file misbehaves, or when the audit workflow is unavailable. Stable IDs — a retired entry keeps its number vacant rather than reusing it (house convention; no owning R-rule). Pointer in `SKILL.md` §Gotchas.

G-01. Skill fails to trigger? Check `description` first (negative triggers, third person, when-to-use). If solid but routing still misses — body is under-signaling (R-03). Routers use full text; even the longest descriptions leave a 31.8pp Hit@1 gap versus full-body routing (SkillRouter 2603.22455 Appendix D).

G-02. Agent ignores MUST / NEVER. Pair every caps marker with a one-sentence rationale — agents follow reasons better than edicts (Anthropic skill-creator guidance; R-62).

G-03. `description` pasted verbatim into system prompt. Third-person mandatory; first/second person breaks routing (vendor authoring convention; R-02).

G-04. Positive framing holds for body (Promptomatix §B.1.1; R-61); negative triggers belong in `description` only. Different contexts, different rules.

G-05. Self-generated SKILL.md / AGENTS.md regresses: below the no-Skills baseline on all three tested configurations — −8.1pp Claude Code+Opus 4.7, −11.3pp Codex+GPT-5.5, −11.5pp Gemini CLI+Gemini 3.1 Pro — while curated Skills add +18.2 to +24.8pp on the same configs (Li 2602.12670 v4 §5.1.1, App. D.6); +20–23% inference cost for −0.5% to −2% success (Gloaguen 2602.11988 §4.2). The failure mode is *ungated one-shot* generation — verification-gated iteration inverts it: CoEvoSkills reaches 71.1% pass vs 53.5% human-curated and 32.0% one-shot (2604.01687 §4.2); SkillOpt's bounded edits accepted only on held-out validation improvement beat human-authored skills on all 52 cells (2605.23904 §3.5, §4.1). Curated gains are domain-dependent, not automatic: on end-to-end SWE tasks 39 of 49 public skills yielded zero pass-rate improvement (average +1.2%; three degraded, to −10%, from version-mismatched guidance; token overhead reached +451% with pass rates unchanged) — verify domain fit and version compatibility, not just skill quality (SWE-Skills-Bench 2603.15401, abstract). Validate with a fresh agent on real tasks; never ship ungated drafts.

G-06. ~26.1% of 42,447 collected community skills contain at least one vulnerability — prompt injection, data exfiltration (13.3%), privilege escalation (11.8%), or supply chain (Liu 2601.10338 §1, the primary scan; surveyed in Xu & Yan 2602.12430 §6.2); script-bundling skills 2.12× more vulnerable; ClawHavoc compromised over 1,184 published skills. Before installing third-party skills, diff against last-consented version — trust binds to identity, not content (R-84).

G-07. Reference files two hops from SKILL.md get partial reads — nested references are previewed (`head -100`) rather than read in full. Keep references one level deep, linked directly from SKILL.md (Anthropic, Skill authoring best practices).

G-08. Numeric edits ("at most 600" vs "610") degrade reliability more than rephrasing (Dong 2512.14754 §3.1). Lock numerics; re-run reliable@10 after any constraint edit (R-64).

G-09. Bundling tax: rule at 98.7% in isolation → 85% bundled with 18 others; 37.5% lose > 5pp (Yang §3.4). If rule N breaks rule N−5 after addition, it is bundling interference — split or prune.

G-10. Prohibitions invert on strong models — lifted GPT-4o 93→97% but dropped GPT-5 96.36→94% (Khan 2510.22251 §4.2, §4.4). Khan tested OpenAI models only; treating Haiku/Sonnet → Opus as the same gradient is an extrapolation. Re-run evals before porting skills across model tiers.

G-11. YAML frontmatter is not a contract — routing has no mechanism to verify body stays within description claims (2604.02837 §3.1). Read the body as an adversary during self-review (R-06).

G-12. Skill bodies lazy-load on activation (Liu 2604.14228 §6.1, §6.3) — a cross-skill body reference is inert until that other skill fires. Descriptions must be self-contained (R-04, R-44).

G-13. When debugging a non-trigger, diagnose by running new cousin prompts rather than asking the model "why did you fail?" — self-confidence AUROC 0.549, perplexity 0.497, both near-random (Dong Table 2).

G-14. Re-tune window-size / context-management hyperparameters on each new scaffold before reuse — tuning is scaffold-bound: the optimal masking window was M=10 on SWE-agent but M=58 on OpenHands, and naive reuse degrades drastically (Lindenbauer 2508.21433 §5.1, v3).

G-15. Context rot has four failure modes: poisoning, distraction, confusion, clash (Vishnyakova 2603.09619 §9, relaying Breunig 2025). Splitting one intent across sequential turns drops quality 39% on average across six generation tasks in simulated sharded conversations — aptitude −15%, unreliability +112% (Laban 2505.06120, abstract; decomposition from its 200,000-conversation analysis). Diagnose before compressing.

G-16. LLM-as-judge drifts on ambiguous correctness. For subjective scoring, prefer multi-round adversarial debate (d=3 rounds) over single-pass — beats single-judge 81.7–95% win rate (Nair 2506.00178 Table 4).

G-17. Multi-skill orchestration — conflict resolution, resource sharing, failure recovery — remains underdeveloped (Xu & Yan §7). Design descriptions with disjoint triggers; audit for near-duplicate siblings (R-76).

G-18. Direct prompt injection remains an open problem (2604.02837 §7.1); Abdelnabi 2605.17634 §4.4 argues no fixed policy can block all context-based attacks without also blocking legitimate flows. The Untrusted Input Handling rules (G8) reduce risk, not eliminate. Pair with human review for high-trust operations (R-85).

G-19. (Retired — it restated the Phase 1 sub-agent dispatch; folded into Phase 1 and R-83. IDs are stable, so the number is left vacant rather than reused.)

G-20. If two sub-agents disagree about line counts or code-ref classification, the Phase 0 inventory wins (see §Phase 0) — re-run Phase 0 if it looks stale. The inventory is itself audit-worthy: Phase 0 errors propagate to every sub-agent context simultaneously, so verify counts with deterministic tools (`wc`, `grep -c`, Python `len()`) rather than visual estimate (verified hands-on — an inventory once misreported a description length by counting its YAML prefix; dated record in the research log).

G-21. Misclassifying a KB card as a skill in Phase 0 cascades into wrong patches from every group (house; follows from the shared-inventory design — every sub-agent reads the same `target_type`).

G-22. The audit workflow needs Claude Code v2.1.154+ with dynamic workflows enabled — off by default on Pro (the Dynamic workflows row in `/config`), disableable org-wide (`disableWorkflows`). When it is unavailable, fall back to manual parallel dispatch (Phase 1): same reference files, same patch format, aggregation done by the main agent instead of in JS (Anthropic, Claude Code workflows docs).

G-23. (Retired — restated the Phase 1 read-only / apply-in-Phase-3 contract; folded into Phase 1 and R-83. IDs are stable, so the number is left vacant rather than reused.)

G-24. A target file changed during Phase 1 — the read-only phase? The dynamic-workflow runtime ignores agent `tools:` allowlists: workflow sub-agents run with `Write`/`Edit` granted and edits auto-approved, i.e. declared ∪ {Write, Edit} (Anthropic, Claude Code workflows docs — "File edits are auto-approved"; claude-code#63762, disk-verified 2026-05). The Task tool does enforce `tools:`, so the manual fallback keeps the hard barrier. Treat a mutated target as a compromised run: discard its patches, restore the target from git, re-run via manual dispatch (R-83, R-85). PreToolUse deny-hooks still fire inside workflows — a coarse hard stopgap where configured.

G-25. Skill regresses after a model *upgrade* — not bundling (G-09), not tier porting (G-10)? Newer Claude generations follow instructions more literally and over-trigger on aggressive wording: skills authored for prior models are often too prescriptive for the newest tier and can degrade output — try *removing* scaffolding (forced interim summaries, enumerated behaviors) and dialing "CRITICAL: You MUST…" down to "Use … when…" before adding anything. On Claude Fable 5, echo-/explain-your-reasoning instructions can trigger the `reasoning_extraction` refusal category with elevated fallbacks — audit for show-your-thinking wording when migrating. Effort names are calibrated per model — the same level is not the same value across models (Anthropic, Claude prompting best practices + per-model guides + model-config docs, 2026; R-60).

G-26. Instructions appear in a context file that nobody wrote, or misbehavior persists across fresh sessions? Persistent context is an injection *persistence* vector: product memory, CLAUDE.md files, mounted workspaces, and the state directories of scheduled and long-running agents are all reloaded each session, so an injection that lands in any of them re-arms indefinitely (Anthropic, "How we contain Claude", 2026). Diff persistent context files after agent runs; treat an unexplained addition as a compromise to remove and investigate, not as drift to merge (R-52, R-84).

G-27. The audit run dies on its first agent, before a single card is read, with an unresolvable agent type? Two causes, checked in this order. (1) Namespacing: `audit-subagent` and `audit-indexer` are declared by this plugin, so they resolve only as `<plugin>:<name>` — `evidence-based-authoring:audit-subagent` — and a bare name matches nothing (verified hands-on 2026-07-26: the session agent registry lists both types namespaced; `scripts/audit-workflow.js` re-derives the prefix from `cardsDir`, so a bare name still runs, but pass it qualified). (2) Stale plugin cache: the copy that runs is `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`, extracted from the marketplace clone of the *remote* repo, not from the local working tree — so a fix reaches the runtime only after commit → push → marketplace update, and the cache directory is keyed by the version in `.claude-plugin/marketplace.json`, so bump it to force a re-extract. Until then an already-fixed skill keeps failing identically (disk-verified 2026-07-26). When a fix does not take effect, `diff -rq` the cached copy against the repo before re-diagnosing.
