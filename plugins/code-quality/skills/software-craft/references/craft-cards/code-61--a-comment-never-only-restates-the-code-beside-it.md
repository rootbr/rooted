---
title: A comment never only restates what the code beside it already tells a reader fluent in the language
rule_id: CODE-61
domain: code
step: [implement, refactor, document]
applies_to: [universal]
triggers: ['^\s*(//+!?|#)\s*[A-Za-z]', '\S\s+(//|#|/\*)\s*[A-Za-z]', '^\s*(/\*+|\*)\s*[A-Za-z]']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A comment never only restates what the code beside it already tells a reader fluent in the language

## Thesis
Each comment tells a reader who knows the language well, though not what the author is trying to do, something the code beside it does not: why the code exists or does what it does, stated at a higher level than its statements, or what a construct does where that behaviour is not obvious to such a reader. A comment that only describes literally what the adjacent statement or block does, such as "Increment x" on x = x + 1, is removed, rewritten to give the reason, or replaced by code that describes itself. Two kinds of comment are not restatements: a comment before a tricky or complicated block that explains it, and a comment that says what a regular expression or a complex algorithm does. The summary of a declaration that the language's documented convention asks for, in a doc comment or in a comment that takes a doc comment's place, is outside the rule even where it repeats the declaration's name. Each comment is judged on its own, by whether it is necessary beside the code it describes.

## Rationale
The reader a comment serves knows the language well, though not what the author is trying to do; to that reader an inline comment that states the obvious is unnecessary and in fact distracting. Extra commentary can obscure the code's purpose rather than clarify it, by adding clutter, restating what the code already says, contradicting the code, or adding the burden of keeping the comments up to date when the code changes; a comment that contradicts the code is worse than no comment. Comments are mostly for information the code itself cannot contain, such as the reasoning behind a decision; where code is intricate or holds a nuance a reader may not be familiar with, commentary that explains it lets future maintainers avoid a mistake and lets readers understand the code without reverse-engineering it. The rule restores that division: code that is not clear enough to explain itself is made simpler, and a comment carries what the code cannot.

## Example
```java
bad:  // Loop over the orders and add up their totals
      for (Order order : orders) { sum += order.total(); }
      width = width + 1; // Add one to the width
      /* Subtract one from the height */
      height = height - 1;
good: // Refunds are booked as negative orders, so this sum is net revenue.
      for (Order order : orders) { sum += order.total(); }
      width = width + 1; // Leave room for the one-pixel right border
      height = height - 1;
```

## Limits
Obviousness is judged for a reader who understands the language well: a nuance such a reader may not be familiar with, such as a closure capturing a loop variable when the closure is many lines away, is not obvious, and a comment on it is not a restatement. A comment at a call site that clarifies the meaning of a nonobvious argument is outside the rule. A doc comment on a declaration documents for a caller the purpose of the code, how it should be used and how it behaves when used; one convention asks that it start with a sentence naming the declared symbol, and another shows its summary as the only part of the text in class and method indexes, so that summary is outside the rule even where it repeats the declaration's name, and so is a comment that a convention asks for in a doc comment's place to say what a routine does. The rule judges a comment that is present and repeats its code: a comment that contradicts the code, commented-out code, a TODO or FIXME marker, a missing comment, the content a doc comment owes its caller and the number of comments in a routine are outside it. A project tolerance stated in the project's context, such as teaching material whose comments narrate each step on purpose, rejects the finding.

