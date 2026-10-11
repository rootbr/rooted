---
title: A switch case that holds statements leaves the switch or marks its passage into the next case explicitly
rule_id: CODE-75
domain: code
step: [implement]
applies_to: [universal]
triggers: ['^\s*case\b[^:]*:\s*(//.*|/\*.*)?$', '^\s*case\b[^:]*:\s*\S', '^\s*default\s*:']
scope: file
check_kind: mechanical
severity_default: major
---

# A switch case that holds statements leaves the switch or marks its passage into the next case explicitly

## Thesis
Control passes from a case that holds statements into the next case's statements only through an explicitly marked passage. In a multi-way branch whose cases fall through by default, each case that holds statements and has another case after it either ends every path through its statements in a statement after which control cannot reach the next case — break, return, throw, continue, a yield that gives a switch expression its value, or a loop that never ends — or ends with a comment stating that control will or might fall through, such as `fall through` or `falls through`, worded and placed as the project's linter recognizes it where one runs, at the end of the case before the next case label. Where the language has an explicit fall-through statement, that statement marks the passage, and in a branch that ends each case by default it is the only mark. Case labels stacked over one shared body, with no statements between them, need no mark, and the last case needs neither an exit nor a mark.

## Rationale
Where cases fall through by default, a case whose statements end without leaving it runs on into the next case's statements, into the default case too, whether or not that case's value matches. That ability is part of what makes the switch one of the more error-prone constructs, and such a switch may have no syntax to indicate that a passage is intentional. A comment marking the passage leaves no confusion about the expected behaviour: it is then clear that the case is meant to fall through. Accidentally leaving out a break is a fairly common bug, and a deliberate fall-through can be a maintenance hazard and should be rare and explicit. Linters flag every passage not marked by a fall-through comment and accept stacked empty labels and the last case, which has nothing to fall into; one compiler option requires every non-empty case to end in break, return or throw, so that a fall-through bug is not shipped by accident. Where a branch ends each case by default, control flows from the end of a clause to the end of the branch unless an explicit fall-through statement transfers it to the first statement of the next clause, so every passage there is marked by construction.

## Example
```typescript
bad:  switch (level) {
        case "notice":
        case "warn": log.warn(msg);
        default: log.error(msg);
      }
good: switch (level) {
        case "notice":
        case "warn": log.warn(msg); break;
        default: log.error(msg);
      }
```

## Limits
A multi-way branch that never falls through by default — a switch whose clauses end at their last statement, an arrow-form switch, a pattern match that runs only the first matching arm — meets the rule by construction. Where the project's compiler configuration requires every non-empty case to end in break, return or throw, a fall-through comment does not satisfy it, and the case ends in an exit. A linter configured with its own fall-through comment wording sets the wording that marks the passage in that project. A project that states it does not enforce an exit or a comment at the end of each case, and turns its fall-through check off, rejects the finding. Whether the switch has a default case or covers every value, and what each case computes, are outside the rule.

