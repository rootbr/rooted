# Context-engineering evidence update — 2026-07-05

Follow-up to `2026-04-18_context-engineering-research.md`. Coverage: everything published or changed since that audit, through 2026-07-05. Five parts: (1) re-verification of every existing citation against fetched originals, with current source versions; (2) new publications; (3) vendor / runtime churn, including one load-bearing correction to `auditing-ai-context`; (4) model-specific optimization — the evidence for and against per-model rule forks (Sonnet 5 / Opus 4.8 / Fable 5); (5) the SKILL.md skill-smells catalog cross-checked against the rule-card corpus. Corpus-architecture decisions, the integration record, rejections, and the monitoring list close the file.

Method: a question map built first (9 discovery methods, 336 raw questions → 38 consolidated in 7 clusters, listed below), then parallel sweep agents — new-paper sweep, version-drift check over all cited papers + OWASP, vendor-churn check over the Claude Code changelog (releases since the 2026-04-18 audit, through v2.1.201) and Anthropic docs — with first-hand verification of every claim that entered the repo: changed abstracts fetched directly; body-level claims verified from `arxiv.org/html/2602.11988v2` and the 2602.12670v4 HTML/PDF; the workflows doc, issue #63762, the Agent Skills best-practices doc, the containment post, and the smells paper's supplementary artifact fetched directly.

## Research questions cross-checked against sources

### A. Skill routing at scale

1. At what installed-skill count does description-based routing degrade, and what published failure cases since April 2026 document it?
2. What did the "Skills 2.0" rearchitecting (commands/skills unified; skills spawn subagents, fork contexts, restrict tools, override models) invalidate in pre-2026 skill-authoring best practices?
3. Does skill visibility now depend on past invocation rate (claimed for Claude Code v2.1.129), and how would that change description authoring?
4. What replaces free-text descriptions as the routing signal (embeddings, learned routers, hierarchies), and what is the migration path?
5. How do overlapping descriptions shadow each other, and what ambiguity test detects shadowing before deployment?
6. Are skill routing and KB-card retrieval converging into one atomic-unit mechanism?

### B. Vendor guidance churn

7. Which Anthropic skill / CLAUDE.md recommendations from 2025–early-2026 have been reversed, deprecated, or contradicted by newer releases or docs?
8. What is the state of AGENTS.md unification across vendors, and what tool-specific behaviour broke?
9. What new Anthropic engineering posts or docs since April 2026 bear on context engineering, skills, or memory?
10. How long is the lag between a vendor guidance change and authoring-practice change, and what detects the change?

### C. Security & supply chain

11. What do the May 2026 impossibility-style results say about prompt injection, and what does that change for wrapper-discipline rules?
12. What do the large-scale skill-security scans measure, and do their vulnerability rates supersede the secondhand 26.1%/42,447 figure?
13. What does Snyk's ToxicSkills study report, and is it primary-source verifiable?
14. What supply-chain controls (signing, provenance, attestation, scanning, yanking) have marketplaces added since April 2026, and what is still missing vs mature package registries?
15. What rule follows from reports of post-install skill edits turning agents malicious — re-consent on update?
16. Does OpenAI's prompt-injection design guidance confirm or contradict the skill's G8 rules?

### D. Retrieval granularity & atomic knowledge units

17. What new work since April 2026 compares proposition-, card-, passage-, and document-level retrieval for agent KBs?
18. What evidence exists on atomization losses — connective tissue between ideas that isolated cards destroy — and does it bound the KB-card approach?
19. Have contextual-retrieval-style situating techniques been re-measured on newer models?

### E. Evidence-base hygiene

20. Which canonical claims (early-position reliability, lost-in-the-middle, LLM-generated context-file overhead) have been re-measured on post-2025 model generations, and did they hold?
21. What new evidence since April 2026 exists on LLM-generated vs human-written context files?
22. Are there new instruction-following reliability results (IFEval++ / reliable@k line) since April 2026?
23. Any published negative results or failed replications in context engineering?

### F. Cost mechanics

24. What measurements since April 2026 locate the crossover between eager skill loading and deferred discovery (latency/turns vs tokens)?
25. How do current cache-pricing schedules shift the static-CLAUDE.md vs runtime-retrieval break-even?

### G. Process, interop, and scope edges (open questions — researched only where sources surfaced)

