# G7 — Anti-Patterns & Maintenance

Sub-agent task: catch the structural and behavioral anti-patterns that survive other groups' checks. Emit JSON patches per `../SKILL.md#patch-format`.

## Why this group matters

The other groups check *positive* properties (right tier, right form, right citation). G7 catches *whole-file failure modes* that emerge from interaction across sections: silent contradictions, cross-file duplication, scope drift since the last edit, near-duplicate sibling skills that steal each other's activations.

These are detection-heavy: many require the discovery inventory from Phase 0 (which lists sections, claims, sibling skill descriptions). G7 reads that inventory before scanning the file.

---

## R-70 — Contradictions across sections MUST be resolved into one rule with explicit conditions

**Statement.** When two sections of the same file prescribe different actions for what appears to be the same situation, the file is in a contradictory state. Either (a) the situations actually differ and the rules need explicit conditions to make the distinction visible, or (b) one rule is stale and must be deleted.

**Why.** The model treats both rules as authoritative and oscillates between them, or — worse — picks the one that appears first or last by positional bias (Hong 2025). Reader trust collapses when the rules contradict.

**How to apply.** From the discovery inventory, retrieve the list of normative claims grouped by topic. For each cluster of claims sharing the same subject (e.g., "where to put architecture", "how to cite sources"), check whether the rules are consistent. If not → flag.

**Bad → Good.**

```
bad (Section A): "All architecture lives in CLAUDE.md."
bad (Section B): "Architecture details belong in dedicated reference files."

good:            "Cross-cutting architecture (data flow, component map) → CLAUDE.md.
                 Domain-specific architecture details → references/architecture-<domain>.md."
```

**Patch shape.**

```json
{
  "rule_id": "R-70",
  "location": {"section_a": "<heading>", "section_b": "<heading>"},
  "current": "<sentence A> // <sentence B>",
  "proposed": "<unified rule with explicit conditional>",
  "justification": "Contradiction between sections; model oscillates or picks by position.",
  "severity": "high"
}
```

---

## R-71 — Cross-file duplication: write once in AGENTS.md, reference from siblings

**Statement.** When CLAUDE.md, AGENTS.md, and copilot-instructions.md coexist in a repo, write conventions once in AGENTS.md and reference from the others. Galster §5.1 observed 311 outgoing CLAUDE.md → AGENTS.md references across 2,631 repos — AGENTS.md is the empirically dominant shared baseline.

**How to apply.** When auditing a file inside a repo with multiple AI-context files, request the discovery inventory's cross-file comparison. For each rule appearing in two or more files verbatim, propose consolidating in AGENTS.md with `see AGENTS.md#<anchor>` from the others.

**Patch shape.**

```json
{
  "rule_id": "R-71",
  "location": {"file": "<current file>", "duplicate_in": "<other file>", "section": "<heading>"},
  "current": "<duplicated content>",
  "proposed": "Consolidate canonical version in AGENTS.md; replace duplicates with `see AGENTS.md#<anchor>`.",
  "justification": "Cross-file duplication; AGENTS.md is empirical shared baseline (Galster §5.1).",
  "severity": "medium"
}
```

---

## R-72 — 50 if-then edge cases MUST become 3–5 canonical examples + heuristic

**Statement.** Long flat lists of edge-case rules ("if X1 then Y1; if X2 then Y2; …") indicate missing generalization. Replace with 3–5 representative examples plus the declarative heuristic that generates them.

**Why.** Bundling tax (Yang §3.4): each independent if-then rule adds to the bundle, displacing other rules. A heuristic + examples expresses the same coverage in 1/10 the tokens with better edge-case generalization.

**How to apply.** Search for runs of 8+ sequential conditional bullets in the same section. For each run, propose a heuristic + 3–5 examples replacement.

**Patch shape.**

```json
{
  "rule_id": "R-72",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<flat list of N conditional rules>",
  "proposed": "<heuristic + 3-5 examples>",
  "justification": "Flat conditional list; bundling tax + missed generalization.",
  "severity": "medium"
}
```

---

## R-73 — Stale references to renamed/removed entities

**Statement.** After repo changes, references to renamed methods, deleted files, or removed packages rot silently. The skill itself prescribes: "After every significant codebase change: grep context files for references to renamed/removed entities."

**How to apply.** Inventory the file's pointers to in-repo entities (`<Class>#<method>`, `<file>::<function>`, repo-relative paths). For each, grep:

```
grep -rn "<symbol>" <repo-root> -l
```

If no match → flag as stale.

**Patch shape.**

```json
{
  "rule_id": "R-73",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<reference to entity not found>",
  "proposed": null,
  "justification": "Reference target absent in current repo state; needs human to supply current name or delete rule.",
  "severity": "medium",
  "needs_human": true
}
```

---

## R-74 — Pasted code snippets replaced with pointers

**Statement.** Code examples appear in 17.68% of Development Guidelines sections in the wild (Santos §4.3) — minimal illustrative snippets are acceptable when a pointer is insufficient. But pasted snippets of *project code* duplicate the source of truth; they rot when the project changes.

**How to apply.** For each fenced code block, classify:

