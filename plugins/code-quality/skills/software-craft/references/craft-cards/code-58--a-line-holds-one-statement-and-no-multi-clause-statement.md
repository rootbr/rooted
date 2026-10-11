---
title: A line holds at most one statement, and a statement with more than one clause, such as if-else or try-except, is never written on a single line
rule_id: CODE-58
domain: code
step: [implement]
applies_to: [universal]
triggers: [';\s*((return|break|continue|throw|raise|import|yield)\b|(let\s+|var\s+|const\s+|val\s+|mut\s+|final\s+)*([A-Za-z_][\w.<>\[\]]*\s+)?[A-Za-z_][\w.]*\s*(=(?!=)|:=|\+=|-=|\(|;))', '(;|\{[^{}]*\})\s*(else|catch|finally)\b', '(^\s*|\}\s*)(try|except|finally|else|elif|catch)\b[^:\n{]*(:(?!=)|\{)\s*[^\s#/}]', '^\s*(if|for|while)\b.*[){:]\s*(return|break|continue|throw|raise|[A-Za-z_][\w.]*\s*(=(?!=)|\+=|-=|\())']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A line holds at most one statement, and a statement with more than one clause, such as if-else or try-except, is never written on a single line

## Thesis
Each statement is followed by a line break, so two statements do not share a line. A compound statement with more than one clause, such as an if with an else or a try with its catch, except or finally, is never written on a single line, and none of its clauses keeps its body on the clause header's line; a switch rule or match arm whose single short result, not a non-empty block, follows an arrow on its label's line is not such a clause. A single-clause if, for or while whose one small body statement fits on the header's line is left to the project's style guide: it is a finding only where the project's stated guide or linter configuration rejects that form. A construct the language treats as one statement, such as a tuple or multiple assignment, counts as one statement, and an if-else used as a value inside one statement may share that statement's line when it has a single else clause and is small.

## Rationale
A compound statement consists of one or more clauses, each a header and the body it controls. Several statements on one line are documented as very difficult to read, and as lowering readability and making debugging the code more complex. Multi-clause statements are documented as needing more than one line: a try and its except cannot both fit on the same line, and an if-else standing as a statement on its own must be multi-line.

## Example
```rust
bad:  let total = base + extra; let half = total / 2;
      if valid { store(half); } else { discard(half); }
good: let total = base + extra;
      let half = total / 2;
      if valid {
          store(half);
      } else {
          discard(half);
      }
```

## Limits
The rule is contested for one form, and the number of clauses separates the cases. A multi-clause statement written on one line is rejected by every strict source and by two tolerant guides: one says never to put a small body on the header's line for multi-clause statements, the other never with a try and its except and, for an if, only when there is no else. The single-clause if, for or while whose small body shares the header's line is where the sources part. On the tolerant side, one guide calls it sometimes okay for an if, for or while with a small body, while listing such lines under "rather not"; another lets the result of a test sit on the test's line only if the entire statement fits on one line and the if has no else; a third lets if statements fitting on one line elide the block, while listing a loop with its body on the header's line as wrong. On the strict side, one guide follows each statement with a line break; one checker reports a braced if with one call on a single line as noncompliant; another reports more than one statement on a single line and allows the body of an if with no else on the test's line only through an option that is off by default; another reports a test and its body on one line; and one guide writes a block on a single line only when it holds a single-line expression and no statements. So the project's stated guide or linter configuration decides that form, and without one that rejects it the finding does not stand. A statement with several parts is still one statement: a tuple assignment assigns the elements of a multi-valued operation to a list of variables, and an if-else in expression context, not a standalone statement, sits on one line when it contains a single else clause and is small. A switch rule or match arm whose label is followed by an arrow and a single short result that is not a non-empty block is outside the multi-clause case: one guide lets such a switch rule be written on a single line if it otherwise follows the guide and breaks the line after the opening brace of a non-empty block, while following the colon of each colon-style case label with a line break, and another keeps a match arm's right-hand side on the arm's line without a block. Semicolons that separate a loop header's initializer, condition and continuation, or a conditional header's init statement from its condition, are not statement separators, and by one checker's default neither are the resources declared in one resource-acquiring header. A class whose whole body is an ellipsis placeholder is exempted by two checkers, and a function stub of that form by one.

