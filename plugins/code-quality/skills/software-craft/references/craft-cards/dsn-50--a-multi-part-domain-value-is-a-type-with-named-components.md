---
title: A domain value made of several related parts is a type with named components, not a positional tuple or pair whose parts the reader tells apart by index
rule_id: DSN-50
domain: design
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['(?:->|:)\s*(?:tuple|Tuple)\[', '\)\s*:\s*\[\s*\w+\s*,|[:=]\s*\[\s*(?:number|string|boolean|bigint)\s*,', '(?:->|:)\s*\(\s*[\w<>&'']+\s*,(?![^()]*\)\s*=>)', '\b(?:Pair|Triple|Tuple\d?|SimpleEntry|ImmutablePair|MutablePair)\s*<', '\)\s*\(\s*(\*?[\w.]+)\s*,\s*\1\s*[,)]', '^\s*return\s+[\[(]?\s*(?!nil\b|err\b)\w+\s*,\s*(?!nil\b|err\b|ok\b|true\b|false\b)\w+\s*[\])]?\s*;?\s*$']
scope: callers
check_kind: semantic
severity_default: minor
---

# A domain value made of several related parts is a type with named components, not a positional tuple or pair whose parts the reader tells apart by index

## Thesis
A value made of several related parts that play different roles — a rectangle's width and height, the fields of a row that a file reader or a database query returns — that is stored, returned or passed on is a struct, record, class or named tuple carrying a name for the whole and a name for each part, so that code reaches each part by its name rather than by its position.

## Rationale
A tuple does not name its elements, so code that uses it indexes into the parts, and the computation is less obvious. The author has to keep in mind which position holds which part — that the width is index 0 and the height index 1 — and someone else who uses the code finds that even harder to figure out and keep in mind. Because the meaning of the data is not conveyed in the code, errors become easier to introduce: mixing up the width and the height does not matter to an area, yet it matters to a rectangle drawn on the screen. A struct adds that meaning by labelling the data, with a name for the whole and names for the parts; the signature of a routine that uses it then says exactly what is meant, conveys that the parts are related, and gives the values descriptive names in place of index numbers, which is a gain in clarity. A named tuple assigns a meaning to each position and adds access by field name to access by position index, so it can be used wherever a plain tuple is used — for instance for the result rows a file reader or a database query returns — and makes the code more readable and self-documenting.

## Example
```java
bad:  Pair<Integer, Integer> bounds(int[] values) { ... }
      Pair<Integer, Integer> range = bounds(values);
      int span = range.getRight() - range.getLeft();
good: record Range(int min, int max) { }
      Range bounds(int[] values) { ... }
      Range range = bounds(values);
      int span = range.max() - range.min();
```

## Limits
A tuple fits an interface that rests heavily on convention, where each element's meaning is obvious, and it leaves each caller free to name the elements as it destructures them; since not every user holds the same view of what is obvious, an object with descriptive property names may still be the better interface. A type that names the whole but leaves its parts unnamed fits where naming each part would be verbose or redundant, as for a colour or a point made of three numbers, and it still keeps a value of one such type from being passed where another made of the same parts is expected. Where a routine returns several results that its signature can name, results whose meaning is clear from context, such as a node and an error, are better left unnamed, since the names would only repeat themselves in the documentation; where two or three results share a type or a result's meaning is not clear from context, names on the results in the signature may be useful in some contexts — a latitude and a longitude named there read more clearly than two unnamed numbers — so the finding accepts such names as its fix, although a caller still binds each result by its position. Grouping a routine's separate parameters into one object is outside this rule. A tolerance the project context states for a tuple or pair type it names rejects the finding.

