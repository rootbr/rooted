# KB Card Specification

A specification for atomic knowledge cards consumed by AI agents. The subject domain of the knowledge is arbitrary — software engineering, law, medicine, finance, craft: the specification constrains the form of a card, not its subject.

Contents: Governing principle · Terms · Card template · Frontmatter reference · Authoring rules (A identity/retrievability C-A1..A5 · B atomicity C-B1..B3 · C self-containedness C-C1..C3 · D consumer applicability C-D1..D3 · E faithfulness C-E1..E3 · F structural consistency C-F1..F3) · Principles · Corpus-level properties · Enforcement · Customization points · Sources.

---

## Governing principle

A card is optimized for the *runtime consumer* (an AI agent, skill, or tool), not for the source material. The consumer never reads the whole knowledge base — it retrieves one card and reads it in isolation, through one of four retrieval paths:

1. **Facet filter** — the loader returns cards matching facet values ("all cards for phase X that apply to Y").
2. **Term grep** — full-text search over `tags`, `defines`, `uses`, and titles.
3. **Index scan** — the agent reads a listing of titles and decides from the title alone whether to open a card.
4. **Link traversal** — from a retrieved card to a linked sibling, when one card is not enough.

Everything below follows from these paths: the card must be self-contained (paths 1–3 return it alone), facet-correct (path 1 is blind to a mis-faceted card), term-correct (path 2 is blind to source-only vocabulary), titled with its full claim (path 3 sees nothing else), and free of anything the consumer does not use.

---

## Terms

| Term | Definition |
|---|---|
| card | One file holding one idea: YAML frontmatter (the retrieval index) plus a fixed sequence of body blocks. |
| slug | The card's filename without extension: lower-case ASCII kebab-case derived from the title's central claim. The stable key used in `links:` and in the provenance map; renaming a slug requires relinking every reference to it. |
| facet | A frontmatter field holding values from a controlled vocabulary, used to filter cards (`operates_on`, `applies_to`, …). |
| plane-1 facet | The store's primary filter facet. Its *name* is chosen per store (`phase`, `domain`, `jurisdiction`, …) because each consumer filters on its own dimension — see Customization points. |
| taxonomy | The store-local file listing the allowed values for every facet. |
| store / corpus | One knowledge base governed by one taxonomy. |
| loader | The tool that returns cards matching facet values. |
| linker | The tool that maintains `links:` integrity — bidirectional, zero broken references. |
| validator | The tool that mechanically checks the rules marked *mechanical* in Enforcement. |
| provenance map | An external file outside the corpus, keyed by slug, holding service metadata the consumer never reads — at minimum each card's source and creation date. Round-trip rule: card + map together reconstruct everything known about the card. |

---

## Card template

```markdown
---
title: <one complete declarative thesis — a proposition, not a question or a topic>
tags: [<3–6 retrieval tags>]
links: [<sibling-slug>, <sibling-slug>, …]        # bidirectional; the linker maintains integrity
confidence: high | medium | low
<plane-1>: [<value>, …]                           # the store's primary filter facet — see Terms
operates_on: [<value>, …]
applies_to: [<value>, …]                          # default [universal]
knowledge_type: [<value>, …]                      # or the store's fourth facet
defines: [<term>, …]                              # terms this card is the authority on (may be [])
uses: [<term>, …]                                 # terms it relies on (for grep)
---

# <same as title>

## Thesis
<the single idea, stated in full, in the consumer's task vocabulary>

## Rationale
<why it holds — the heuristic + its reasoning, not brittle steps and not a slogan>

## Example
​```
rejected: <…>            # or:  input: … / action: … / output: …
accepted: <…>
​```

## Counter-example / limits
<when it does not apply — the card's own applicability bound>

## Terminology            (required when `defines` is non-empty, unless the body already defines the terms)
| term | definition |
|---|---|
| <term> | <self-contained definition> |

## Skill application
<1–3 sentences naming the sub-task (when), the downstream consumer (who), and the
output / artifact field (where) — rule C-D2. e.g. "When assessing the risks of a contract
clause, the reviewing agent populates the `risks[]` section of the assessment report.">
```

Frontmatter carries only the fields above (rule C-A5); service metadata lives in the provenance map.

---

## Frontmatter reference

