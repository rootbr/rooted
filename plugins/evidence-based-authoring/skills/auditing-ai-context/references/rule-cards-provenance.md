# Rule-cards provenance map

Out-of-runtime maintainer record. The audit workflow does **not** pass this file to sub-agents — cards carry the rule, its numbers, and a compact `## Source` locator; this map carries the full citation, the origin, and the maintenance notes. Round-trip rule: a card plus its line here reconstruct everything known about the rule.

One line per card: `rule_id · source · origin-file · notes` (ownership / non-default `applies_to_target` / evidence caveat, where notable). `group` is derivable from `rule_id`; `confidence`/evidence strength is the caveat in the notes. The `origin` g1–g8 group files were removed once carded — git history preserves them; the cards are now canonical.

**Status: G1–G9 complete — 78 cards; 7 source rules without cards (table at end).**

---

## G1 — routing  ·  `applies_to_target: [skill, agent-prompt]` (CLAUDE.md / AGENTS.md are always-loaded, not routed)

- **R-01** · SkillRouter 2603.22455 App. C (`name` 3.0% tokens / 26.3% attention), App. L.1 (retrieval cases 0/12→9/12, 0/12→12/12; Case C counter-case 8/12 vs 4/12 in specialized domains; not renames), Limitations (scope: large registries with heavy overlap); Anthropic Agent Skills best practices (name spec: ≤64 chars, [a-z0-9-], no XML, no reserved words) · g1-routing.md · house: "name the function" inference
- **R-02** · Anthropic Agent Skills best practices (description spec: non-empty, ≤1024 chars, no XML tags — auto-reject); Dong 2512.14754 §2.2 (reliable@10, 61.8pp); Xu & Yan 2602.12430 §7 · g1-routing.md · moderate (voice/triggers = convention); owns description-field platform validity
- **R-03** · SkillRouter 2603.22455 §3 Fig 1 (31–44pp body ablation), App. A Table 7 (704-word median body) · g1-routing.md · house: ~30-token floor
- **R-04** · Liu 2604.14228 §6.1, §6.3 (skills lazy-load; cross-skill refs inert) · g1-routing.md · moderate (reasoned)
- **R-05** · Dong 2512.14754 §3.1 (numeric edits degrade reliability > rephrasing) · g1-routing.md · moderate (description-specific = extrapolation)
- **R-06** · Li 2604.02837 §3.1 (YAML frontmatter is not a contract) · g1-routing.md · moderate (qualitative)

## G2 — tiering  ·  default `[context-file, skill, agent-prompt]`

- **R-10** · Lulla 2601.20404 (triple −20.08% tokens); Li 2602.12670 v4 App. A.2 Fig. 7 + §5.1.3/App. F.2 Table 9; Galster 2602.14690 §6.2 (95% ≤500 lines) · g2-tiering.md · owns tier+budget+cold-ToC; house ~30%/budget thresholds
- **R-11** · ACE Zhang 2510.04618 §2.2 (18,282→122 tokens, 66.7%→57.1%, below baseline) · g2-tiering.md · owns format-vs-meaning compression; house safe/unsafe-transform taxonomy
- **R-13** · Lulla 2601.20404 (triple = inclusion criterion; partial untested) · g2-tiering.md · `[context-file]`
- **R-14** · Hong 2025 Context Rot (early-position retrieval; direction, not %) · g2-tiering.md · `[skill, agent-prompt]`; house ~30% cutoff
- **R-15** · Liang 2410.21647 §4.2 (GPT-4o pass@1 <10% past 232 tokens) · g2-tiering.md · `[skill, agent-prompt]`
- **R-16** · Tokalator 2604.08290 §1, Eq. 1 (O(T²); ~20-turn rot; provider-specific per §3.2.1, relaying Hong 2025); Gao & Peng 2510.16786 §1 · g2-tiering.md · `[skill, agent-prompt]`
- **R-17** · Lindenbauer 2508.21433 §1 (~84% of tokens); Bulle Labate 2511.22729 §3.1–3.2 (masking 50.9–57.1%; pointer ~7× measured / ~16,900× est) · g2-tiering.md · `[skill, agent-prompt]`; house `context: fork` mapping
- **R-18** · Pollertlam 2603.04814 §4.1 (33–35pp; PersonaMem v2 7.3pp), §4.3 (~10+ reuses) · g2-tiering.md · —

