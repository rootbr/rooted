# G1 — Frontmatter & Routing

Sub-agent task: audit the target file's frontmatter and the routing-signal vocabulary in its body. Output JSON patches per `../SKILL.md#patch-format`. Do not edit.

## Why this group matters

The router never sees the body until the skill fires. Until then, the only signal is the YAML frontmatter — name and description — plus, on modern routers, a backing scan of the full body. SkillRouter (2603.22455 Fig 1, Appendix L.1) measured a 31–44 pp Hit@1 drop when bodies were hidden vs. exposed: routers *do* read bodies, but the frontmatter still gates whether the body is consulted. Frontmatter errors are silent — the skill never fires, the user never sees the failure, no log records the miss.

The skill triggers `reliable@10`: 10 paraphrased should-trigger prompts plus 10 should-not, all 20 must pass jointly (not majority). Dong 2512.14754 §2.2 measured up to 61.8 pp reliability collapse between nominal accuracy and reliable@10 — a description that triggers "usually" routes wrongly on cousin prompts in production.

---

## R-01 — `name` describes the function, not the surface topic

**Statement.** The skill's directory name and frontmatter `name` field must name the *function performed* (verb + object, or tool + mode), not the domain or asset type the skill operates on.

**Why.** Routers weigh name tokens at ~3% of total token mass but with disproportionate per-token influence (SkillRouter §L.1). A topic-named skill loses routing duels to function-named alternatives even when the body is more specific. Two case studies in the paper: renaming `video-tutorial-indexer` → `speech-to-text` lifted success 0/12 → 9/12; `software-dependency-audit` (generic) was beaten by `dependency-security`, and renaming to `trivy-offline-vulnerability-scanning` (tool + mode) lifted success 0/12 → 12/12.

**How to apply.** Decompose the name. Does it contain (a) a verb or gerund (the function), (b) a disambiguating qualifier (tool, mode, target type)? If only domain words ("auditing", "research", "documents") → flag.

**Bad → Good.**

```
bad:  video-tutorial-indexer        good: speech-to-text
bad:  software-dependency-audit     good: trivy-offline-vulnerability-scanning
bad:  pdf-helper                    good: pdf-extraction
bad:  java-skill                    good: reviewing-java
```

**Validator question.** Reading the name alone, can the router infer (a) what action is performed, (b) on what kind of input, (c) what distinguishes it from a sibling?

**Patch shape.**

```json
{
  "rule_id": "R-01",
  "location": {"section": "frontmatter", "field": "name"},
  "current": "<current name>",
  "proposed": "<verb-or-tool-anchored name>",
  "justification": "Generic topic name competes poorly against function-named alternatives.",
  "severity": "high"
}
```

---

## R-02 — `description` MUST be third person, ≤ 1024 chars, contain when-to-trigger AND when-NOT-to-trigger

**Statement.** Frontmatter `description` is pasted verbatim into the system prompt of the routing model. It must read as third-person prose, fit within 1024 characters (Anthropic auto-rejects longer), and explicitly name (a) what the skill does, (b) phrases / contexts that should trigger it, (c) one or more should-not-trigger contexts.

**Why.** Third person is the canonical routing voice — "I can…" or "you use this to…" degrades Hit@1 because the router models trained on third-person descriptors. Negative triggers ("NOT for Vue or Svelte") are the only place where prohibitions help: they shrink the should-trigger basin and prevent adjacent skills from being stolen by overly broad descriptions (G-18 in the parent skill: no runtime arbitration between simultaneously-triggered skills, so disjoint descriptions are the only safeguard).

**How to apply.** Parse the description:

1. Count characters. > 1024 → flag.
2. Voice check. First/second person ("I", "you", "we", "my") → flag.
3. Trigger phrasing. Look for "use this when", "use whenever", "triggers on", phrase-list of user-facing intents. Missing → flag.
4. Negative triggers. Look for "NOT for", "not for", "do not use for". Missing → flag.

