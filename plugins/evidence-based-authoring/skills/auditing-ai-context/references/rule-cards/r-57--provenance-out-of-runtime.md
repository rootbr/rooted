---
title: Provenance stays out of runtime context — cite the finding, not the bookkeeping
rule_id: R-57
applies_to_target: [context-file, skill, agent-prompt, doc, code]
check_kind: mechanical
severity_default: low
---

# Provenance stays out of runtime context — cite the finding, not the bookkeeping

## Thesis
Hands-on evidence is cited by naming the verified finding — what was observed, where, with its numbers. Maintainer bookkeeping — calendar dates of verification or audit runs, audit-run identifiers, tmp-log paths, changelog-style remarks ("all applied <date>") — must not appear in bodies or references; it lives in the repo's research log and git history.

## Rationale
The runtime consumer acts on the finding, never on the date — a verification date changes no decision, and context should be the smallest possible set of high-signal tokens. The round-trip holds because the dated record survives in the research log and git history, so cutting it from runtime loses nothing recoverable.

## Example
```
bad:  Verified 2026-06-06 on the source re-audit: multiple drifts found.
good: Verified on the source re-audit: multiple drifts found.
      (the dated record lives in research/<date>_<topic>.md)
```

## Limits
A date that is part of a source citation — a paper year, an RFC date, a doc version — is kept; only maintainer bookkeeping is stripped. Hits inside fenced example blocks are out of scope. Before cutting a dated note, the dated record must be confirmed to exist in the research log or git history.

## Validator
Grep for ISO dates (`\b20[0-9]{2}-[0-9]{2}-[0-9]{2}\b`), `tmp/` log paths, and run identifiers outside fenced example blocks. Classify each hit: part of a source citation (paper year, RFC date, doc version) → keep; maintainer bookkeeping → strip. Validator question: does any decision change if this date / run-ID / log path is removed? If no, it is provenance — move it to the repo layer.

## Patch output
When a date, run-ID, or log path is embedded as bookkeeping in runtime context, emit one patch (`rule_id: R-57`, `location.section` = heading, severity low) keeping the finding and removing the bookkeeping, after confirming the dated record exists in the research log or git history. The keep-vs-strip classification is mechanical.

## Source
Anthropic, Effective context engineering (context is "the smallest possible set of high-signal tokens").
