---
title: Inside an aligned block every glyph has a context-independent width
rule_id: S-09
applies_to_target: [answer, doc]
check_kind: mechanical
severity_default: low
---

# Inside an aligned block every glyph has a context-independent width

## Thesis
In a block whose columns are meant to line up — a table drawn with spaces, an ASCII diagram, a bar row — use only characters whose display width is fixed by the character itself.

## Rationale
The width of a rendered column cannot be computed from the characters alone. The standard that classifies characters into six width categories, resolving to two abstract widths, disclaims exactly the use one would reach for: "The East_Asian_Width property is not intended for use by modern terminal emulators without appropriate tailoring on a case-by-case basis." Its ambiguous class states the problem outright — "Ambiguous characters require additional information not contained in the character code to further resolve their width" — and defaults them to narrow only where the context cannot be established. So no character count repairs an indeterminate glyph: the block lines up in one reader's terminal and breaks in another's, from the same bytes. The rule is therefore about choosing determinate glyphs, not about counting them.

## Example
```
bad:  | done ✓ | 12 |    the mark's width is not fixed by the character
good: | done   | 12 |    a determinate glyph, or the word, holds the column
```

## Limits
Covers a block whose columns are meant to align. Prose that reflows, and the same character used outside an aligned block, are out of scope. The check is glyph determinacy rather than an arithmetic one, and no column limit follows from it — a width cap is a separate matter with a separate basis.

## Validator
For each aligned block, inspect every character against the fixed-width set the block relies on. Flag ambiguous-width characters, emoji, and any glyph whose rendered width depends on the reader's terminal, font, or locale, and propose a determinate replacement or the word it stands for. Validator question: is every glyph in this block one whose width the character itself fixes?

## Patch output
When auditing an aligned block containing a glyph of indeterminate width, emit one patch (`rule_id: S-09`, `location` set to the block and line hint, `current` = the offending line, `proposed` = the line with a determinate glyph or the spelled-out word, severity low). Membership in the ambiguous and emoji sets is decidable from the character, so no `needs_human` flag.

## Source
Unicode Standard Annex #11, *East Asian Width* (<https://www.unicode.org/reports/tr11/>) — six property values (Wide, Fullwidth, Halfwidth, Narrow, Ambiguous, Neutral) resolving to two abstract widths; "The East_Asian_Width property is not intended for use by modern terminal emulators without appropriate tailoring on a case-by-case basis"; "Ambiguous characters require additional information not contained in the character code to further resolve their width", defaulting to narrow where context cannot be established.
