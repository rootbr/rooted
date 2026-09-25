---
title: A boolean selector parameter that chooses between two paths is replaced by one method per path
rule_id: MNT-02
domain: maintainability
triggers: ['boolean \w+\s*[,)]', ',\s*(true|false)\s*[,)]', '\(\s*(true|false)\s*[,)]', 'if\s*\(\s*!?\w+\s*\)\s*\{']
scope: file
check_kind: mechanical
severity_default: minor
---

# A boolean selector parameter that chooses between two paths is replaced by one method per path

## Thesis
A method whose boolean parameter is tested to decide which of two branches the method runs is written as two methods, one per branch, each named for what it does; the caller then reads as `renderForSuite(page)` rather than `render(page, true)`.

## Rationale
At the call site a boolean literal shows its value and not its meaning, so every reader either guesses or opens the declaration; the parameter also declares that the method does at least two things. Two methods give each path a name, let each be tested and changed alone, and remove the branch. Where the boolean is data rather than a selector — stored or forwarded, not tested — the parameter is legitimate, and a call-site parameter comment such as `/* urgent= */ true` documents the literal.

## Example
```java
bad:  String render(PageData page, boolean isSuite) {
          if (isSuite) { return suite(page); } else { return single(page); }
      }
      render(page, true);
good: String renderForSuite(PageData page) { return suite(page); }
      String renderForSingleTest(PageData page) { return single(page); }
      renderForSuite(page);
```

## Limits
A boolean that is stored, forwarded or returned rather than branched on is data, not a selector. A method implementing an interface or overriding a supertype signature cannot drop the parameter and is out of scope. A private helper with one internal caller is a lower-value finding; a public method is the case. A tolerance in the project context ("selector booleans accepted in builders") rejects the finding.

## Validator
On the triggered hunk find each method declaration with a `boolean` parameter and each call passing a boolean literal. Open the file and read the method body: flag when the parameter appears in an `if`, `?:` or `switch` condition that selects between two otherwise separate paths. Validator question: **is this boolean parameter tested inside the method to choose which of two paths runs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-02`, severity minor, `file`, `symbol`, `code` = the declaration and one literal-passing call quoted verbatim from the diff, `fix` = the two named methods, `rationale` naming the unreadable literal at the call site).

## Source
SonarSource `java:S2301` "Public methods should not contain selector arguments" — "A selector argument is a boolean argument that's used to determine which of two paths to take through a method … the maintainers of the code calling the method won't see the parameter name, only its value … Instead, separate methods should be written" (rule text from the `sonar-java` 6.15.1 plugin resources). Error Prone `BooleanParameter` — "Use parameter comments to document ambiguous literals"; a parameter comment on a boolean literal improves readability at the call site.
