---
title: An expression mixing shift or bitwise operators with arithmetic, or bitwise operators with comparisons, shows its grouping with parentheses
rule_id: CODE-53
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['(<<|>>)\s*[\w.]+(\[[^\]]*\]|\([^()]*\))?\s*[-+*/%]', '[-+*/%]\s*[\w.]+(\[[^\]]*\]|\([^()]*\))?\s*(<<|>>)(?!=)', '[\w)\]]\s*(&\^|[&|^])\s*[\w.]+(\[[^\]]*\]|\([^()]*\))?\s*(==|!=|\s[<>]=?\s|[-+*/%])', '(==|!=|\s[<>]=?\s|[-+*/%])\s*[\w.]+(\[[^\]]*\]|\([^()]*\))?\s*(&\^|[&|^])\s*[\w(]']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# An expression mixing shift or bitwise operators with arithmetic, or bitwise operators with comparisons, shows its grouping with parentheses

## Thesis
Where a shift operator (`<<`, `>>`, `>>>`) meets an arithmetic operator (`+`, `-`, `*`, `/`, `%`), or a bitwise operator (`&`, `|`, `^`, `&^`) meets an arithmetic operator or a comparison (`==`, `!=`, `===`, `!==`, `<`, `<=`, `>`, `>=`), so that the sub-expression built with one is an operand of the other, parentheses enclose that sub-expression, and the grouping is written in the code instead of being left to the operator precedence table.

## Rationale
Precedence tables disagree on several of these pairs, so the same unparenthesized text groups differently from one language to the next. One table places the shifts and bitwise-and at the level of multiplication and bitwise-or and exclusive-or at the level of addition, so there `x<<8 + y<<16` means what its spacing implies, unlike in the other languages, and `1 << 2 + 3` is `(1 << 2) + 3`, which equals 7; the tables that rank the shifts below addition read the same text as `1 << (2 + 3)`, which equals 32. Against a comparison the tables split again: some bind bitwise-and tighter than equality, so `flags & mask == mask` compares the masked bits with `mask`, and others bind equality tighter, so the same text applies bitwise-and to `flags` and to the result of `mask == mask`. Not everyone knows the precedence of these operators by heart, so such expressions may trip a reader reasoning about the code, and it is not reasonable to assume that every reader has the whole precedence table memorized. Static checks flag the unparenthesized mix of a shift or bitwise operator with arithmetic and suggest parentheses that make the precedence explicit; both warn by default. Parentheses that restate the grouping the precedence already gives do not change the expression's semantics, yet they make the precedence explicit, which may be useful for rarely used operators, and a redundant-parentheses check leaves such clarifying parentheses unreported by default. Style guidance concurs: optional grouping parentheses are left out only when author and reviewer agree that there is no reasonable chance of a misreading and that they would not make the code easier to read, precedence alone is no reason to elide them, and tools should not insert or remove them automatically.

## Example
```rust
bad:  let index = base << shift + offset;
      let bytes = bits + 7 >> 3;
      let next = head + 1 & mask;
      let is_set = flags & mask == mask;
good: let index = base << (shift + offset);
      let bytes = (bits + 7) >> 3;
      let next = (head + 1) & mask;
      let is_set = (flags & mask) == mask;
```

## Limits
A shift met only by a comparison (`value << 2 == limit`) is outside the rule: every precedence table this rule rests on binds the shift tighter than the comparison, and the shift-precedence checks flag only arithmetic beside a shift. A mix of shift and bitwise operators with each other, and a condition built only from the logical and/or operators, are outside it as well; a check for the shift-with-bitwise mix exists but is off by default. Spacing does not stand in for the parentheses: style guidance says not to use spaces to indicate precedence, and spacing that shows the grouping under one table, as one language's documentation notes for `x<<8 + y<<16`, does not match the meaning in other languages. Parentheses may be left out where author and reviewer agree that there is no reasonable chance of a misreading and that they would not make the code easier to read; a tolerance in the project context recording that agreement rejects the finding.