## Validator
Grep the added lines of the hunk for a semicolon followed on the same line by another statement, for a block opened and closed on one line and followed by else, catch or finally, and for a clause header followed on its own line by its body. For each hit, read the line and name what it holds. Skip the semicolons inside a loop header or after the init statement of an if or switch header, resource declarations inside one resource-acquiring header, a tuple or multiple assignment, a switch rule or match arm whose single short result, not a non-empty block, follows an arrow on its label's line, an if-else used as a value that has a single else clause and is small, and a definition whose body is only an ellipsis placeholder. Flag two statements that follow one another on the line, neither being the body of the other's header, a multi-clause statement written on one line, and any clause of a multi-clause statement whose body sits on its header's line. Flag a single-clause if, for or while whose one body statement shares the header's line only when the project context names a style guide or a linter setting that rejects that form; otherwise skip it. Validator question: **Does an added line hold two statements one after the other, a multi-clause statement or one of its clause bodies on a header's line, or a single-clause body on its header's line that the project's stated guide rejects?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-58`, severity suggestion, `file`, `symbol`, `code` = the added line holding the joined statements or the one-line compound statement, verbatim from the diff, `fix` = the same code with each statement on its own line and each clause's body below its header, in the file's language, `rationale` = which statements or clauses share the line, and that several statements on one line are hard to read and make debugging more complex).

## Source
- Google Java Style Guide §4.3 One statement per line: "Each statement is followed by a line break." (fetched)
- Google Java Style Guide §4.8.4.1 Indentation: "In a new-style switch, a switch rule can be written on a single line if it otherwise follows Google style. (It must not exceed the column limit, and if it contains a non-empty block then there must be a line break after `{`.)"; "In an old-style switch, the colon of each switch label is followed by a line break." (fetched)
- PEP 8, Whitespace in Expressions and Statements › Other Recommendations: "Compound statements (multiple statements on the same line) are generally discouraged"; "While sometimes it's okay to put an if/for/while with a small body on the same line, never do this for multi-clause statements."; `if foo == 'blah': do_blah_thing()` under "Rather not". (fetched)
- Google Python Style Guide §3.14 Statements: "you may put the result of a test on the same line as the test only if the entire statement fits on one line. In particular, you can never do so with `try`/`except` since the `try` and `except` can't both fit on the same line, and you can only do so with an `if` if there is no `else`." (fetched)
- Google TypeScript Style Guide, Control structures › Control flow statements and blocks: "The first statement of a non-empty block must begin on its own line."; "Exception: `if` statements fitting on one line may elide the block."; listed as wrong: `for (let i = 0; i < x; i++) doSomethingWith(i);` (fetched)
- Rust Style Guide, Expressions › Blocks: "A block expression must have a newline after the initial `{` and before the terminal `}`, unless it qualifies to be written as a single line based on another style rule."; "Write a block on a single line if: [...] it contains a single-line expression and no statements"; › Single line `if else`: "Put an `if else` or `if let else` on a single line if it occurs in expression context (i.e., is not a standalone statement), it contains a single `else` clause, and is *small*", with the standalone `if x { 0 } else { 1 }` among the "Examples that must be multi-line". (fetched)
- Rust Style Guide, Expressions › Match: "If the right-hand side of the match arm is kept on the same line, never use a block (unless the block is empty)." (fetched)
- Rust Style Guide, Blank lines: "Separate items and statements by either zero or one blank lines (i.e., one or two newlines)." (fetched)
- Checkstyle `OneStatementPerLine`: "Checks that there is only one statement per line. Rationale: It's very difficult to read multiple statements on one line."; property `treatTryResourcesAsStatement`, "Enable resources processing.", default `false`. (fetched)
- SonarSource RSPEC S122 "Statements should be on separate lines": "Putting multiple statements on a single line lowers the code readability and makes debugging the code more complex."; noncompliant: `if (someCondition) { doSomething(); }` (fetched)
- Pylint C0321 `multiple-statements`: "Used when more than one statement is found on the same line."; option `single-line-if-stmt`, default False: "Allow the body of an if to be on the same line as the test if there is no else."; "Functions stubs and class with ``Ellipsis`` as body are exempted." (fetched)
- Ruff E701: "Checks for compound statements (multiple statements on the same line).", flagged example `if foo == "blah": do_blah_thing()`; E702: "Checks for multiline statements on one line.", flagged example `do_one(); do_two(); do_three()`; "This is used to allow `class C: ...`-style definitions in stubs." (fetched)
- Python Language Reference, Compound statements: "A compound statement consists of one or more 'clauses.' A clause consists of a header and a 'suite.'"; "A suite is a group of statements controlled by a clause." (fetched)
- The Go Programming Language Specification, Assignment statements: "A tuple assignment assigns the individual elements of a multi-valued operation to a list of variables." (fetched)
- The Go Programming Language Specification, If statements: "The expression may be preceded by a simple statement, which executes before the expression is evaluated." (fetched)
- Effective Go, Semicolons: "Idiomatic Go programs have semicolons only in places such as `for` loop clauses, to separate the initializer, condition, and continuation elements. They are also necessary to separate multiple statements on a line, should you write code that way." (fetched)
- Caveat: the evidence is style guides and checker documentation; it states the readability and debugging cost without a measured number.
