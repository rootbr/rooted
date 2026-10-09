---
title: A suppression names the specific diagnostics it silences and never silences every diagnostic on its line, block or file
rule_id: TOOL-18
domain: tooling
step: [implement, review]
applies_to: [universal]
triggers: ['(?i)#\s*(?:(?:ruff|flake8):\s*)?noqa\b(?!\s*:)', '#\s*type:\s*ignore(?!\s*\[)', '(?m)eslint-disable(?:-next-line|-line)?[ \t]*(?:\*/|-->|--|$)', '//\s*nolint(?::(?:[\w-]+,\s*)*all\b|(?![:\w]))', '@SuppressWarnings\(\s*(?:value\s*=\s*)?"all"', '#!?\[allow\(\s*(?:warnings|clippy::all)\b', '@SuppressFBWarnings\b(?![^\n]*\bEXACT\b)']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A suppression names the specific diagnostics it silences and never silences every diagnostic on its line, block or file

## Thesis
Where the suppression mechanism accepts the identifier of a diagnostic, every suppression names exactly the diagnostics it is meant to silence: a coded ignore rather than a bare one, named rules rather than a disable-all, an exact identifier rather than a prefix match, so that only the expected diagnostics are silenced on its line, block or file.

## Rationale
A suppression that names no diagnostic silences every diagnostic in its reach, so it can hide issues in the code and may cause warnings to be overlooked unintentionally. On a line whose ignore was meant for one expected error, a typo in an attribute name goes unreported, because both the expected error and the unexpected one are silenced; with the expected error's code named, the line reports the typo. Naming the code clarifies the intent of the suppression and ensures that only the expected errors are silenced. A blanket suppression is also harder to interpret and maintain, because it does not say which diagnostics it was meant to suppress. A suppression matched by prefix silences every diagnostic whose identifier begins with the given text, such as two bug types for one truncated name; an exact match silences the named diagnostic and not a neighbour whose identifier extends it. A study of suppressions for four static analyzers in projects written in three languages found that some suppressions may unintentionally hide future warnings.

## Example
```typescript
bad:  // eslint-disable-next-line
      function onMessage(event: any): void { console.log(event.data); }
good: // eslint-disable-next-line @typescript-eslint/no-explicit-any -- sender defines the payload shape
      function onMessage(event: any): void { console.log(event.data); }
```

## Limits
Some mechanisms accept no diagnostic identifier, such as a comment that always suppresses all errors that originate on the following line; such a mechanism is outside the rule, and for it the recommended practice is that the remainder of the comment explain which error is being suppressed. A directive that accepts identifiers but names none stays inside the rule. Whether a suppression still has an effect and whether it carries an explanation are separate checks from whether it names the diagnostic it suppresses.

## Validator
Grep the hunk for added or changed suppressions of the language's suppression mechanism and of the project's configured analyzer: suppression comments, annotations and attributes. For each, read what follows the directive keyword: a list of codes, rule names or lint names, a catch-all value, or nothing. Skip a mechanism that accepts no diagnostic identifier. Read the line, block or file the suppression covers only to name, for the fix, the diagnostic the covered code raises. Validator question: **Does an added or changed suppression, in a mechanism that accepts diagnostic identifiers, name no diagnostic, name only a catch-all value such as all or warnings, or name an identifier that the mechanism matches by prefix and that begins the identifier of another diagnostic?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-18`, severity major, `file`, `symbol`, `code` = the suppression line verbatim from the diff, `fix` = the same suppression naming the specific code, rule or lint the covered code raises, or its exact-match form, in the file's language, `rationale` = names that the suppression also silences diagnostics nobody meant to silence, including ones introduced later, and does not say which diagnostic it was meant for).

## Source
- Ruff rule PGH004 blanket-noqa, astral-sh/ruff crates/ruff_linter/src/rules/pygrep_hooks/rules/blanket_noqa.rs (fetched): "Suppressing all diagnostics can hide issues in the code. Blanket `noqa` annotations are also more difficult to interpret and maintain, as the annotation does not clarify which diagnostics are intended to be suppressed."
- mypy docs, ignore-without-code, python/mypy docs/source/error_code_list2.rst (fetched): "This clarifies the intent of the ignore and ensures that only the expected errors are silenced." Its example: "This line has a typo that mypy can't help with as both: the expected error 'assignment', and the unexpected error 'attr-defined' are silenced"; with `# type: ignore[assignment]`, "This line warns correctly about the typo in the attribute name".
- eslint-plugin-eslint-comments no-unlimited-disable, docs/rules/no-unlimited-disable.md (fetched): "`eslint-disable` directive-comments disable all rules by default. This may cause to overlook some ESLint warnings unintentionally. So you should specify the rules to disable accurately."
- SpotBugs SuppressFBWarnings.matchType() Javadoc, spotbugs-annotations/.../SuppressFBWarnings.java (fetched): "@SuppressFBWarnings(value = "EI_EXPO", ...) will suppress bugs of type EI_EXPOSE_REP and EI_EXPOSE_REP2"; "matchType=EXACT ... to suppress EI_EXPOSE_REP, but not EI_EXPOSE_REP2".
- TypeScript 2.6 release notes, microsoft/TypeScript-Website packages/documentation/copy/en/release-notes/TypeScript 2.6.md (fetched): "A `// @ts-ignore` comment suppresses all errors that originate on the following line. It is recommended practice to have the remainder of the comment following `@ts-ignore` explain which error is being suppressed."
- golangci-lint nolintlint settings, .golangci.reference.yml (fetched): "require nolint directives to mention the specific linter being suppressed"; "require an explanation of nonzero length after each nolint directive"; "ensure that all nolint directives actually have an effect".
- DOI 10.1145/3715729, abstract, via PurCL/ASE data/rawdata/2025/FSE2025.bib (fetched): "studying projects written in three popular languages and suppressions for warnings by four popular static analyzers ... some suppressions, including useless ones, may unintentionally hide future warnings".
- Caveat: the evidence is analyzer and compiler documentation plus one empirical study; none measures how often a blanket suppression hides a real defect.
