---
title: A finding on code the change adds or modifies is fixed in the code, with the tool's own fix where one exists, and is suppressed only when it is a false positive or cannot be avoided
rule_id: TOOL-14
domain: tooling
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['#\s*(?:noqa|type:\s*ignore|pyright:\s*ignore|pylint:\s*disable|ruff:\s*(?:noqa|ignore|file-ignore|disable))', 'eslint-disable|@ts-(?:ignore|expect-error|nocheck)', '@Suppress(?:Warnings|FBWarnings)\(', '#!?\[(?:allow|expect)\(', '//\s*(?:nolint|lint:(?:file-)?ignore)\b', '(?m)(?:^[+ \t]*|\b(?:var|let)[ \t]+)_[ \t]*=[ \t]*[A-Za-z_][\w.]*[ \t]*;?[ \t]*(?://|#|$)']
scope: file
check_kind: semantic
severity_default: major
---

# A finding on code the change adds or modifies is fixed in the code, with the tool's own fix where one exists, and is suppressed only when it is a false positive or cannot be avoided

## Thesis
When the project's configured analyzer or type checker reports a finding on code the change adds or modifies, the change rewrites that code so the finding goes away. Where the tool offers a safe automatic fix for the finding, one that keeps the code's runtime behavior, the change applies it instead of suppressing the finding. The change adds a suppression through the language's suppression mechanism only with a clear and valid reason: a genuine false positive, which is also reported so that it can be fixed, or a rare case where the code has to look odd enough to confuse the tool or a well-meant suggestion does not apply. A placeholder that only quiets a check during development, such as a dummy reference that keeps an unused import alive, is deleted before the change is committed.

## Rationale
If a problem is worth complaining about, it is worth fixing in the code. Comment directives that suppress a type checker's errors reduce the type checker's effectiveness overall, and correcting the code makes the directives unnecessary. In a study of 1,425 open-source projects that suppress the warnings of a bug-pattern analyzer, false positives accounted, contrary to expectations, for a minor proportion of suppressions, and a significant number of suppressions introduced technical debt. In 20 open-source projects that run static analysis tools in continuous integration, build breakages due to those tools were quickly fixed by actually solving the problem rather than by disabling the warning. Running the tool's automatic fix before suppressing anything keeps a violation that can be auto-fixed from being suppressed.

## Example
```go
bad:  //lint:ignore SA1019 still works
      _, err := f.Seek(0, os.SEEK_SET)
good: _, err := f.Seek(0, io.SeekStart)
```

## Limits
A suppression is correct for a genuine false positive and for the rare case where the code has to look odd enough to confuse the tool, such as a test that deliberately compares the results of two identical calls. For a check that flags outright-wrong code, suppressing a finding calls for thinking twice or for feedback to the tool. For a check that flags likely-wrong code or a matter of style, fixing remains the typical response, and a suppression comment that states its reason is an accepted outcome. A suppression directive added as a temporary measure for a pressing issue is acceptable only with a recorded follow-up task to address the underlying problem. When a rule is first enabled on a codebase, its existing violations may be suppressed all at once, with the tool's automatic fix run first so that no violation that can be auto-fixed is suppressed. A placeholder reference lets unused things persist while the code is being developed. Findings on code the change leaves untouched are outside the rule.

## Validator
Grep the hunk's added lines for a suppression directive and for a placeholder that only references an otherwise unused item, such as an imported name or a local value assigned to a discarded target, often with a note to delete it. Open the file and read the line the directive silences: name the check, what it reports there, and whether the line is code the change adds or modifies. Decide whether rewriting the line would remove the finding, whether the tool offers a safe automatic fix for it, and whether the directive or its comment states a genuine false positive, a clear and valid reason the code has to take this form, or, for a suppression directive added as a temporary measure for a pressing issue, a recorded follow-up task to address the underlying problem. Validator question: **Does the change add a suppression or a placeholder for a finding on its own code that a rewrite or the tool's safe automatic fix would remove, with no genuine false positive, no clear and valid reason and, for a temporary suppression directive, no recorded follow-up task stated?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-14`, severity major, `file`, `symbol`, `code` = the suppression directive or placeholder and the line it silences, verbatim from the diff, `fix` = the rewritten line with the finding gone or the tool's safe automatic fix applied, in the file's language, `rationale` = the check the directive silences and why the finding is neither a false positive nor unavoidable).

## Source
- Staticcheck documentation, Configuration § Ignoring problems with linter directives (go-tools website/content/docs/configuration/_index.md): "Dubious code should be rewritten and genuine false positives should be reported so that they can be fixed." … "Sometimes code just has to look weird enough to confuse tools, and sometimes suggestions, though well-meant, just aren't applicable. For those rare cases, there are several ways of ignoring unwanted problems." (fetched)
- ESLint documentation, Configure Rules § Use configuration comments, "Use with Caution" (eslint docs/src/use/configure/rules.md): "Disabling ESLint rules inline should be restricted and used only in situations with a clear and valid reason for doing so. Disabling rules inline should not be the default solution to resolve linting errors." … "If a disable comment is added as a temporary measure to address a pressing issue, create a follow-up task to address the underlying problem adequately." (fetched)
- ESLint documentation, Bulk Suppressions (eslint docs/src/use/suppressions.md): "After you enable a rule as `"error"` in your configuration file, you can suppress all the existing violations at once … It is recommended to execute the command with the `--fix` flag so that you don't suppress violations that can be auto-fixed." (fetched)
- typescript-eslint rule ban-ts-comment (packages/eslint-plugin/docs/rules/ban-ts-comment.mdx): "Using these to suppress TypeScript compiler errors reduces the effectiveness of TypeScript overall. Instead, it's generally better to correct the types of code, to make directives unnecessary." (fetched)
- Ruff documentation, The Ruff Linter, rule categories, a preview feature (ruff docs/linter.md): "If you encounter a correctness issue, you should try to fix it rather than suppressing the error with `noqa` or `ruff: ignore`." … "You will still typically want to fix these issues, but using a suppression comment may occasionally be necessary." … "In general, you should feel comfortable using a `ruff: ignore` comment on diagnostics from the `suspicious` or lower categories but think twice (or share feedback!) about suppressing a `correctness` lint." … of the `complexity`, `performance` and `style` categories: "even if you enable these categories, you should feel comfortable ignoring certain rules project-wide or inline with suppression comments." (fetched)
- Ruff documentation, The Ruff Linter § Fix safety (ruff docs/linter.md): "The meaning and intent of your code will be retained when applying safe fixes, but the meaning could change when applying unsafe fixes." … "an unsafe fix could lead to a change in runtime behavior, the removal of comments, or both" (fetched)
- Go FAQ, unused variables and imports (golang/website _content/doc/faq.md): "if it's worth complaining about, it's worth fixing in the code" … "Use the blank identifier to let unused things persist while you're developing." … "var _ = unused.Item  // TODO: Delete before committing!" (fetched)
- MSR 2017, DOI 10.1109/MSR.2017.2, abstract: "build breakages due to static analysis tools are quickly fixed by actually solving the problem, rather than by disabling the warning" (fetched, IEEE metadata mirror)
- arXiv:2311.07482, abstract: "Contrary to expectations, false positives account for a minor proportion of suppressions. A significant number of suppressions introduce technical debt" (fetched, arXiv listing mirror)
- Caveat: both studies examined Java projects (1,425 using FindBugs or SpotBugs; 20 on Travis CI, where breakages came mainly from coding-standard checks); the statement on suppressed type-checker errors is the TypeScript linter's; the other statements are the tools' own documentation.
