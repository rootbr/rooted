# G4 — Content Pointers & Anti-Duplication

Sub-agent task: audit the target file for **how it references code, sources, and itself**. The recurring failures this group catches: real names left in place of generic placeholders, line-anchored references that rot on edit, the same rule stated twice in different sections.

Load this file as your sole rule set. Read the target file once. Emit a JSON patch array per `../SKILL.md#patch-format` covering every violation. Do not fix anything yourself — propose patches.

## Why this group fails most often

Three forces combine: (a) **bundling tax** — when 100+ rules sit in one prompt, individual rules at 98.7% isolated compliance drop to 85% in bundle (Yang 2505.13360 §3.4); (b) **state-once-then-reference** rules are *negative* checks (don't say it twice), and Yang §3.2 shows conditional / edge-case rules are inferred correctly only 22.9% of the time vs 70.7% for format defaults; (c) **placeholder substitution** is a transformation, not a recognition task, so the model can read the rule and still emit the violation.

The per-requirement validator pattern (Yang §A.6, 95.6% human–LLM agreement) is the antidote: one rule, one focused check, one patch.

---

## R-40 — Illustrative code references MUST use generic placeholders, not real identifiers

**Statement.** When a rule, anti-pattern, or example exists to *teach a pattern* rather than point to one specific call site, identifiers must be of the form `Class#method`, `<Module>.<function>`, `<service>/<endpoint>`. Real production names (`UserService.findById`, `OrderRepo.save`, `auth_middleware.py:42`) are reserved for direct pointers to that exact location.

**Why.** Real names couple the illustration to a single revision. Renames rot the example silently; readers also conflate "see this for the pattern" with "this is *the* implementation," weakening the abstraction (the existing SKILL.md notes this as "pattern-vs-pointer intent"). The skill itself already states the rule but applies it inconsistently — illustration of the exact failure mode you reported.

**How to apply.** For every code-shaped reference in the target file, classify:

| Intent | Form | Identifier policy |
|--|--|--|
| Teach a pattern | "Builder pattern: see `<Class>#<method>`" | Generic placeholders MUST be used |
| Point to a specific location | "Auth retry lives in `RetryPolicy#shouldRetry`" | Real name allowed, no line numbers |
| Quote a snippet | inline fenced block | Real names allowed inside the block, but the surrounding sentence MUST name the file path |

If intent is ambiguous, treat as illustrative and demand placeholders.

**Bad → Good.**

```
bad:  Builder pattern: see UserService.findById()
good: Builder pattern: see Class#method

bad:  Errors: throw OrderValidationError from PlaceOrderHandler.handle
good: Errors: Result<T, E> pattern. Throw <DomainError> subclasses from <UseCaseHandler>#handle

bad:  Retry policy: see backend/orders/src/main/java/com/acme/orders/RetryPolicy.java:142
good: Retry policy: see RetryPolicy#shouldRetry
```

**Validator question.** For each code-shaped identifier in the target file: is it pointing to *that exact entity* (pointer) or teaching a *class of entities* (pattern)? If pattern → must be generic. If pointer → must lack line numbers (R-41).

**Patch shape.**

```json
{
  "rule_id": "R-40",
  "location": {"section": "<section heading>", "line_hint": <int>},
  "current": "<exact substring containing the real-named reference>",
  "proposed": "<same sentence with the identifier replaced by Class#method or domain placeholder>",
  "justification": "Illustrative reference — pattern-vs-pointer intent.",
  "severity": "medium"
}
```

---

## R-41 — Source citations MUST use stable structural anchors, not page numbers, line numbers, or character offsets

**Statement.** Every external citation (book, paper, RFC, video, spec) MUST identify content by a structural anchor stable across editions, reflows, and renumbering. File-internal references MUST identify by symbol (method, class, function) not by line.

**Stable anchors, by source type:**

| Source | Stable anchor | Unstable surrogate |
|--|--|--|
| Book | Chapter title + § subsection heading; practice / exercise / figure number | Page number (drifts across editions, ebook reflow, PDF font scaling) |
| Paper | Section number (§N) + subsection name | Page; arxiv abs vs pdf URL |
| RFC | § number + section name | Page in PDF rendering |
| Video / podcast | Chapter title + speaker, optional `t=Hh:Mm` timestamp | Slider position, percentage |
| Repo file | `Class#method`, `<file>::<function>` | `<path>:<line>` |

A page or line MAY augment a stable anchor for convenience (`Practice #14, §"Verb-mixing ban" — p.110 in 2022 print`) but never replace it.

**Why.** Pages drift the moment the source is reformatted — German hardback, English Kindle, OCR PDF, and audiobook chapters all disagree about page 110. Line numbers in code rot on every edit above the cited line; `path:142` is wrong before the next commit. Pollertlam 2603.04814 §5.1 shows that flat fact-extraction "irretrievably loses" temporal markers and version metadata; the same loss happens when an anchor depends on rendering geometry rather than authored structure.

**How to apply.** Scan for `p.<digits>`, `page <digits>`, `:<digits>` after a path, `pp.<digits>-<digits>`, and bare `<digits>` following a citation. For each occurrence:

1. Is the surrounding citation already anchored to a chapter / § / symbol?
   - Yes → keep the page/line as supplement, no patch needed.
   - No → propose adding the stable anchor; leave the page/line as supplement if present.
2. Is the page/line the *only* locator?
   - Yes → propose a replacement that names the structural anchor.

**Bad → Good.**

```
bad:  See "Atomic Habits" p.142 for the cue–craving loop
good: See "Atomic Habits" Ch.3 §"How a Habit Works" for the cue–craving loop (p.142 in 2018 hardback)

bad:  Retry logic: src/main/java/com/acme/orders/RetryPolicy.java:142
good: Retry logic: see RetryPolicy#shouldRetry

bad:  Zhang §4.7 p.18
good: Zhang 2510.04618 §4.7 "KV-cache amortization"

bad:  Hong 2025 figure on page 6
good: Hong 2025 Fig. 3 "Position-vs-accuracy decay"
```

**Validator question.** For every citation: can a reader find the same content in a different edition / commit / rendering of the same source using the locator alone? If no → flag.

**Patch shape.**

```json
{
  "rule_id": "R-41",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<citation substring with page/line locator>",
  "proposed": "<citation with structural anchor; page/line as parenthetical if useful>",
  "justification": "Page / line locator unstable across editions or edits.",
  "severity": "high"
}
```

---

## R-42 — Cross-file path references MUST be repo-relative; absolute paths MUST NOT appear

**Statement.** Any path inside instruction prose (`see <file>`, "edit <file>", "located at <file>") must be relative to the repo root or to the file the rule is written in. Absolute paths (`/Users/aleksei/...`, `/home/...`, `C:\Users\...`) leak machine state into a portable artifact and break for every other user.

**Why.** Skills and CLAUDE.md propagate across machines, branches, and contributors. An absolute path is a leaked constant — it cannot survive a `git clone` to a different `$HOME`. The same logic applies to `~/projects/...` if the rest of the skill is repo-portable: prefer the form callers can copy verbatim.

**How to apply.** Grep for `/Users/`, `/home/`, `/opt/`, `C:\`, `~/`. For each hit inside instruction prose (not inside a literal block demonstrating a different concept):

- Is the path *inside* the same repo as the file being audited? → propose repo-relative form.
- Is it pointing at the user's home or another machine? → flag and ask whether the rule belongs in user-level CLAUDE.md (`~/.claude/CLAUDE.md`) instead.

**Bad → Good.**

```
bad:  Read /Users/aleksei/projects/rooted/plugins/evidence-based-authoring/skills/auditing-ai-context/SKILL.md
good: Read plugins/evidence-based-authoring/skills/auditing-ai-context/SKILL.md
good: Read ../SKILL.md   (when the reference itself lives in references/)

bad:  Settings: /Users/aleksei/.claude/settings.json
good: Settings: ~/.claude/settings.json   (only acceptable inside user-global CLAUDE.md; flag elsewhere)
```

**Validator question.** Could this path be checked into git and still resolve correctly on a fresh clone in another developer's `$HOME`?

**Patch shape.**

```json
{
  "rule_id": "R-42",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<absolute path substring>",
  "proposed": "<repo-relative or symbol-based equivalent>",
  "justification": "Absolute path leaks machine state; will break on clone or for other users.",
  "severity": "high"
}
```

---

## R-43 — State each fact once; downstream sections MUST reference, not restate

**Statement.** A factual claim, threshold, citation, or instruction may appear once in the file. Subsequent sections that depend on it MUST link by section name, rule ID, or short tag rather than repeat the wording.

**Why.** Duplication has three failure modes: (a) drift — one copy is updated, the other rots into a contradiction; (b) bundling tax — the same rule appearing twice consumes two slots in the model's attention budget, displacing distinct rules (Yang §3.4); (c) reader confusion — the reader cannot tell whether the second mention is reinforcement or a *different* rule. The skill's own Maintenance section already names this: "MUST merge exact duplicates immediately."

**How to apply.** Build a near-duplicate inventory across the file. Two passes:

1. **Exact-or-near-exact.** Sliding 6-gram match; threshold ≥ 0.85 Jaccard. Flag pairs.
2. **Semantic dupe.** Different surface form, same prescription. Detect via shared subject + verb + threshold. Example: "ALL-CAPS prohibitions ≤ 3 per SKILL.md" and "Target no more than 3 ALL-CAPS prohibitions" are the same rule.

For each duplicate pair, decide which copy is the canonical source:

| Tie-breaker | Pick |
|--|--|
| One copy is in a Principles / Definitions section, the other in a Checklist | Principles wins; Checklist references it by rule ID |
| One has the citation, the other does not | Cited copy wins |
| One is more compressed | Compressed copy wins (per *Token Economy*) |
| Both equivalent | First occurrence wins |

**Bad → Good.**

```
bad (two sections, same file):

  ## Token Economy
  Target ≤ 3 ALL-CAPS prohibitions per SKILL.md; everything else as SHOULD.

  ## Self-Review Checklist
  - Priority markers used consistently; ALL-CAPS prohibitions ≤ 3, each tied to safety / data integrity (not style)

good:

  ## Token Economy
  Target ≤ 3 ALL-CAPS prohibitions per SKILL.md; everything else as SHOULD. <R-62>

  ## Self-Review Checklist
  - Priority markers: see R-62
```

**Validator question.** For every flagged pair: are these two surface forms saying the same *prescriptive thing*? If yes → consolidate. If they prescribe different actions despite sharing vocabulary → leave both but tighten the wording so the distinction is visible.

**Patch shape.**

```json
{
  "rule_id": "R-43",
  "location": {"section": "<duplicate-instance heading>", "line_hint": <int>},
  "current": "<full duplicate sentence/bullet>",
  "proposed": "<reference form: 'see R-XX' or 'see §<canonical section>'>",
  "justification": "Restates <canonical section heading or R-ID>. Canonical retained; duplicate folded to reference.",
  "severity": "medium",
  "canonical_location": {"section": "<canonical heading>", "line_hint": <int>}
}
```

---

## R-44 — Cross-skill body references MUST NOT appear; descriptions MUST be self-contained

**Statement.** A SKILL.md may not assume another skill's body is loaded. Cross-references that read "see auditing-ai-context for stable-anchor rules" are inert at routing time — the referenced body is not in context until that other `SkillTool` fires.

**Why.** Liu 2604.14228 §6.3 establishes that `SkillTool` lazy-loads each skill's body on its own activation. The router sees only the frontmatter `description`. Inside a sibling skill's body you cannot rely on a peer's body being available — even if it loaded earlier in the session, compaction or sub-agent forking may have evicted it.

**How to apply.** Grep for `see <skill-name>` or `as documented in <skill-name>/SKILL.md` or any reference to another `SKILL.md` inside instruction prose. Each hit is one of:

- A description-level mention ("complements <other skill>") — acceptable in frontmatter only if the other skill's existence is the relevant fact, not its body.
- A body-level claim that depends on the other body's content — MUST be inlined or moved to a shared reference file under the calling skill.

**Bad → Good.**

```
bad:  Follow the placeholder rules from auditing-ai-context.
good: Use generic placeholders for illustrative code references (Class#method form, not real identifiers). See ../references/g4-pointers.md#R-40 for rationale.

bad:  Defer to evidence-based-authoring/SKILL.md on sourcing.
good: Every rule MUST trace to one of: peer-reviewed paper, technical standard, dated hands-on note. (Self-contained, no peer dependency.)
```

**Validator question.** If the reader has only this file in context — never having loaded the cross-referenced skill — can they still apply the rule? If no → inline or move into this skill's own references/.

**Patch shape.**

```json
{
  "rule_id": "R-44",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<cross-skill reference>",
  "proposed": "<inlined rule or pointer to this skill's references/ file>",
  "justification": "Cross-skill body not in context at routing time (Liu 2604.14228 §6.3).",
  "severity": "high"
}
```

---

## R-45 — Static inventories of project state (file lists, plugin lists, env-var dumps) MUST be replaced by discovery commands

**Statement.** Anything that enumerates project structure — directory trees, plugin catalogs, environment-variable dumps, dependency lists — must be replaced by a command or script that returns current state. Reasoning: the inventory rots on every change to the underlying state, and the skill cannot detect the rot.

**Why.** Empirical: Galster §5.1 across 2,631 repos shows CLAUDE.md / AGENTS.md files routinely list components that no longer exist. Gloaguen 2602.11988 §4.2 establishes that deleting README content from auto-generated AGENTS.md *improves* AGENTbench by ~4.7pp — duplication harms. The same applies to any list that the filesystem already answers.

**How to apply.** Flag any sequence ≥ 3 lines that enumerates files, directories, plugins, skills, env vars, ports, or dependencies. Two patches:

- If the list is *short* and the file is the system-of-record (e.g., a single canonical README) → keep.
- Otherwise → replace with `run \`<command>\` to view current <thing>`. Create the command if it does not exist and add it to `.claude/settings.json` permissions.allow.

**Bad → Good.**

```
bad:

  ## Plugins
  - plugin-a
  - plugin-b
  - plugin-c
  - …17 more lines…

good:

  ## Plugins
  Run `./overview.sh plugins` to list current plugins. Read individual plugin SKILL.md only when needed.
```

**Validator question.** Is this list the system-of-record, or a cached copy of something the filesystem / build system already knows? If cached → propose a discovery command.

**Patch shape.**

```json
{
  "rule_id": "R-45",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<full enumeration>",
  "proposed": "Run `<command>` to view current <thing>.",
  "justification": "Static inventory rots on every state change; discovery command returns ground truth.",
  "severity": "medium"
}
```

---

## R-46 — Cited code or text MUST be re-checked against the current source before emitting the patch

**Statement.** Before suggesting a fix that names a file, class, function, or external section, verify the named entity still exists. If the reference is to a paper / RFC / book section, the citation passes (you cannot fetch every source mid-audit); if it is to a repo entity, grep for the symbol before keeping the reference.

**Why.** Memory recall vs. ground truth — a recommendation that "the memory says X exists" is not the same as "X exists now." This is recorded in the parent harness (auto-memory section) but applies equally to skill-internal references: an audit that proposes "see UserService" when `UserService` was renamed last week is worse than no proposal.

**How to apply.** For every repo-internal pointer the audit *proposes*, run `grep -rn "<symbol>"` (sub-agents have Bash). Where the proposed pointer is to an entity that no longer exists, downgrade severity to `info` and emit a clarification patch asking the human reviewer to supply the new name.

**Validator question.** Does the symbol I'm proposing to point at exist in the current repo state?

**Patch shape.**

```json
{
  "rule_id": "R-46",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<existing reference to a removed/renamed entity>",
  "proposed": null,
  "justification": "Pointer target not found via grep; needs human to supply current name.",
  "severity": "info",
  "needs_human": true
}
```

---

## Output protocol for this sub-agent

1. Build a duplicate inventory of the file (R-43 prep) before reading other rules — duplicates inform which sections you cite as canonical.
2. Walk the file top-to-bottom once. For each candidate violation, emit one patch object.
3. Sort the final JSON array by `severity` (high → medium → info) then by `location.line_hint`.
4. Return the array to the main agent. Do not edit the file.
