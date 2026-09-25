---
title: Every rule the config expects code to obey is a numbered invariant, never a sentence in prose
rule_id: META-08
domain: meta
triggers: ['\bmust\b', '\bnever\b', '\bshould\b', '(?i)we (also )?want|please|avoid\b|keep\b', '^\s*[-*]\s']
scope: file
check_kind: mechanical
severity_default: minor
---

# Every rule the config expects code to obey is a numbered invariant, never a sentence in prose

## Thesis
A rule a diff could violate lives in the invariant list as `N. **Title**: rule. Violation: …` under a number of its own. A `we also want to avoid …` in a paragraph, a bullet under a heading, a `please keep … thin` in a note has no id a finding can cite, no handle a later invariant can refine or supersede, and no place in the map a reviewer walks.

## Rationale
A finding is a claim that a change violates a named rule; without a number the name is a paraphrase, and two reviewers paraphrase differently. Decision records are kept as numbered files, `nnnn-title.md`, and the identifier of each requirement should be unique, so a reference by number resolves to one rule and nothing else. Prose rules also escape every other check: they carry no `Violation:` clause, no scale, no evidence handle, and a tool that indexes numbered invariants never sees them, so the rule is enforced by whoever happens to remember it.

## Example
```java
bad:  Also, please try to keep the controller layer thin. We also want to avoid
      Spring annotations in the domain.
good: 11. **Domain is framework-free**: No class in `..domain..` imports from
          `org.springframework`. Violation: an `org.springframework` import under
          `..domain..`. Enforced by ArchUnit rule `DomainFreeOfSpringAnnotations`.
```

## Limits
Applies to text that states what code must or must not do. A tolerances section (`lost increments are accepted on Stats#sample`), a rationale paragraph, a definitions list and a description of the project are not rules and are not flagged. A bullet inside a numbered invariant's own continuation lines belongs to that invariant.

## Validator
Open the config at HEAD. In the diff's added lines, find every sentence outside a numbered invariant that states an obligation on code — `must`, `never`, `should`, `avoid`, `keep`, `we want` — and is not under a tolerances, definitions or rationale heading. Validator question: **does the diff add a rule on code that has no invariant number?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: META-08`, severity minor, `file` = the config path, `symbol` = the nearest heading above the sentence, `code` = the prose sentence quoted verbatim from the diff, `fix` = the sentence rewritten as the next numbered invariant with a `Violation:` clause, `rationale` naming that a finding cites an invariant by number).

## Source
MADR `README.md` (`adr/madr`, `main`) — "For each ADR, copy the template to `nnnn-title.md`": every record is a numbered file. arXiv:2103.02255 §4.1 — the requirement tuple's first element, "id: The identifier of the requirement … The id of each requirement should be unique".
