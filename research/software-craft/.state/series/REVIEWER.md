# Domain reviewer — prompt

One reviewer per domain, run after every topic of the domain is written (`claude-opus-5-5`, effort max, read-only: Read, Grep, Glob, Bash for read-only git). The orchestrator fills `<DOMAIN>`, `<PREFIX>`, the topic list and the card paths, dispatches one agent, and acts on its JSON: `DEFER_TO` pairs go to `scripts/craft-review-workflow.js` and `references/maintenance.md`; contradictions and facet errors go back to the cards through a fix pass the orchestrator reviews card by card; gaps are checked against `references/pending-evidence.md` and the taxonomy row, and a gap that names an openable source becomes a new research run, never a hand-written card.

---

You review the `<DOMAIN>` domain of the software-craft card corpus: the cards `<PREFIX>-NN--*.md` under `<skill-dir>/references/craft-cards/`, written by separate research runs over the topics `<TOPICS>`. Each card is one language-agnostic checkable rule with its evidence; the schema is `<skill-dir>/references/craft-cards-taxonomy.md` (facets, the controlled vocabulary, the block order) and the domain's row in the topic taxonomy of `research/2026-09-26_software-craft-cards.md` §Topic taxonomy names the concepts the domain owns. The runtime that consumes the cards: a pre-pass matches each card's `triggers` (regular expressions against the added lines of a diff, or `signal:<name>`) and dispatches one finder per card with the matched hunks; an aggregation step then drops a finding when the span's owner card also flagged it (`DEFER_TO`, a map from a deferring rule id to its owner rule ids) and resolves conflicts by domain priority. You read; you write nothing.

Read every card of the domain in full. Then answer five questions, with evidence quoted from the cards:

1. Overlap. Which pairs of cards would flag the same added line for the same defect? For each pair: the two rule ids, the kind of line both flag (quote the Validator question of each), which card owns the concept by the taxonomy row, and the `DEFER_TO` entry you propose (`deferring → owner`). A pair whose Validators ask different questions about one line is not an overlap; say so for the near misses you rejected.
2. Contradiction. Which pairs of cards would call one code shape good in one and bad in the other, outside a Limits clause that names the other card's case? Quote the two sentences. Propose the Limits sentence that resolves it, and name which card should carry it.
3. Gap. Which concepts of the domain's taxonomy row have no card and no entry under the domain's heading in `<skill-dir>/references/pending-evidence.md`? For each, name the concept, and say whether an admissible source you can open from this environment (GitHub-hosted documentation or tool-rule pages; a paper only as a GitHub-hosted copy) states a checkable claim about it, with its path; a concept with no such source is reported as a gap with no source, not invented.
4. Facets. Which cards carry a facet value the card's own text does not support: a `step` the card's Thesis never bears on, an `applies_to` broader or narrower than its Limits, a `scope` the Validator's instructions exceed or never use, a `check_kind: mechanical` whose Validator needs a judgement, a `severity_default` the Rationale's evidence does not support under the scale (Major: a correctness or maintainability defect the evidence ties to failures or measured cost; Minor: a clarity or design cost; Suggestion: style, naming, documentation)? Quote the sentence and name the value you propose.
5. Triggers. Which cards' `triggers` cannot match the bad half of the card's own Example (compile each pattern as Python `re` in your head or with `python3 -c` on a scratch string outside the repository, never on repository files), and which two cards' trigger sets are identical or nested so that every dispatch of one is a dispatch of the other? Name the rule ids and the pattern.

Rules of evidence: a claim about a card quotes the card; a claim about the taxonomy quotes the row; "probably" and "seems" are not findings. Do not propose new rules, do not rewrite cards, do not grade the evidence of a card against its Source (the research skeptic did that), and do not report a schema delta the taxonomy documents as deliberate.

Return JSON only:

{
  "domain": "<DOMAIN>",
  "cards_read": ["<PREFIX>-01", ...],
  "overlaps": [{"deferring": "<PREFIX>-NN", "owner": "<PREFIX>-NN", "line_kind": "...", "validator_a": "...", "validator_b": "...", "taxonomy_owner": "..."}],
  "near_misses": [{"a": "...", "b": "...", "why_not": "..."}],
  "contradictions": [{"a": "...", "b": "...", "sentence_a": "...", "sentence_b": "...", "resolving_limits_sentence": "...", "carried_by": "..."}],
  "gaps": [{"concept": "...", "taxonomy_row_text": "...", "source_path": "... or null", "claim": "... or null"}],
  "facet_errors": [{"rule_id": "...", "facet": "...", "current": "...", "proposed": "...", "evidence": "..."}],
  "trigger_errors": [{"rule_id": "...", "pattern": "...", "problem": "does not match the bad Example | identical to <id> | nested in <id>"}],
  "summary": "three sentences at most"
}
