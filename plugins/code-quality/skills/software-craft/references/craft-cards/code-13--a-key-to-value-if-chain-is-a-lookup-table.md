---
title: An if chain that tests one key against three or more literal constants and only returns an effect-free value in every branch is written as a lookup table
rule_id: CODE-13
domain: code
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['^\s*(\}\s*)?else\s+if\s*\(?\s*[\w.]+\s*={2,3}\s*[\x22\x27\w.-]+', '^\s*elif\s+[\w.]+\s*==\s*[^:]+:', '\belse\s+if\s*\(.*[.]equals(IgnoreCase)?\(']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# An if chain that tests one key against three or more literal constants and only returns an effect-free value in every branch is written as a lookup table

## Thesis
Code that selects a value by comparing one key with literal constants holds the constant-value pairs in a lookup table, read with one lookup whose default entry is the value of the final else, once the selection is a chain of if, else-if and else branches whose tests compare the same variable for equality with three or more distinct literal constants and whose every branch, the final else included, is a single return of a value whose evaluation has no side effect.

## Rationale
Looking information up in a table rather than selecting it with if and case statements is, used in appropriate circumstances, simpler than complicated logic and easier to modify, and it leaves two decisions: what information to store in the table and how to reach an entry efficiently. Three or more consecutive equality tests on one variable that each return a value directly simplify into one dictionary lookup, the final else's value becoming the lookup's default.

## Example
```java
bad:  String label(int code) {
          if (code == 1) return "new";
          else if (code == 2) return "open";
          else if (code == 3) return "closed";
          else return "unknown";
      }
good: static final Map<Integer, String> LABELS = Map.of(1, "new", 2, "open", 3, "closed");
      String label(int code) {
          return LABELS.getOrDefault(code, "unknown");
      }
```

## Limits
A choice among fewer than three constants stays as if-else logic: a switch of fewer than three branches is documented as harder to understand than the if-else it would replace, and the three-branch check reports only once its tests compare three distinct constants. The rule reaches only a chain of single side-effect-free returns whose tests compare one variable for equality with literal constants. A chain with a test on another variable, a comparison other than equality, a comparison with an enumeration member or a named constant, a branch of more than one statement or a returned value whose evaluation has an effect is outside it.

A switch or match over the constants is outside the rule at any size. The documented checks for a large switch report nothing up to thirty cases, and above thirty their positions disagree: one holds that a switch with a large set of cases is usually an attempt to map two sets of data, which a real map structure holds more readably and maintainably; the other holds that a switch whose case clauses are all single-line keeps its readability, so one statement per case satisfies the check.

The project context rejects the finding where it turns off the three-branch check, which its tool classes as highly opinionated or prone to false positives.

## Validator
Grep the hunk's added lines for else-if tests that compare a variable for equality with a constant. Read the whole chain in the hunk; where it runs past the hunk's edges, count only the branches the hunk shows. Collect the distinct literal constants its tests compare for equality with the same variable, and check that every branch, the final else included, is a single return of a value with no side effect. Skip a switch or match, and a chain in a project whose context turns the three-branch check off. Validator question: **Does an added chain of if, else-if and else branches compare one variable for equality with three or more distinct literal constants, with every branch, the final else included, a single side-effect-free return of a value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-13`, severity minor, `file`, `symbol`, `code` = the opening if line and the first two else-if branches of the chain, verbatim from the diff, `fix` = the table declared once from each constant to its value and the chain rewritten as one lookup whose default is the value of the final else, in the file's language, `rationale` = the number of distinct constants, the one variable the tests compare with them, and that a lookup table is simpler than the chain and easier to modify).

## Source
- SWEBOK Guide V3.0 ch. 3 §4.7 "State-Based and Table-Driven Construction Techniques" (V4.0a ch. 4 §4.7 keeps the title): "A table-driven method is a schema that uses tables to look up information rather than using logic statements (such as *if* and *case*). Used in appropriate circumstances, table-driven code is simpler than complicated logic and easier to modify. When using table-driven methods, the programmer addresses two issues: what information to store in the table or tables, and how to efficiently access information in the table." (fetched)
- Ruff SIM116 `if-else-block-instead-of-dict-lookup`, doc comment and rule conditions: "Checks for three or more consecutive if-statements with direct returns"; "These can be simplified by using a dictionary"; `return phrases.get(x, "Goodnight")`; "Each if or elif statement's test must consist of a constant equality check with the same variable."; "Each if or elif statement's body must consist of a single `return`."; "The else must also be a single effect-free return statement"; `let Some(literal_expr) = expr.as_literal_expr() else { return; };`; `if literals.len() < 3 { return; }`; category `Pedantic`: "Rules that are highly opinionated or prone to false positives". (fetched)
- PMD `TooFewBranchesForSwitch` (category performance), `minimumNumberCaseForASwitch` default 3: "Using a switch for only a few cases is ill-advised, since switches are not as easy to understand as if-else statements." (fetched)
- SonarSource RSPEC-1479 '"switch" statements should not have too many "case" clauses' (Java; the Go, PHP and JavaScript rules carry the same rationale, the Kotlin rule the same for `when`): "When switch statements have large sets of case clauses, it is usually an attempt to map two sets of data. A real map structure would be more readable and maintainable, and should be used instead."; check class `SwitchWithTooManyCasesCheck`: `DEFAULT_MAXIMUM_CASES = 30`, reports when `size > maximumCases`. (fetched)
- SonarSource RSPEC-1479 '"switch" statements with many "case" clauses should have only one statement' (C#; the VB.NET rule carries the same text for `Select Case`): "When switch statements have large sets of multi-line case clauses, the code becomes hard to read and maintain."; "When all the case clauses of a switch statement are single-line, the readability of the code is not affected."; analyzer `TooManyLabelsInSwitchBase`: `DefaultValueMaximum = 30`, reports when `GetSectionsCount(switchNode) > Maximum` and `!AllSectionsAreOneLiners(switchNode)`, message "Consider reworking this '{0}' to reduce the number of '{1}' clauses to at most {{0}} or have only one statement per '{1}'." (fetched)
- Caveat: no study measuring table-driven code against conditional chains was found; the three-branch count is the default of one tool rule, written for one language and classed by its tool as pedantic.
