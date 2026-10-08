---
title: While an old module or API stays reachable during a migration off it, the project's analyzer is configured to reject new uses of it and to name the replacement
rule_id: CHG-32
domain: change
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['(?i)no-restricted-(?:imports|syntax|properties)|banned[-_]?api|TID251|disallowed[-_](?:methods|types|macros)|IllegalImport|depguard|forbidigo', '@[Dd]eprecated\b|#\[deprecated\b|//\s*Deprecated:|@warnings[.]deprecated\(']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# While an old module or API stays reachable during a migration off it, the project's analyzer is configured to reject new uses of it and to name the replacement

## Thesis
While an old module, type or function stays reachable during a migration away from it, because uses of it remain or because it lives in code the project cannot delete, the project's analyzer configuration rejects new uses of it with a message that names the replacement, and the existing uses are recorded in a committed baseline or as suppressions that are removed as callers move.

## Rationale
Removing the existing uses of a path and keeping new ones out are two separate jobs: existing violations must be resolved before a rule can be enabled as an error, but while that work goes on other violations may occur, and unless the rule is enabled early it becomes harder and harder to enable as the code base grows. Two modules with similar or identical functionality bloat the project and carry the maintenance cost of two dependencies when one would suffice, so a project that has standardized on one wants the alternative left unused. A restriction entry in the analyzer configuration enforces such a convention project-wide automatically, including a convention around certain modules or module members that the language itself cannot enforce. An entry can carry a message displayed when the restricted path is used, appended to the analyzer's error or offered as a suggested replacement, so an entry whose message names the replacement puts that name in the report on every new use. Suppressing the existing violations lets the rule be enforced for new code while those violations are addressed at the project's own pace; the suppressions file is committed so that every developer shares it, and where the analyzer reports as an error a suppression whose violation has been resolved, the record is worked down as callers move.

## Example
```typescript
bad:  /** @deprecated Use fetchItem from "./client". */
      export function loadItem(id: string) { ... }
      // eslint.config.js: no "no-restricted-imports" entry for loadItem,
      // and "@typescript-eslint/no-deprecated" is not set to "error"
good: export default [{ rules: { "no-restricted-imports": ["error", {
        patterns: [{ regex: "(^|/)legacy-client$", importNames: ["loadItem"],
          message: "Use fetchItem from './client' instead." }],
      }] } }];
```

## Limits
A deprecation marker on the old path whose text names the replacement meets the rule where the analyzer runs, as an error, a rule that reports every reference to code carrying that marker and quotes the marker's text in its report; a rule whose report omits that text rejects the use without naming the replacement, and a marker that an editor only displays, with no analyzer rule reporting the references, leaves new uses unreported. An entry that exempts named files or test files still meets the rule, since the configuration need not apply the check across the whole code base. An entry catches the uses the analyzer resolves; a use reached through dynamic loading or evaluation passes it, so the entry guards against accidental uses rather than deliberate circumvention. The rule does not reach the decision to deprecate, the announcement of a deprecation, or the removal of the old path that ends the migration.

## Validator
Grep the hunk for a deprecation marker (`@deprecated`, `#[deprecated`, `Deprecated:`, `warnings.deprecated(`), for an edit to a restricted-path entry of the analyzer configuration (`no-restricted-imports`, `banned-api`, `disallowed-methods`, `depguard`, `forbidigo`, `IllegalImport`), and for call sites moved from an old module, type or function to a new one. Name the old path and confirm at head that it stays reachable: still defined in the repository, or provided by a dependency the project keeps. Open the analyzer configuration at head and at base (`git show <base_sha>:<path>`) and look for an entry that rejects uses of the old path at error level, reading the level wherever the analyzer sets it (in the entry itself, in a separate lint-level table or attribute, or in the command that turns warnings into errors), or an error-level rule that reports every reference to code carrying the deprecation marker and quotes the marker's text in its report; read the entry's message or the marker's text for the name of the replacement. Trace every use of the old path that the hunk adds and every suppression or baseline entry that it adds. Validator question: **Does the change leave an old module, type or function reachable during a migration away from it with no error-level analyzer entry at head that rejects new uses and names the replacement, or does it add, outside the files the entry exempts, a use of the old path or a suppression for a use the base did not contain?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-32`, severity minor, `file`, `symbol`, `code` = the deprecation marker, the moved call site, the configuration entry or the added use of the old path, quoted verbatim from the diff, `fix` = the analyzer configuration entry that rejects uses of the old path with a message naming the replacement, in the configuration file's own format, with the existing uses moved to a committed suppressions record, `rationale` = names the old path, its replacement, and that new uses stay possible while the old path stays reachable).

