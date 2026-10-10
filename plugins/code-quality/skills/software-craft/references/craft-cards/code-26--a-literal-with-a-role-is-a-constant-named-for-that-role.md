---
title: A numeric literal that stands for a quantity whose meaning the surrounding code does not state is a constant named for its role, while a literal whose value is its whole meaning stays a literal
rule_id: CODE-26
domain: code
step: [implement, refactor]
applies_to: [universal]
triggers: ['signal:magic_number', '(?<![\w.])(60|24|365|1000|1024|3600|86400|1000000|60000|3600000|86400000|1_000|1_000_000|1e3|1e6|1e9)(?![\w.])']
scope: file
check_kind: mechanical
severity_default: minor
---

# A numeric literal that stands for a quantity whose meaning the surrounding code does not state is a constant named for its role, while a literal whose value is its whole meaning stays a literal

## Thesis
A numeric literal that encodes a quantity with a role apart from its value, such as a quantity of the application domain, a limit or a unit factor, and whose meaning a reader would have to infer from the surrounding context, is defined once as a named constant, and every use of that quantity refers to the constant. The constant is named for its role, for what the value denotes rather than for the value itself, and its definition may be the expression that derives the value from its parts (`24 * 60 * 60` rather than `86400`). A literal with no role apart from its value needs no constant. The small values that linters exempt by default are not magic by themselves: the default lists of five linters name 0 and 1, some also name -1 and one names 2, while a sixth linter exempts no value by default.

## Rationale
An unnamed literal leaves readers to infer its meaning from the context, and to know the global context to understand the number itself. Its use may seem obvious when the code is written, and may not be obvious to another developer, or later once the context has faded. A number that may change can be hard to update when it is not defined as a constant, and numbers that occur several times without an explicit meaning are preferably replaced by named constants, which make their meaning explicit and refactoring easier. Naming a hard-coded value used across the program as a constant conveys its meaning to future maintainers and leaves one place in the code to change if the value needs updating. Writing the definition as the expression that derives the value is easier to understand and verify than writing the computed result. A constant's name is not a derivative of its value, as a constant named twelve holding 12 would be; it explains what the value denotes.

## Example
```go
bad:  if ageSeconds > 86400 {
          return errExpired
      }
good: const maxSessionAgeSeconds = 24 * 60 * 60
      if ageSeconds > maxSessionAgeSeconds {
          return errExpired
      }
```

## Limits
The rule is contested. One position treats every numeric literal that is not defined as a constant as magic, exempting only a few small values, because a hard-coded number requires the reader to know the global context. The other holds that a constant with no role apart from its value is unnecessary, and that a project which frequently deals with constant numbers may not want the check, recommending at least descriptive comments or names for those numbers; three linters ship the check outside their default rule sets, as an optional checker, as a rule not recommended, or in a category described as too opinionated or too prone to false positives. The separating condition is whether the literal has a role apart from its value: it is magic when it encodes a quantity whose meaning the reader must infer from the context, when it occurs several times without an explicit meaning, or when it may change while nothing at that point names its role; it needs no constant when its value is its whole meaning. One constant may define several numeric literals within one expression; those literals are its definition, not magic numbers. One linter ignores routines that compute a hash code, and another offers that exemption as an option that is off by default; one linter excludes test files by default. A project's documented linter configuration that exempts further values, files or routines rejects the finding for what it covers, and so does a documented project decision not to declare its constant numbers, where the literal carries a descriptive comment or name. How a constant's name is cased, non-numeric literals, and a value shared and mutated across components are outside this rule.

## Validator
Grep the hunk for numeric literals in arguments, assignments, case labels, conditions, arithmetic operations and return statements, other than 0 and 1 and any value the project's linter configuration exempts. Open the file and, for each literal, read the statement around it: name the quantity the literal encodes, check whether a constant or a binding named for that role states the role at that point, search the file for the same value standing for the same quantity elsewhere, and look for an existing constant for that quantity that the line bypasses. Drop a literal inside a constant's defining expression, a literal whose value is its whole meaning, a literal the project's documented linter configuration exempts, and, where the project documents that it does not declare its constant numbers, a literal described by a descriptive comment or name. Validator question: **Does an added numeric literal outside a constant's definition encode a domain quantity, a limit or a unit factor whose role no constant or binding named for it states at that point, so that a reader must infer its meaning from context, or write out a quantity the file already defines as a constant?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-26`, severity minor, `file`, `symbol`, `code` = the added line holding the literal, verbatim from the diff, `fix` = a constant named for the literal's role, defined once (as the expression that derives the value where it is built from unit factors), and the line rewritten to use it, in the file's language, `rationale` = the quantity the literal encodes and what a reader at that line cannot tell from the number, or the existing constant the literal bypasses).
