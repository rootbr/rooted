---
title: A string literal of five or more characters that recurs three or more times in a file for one purpose is declared once as a named constant
rule_id: DSN-22
domain: design
step: [implement, refactor]
applies_to: [universal]
triggers: ['"(?:[^"\\\n]|\\[^\n]){5,}"', '''(?:[^''\\\n]|\\[^\n]){5,}''', '`[^`\n]{5,}`']
scope: file
check_kind: mechanical
severity_default: minor
---

# A string literal of five or more characters that recurs three or more times in a file for one purpose is declared once as a named constant

## Thesis
When a string literal of five or more characters between its quotes occurs three or more times in one file standing for one value, so that a change to the value would have to be made at each of those occurrences, the value is declared once as a named constant and each of those occurrences refers to that constant. Where the file already declares a constant holding the value, the occurrences refer to that constant rather than to a second one.

## Rationale
A repeated literal makes refactoring complex and error-prone, because any change to it has to be propagated to every occurrence; a constant can be referenced from many places and needs updating in a single place. Naming the value as a constant is also useful in conveying its meaning to future maintainers of the code. Two of the checks present the constant as the usual remedy rather than an invariable one: code duplication makes maintenance more difficult, so it can be better to replace the occurrences with a constant, and code with duplicate literals can usually be improved by declaring the string as a constant field. The numbers are tool defaults. One check, documented in a separate rule for each language it covers, reports a literal from its third occurrence in a file in each of four of its language rules; two of them leave out literals shorter than five characters, the third literals of five or fewer characters and the fourth literals shorter than ten characters. Another check reports a literal of three or more characters that appears four or more times in a file, another reports a non-empty literal from its second occurrence within a single file, and a fourth, enabled through a linter runner, reports a literal of three or more characters from its third occurrence, though by default it leaves out every literal passed as an argument to a function call. Two checks also compare literals with the constants already declared: the multi-language check, in one of its four cited language rules, asks for the already-defined constant in place of any occurrence of a value that a constant of the same file holds, and the other looks for existing constants matching the values by default.

## Example
```java
bad:  void sync(Store a, Store b) {
          a.put("orders.pending", load("orders.pending"));
          b.put("orders.pending", a.get("orders.pending"));
      }
good: private static final String PENDING_KEY = "orders.pending";
      void sync(Store a, Store b) {
          a.put(PENDING_KEY, load(PENDING_KEY));
          b.put(PENDING_KEY, a.get(PENDING_KEY));
      }
```

## Limits
The cost the checks name arises where a change to the value would need to be propagated to all occurrences, so equal strings that stand for different things, where a change to one would not have to reach the others, are not one value: only the occurrences that stand for one value count toward the three. A literal passed to a logging call is outside the rule, since log messages are rarely extracted to constants in practice, and so is a literal passed to the constructor of an error that is thrown or to an error-creating function; such occurrences do not count toward the three. The path of an HTTP route, including the prefix of a route group or a sub-router, is outside the rule: the same path is normally repeated across the registrations of one resource, and moving it into a constant hides the URL structure the code exposes. A literal inside an annotation or a decorator, a literal in an import or export statement, a statement-like directive, a documentation string, and a literal that is one fragment of a string joined from adjacent literals, such as a query assembled from several literals, are outside the rule. Test files are outside it: each of the four cited language rules of the multi-language check gives main code as its scope, and two of them also skip test files in their implementation. Three of the four cited language rules of the multi-language check also leave out a literal made only of letters, digits and underscores, one of them giving that exclusion, with its ten-character floor, as a guard against false positives, while the other checks count such a literal; the rule follows the exclusion, and a bare-word literal is flagged only where the project's configured check counts it. A repeated numeric literal is outside the rule, which covers string literals. A threshold or exclusion pattern configured in the project's check, and a minimum length it sets at five characters or more, replace the defaults for the code that configuration covers, and a tolerance for repeated literals stated in the project context rejects the finding. A literal of user-visible text that the project's message catalog should hold is judged by its own rule.

## Validator
Grep the added lines for string literals of five or more characters between their quotes. For each, open the file and count the occurrences of the same literal value across the whole file, the added ones included. Leave out of the count the occurrences inside an annotation or a decorator, an import or export statement, a statement-like directive or a documentation string, the arguments of a logging call, of the constructor of a thrown error and of an error-creating function, the path of an HTTP route, and a fragment of a string joined from adjacent literals. Skip a test file, a literal made only of letters, digits and underscores unless the project's configured check counts it, and a literal the project's configured exclusions name; where the project configures the check, apply its threshold in place of three occurrences, and a minimum length it sets at five characters or more in place of five characters. When three or more occurrences remain and an added line carries one of them, read what each occurrence stands for, a key, a name, a message, a path or a format, and count only the occurrences that stand for one value, which a change would have to reach at each of them. Look for a constant the file already declares with that value, and note whether the occurrences refer to it. Validator question: **Does an added line carry a string literal of five or more characters that occurs three or more times in the file outside the left-out contexts standing for one value that would change together at each of those occurrences, and no named constant holds the value in their place?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-22`, severity minor, `file`, `symbol`, `code` = the added line carrying the repeated literal, quoted verbatim from the diff, `fix` = one named constant declaration holding the value, or the constant the file already declares for it, with each occurrence that stands for the value rewritten to refer to that constant, in the file's language, `rationale` = the literal, how many times and on which lines it occurs in the file, and what the value stands for).
