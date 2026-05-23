# G3 — Document Structure & Form

Sub-agent task: audit headings, list-vs-prose choice, instruction-style mix, topology rendering, and load-bearing-rule placement. Output JSON patches per `../SKILL.md#patch-format`.

## Why this group matters

Two empirical results govern this group:

- **Shuffled / discrete content beats logically structured prose for reference material.** Hong 2025 Context Rot: "structural coherence consistently hurts model performance." Tables and bullets win over narrative for reference content; reserve narrative flow for genuine argument.
- **Mix five instruction styles deliberately** (Mohsenimofidi §4.2): descriptive, prescriptive, prohibitive, conditional, explanatory. Monocultural prose under-cues — the model uses style as a meta-signal about the *kind* of rule it's processing.

Across 253 surveyed CLAUDE.md files, empirical median: H1=1, H2=5, H3=9; H4 in < 15%. Depth > 3 signals over-nesting.

---

## R-20 — Header hierarchy stays flat (2–3 levels typical, 4 rare)

**Statement.** Use H1 for major domains, H2 for components, H3 for details. H4+ is a yellow flag — usually means a component should be split into its own H2.

**Why.** Deep nesting fragments the reader's mental model. Empirical median across 253 CLAUDE.md files: H4 appears in fewer than 15% of files; when it does, it's usually accidental drift.

**How to apply.** Count headings by level. If H4+ appears, examine the parent H3: would it work as a top-level component (H2) with its H4s promoted to H3?

**Patch shape.**

```json
{
  "rule_id": "R-20",
  "location": {"section": "<H4 heading>", "line_hint": <int>},
  "current": "#### <heading>",
  "proposed": "Promote parent H3 to H2; promote this H4 to H3.",
  "justification": "H4+ appears in <15% of surveyed files; structural drift signal.",
  "severity": "low"
}
```

---

## R-21 — Lists for instructions; tables for lookup data; prose for argument

**Statement.** Match form to function:

| Content | Form |
|--|--|
| Ordered procedures, multi-step instructions | Numbered list |
| Independent rules, options, anti-patterns | Bullet list |
| Comparisons across a fixed set of dimensions | Table |
| Single proposition with reasoning | One sentence + one explanation |
| Multi-clause reasoning that needs sequencing | Prose paragraph (≤ 3 sentences) |

**Why.** Hong 2025 found prose containers degrade retrieval; bullets and tables compress equivalent semantic content into denser, more retrievable form. The reverse is not true: forcing a single complex argument into a bullet list creates orphan claims with no connective tissue.

**How to apply.** Scan paragraphs:

- Paragraph contains numbered or pseudo-numbered items ("First, …; second, …") → propose conversion to ordered list.
- Two consecutive paragraphs compare the same fixed dimensions ("A is …; B is …") → propose table.
- Single bullet stretching over 4+ lines → check whether it's actually a multi-clause argument that should be a paragraph.

**Patch shape.**

```json
{
  "rule_id": "R-21",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<prose paragraph or oversized bullet>",
  "proposed": "<converted to list / table / split into sentences>",
  "justification": "Form mismatch: <content type> renders <better form>.",
  "severity": "low"
}
```

---

## R-22 — Mix five instruction styles per Mohsenimofidi §4.2

**Statement.** Across a SKILL.md body, ensure presence of all five instruction styles:

| Style | Example |
|--|--|
| Descriptive | "Uses dependency injection pattern" |
| Prescriptive | "Follow the validator-per-rule convention" |
| Prohibitive | "Never commit without tests" |
| Conditional | "If the file is hot-tier, apply R-13" |
| Explanatory | "Avoid X because Y rots on edit" |

A skill that uses only prescriptive sentences cues the model to read everything as an order; mixing styles helps the model classify each rule's strictness and applicability.

**How to apply.** Sample 10–15 rule sentences from the body. Categorize by style. If any of the five styles is missing or under 5% of the sample → flag and propose adding 1–2 sentences in the missing style. Conditional rules deserve special attention — Yang §3.2 shows the model recovers conditional rules only 22.9% of the time when not made explicit, so missing conditional phrasing is the highest-priority style gap.

**Patch shape.**

```json
{
  "rule_id": "R-22",
  "location": {"section": "<whole file>"},
  "current": "Style distribution: <descriptive=N, prescriptive=N, ...>",
  "proposed": "Add 1–2 <missing-style> rules; example phrasings: <samples>.",
  "justification": "Monocultural instruction style; <missing> style absent.",
  "severity": "low"
}
```

