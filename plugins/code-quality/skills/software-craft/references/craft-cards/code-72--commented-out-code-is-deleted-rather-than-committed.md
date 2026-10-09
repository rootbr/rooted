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


A commented-out test or check whose failure the change does not fix is judged by its own rule, which keeps it in the suite under a skip or expected-failure mark with its reason and tracking issue rather than deleting it.
## Validator
Grep the added lines of the hunk for comment lines and block comments, and for a multi-line string literal that stands alone as a statement. Read each match together with the run of consecutive comment lines it belongs to. Strip the comment markers and read the text as the file's language: a statement, a declaration, an assignment, a call, a control-flow header or a closing brace. Skip a doc comment or documentation string and the examples inside it, a directive or suppression a tool reads, an encoding declaration, a license header, a task marker, prose that resembles code, generated code, and any comment matching a keep pattern the project context declares. Take a line the hunk removes and re-adds as a comment, or a preamble such as "old version" or "kept just in case", as confirmation that the run is disabled code. Validator question: **Does an added comment, or a multi-line string literal standing alone as a statement, hold code written to run that the change disabled or kept beside its replacement, rather than documentation, a directive or prose?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-72`, severity minor, `file`, `symbol`, `code` = the commented-out lines quoted verbatim from the diff, with any preamble comment that announces them, `fix` = the same lines of the hunk with the commented-out code and its preamble deleted and the live code unchanged, in the file's language, `rationale` = that the lines are disabled code that never runs and goes out of date, and that version control history keeps the old version).

## Source
- SonarSource S125 "Sections of code should not be commented out" (SonarSource/sonar-python, `python-checks/src/main/resources/org/sonar/l10n/py/rules/python/S125.html`; the same text in SonarSource/sonar-java, `sonar-java-plugin/src/main/resources/org/sonar/l10n/java/rules/java/S125.html`): "Commented-out code distracts the focus from the actual executed code. It creates a noise that increases maintenance code. And because it is never executed, it quickly becomes out of date and invalid."; "Commented-out code should be deleted and can be retrieved from source control history if required."; `S125.json`: `"type": "CODE_SMELL"`, `"defaultSeverity": "Major"`, tag `unused`; listed in the Python `Sonar_way_profile.json` (fetched)
- S125 checks (SonarSource/sonar-java, `java-checks/src/main/java/org/sonar/java/checks/CommentedOutCodeLineCheck.java`; SonarSource/sonar-python, `python-checks/src/main/java/org/sonar/python/checks/CommentedCodeCheck.java`): `boolean isJavadocOrMarkdownComment = syntaxTrivia.isComment(CommentKind.JAVADOC, CommentKind.MARKDOWN);`; "We assume that comment before the first code token is a license header."; "JSNI methods are declared native and contain JavaScript code in a specially formatted comment block"; rule property `exception`: "Regular expression used to ignore commented out code. Only a full match is excluded."; `"source code encoding" comments (e.g. # coding=utf8) should be excluded`; generated files return early through `isGeneratedFile(ctx)`; a string checked as code when `firstElement.isTripleQuoted() && parent.is(Tree.Kind.EXPRESSION_STMT)` (fetched)
- Ruff ERA001 `commented-out-code` (astral-sh/ruff, `crates/ruff_linter/src/rules/eradicate/rules/commented_out_code.rs` and `detection.rs`): "Commented-out code is dead code, and is often included inadvertently. It should be removed."; "Prone to false positives when checking comments that resemble Python code, but are not actually Python code"; "Ignore task tag comments (e.g., "# TODO(tom): Refactor")."; allowlist entries `noqa`, `type:\s*ignore`, `fmt:\s*(on|off|skip)`, `region|endregion`, `SPDX-License-Identifier:` (fetched)
- PEP 257, What is a Docstring? (python/peps, `peps/pep-0257.rst`): "A docstring is a string literal that occurs as the first statement in a module, function, class, or method definition." (fetched)
- Rust API Guidelines C-EXAMPLE (rust-lang/api-guidelines, `src/documentation.md`): "Every public module, trait, struct, enum, function, method, macro, and type definition should have an example that exercises the functionality." (fetched)
- Go Doc Comments § Code blocks (golang/website, `_content/doc/comment.md`): "Code blocks often contain Go code." (fetched)
- Effective Go § Commentary (golang/website, `_content/doc/effective_go.html`): block comments "are useful within an expression or to disable large swaths of code." (fetched)
- Fixture: eval 5 `dead-commented-old-code` (rootbr/rooted, `plugins/evidence-based-authoring/skills/auditing-ai-context/evals/seeds/seed5_dead_code.swift`, `evals/evals.json`): a block under "// Old render path, kept just in case:" beside the live `render`; expected output "The commented-out old render path is gone; current render kept." (fetched)
- jest-community/eslint-plugin-jest docs/rules/no-disabled-tests.md (fetched) — "Before committing changes we may want to check that all tests are running. This rule raises a warning about disabled tests."

Caveat: the evidence is tool-rule documentation, the tools' own checks and one fixture; no study measuring a defect or comprehension cost of commented-out code is cited.
