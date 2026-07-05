---
title: Source citations must use stable structural anchors, not page numbers, line numbers, or character offsets
rule_id: R-41
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: high
---

# Source citations must use stable structural anchors, not page numbers, line numbers, or character offsets

## Thesis
Every external citation (book, paper, RFC, video, spec) must identify content by a structural anchor that is stable across editions, reflows, and renumbering. File-internal references must identify by symbol (method, class, function), not by line. A page or line may augment a stable anchor for convenience but never replace it.

## Rationale
Pages drift the moment a source is reformatted: a German hardback, an English Kindle, an OCR PDF, and audiobook chapters all disagree about where page 110 falls. Line numbers in code rot on every edit above the cited line; `path:142` is wrong before the next commit. Under flat fact-extraction, precise temporal markers, implicit coreferences, and ephemeral one-off details are irretrievably lost — the same loss occurs when an anchor depends on rendering geometry rather than authored structure.

## Example
```
bad:  See "Atomic Habits" p.142 for the cue-craving loop
good: See "Atomic Habits" Ch.3 §"How a Habit Works" (p.142 in 2018 hardback)

bad:  Retry logic: src/main/java/com/acme/orders/RetryPolicy.java:142
good: Retry logic: see RetryPolicy#shouldRetry
```

## Limits
The stable anchor differs by source type: book uses chapter title plus section heading or a practice/exercise/figure number; paper uses section number plus subsection name; RFC uses section number plus section name; video uses chapter title plus speaker; a repo file uses `Class#method` or `<file>::<function>`. A page or line as a parenthetical supplement is acceptable and needs no patch.

## Validator
Scan for `p.<digits>`, `page <digits>`, `:<digits>` after a path, `pp.<digits>-<digits>`, and a bare `<digits>` following a citation. If the citation is already anchored to a chapter, section, or symbol, keep the page or line as supplement and emit no patch. If the page or line is the only locator, propose a replacement that names the structural anchor. Validator question: can a reader find the same content in a different edition, commit, or rendering using the locator alone? If no, flag.

## Patch output
When auditing a citation whose only locator is a page, line, or offset, emit one patch (`rule_id: R-41`, location of the citation, severity high) proposing the structural anchor, keeping the page or line as a parenthetical when useful.

## Source
Pollertlam 2603.04814 §5.1 (flat extraction loses precise markers, implicit coreferences, one-off details).