| Source | Verdict |
|--|--|
| Generic / language-syntax illustration | Keep |
| Project-specific code, > 10 lines | Replace with pointer (`see <Class>#<method>`) |
| Project-specific code, ≤ 10 lines, teaching a pattern | Replace with pointer + brief inline summary |

**Patch shape.**

```json
{
  "rule_id": "R-74",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<code block>",
  "proposed": "<pointer + optional 1-2 line description>",
  "justification": "Pasted project code rots on edit; pointer keeps the audit aligned with source.",
  "severity": "low"
}
```

---

## R-75 — Files that only grow MUST be reviewed when over budget

**Statement.** A file that has only appended for many edits will eventually outgrow its tier budget. When the file exceeds the budget (R-10), G7 emits a maintenance patch proposing a review.

**Important distinction from G2 R-11:** the review proposes *refactoring* (split sections, demote to cold tier, drop unsourced bullets) — not paraphrase compression (which collapses accuracy per ACE).

**Patch shape.**

```json
{
  "rule_id": "R-75",
  "location": {"file": "<path>"},
  "current": "<line count> / <token estimate> (over budget)",
  "proposed": "Refactor pass: <list 3–5 candidate sections for demotion or split>.",
  "justification": "Over budget; refactor needed (split / demote / cut unsourced — not paraphrase, per ACE).",
  "severity": "medium"
}
```

---

## R-76 — Near-duplicate sibling skills cause router false negatives

**Statement.** Zheng §4 observed that near-duplicate skills in a catalog cause router false negatives beyond what exact-dupe merging catches. When two skills have semantically overlapping descriptions, the router may pick neither, or oscillate. Audit for semantic overlap; consolidate or sharpen name / description to create routing separation.

**How to apply.** Discovery inventory provides sibling skill descriptions in the same plugin / marketplace. For each pair (current_skill, sibling): compute semantic similarity (subject + action + target overlap). If ≥ 70% overlap → flag.

**Patch shape.**

```json
{
  "rule_id": "R-76",
  "location": {"current_skill": "<name>", "sibling": "<sibling-name>"},
  "current": "<overlap summary>",
  "proposed": "<sharpen description: add disambiguating term | mark NOT-for sibling's domain | consolidate>",
  "justification": "Semantic overlap with sibling causes router false negatives (Zheng §4).",
  "severity": "medium"
}
```

---

## R-77 — Body scope and description scope MUST stay synchronized across commits

**Statement.** On every body edit that changes scope (new tool, new file access, new external call), the description MUST be updated in the same commit. Drift between body and description is detectable by diffing both across the last N commits — if body changed and description didn't, scope drift is likely.

**Why.** Yang §3.3: unspecified requirements are ~2× more likely to regress across model / prompt changes. A description that doesn't advertise a new body capability is an unspecified requirement.

**How to apply.** If git history is available (sub-agents have Bash):

```
git log -p --follow <path-to-SKILL.md>
```

Inspect the last 5 commits. For each, check whether changes to body section text are mirrored in description changes. If body grew capabilities while description stayed static → flag.

**Patch shape.**

```json
{
  "rule_id": "R-77",
  "location": {"file": "<path>", "commit_range": "<sha>..HEAD"},
  "current": "Body changes: <summary>; description unchanged",
  "proposed": "Update description to advertise <new capability>.",
  "justification": "Scope drift since <sha>; description-body mismatch creates unspecified-requirement risk (Yang §3.3).",
  "severity": "medium",
  "needs_human": true
}
```

`needs_human: true` because the sub-agent should not silently change the description — the author confirms scope.

---

## R-78 — Default for accumulated playbook bullets is keep-and-refine

**Statement.** ACE (Zhang §2.2) showed that bulk paraphrase compression drops accuracy 9.6pp. Default for established playbook bullets is keep-and-refine, not delete. Default for unsourced prose is cut. G7 distinguishes:

| Category | Default action |
|--|--|
| Sourced bullet, ≥ 1 model interaction validated | Keep; consider refine for clarity |
| Sourced bullet, brand new | Keep |
| Unsourced bullet, in playbook ≥ 3 versions | Keep; mark provisional |
| Unsourced bullet, recent addition | Cut (after author confirms via R-50) |
| Verbose prose, low information density | Refactor to bullet / table |

**How to apply.** No direct patch; this rule informs the *severity* and *needs_human* fields of patches emitted by other rules. When G5 R-50 flags an unsourced bullet, G7 looks up bullet provenance (git blame); if recent → `severity: medium`; if old → `severity: low` + `needs_human: true`.

---

## R-79 — Same content stated more than once: keep best, delete the rest

**Statement.** See R-43 in G4 — anti-duplication is owned there. G7 cross-checks: when G4 reports a duplicate, G7 verifies the *canonical* choice respects R-78 priorities. If G4 chose to keep the wrong copy (e.g., kept the unsourced version), G7 emits a follow-up patch correcting the choice.

---

## Output protocol for this sub-agent

1. Consume the Phase 0 discovery inventory before scanning the file — anti-pattern detection is cross-section by nature.
2. Run grep checks for stale references (R-73) if Bash is available.
3. Inspect git log if available (R-77).
4. Cross-reference with sibling skills (R-76).
5. Emit patches sorted by severity; do not duplicate G4 R-43 duplicate-report.