**Bad → Good.**

```
bad:  "Helps with agent files."
      (vague, no triggers, no negative cases)

good: "Audit AI agent context files. Use this whenever the user creates, edits,
      or reviews CLAUDE.md, SKILL.md, or agent definitions; writes system prompts
      or LLM instructions; or edits .md files in .claude/ or .cursor/. NOT for
      auto-generating context files from scratch — LLM-generated files cost
      +20-23% tokens with −0.5% to −2% success."

bad:  "I help you write better SKILL.md files."
      (first person)

good: "Writes and audits SKILL.md, CLAUDE.md, and agent prompts…"
```

**Validator question.** Can a stranger reading only this description in isolation decide whether this skill should fire on a given prompt?

**Patch shape.**

```json
{
  "rule_id": "R-02",
  "location": {"section": "frontmatter", "field": "description"},
  "current": "<existing description>",
  "proposed": "<rewritten description>",
  "justification": "Specify failure: [too long | first-person | missing trigger list | missing NOT-for].",
  "severity": "high"
}
```

---

## R-03 — Body MUST carry routing-signal vocabulary

**Statement.** SKILL.md bodies are scanned by modern routers, not just descriptions. The body should mention tool names the agent will use, trigger verbs, file types, negative cases. Bodies that read like marketing copy with no concrete vocabulary lose Hit@1 by 31–44 pp (SkillRouter Fig 1).

**Why.** The router's text encoder hashes the *concrete tokens* — `gradle`, `pytest`, `.docx`, `RFC 2119`, `SkillTool`. Abstract phrasing ("optimize agent behavior", "improve quality") matches no concrete user prompt. Median effective body size for routing-positive skills is 704 words; bodies below ~400 words of substantive routing signal under-trigger.

**How to apply.** Inventory concrete tokens in the body: tool names, file extensions, framework names, command names, function verbs, error names. If fewer than ~30 such tokens, or if they only appear in headings, flag — body needs more concrete vocabulary.

**Bad → Good.**

```
bad:  "This skill helps the agent reason carefully about agent files
      and provides high-quality guidance for context engineering."
good: "Use this skill on CLAUDE.md, SKILL.md, AGENTS.md, copilot-instructions.md.
      Operates on .md files in .claude/, .cursor/, and similar AI config dirs.
      Tools used: Read, Grep, Glob. Concepts: progressive disclosure, KV-cache,
      reliable@10, cousin prompts, bundling tax."
```

**Validator question.** Does the body contain at least one concrete token for each of: tool names, file types, framework / spec names, trigger verbs the user would type?

**Patch shape.**

```json
{
  "rule_id": "R-03",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<abstract paragraph>",
  "proposed": "<same paragraph with concrete tool / file / framework tokens added>",
  "justification": "Routing signal under-specified; body should expose concrete tokens for the router to match.",
  "severity": "medium"
}
```

---

## R-04 — Frontmatter `description` MUST be self-contained — no cross-file references, deictic refs, or citations

**Statement.** Description text must not contain `see <other-file>`, `as documented in …`, "this skill", pronouns referring to absent context, or paper citations. At routing time the description is the *only* text the router sees — every dangling reference is opaque.

**Why.** Two failure modes: (a) the router cannot follow `see references/g4-pointers.md` — that file isn't loaded; (b) `this skill` is meaningless when 50 skill descriptions are pasted side by side in the router prompt. The description must read as standalone third-person prose.

**How to apply.** Search for: `see `, `documented in `, `as described `, `this skill `, `this tool`, `our `, citation pattern `(Author 2025)`, file paths inside the description. Each is a candidate.

**Bad → Good.**

```
bad:  "This skill audits agent files using rules from Yang 2505.13360 §3.4
      and Zhang 2510.04618. See references/ for the full rule set."

good: "Audits AI agent context files (CLAUDE.md, SKILL.md, agent prompts)
      for token budget, routing signal, sourcing, and anti-duplication. Use
      whenever the user edits an .md file containing agent instructions. NOT
      for auto-generating new agents from scratch."
```