| Field | What it is | How it is used and filled |
|---|---|---|
| `title` | A single complete declarative thesis — a proposition, never a question or a bare topic. | The agent sees only the title in an index scan and decides from this line alone whether to open the card. A vague title means a relevant card is skipped or an irrelevant one is opened. |
| `tags` | 3–6 flat lower-case keywords; free vocabulary. | Fallback grep index when the agent does not know the exact facet value. Do not repeat facet values — facets are already filterable; tags cover retrieval angles the taxonomy misses. |
| `links` | Sibling slugs, maintained bidirectionally by the linker. | Enrich context when one card is not enough; the agent is never required to follow them. Link a sibling when it changes or bounds how this card is applied; typically 2–6 links. |
| `confidence` | `high` / `medium` / `low`. | The consumer weights the card in conflicts (`high` outranks `medium`) and may exclude `low` for critical decisions. The author assigns: `high` — multiple canonical sources agree or the claim is empirically verified; `medium` — one credible source, no known dissent; `low` — contested or speculative, verify against the source before relying on it. |
| `<plane-1>` | The store's primary filter facet. | The main extraction index: "give me cards for facet value X". Values strictly from the taxonomy; a wrong value makes the card invisible. |
| `operates_on` | The entity the idea acts upon. | Second-level filter: the agent works on an entity of kind X and requests only cards whose `operates_on` matches. |
| `applies_to` | Scope of applicability; default `[universal]`. | Self-restriction: tells the agent whether the rule is universal or valid only in a named context. Prevents misapplication. |
| `knowledge_type` | The kind of knowledge (principle, pattern, anti-pattern, conflict, …). | Lets the agent request "only patterns" or "only anti-patterns" — separates *what to do* from *what to avoid*. |
| `defines` | Terms this card is the **authority** on within the corpus. | When the agent meets an unfamiliar term, it greps `defines`; the card listing the term is the canonical definition. Exactly one authority per term corpus-wide — on collision, merge the cards or demote one to `uses`. Every `defines` term must actually be defined in the card (in `## Terminology` or the Thesis). |
| `uses` | Terms the card relies on but does not define. | Reverse navigation: "which cards depend on this term?" |

---

## Authoring rules

The letter in a rule ID names its group. Groups A–C make the card *findable and readable in isolation*; D–E make it *applicable and true*; F makes the corpus *uniform*.

### A. Identity and retrievability — the frontmatter is the index

A card the loader or grep cannot find does not exist.

| Rule | Instruction | Why |
|---|---|---|
| **C-A1** | `title` is one complete declarative thesis; never a question or a bare topic. | The index scan shows only the title; the agent decides from it whether to read the body (proposition-level retrieval — Dense X Retrieval). |
| **C-A2** | The `slug` matches the title's thesis; if you rewrite the thesis, realign the title or the slug. | The slug is the stable key in every `links:`; drift breaks navigation. |
| **C-A3** | Fill every facet from the store's taxonomy; where cards are foldered by plane-1, the folder must equal a plane-1 value. | Facets are the retrieval index — a wrong facet makes the card invisible to the consumer. |
| **C-A4** | `defines`/`uses` carry the exact terms an agent will grep, in the **consumer's** vocabulary, not only the source's — and `uses`/`tags` carry, beside the canonical terms, the **symptom vocabulary**: 2–5 terms a practitioner greps *before knowing the canonical term* (`<symptom phrase>`, `<lay paraphrase>` beside `<canonical term>` — e.g. `high blood pressure` beside `hypertension`). Symptom terms must be the common words of the symptom, defensible without sight of any evaluation set — never echoes of specific queries, which is overfitting to a benchmark, not retrievability. | Grep is blind to source-only vocabulary; such a card is unreachable. The consumer needs a card most exactly when it does not yet know the card's term: in an internal, unpublished retrieval eval over symptom-phrased queries every miss was this gap — the card indexed in the author's terms, the query phrased in the situation's words — and adding symptom terms to 24 cards lifted recall@5 from 0.63 to 0.80. |
| **C-A5** | Frontmatter contains consumer fields only; provenance and dates go to the provenance map. | Smallest set of high-signal tokens; service fields confuse retrieval and application. |

Title contrast (C-A1):

```
rejected: Meeting hygiene                      # bare topic — no claim to act on
rejected: Should long meetings be split?       # question — undecidable from the index
accepted: Split any meeting longer than 90 minutes into two sessions with separate agendas
```

