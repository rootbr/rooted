---
title: Every rule must cite a traceable source
rule_id: R-50
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# Every rule must cite a traceable source

## Thesis
Every prescription — rule, threshold, anti-pattern, recommended pattern — must trace to a peer-reviewed paper (arxiv ID + section anchor), a technical standard (RFC number + §), a vendor or framework doc (stable URL or doc-version), or a dated hands-on note ("Verified on <project>: <finding>", the dated record kept in the repo's research log). A prescription without an attributable source must be cut or marked provisional.

## Rationale
The repo's "Evidence-Based Rule" is explicit: no traceable source, do not add. Even a good idea without a source cannot be defended against later "delete this rule, it costs tokens" pressure — and under the bundling tax every retained rule must justify its slot.

## Example
```
bad:  "Always use 3-5 examples — too few under-trains, too many confuse." (no source)
good: "Use 2–5 diverse examples; inconsistent label/format across examples
      cuts effectiveness up to 40% (Promptomatix 2507.14241 §B.2.1)."
```

## Limits
Covers source presence for each prescription. Whether the cited locator is structurally stable (anchor vs page/line) is a separate check and not flagged here. A rule may legitimately remain if marked provisional rather than asserted as fact.

## Validator
For each rule sentence, look in the surrounding 5 lines for a source pattern: `(Author <Year>)`, `(<Author> §<N>)`, `RFC <N>`, `<arxiv-id> §<N>`, `Verified on <project>`, or a link to a stable doc. If none is present, flag. Does this prescription rest on a source a reader could open, or only on assertion?

## Patch output
When auditing a rule sentence with no source in its surrounding lines, emit one patch (`rule_id: R-50`, `location.section` = heading, severity medium) proposing either a citation appended or the rule marked provisional / cut; set `needs_human: true` because the sub-agent cannot invent a citation — the patch is a request to supply one or accept removal.

## Source
Repo CLAUDE.md "Evidence-Based Rule" ("No traceable source → do not add"); Yang 2505.13360 §3.4 (bundling tax — each retained requirement must justify its slot).