## G3 — structure  ·  default `[context-file, skill, agent-prompt]`

- **R-20** · Chatlatanagulchai 2509.14744 (median H1=1,H2=5,H3=9; H4 37/253) · g3-structure.md · moderate (descriptive survey)
- **R-21** · Hong 2025; ACE 2510.04618 §3.1 (itemized bullets > monolithic prose) · g3-structure.md · —
- **R-22** · Mohsenimofidi §4.2 (five styles); Yang 2505.13360 §3.2 (conditionals recovered 22.9%) · g3-structure.md · —
- **R-23** · Santos Section 5 (Mermaid 2/328 files) · g3-structure.md · low; example reworded (source had a nested ```mermaid fence)
- **R-25** · Chatlatanagulchai 2509.14744 (token-economy convention) · g3-structure.md · low
- **R-26** · Chatlatanagulchai 2509.14744 (horizontal-rule convention) · g3-structure.md · low
- **R-27** · Chatlatanagulchai 2509.14744 (emphasis convention; ~10 per 100 lines) · g3-structure.md · low
- **R-28** · Chatlatanagulchai 2509.14744 (contrast-pair convention) · g3-structure.md · low

## G4 — pointers  ·  default `[context-file, skill, agent-prompt]`

- **R-40** · authoring heuristic + verified hands-on (no academic cite) · g4-pointers.md · owns pattern-vs-pointer; low
- **R-41** · Pollertlam 2603.04814 §5.1 (flat extraction loses anchors) · g4-pointers.md · **owns stable anchors**
- **R-42** · verified hands-on (absolute paths break on clone); Anthropic Agent Skills best practices (anti-pattern "Avoid Windows-style paths" — forward slashes always) · g4-pointers.md · owns repo-relative paths + separator form; high (self-evident)
- **R-43** · Yang 2505.13360 §3.4 (a duplicate consumes two attention slots) · g4-pointers.md · **owns state-once / anti-dup**; defines `canonical_location`
- **R-44** · Liu 2604.14228 §6.3 (skills lazy-load) · g4-pointers.md · owns cross-skill body-ref prohibition
- **R-45** · Gloaguen 2602.11988 App. B Fig. 12 (+2.7% with all repo docs removed; anchor moved from §4.2 in v2) · g4-pointers.md · **owns discovery-cmds**; needs_human when a command must be created/allow-listed
- **R-46** · verified hands-on (renamed-symbol pointer worse than none) · g4-pointers.md · owns re-check-cited-code; low; severity info
- **R-47** · Anthropic, Skill authoring best practices (two-hop partial reads) · g4-pointers.md · **owns read-in-isolation**; `[skill]`

## G5 — sourcing  ·  default `[context-file, skill, agent-prompt]`

- **R-50** · repo CLAUDE.md Evidence-Based Rule; Yang 2505.13360 §3.4 (bundling tax) · g5-sourcing.md · owns source-presence; `needs_human` always (cannot invent a citation)
- **R-52** · Gloaguen 2602.11988 §4.2; Li 2602.12670 v4 §5.1.1 + App. D.6 · gate exemption SkillOpt 2605.23904 §3.5, CoEvoSkills 2604.01687 §4.2 · g5-sourcing.md · owns self-authoring audit; house signal-table threshold
- **R-54** · Yang 2505.13360 §3.3 (5.9% regress >20%, ~2×) · g5-sourcing.md · owns number-presence; mechanical
- **R-55** · convention (token economy) · g5-sourcing.md · house convention; low
- **R-56** · Maynez 2005.00661 (ACL 2020; entailment >> n-gram for faithfulness) · g5-sourcing.md · **owns faithfulness**; house four-drift table; `needs_human` when source not re-fetched
- **R-57** · Anthropic, Effective context engineering (smallest high-signal set) · g5-sourcing.md · **owns provenance-vs-finding**; house grep heuristic (ISO dates, tmp/ paths, run-IDs)

## G6 — constraints  ·  default `[context-file, skill, agent-prompt]`

- **R-60** · Khan 2510.22251 §4.2, §4.4 (+4 gpt-4o vs −2.4 GPT-5), §6.2.1, §6.3.2 (OpenAI-only; Claude-tier = extrapolation; implicit-rule recovery 44.7% vs 24.5%) · g6-constraints.md · owns density-vs-tier; semantic
- **R-61** · Promptomatix §B.1.1; Khan 2510.22251 §5.3 · g6-constraints.md · owns positive framing; house two-place exception
- **R-62** · Anthropic skill-creator guidance; Yang 2505.13360 §3.4 (bundling tax) · g6-constraints.md · owns ALL-CAPS count; house ≤3 ceiling
- **R-63** · RFC 2119 · g6-constraints.md · owns RFC-2119 keyword consistency; house NEVER/ALWAYS/ONLY-as-extensions
- **R-64** · Dong 2512.14754 §3.1 · g6-constraints.md · owns body-internal numeric consistency; shares Dong §3.1 with R-05 (description numbers) — dedupe by location
- **R-65** · Promptomatix §B.2.1 (vendor-grade: 2–3×, up to 40%) · g6-constraints.md · owns example count/format/order; low
- **R-66** · Dong 2512.14754 Fig 5 (cousin-augmented >45%) · g6-constraints.md · owns example realism; semantic
- **R-67** · Yang 2505.13360 §3.2 (70.7% vs 22.9%) · g6-constraints.md · owns conditional explicitness

## G7 — antipatterns  ·  default `[context-file, skill, agent-prompt]`; ownership none (whole-file failure modes)

- **R-70** · Hong 2025 (positional / primacy bias) · g7-antipatterns.md · house cluster-by-subject procedure
- **R-71** · Galster 2602.14690 §6.1 (301 CLAUDE→AGENTS refs; AGENTS dominant) · g7-antipatterns.md · `[context-file]`
- **R-72** · Yang 2505.13360 §3.4 (bundling tax) · g7-antipatterns.md · house 8+ trigger, 3–5 examples
- **R-73** · verified hands-on (pointers rot after rename/delete) · g7-antipatterns.md · house grep procedure; needs Bash + checkout
- **R-74** · Santos Section 5 (code in 17.68% of guideline sections) · g7-antipatterns.md · house line-count table
- **R-75** · ACE 2510.04618 §2.2 (paraphrase compression −9.6pp → refactor, not paraphrase) · g7-antipatterns.md · depends on Phase 0 over-budget flag
- **R-76** · Zheng §4 (~10% of 39,065 mined pairs near-dup) · g7-antipatterns.md · `[skill]`; house ≥70% overlap
- **R-77** · Yang 2505.13360 §3.3 (unspecified ~2× regress) · g7-antipatterns.md · `[skill, agent-prompt]`; needs git history

## G8 — security  ·  default `[context-file, skill, agent-prompt]`

- **R-80** · Promptomatix 2507.14241 §B.5.1 · g8-security.md · owns delimited-wrapping; `[+kb-card]`; severity high
- **R-81** · Promptomatix 2507.14241 §B.5.1 · g8-security.md · owns safety-tier placement
- **R-82** · Liu 2601.10338 §1 (script-bundling 2.12×, OR=2.12 p<0.001); OWASP AST07 · g8-security.md · owns script-doc gate + hash-pin; `[skill]`
- **R-83** · OWASP Agentic Skills Top 10 v1.0 AST03 (least privilege); claude-code#63762 (dynamic workflows grant Write/Edit regardless of `tools:`; disk-verified 2026-05) · g8-security.md · owns privilege attenuation; `[skill, agent-prompt]`; declarative layers on prose, never replaces
- **R-84** · Li 2604.02837 §3.3 (trust binds to identity); Ji 2607.02357 abstract (SFS packing bypasses all 8 tested scanners >90% — scan-pass ≠ safe) · g8-security.md · owns consent-diff; `[skill]`
- **R-85** · Li 2604.02837 §7.1; Abdelnabi 2605.17634 §3–4.4 (structural limit); Anthropic "How we contain Claude" 2026 (~93% of permission prompts approved — approval fatigue) · g8-security.md · owns human-gate; `[+kb-card]`; severity high

## G9 — kb-card  ·  default `[kb-card]`; ownership none; shared source `kb-card-specification.md` §Authoring rules + §Enforcement

- **C-A1** · Dense X Retrieval (Chen et al. EMNLP 2024) 2312.06648 (proposition is the indexing unit) · kb-card-specification.md · —
- **C-A2** · spec §A / §Terms (slug = stable link key; drift breaks navigation) · kb-card-specification.md · `[+kb-corpus]`
- **C-A3** · spec §A / §Enforcement (facets = retrieval index) · kb-card-specification.md · `[+kb-corpus]`
- **C-A4** · Anthropic Contextual Retrieval (recall@5 0.63 → 0.80) · kb-card-specification.md · high
- **C-A5** · Anthropic Effective context engineering (smallest high-signal set) · kb-card-specification.md · corpus deviation: a compact `## Source` is kept in-card
- **C-B1** · Ahrens 2017 / zettelkasten.de / Matuschak (one idea only) · kb-card-specification.md · —
- **C-B2** · ACE 2510.04618 (66.7→57.1 vs 63.7 baseline); Anthropic ("minimal ≠ short") · kb-card-specification.md · high
- **C-B3** · spec §B / §Enforcement (foundation for faithfulness + verification) · kb-card-specification.md · —
- **C-C1** · spec §C / §Enforcement (read with no source in context) · kb-card-specification.md · —
- **C-C2** · spec §C / §Enforcement (links enrich, never complete) · kb-card-specification.md · —
- **C-C3** · Anthropic Contextual Retrieval (situating cuts top-20 failure 35% / 49% / 67%) · kb-card-specification.md · high
- **C-D1** · spec §D / §Enforcement (serves a job, not a syllabus) · kb-card-specification.md · —
- **C-D2** · spec §D / §Enforcement (when / who / where bridge) · kb-card-specification.md · —
- **C-D3** · Anthropic Effective context engineering (right altitude); Skill authoring best practices (explain why) · kb-card-specification.md · —
- **C-E1** · Maynez 2005.00661 (ACL 2020; intrinsic hallucination; entailment >> overlap) · kb-card-specification.md · high
- **C-E2** · spec §E / §Enforcement (author-bound jargon is dead weight) · kb-card-specification.md · corpus deviation: compact `## Source` kept (prose stays attribution-free)
- **C-E3** · spec §E / §Enforcement (de-quantified claim is unfalsifiable) · kb-card-specification.md · —
- **C-F1** · spec §F / §Enforcement (one schema → predictable parse + grep) · kb-card-specification.md · —
- **C-F2** · spec §F / §Customization / §Enforcement (one block, one name per corpus) · kb-card-specification.md · —
- **C-F3** · spec §F / §Enforcement (machine-parseable; everyday domain) · kb-card-specification.md · —

---

## Rules without cards

Seven source rules are intentionally not carded — deference stubs and non-emitting meta-rules. Their effect is realized elsewhere; listed for round-trip completeness.

| Rule | Reason | Realized by |
|--|--|--|
| R-12 (state once) | deference stub | workflow `DEFER_TO` R-12 → R-43 (G4 card) |
| R-19 (static lists → discovery commands) | deference stub | `DEFER_TO` R-19 → R-45 (G4 card) |
| R-24 (load-bearing rules early) | deference stub | `DEFER_TO` R-24 → R-14 (G2 card) |
| R-51 (stable anchors, sourcing angle) | deference stub | `DEFER_TO` R-51 → R-41 (G4 card) |
| R-53 (failed-trajectory is the strongest source) | non-emitting (informs justifications) | folded into R-50's authoring guidance |
| R-78 (keep-and-refine default) | non-emitting (informs severity / needs_human) | the workflow aggregator + each card's `severity_default` |
| R-79 (duplicate content) | deference stub | `DEFER_TO` R-79 → R-43 (G4 card) |
