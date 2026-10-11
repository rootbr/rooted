---
title: A boolean value is tested as it is, never compared with true or false, and a condition is never turned into true or false through an if or a conditional expression
rule_id: CODE-82
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['[=!]==?\s*(?:true|false|True|False)\b|\bis\s+(?:not\s+)?(?:True|False)\b', '\b(?:true|false|True|False)\s*[=!]==?(?!>)', '\?\s*(?:true|false)\s*:\s*(?:true|false)\b|\b(?:True|False)\s+if\b.*\belse\s+(?:True|False)\b|\{\s*(?:return\s+|[\w.]+\s*=\s*)?(?:true|false)\s*;?\s*\}\s*else\s*\{\s*(?:return\s+|[\w.]+\s*=\s*)?(?:true|false)\s*;?\s*\}', '^\s*(?:return\s+|[\w.]+\s*:?=\s*)?(?:true|false|True|False)\s*;?\s*$']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A boolean value is tested as it is, never compared with true or false, and a condition is never turned into true or false through an if or a conditional expression

## Thesis
A condition uses an operand of exactly boolean type as it is, or through one negation, in place of a comparison of that operand with the literal true or false by equality or identity. A routine that returns or assigns the truth of a condition returns or assigns the condition itself, or its negation, in place of an if-else or a conditional expression whose only results are the literals true and false, or of an if without else that returns one of the two literals and is directly followed, in the same block, by a return of the other. Both hold where the operand's type is exactly boolean and its equality operator is not one a library overrides.

## Rationale
Comparing a boolean value with a boolean literal results in the same boolean, or its negation; the value used directly, or through one unary negation, is more concise and clearer. An if-else or a conditional expression whose results are only the two literals, or an early-return guard directly followed in the same block by a return of the other literal, is redundant in the same way: it yields the condition or its negation, and the condition can be returned or assigned directly. Linters in several ecosystems report both forms: one names them over-complicated boolean expressions, on the rationale that complex boolean logic makes code hard to understand and maintain; another classes them as code that does something simple in a complex way, a class it warns on by default.

## Example
```java
bad:  if (isReady == true || false != isDone) { ... }
      boolean empty = size == 0 ? true : false;
      if (isValid()) { return false; }
      return true;
good: if (isReady || isDone) { ... }
      boolean empty = size == 0;
      return !isValid();
```

## Limits
An operand whose type is a union that includes boolean, such as string or boolean, is outside: there a comparison with a boolean literal is not considered unnecessary. An operand that may be null or undefined is outside too: comparisons of such nullable booleans with literals are not checked by default, and the documented replacement for a comparison with false there supplies a default for the missing value rather than a plain negation. An operand whose equality operator a library overrides is outside, because replacing its comparison with the literal by the operand alone may alter runtime behaviour. Two literal branches that are each carefully documented may have some value, though the documentation can be rewritten to match the shorter code. The rule reaches comparisons with a boolean literal and branches whose only results are boolean literals; a comparison between two non-literal boolean expressions is outside it.

## Validator
Grep the hunk for an equality or identity comparison with true or false, for a conditional expression whose two results are true and false, and for a return, an assignment or a branch value that is a bare true or false. At each match, open the hunk and read the operand's declared or inferred type: continue only when it is exactly boolean, neither a union that includes boolean nor a nullable boolean, and its equality operator is the language's own rather than one a library overrides. For a return or a branch value that is a literal, trace the enclosing if: it counts when the branches yield only the literals true and false, or when an if without else returns one literal and the statement directly after that if, in the same block, returns the other; a guard whose if ends a loop body, with the other return after the loop, or one followed first by any other statement, does not count. For an assignment, check that both branches assign one literal each to the same variable. Validator question: **Does the hunk compare an operand of exactly boolean type with a boolean literal, or turn a condition into true or false through an if-else or a conditional expression whose only results are the two literals, or through an early return directly followed in the same block by a return of the other literal?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-82`, severity suggestion, `file`, `symbol`, `code` = the comparison with the boolean literal, or the if-else, conditional expression or guard-and-return with literal results, quoted verbatim from the diff, `fix` = the operand or condition used directly, or through one negation, in the file's language, `rationale` = names that the comparison or the literal branches yield the same boolean as the value itself).

## Source
- PEP 8, § Programming Recommendations (python/peps `peps/pep-0008.rst`): "Don't compare boolean values to True or False using ``==``: # Correct: if greeting: # Wrong: if greeting == True: Worse: # Wrong: if greeting is True:" (fetched)
- typescript-eslint `no-unnecessary-boolean-literal-compare` (`packages/eslint-plugin/docs/rules/no-unnecessary-boolean-literal-compare.mdx`): "Comparing boolean values to boolean literals is unnecessary: those comparisons result in the same booleans. Using the boolean values directly, or via a unary negation (`!value`), is more concise and clearer." / "A comparison is **_not_** considered unnecessary if the type is a union of booleans (`string | boolean`, `SomeObject | boolean`, etc.)." / "Comparisons between nullable boolean variables and boolean literals are **not** checked by default." / correct form for `someUndefinedCondition === false`: "`if (!(someUndefinedCondition ?? true))`" (fetched)
- rust-clippy `BOOL_COMPARISON`, group complexity (`clippy_lints/src/bool_comparison.rs`): "Checks for expressions of the form `x == true`, `x != true` [...] and suggest using the variable directly." (fetched); clippy `README.md` lint groups: "`clippy::complexity` | code that does something simple but in a complex way | **warn**" (fetched)
- rust-clippy `NEEDLESS_BOOL` and `NEEDLESS_BOOL_ASSIGN`, group complexity (`clippy_lints/src/needless_bool.rs`): "Checks for expressions of the form `if c { true } else { false }` (or vice versa) and suggests using the condition directly. This also covers the early-return guard form, where a condition returns a tuple-like based on it." / code comment on that form: "The optional `Ok(..)` wrapper can be any tuple-like constructor (or absent), as long as the guard and the trailing expression use the same one." / code on that form, which takes the guard only as the block's last statement before its trailing expression: "if let Some(tail) = block.expr" [...] "let [.., last_stmt] = block.stmts" / "Why is this bad? Redundant code." / "Sometimes, the two branches are painstakingly documented [...] so they *may* have some value. Even then, the documentation can be rewritten to match the shorter code." / "Checks for expressions of the form `if c { x = true } else { x = false }` (or vice versa) and suggest assigning the variable directly from the condition." (fetched)
- Checkstyle `SimplifyBooleanExpression` (`src/site/xdoc/checks/coding/simplifybooleanexpression.xml`): "it finds code like `if (b == true)`, [...] `boolean a = q > 12 ? true : false`, etc. Rationale: Complex boolean logic makes code hard to understand and maintain." (fetched); `SimplifyBooleanReturn` (`simplifybooleanreturn.xml`): "if (valid()) return false; else return true; could be written as return !valid();" (fetched)
- Ruff `E712` true-false-comparison, Fix safety (`crates/ruff_linter/src/rules/pycodestyle/rules/literal_comparisons.rs`): fix "Replace with `{cond}`"; "This rule's fix is marked as unsafe, as it may alter runtime behavior when used with libraries that override the `==`/`__eq__` or `!=`/`__ne__` operators." (fetched)
- Caveat: the evidence is style-guide and linter documentation; no controlled study measures the comprehension cost of either form.