## Source
- ESLint rule `no-restricted-imports`, eslint/eslint `docs/src/rules/no-restricted-imports.md`: "Your project may have standardized on a module. You want to make sure that the other alternatives are not being used as this would unnecessarily bloat the project and provide a higher maintenance cost of two dependencies when one would suffice."; "(The custom message is appended to the default error message from the rule.)" (fetched)
- ESLint 'Bulk Suppressions', eslint/eslint `docs/src/use/suppressions.md`: "Unless the rule is enabled during the early stages of the project, it becomes harder and harder to enable it as the codebase grows. Existing violations must be resolved before enabling the rule, but while doing that other violations may occur."; "While the rule will be enforced for new code, the existing violations will not be reported. This way, you can address the existing violations at your own pace."; "You should commit this file to the repository so that the suppressions are shared with all the developers."; "an error is reported about unused suppressions" (fetched)
- Ruff rule TID251 `banned-api`, astral-sh/ruff `flake8_tidy_imports/rules/banned_api.rs`, `flake8_tidy_imports/settings.rs`, `ruff_workspace/src/options.rs`: "Projects may want to ensure that specific modules or module members are not imported or accessed."; "projects may adopt conventions around the use of certain modules or module members that are not enforceable by the language itself. This rule enforces certain import conventions project-wide automatically."; "The message to display when the API is used."; "this rule is only meant to flag accidental uses, and can be circumvented via `eval` or `importlib`." (fetched)
- Clippy lint `disallowed_methods`, rust-lang/rust-clippy `clippy_lints/src/disallowed_methods.rs`: "Denies the configured methods and functions in clippy.toml"; "Can also add a `replacement` that will be offered as a suggestion."; "Note: Even though this lint is warn-by-default, it will only trigger if methods are defined in the clippy.toml file." (fetched)
- depguard, OpenPeeDeeP/depguard `README.md`: "It can also deny a list of packages"; "`packageErrorMessages` is a mapping from packages to the error message to display"; "`inTests` is a list of packages allowed/disallowed only in test files."; "we need not apply package import checks across our entire code base." (fetched)
- Checkstyle `IllegalImport`, checkstyle/checkstyle `checks/imports/IllegalImportCheck.java`: "Checks for imports from a set of illegal packages and modules." (fetched)
- Checkstyle configuration, checkstyle/checkstyle `src/site/xdoc/config.xml`, §Custom messages: "Each check configuration element can have zero or more message elements." (fetched)
- forbidigo, ashanbrown/forbidigo `README.md`: "`msg`: an additional comment that gets added to the error message when a pattern matches." (fetched)
- typescript-eslint rule `no-deprecated`, typescript-eslint/typescript-eslint `packages/eslint-plugin/docs/rules/no-deprecated.mdx`: "This rule reports on any references to code marked as `@deprecated`."; "allowing editors to visually indicate deprecated code [...] However, TypeScript doesn't report type errors for deprecated code on its own." (fetched)
- typescript-eslint rule `no-deprecated`, typescript-eslint/typescript-eslint `packages/eslint-plugin/src/rules/no-deprecated.ts`, message `deprecatedWithReason`: "`{{name}}` is deprecated. {{reason}}"; `packages/eslint-plugin/src/configs/flat/strict-type-checked.ts`: "'@typescript-eslint/no-deprecated': 'error'" (fetched)
- OpenJDK javac, openjdk/jdk `src/jdk.compiler/share/classes/com/sun/tools/javac/resources/compiler.properties`, `compiler.warn.has.been.deprecated`: "{0} in {1} has been deprecated" (fetched)
- Caveat: tool documentation states the mechanism and the cost of keeping two alternatives; no measured study of new uses added during a migration was reachable.