### B. Atomicity — one idea, but the whole idea

| Rule | Instruction | Why |
|---|---|---|
| **C-B1** | One thesis per card; if a second idea accretes, split into a linked pair. | Atomicity enables reuse and linking: a note holds "one idea and one idea only" (Zettelkasten); capture "the entirety of that thing" in one place (evergreen-notes principle). |
| **C-B2** | Atomic does not mean short — keep the precondition, trade-off, and counter-example that make the thesis true. | Over-compression collapses accuracy: bulk-rewriting an accumulated agent context into a short summary dropped task accuracy 66.7 → 57.1, below the 63.7 no-context baseline (ACE); "minimal does not necessarily mean short" (Anthropic). |
| **C-B3** | The thesis is a single checkable claim. | Foundation for faithfulness checking and downstream verification. |

### C. Self-containedness — the card is read in isolation

| Rule | Instruction | Why |
|---|---|---|
| **C-C1** | No source-deixis: never "this chapter", "the source", "as we saw", "as noted earlier". | The card is read with no source in context. (Bare "the author" as a role inside the consumer's own domain — e.g. the author of a requirement — is fine.) |
| **C-C2** | Links enrich, never complete: the card must make sense without following any link. | Retrieved in isolation. |
| **C-C3** | The card self-situates — `applies_to` plus Counter-example/limits state where it holds. | Situating context cuts top-20 retrieval failure rate by 35% — 49% with added lexical matching, 67% with reranking (Anthropic Contextual Retrieval). |

### D. Consumer applicability — shaped to the job, not the source

| Rule | Instruction | Why |
|---|---|---|
| **C-D1** | Write in the consumer's task vocabulary, shaped to its sub-task — not to the source's structure. | The card serves a job, not a syllabus. |
| **C-D2** | End with exactly one consumer block naming three things: (1) the **sub-task** — the exact situation where the card applies; (2) the **downstream consumer** — which agent, skill, or tool acts on it; (3) the **output / artifact field** — the concrete field or structure the consumer populates. | Without this bridge the card is a passive fact; with it the consumer knows *when*, *who*, and *where*. Two or more blocks signal a second idea (C-B1). Count and name are governed by C-F2. |
| **C-D3** | Give a heuristic plus its reason; avoid both rigid step-lists and vague slogans; no unexplained ALL-CAPS. | The "right altitude" between brittle hardcoded logic and vague guidance (Anthropic); explain *why*, not only *what* — the model generalizes from reasons (skill-authoring best practices). |

### E. Faithfulness — the card must not outrun its source

| Rule | Instruction | Why |
|---|---|---|
| **C-E1** | The thesis must follow from the source: no inversion, no stripped precondition, no refuted position stated as a recommendation, no conditional flattened to an absolute. | The four drifts are instances of intrinsic hallucination — content that misrepresents the source; entailment by the source correlates with faithfulness far better than n-gram overlap (Maynez et al.). |
| **C-E2** | No attribution of a method or idea to an author, publication, or upstream source in the body, title, or Terminology. Name the idea by what it is, not by who wrote it. | A reader without the author in context cannot parse "X's method" — author-bound jargon is dead weight; in-body attribution is also a provenance. Provenance belongs in the map. |
| **C-E3** | Keep the number on any quantified claim. | A de-quantified claim is an unfalsifiable gesture. |

### F. Structural consistency — one schema across the corpus

| Rule | Instruction | Why |
|---|---|---|
| **C-F1** | Body blocks present and in order: Thesis → Rationale → Example → Counter-example / limits → [Terminology] → consumer block. | One schema across the corpus yields predictable parse and grep context. |
| **C-F2** | Exactly one consumer block, named with the corpus's consumer-block name (default `## Skill application`); never a second block under another name. | Corpus consistency: one block per card, one name per corpus. |
| **C-F3** | `## Example` is a fenced contrast pair of at most about three lines (`rejected → accepted` or `input → action → output`) in an everyday domain — never a niche specific to the card author or their organization. | Machine-parseable and uniform; an everyday domain parses for any consumer. |

---

## Principles

### A card is a proposition for the consumer, not a summary of the source

Three independent sources converge on the same unit of knowledge for an LLM consumer:

1. **Dense X Retrieval** (Chen et al., EMNLP 2024). The best indexing unit is the *proposition*: "atomic expressions within text, each encapsulating a distinct factoid and presented in a concise, self-contained natural language format". Proposition-level indexing beats passage-level retrieval (up to +9–12 points Recall@5 with retrievers not tuned to the corpus) and improves downstream QA under a fixed token budget — and an agent assembling its working context operates exactly in that fixed-budget, untuned regime. An ideal card is a proposition.
2. **Zettelkasten** (Ahrens, *How to Take Smart Notes*; zettelkasten.de). A permanent note holds "one idea and one idea only", written in full sentences, in your own words, as if for someone else. A note that needs "as mentioned above" to be understood is an essay fragment, not a note. Atomic does not mean small: notes should be "only about one thing — but which, as much as possible, capture the entirety of that thing" (Matuschak).
3. **Anthropic** (*Effective context engineering for AI agents*). Context engineering means finding "the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome", written at the right altitude — the Goldilocks zone between brittle hardcoded logic and vague guidance — and "minimal does not necessarily mean short".

Consequences for any KB pipeline:

- Frontmatter facets are the extraction index; facet correctness is retrieval-critical, not cosmetic (C-A3).
- Each card is read in isolation; self-sufficiency and zero deixis are mandatory, not stylistic (group C).

---

## Corpus-level properties

These hold across the whole corpus and are maintained by tooling, not by individual card authors:

- **Link integrity** — bidirectional links are consistent; the linker reports zero broken or asymmetric references.
- **Explicit conflict cards** — when canonical sources disagree, the conflict is a dedicated card, faceted like any other so it is retrieved alongside the disagreeing pair: its Thesis states both positions and the tiebreaker (which wins, under what condition), and it links to both sides.
- **Controlled vocabulary** — the taxonomy of terms and facets is stable across distillation sessions so that cross-source retrieval does not break.
- **Utilization** — dead-weight and over-generic hub cards are identified by retrieval evaluation, not by inspection.

---

## Enforcement

Two checks with different mechanisms:

**Mechanical** — a validator checks before a card is accepted and must report zero error-severity findings: facets against the taxonomy (C-A3), slug–title alignment (C-A2), frontmatter whitelist (C-A5), title form (C-A1), source-deixis scan (C-C1), attribution scan against the store's source-name list (C-E2), number present on quantified claims (C-E3), block set and order (C-F1), single consumer block (C-F2), Example form (C-F3).

**Semantic** — not mechanically checkable; verified by review (a fresh agent or a human) against the source: thesis entailment (C-E1), one-idea atomicity and claim checkability (C-B1, C-B3), completeness of the thesis (C-B2), consumer-vocabulary fit (C-D1, C-A4), consumer-block usefulness (C-D2), right altitude (C-D3), link-independence of the body (C-C2), self-situating scope (C-C3).

In addition, the linker check must report zero broken and zero asymmetric links.

---

## Customization points

The following are intentionally local to each store and are not unified:

- **Plane-1 facet name** (`phase`, `domain`, `jurisdiction`, …) — each consumer filters on its own dimension.
- **Fourth facet** (`knowledge_type` or a domain-specific classification).
- **Taxonomy vocabulary** — the allowed values for every facet live in a taxonomy file local to the store.
- **Consumer block name** — default `## Skill application`; a store may choose another name, but exactly one name per corpus, and C-F2/C-D2 then apply to the chosen name.

Everything else in this specification is uniform across all stores.

---

## Sources

- Anthropic. *Contextual Retrieval* (2024). anthropic.com/news/contextual-retrieval
- Anthropic. *Effective context engineering for AI agents* (2025). anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic. *Skill authoring best practices*. platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Chen, T., et al. "Dense X Retrieval: What Retrieval Granularity Should We Use?" *EMNLP 2024*. arXiv:2312.06648
- Maynez, J., et al. "On Faithfulness and Factuality in Abstractive Summarization." *ACL 2020*. arXiv:2005.00661
- Zhang, Q., et al. "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models" (ACE). arXiv:2510.04618
- Ahrens, S. *How to Take Smart Notes*. 2017
- zettelkasten.de. "Atomicity." zettelkasten.de/atomicity/guide/
- Matuschak, A. "Evergreen notes should be atomic." notes.andymatuschak.org/Evergreen_notes_should_be_atomic