26. Review workflows for context files (CODEOWNERS, eval-gated review); what can eyeball review not catch?
27. Agent-to-agent capability advertisement (agent cards / manifests) vs SKILL.md frontmatter — convergence or competition?
28. IP / licensing / GDPR for distilled KB corpora and marketplace skills (out of the audited skill's scope).

## Part 1 — Re-verification of the existing evidence base

Parallel verification agents fetched every cited source and checked every claim in the `auditing-ai-context` corpus and README against the fetched original. Tally: ~120 claims checked; ~85 confirmed; ~35 fixed in this pass. Notable corrections:

- **Fabricated anchors/claims removed**: Tokalator §3.4 (paper has no §3.3/§3.4 — content is §1); "Galster §5.1: files routinely list components that no longer exist" (no such finding in any version); Yang quote "~2× as likely to regress across model/prompt changes" (actual: 5.9% of requirements regress >20% over *model updates* when unspecified — almost 2×); "100+ rules" bundling framing (Yang bundles at most 19).
- **Misattributions fixed**: few-shot example guidance (2–5, best-last, −40%) is Promptomatix §B.2.1, not Khan §6.2.1; "601 skills / 95% within budget" is Galster §6.2 and the unit is 500 *lines*, not 5,000 tokens; "~6 security rules per 100 repos" is Mohsenimofidi Table 1 (6 headings among 155 AGENTS.md), not Galster; SkillRouter "renaming experiments" never happened — Appendix L.1 compares retrievers on a fixed catalog; the 3%-token/26.3%-attention figure is Appendix C.
- **Numbers/conditions restored**: Liang threshold is 232 tokens; Nair win-rate span is 81.7–95%; Bulle Labate is ~7× measured (16,900× is an estimate vs an infeasible baseline); summarization overhead range is 0.65–7.20%; Gloaguen's deletion result is +2.7% with *all* repo docs removed; Lulla's qualifying triple is an inclusion criterion, not a tested minimum; Hong gives no 30% positional threshold (house heuristic); Hong made no bullets-vs-prose comparison (that is ACE §3.1); Khan tested OpenAI models only — Claude-tier mapping is extrapolation; Xu & Yan's 26.1% covers four vulnerability categories, not prompt injection alone.
- **Two SkillRouter measurements, kept distinct**: the body-ablation Hit@1 drop is 31.4–44.0 pp (§3 Fig 1 — R-03's claim), while the nd-vs-full gap for the longest (>35-word) descriptions is 31.8 pp (Appendix D — G-01's claim). Both verified against the fetched paper; citing either number under the other's anchor is a drift.

Current versions of the cited papers, re-verified against fetched abstracts and bodies (the corpus cites these):

- **Gloaguen 2602.11988 v2 (2026-06-23).** Abstract: "providing context files **does not generally improve task success rates**, while increasing inference cost by over 20% on average". §4.2 carries −0.5%/−2% (SWE-bench/CTXBENCH) and the 20%/23% cost increase — measured as **USD inference cost** (Table 2), not tokens. The **+2.7% docs-removed result lives in App. B Fig. 12** ("Context files are redundant documentation"). Two further repo-relevant findings: "instructions in the context files are well followed … **repository overviews, although popular and recommended by model providers, are not helpful**", and "context files are useful for specifying non-standard coding practices" — direct support for the README's lean-context / `overview.sh` design. Developer-written files: +2.4% avg, p=21% (not significant); dev-vs-LLM gap 7%.
- **Li (SkillsBench) 2602.12670 v4 (2026-06-14).** 87 tasks / 8 domains / 18 model-harness configs / 3 trials. Headline +16.6pp (33.9→50.5%; 25.5% normalized; per-config +4.1…+25.7pp). Self-generated Skills land **below the no-Skills baseline on all three tested configs** (§5.1.1 + App. D.6 Table 6): −8.1pp (Claude Code+Opus 4.7), −11.3pp (Codex+GPT-5.5), −11.5pp (Gemini CLI+Gemini 3.1 Pro) — while curated Skills add +18.2…+24.8pp on the same configs. Complexity buckets (App. F.2 Table 9): Compact +19.0, **Standard +21.5**, Detailed +14.5, Comprehensive **+0.7** (flat, not negative). Quantity (App. F.1 Table 8): 1 skill +18.0, 2–3 +19.0, ≥4 +10.1 — "≤3 focused modules". Ecosystem snapshot: 2.01M skills; SKILL.md median **~1.2k tokens** (4.8 KB; bundle ~1.8k) over 767k clones (App. A.2 Fig. 7). Caution: v4 restructured earlier findings and dropped the old Finding numbering — cite §5.1.1 / App. D.6 / F.2 anchors only.
- **Galster 2602.14690 v5 (2026-06-30)** — title: *Harness Engineering for Agentic AI Coding Tools: An Exploratory Study* (AIware 2026). 2,853 repos; 95% of Skills ≤500 lines.
- **Liu 2602.06547 v4 (2026-06-10)** — camera-ready, USENIX Security 2026. Stats: 98,380 skills / 157 confirmed malicious / 632 vulnerabilities / avg 4.03 / 100% removed after disclosure.
- **Liu 2604.14228 v2 (2026-07-02)** — adds Hermes Agent as a third comparison system; the Claude Code facts the repo cites are unchanged.
- **Dong 2512.14754 v3 (2026-05-28)** — ACL 2026 main, oral. Cited claims unchanged.
- **OWASP Agentic Skills Top 10** — v1.0 (March 2026 page); roadmap: v1.0 RC Q3 2026, final Q4 2026.
- No newer versions: Yang 2505.13360 (v3), SkillRouter 2603.22455 (v4), Li 2604.02837 (v1), Liu 2601.10338 (v1), CoEvoSkills (v2), SkillOpt (v2), Abdelnabi (v1), Lulla (v2), Tokalator (v1), Pollertlam (v1), Xu & Yan (v4), Santos (v2).

## Part 2 — New publications and industry changes since 2026-04-18

### Security & supply chain (strongest cluster)

- 2026-01 · [2601.10338](https://arxiv.org/abs/2601.10338) — Liu et al. — *Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale*. **The primary source** for the 26.1%/42,447 figures (Li 2604.02837 §5.3 and Xu & Yan §6.2 relay them): 42,447 skills collected from two marketplaces, 31,132 analyzed with SkillScan (86.7% precision / 82.5% recall); 26.1% contain ≥1 vulnerability across 14 patterns in 4 categories; 13.3% data exfiltration; 11.8% privilege escalation; 5.2% high-severity patterns suggesting malicious intent; script-bundling skills 2.12× more vulnerable (OR=2.12, p<0.001). Calls for capability-based permissions and mandatory vetting.
- 2026-02 · [2602.06547](https://arxiv.org/abs/2602.06547) — Liu et al. — *"Do Not Mention This to the User": Detecting and Understanding Malicious Agent Skills*. 98,380 skills across two registries; 157 confirmed malicious; 632 distinct vulnerabilities across 13 attack techniques (avg 4.03 per malicious skill); two dominant strategies — credential theft via remote code execution, agent manipulation via adversarial instructions in documentation; >50% of confirmed cases from one threat actor using templated brand impersonation; 100% removal after responsible disclosure.
- 2026-02 · [Snyk ToxicSkills](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) — 3,984 skills scanned (ClawHub + skills.sh, 2026-02-05): 36.82% (1,467 skills) with ≥1 security flaw; 13.4% (534) with ≥1 critical issue; 76 human-confirmed malicious payloads, 8 still public at publication; 100% of confirmed-malicious combined code payloads with prompt injection; documented case: three lines of SKILL.md markdown sufficed to exfiltrate SSH keys. Submission volume grew 10× in weeks (≤50/day mid-Jan → >500/day early Feb).
- 2026-04-27 · [OWASP Agentic Skills Top 10](https://owasp.org/www-project-agentic-skills-top-10/) v1.0 — AST01 Malicious Skills … AST10 Cross-Platform Reuse. Author-side guidance: manifest honesty (AST04), least privilege (AST03), ed25519 signing + content hash, pin dependencies to immutable hashes (AST07), avoid identity-file write access.
- 2026-05 · [2605.17634](https://arxiv.org/abs/2605.17634) — Abdelnabi & Bagdasarian — *AI Agents May Always Fall for Prompt Injections*. Contextual-integrity-theoretic argument: "an adversary can always construct a context under which a blocked flow appears legitimate, or a defender who tightens norms will block genuinely legitimate flows"; three attack vectors (misrepresent flow, manipulate norms, mix flows); data-instruction separation defenses address "a shrinking fraction of future attack surfaces". Theoretical grounding for treating injection defense as risk reduction, never elimination.
- 2026-05-25 · [Anthropic, *How we contain Claude*](https://www.anthropic.com/engineering/how-we-contain-claude) — two findings the corpus encodes: telemetry shows users approve **~93% of permission prompts** (approval fatigue — the human gate degrades under volume; R-85), and **persistent memory poisoning**: product memory, CLAUDE.md files, mounted workspaces, and state directories of scheduled/long-running agents reload every session, so a landed injection re-arms indefinitely (G-26).
- 2026-07 · [2607.02357](https://arxiv.org/abs/2607.02357) — Ji et al. (HKUST) — *Cloak and Detonate* (v1, submitted 2026-07-02). Self-Extracting-Skill packing bypasses all 8 tested scanners at >90% (per-scanner SFS bypass mostly >99%: −99.8/−99.8/−99.9% in the evasion tables); the strongest static scanner falls 98.6%→10.1% under Structural Obfuscation; runtime taint-tracking auditor (SkillDetonate) 97% detection / 2% FP in the lab, 87% on real-world malicious skills. **Static/install-time scanning is defeatable — "passed the scan" is not evidence of safety**; encoded in R-84 (trust binds to identity; diff against consent) and README ref 34.
- 2026-06 · [2606.23416](https://arxiv.org/abs/2606.23416) — Etteib et al. — attention-based locate-and-judge malicious-skill detection; ~134k skills scanned, 131 confirmed malicious at 83% precision incl. 82 that evade SkillSpector/Cisco. Corroborates the scanning-gap picture.
- 2026-06 · [2606.18530](https://arxiv.org/abs/2606.18530) — prompting-based injection defenses are model-dependent (paraphrasing most consistent, −55–84% ASR; spotlighting helps Claude Haiku, does nothing on Llama 3.1 8B). Synthetic docs; single author. Consistent with G-18 risk-reduction framing; no rule change.
- Related: CSA research note on SKILL.md context poisoning (2026-05-06); SkillSieve [2604.06550](https://arxiv.org/abs/2604.06550) (hierarchical malicious-skill triage); NVIDIA Verified Agent Skills / SkillSpector.

### Skills / authoring

- 2026-07 · [2607.01456](https://arxiv.org/abs/2607.01456) — Hong, Imani, Ahmed — *From Anatomy to Smells: An Empirical Study of SKILL.md in Agent Skills* (v1, submitted 2026-07-01). 238 skills qualitatively analyzed → 13/44-component taxonomy; MLR of 29 sources → best practices → 26 "skill smells"; automated detector (SSD, weighted F1 0.78): **>99% of SKILL.md files carry ≥1 smell** (one smell-free file in the 228-skill detector sample; avg 10.5 smells/file); longitudinal (142 files, 1,199 commits, 35 weeks): smell prevalence never decreases — smells are seldom corrected once introduced. Strengthens the audit-based approach. Full cross-check against the rule-card corpus in Part 5.
- 2026-06 · [2606.10388](https://arxiv.org/abs/2606.10388) — Ding — *SkillResolve-Bench*. Same-capability sibling ambiguity: 661 helpful/risky pairs over 7,982 candidates; harmful-sibling-rate metric; SkillRouter HSR@3 = 0.693 vs SkillResolve 0. Single-author, unreplicated. Strengthens R-76 (near-duplicate siblings are a *safety* problem, not just routing noise); R-76 unchanged pending replication.
- 2026-06 · [2606.11435](https://arxiv.org/abs/2606.11435) — survey of skill evaluation/evolution (4 paradigms, 6 benchmark categories). Map, not evidence; no integration.
- 2026-03 · [2603.15401](https://arxiv.org/abs/2603.15401) — *SWE-Skills-Bench*. 49 public SWE skills × ~565 task instances across six SWE subdomains, deterministic acceptance-criteria verification, paired with/without evaluation: **39/49 skills yield zero pass-rate improvement, average gain +1.2%**; only 7 specialized skills produce meaningful gains (up to +30%); 3 degrade (to −10%) from version-mismatched guidance conflicting with project context; token overhead reaches +451% with pass rates unchanged. Tempers skill-benefit expectations in the SWE domain; encoded as the domain-fit caveat in G-05.

### Self-evolving skills

- 2026-04 · [2604.01687](https://arxiv.org/abs/2604.01687) (v2) — Zhang et al. — *CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification*. Skill generator + co-evolving surrogate verifier (no ground-truth test access); highest pass rate among five baselines on SkillsBench on both Claude Code and Codex; generalizes to six additional LLMs.
- 2026-05 · [2605.23904](https://arxiv.org/abs/2605.23904) (v2) — Yang et al. — *SkillOpt: Executive Strategy for Self-Evolving Agent Skills*. Skills as trainable external parameters, model frozen; optimizer proposes bounded add/delete/replace edits, accepted **only on held-out validation improvement**; +19.1 pts Claude Code, +23.5/+24.8 GPT-5.5 across 52 cells / 6 benchmarks / 7 models; beats human-authored, one-shot LLM, TextGrad, GEPA, EvoSkill.
- Net reading of the self-authoring line (with SkillsBench v4): the failure mode is *ungated* one-shot self-generation; iterative generation gated by external verification beats both one-shot and human-authored baselines. Bounded-edit discipline mirrors ACE append-and-refine.

### Reliability / evidence hygiene

- Dong [2512.14754](https://arxiv.org/abs/2512.14754): 20 proprietary + 26 open-source models; IFEval++ = 541 cases × (1 original + 9 cousins); ≤61.8% reliability drop stands. Adjacent benchmarks: IF-RewardBench (2603.04738), RubricEval (2603.25133).
- Descriptive studies pre-dating the base audit: *Agent READMEs* [2511.12884](https://arxiv.org/abs/2511.12884); *Developer-Provided Context in OSS* [2512.18925](https://arxiv.org/abs/2512.18925). Not integrated as rules — coverage overlaps the three descriptive studies already cited.
- 2026-05 · [2605.05400](https://arxiv.org/abs/2605.05400) — *Mise en Place for Agentic Coding* — "context fluency" methodology framing; no quantitative rules.

### Retrieval granularity & context mechanics (KB cards)

- 2026 re-evaluations nuance Dense X: recursive 512-token chunking remains a strong baseline (Vecta, 2026-02: 69% end-to-end across 50 papers); fixed 200-word chunks matched semantic chunking (NAACL 2025 Findings); over-fine fragments (~43 tokens) retrieve well but starve generation — direct support for kb-card-specification C-B2 ("atomic does not mean short").
- 2026-05/06 · [2606.00881](https://arxiv.org/abs/2606.00881) — chunking-methods comparison (88 configs): proposition-level (Dense X) among the worst and often non-viable; fixed/recursive-semantic best trade-off; **chunk coherence beats chunk count** — a second consecutive tempering of Dense X, consistent with C-B2. The kb-card spec stands: its cards are coherent claim-units, not maximal fragments. Field consensus: cross-granularity (index fine, assemble coarse) plus contextual enrichment — consistent with C-C3 self-situating.
- 2026-06 · [2606.10209](https://arxiv.org/abs/2606.10209) — Microsoft — pruning to last-5 tool pairs beats full history (79.0% vs 71.0% at −63.9% tokens); pruning+summarization reaches 91.6%. **Nuances R-17** (masking-over-summarization): on this one enterprise benchmark the *combination* beat pruning alone — single workflow, vendor-authored; recorded as a caveat here, R-17 unchanged pending replication (Lindenbauer's masking-vs-summarization comparison remains the controlled study).
- 2026-06 · [2606.06203](https://arxiv.org/abs/2606.06203) — lexical density as a third long-context degradation factor (independent of length and position): near-perfect models drop below 60% retrieval in dense ~12k-token contexts (9B–685B open-weight). Supports lean, well-spaced context bodies; complements Hong 2025.

## Part 3 — Vendor / runtime churn

**Load-bearing finding (encoded in `auditing-ai-context`):** the dynamic-workflow runtime **ignores agent `tools:` allowlists** — workflow sub-agents run in `acceptEdits` with `declared ∪ {Write, Edit}` and file edits auto-approved (Claude Code workflows doc: "The subagents the workflow spawns always run in acceptEdits mode … File edits are auto-approved"; [claude-code#63762](https://github.com/anthropics/claude-code/issues/63762), disk-verified repro 2026-05-29, **closed as not planned** 2026-07-02). The Task/Agent tool path *does* enforce `tools:`. Consequences encoded: prompt-level prohibition declared load-bearing on the workflow path; mandatory post-run `git status` integrity check (SKILL.md Phase 2b + always-on `main_agent_followups` entry); G-24; R-83 Limits (declarative layers on prose, never replaces); PreToolUse deny-hooks still fire inside workflows (coarse stopgap). Also verified: workflow script contract (`export const meta` + top-level await/return, runtime wraps the body; `agent()` accepts `{label, phase, schema, agentType, model, isolation}`; schema-retry; 16 concurrent / 1,000 agents per run; v2.1.154+; Pro: Dynamic workflows row in `/config`).

Skills 2.0 mechanics (confirmed via the [Claude Code changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md) and community deep-dives): commands and skills unified; skills spawn isolated subagents, run in forked contexts (`context: fork`), inject live shell data, override models, register lifecycle hooks. `disallowed-tools` frontmatter for skills and slash commands (v2.1.152) — privilege attenuation is declarative on the skill layer; `/reload-skills` + `SessionStart` `reloadSkills: true` (v2.1.152); plugins auto-load from `.claude/skills` (v2.1.157); `disableBundledSkills` (v2.1.169); marketplace shows projected per-turn / per-invocation token cost pre-install (v2.1.144).

Enforcement improved on the **Agent-tool path** in-window: v2.1.178 fixed MCP server-level specs in subagent `disallowedTools` being silently ignored; v2.1.186 fixed `Agent(type)` deny rules not enforced for named spawns. Other churn relevant to authoring: subagents nest to 5 levels (v2.1.172); malformed SKILL.md YAML now loads the body with empty metadata instead of failing silently, and four frontmatter keys accept case variants (v2.1.186) — "malformed frontmatter = silent skill loss" is not an accurate failure mode anymore; workflow trigger keyword is `ultracode` (renamed from `workflow`, v2.1.160); CLAUDE.md "too long" warning threshold scales with the model's context window (v2.1.169); Sonnet 5 default with native 1M context (v2.1.197); external plugins via project settings require explicit install consent on every loader path (v2.1.195) and `.mcp.json` self-approval closed (v2.1.196). No signing mechanism for Claude Code plugin marketplaces shipped.

Frontmatter validity spec (Agent Skills best practices, fetched 2026-07-05): `name` ≤64 chars, lowercase letters/numbers/hyphens only, no XML tags, no reserved words ("anthropic", "claude"); `description` non-empty, ≤1024 chars, no XML tags. Anti-pattern "Avoid Windows-style paths": always forward slashes, even on Windows — agents navigate the skill directory like a filesystem. Encoded in R-01, R-02, R-42.

Marketplace security: ClawHub ships **NVIDIA Skill Cards + SkillSpector scanning + ClawScan LLM-judge gate** on every skill (2026-06-01), with 67k scan outcomes open-sourced; scanner agreement is **≤10.4% Jaccard, 81.9% of positives from a single scanner** — no single scanner suffices, and 2607.02357 shows even ensembles are evadable. Registry yanking for git-URL registries cannot reach cloned copies (Nesbitt 2026-06-03).

## Part 4 — Model-specific optimization (Sonnet 5 / Opus 4.8 / Fable 5)

Question: should rules differ per model? Evidence-based answer: **differences are real but cluster by model generation and are handled by routing + de-prescription, not by per-model rule forks.**

Confirmed from Anthropic's per-model prompting guides (platform.claude.com, fetched 2026-07-05):

- **Fable 5**: "Skills developed for prior models are often too prescriptive for Claude Fable 5 and can degrade output quality. Review and consider removing older instructions if default performance is better." Echo-/explain-your-reasoning instructions can trigger the `reasoning_extraction` refusal category → elevated fallbacks to Opus 4.8; audit skills for show-your-thinking wording when migrating. Lower effort on Fable 5 often exceeds `xhigh` on prior models.
- **Opus 4.5+ / current models**: over-trigger on aggressive language — dial "CRITICAL: You MUST use this tool when…" back to "Use this tool when…"; "If in doubt, use [tool]" causes overtriggering.
- **Sonnet 5 / Opus 4.8**: literal instruction-following — state scope explicitly; remove interim-status scaffolding; review-skill recall drops after upgrade are harness effects (the model obeys "only report high-severity" more faithfully). Opus 4.8: thinking off by default, `xhigh` recommended; Sonnet 5: adaptive thinking on by default. **Effort names are calibrated per model — the same level is not the same value across models** (model-config doc).
- Tier checklist (skill authoring best practices): Haiku — enough guidance?; Sonnet — clear and efficient?; Opus — avoids over-explaining?; and the explicit recommendation to keep **one version that works across models**, not forks.
- Routing is the documented per-model mechanism: SKILL.md/agent frontmatter `model:` + `effort:` overrides (haiku for exploration, cost rationale).
- Long context: Sonnet 5's native 1M does **not** relax lean-context guidance anywhere; its new tokenizer inflates token counts ~30% for the same text (budgets tighten); context-rot (Hong 2025) + lexical density (2606.06203) + "smallest high-signal set" all still point to lean files regardless of window.

Research beyond vendor docs: Khan 2510.22251 remains OpenAI-only (no Claude replication of the help→harm inversion as of 2026-07-05); SkillsBench v4 shows skill benefit varies by config non-monotonically (+4.1…+25.7pp; frontier Claude gains least among Claude rows — OpenHands+Opus 4.8 +8.4pp vs Sonnet 4.6 +13.6pp — but the weakest tested model also gained least, so "smaller gains more" is an overclaim; supported: "smaller models with Skills can match larger models without"); CCI 2605.05716: scaffolding interference *saturates to ≈0* on Claude Haiku 4.5 — opposite shape from Khan's inversion; both agree the minimal adequate scaffold never loses.

Encoded: R-60 Limits/Source carry the vendor-confirmed direction for the Claude family (thresholds remain extrapolation); gotcha **G-25** (regression after model upgrade → de-prescribe first; Fable 5 `reasoning_extraction` trap; per-model effort calibration); SKILL.md §Maintenance: on model upgrade, try removing scaffolding/prescriptive language before adding.

## Part 5 — Skill-smells catalog × rule-card corpus (2607.01456 cross-check)

Two gates governed this cross-check, both from the paper itself: the normative base is **grey literature** (29 top-of-Google sources — the supplementary `rq2/artifact/best_practice_skill_smell_sources.csv` confirms vendor docs + blogs; the authors state it), and **impact on agent performance is unmeasured** ("remains an open question"). Per the Evidence-Based Rule, a smell enters the corpus only with an independently verified source; prevalence numbers (Table IV, 228-skill sample) are descriptive corroboration and stay in this log, not on cards.

Mapping (smell → corpus status; prevalence in the full sample):

| Smell | Prevalence | Status |
|---|---|---|
| LSD ≈0% · NTPD 3% · CSD 32% | description length / voice / structure | covered — R-02 |
| XID 0% (XML in description) | injection surface in an always-loaded field | **added to R-02** — the Anthropic frontmatter spec ("Cannot contain XML tags", ≤1024, non-empty) verified first-hand and now cited; mechanical check |
| LSN 0% · USN 17% | name length / clarity | covered — R-01; **name spec added to R-01** (≤64 chars, charset, no XML, no reserved words; same vendor spec) |
| BP 1% (backslash paths) | breaks non-Windows navigation | **added to R-42** — vendor anti-pattern "Avoid Windows-style paths" verified first-hand and now cited; mechanical check |
| LSB ≈0% · UD 46% | body length / undelegated detail | covered — R-10 / R-11 / R-74 |
| NAH 77% | never asks human | covered — R-85 |
| ME 34% | missing examples | covered — R-65 / R-28 |
| TSS 3% | time-sensitive content | covered — R-57 / R-73 |
| BG 81% | buried gotchas | house Gotchas convention — external practice-base corroboration recorded here |
| SOC 62% | over-prescribed command series | direction matches R-60 / G-25 de-prescription; descriptive corroboration only |
| TSW 32% · MT 25% | prose workflows / missing template | partially covered — R-21 / R-22; not carded (impact unmeasured) |
| NG 67% · MUR 44% · MC 71% | missing guardrails / usage rules / caveats | partially covered — R-02 NOT-for triggers + Gotchas convention |
| MUS 66% | missing utility script | **rejected** — conflicts with R-82: script-bundling skills are 2.12× more vulnerable (Liu 2601.10338, OR=2.12, p<0.001); the security gate wins over the convenience practice |
| RL 94% · NPT 71% · NVS 69% · EWP 78% · MDT 69% · TOB 8% | follow-through guards, validation loops, plan-first, decision trees, defaults | **not carded** — grey-literature base, impact unmeasured; the nearest measured evidence (CoEvoSkills / SkillOpt) gates *authoring-time* verification, not in-body loops — a different claim. Revisit any of these on measured evidence |

Eval opportunity, decided: the paper's 53-file human-labeled ground truth is public (supplementary) — running the R-corpus per-card validators against it and comparing coverage/precision with their SSD detector (weighted F1 0.78) is a candidate eval for the skill-creator/skill-optimizer harness. Not run in this pass — it is harness work, not a corpus edit.

## Corpus architecture decisions (dated record)

- **R-57 — provenance stays out of runtime context.** Mirror of C-A5: hands-on evidence is cited as the verified finding with its numbers; calendar dates, audit-run IDs, and log paths live in this research log and git history.
- **R-47 — reference files read in isolation.** Mirror of C-C1/C-C2: no unnamed-document deixis, references enrich but never complete; deference stubs are exempt (their operative instruction — omission — is complete in itself). Source of the two-hop limit: Anthropic "Skill authoring best practices" ("Claude may partially read files when they're referenced from other referenced files… Keep references one level deep") — also the primary source of the cold-tier ToC rule in R-10.
- **Per-card corpus.** One rule = one atomic card in `references/rule-cards/` (Thesis → Rationale → Example → Limits → Validator → Patch output → Source), dispatched one card per sub-agent by the `applies_to_target` facet; the g1–g8 group files that preceded the cards are removed (git history preserves them; the cards are canonical). Cross-card concerns (ownership/defer, conflict priority) live in `audit-workflow.js`; full citations in `rule-cards-provenance.md`; controlled vocabulary in `rule-cards-taxonomy.md` — all out-of-runtime.
- **Deference stubs are unconditional** ("G<N> owns this check; do not emit") — a "if the owner already reports" condition is unobservable to a parallel sub-agent.
- **Warm-budget acceptance:** SKILL.md at ≈21k chars is ≈4.9k tokens at a realistic ~4.3 chars/token — within the ~5,000 budget; no demotion.
- **G-20's deterministic-count rule — hands-on record:** a Phase 0 inventory misreported a skill's description length by counting its YAML prefix (1034 counted vs 1011 actual); a sub-agent corrected it with `wc`. This is the dated record behind the gotcha's "verify counts with deterministic tools" instruction.
- **`../SKILL.md#patch-format` pointers stay** in dispatch prompts: sub-agents hold Read and the dispatch directs them to that section; inlining would duplicate the schema across every card.
- **Scaffold duplication is kept** (the shared scaffold block repeated verbatim in all 12 discovering-subtopics agent prompts; "Empty case"/"Step 2 git command" in all 6 reviewing-java specialists). Dispatched prompts are read in isolation — the same property that motivates R-47/C-C2; a pointer adds a two-hop partial read (G-07); moving the block into orchestrator-injected dispatch text would silently strip it from any directly-dispatched agent file; and structural rewires are accepted only on held-out eval improvement (SkillOpt discipline) — no eval harness covers these skills. R-43's state-once applies within one file or a corpus read together, not across independently-dispatched prompts.
- **Model/effort routing adopted at the invocation layer** (vendor cost rationale — "route tasks to faster, cheaper models"): the workflow accepts `modelByCheckKind` / `effortByCheckKind` / `indexModel`, recommended mechanical → haiku + low, semantic → sonnet + medium, indexer → haiku + low. An audit sub-agent runs one narrow prescriptive validator — the task profile where smaller models with a good scaffold match larger ones (SkillsBench v4). The defaults inherit the session model, so the routing is a reversible per-run choice, not a frontmatter fork; quality is watched on each gate run, and a held-out eval of the routed configuration stays open.
- **Gate mode (diff-triage) adopted**: the pre-commit gate dispatches only the cards whose concern a diff hunk can affect, plus the whole-file core R-43 / R-70 / R-73; new files and reworks run the full set. Coverage stays incremental — every line passed the full corpus when it last changed.
- **Static pre-pass adopted** (`scripts/static-audit.py`, declared per R-82): the fully mechanical validators (R-01/R-02 spec halves, R-10 budget, R-20, R-27, R-42, R-62) run as stdlib Python with no LLM; R-20 / R-27 / R-42 / R-62 leave the dispatch list when the pre-pass has run.
- **Declarative attenuation adopted where it applies:** `reviewing-java` gains `disallowed-tools: Edit, NotebookEdit` (its orchestrator writes state/prompts/reports but never edits code — least privilege, OWASP AST03 / R-83), with the standing caveat that the workflow runtime ignores agent allowlists (#63762) and prose remains the operative barrier there. `committing-changes` / `cleaning-code` keep full tool sets — their function requires mutations.

## Integration record (this pass)

- **Cards**: R-01 (+name spec), R-02 (+description spec incl. no-XML), R-42 (+forward-slash separators), R-84 (+scanner-evasion caveat, Ji 2607.02357), R-85 (+approval-fatigue caveat, Anthropic containment telemetry) — with matching `rule-cards-provenance.md` lines.
- **Gotchas**: G-05 gains the SWE-Skills-Bench domain-fit caveat; new G-26 (persistent-context poisoning). SKILL.md §Gotchas range → G-01…G-26.
- **committing-changes**: the atomic-and-functional MUST now cites Git *SubmittingPatches* ("make separate commits for logically separate changes"; "after any code change, make sure that the entire test suite passes") — fetched and verified.
- **discovering-subtopics**: description now advertises live web search (Field intelligence) and file outputs under `tmp/coverage-map-{topic-slug}/` (R-77 body/description scope sync), and fits the platform spec at 1016 chars (was 1034 — over the ≤1024 auto-reject limit).
- **reviewing-java**: `disallowed-tools: Edit, NotebookEdit` frontmatter.
- **README**: ref 34 (Ji 2607.02357) added; badge 34→35 papers; research-audit link points here.
- **Workflow cost controls**: `audit-workflow.js` gains per-`check_kind` model/effort routing and per-target `cards` allowlists (validated loud); new `scripts/static-audit.py` static pre-pass; SKILL.md Phase 1 documents both plus the gate-mode triage map.
- **maintenance-map.md** added (out-of-runtime, same class as provenance/taxonomy): the reviewer's anchor legend — what each token class is and how to verify it — plus volatile-dependency dossiers; the #63762 flip-site list lives there.
- **Deep-review pass** (deterministic cross-reference layer + five routed sonnet lenses over the whole skill): deterministic layer clean — all rule/gotcha IDs, paths, `DEFER_TO`/`GROUP_PRIORITY`/`PATCH_SCHEMA`/`groupOf` contracts in sync; 16 semantic findings fixed: Phase 2/3 single-ask seam; Phase 2a dedup/ordering text re-synced to the aggregator's actual keys; kb-card facet vocabulary corrected in Phase 0; kb-corpus dispatch made precise (C-A2/C-A3; security cards named R-80/R-85); taxonomy now documents the C-cards' `rejected:/accepted:` example labels; prompt template and `prompt()` converged (tools line, severity default); static pre-pass contract fixes (no `current` truncation, R-27 scoped to its density trigger, output-shape wording); invocation example gains `indexAgentType`; provenance R-16/R-60 lines completed to the cards' anchors; R-05 extrapolation caveat surfaced in Limits; maintenance-map flip-site #3 precision. Two agent findings rejected: the G-01 31.8 pp / App. D vs R-03 31–44 pp / §3 pairing is two distinct verified measurements (recorded above), and a field-order difference in the indexer description is cosmetic.
- **marketplace.json**: both plugins 4.7.0 → 4.8.0.
- Cross-skill audit findings applied: researching-topics R-04 deixis; committing-changes R-02 NOT-fors + R-50 citations (Beams, cbea.ms/git-commit); reviewing-java R-77 description scope, R-83 dispatch tool pinning, R-80 `<findings>` delimiters; discovering-subtopics R-47 deixis ×2.
- **Pre-commit gate run (routed)**: static pre-pass over 32 context files (19 findings, all low pre-existing style traits — deferred) + 84 sub-agents on haiku/sonnet over 10 diff-triaged targets → 34 patches, 21 applied / 13 rejected. Applied highlights: Liang GPT-4o qualifier restored in SKILL.md; Beams rule anchors corrected (wrap-72 is rule 6; imperative/no-period are 5/4; lowercase is the Conventional-Commits/Angular convention); SkillRouter Case C counter-case + large-registry scope added to R-01 Limits (verified first-hand: baseline 8/12 vs router 4/12 in specialized domains); discovering-subtopics description gains a NOT-for and sheds path/cwd jargon, its sole-writer anti-pattern reconciled with G-06's pre-restart cleanup; reviewing-java description now names `gh pr view` and config-set report paths, the layout diagram matches disk (checklist.md), modified findings routed to one report, verification agent's tools pinned; gotcha source markers (G-02/03/04/15/20/21).

## Rejected (do not re-propose without new evidence)

- **Per-model rule forks** (Sonnet 5 / Opus 4.8 / Fable 5): vendor guidance prefers one cross-model version + `model:`/`effort:` routing; differences encoded as generation-level de-prescription (R-60, G-25). No per-model numeric budgets exist; Khan 2510.22251 remains OpenAI-only; "weaker models gain more from skills" contradicted by SkillsBench v4 (weakest config gained least, +4.1pp).
- **1M-context relaxation of size budgets**: Sonnet 5 tokenizer inflates counts ~30%; context rot + lexical density unchanged; no vendor doc relaxes lean-context guidance.
- **Smell-catalog imports beyond the vendor-spec checks** (RL, NPT, NVS, EWP, MDT, TOB, MT, TSW as cards): grey-literature normative base; impact unmeasured — see Part 5.
- **MUS ("missing utility script")**: conflicts with R-82's measured security evidence; rejected toward R-82.
- **Prevalence numbers as card citations**: descriptive, not evidential for rule validity; recorded in this log only.
- **R-85 human gate before writing the review report** (reviewing-java): report writing is reversible; outside the card's Limits.
- **61.8 pp attached to the third-person voice claim** (gate patch on R-02): Dong §2.2 measures paraphrase-induced reliable@10 collapse, not voice effects — attaching the number would fabricate precision.
- **C-B1 split of the R-01/R-02 field-spec bundles**: the naming/voice heuristic and the platform spec share one audit moment (the same frontmatter field), the spec half is already carried by the static pre-pass, and a new card would land in the wrong `groupOf` range; revisit only if the group ranges are re-cut.
- **Within-file restatements flagged by R-43 in discovering-subtopics / reviewing-java dispatch texts**: text appended to a sub-agent dispatch is read in isolation — self-containedness wins over state-once there (same rationale as the scaffold-duplication decision); the Mission/Workflow summaries restate across tiers by design.
- **Advertising `coverage-gap-auditor` in the discovering-subtopics description** (R-06/R-77 gate patches): the auditor is an internal background agent of the same skill — the capability class is already advertised — and the description sits near the 1024-char ceiling.
- **G-16 Nair recitation** (gate patch): the debate-beats-single-judge win-rate span 81.7–95% was verified against the fetched source in Part 1; the gotcha's framing sentence is the house symptom index, not the cited claim.
- **R-61 rewrites in reading-companion**: the two flagged negatives are safety-scoped (anti-fabrication), within the card's exception.
- **Conventional-Commits citation for the atomicity/message rules**: the CC spec contains no such rules — a fabricated anchor (R-56); real sources are Beams (cbea.ms/git-commit) and Git *SubmittingPatches*.
- **v2.1.129 "least-used skills dropped from listing by recency/frequency"**: no such changelog entry (v2.1.129 added `skillOverrides`); excluded.
- **Agent READMEs 2511.12884 / 2512.18925 as rules**: descriptive overlap with the three descriptive studies already cited; bundling-tax cost exceeds value.
- **IP / licensing / GDPR cluster**: out of the audited skill's scope — open questions only.

## Monitoring

- **claude-code#63762 / workflow tools enforcement**: if a release honors agent `tools:` inside workflows (or adds `tools` to `agent()`), flip the enforcement-caveat wording across the anchored sites — all written to be reversible; the living flip list and re-verification procedure are in `maintenance-map.md`.
- **OWASP Agentic Skills Top 10**: v1.0 RC expected Q3 2026, final Q4 — re-check AST anchors on release.
- **SkillsBench**: v4 dropped per-domain deltas and the old Finding numbering; on a v5, re-verify §5.1.1 / App. D.6 / F.2 anchors.
- **SkillResolve-Bench** (2606.10388): single-author, unreplicated — integrate into R-76 on replication.
- **Pruning+summarization** (2606.10209) and **lexical density** (2606.06203): caveats recorded above; R-17 / R-11 unchanged pending replication.
- **XID / BP prevalence**: both ~0–1% in the wild today; the R-02/R-42 mechanical checks are near-free — keep, re-examine only if the platform spec changes.
- **External URLs are outside every validator**: R-73 checks repo-state pointers and audit sub-agents run without network, so a dead external link survives the gate (a 404 Conventional-Commits spec URL was human-caught; the full 59-URL sweep of this commit found no other dead link). Candidate: a main-agent follow-up that status-checks every external URL in changed context files — with the caveat that some hosts (github.com list pages) 404 to non-browser clients, so anomalies need an API cross-check before flagging.
