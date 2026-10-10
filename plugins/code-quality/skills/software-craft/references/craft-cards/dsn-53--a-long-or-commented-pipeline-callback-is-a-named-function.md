---
title: A pipeline callback longer than 10 lines or explained by a comment is a named function, not an inline lambda
rule_id: DSN-53
domain: design
step: [implement, refactor]
applies_to: [functional]
triggers: ['(=>|->)\s*\{?\s*$', '\|[^|]*\|\s*\{\s*$', '[(,]\s*func\s*\(', '[(,]\s*function\b', '(\blambda\b[^:]*:|=>|->)\s*([^\s{].{60,}|.*[(\[]\s*$)', '(\blambda\b[^:]*:|=>|->|\|[^|\s][^|]*\|).*(\s#|//)\s*\S']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# A pipeline callback longer than 10 lines or explained by a comment is a named function, not an inline lambda

## Thesis
An inline callback that is a step of a data transformation — the function a map, filter, sort, search, fold or for-each operation applies to its elements — holds behaviour that fits in a few lines and reads without a comment. A callback that spans more than 10 lines, counted from the first line of its body to the last, or that carries a comment saying what it does, usually moves out into a declared function — nested, local, a method or top-level — whose name states what the callback does, taken from the essence of that comment where there is one; the step then passes the function by name, or calls it from a one-line callback where the step cannot take the function itself, as when the step's parameter type differs or a method would lose its receiver, and the comment goes.

## Rationale
A long inline callback is hard to understand, and it hides the flow of the routine in which it is defined. An inline function is a convenient, compact way to inject behaviour without declaring a dedicated routine, meant for behaviour that can be defined in a few lines; past that, the source code can quickly become unreadable. An inline function also has no name of its own, which makes it harder to read and debug than a local function: stack traces and string representations show a generic label for it, where a declared function shows its name. A comment written to say what a callback does already holds the missing name: a name that captures the essence of the comment becomes the declared function's name, and the comment is then removed. Two checkers flag an inline function body of more than 10 lines by default, a bound each lets a project configure, and one of them states that a long body should usually be extracted to a method; a style guide suggests that a declared nested function might be better already once an inline function spans multiple lines or is longer than 60 to 80 characters.

## Example
```go
bad:  func firstStale(users []User) int {
          return slices.IndexFunc(users, func(u User) bool {
              // stale: closed, or unverified past the grace period
              return u.Closed || (!u.Verified && time.Since(u.Created) > grace)
          })
      }
good: func isStale(u User) bool { return u.Closed || (!u.Verified && time.Since(u.Created) > grace) }
      func firstStale(users []User) int { return slices.IndexFunc(users, isStale) }
```

## Limits
A callback of one line or of a few lines that reads without a comment stays inline: that is the case inline functions are for; where the language's inline functions hold a single expression only, a callback that runs past one line is judged by its own rule, and this few-lines case does not reach it. The comment that calls for a name is one that says what the callback as a whole does; a comment that explains one statement of a longer body is outside that condition. A project tolerance sets the bound: a project that configures another maximum length for inline functions applies that maximum, and one whose style guide prefers a declared function once an inline function spans multiple lines or runs past 60 to 80 characters applies that tighter bound. A callback that is not a step of a data transformation — a test body, a request or event handler, a function started concurrently or deferred — is outside this rule.

## Validator
Grep the added lines for an inline function passed as an argument: an arrow or closure that opens a block or continues at the end of the line, a function literal or function expression after an opening parenthesis or a comma, a lambda with a long or continued body, and an inline function carrying a trailing comment. Keep a hit whose enclosing call is a step of a data transformation — a map, filter, sort, search, fold or for-each operation over a collection, stream, iterator or sequence — and drop a test body, a request or event handler, and a function started concurrently or deferred. For each kept callback, count the lines from the first line of its body to the last, inclusive, and read the comments inside its body, at the end of its opening line and on the line directly above the call. Use a bound the project context states in place of 10 lines. Validator question: **Does an added inline callback in a data-transformation step exceed its bound — more than 10 lines unless the project context states another — or carry a comment that says what the callback as a whole does?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-53`, severity minor, `file`, `symbol`, `code` = the line that opens the inline callback, with its explaining comment when it has one, quoted verbatim from the diff, `fix` = a declared function named for what the callback does, holding its body, and the step passing that function by name, or calling it from a one-line callback where the step cannot take the function itself, with the comment removed, in the file's language, `rationale` = the callback's line count against the bound, or the comment whose essence the name replaces).
