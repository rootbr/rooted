---
title: A switch or match over an enumerated type names every member or has a default branch wherever the compiler accepts a missing member
rule_id: CODE-19
domain: code
step: [implement, handle-errors, review]
applies_to: [universal]
triggers: ['^\s*switch\b', '^\s*match\s+\S.*:\s*$|\bmatch\s+[\w.&*()]+\s*\{', '^\s*case\s+(([\w.]+[.])?[A-Z]\w*|[\x22\x27][\w-]+[\x22\x27])\s*(:|->|,)', '^\s*((export|public|private|protected|pub|declare|const)\s+)*enum\s+\w+|^\s*(export\s+)?type\s+\w+\s*=\s*\|?\s*([\x22\x27][\w-]+[\x22\x27]|[A-Z]\w*)\s*\||\bLiteral\[\s*[\x22\x27]|=\s*iota\b|^\s*class\s+\w+\(\s*(\w+[.])?\w*Enum\s*\)', '^\s+[A-Z][A-Z0-9_]*\s*(=\s*[^=\s]|,|\(|;|$)|^\s*\|\s*([\x22\x27][\w-]+[\x22\x27]|[A-Z]\w*\s*;?\s*$)|^\s+[A-Z]\w*\s*$|^\s+[A-Z]\w*\s*(=\s*([\x22\x27][\w-]*[\x22\x27]|-?\d+))?,\s*$|^\t+(?!(return|break|continue|fallthrough|goto|default)\b)[a-z]\w*\s*$|^(\t+|\s*const\s+)[A-Za-z]\w*\s+[A-Z]\w*\s*=\s*[^=\s]']
scope: callers
check_kind: semantic
severity_default: major
---

# A switch or match over an enumerated type names every member or has a default branch wherever the compiler accepts a missing member

## Thesis
A switch or match whose subject has an enumerated type (an enumeration, a union of literal values, or a defined type with a fixed set of named constants) has a case for every member of that type or has a default branch, wherever the language accepts the construct with a member missing. After a change that adds a member to such a type, every switch and match over the type still meets that condition.

## Rationale
A switch over an enumerated type that misses a member and has no default leaves its intent unclear, since three readings fit it: the missing members are known to be impossible, execution is meant to fall out of the switch and continue below it, or the code has a bug and the missing cases should have been handled. Where the language does not require the construct to be exhaustive, a value that no case matches executes no branch, and execution falls out of the switch. When the enumeration or the union changes, it is easy to forget to update the cases for the new member. A switch that has a case for every member, or a default branch, is exhaustive, and its control flow is easier to follow. The default can make the intent clear: raising an error that names the value says the remaining members are impossible, and a comment that execution falls out says the fall-out is intended. Where a language chose not to raise an error at run time when no case matches, raising one is left to the programmer, explicitly, where that is the behaviour wanted. A default that passes the value to an assertion of unreachability whose parameter has the bottom type, which no value has, is checked statically and at run time: a type checker emits an error when it finds the call reachable, as it is when a member has no case of its own, and at run time the call raises an exception.

## Example
```python
bad:  match state:
          case State.IDLE: return "idle"
          case State.RUNNING: return "running"
good: match state:
          case State.IDLE: return "idle"
          case State.RUNNING: return "running"
          case State.DONE: return "done"
          case _: assert_never(state)
```

## Limits
A construct the compiler rejects when a member is missing is outside the rule: there a missing member stops the build, and a value from a type changed after compilation can raise an error at run time. Where a checker that the project runs on every build reports a switch over an enumerated type that misses a member and has no default, the omission does not pass silently; a project context naming such a checker rejects the finding. Checkers differ on whether a default stands in for a member: some count a switch with a default as exhaustive, while others, in their default setting, still ask for a case for every member, one of them noting that this can be useful to make sure every value added later receives explicit handling, with the default reserved for reporting an error; the rule flags only the construct both settings report, a missing member with no default. A subject whose type is not enumerated, such as an integer or a string, is outside the rule. A default branch with no code follows the rule, since a default label can be required even where it contains no code; what a default does with a value the code believed impossible, and whether a switch that names every member keeps a default as well, are judged by their own rules.

