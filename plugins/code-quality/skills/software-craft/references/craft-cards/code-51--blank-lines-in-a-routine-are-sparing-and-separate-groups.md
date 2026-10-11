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

## Source
- PEP 8, Code Lay-out > Blank Lines (python/peps, `peps/pep-0008.rst`): "Surround top-level function and class definitions with two blank lines."; "Method definitions inside a class are surrounded by a single blank line."; "Use blank lines in functions, sparingly, to indicate logical sections." (fetched)
- Google Java Style Guide §4.6.1 Vertical whitespace (google/styleguide, `javaguide.html`): "A single blank line always appears: Between consecutive members or initializers of a class"; "A single blank line may also appear anywhere it improves readability, for example between statements to organize the code into logical subsections."; "Multiple consecutive blank lines are permitted, but never required (or encouraged)." (fetched)
- Google TypeScript Style Guide, Formatting functions (google/styleguide, `tsguide.html`): "Blank lines at the start or end of the function body are not allowed. A single blank line may be used within function bodies sparingly to create logical groupings of statements." (fetched)
- Rust Style Guide, Blank lines (rust-lang/rust, `src/doc/style-guide/src/README.md`): "Separate items and statements by either zero or one blank lines (i.e., one or two newlines)." (fetched)
- Checkstyle `EmptyLineSeparator`, property `allowMultipleEmptyLinesInsideClassMembers` (checkstyle/checkstyle, `src/site/xdoc/checks/whitespace/emptylineseparator.xml`): "To disallow multiple empty lines inside constructor, initialization block and method" set it to `false` (fetched)
- ESLint `no-multiple-empty-lines` (eslint/eslint, `docs/src/rules/no-multiple-empty-lines.md`; deprecated in core per `lib/rules/no-multiple-empty-lines.js`, `deprecatedSince: "8.53.0"`): "Whitespace is useful for separating logical sections of code, but excess whitespace takes up more of the screen."; "This rule aims to reduce the scrolling required when reading through your code." (fetched)
- Prettier Rationale, Empty lines (prettier/prettier, `docs/rationale.md`): "empty lines are very hard to automatically generate. The approach that Prettier takes is to preserve empty lines the way they were in the original source code."; "Prettier collapses multiple blank lines into a single blank line."; "Empty lines at the start and end of blocks (and whole files) are removed." (fetched)
- Black code style, Empty lines (psf/black, `docs/the_black_code_style/current_style.md`): "_Black_ avoids spurious vertical whitespace."; "_Black_ will allow single empty lines inside functions, and single and double empty lines on module level left by the original editors"; its example output keeps one empty line between a function's signature and `print("One empty line above me will be kept!")` (fetched)
- Go printer (golang/go, `src/go/printer/printer.go`): "maxNewlines = 2     // max. number of newlines between source text" (fetched)
- ESLint `newline-after-var` (eslint/eslint, `docs/src/rules/newline-after-var.md`): "Some developers leave an empty line between var statements and the rest of the code"; "Whereas others don't leave any empty newlines at all."; `"always"` (default) "requires an empty line after `var`, `let`, or `const`" (fetched)
- wsl (bombsimon/wsl, `README.md`): "a linter that wants you to use empty lines to separate grouping of different types to increase readability"; "Expressions are e.g. function calls or index expressions, they should only be cuddled with variables used on the line above" (fetched)
- DOI 10.1109/TSE.2009.70, Abstract: "With data collected from 120 human annotators, we derive associations between a simple set of local code features and human notions of readability."; "our data suggest that comments, in and of themselves, are less important than simple blank lines to local judgments of readability." (fetched); §6: "our model of readability is descriptive rather than normative or prescriptive. That is, while it can be used to predict human readability judgments for existing software, it cannot be directly interpreted to prescribe changes that will improve readability. For example, while 'average number of blank lines' is a powerful feature in our metric that is positively correlated with high readability, merely inserting five blank lines after every existing line of code need not improve human judgments of that code's readability." (relayed)
- arXiv:2208.12141 §4.2 Spacing, reporting DOI 10.1145/3196321.3196342: "a survey with 55 students and 7 professionals to investigate the impact of a set of Java coding practices on code understandability"; "the authors asked the subjects (by presenting code examples) whether blank lines must be used to create a vertical separation between related instructions (Giving an opinion). The results also did not show a statistically significant difference (Two-tailed test for proportion, p = 1.0) between subjects who agree and disagree with this practice." (fetched)

Caveat: the research is a descriptive model of annotators' readability judgments and an opinion survey on Java coding practices; the rule's form rests on the style documents and the formatters' documented behaviour.
