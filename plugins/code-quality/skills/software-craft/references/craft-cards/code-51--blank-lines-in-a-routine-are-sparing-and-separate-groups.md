---
title: Blank lines inside a routine are sparing, each separating one group of related statements from the next
rule_id: CODE-51
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['^[ \t]*$', 'signal:long_routine']
scope: hunk
check_kind: semantic
severity_default: suggestion
---

# Blank lines inside a routine are sparing, each separating one group of related statements from the next

## Thesis
Inside a routine body, a blank line between statements marks the boundary between two logical groups of related statements: the statements of one group follow each other with no blank line between them. Blank lines are used sparingly, at the boundaries between groups.

## Rationale
The style documents that name a purpose for a blank line between statements name the same one: to indicate a logical section, to organize the code into logical subsections, to create logical groupings of statements; two of them ask for it sparingly. Whitespace is useful for separating logical sections of code, but excess whitespace takes up more of the screen, and the check that limits it aims to reduce the scrolling required when reading code. Formatters for several of the languages keep a single blank line inside a function where the writer put it and collapse a run of blank lines to one, and one of them gives the reason that empty lines are very hard to generate automatically, so where the blank lines go is left to the writer. The measured evidence is correlational or opinion, and it does not show that adding blank lines improves readability. In a readability model fitted to the judgments of 120 annotators, the average number of blank lines was a powerful feature positively correlated with high readability, and the data suggest that comments in and of themselves are less important than simple blank lines to local judgments of readability; the model is descriptive rather than normative or prescriptive, cannot be directly interpreted to prescribe changes that will improve readability, and inserting five blank lines after every existing line of code need not improve those judgments. In an opinion survey of 55 students and 7 professionals, asked whether blank lines must be used to create a vertical separation between related instructions, the share who agreed did not differ significantly from the share who disagreed (two-tailed test for proportion, p = 1.0).

## Example
```typescript
bad:  const request = new Request(url);

      request.headers.set("Accept", "application/json");

      const response = await fetch(request);
good: const request = new Request(url);
      request.headers.set("Accept", "application/json");

      const response = await fetch(request);
```

## Limits
Blank lines outside a routine body follow the language's own counts and are outside the rule: one style guide surrounds top-level definitions with two blank lines and methods with one, another puts a single blank line between consecutive members of a class. A blank line directly after a body's opening line or before its closing line is left to the language's style guide and formatter, which disagree: one style guide disallows it and one formatter removes empty lines at the start and end of blocks, while another formatter keeps a single empty line at the top of a function body. A routine with no blank line between its groups is not flagged: most of the style documents permit a blank line between groups rather than require one, and the readability model cannot be directly interpreted to prescribe changes that will improve readability. A run of two or more blank lines between statements is not flagged: formatters collapse it to a single blank line, so it is style a formatter fixes; one style guide separates statements by zero or one blank lines, another permits consecutive blank lines while never requiring or encouraging them, and a linter check can be configured to disallow them inside a method. A blank line that a lint rule configured in the project requires by statement kind is not flagged: some linters place blank lines by the kind of statement rather than by the step, one requiring by default an empty line after variable declarations and another requiring one above a call that uses no variable from the line above, so the project's lint configuration decides those lines. A layout tolerance stated in the project context rejects the finding.

## Validator
Grep the hunk for added blank lines and for added statements that sit directly above or below a blank line of the hunk context; blank lines elsewhere in the routine are outside the change. Keep only those between two statements inside a routine body; skip a blank line between members, definitions or imports, one directly after a body's opening line or before its closing line, and one inside a string literal. For each blank line, read the statements on both sides in the hunk and name the step each side carries out: the two sides form one logical group when the statements below the blank line continue the step above it, such as finishing the value the statements above began to build or continuing one sequence of checks; a new step starts where the statements below take a finished value to its next use or begin another computation. Validator question: **Inside a routine body, does the change add or leave a blank line between statements that carry out one logical step?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-51`, severity suggestion, `file`, `symbol`, `code` = the statements on both sides of the blank line, with the blank line between them, quoted verbatim from the diff and including at least one added line, `fix` = the same statements with the blank line inside the group removed, in the file's language, `rationale` = the step the split statements carry out together).
