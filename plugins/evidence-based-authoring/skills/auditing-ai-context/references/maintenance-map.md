# Maintenance map — anchor legend & volatile dependencies

Out-of-runtime maintainer doc, same class as `rule-cards-provenance.md` and `rule-cards-taxonomy.md`: the audit workflow does not pass this file to sub-agents. It decodes the compact anchor tokens that runtime files carry, and it is the living record of volatile external dependencies — what they mean, how to re-verify them, and which files to flip when they change. Runtime files keep only the one-token anchors: they are the grep keys and the minimal in-file traceability (R-50); everything longer lives here.

## Anchor legend — what a token is and how to review it

| Token class | What it is | Full record | How to verify |
|---|---|---|---|
| `R-01`…`R-85` | audit rule for context files / skills / agent prompts | its card `rule-cards/r-XX--*.md`; full citation, ownership, evidence caveats in `rule-cards-provenance.md` | read the card's Thesis + Source; cross-check the provenance line |
| `C-A1`…`C-F3` | audit rule for KB cards | same pattern (`rule-cards/c-XX--*.md` + provenance) | same |
| `G-01`…`G-26` | symptom-indexed gotcha | `gotchas.md` — each entry carries its own source inline | read the entry; verify its source as below |
| `<Author> <arXiv-ID> §x` / `Table N` / `abstract` | academic source with a structural anchor | provenance line (card rules) or README §References | fetch `arxiv.org/abs/<ID>`; confirm the anchored section states the claim as written (R-56: entailment, not vibes) |
| `Anthropic, <doc name>` | vendor doc (platform.claude.com / code.claude.com) | named inline; no separate record | fetch the named doc; vendor pages are versionless — on mismatch treat as drift and re-anchor |
| `RFC NNNN` | technical standard | named inline | rfc-editor.org |
| `claude-code#NNNNN` | Claude Code GitHub issue pinning a volatile runtime behavior | dossier below | `gh api repos/anthropics/claude-code/issues/NNNNN --jq '{state,state_reason}'`; re-read the linked doc |
| `house convention` / `verified hands-on` | author-verified practice | dated record in `research/` logs | find the dated entry; if none exists, that is an R-50 finding |

## Volatile dependencies

### claude-code#63762 — workflow runtime ignores agent `tools:` allowlists

- **Claim pinned by the anchor:** dynamic-workflow sub-agents run in `acceptEdits` with `declared ∪ {Write, Edit}` and file edits auto-approved, regardless of the agent's `tools:` frontmatter. The Task/Agent-tool dispatch path *does* enforce allowlists.
- **Evidence:** Claude Code workflows doc ("The subagents the workflow spawns always run in acceptEdits mode … File edits are auto-approved"); issue closed as *not planned* 2026-07-02; disk-verified reproduction (dated record in the research log).
- **Re-verify:** `gh api repos/anthropics/claude-code/issues/63762 --jq '{state,state_reason}'` plus the workflows doc; a fresh repro is a one-file workflow that attempts an Edit from a `tools: Read`-only agent.
- **Flip condition:** a release enforces agent `tools:` inside workflows, or `agent()` gains a `tools` option.
- **Flip sites** (`grep -r 63762` — keep this list in sync):
  1. `../SKILL.md` §Phase 1 — enforcement caveat paragraph
  2. `gotchas.md` G-24
  3. `rule-cards/r-83--sub-skills-get-attenuated-privileges.md` — Source (Limits carries the caveat in prose, without the token)
  4. `../../../agents/audit-subagent.md` — load-bearing prohibition sentence
  5. `../../../agents/audit-indexer.md` — allowlist-is-not-a-barrier sentence
  6. `../scripts/audit-workflow.js` — header comment + `main_agent_followups` integrity entry
  7. `rule-cards-provenance.md` — R-83 line (citation record)
- **On flip:** declarative allowlists become the hard barrier on both dispatch paths — demote the prompt prohibitions to defense-in-depth, relax the mandatory Phase 2b integrity check to a spot-check, and rewrite G-24 as a historical note or retire its number.