---

## R-23 — Topology rendered as text, not Mermaid or ASCII art

**Statement.** Describe data flow, hierarchies, and process diagrams using compact text notation: `A → B → C[]`, `Hierarchy: parent → child → grandchild`, `Flow: ingest → parse → emit`. Mermaid appears in only 2 of 328 surveyed CLAUDE.md files — it is not the convention, and the model derives less from rendered diagrams than from arrow-notation prose.

**How to apply.** Search for Mermaid fences (` ```mermaid `) and large ASCII boxes. For each, propose the equivalent text-arrow notation.

**Patch shape.**

```json
{
  "rule_id": "R-23",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<Mermaid or ASCII diagram>",
  "proposed": "<arrow-notation text equivalent>",
  "justification": "Text topology dominates empirically (326/328 surveyed files); diagram cost outweighs benefit.",
  "severity": "low"
}
```

---

## R-24 — Load-bearing rules placed early; positional decay past 30% of file

**Statement.** See R-14 in G2 — same rule, audited from the structure angle. If G2 has already emitted a patch on a load-bearing rule, G3 should not duplicate. Sub-agents coordinate by rule ID; aggregator dedupes.

---

## R-25 — Section intros and meta-commentary trimmed

**Statement.** Sections start with the rule, not with framing. "In this section we will discuss X" / "The following table summarizes Y" / "Note that Z is important" are pure overhead.

**How to apply.** First sentence of each section: does it state a rule, fact, or instruction? If it announces what is to come or comments on the structure → flag.

**Bad → Good.**

```
bad:  "## Token Economy
       The following bullet points describe the rules around token usage in skills.
       It's important to note that …
       - Tables for lookup data."

good: "## Token Economy
       - Tables for lookup data.
       - …"
```

**Patch shape.**

```json
{
  "rule_id": "R-25",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<intro sentence>",
  "proposed": "<delete; first rule moves to first position>",
  "justification": "Section intros are pure overhead; state facts directly.",
  "severity": "low"
}
```

---

## R-26 — Horizontal rules only for major breaks

**Statement.** `---` separates top-level sections, not every paragraph. Decorative rules consume vertical attention without adding hierarchy beyond what headings already provide.

**How to apply.** Count `---` lines. If they outnumber H2 headings, prune the ones between H3-level subsections.

**Patch shape.**

```json
{
  "rule_id": "R-26",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "---",
  "proposed": "<delete; rely on H2 heading for separation>",
  "justification": "Decorative horizontal rule.",
  "severity": "low"
}
```

---

## R-27 — Bold/italic sparingly, only critical terms or warnings

**Statement.** Bold every fifth phrase and bold loses meaning. Empirical convention: critical warnings (safety, data integrity) and first introduction of a term — nothing else.

**How to apply.** Count `**` occurrences per 100 lines. If > 10 per 100 lines, the file is over-emphasizing. Sample emphasized phrases: are they (a) safety warnings, (b) first-introduction of a defined term? If neither → propose unbolding.

**Patch shape.**

```json
{
  "rule_id": "R-27",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<bolded phrase>",
  "proposed": "<unbolded equivalent>",
  "justification": "Emphasis density >10/100 lines; bold devalued.",
  "severity": "low"
}
```

---

## R-28 — Bad/good contrast pairs used for normative rules

**Statement.** Normative rules (do this, not that) gain meaningfully from bad/good example pairs. The skill itself recommends this pattern in its current "Use bad/good contrast pairs" bullet.

**How to apply.** For each MUST / SHOULD rule, check whether at least one bad/good pair is adjacent. Long rules without examples are candidates for example-addition; rules with examples don't need patches.

**Patch shape.**

```json
{
  "rule_id": "R-28",
  "location": {"section": "<heading>", "line_hint": <int>},
  "current": "<rule sentence with no examples>",
  "proposed": "Add example pair:\\nbad: <…>\\ngood: <…>",
  "justification": "Normative rule lacks contrast example; reader latency on edge cases.",
  "severity": "low"
}
```

---

## Output protocol for this sub-agent

1. Build a heading-level histogram (`H1=N, H2=N, ...`) — record in the first patch's `meta`.
2. Count instruction-style distribution across the body.
3. Walk file in order, emitting patches per rule.
4. Defer to G2 on R-14 (load-bearing position) when the same rule is already patched there.
