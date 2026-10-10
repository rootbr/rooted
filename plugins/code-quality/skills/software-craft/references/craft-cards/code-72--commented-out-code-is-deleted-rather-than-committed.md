---
title: Commented-out code is deleted rather than committed, because version control keeps the old version
rule_id: CODE-72
domain: code
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['signal:commented_out_code', '^\s*(//|#)\s*(if|for|while|return|def|fn|func|function|var|let|const|import|from|class)\b.*[;:{()=]\s*$', '^\s*(//|#(?!\[))\s*(([\w.\[\]<>,?]+\s+)?[\w.\[\]]+\s*(=|:=|\+=|-=)\s*\S.*|[\w.:]+!?\(.*\)\s*;?)\s*$', '^\s*(/\*|"{3}|\x27{3})\s*$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Commented-out code is deleted rather than committed, because version control keeps the old version

## Thesis
Code that a change stops running is deleted, not turned into a comment, and the comments a change adds hold no code written to run: no statement, declaration or block disabled by placing it inside a comment, or inside a multi-line string literal that stands alone as a statement. When the old version is required again, it is retrieved from version control history.

## Rationale
Commented-out code is never executed, so it quickly becomes out of date and invalid. It distracts the reader from the code that actually executes and adds noise to the code being maintained. It is dead code, and it is often included inadvertently. Version control history keeps the old version, so it can be retrieved from there if required, and the file need not carry it. The fix deletes the disabled lines, including a preamble that says they are kept just in case, and leaves the live code as it was.

## Example
```python
bad:  def total(items):
          # subtotal = sum(i.price for i in items)
          # return subtotal * (1 + tax_rate)
          return sum(i.price * i.qty for i in items)
      """
      def total_with_tax(items): ...
      """
good: def total(items):
          return sum(i.price * i.qty for i in items)
```

## Limits
A doc comment, or a documentation string where the language uses one, is documentation rather than disabled code, and so is the example code that the language's documented doc-comment convention puts inside it. Prose that merely resembles code is not commented-out code. A comment that a tool reads is not commented-out code either: a linter or type-checker suppression, a formatter switch, an encoding declaration, a license header at the top of the file, a region marker, and code that a tool compiles from a specially formatted comment. A task marker with its note is not commented-out code. Generated code is outside the rule. A project may declare a pattern for comments it keeps on purpose, in its project context or as its analyser's exception setting; a comment that matches it is outside the rule. Disabling code with a comment while editing is a documented use of block comments; the rule judges what the change commits, which is what version control history keeps.

A commented-out test or check whose failure the change does not fix is a disabled test, and the rule on disabled tests judges it.

## Validator
Grep the added lines of the hunk for comment lines and block comments, and for a multi-line string literal that stands alone as a statement. Read each match together with the run of consecutive comment lines it belongs to. Strip the comment markers and read the text as the file's language: a statement, a declaration, an assignment, a call, a control-flow header or a closing brace. Skip a doc comment or documentation string and the examples inside it, a directive or suppression a tool reads, an encoding declaration, a license header, a task marker, prose that resembles code, generated code, and any comment matching a keep pattern the project context declares. Take a line the hunk removes and re-adds as a comment, or a preamble such as "old version" or "kept just in case", as confirmation that the run is disabled code. Validator question: **Does an added comment, or a multi-line string literal standing alone as a statement, hold code written to run that the change disabled or kept beside its replacement, rather than documentation, a directive or prose?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-72`, severity minor, `file`, `symbol`, `code` = the commented-out lines quoted verbatim from the diff, with any preamble comment that announces them, `fix` = the same lines of the hunk with the commented-out code and its preamble deleted and the live code unchanged, in the file's language, `rationale` = that the lines are disabled code that never runs and goes out of date, and that version control history keeps the old version).
