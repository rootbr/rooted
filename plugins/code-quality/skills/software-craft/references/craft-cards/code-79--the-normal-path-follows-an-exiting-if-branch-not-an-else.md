---
title: When an if branch handles an error or special case and leaves the routine or iteration, the normal path follows the if at its level rather than inside an else
rule_id: CODE-79
domain: code
step: [implement, handle-errors, refactor]
applies_to: [universal]
triggers: ['\belse\s*[{:]', '^\s*\}?\s*else\b(?!\s+if\b)']
scope: file
check_kind: mechanical
severity_default: minor
---

# When an if branch handles an error or special case and leaves the routine or iteration, the normal path follows the if at its level rather than inside an else

## Thesis
When an if branch handles an error or a special condition and ends by leaving — with a return, a throw or raise, a break or a continue, or a call that never returns, such as a panic or a call that exits the process — the code that runs when the condition is not met follows the if block at the if's own indentation and is not placed in an else. Error and special cases are dealt with first, each ending in its exit, and the normal path of the routine or of the loop body runs down the page at minimal indentation. The rule reaches a plain else that follows a chain of if and else-if branches which all end by leaving.

## Rationale
Handling errors before the rest of the code lets the reader find the normal path quickly: the code reads well if the successful flow of control runs down the page, eliminating error cases as they arise, and a normal path kept at minimal indentation can be scanned visually. A branch that ends in a return, a throw or raise, a break or a continue does not flow into the next statement, so the else after it is unnecessary: it can be removed without changing semantics, and its contents placed after the if block. Kept, the else adds unnecessary indentation and verbosity, and the normal code inside it looks abnormal; removing it reduces nesting and makes the code more readable. Inside a loop the same holds for a special condition handled first by continuing to the next iteration or by breaking out of the loop.

## Example
```typescript
bad:  if (input === undefined) {
        throw new Error("input missing");
      } else {
        const value = parse(input);
        return handle(value);
      }
good: if (input === undefined) { throw new Error("input missing"); }
      const value = parse(input);
      return handle(value);
```

## Limits
The case in dispute is an if-else, or a chain of if and else-if branches closed by an else, whose branches are each a single return of one value, a choice among results. That shape may keep its else: a style guide lists both the if-else form and the guard form of such a routine as correct, one lint for the redundant else names among its known problems, without naming a shape, that some prefer to keep the else for clarity, and another states that it cannot decide whether keeping an else-if makes a deliberately exhaustive decision tree easier for readers to recognize, and says to keep that structure, with its message disabled locally, where it is clearer. Lint rules that report every else after a chain of returning ifs flag this shape too; this rule does not. What separates the cases is what the else holds after the branch that leaves: when the branch handles an error or a special condition and the else holds the continuing normal path of the routine or the iteration, the else goes; when every branch, the else included, is a single return of one value, either form is correct. An else-if after a branch that leaves is outside the check, as it is by default in one lint for this pattern. An if used as a value, such as the initializer of a binding, is outside the check, as it is for the lint that inspects only an if in statement or tail position; there the fix moves the leaving branch above the binding, a change other than dropping the else. A branch that can fall through into the code after the if is outside the rule, as is an if whose else, not its if branch, is the one that leaves; the lint rules for this pattern report an else only after a branch that leaves. The fix moves the else's contents to follow the if and keeps the routine's exits as they were; where those contents use a variable declared in the if's own header, the fix first moves that declaration to its own line before the if, and where the else declares a variable, the move extends that variable's scope to the end of the enclosing block, so the fix is checked against a later declaration of the same name and against a resource released at the end of the else's block before the code that follows. A local suppression of the else-after-exit lint on the reported if, or a project context that disables that lint or keeps the else after an exit as its style, rejects the finding.

## Validator
Grep the added lines for an else: a closing brace followed by else and an opening brace, else alone on its line, else followed by a colon, or else followed by a statement on the same line. Open the file and find the if, or the chain of if and else-if branches, that the else closes; skip an else-if, an if used as a value, such as the initializer of a binding, and an else that belongs to a loop, an exception handler or a pattern-matching binding rather than to an if. Check that every preceding branch of the chain ends by leaving: its last statement is a return, a throw or raise, a break or continue, or a call that never returns, such as a panic or a call that exits the process; a fatal-level logging call counts only where its documentation says it ends the process. Read what the leaving branch handles and what the else holds: the branch deals with an error or a special condition, and the else holds the work the routine or the loop iteration goes on to do. Skip a chain whose every branch, the else included, is a single return of one value, and an if that carries a local suppression of the else-after-exit lint. Validator question: **Does an added else follow an if chain whose every branch handles an error or special condition and ends by leaving, while the else holds the routine's or the iteration's continuing normal path?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-79`, severity minor, `file`, `symbol`, `code` = the if condition, the statement by which its branch leaves and the else line, quoted verbatim from the diff, `fix` = the if with its leaving branch followed by the else's former contents one indentation level out with no else, a declaration in the if's header that those contents use moved to its own line before the if, in the file's language, `rationale` = the error or special condition the branch handles, the statement by which it leaves, and the normal path the else indents).
