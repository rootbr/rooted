---
title: Commented-out code is deleted; version control holds it
rule_id: D-04
applies_to_target: [code]
check_kind: mechanical
severity_default: medium
---

# Commented-out code is deleted; version control holds it

## Thesis
A block of code that has been commented out is deleted from the source file. Version control holds every prior version completely, so the block recovers nothing that is not already recoverable and leaves the reader deciding whether it still matters.

## Rationale
A commented-out block is indistinguishable on sight from a block temporarily disabled and due to come back, and nothing in the file answers which it is. So every reader re-reads it, re-reasons about it, and carries it through edits it never participates in. Version control holds the same bytes with the date, the author and the removing commit attached, none of which the comment carries. The block also decays where it sits: it is not compiled, not tested and not refactored with the code around it, so by the time anyone wants it back it no longer applies to the code it was cut from.

## Example
```
bad:  drawComposited(node)
      // Old render path, kept just in case: drawLegacy(node); fixupArtifacts(node)
good: drawComposited(node)
```

## Limits
Applies to commented-out executable statements. Illustrative code inside a doc-comment or a usage example is prose about the interface and stays. A single commented line documenting a deliberate omission — a parameter left unset with the reason beside it — carries a reason and is not a disabled block. Detection needs the target file's language to be known, since the comment syntax is what delimits the block; a file whose language the pre-pass cannot identify is out of scope.

## Validator
On a `code` target read only the comment spans the static pre-pass extracts for that file's language — the surrounding source is not Markdown and is not scanned for this check. Flag a run of two or more consecutive comment lines whose text carries statement syntax for that language: a trailing `;`, a brace `{` or `}`, an assignment `=`, or a call of the form `identifier(`. Then ask one binary question: **would these comment lines compile as written if their comment markers were removed?** Yes → the run is disabled code, not a comment.

## Patch output
When a run of comment lines is disabled code, emit one patch (`rule_id: D-04`, `location.section` + `line_hint`, `current` = the exact commented-out block including any "kept just in case" preamble line, `proposed: ""`, severity medium) deleting it. The block's status is decidable from its syntax, so no `needs_human` flag in the clear case; set it only where a comment line is ambiguous between disabled code and an inline example.

## Source
Verified hands-on experience — eval seed 5, `plugins/evidence-based-authoring/skills/auditing-ai-context/evals/seeds/seed5_dead_code.swift`: a commented-out render path kept "just in case" beside the live one, whose cleanup deletes the block and preserves the current call.