## Validator
Grep the added lines for a switch or match head, a case label naming a constant, the declaration of an enumeration, a union of literal values or a set of named constants, and a line that adds a member to one. For a switch or match head or a case label, open the declaration of the subject's type and decide whether it is enumerated; skip a subject of any other type and skip a construct whose compiler rejects a missing member. List the members of the type, list the members the case labels name, and note whether the construct has a default, wildcard or catch-all case. For an added member or an added enumerated type, search the repository for every switch and match whose subject has that type, and check each one the same way, since a construct the diff does not touch can now miss the new member. Skip a construct that a checker named in the project context already reports. Validator question: **Does a switch or match whose subject has an enumerated type, added or changed in the diff or over a type to which the diff adds a member, leave at least one member without a case and have no default branch, in a construct the compiler accepts with a member missing?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-19`, severity major, `file`, `symbol`, `code` = the switch or match head and its case labels, or the added member line with the switch that misses it, quoted verbatim from the diff where the diff shows them and from the file otherwise, `fix` = the same switch with a case for each missing member, or given a default branch that raises an error naming the value where the missing members cannot occur, or one stating that execution falls out where that is intended, in the file's language, `rationale` = which members of which type have no case and what the code does when one of them reaches the switch).

## Source
- Error Prone `MissingCasesInEnumSwitch` (google/error-prone `docs/bugpattern/MissingCasesInEnumSwitch.md`; the summary and severity WARNING in the `@BugPattern` of `core/src/main/java/com/google/errorprone/bugpatterns/MissingCasesInEnumSwitch.java`) — "Switches on enum types should either handle all values, or have a default case."; "The author's intent isn't clear. There are three possibilities": "`default: throw new AssertionError(color);`", "`default: // fall out`", "The code has a bug, and the missing cases should have been handled."; "If there is no default branch code execution will simply fall out of the switch statement." (fetched)
- PMD `NonExhaustiveSwitch` (pmd-java `category/java/bestpractices.xml`) — "Switch statements should be exhaustive, to make their control flow easier to follow. This can be achieved by adding a `default` case, or, if the switch is on an enum type, by ensuring there is one switch branch for each enum constant."; pattern switches and switch expressions are skipped "since for these the compiler already ensures that all cases are covered" (fetched)
- Google Java Style Guide §4.8.4.3 (google/styleguide `javaguide.html`) — "Google Style requires every switch to be exhaustive, even those where the language itself does not require it. This may require adding a default label, even if it contains no code." (fetched)
- typescript-eslint `switch-exhaustiveness-check` (`docs/rules/switch-exhaustiveness-check.mdx`; defaults in `src/rules/switch-exhaustiveness-check.ts`) — "if the union type or the enum changes, it's easy to forget to modify the cases to account for any new types"; `considerDefaultExhaustiveForUnions`, default false: "Keeping this option disabled can be useful if you want to make sure every value added to the union receives explicit handling, with the `default` case reserved for reporting an error." (fetched)
- nishanths/exhaustive (`passes/exhaustive/doc.go`) — "checks that expression switch statements, in which the type of the switch expression is an enumerated type, are exhaustive"; "by default, including a default case in a switch statement does not automatically make a switch statement exhaustive" (fetched)
- The Go Programming Language Specification §Expression switches (golang/go `doc/go_spec.html`) — "If no case matches and there is a "default" case, its statements are executed." (fetched)
- PEP 634 §The Match Statement — "If no case blocks qualify the match statement is complete"; PEP 622 §Rejected Ideas, Check exhaustiveness at runtime — "it's better to have the programmer explicitly throw an exception if that is the behavior they want." (fetched)
- Python `typing.assert_never` (python/cpython `Doc/library/typing.rst`) — "If a type checker finds that a call to ``assert_never()`` is reachable, it will emit an error."; "For a call to ``assert_never`` to pass type checking, the inferred type of the argument passed in must be the bottom type, :data:`Never`, and nothing else."; the `Never` entry: the bottom type, "a type that has no members"; "At runtime, this throws an exception when called." (fetched)
- TypeScript Handbook, Narrowing §Exhaustiveness checking (microsoft/TypeScript-Website `handbook-v2/Narrowing.md`) — a `default` assigning the value to `never`; "Adding a new member to the `Shape` union, will cause a TypeScript error" (fetched)
- The Rust Programming Language ch. 6.2 §Matches Are Exhaustive (rust-lang/book `src/ch06-02-match.md`) — "Matches in Rust are _exhaustive_: We must exhaust every last possibility in order for the code to be valid." (fetched)
- OpenJDK 21 `java.lang.MatchException` (openjdk/jdk `jdk-21-ga`) — "may be thrown when an exhaustive pattern matching language construct (such as a `switch` expression) encounters a value that does not match any of the specified patterns at run time", as when "an enum class has a different set of enum constants at runtime than it had at compile time" (fetched)
- Caveat: no source measures how often a missing member causes a failure; the rule rests on tool rules, a style guide and official language documentation.
