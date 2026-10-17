---
title: Provenance stays out of runtime context — cite the finding, not the bookkeeping
rule_id: R-57
applies_to_target: [context-file, skill, agent-prompt, kb-card, doc, code]
check_kind: mechanical
severity_default: low
---

# Provenance stays out of runtime context — cite the finding, not the bookkeeping

## Thesis
Provenance stays out of runtime text, which cites the finding — what was observed, where, with its numbers. The record behind it lives in the repo layer: maintainer bookkeeping — calendar dates of verification or audit runs, audit-run identifiers, tmp-log paths, changelog-style remarks ("all applied <date>") — in the research log and git history; a KB card's source citations on the card's line in the corpus's provenance map, keyed by the card's id; the card itself carries none.

## Rationale
The runtime consumer acts on the finding, never on the date — a verification date changes no decision, and context should be the smallest possible set of high-signal tokens. A consumer that reads a KB card whole pays for every citation and quote in a source block while it acts on the rule: in three measured KB-card corpora the source block held 18 % to 40 % of the bytes their consumers read, and no consumer opened a source at runtime. The round-trip holds because the dated record survives in the research log and git history, and the citation with its quoted evidence survives on the card's provenance line, so cutting it from runtime loses nothing recoverable.

## Example
```
bad:  Verified 2026-06-06 on the source re-audit: multiple drifts found.
good: Verified on the source re-audit: multiple drifts found.
      (the dated record lives in research/<date>_<topic>.md)
```

## Limits
A date that is part of a source citation — a paper year, an RFC date, a doc version — is kept; only maintainer bookkeeping is stripped. A number a Rationale needs stays in the Rationale (C-E3), named by what it measures rather than by who measured it. Hits inside fenced example blocks are out of scope. Before cutting a dated note or a citation, the record must be confirmed to exist in the research log, the provenance map or git history.

## Validator
Grep for ISO dates (`\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b`), `tmp/` log paths, and run identifiers outside fenced example blocks. Classify each hit: part of a source citation (paper year, RFC date, doc version) → keep; maintainer bookkeeping → strip. On a `kb-card` target flag a `## Source` block or a block of another name that lists citations, an inline locator (an arXiv id, a DOI, a URL), an author-year attribution and a fetch marker — `(fetched)`, `(relayed)`, `(unfetched)` and their bold forms. Each flagged citation, attribution or marker moves to the card's provenance line. Validator question: does any decision change if this date / run-ID / log path / citation block is removed? If no, it is provenance — move it to the repo layer.

## Patch output
When a date, run-ID, or log path is embedded as bookkeeping in runtime context, emit one patch (`rule_id: R-57`, `location.section` = heading, severity low) keeping the finding and removing the bookkeeping, after confirming the dated record exists in the research log or git history. When a KB card carries a citation block, an inline locator, an attribution or a fetch marker, emit one patch per block or sentence (`location.section` = its heading, severity low) that removes it, after confirming the card's provenance line holds every citation, quote and status. The keep-vs-strip classification is mechanical.
