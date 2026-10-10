---
title: Provenance stays out of runtime context — cite the finding, not the bookkeeping
rule_id: R-57
applies_to_target: [context-file, skill, agent-prompt, kb-card, doc, code]
check_kind: mechanical
severity_default: low
---

# Provenance stays out of runtime context — cite the finding, not the bookkeeping

## Thesis
Provenance stays out of runtime text, which cites the finding — what was observed, where, with its numbers. The record behind it lives in the repo layer: maintainer bookkeeping — calendar dates of verification or audit runs, audit-run identifiers, tmp-log paths, changelog-style remarks ("all applied <date>") — in the research log and git history; a KB card's source citations on the card's line in the corpus's provenance map, keyed by the card's id. A corpus that keeps a one-line footer documents it in its taxonomy.

## Rationale
The runtime consumer acts on the finding, never on the date — a verification date changes no decision, and context should be the smallest possible set of high-signal tokens. A consumer that reads a KB card whole pays for every citation and quote in a source block while it acts on the rule: in three measured KB-card corpora the source block held 18 % to 40 % of the bytes their consumers read, and no consumer opened a source at runtime. The round-trip holds because the dated record survives in the research log and git history, and the citation with its quoted evidence survives on the card's provenance line, so cutting it from runtime loses nothing recoverable.

## Example
```
bad:  Verified 2026-06-06 on the source re-audit: multiple drifts found.
good: Verified on the source re-audit: multiple drifts found.
      (the dated record lives in research/<date>_<topic>.md)
```

## Limits
A date that is part of a source citation — a paper year, an RFC date, a doc version — is kept; only maintainer bookkeeping is stripped. A one-line footer that a corpus's taxonomy documents stays, without quoted evidence or a fetch status; the audit corpus's own one-line footer is documented in `rule-cards-taxonomy.md`. A number a Rationale needs stays in the Rationale (C-E3). Hits inside fenced example blocks are out of scope. Before cutting a dated note or a citation, the record must be confirmed to exist in the research log, the provenance map or git history.

## Validator
Grep for ISO dates (`\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b`), `tmp/` log paths, and run identifiers outside fenced example blocks. Classify each hit: part of a source citation (paper year, RFC date, doc version) → keep; maintainer bookkeeping → strip. On a `kb-card` target, open the corpus's taxonomy and flag a `## Source` block, or a block of another name that lists citations, when the taxonomy documents no footer; in a footer the taxonomy documents, flag a statement quoted from the source and a fetch marker — `(fetched)`, `(relayed)`, `(unfetched)` and their bold forms; a quoted title or term belongs to the locator and stays. Each flagged citation, quote or marker moves to the card's provenance line. Validator question: does any decision change if this date / run-ID / log path / citation block is removed? If no, it is provenance — move it to the repo layer.

## Patch output
When a date, run-ID, or log path is embedded as bookkeeping in runtime context, emit one patch (`rule_id: R-57`, `location.section` = heading, severity low) keeping the finding and removing the bookkeeping, after confirming the dated record exists in the research log or git history. When a KB card carries a citation block its taxonomy does not document, or a documented footer carries quoted evidence or a fetch marker, emit one patch for that block (`location.section` = the block's heading, severity low) that removes the block — or, from a documented footer, the quotes and markers — after confirming the card's provenance line holds every citation, quote and status. The keep-vs-strip classification is mechanical.

## Source
Anthropic, Effective context engineering; verified hands-on — the source-block measurement of three KB-card corpora, its dated record named on the provenance line.