**Validator question.** Cut the description out and paste it into a fresh chat — does it still parse as a complete statement of what / when / not-for?

**Patch shape.**

```json
{
  "rule_id": "R-04",
  "location": {"section": "frontmatter", "field": "description"},
  "current": "<description with cross-ref or deixis>",
  "proposed": "<rewritten self-contained description>",
  "justification": "Description must be standalone — router sees no other context.",
  "severity": "high"
}
```

---

## R-05 — Numeric thresholds in description MUST be locked; numeric edits and constraint reconfiguration degrade more than rephrasing

**Statement.** Numbers in a description (line counts, token counts, percent thresholds, version cutoffs) act as hard pivots for the router. Once a description says "≤ 500 lines", any cousin prompt that asks for 510 lines may fail to trigger. Either keep the number exact across all uses, or remove it from the description and let the body govern.

**Why.** Dong 2512.14754 §3.1 found numeric edits ("at most 600" vs "610") cause widespread reliability failures — far more than pure rephrasing. The model treats numbers as constraints rather than approximations.

**How to apply.** Extract every numeric value from the description. For each, ask: (a) is it the *real* threshold (a hard limit) or a rough guideline? (b) does it appear consistently in the body? Mismatches between description and body numbers are a routing footgun.

**Bad → Good.**

```
bad description:  "Use for files ≤ 600 lines."
   body:          "Audit any agent file regardless of length."

good description: "Use for agent context files of any length; primary cases are
                  CLAUDE.md, SKILL.md, and agent prompts."
```

**Validator question.** Is every numeric threshold in the description either (a) a true hard limit consistent with the body, or (b) absent — pushed into the body where it can be qualified?

**Patch shape.**

```json
{
  "rule_id": "R-05",
  "location": {"section": "frontmatter", "field": "description"},
  "current": "<description text containing the number>",
  "proposed": "<description with number removed or aligned with body>",
  "justification": "Numeric mismatch between description and body; cousin-prompt reliability risk (Dong §3.1).",
  "severity": "medium"
}
```

---

## R-06 — Body scope MUST NOT exceed description scope

**Statement.** Whatever tools the body invokes, files it touches, or external calls it makes, the description must advertise. A skill whose description says "audits .md files" but whose body silently calls a network endpoint or writes outside the cwd violates the implicit routing contract. Li 2604.02837 §3.1 notes the YAML frontmatter has no mechanism to verify body stays inside description scope — humans enforce.

**Why.** The router and the user both rely on description as the consent surface. Scope drift is invisible until the skill fires; by then the agent is already invoking the unexpected tool or path.

**How to apply.** Read the body looking for: tool invocations (Bash commands, network calls, file writes outside referenced paths), external integrations (MCP, APIs), modes of operation (read-only vs mutating). For each, check the description claims the capability. If not → either narrow the body or widen the description.

**Bad → Good.**

```
bad:  description: "Reviews .md files for AI agent context."
      body:        "…posts results to Slack channel #agents…"

good: description: "Reviews .md files for AI agent context and posts findings
                   to a Slack channel when configured."
      body:        "…posts results to Slack channel #agents…"
```

**Validator question.** For every tool / network / file-mutation behavior in the body, does the description explicitly grant it?

**Patch shape.**

```json
{
  "rule_id": "R-06",
  "location": {"section": "<body section where the unannounced behavior lives>", "line_hint": <int>},
  "current": "<unannounced behavior excerpt>",
  "proposed": "<either: 'Add to description: <...>' or 'Remove from body: <...>'>",
  "justification": "Body scope exceeds description; routing consent contract violated (Li 2604.02837 §3.1).",
  "severity": "high"
}
```

---

## Output protocol for this sub-agent

1. Read frontmatter first — verify name, description independently.
2. Walk body for routing signal (R-03) and scope drift (R-06).
3. Emit patches sorted by severity then by file order.
