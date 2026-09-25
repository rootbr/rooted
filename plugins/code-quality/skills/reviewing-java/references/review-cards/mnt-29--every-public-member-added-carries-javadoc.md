---
title: Every public class and every public or protected member the diff adds carries a Javadoc comment with a summary sentence
rule_id: MNT-29
domain: maintainability
triggers: ['^\s*public (abstract |final |static |sealed )*(class|interface|enum|record)\s+\w+', '^\s*(public|protected) (static |final |abstract |synchronized |default )*[\w<>\[\], ?]+\s+\w+\s*\(', '^\s*(public|protected) \w+\s*\(', '^\s*(public|protected) (static |final )*[\w<>\[\], ?]+\s+\w+\s*(=|;)', '^\s*/\*\*']
scope: file
check_kind: mechanical
severity_default: suggestion
---

# Every public class and every public or protected member the diff adds carries a Javadoc comment with a summary sentence

## Thesis
A public top-level type, and each public or protected member of a visible type — method, constructor, field, record component — that the diff adds has a Javadoc comment beginning with a summary sentence that says what the element is for; excepted are self-explanatory members where nothing beyond the name can be said, and overrides of documented supertype methods.

## Rationale
A public element is read from outside the file — in an IDE tooltip, a generated API page, a call site — where the body is not visible: the summary sentence is the one thing a caller sees before deciding to use it. Thread-safety, units, nullability of a return, and the conditions of a thrown exception are exactly what a signature does not show and what a caller gets wrong without being told. The exception for obvious members exists so that the rule adds information rather than noise.

## Example
```java
bad:  public Duration retryDelay(int attempt) { ... }
good: /**
       * Delay before the given retry attempt, growing exponentially and capped at {@code maxDelay}.
       *
       * @param attempt the 1-based attempt number; must be positive
       * @throws IllegalArgumentException if {@code attempt} is not positive
       */
      public Duration retryDelay(int attempt) { ... }
```

## Limits
`getFoo()` with nothing to say beyond "the foo", a method overriding a documented supertype method, a test class, and a private or package-private member are not flagged. A record component named by a domain term the reader may not know is not "obvious". A documentation policy declared in the project context (internal-only module, generated code) is out of scope.

## Validator
On the triggered hunk take each added public type and public or protected member; open the file to see the lines above it for a `/**` comment with a summary sentence. Apply the two exceptions. Validator question: **is this visible element without a Javadoc summary, and is it neither self-explanatory nor an override?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-29`, severity suggestion, `file`, `symbol`, `code` = the declaration quoted verbatim from the diff, `fix` = the Javadoc with a summary sentence, `rationale` naming what the signature does not tell a caller).

## Source
Google Java Style Guide §7.3 "Where Javadoc is used" — "At the minimum, Javadoc is present for every visible class, member, or record component … A top-level class is visible if it is public; a member is visible if it is public or protected and its containing class is visible"; §7.3.1 exception for self-explanatory members, with the caveat that it does not justify omitting information "a typical reader might need to know"; §7.3.2 exception for overrides. Error Prone `MissingSummary` — "A summary line is required on public/protected Javadocs".