## Validator
In the hunk, find each tuple, pair or triple type and each fixed-size positional group that an added line declares as a routine's result, a parameter, a field or a variable, each return of several bare values, and each routine signature that lists several unnamed results of one shared type. Read what each position holds, and skip a group whose positions all play the same role, a group whose parts have distinct types and a meaning clear from context such as a value and its error, a type that names the whole where naming each part would be verbose or redundant, and an interface whose positions follow a convention that makes each element's meaning obvious. Open the callers of the changed symbol and read how they reach the parts: by index, through first and second or left and right accessors, or by destructuring into names each caller picks; a caller that binds a part under the wrong name is the defect at work. Validator question: **is a value whose parts play different roles stored, returned or passed on as a tuple, a pair or an unnamed positional group, so that its users must know which position holds which part?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-50`, severity minor, `file`, `symbol`, `code` = the declaration of the tuple, pair or positional group and, where present, a line that reads a part by index or by a positional accessor, quoted verbatim from the diff, `fix` = a struct, record, class or named tuple with a name for the whole and one for each part, or names on the results where the routine's signature can name them, together with the access by name where the fix is a type, in the file's language, `rationale` naming the parts and the position a user has to remember for each).

## Source
- The Rust Programming Language, ch. 5.2 "An Example Program Using Structs", § "Refactoring with Tuples" and § "Refactoring with Structs" (`rust-lang/book`, `src/ch05-02-example-structs.md`) — "Tuples don’t name their elements, so we have to index into the parts of the tuple, making our calculation less obvious."; "Mixing up the width and height wouldn’t matter for the area calculation, but if we want to draw the rectangle on the screen, it would matter! We would have to keep in mind that `width` is the tuple index `0` and `height` is the tuple index `1`. This would be even harder for someone else to figure out and keep in mind if they were to use our code. Because we haven’t conveyed the meaning of our data in our code, it’s now easier to introduce errors."; "We use structs to add meaning by labeling the data. We can transform the tuple we’re using into a struct with a name for the whole as well as names for the parts"; "Our function signature for `area` now says exactly what we mean"; "This conveys that the width and height are related to each other, and it gives descriptive names to the values rather than using the tuple index values of `0` and `1`. This is a win for clarity." (fetched)
- Python documentation, `collections`, § "`namedtuple()` Factory Function for Tuples with Named Fields" (`python/cpython`, `Doc/library/collections.rst`) — "Named tuples assign meaning to each position in a tuple and allow for more readable, self-documenting code. They can be used wherever regular tuples are used, and they add the ability to access fields by name instead of position index."; "Named tuples are especially useful for assigning field names to result tuples returned by the csv or sqlite3 modules" (fetched)
- TypeScript Handbook, "Object Types", § "Tuple Types" (`microsoft/TypeScript-Website`, `packages/documentation/copy/en/handbook-v2/Object Types.md`) — "Tuple types are useful in heavily convention-based APIs, where each element's meaning is "obvious". This gives us flexibility in whatever we want to name our variables when we destructure them."; "since not every user holds the same view of what's obvious, it may be worth reconsidering whether using objects with descriptive property names may be better for your API." (fetched)
- The Rust Programming Language, ch. 5.1, § "Creating Different Types with Tuple Structs" (`src/ch05-01-defining-structs.md`) — "Tuple structs are useful when you want to give the whole tuple a name and make the tuple a different type from other tuples, and when naming each field as in a regular struct would be verbose or redundant."; "a function that takes a parameter of type `Color` cannot take a `Point` as an argument, even though both types are made up of three `i32` values." (fetched)
- Go Code Review Comments, § "Named Result Parameters" (`golang/wiki`, `CodeReviewComments.md`) — `(node *Node, err error)` "will be repetitive in godoc; better to use" `(*Node, error)`; "if a function returns two or three parameters of the same type, or if the meaning of a result isn't clear from context, adding names may be useful in some contexts."; `Location() (float64, float64, error)` "is less clear than" `Location() (lat, long float64, err error)` (fetched)
- Caveat: the sources are official language documentation that state the mechanism; none measures a defect rate, so the severity rests on clarity.