## Validator
Grep the added lines for a line comment, a comment trailing code, and a block or doc-comment line. For each match, read the comment together with the statement or block it sits beside in the hunk. Set aside the summary a doc comment on a declaration opens with, a comment the language's documented convention asks for in place of a doc comment to say what a routine does, a comment before a tricky or complicated block that explains it, a comment that says what a regular expression or a complex algorithm does, a comment clarifying a nonobvious argument at a call site, and a comment on behaviour a reader who knows the language well would not see from the code. For each comment that remains, compare its words with the code and decide whether it adds a reason, an intent above the statements, or a meaning the construct does not show. Validator question: **Does an added comment only describe literally what the statement or block beside it does, telling a reader fluent in the language nothing the code does not already say?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-61`, severity suggestion, `file`, `symbol`, `code` = the comment line and the statement or block it restates, verbatim from the diff, `fix` = the code without the comment, or with the comment rewritten to the reason where the hunk or the change description states one, in the file's language, `rationale` = the words of the comment that repeat the code and what a comment there could carry instead).

## Source
- PEP 8, "Comments", "Inline Comments" and "Documentation Strings" (python/peps, `peps/pep-0008.rst`): "Comments that contradict the code are worse than no comments. Always make a priority of keeping the comments up-to-date when the code changes!"; "Inline comments are unnecessary and in fact distracting if they state the obvious.", bad `x = x + 1  # Increment x`, good `# Compensate for border`; "Docstrings are not necessary for non-public methods, but you should have a comment that describes what the method does. This comment should appear after the def line." (fetched)
- Google Python Style Guide §3.8.5 "Block and Inline Comments" (google/styleguide, `pyguide.md`): "Complicated operations get a few lines of comments before the operations commence. Non-obvious ones get comments at the end of the line."; "never describe the code. Assume the person reading the code knows Python (though not what you're trying to do) better than you do." (fetched)
- Google C++ Style Guide, "Implementation Comments" (google/styleguide, `cppguide.html`): "Tricky or complicated code blocks should have comments before them."; "When the meaning of a function argument is nonobvious [...] As a last resort, use comments to clarify argument meanings at the call site."; "Do not state the obvious. In particular, don't literally describe what code does, unless the behavior is nonobvious to a reader who understands C++ well. Instead, provide higher-level comments that describe why the code does what it does, or make the code self-describing." (fetched)
- Google Go Style Guide, "Clarity" → "Why is the code doing what it does?" (google/styleguide, `go/guide.md`): "nuances that a reader may not be familiar with, such as: A nuance in the language, e.g., a closure will be capturing a loop variable, but the closure is many lines away"; "a piece of code may be intricate and difficult to follow [...] it is important that accompanying commentary and documentation explain these aspects so that future maintainers don't make a mistake and so that readers can understand the code without needing to reverse-engineer it"; "some attempts to provide clarity (such as adding extra commentary) can actually obscure the code's purpose by adding clutter, restating what the code already says, contradicting the code, or adding maintenance burden to keep the comments up-to-date." (fetched)
- Google Engineering Practices, "What to look for in a code review" → "Comments" (google/eng-practices, `review/reviewer/looking-for.md`): "Are all of the comments actually necessary? Usually comments are useful when they explain why some code exists, and should not be explaining what some code is doing. If the code isn't clear enough to explain itself, then the code should be made simpler."; "regular expressions and complex algorithms often benefit greatly from comments that explain what they're doing"; "mostly comments are for information that the code itself can't possibly contain, like the reasoning behind a decision"; "comments are different from documentation of classes, modules, or functions, which should instead express the purpose of a piece of code, how it should be used, and how it behaves when used." (fetched)
- Google Java Style Guide §7.2 "The summary fragment" (google/styleguide, `javaguide.html`): "Each Javadoc block begins with a brief summary fragment. This fragment is very important: it is the only part of the text that appears in certain contexts such as class and method indexes." (fetched)
- Go Doc Comments (golang/website, `_content/doc/comment.md`): "Every exported (capitalized) name should have a doc comment."; "As with packages (above) and funcs (below), doc comments for types start with complete sentences naming the declared symbol."; "Funcs": "A function's doc comment should explain what the function returns or, for functions called for side effects, what it does." (fetched)

Caveat: these are official style guides and a code-review guide; they state the practice and its reasons, and none measures the cost of a restating comment.
