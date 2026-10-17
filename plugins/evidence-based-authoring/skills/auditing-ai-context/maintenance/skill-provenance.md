# Provenance of the auditing-ai-context run set outside the rule cards

One line per source reference that backs a claim in `SKILL.md`, `references/gotchas.md` or `references/kb-card-specification.md`, keyed by the gotcha id or by the file and section, so that the run-set line and its provenance line together carry everything known. Each line holds the citation as it stood in the run-set text — author, short title, id or URL, section — then the claim it backs. A rule card's sources stand on its line in `rule-cards-provenance.md`; the anchor tokens `R-xx`, `G-xx`, `claude-code#NNNNN` and `house convention` are decoded in `maintenance-map.md`.

## SKILL.md

- **SKILL.md § When this skill is invoked** · Yang 2505.13360 §3.4 — the bundling tax that a single-pass holistic review pays.
- **SKILL.md § When this skill is invoked** · Liang 2410.21647 §4.2 — GPT-4o pass@1 below 10% past 232 generated tokens on repo-level code; the extrapolation to review output is a house inference.
- **SKILL.md § Phase 1**, and the same caveat in the plugin's `agents/audit-subagent.md` and `agents/audit-indexer.md` · Anthropic, Claude Code workflows docs; claude-code#63762 — the workflow runtime ignores agent `tools:` allowlists, so its sub-agents run with `Write`/`Edit` granted and edits auto-approved; `maintenance-map.md` § claude-code#63762 holds the record.
- **SKILL.md § Phase 3** · Li 2604.02837 §7.1 — human review of the Phase 2 summary is the last line of defense against injection-biased patches.

## references/gotchas.md

- **gotchas header** · house convention, no owning R-rule — a retired entry keeps its number vacant.
- **G-01** · SkillRouter 2603.22455 Appendix D — the 31.8pp Hit@1 gap of description-only routing against full-body routing.
- **G-02** · Anthropic skill-creator guidance — agents follow reasons better than edicts.
- **G-03** · vendor authoring convention — `description` in the third person; first or second person breaks routing.
- **G-04** · Promptomatix §B.1.1 — positive framing holds for the body.
- **G-05** · Li 2602.12670 v4 §5.1.1, App. D.6 — self-generated Skills below the no-Skills baseline (−8.1pp Claude Code+Opus 4.7, −11.3pp Codex+GPT-5.5, −11.5pp Gemini CLI+Gemini 3.1 Pro); curated Skills +18.2 to +24.8pp.
- **G-05** · Gloaguen 2602.11988 §4.2 — +20–23% inference cost for −0.5% to −2% success.
- **G-05** · CoEvoSkills 2604.01687 §4.2 — 71.1% pass against 53.5% human-curated and 32.0% one-shot.
- **G-05** · SkillOpt 2605.23904 §3.5, §4.1 — bounded edits accepted only on held-out validation improvement beat human-authored skills on all 52 cells.
- **G-05** · SWE-Skills-Bench 2603.15401, abstract — 39 of 49 public skills with zero pass-rate improvement on end-to-end SWE tasks; average +1.2%; three degraded to −10%; token overhead up to +451%.
- **G-06** · Liu 2601.10338 §1, the primary scan; surveyed in Xu & Yan 2602.12430 §6.2 — ~26.1% of 42,447 community skills vulnerable; data exfiltration 13.3%, privilege escalation 11.8%; script-bundling skills 2.12× more vulnerable; ClawHavoc over 1,184 compromised skills.
- **G-07** · Anthropic, Skill authoring best practices — nested references are previewed (`head -100`) rather than read in full.
- **G-08** · Dong 2512.14754 §3.1 — numeric edits degrade reliability more than rephrasing.
- **G-09** · Yang 2505.13360 §3.4 (cited in the entry as "Yang §3.4") — 98.7% in isolation, 85% bundled with 18 others; 37.5% of rules lose more than 5pp.
- **G-10** · Khan 2510.22251 §4.2, §4.4 — prohibitions lifted GPT-4o 93→97% and dropped GPT-5 96.36→94%; only OpenAI models tested.
- **G-11** · 2604.02837 §3.1 (Li, as SKILL.md cites the same id) — routing has no mechanism to verify that the body stays within the description's claims.
- **G-12** · Liu 2604.14228 §6.1, §6.3 — skill bodies lazy-load on activation.
- **G-13** · Dong 2512.14754 Table 2 (cited in the entry as "Dong Table 2") — self-confidence AUROC 0.549, perplexity 0.497.
- **G-14** · Lindenbauer 2508.21433 §5.1, v3 — the optimal masking window M=10 on SWE-agent against M=58 on OpenHands.
- **G-15** · Vishnyakova 2603.09619 §9, relaying Breunig 2025 — the four failure modes of context rot.
- **G-15** · Laban 2505.06120, abstract; decomposition from its 200,000-conversation analysis — sharded conversations drop quality 39% on average across six generation tasks; aptitude −15%, unreliability +112%.
- **G-16** · Nair 2506.00178 Table 4 — multi-round adversarial debate (d=3) beats a single judge at an 81.7–95% win rate.
- **G-17** · Xu & Yan 2602.12430 §7 (cited in the entry as "Xu & Yan §7") — multi-skill orchestration remains underdeveloped.
- **G-18** · 2604.02837 §7.1 — direct prompt injection remains an open problem.
- **G-18** · Abdelnabi 2605.17634 §4.4 — argues that no fixed policy blocks all context-based attacks without also blocking legitimate flows.
- **G-20** · verified hands-on; dated record in the research log — an inventory misreported a description length by counting its YAML prefix.
- **G-21** · house inference from the shared-inventory design — a Phase 0 misclassification cascades into every group.
- **G-22** · Anthropic, Claude Code workflows docs — the fallback to manual parallel dispatch.
- **G-24** · Anthropic, Claude Code workflows docs ("File edits are auto-approved"); claude-code#63762, disk-verified 2026-05 — workflow sub-agents run with declared ∪ {Write, Edit}.
- **G-25** · Anthropic, Claude prompting best practices + per-model guides + model-config docs, 2026 — literal instruction following of newer generations, the `reasoning_extraction` refusal category, effort names calibrated per model.
- **G-26** · Anthropic, "How we contain Claude", 2026 — persistent context as an injection persistence vector.
- **G-27** · verified hands-on 2026-07-26 — the session agent registry lists both agent types namespaced.
- **G-27** · disk-verified 2026-07-26 — the cached plugin copy keeps failing until commit → push → marketplace update.
- **G-28** · verified hands-on 2026-08-08 — the persisted run record stores `args` as one JSON string and the wrapper crashed at its first field access.

