---
title: Where braces are optional, a control-statement body that starts on its own line is enclosed in braces
rule_id: CODE-54
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['\b(if|for|while)\s*\(.*\)\s*(//.*)?$', '^\s*(\}\s*)?(else|do)\s*(//.*)?$']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Where braces are optional, a control-statement body that starts on its own line is enclosed in braces

## Thesis
Where the language lets a control statement take one unbraced statement as its body, an if, else, for, while or do body that starts on a line below its header is enclosed in braces, even when it is a single statement.

## Rationale
Without braces, the reader takes the body's extent from the indentation, which gives strong but misleading guidance: when the lines after a control structure are indented as if inside its block, the omitted braces mean those lines are executed unconditionally, once. This arises in maintenance: it is easy to forget to add the braces when inserting a statement into a body that contains a single statement, because the indentation already indicates that the new line belongs to the block. After an if, the inserted line runs whether or not the condition holds; after a loop, it runs once after the loop, not on every iteration. Nesting adds a second trap: an else beneath an unbraced if whose body is another unbraced if binds to the inner if, whatever the indentation says; in a survey of 97 developers, 71.73% perceived this dangling-else form as negative. Braces remove the ambiguity and prepare the body for the next statement added to it. The evidence on comprehension is narrower and mixed. In an experiment with 73 participants who predicted the output of tiny programs of about eight lines, subjects made significantly more mistakes (p < 0.05) on programs whose single-statement if, while or for body omitted the braces than on the equivalent programs with braces; a study in which 36 students traced program segments found no difference between delimiters required around every block and delimiters used only around multi-line blocks (p = 0.955).

## Example
```java
bad:  if (count > limit)
        reset();
      else
        increment();
good: if (count > limit) {
        reset();
      } else {
        increment();
      }
```

## Limits
The rule decides nothing where the grammar requires a block after every control-statement header, or where indentation alone delimits blocks. An else followed by if on the same line continues an if chain and is not an unbraced body; braces around a lambda body or a switch case are outside the rule. Whether a single-statement body may stay unbraced is contested, and the line on which the body starts separates the cases. One side braces every body wherever it sits: a secure-coding recommendation, a style guide, and the default configuration of four static-analysis rules. The other side admits an unbraced single statement on the header's own line and nowhere else: one style guide lets an if statement that fits on one line elide the block while it marks a loop with its body on the header's line as bad, one rule raises no issue for a single return, break or continue on the same line as its if, and two rules offer an option that allows single-line statements without braces and still reports a body that starts on the next line. A body on the header's own line is therefore left to the project's style guide or checker configuration, and the rule does not flag it. A third position omits braces around a single statement, own line included; it appears in an operating-system kernel's coding style and in two non-default options of one checker, which report braces around a single-statement body. Where the project context documents that convention, the finding is rejected. The triggers read added lines one at a time, so a statement added beneath an unbraced body whose header is context is checked only when another added line of the same file matches a trigger.

## Validator
Grep the added lines for an if, else if, for or while header, that ends at its closing parenthesis (a header whose condition wraps is read from the hunk when another added line matches), and for an else or do that ends its line, then read the next line of the hunk that is neither blank nor a comment: that line starts the body. Skip a header whose next line opens a brace, an else followed by if on the same line, and a file whose language requires a block after every header or delimits blocks by indentation. Check, too, an added line placed directly beneath an unbraced body whose header is context, and indented like that body. Read the project context for a documented convention that omits braces around single statements. Validator question: **Does the hunk add a control-statement header whose body starts on a following line without an opening brace, or add a statement directly beneath such a body and indented like it, in a language where that brace is optional and with no documented project convention that omits braces around single statements?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-54`, severity minor, `file`, `symbol`, `code` = the added header line and the unbraced body line beneath it, or, where that header and body are context, the added statement indented beneath the body, quoted verbatim from the diff, `fix` = the same statement with its body enclosed in braces, in the file's language, `rationale` = the unbraced body that starts on its own line and the statement an edit beneath it, indented like it, would run outside the block).
