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
A callback of one line or of a few lines that reads without a comment stays inline: that is the case inline functions are for. The comment that calls for a name is one that says what the callback as a whole does; a comment that explains one statement of a longer body is outside that condition. A project tolerance sets the bound: a project that configures another maximum length for inline functions applies that maximum, and one whose style guide prefers a declared function once an inline function spans multiple lines or runs past 60 to 80 characters applies that tighter bound. A callback that is not a step of a data transformation — a test body, a request or event handler, a function started concurrently or deferred — is outside this rule.


Where the language's inline functions hold a single expression only, a callback that spans more than one line or runs past 80 characters is past its bound, whether or not the project's style guide says so.
## Validator
Grep the added lines for an inline function passed as an argument: an arrow or closure that opens a block or continues at the end of the line, a function literal or function expression after an opening parenthesis or a comma, a lambda with a long or continued body, and an inline function carrying a trailing comment. Keep a hit whose enclosing call is a step of a data transformation — a map, filter, sort, search, fold or for-each operation over a collection, stream, iterator or sequence — and drop a test body, a request or event handler, and a function started concurrently or deferred. For each kept callback, count the lines from the first line of its body to the last, inclusive, and read the comments inside its body, at the end of its opening line and on the line directly above the call. Use a bound the project context states in place of 10 lines. Validator question: **Does an added inline callback in a data-transformation step exceed its bound — more than 10 lines unless the project context states another — or carry a comment that says what the callback as a whole does?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-53`, severity minor, `file`, `symbol`, `code` = the line that opens the inline callback, with its explaining comment when it has one, quoted verbatim from the diff, `fix` = a declared function named for what the callback does, holding its body, and the step passing that function by name, or calling it from a one-line callback where the step cannot take the function itself, with the comment removed, in the file's language, `rationale` = the callback's line count against the bound, or the comment whose essence the name replaces).

## Source
- Checkstyle `LambdaBodyLength` (since 8.37; property `max`, default 10, counted from the first line of the lambda's body to its last) — "if lambda body becomes very long it is hard to understand and to see the flow of the method where the lambda is defined. Therefore, long lambda body should usually be extracted to method." (fetched)
- SonarSource RSPEC-5612 "Lambdas should not have too many lines" (sonar-java `LambdaTooBigCheck`, `DEFAULT_MAX = 10`) — "a very convenient and compact way to inject a behavior without having to create a dedicated class or method. But those lambdas should be used only if the behavior to be injected can be defined in a few lines of code, otherwise the source code can quickly become unreadable." (fetched)
- Google Python Style Guide §2.10 Lambda Functions — "Okay for one-liners."; "Harder to read and debug than local functions. The lack of names means stack traces are more difficult to understand."; "If the code inside the lambda function spans multiple lines or is longer than 60-80 chars, it might be better to define it as a regular nested function." (fetched)
- PEP 8 §Programming Recommendations — "the name of the resulting function object is specifically 'f' instead of the generic '<lambda>'. This is more useful for tracebacks and string representations in general." (fetched)
- Python documentation, Functional Programming HOWTO §Small functions and the lambda expression — "2. Write a comment explaining what the heck that lambda does. 3. Study the comment for a while, and think of a name that captures the essence of the comment. 4. Convert the lambda to a def statement, using that name. 5. Remove the comment." (fetched)
- Google Python Style Guide §2.10 Lambda Functions: "Okay for one-liners."; "Harder to read and debug than local functions. The lack of names means stack traces are more difficult to understand. Expressiveness is limited because the function may only contain an expression."; "If the code inside the lambda function spans multiple lines or is longer than 60-80 chars, it might be better to define it as a regular nested function." (fetched)
- Caveat: the 10-line bound is two checkers' configurable default and the multiple-line or 60-to-80-character bound one style guide's hedged suggestion, not measured thresholds; the documentation offers the comment-to-name recipe as a style preference its readers are "free to disagree" with, and no source measures the cost of a long callback.