## references/kb-card-specification.md

The same file ships byte-identical in `reading-companion/references/`; this map serves both copies.

- **kb-card-specification § Authoring rules C-B1** · zettelkasten.de, "Atomicity", zettelkasten.de/atomicity/guide/; Matuschak, A., "Evergreen notes should be atomic", notes.andymatuschak.org/Evergreen_notes_should_be_atomic — "one idea and one idea only"; "the entirety of that thing".
- **kb-card-specification § Authoring rules C-B2** · Zhang, Q., et al., "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models" (ACE), arXiv:2510.04618 — accuracy 66.7 → 57.1 against the 63.7 no-context baseline.
- **kb-card-specification § Authoring rules C-B2, C-D3; § Principles item 2** · Anthropic, *Effective context engineering for AI agents* (2025), anthropic.com/engineering/effective-context-engineering-for-ai-agents — "the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome"; the right altitude; "minimal does not necessarily mean short".
- **kb-card-specification § Authoring rules C-C3** · Anthropic, *Contextual Retrieval* (2024), anthropic.com/news/contextual-retrieval — top-20 retrieval failure cut by 35%, 49% with lexical matching, 67% with reranking.
- **kb-card-specification § Authoring rules C-D3** · Anthropic, *Skill authoring best practices*, platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices — explain why, not only what.
- **kb-card-specification § Authoring rules C-E1** · Maynez, J., et al., "On Faithfulness and Factuality in Abstractive Summarization", *ACL 2020*, arXiv:2005.00661 — intrinsic hallucination; entailment tracks faithfulness better than n-gram overlap.
- **kb-card-specification § Principles item 1** · Chen, T., et al., "Dense X Retrieval: What Retrieval Granularity Should We Use?", *EMNLP 2024*, arXiv:2312.06648 — the proposition as indexing unit; up to +9–12 points Recall@5 with untuned retrievers.
- **kb-card-specification § Principles item 3** · zettelkasten.de, "Atomicity" — "not a rigid law, but a guiding compass"; Matuschak, "Evergreen notes should be atomic" — "only about one thing — but which, as much as possible, capture the entirety of that thing", "no clear litmus test". The formulation C-B1 follows, never its evidence: C-B1 rests on the Dense X Retrieval measurement.
