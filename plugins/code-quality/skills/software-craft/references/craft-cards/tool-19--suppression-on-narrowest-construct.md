---
title: A suppression sits on the narrowest construct where it takes effect, a line or a declaration, never on an enclosing class, module or file for a finding at one site
rule_id: TOOL-19
domain: tooling
step: [implement, review]
applies_to: [universal]
triggers: ['@ts-nocheck|#\s*(?:mypy:\s*ignore-errors|ruff:\s*(?:noqa|file-ignore|disable)|pyright:\s*basic)|//\s*lint:file-ignore', '/\*\s*eslint-disable(?!-(?:next-)?line)', '#!\[allow\(', '#\s*pylint:\s*disable=', '@SuppressWarnings\(', 'warnings[.](?:simplefilter|filterwarnings)\(\s*["'']ignore']
scope: file
check_kind: semantic
severity_default: minor
---

# A suppression sits on the narrowest construct where it takes effect, a line or a declaration, never on an enclosing class, module or file for a finding at one site

## Thesis
A suppression of a compiler or analyzer finding sits on the most deeply nested element where the language's suppression mechanism takes effect. The most fine-grained placement is the offending line itself, through an end-of-line directive or a directive on the line before it; findings spread through one block may share one suppression placed at the beginning of that block. Where the mechanism attaches only to declarations, it goes on the declaration that holds the finding, the function rather than its enclosing type. A range suppression that would otherwise run past the block holding its findings is closed explicitly by its matching enable directive, and a runtime warning filter is set inside a context that wraps only the code that triggers the warning.

## Rationale
A suppression applies to the element it is attached to and to every element that element contains, and the warnings suppressed in an element are the union of those suppressed in all elements around it. A disable directive whose enable directive is missing extends to the end of the file or of its enclosing scope, so a warning in those lines may be overlooked unintentionally. An explicit range prevents accidental suppression of violations, a risk the tool documentation singles out at module scope. A runtime filter wrapped around the triggering call lets known-deprecated code run without the warning, while other code that might not be aware of its use of deprecated code still reports it, unless that code runs concurrently with the wrapped call and the runtime keeps its filters in global state. The placement is mechanically enforceable: an analyzer can be configured so that named warnings cannot be suppressed on anything but variable and parameter declarations.

## Example
```go
bad:  //lint:file-ignore SA1019 one call to strings.Title below
      package label
      import "strings"
      func heading(s string) string { return strings.Title(s) }
good: package label
      import "strings"
      func heading(s string) string {
          //lint:ignore SA1019 labels hold only ASCII letters and spaces, so Title's word breaks hold
          return strings.Title(s)
      }
```

## Limits
A file-wide directive is the documented form for generated code: where code generation leaves the same finding at many sites, such as unused code, the generator injects a single file-wide directive instead of annotating every instance. Where the mechanism has no line or block form, the most deeply nested declaration where it is effective is the correct placement even when that declaration is larger than the finding. The rule judges where a suppression sits, not whether the finding deserves one.

## Validator
Grep the hunk for added suppressions: file-level directives, disable comments that open a range, attributes or annotations on a type, module or class, and calls that set a warning filter to ignore. Open the file and locate the findings each one is meant to silence: the line its reason names, or the lines that report the named rule once the suppression is removed. Taking the findings in each function or type as a separate group, trace outward from each group's lines to the smallest line, block, declaration or function that holds the group and that the language's suppression mechanism can attach to, and check whether the file carries a generated-code header. For a disable comment, look for its matching enable comment; for a warning filter, check that a context wraps only the triggering call. Validator question: **Does an added suppression cover an element wider than the narrowest one that the language's suppression mechanism can attach to and that holds the findings it is meant to silence, counting the findings in each function or type as a separate group, in a file that is not generated?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-19`, severity minor, `file`, `symbol`, `code` = the suppression directive, attribute or filter call quoted verbatim from the diff with the element it attaches to, `fix` = the same suppression moved onto the line, block or declaration of the finding, one suppression per function or type that holds findings, its range closed or its filter wrapped around the triggering call, in the file's language, `rationale` = names the finding the suppression targets and the wider code it also silences).

## Source
- Java SE API, `java.lang.SuppressWarnings` class documentation (openjdk/jdk tag jdk-21-ga, src/java.base/share/classes/java/lang/SuppressWarnings.java), paragraphs 1 to 3: "Indicates the warnings to be suppressed at compile time in the annotated element, and in all elements contained in the annotated element." "programmers should always use this annotation on the most deeply nested element where it is effective. For example, if you want to suppress a warning in a particular method, you should annotate that method rather than its class." "The set of warnings suppressed in a given element is a union of the warnings suppressed in all containing elements." (fetched)
- Python documentation, `warnings`, § Temporarily Suppressing Warnings (python/cpython main, Doc/library/warnings.rst): "This allows you to use known-deprecated code without having to see the warning while not suppressing the warning for other code that might not be aware of its use of deprecated code." § Concurrent safety of Context Managers: "If the context_aware_warnings flag is false, then catch_warnings will modify the global attributes of the warnings module. This is not safe if used within a concurrent program (using multiple threads or using asyncio coroutines)." (fetched)
- Google Python Style Guide §3.16.5 item 3 (google/styleguide gh-pages, pyguide.md): "Use a narrowly-scoped `pylint: disable=invalid-name` directive to silence warnings. For just a few variables, use the directive as an endline comment for each one; for more, apply the directive at the beginning of a block." (fetched) The block form is stated there for name warnings.
- Ruff documentation, § Error suppression (astral-sh/ruff main, docs/linter.md): "If no matching "enable" comment is found, Ruff will also treat this as an "implicit" range. The implicit range is defined from the starting "disable" comment, until reaching a logical scope indented less than the starting comment" "It is strongly suggested to use explicit range suppressions, in order to prevent accidental suppressions of violations, especially at global module scope." (fetched)
- eslint-plugin-eslint-comments rule `disable-enable-pair` (eslint-community/eslint-plugin-eslint-comments main, docs/rules/disable-enable-pair.md): "`eslint-disable` directive-comments disable ESLint rules in all lines preceded by the comment. If you forget `eslint-enable` directive-comment, you may overlook ESLint warnings unintentionally." (fetched)
- Checkstyle check `SuppressWarnings` (checkstyle/checkstyle master, src/site/xdoc/checks/annotation/suppresswarnings.xml), § Description and § Examples: "Allows to specify what warnings that @SuppressWarnings is not allowed to suppress. You can also specify a list of TokenTypes that the configured warning(s) cannot be suppressed on." "the "unchecked" and "unused" warnings cannot be suppressed on anything but variable and parameter declarations." (fetched)
- Staticcheck documentation, Configuration § Line-based linter directives and § File-based linter directives (dominikh/go-tools master, website/content/docs/configuration/_index.md): "The most fine-grained way of ignoring reported problems is to annotate the offending lines of code with linter directives." "The `//lint:ignore Check1[,Check2,...,CheckN] reason` directive ignores one or more checks on the following line of code." "code generation may leave behind a lot of unused code, as it simplifies the generation process. Instead of manually annotating every instance of unused code, the code generator can inject a single, file-wide ignore directive to ignore the problem." (fetched)
- Caveat: every source is language or tool documentation; no measured study of suppression scope backs the rule.
