---
title: Code whose reason or meaning a reader fluent in the language could not infer from reading it, such as a workaround, a deliberately unusual form or a dense expression, carries a comment that states it
rule_id: CODE-63
domain: code
step: [implement, document]
applies_to: [universal]
triggers: ['\b(re[.](compile|match|search|fullmatch|sub|findall|split)|Regex::new|regexp[.](MustCompile|Compile)|Pattern[.]compile|new RegExp)\s*\(', '\w\s*[&^]\s*[\w(]']
scope: file
check_kind: semantic
severity_default: minor
---

# Code whose reason or meaning a reader fluent in the language could not infer from reading it, such as a workaround, a deliberately unusual form or a dense expression, carries a comment that states it

## Thesis
Where the names in a piece of code do not tell a reader who knows the language well, though not what the author is trying to do, why the code does what it does, a comment states that reason; where a dense construct does not show what it does, the comment states its meaning. Such places include code that relies on a nuance of the language or of the business logic the reader may not be familiar with; code that handles a value a called interface is known to produce in violation of the convention it is expected to follow, such as a thrown value that is not an error object, where the comment identifies where that value originates; an adjustment, such as an offset, whose reason lies outside the statement; code made intricate for performance; a form chosen over the usual one because the code depends on a behaviour the usual form would lose, where the comment says the choice is intentional; an unchecked type or non-null assertion, where the comment says why it is safe; and a regular expression, a bit-level test, a complex algorithm or a complex sequence of mathematical operations that uses type conversions in an unexpected way, where the comment says what it does. The test is whether the author would have to explain the code at its next code review. The first remedy is clearer code, and a comment carries what clarification cannot; code whose names already communicate its rationale needs no such comment.

## Rationale
The reasoning behind a decision is information the code itself cannot contain. Names often communicate a rationale; where they do not, a reader who meets a nuance, an intricate passage or an unexpected sequence of operations has to reverse-engineer the code, and a future maintainer can make a mistake. A reviewer who does not understand a piece of code signals that future readers likely will not either, and an explanation written only in the review tool does not help those readers, while clarified code or a comment in the code does. In a largely uniform codebase, code that stands out by using an unfamiliar pattern is often doing so for a good reason, typically performance, and keeping that property makes clear where readers should focus their attention. A less usual form also sends a signal of its own: where a codebase's convention evaluates a loop's end once before the loop, a loop that re-evaluates it on every pass hints that the loop mutates the container, a fact a comment would confirm. Commentary that only restates what the code does adds clutter and a burden of keeping it up to date, so the comment usually carries why something is done, which the code cannot show, and says what the code does only where a dense construct does not show it.

## Example
```typescript
bad:  if ((size & (size - 1)) === 0) { grow(); }
      const postal = new RegExp("^[0-9]{5}(-[0-9]{4})?$");
      if (typeof err === "string") { report(err); }
good: // True when size is 0 or a power of two.
      if ((size & (size - 1)) === 0) { grow(); }
      // Five digits, optionally followed by a hyphen and four more digits.
      const postal = new RegExp("^[0-9]{5}(-[0-9]{4})?$");
      // The parser library throws plain strings instead of Error objects.
      if (typeof err === "string") { report(err); }
```

## Limits
Obviousness is judged for a reader who knows the language well but not what the author is trying to do: behaviour that is obvious to such a reader needs no comment, and where the reasoning behind an unchecked assertion is obvious in the context of the code, its comment may be left out. A clearer name, a named constant or a self-describing structure that makes the reason or meaning plain satisfies the rule without a comment and is the first remedy; a comment that only explains needlessly complex code is not a remedy, and such code is rewritten more clearly. Where the comment sits is a layout choice: a few lines before a complicated operation, a comment at the end of a non-obvious line, and a comment at the head of the enclosing routine each satisfy the rule, and one documented convention keeps comments inside a routine body to small notes or warnings about something particularly clever or ugly and puts the rest, including why the routine does what it does, at its head. The rule asks for a missing comment on implementation code: the documentation a declaration owes its callers, which expresses the purpose of the code, how it should be used and how it behaves when used, is a different kind of comment and outside it, as are a comment that is present but restates or contradicts its code, a TODO or FIXME marker, and the reason owed for leaving a caught error unhandled.

## Validator
Read the added lines of the hunk and pick out each place a reader who knows the language well, though not what the author is trying to do, would have to ask about: a regular expression; a bit-level test, mask or shift; a complex algorithm or a run of mathematical operations with type conversions; an arithmetic adjustment such as an offset; a form that departs from the usual one in the language or in the surrounding code; an unchecked type or non-null assertion; handling of a value a called interface should not produce. For each, look in the hunk and in the opened file for a comment on the same line, directly above it or at the head of the enclosing routine that states the reason or, for a dense construct, what it does, and for a variable, constant or routine name that already carries it; judge a departure from the usual form against the rest of the file. Set aside a place whose behaviour such a reader sees at once from the code. Validator question: **Does the hunk add code whose reason, or for a dense construct whose meaning, a reader fluent in the language could not infer from the code, with neither a comment nor a name that states it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-63`, severity minor, `file`, `symbol`, `code` = the added line or lines whose reason or meaning a fluent reader cannot infer, quoted verbatim from the diff, `fix` = the same code in the file's language with a comment above or beside it that states the reason, or for a dense construct what it does, taken from the change description or the surrounding code where they give it and otherwise phrased as the question the author must answer, or with a name that carries it, `rationale` = the question a reviewer would have to ask about the code and why its names do not answer it).
