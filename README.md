# Rooted — Claude Code plugins rooted in evidence

[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/rootbr/rooted?style=social)](https://github.com/rootbr/rooted/stargazers)
[![Rules cited from](https://img.shields.io/badge/rules%20cited%20from-35%20papers%20%C2%B7%203%20standards-success)](#references)

Skills for the full evidence-based preparation pipeline: research any topic with source verification, map its complete question space before you start, then write AI agent context that actually works — grounded instructions and disciplined reasoning instead of vibes. [Research shows](https://arxiv.org/abs/2602.11988) LLM-generated context files do not generally improve agent task success while raising inference cost by 20–23% — and the repository overviews they typically contain are specifically unhelpful. Rooted structurally refuses them: every rule traces to a peer-reviewed paper or an RFC. Software-development and code-review skills apply the same discipline to everyday coding.

- **Evidence-based, not LLM-generated.** Every rule traces to a peer-reviewed paper, RFC/spec, or a hands-on test — not to "ask the model to write a skill."
- **Lean context over static dumps.** For example, instead of an `/init`-style project-structure blob in `CLAUDE.md` (a file class shown not to improve success while raising cost ~20%, with repository overviews specifically found unhelpful [[15]](#references)), orientation happens on demand via [`overview.sh`](overview.sh) with an explicit stop-instruction. The agent doesn't preemptively slurp the whole tree into context, so it doesn't fill its working memory with project content it doesn't need and later lose focus on the actual task.

## Methodology

Every rule, checklist item, and review criterion traces to one of:

- **Academic research** — arxiv.org, peer-reviewed papers, Google Scholar, PubMed
- **Technical standards** — RFCs, official specifications, language/framework documentation
- **Human-tested** — double-checked and reviewed by a human before commit

## Plugins

### evidence-based-authoring

Five evidence-based skills. Three form a preparation pipeline — research → explore → write: gather verified sources, map every angle of a topic, then produce agent instructions grounded in evidence. `/appraising-research` adds a critical-appraisal gate over a finished report — grading evidence quality, surfacing hidden assumptions, hunting competing hypotheses and blind spots, and mapping who benefits. The last, `/reading-companion`, is an active-reading companion for a book you study yourself — grounded in learning-science research.

| Skill | Description |
|--|--|
| `/researching-topics` | Research any topic on the web with source verification and critical analysis |
| `/discovering-subtopics` | Build a maximum-breadth question map across any topic using 10 complementary methods — structural decomposition, perspective shifting, causal chains, and more |
| `/appraising-research` | Critically appraise a finished research report — evidence grading, hidden assumptions, competing hypotheses, premortem/red-team, and beneficiary/funding analysis — then rank what to re-check, with adversarial debate on the highest-stakes findings |
| `/auditing-ai-context` | Audit and optimize any AI agent context: CLAUDE.md, SKILL.md, prompts, instructions. Adapt project docs for AI consumption |
| `/reading-companion` | Active-reading companion for a book you study yourself — classify it, scaffold a per-book workspace, then explain intent, translate fragments, walk proofs, and capture your own notes; amplifies recall, never substitutes for it |

### code-quality

| Skill | Description |
|--|--|
| `/reviewing-java` | Deep Java code review with parallel specialist agents and verification. [Details](plugins/code-quality/skills/reviewing-java/README.md) |
| `/architecting-code` | Structural and boundary-level design: dependency direction, layering, component cohesion/coupling, plugin architecture, use-case isolation |
| `/cleaning-code` | Improve code readability and maintainability |
| `/committing-changes` | Review changes and create atomic commits following Conventional Commits |

## Installation

Add the marketplace:

```
/plugin marketplace add rootbr/rooted
```

Install plugins:

```
/plugin install code-quality@rooted
/plugin install evidence-based-authoring@rooted
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Every new rule must cite a source — an arXiv ID, an RFC number, or a linked hands-on test. PRs without citations are rejected by design, not by oversight.

## References

For the full cross-check of each paper against the research questions this marketplace tries to answer, see the [research audit](research/2026-04-18_context-engineering-research.md) and its [2026-07-05 update](research/2026-07-05_context-engineering-update.md) — findings extracted per paper, every existing citation re-verified against the fetched original, including tangential results that inform but do not yet back a specific skill rule.

The badge and the list below count the context-engineering corpus that backs the authoring and code-review skills. [`/reading-companion`](plugins/evidence-based-authoring/skills/reading-companion/SKILL.md) rests on a separate body of learning- and reading-science research (Adler; Dunlosky et al. 2013; Roediger & Karpicke; Cepeda et al. 2006; Chi & Wylie 2014; and others); its full bibliography is bundled with the skill in [`reading-methodology.md`](plugins/evidence-based-authoring/skills/reading-companion/references/reading-methodology.md).

[`/appraising-research`](plugins/evidence-based-authoring/skills/appraising-research/SKILL.md) likewise rests on a separate body of critical-thinking and evidence-appraisal research (Toulmin's argument model; Walton's argumentation schemes; Heuer's Analysis of Competing Hypotheses; Guyatt et al.'s GRADE; Lundh et al.'s Cochrane review of sponsorship bias; and the LLM self-critique literature — Constitutional AI, Chain-of-Verification, multi-agent debate, and their documented failure modes). Its full bibliography is bundled with the skill in [`appraisal-methodology.md`](plugins/evidence-based-authoring/skills/appraising-research/references/appraisal-methodology.md), with the design rationale in the [research note](research/2026-07-01_critical-thinking-layer-for-research-pipeline.md).

### Technical standards

- Bradner (1997). *Key words for use in RFCs to Indicate Requirement Levels.* [BCP 14 / RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — MUST / SHOULD / MAY priority keywords used in [`/auditing-ai-context`](plugins/evidence-based-authoring/skills/auditing-ai-context/SKILL.md).
- Leiba (2017). *Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words.* [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174) — Clarifies that BCP 14 keywords only apply in ALL CAPITALS.
- OWASP (2026). *Agentic Skills Top 10, v1.0.* [owasp.org/www-project-agentic-skills-top-10](https://owasp.org/www-project-agentic-skills-top-10/) — AST01–AST10 risk framework; author duties: honest manifests, least privilege, signing, immutable-hash dependency pins.

### Research papers

1. Liang et al. (2024). *Can Language Models Replace Programmers for Coding? RepoCod Says 'Not Yet'.* [arXiv:2410.21647](https://arxiv.org/abs/2410.21647) — Repo-level benchmarks: no tested LLM exceeds 30% pass@1; commercial models did best with current-file context, RAG helps only some open-source models.
2. Yang et al. (2025). *What Prompts Don't Say: Understanding and Managing Underspecification in LLM Prompts.* [arXiv:2505.13360](https://arxiv.org/abs/2505.13360) — Rule bundling tax: 37.5% of rules lose >5% compliance when combined; per-rule validators hit 95.6% human agreement.
3. Nair et al. (2025). *Tournament of Prompts: Evolving LLM Instructions Through Structured Debates and Elo Ratings.* [arXiv:2506.00178](https://arxiv.org/abs/2506.00178) — Multi-round adversarial LLM debate (d=3, two advocates + judge) beats single-pass LLM-as-judge 81.7–95% of the time — evidence for adversarial eval over single-judge scoring.
4. Murthy et al. (2025). *Promptomatix: An Automatic Prompt Optimization Framework for Large Language Models.* [arXiv:2507.14241](https://arxiv.org/abs/2507.14241) — Positive-over-negative framing; 2–5 diverse examples, best-fit placed last.
5. Lindenbauer et al. (2025). *The Complexity Trap: Simple Observation Masking Is as Efficient as LLM Summarization for Agent Context Management.* [arXiv:2508.21433](https://arxiv.org/abs/2508.21433) — Tool outputs consume ~84% of agent tokens; masking beats summarization.
6. Chatlatanagulchai et al. (2025). *On the Use of Agentic Coding Manifests: An Empirical Study of Claude Code.* [arXiv:2509.14744](https://arxiv.org/abs/2509.14744) — Empirical analysis of 253 `CLAUDE.md` files; shallow 2–3 level hierarchies dominate.
7. Zhang et al. (ICLR 2026). *Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models.* [arXiv:2510.04618](https://arxiv.org/abs/2510.04618) — ACE: context-collapse evidence against aggressive compression; bullets with metadata beat prose.
8. Gao & Peng (2025). *More with Less: An Empirical Study of Turn-Control Strategies for Efficient Coding Agents.* [arXiv:2510.16786](https://arxiv.org/abs/2510.16786) — Concrete cost/accuracy across Claude / Gemini / GPT; eval repetition (10× per task) required to reach statistical significance.
9. Mohsenimofidi et al. (2025). *Context Engineering for AI Agents in Open-Source Software.* [arXiv:2510.21413](https://arxiv.org/abs/2510.21413) — AI context files in 466 of 10,000 scanned OSS repos (155 `AGENTS.md` analyzed); five instruction styles observed in the wild.
10. Khan (2025). *You Don't Need Prompt Engineering Anymore: The Prompting Inversion.* [arXiv:2510.22251](https://arxiv.org/abs/2510.22251) — Constrained prompts help <90%-accuracy models but degrade >95%-accuracy frontier models.
11. Santos et al. (2025). *Decoding the Configuration of AI Coding Agents: Insights from Claude Code Projects.* [arXiv:2511.09268](https://arxiv.org/abs/2511.09268) — Empirical study of 328 `CLAUDE.md` files; Architecture dominates top-5 patterns.
12. Bulle Labate et al. (2025). *Solving Context Window Overflow in AI Agents via Memory Pointers.* [arXiv:2511.22729](https://arxiv.org/abs/2511.22729) — Replacing tool outputs with pointer IDs achieved a ~7× measured token reduction, ~16,900× estimated against a would-overflow baseline; supports handle-returning tools over inline blobs.
13. Dong et al. (ACL 2026). *Revisiting the Reliability of Language Models in Instruction-Following.* [arXiv:2512.14754](https://arxiv.org/abs/2512.14754) — IFEval++ and `reliable@k` metric; up to 61.8% drop under paraphrased instructions.
14. Lulla, Mohsenimofidi, Galster, Zhang, Baltes, Treude (2026). *On the Impact of AGENTS.md Files on the Efficiency of AI Coding Agents.* [arXiv:2601.20404](https://arxiv.org/abs/2601.20404) — 124 PRs × 10 repos; qualifying AGENTS.md yields −28.64% median runtime, −16.58% median output tokens.
15. Gloaguen et al. (2026). *Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?* [arXiv:2602.11988](https://arxiv.org/abs/2602.11988) — **Primary citation** (v2, 2026-06-23). Context files do not generally improve task success while raising inference cost 20–23%; instructions are followed but repository overviews are not helpful; developer-written files outperform LLM-generated ones yet help only marginally (+2.4%, not significant).
16. Xu & Yan (2026). *Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward.* [arXiv:2602.12430](https://arxiv.org/abs/2602.12430) — Three-level progressive disclosure; 26.1% of 42,447 community skills contain vulnerabilities.
17. Li et al. (2026). *SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks.* [arXiv:2602.12670](https://arxiv.org/abs/2602.12670) — v4 (2026-06-14): 87 tasks × 18 configs; curated Skills +16.6pp (33.9→50.5%); ≤3 focused modules beat exhaustive bundles (≥4 modules +10.1pp vs +19.0pp); self-generated Skills land below the no-Skills baseline on all tested configs (−8.1…−11.5pp).
18. Galster et al. (2026). *Harness Engineering for Agentic AI Coding Tools: An Exploratory Study.* [arXiv:2602.14690](https://arxiv.org/abs/2602.14690) — v5 retitle of *Configuring Agentic AI Coding Tools*; 2,853-repo sample; 95% of Skills within 500-line budget; reference-over-duplication pattern.
19. Vasilopoulos (2026). *Codified Context: Infrastructure for AI Agents in a Complex Codebase.* [arXiv:2602.20478](https://arxiv.org/abs/2602.20478) — Three-tier context system (~660/~9,300/~16,250 lines); drift detector against Git commits; "explained twice → write it down".
20. Pollertlam & Kornsuwannawit (2026). *Beyond the Context Window: A Cost-Performance Analysis of Fact-Based Memory vs. Long-Context LLMs for Persistent Agents.* [arXiv:2603.04814](https://arxiv.org/abs/2603.04814) — Long-context beats fact-extracted memory by 33–35pp on two of three benchmarks; retrieval wins only after ~10 reuses.
21. Liu et al. (2026). *A Scalable Benchmark for Repository-Oriented Long-Horizon Conversational Context Management.* [arXiv:2603.06358](https://arxiv.org/abs/2603.06358) — LoCoEval benchmark; composite text+path memory (Mem0R 62.22%) beats pure-text (Vanilla RAG 52.22%) on multi-hop repo tasks.
22. Vishnyakova (2026). *Context Engineering: From Prompts to Corporate Multi-Agent Architecture.* [arXiv:2603.09619](https://arxiv.org/abs/2603.09619) — Four context-rot modes (poisoning, distraction, confusion, clash); provenance and privilege-attenuation criteria.
23. Zheng et al. (2026). *SkillRouter: Skill Routing for LLM Agents at Scale.* [arXiv:2603.22455](https://arxiv.org/abs/2603.22455) — Hiding skill body from routing at 80K-skill scale costs 31–44 pp Hit@1; its surface-keyword routing traps motivate function-anchored skill names.
24. Li, Wu, Ling, Cui, Luo (2026). *Towards Secure Agent Skills: Architecture, Threat Taxonomy, and Security Analysis.* [arXiv:2604.02837](https://arxiv.org/abs/2604.02837) — 7 threat categories × 17 scenarios; ClawHavoc compromised 1,184 skills; YAML frontmatter is not a contract.
25. Farajijobehdar, Köseoğlu Sarı, Üre, Zeydan (2026). *Tokalator: A Context Engineering Toolkit for AI Coding Assistants.* [arXiv:2604.08290](https://arxiv.org/abs/2604.08290) — Instruction-file token accounting; prompt-caching break-even at n*=2 reuses; O(T²) history growth.
26. Li et al. (2026). *Escaping the Context Bottleneck: Active Context Curation for LLM Agents via Reinforcement Learning.* [arXiv:2604.11462](https://arxiv.org/abs/2604.11462) — DOM contains >90% structural noise; similarity retrieval "frequently fail[s] to retrieve implicit reasoning anchors" — causally essential context needs curation, not similarity lookup.
27. Liu, Zhao, Shang, Shen (2026). *Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems.* [arXiv:2604.14228](https://arxiv.org/abs/2604.14228) — Peer-academic analysis of Claude Code internals; cost ordering `hooks < skills < plugins < MCP`; `parseSkillFrontmatterFields` parses 15+ fields including model/effort overrides.
28. Hong, Troynikov, Huber (2025). *Context Rot: How Increasing Input Tokens Impacts LLM Performance.* [trychroma.com/research/context-rot](https://www.trychroma.com/research/context-rot) — 18-model study; non-uniform degradation with input length; single distractor reduces accuracy.
29. Liu et al. (2026). *Agent Skills in the Wild: An Empirical Study of Security Vulnerabilities at Scale.* [arXiv:2601.10338](https://arxiv.org/abs/2601.10338) — Primary SkillScan study: 42,447 skills collected / 31,132 analyzed; 26.1% with ≥1 vulnerability across 14 patterns; script-bundling 2.12× (OR=2.12, p<0.001).
30. Liu et al. (2026). *"Do Not Mention This to the User": Detecting and Understanding Malicious Agent Skills.* [arXiv:2602.06547](https://arxiv.org/abs/2602.06547) — 157 confirmed-malicious among 98,380 registry skills; 4.03 vulnerabilities each; 54.1% from one actor via templated brand impersonation.
31. Zhang et al. (2026). *CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification.* [arXiv:2604.01687](https://arxiv.org/abs/2604.01687) — Verification-gated iteration reaches 71.1% pass vs 53.5% human-curated and 32.0% one-shot self-generation on SkillsBench.
32. Abdelnabi & Bagdasarian (2026). *AI Agents May Always Fall for Prompt Injections.* [arXiv:2605.17634](https://arxiv.org/abs/2605.17634) — Contextual-integrity argument: no fixed policy blocks all context-based attacks without blocking legitimate flows; injection defense is risk reduction, not elimination.
33. Yang et al. (2026). *SkillOpt: Executive Strategy for Self-Evolving Agent Skills.* [arXiv:2605.23904](https://arxiv.org/abs/2605.23904) — Bounded add/delete/replace skill edits gated on held-out validation beat human-authored skills on all 52 cells; median deployed skill ~920 tokens.
34. Ji et al. (2026). *Cloak and Detonate: Scanner Evasion and Dynamic Detection of Agent Skill Malware.* [arXiv:2607.02357](https://arxiv.org/abs/2607.02357) — Payload-preserving evasion defeats install-time scanning: self-extracting-skill packing bypasses all eight tested scanners at >90%; a runtime taint-tracking auditor detects 97% at 2% false positives — a scan pass is not evidence of safety.
35. Snyk (2026). *ToxicSkills: Malicious AI Agent Skills on ClawHub.* [snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) — 3,984 skills scanned: 36.82% with ≥1 flaw, 76 confirmed-malicious payloads; three lines of SKILL.md markdown sufficed for SSH-key exfiltration.

## License

Apache 2.0