## Validator
Grep the added lines for a shift operator beside an arithmetic operator, or a bitwise `&`, `|`, `^` or `&^` beside an arithmetic operator or a comparison, and read the whole expression in the hunk, continuation lines included. Set aside tokens that are not those binary operators: the logical `&&` and `||`, a compound assignment such as `+=`, `<<=` or `&=`, a reference or address-of `&`, the bars of a closure's parameter list or of a type union, the closing brackets of a generic type, and text inside comments and string literals. Set aside a shift met only by a comparison, and a mix of shift and bitwise operators alone. For each remaining pair, find the sub-expression built with one operator that is an operand of the other, and check whether parentheses enclose it; a call's argument list or an index bracket encloses it as well. Read the project context for a recorded tolerance. Validator question: **Does an added expression combine a shift with an arithmetic operator, or a bitwise operator with an arithmetic operator or a comparison, so that the sub-expression built with one is an operand of the other without parentheses around it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-53`, severity minor, `file`, `symbol`, `code` = the added line holding the expression, quoted verbatim from the diff, `fix` = the same expression with parentheses around the sub-expression that the file's language already groups, so behaviour is unchanged, or around the other sub-expression where the surrounding code shows that grouping was meant, in the file's language, `rationale` = the two operators, the grouping the file's language gives them, the other grouping a different precedence table gives the same text, and, where the fix regroups, that the value changes).

## Source
- clippy `precedence`, group complexity, warn by default (rust-lang/rust-clippy, `clippy_lints/src/precedence.rs`; `README.md`): "It catches a mixed usage of arithmetic and bit shifting/combining operators"; "Not everyone knows the precedence of those operators by heart, so expressions like these may trip others trying to reason about the code."; "`1 << 2 + 3` equals 32, while `(1 << 2) + 3` equals 7"; the shift-with-bitwise mix is `precedence_bits`, group restriction, allow by default (fetched)
- Error Prone `OperatorPrecedence`, severity WARNING, enabled by default (google/error-prone, `docs/bugpattern/OperatorPrecedence.md`, `core/src/main/java/com/google/errorprone/bugpatterns/OperatorPrecedence.java`; listed in `ENABLED_WARNINGS` of `core/src/main/java/com/google/errorprone/scanner/BuiltInCheckerSuppliers.java`, whose `defaultChecks()` keeps the `ENABLED_ERRORS` and `ENABLED_WARNINGS` checks): "Use grouping parenthesis to make the operator precedence explicit"; `int z = (x + y) << 2;` instead of `int z = x + y << 2;` (fetched)
- PMD `UselessParentheses`, codestyle, property `ignoreClarifying` default `true` (pmd/pmd, `pmd-java/src/main/resources/category/java/codestyle.xml`, `UselessParenthesesRule.java`): "Parentheses whose removal would not change the relative nesting of operators are unnecessary, because they don't change the semantics of the enclosing expression."; “"Clarifying" parentheses, which separate operators of difference precedence. While unnecessary, they make precedence rules explicit, which may be useful for rarely used operators.” (fetched)
- Google Java Style Guide §4.7 Grouping parentheses: recommended (google/styleguide, `javaguide.html`): "Optional grouping parentheses are omitted only when author and reviewer agree that there is no reasonable chance the code will be misinterpreted without them, nor would they have made the code easier to read. It is not reasonable to assume that every reader has the entire Java operator precedence table memorized." (fetched)
- Rust Style Guide, Expressions, Binary operations (rust-lang/rust, `src/doc/style-guide/src/expressions.md`): "Use parentheses liberally; do not necessarily elide them due to precedence. Tools should not automatically insert or remove parentheses. Do not use spaces to indicate precedence." (fetched)
- The Go Programming Language Specification, Operator precedence (golang/go, `doc/go_spec.html`): "There are five precedence levels for binary operators. Multiplication operators bind strongest, followed by addition operators, comparison operators"; table rows 5 `* / % << >> & &^`, 4 `+ - | ^`, 3 `== != < <= > >=` (fetched)
- Effective Go, Formatting, Parentheses (golang/website, `_content/doc/effective_go.html`): "the operator precedence hierarchy is shorter and clearer, so x<<8 + y<<16 means what the spacing implies, unlike in the other languages." (fetched)
- The Python Language Reference, Operator precedence (python/cpython, `Doc/reference/expressions.rst`): "The following table summarizes the operator precedence in Python, from highest precedence (most binding) to lowest precedence (least binding)."; rows in that order include `+`, `-` · `<<`, `>>` · `&` · `^` · `|` · `<`, `<=`, `>`, `>=`, `!=`, `==` (fetched)
- The Rust Reference, Expression precedence, `r[expr.precedence]` (rust-lang/reference, `src/expressions.md`): "The precedence of Rust operators and expressions is ordered as follows, going from strong to weak."; rows in that order include `+` `-` · `<<` `>>` · `&` · `^` · `|` · `==` `!=` `<` `>` `<=` `>=` (fetched)
- ECMA-262 grammar, Bitwise Shift, Relational, Equality and Binary Bitwise Operators (tc39/ecma262, `spec.html`), productions with parameters elided: "ShiftExpression : ShiftExpression `<<` AdditiveExpression"; "RelationalExpression : RelationalExpression `<` ShiftExpression"; "EqualityExpression : EqualityExpression `==` RelationalExpression"; "EqualityExpression : EqualityExpression `===` RelationalExpression"; "BitwiseANDExpression : BitwiseANDExpression `&` EqualityExpression" (fetched)
- OpenJDK javac operator precedences (openjdk/jdk, `src/jdk.compiler/share/classes/com/sun/tools/javac/tree/TreeInfo.java`): "bitandPrec = 8, eqPrec = 9, ordPrec = 10, shiftPrec = 11, addPrec = 12" (fetched)

Caveat: the lints flag a shift or bitwise operator mixed with arithmetic; the bitwise-with-comparison clause rests on the precedence tables' disagreement and the style guidance alone.
