---
title: Tokens on neighbouring lines are not padded into columns by hand, and column alignment appears only where a formatter the code runs through produces and maintains it
rule_id: CODE-57
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['\S {2,}([-+*/%&|^]?=|:=|=>|:)\s', '\S {2,}(//|#)\s', '\S {2,}\S']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# Tokens on neighbouring lines are not padded into columns by hand, and column alignment appears only where a formatter the code runs through produces and maintains it

## Thesis
Where neither the formatter the project runs on the file nor the language's standard formatter emits the alignment itself, an added or changed line carries the language's ordinary spacing between its tokens and no extra spaces that put a token in a column with a token on a consecutive line: at most one space around an assignment or other operator or a colon and between a declaration's type and its name, and before a trailing comment the minimum spacing the language's style sets. In such code, a change to one line of an aligned group leaves the whitespace of its unchanged neighbours as it was rather than re-padding them to restore the columns. Where the formatter emits column alignment itself, the columns stay exactly as the formatter emits them.

## Rationale
Alignment adds a variable number of spaces so that certain tokens appear directly below certain other tokens on previous lines, so a change that touches only one line can disrupt it. Restoring it then means additional changes on nearby lines simply to realign them, and formatting changes on otherwise unaffected lines corrupt version history, slow down reviewers and exacerbate merge conflicts; without restoring it, future edits may leave the group unaligned. Spaces that vertically align tokens on consecutive lines therefore become a maintenance burden. The same diff cost is the reason one style guide prefers indenting continuation lines by a block over aligning them under a call's opening delimiter: smaller diffs when the call is renamed, and less rightward drift. Alignment can aid readability, and a formatter that emits the columns itself removes the time spent lining them up: the reader keeps the columns and no hand edit maintains them.

## Example
```go
bad:  width  := 10  // px
      height := 200 // px
      return width * height
good: width := 10   // px
      height := 200 // px
      return width * height
```

## Limits
The style sources divide on alignment itself, and the condition that separates them is who maintains it. Against alignment kept by hand: one language's style guide lists more than one space around an assignment or other operator to align it with another among the extraneous whitespace to avoid; another says not to use spaces to vertically align tokens on consecutive lines, since it becomes a maintenance burden, and applies this to colons, comment markers and assignments; a third permits the practice but calls it discouraged, never requires it, does not require keeping an existing alignment, and holds it important not to realign nearby lines when a change touches one. For alignment the formatter emits: a language's standard formatter uses blanks for alignment and emits the source in a standard style of indentation and vertical alignment, so there is no need to spend time lining up the comments on a structure's fields, and where its layout seems wrong the program is rearranged rather than the formatter worked around; the third of the guides against hand alignment concedes that alignment can aid readability. Columns that formatter, or a formatter the project runs on the file, emits are its output and are not flagged. Indenting a continuation line so that it sits under its opening delimiter is outside the rule and is settled by the language's style guide: one guide lists alignment with the opening delimiter among the correct continuation forms, another prefers block indentation because it makes for smaller diffs. A project tolerance that permits hand alignment, as one style guide does while never requiring it, rejects a finding on padding in added or changed lines; re-padding unchanged neighbours after a one-line change is still flagged under that tolerance, since the same guide holds it important not to introduce additional changes on nearby lines simply to realign them. The rule judges only spaces added so that a token appears directly below a token on a neighbouring line; leading indentation, line length and line breaking are outside it.

## Validator
Grep the added lines for two or more spaces before an assignment, compound-assignment or other operator or a colon, after a key's or field's colon, between a declaration's type and its name, or before a trailing comment. For each match, read the consecutive lines in the hunk and check whether the padding puts the token in the same column as a token on a neighbouring line and exceeds the minimum spacing the language's style sets for that position. Decide from the formatter the project runs on the file, as configured in the repository, or else from the language's standard formatter, by its documented behaviour or by running it where the toolchain is available, whether that formatter emits this column for this construct; skip columns it emits, and skip whitespace it rewrites on neighbouring lines to keep them. Skip a continuation line indented under its opening delimiter. Compare the hunk's removed and added lines: a line whose only change is whitespace that restores columns broken by a change to a neighbouring line is a re-padded neighbour. Read the project context for a tolerance that permits hand alignment; under it, skip padding on added or changed lines, but not a re-padded unchanged neighbour. Validator question: **Does an added line carry extra spaces that put a token in a column with a token on a consecutive line, or re-pad an unchanged neighbour to restore such a column, where neither the formatter the project runs on the file nor the language's standard formatter emits that alignment?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-57`, severity suggestion, `file`, `symbol`, `code` = the padded added line and the consecutive line it is aligned with, quoted verbatim from the diff, `fix` = the added line with the padding reduced to the language's ordinary spacing, or the re-padded neighbour restored to its previous whitespace, in the file's language, `rationale` = the token padded into a column, the line it is aligned with, and that neither the project's formatter nor the language's standard formatter emits that alignment, so a later edit to the group either re-pads its neighbours by hand or leaves the group unaligned).

## Source
- PEP 8, Whitespace in Expressions and Statements > Pet Peeves; Indentation; Inline Comments (python/peps, `peps/pep-0008.rst`): "Avoid extraneous whitespace in the following situations: [...] More than one space around an assignment (or other) operator to align it with another"; "# Aligned with opening delimiter." under "# Correct:"; "Inline comments should be separated by at least two spaces from the statement." (fetched)
- Google Python Style Guide §3.6 Whitespace and §3.4 Indentation (google/styleguide, `pyguide.md`): "Don't use spaces to vertically align tokens on consecutive lines, since it becomes a maintenance burden (applies to `:`, `#`, `=`, etc.)"; "Implied line continuation should align wrapped elements vertically [...] or use a hanging 4-space indent." (fetched)
- Google Java Style Guide §4.5.2 and §4.6.3 (google/styleguide, `javaguide.html`): "the discouraged practice of using a variable number of spaces to align certain tokens with previous lines"; "This practice is permitted, but is never required by Google Style. It is not even required to maintain horizontal alignment in places where it was already used."; "private int   x;      // permitted, but future edits / private Color color;  // may leave it unaligned"; "Alignment can aid readability [...] it's important **not** to introduce additional changes on nearby lines simply to realign them. Introducing formatting changes on otherwise unaffected lines corrupts version history, slows down reviewers, and exacerbates merge conflicts." (fetched)
- Rust Style Guide, Block indent and Comments (rust-lang/rust, `src/doc/style-guide/src/README.md`): "Prefer block indent over visual indent [...] This makes for smaller diffs (e.g., if `a_function_call` is renamed in the above example) and less rightward drift."; "Where a comment follows code, put a single space before it." (fetched)
- gofmt command documentation (golang/go, `src/cmd/gofmt/doc.go`): "Gofmt formats Go programs. It uses tabs for indentation and blanks for alignment." (fetched)
- Effective Go, Formatting (golang/website, `_content/doc/effective_go.html`): "reads a Go program and emits the source in a standard style of indentation and vertical alignment [...] if the answer doesn't seem right, rearrange your program (or file a bug about `gofmt`), don't work around it."; "there's no need to spend time lining up the comments on the fields of a structure. Gofmt will do that for you." (fetched)

Caveat: the evidence is style-guide and formatter documentation; the diff and maintenance costs are stated by the guides, not measured, and the comment guidelines that ask for a single space before a trailing comment are marked recommendations a formatter may skip.
