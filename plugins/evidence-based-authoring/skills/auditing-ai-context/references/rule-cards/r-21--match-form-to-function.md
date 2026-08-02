---
title: Lists carry instructions, tables carry lookup data, prose carries argument
rule_id: R-21
applies_to_target: [context-file, skill, agent-prompt, doc, answer]
check_kind: semantic
severity_default: low
---

# Lists carry instructions, tables carry lookup data, prose carries argument

## Thesis
Match form to function: ordered procedures and multi-step instructions as a numbered list; independent rules, options, and anti-patterns as a bullet list; comparisons across a fixed set of dimensions as a table; a single proposition with reasoning as one sentence plus one explanation; multi-clause reasoning that needs sequencing as a prose paragraph of at most three sentences.

## Rationale
Structural coherence hurts retrieval in long inputs, and itemized bullets outperform monolithic prose because they permit localized edits. The reverse does not hold: forcing a single complex argument into a bullet list creates orphan claims with no connective tissue.

## Example
```
bad:  one paragraph: "First validate, second parse, third emit…"
good: 1. Validate  2. Parse  3. Emit
```

## Limits
Covers the form/function fit only, not heading depth or emphasis. A multi-clause argument that genuinely needs sequencing belongs in prose, not a list — over-itemizing is the symmetric error. Deciding whether a block is an argument or a lookup set is a reading judgement.

## Validator
Scan paragraphs. A paragraph with numbered or pseudo-numbered items ("First, …; second, …") → propose conversion to an ordered list. Two consecutive paragraphs comparing the same fixed dimensions ("A is …; B is …") → propose a table. A single bullet stretching over four or more lines → check whether it is actually a multi-clause argument that should be a paragraph.

## Patch output
When a block's form mismatches its content, emit one patch (`rule_id: R-21`, `location.section` + `line_hint`, severity low) proposing the converted form (list, table, or split sentences); set `needs_human: true` when the content type is ambiguous.

## Source
Hong 2025 (structural coherence hurts retrieval in long inputs); ACE 2510.04618 §3.1 (itemized bullets outperform monolithic prose, permitting localized edits).
