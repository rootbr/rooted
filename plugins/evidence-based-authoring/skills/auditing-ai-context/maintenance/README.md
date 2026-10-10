# Maintaining auditing-ai-context

Nothing under `maintenance/` is read or executed in a run of the audit. Paths are relative to the skill directory; `../../agents/` is the plugin's agent directory.

- Add to an existing section if conceptually fits; new section only when no match (verified on this repo's own context files; the dated record lives in the research log).
- Merge exact duplicates immediately (exact only — never bulk-paraphrase, per ACE).
- After codebase changes: grep context files for references to renamed/removed entities (R-73).
- Pin model version in evals; re-run on every model upgrade (Yang §3.3: minor model bump silently dropped one rule's compliance by 48%). On upgrade, first try *removing* scaffolding and prescriptive language — skills authored for prior models are often too prescriptive for newer tiers (G-25).
- When iterating a skill against eval results, apply bounded add/delete/replace edits and accept each only if a held-out validation set improves; keep rejected edits as negative feedback (SkillOpt 2605.23904 §3.4–3.5).
- On every body edit that changes scope (new tool, new file access, new external call), update description in the same commit (R-77).
- A rule is one card in `references/rule-cards/`; adding or removing one means adding/removing its card plus its `maintenance/rule-cards-provenance.md` line (and a `maintenance/rule-cards-taxonomy.md` value if a facet is new). When the ownership map, patch format, or sub-agent prompt changes, update `scripts/audit-workflow.js` (its `DEFER_TO`, `GROUP_PRIORITY`, `PATCH_SCHEMA`, `prompt()`) and `../../agents/audit-subagent.md` / `../../agents/audit-indexer.md` in the same commit — the script encodes this skill's contract. A mechanical validator changed on a card covered by the static pre-pass means the same change in `scripts/static-audit.py`.
- A new `rule_id` prefix earns a `groupOf()` branch and a `GROUP_PRIORITY` tier in the same commit as its first card; the function throws on an unmapped prefix rather than letting it inherit safety priority and win every conflict it enters. A new target type earns a `TARGET_TYPES` entry in both scripts and a check set in `scripts/static-audit.py`. Widening a card's `applies_to_target` means re-reading the dispatch bullets of SKILL.md §Phase 1, which paraphrase the facets and go stale silently.
- Anchor tokens in runtime files (`R-xx`, `G-xx`, `claude-code#NNNNN`, `house convention`) stay one-token — `maintenance/maintenance-map.md` decodes them for reviewers and keeps the living dossiers of volatile dependencies with their flip sites.
- Capture developer knowledge not found in docs or source code — context files measurably help only as the sole source: with repo docs removed they flip from net-negative to +2.7% (Gloaguen App. B).

## Layout

- `maintenance/rule-cards-provenance.md` — one line per rule card, keyed by `rule_id`: its source, origin and ownership.
- `maintenance/rule-cards-taxonomy.md` — the card schema and the controlled vocabulary of every facet.
- `maintenance/maintenance-map.md` — the legend of the anchor tokens runtime files carry and the dossiers of volatile dependencies with their flip sites.

Who reads or runs every other file of the skill, and when: `README.md` §Layout.