## Validator
Grep the added lines for a case or default label. Open the file and find the multi-way branch around each hit. Skip a branch that never falls through by default: an arrow-form switch, a pattern match that runs only the first matching arm, a switch whose clauses end at their last statement. In a branch whose cases fall through by default, examine every case that holds an added line and the case just before each added label, since a label added after the former last case gives that case a successor. For each examined case that holds statements and has another case after it, trace every path through its statements: the case passes when each path ends in break, return, throw, continue, a yield that gives a switch expression its value (a generator's yield resumes inside the case and does not end it) or a loop that never ends, or when a comment at the end of the case, before the next label, states that control will or might fall through, worded and placed as the project's linter recognizes it where one runs; where the project's compiler configuration requires every non-empty case to end in an exit, a comment does not pass the case. Skip a case that ends in the language's explicit fall-through statement, labels stacked with no statements between them, the last case, and a project that states it turns its fall-through check off. Validator question: **Can control reach the end of a case's statements and run on into the next case's statements with no explicit fall-through statement, and no fall-through comment the project's checks accept, marking that passage?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-75`, severity major, `file`, `symbol`, `code` = the added line that opens or ends the unmarked passage — the case's last statement or the label after it — quoted verbatim from the diff, `fix` = the case ending in break, return or throw, or, where the passage is intended, a fall-through comment at the end of the case or the language's fall-through statement, in the file's language, `rationale` = which case runs on into which next case and what the next case's statements then do with a value they were not written for).

## Source
- ESLint `no-fallthrough`, in `eslint:recommended` (eslint/eslint, `docs/src/rules/no-fallthrough.md`): "The `switch` statement in JavaScript is one of the more error-prone constructs of the language thanks in part to the ability to "fall through" from one `case` to the next."; "what if the fallthrough is intentional, there is no way to indicate that in the language"; "there is no confusion as to the expected behavior. It is clear that the first case is meant to fall through to the second case."; "it flags any fallthrough scenarios that are not marked by a comment"; among its correct examples a `case 1: {` block whose last line inside the braces is `// falls through`, before `case 2:`; a case whose `if`/`else` branches end in `throw`, `break` and `return` "cannot fallthrough"; stacked `case 1: case 2:` labels in its correct examples; "the last `case` statement in these examples does not cause a warning because there is nothing to fall through into"; `commentPattern` changes "the test for intentional fallthrough comment"; When Not To Use It: "If you don't want to enforce that each `case` statement should end with a `throw`, `return`, `break`, or comment, then you can safely turn this rule off." (fetched)
- C++ Core Guidelines ES.78 (isocpp/CppCoreGuidelines, `CppCoreGuidelines.md`): "Accidentally leaving out a `break` is a fairly common bug. A deliberate fallthrough can be a maintenance hazard and should be rare and explicit."; "Multiple case labels of a single statement is OK"; Exceptions: "In rare cases if fallthrough is deemed appropriate, be explicit and use the `[[fallthrough]]` annotation" (fetched)
- Google Java Style Guide §4.8.4.2 (google/styleguide, `javaguide.html`): "each statement group either terminates abruptly (with a `break`, `continue`, `return` or thrown exception), or is marked with a comment to indicate that execution will or *might* continue into the next statement group."; "This special comment is not required in the last statement group of the switch block."; "Notice that no comment is needed after `case 1:`, only at the end of the statement group."; "There is no fall-through in new-style switches." (fetched)
- Error Prone `FallThrough` (google/error-prone, `docs/bugpattern/FallThrough.md`): "each statement group either terminates abruptly (with a `break`, `continue`, `return` or `throw` statement), or is marked with a comment" (fetched)
- Checkstyle `FallThrough` (checkstyle/checkstyle, `src/site/xdoc/checks/coding/fallthrough.xml`): "Finds locations where a `case` contains Java code but lacks a `break`, `return`, `yield`, `throw` or `continue` statement."; `reliefPattern`, "the RegExp to match the relief comment that suppresses the warning about a fall through", default `falls?[ -]?thr(u|ough)`, the comment "must be on the last non-empty line before the `case` triggering the warning or on the same line before the `case`"; "A `case` whose code ends in an infinite loop is not flagged" (fetched)
- PMD `ImplicitSwitchFallThrough` (pmd/pmd, `pmd-java/src/main/resources/category/java/errorprone.xml`): "Empty cases are ignored as these indicate an intentional fall-through." (fetched)
- TSConfig reference `noFallthroughCasesInSwitch` (microsoft/TypeScript-Website, `packages/tsconfig-reference/copy/en/options/noFallthroughCasesInSwitch.md`): "Ensures that any non-empty case inside a switch statement includes either `break`, `return`, or `throw`. This means you won't accidentally ship a case fallthrough bug." (fetched)
- MDN `switch` § Breaking and fall-through (mdn/content, `files/en-us/web/javascript/reference/statements/switch/index.md`): "If `break` is omitted, execution will proceed to the next `case` clause, even to the `default` clause, regardless of whether the value of that clause's expression matches." (fetched)
- The Go Programming Language Specification § Expression switches (golang/go, `doc/go_spec.html`): "the last non-empty statement may be a (possibly labeled) "fallthrough" statement to indicate that control should flow from the end of this clause to the first statement of the next clause. Otherwise control flows to the end of the "switch" statement." (fetched)
- Python tutorial § match Statements (python/cpython, `Doc/tutorial/controlflow.rst`): "Only the first pattern that matches gets executed"; The Rust Programming Language §6.2 (rust-lang/book, `src/ch06-02-match.md`): "Because the first arm matched, no other arms are compared." (fetched)
- Caveat: no source measures how often an omitted break causes a defect; "a fairly common bug" is one guideline's statement, written for a switch that falls through by default, and the rest rests on style guides, tool rules and language documentation.
