---
title: A catch clause names the specific exceptions it handles, and catch of Exception, RuntimeException or Throwable appears only at a documented last-resort boundary
rule_id: MNT-23
domain: maintainability
triggers: ['catch\s*\(\s*(final\s+)?(Exception|RuntimeException|Throwable|Error)\s+\w+\s*\)', 'catch\s*\([^)]*\b(Exception|RuntimeException|Throwable)\s*\|', 'catch\s*\([^)]*\|\s*(Exception|RuntimeException|Throwable)\b']
scope: file
check_kind: mechanical
severity_default: minor
---

# A catch clause names the specific exceptions it handles, and catch of Exception, RuntimeException or Throwable appears only at a documented last-resort boundary

## Thesis
A `catch` clause lists the exception types the block can handle — `IOException`, `SQLException`, a domain exception, a multi-catch of several — and not `Exception`, `RuntimeException` or `Throwable`; the broad forms are reserved for a boundary that documents itself as last resort (a request or job dispatcher, a thread's top level, a controller-advice fallback), and `Throwable` and `Error` are not caught even there.

## Rationale
`catch (Exception e)` handles every checked exception the block can throw the same way, including ones added to callee signatures later, and every `RuntimeException`, which signals a programming error to be fixed rather than handled; the handler cannot know which situation it is in, so it either discards or reports generically, and the reader cannot see what can actually go wrong. `Throwable` and `Error` also catch `OutOfMemoryError`, `StackOverflowError` and `InternalError`, from which the application should not attempt to recover.

## Example
```java
bad:  try { return parser.parse(input); } catch (Exception e) { throw new InvalidInputException(input, e); }
good: try { return parser.parse(input); }
      catch (ParseException | IOException e) { throw new InvalidInputException(input, e); }
```

## Limits
A top-level dispatcher, a scheduler's task wrapper, a servlet filter or a controller-advice fallback that logs and converts anything unexpected is a boundary; the project context names those classes, or a comment on the clause states the role. A framework callback whose contract requires catching `Exception` (an SPI signature) is out of scope. A multi-catch of specific types is the intended form.

## Validator
On the triggered hunk find each `catch` of `Exception`, `RuntimeException`, `Throwable` or `Error`. Open the file to see whether the enclosing method is a documented boundary and what the `try` body can throw. Validator question: **does this clause catch a generic exception type outside a documented last-resort boundary, or catch `Throwable` or `Error` anywhere?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-23`, severity minor, `file`, `symbol`, `code` = the catch clause quoted verbatim from the diff, `fix` = the specific types the try body throws, `rationale` naming what the broad clause hides).

## Source
PMD `AvoidCatchingGenericException` — "Catching overly broad exception types makes it difficult to understand what can actually go wrong in your code and can hide real problems"; catching `Exception` "means you're handling all possible checked exceptions the same way", `RuntimeException` "represent programming errors … Catching them can hide bugs", `Throwable` "means you're trying to handle both recoverable exceptions and serious errors (like OutOfMemoryError) the same way, which is dangerous". SonarSource `java:S1181` "Throwable and Error should not be caught" — "Catching either Throwable or Error will also catch OutOfMemoryError and InternalError, from which an application should not attempt to recover" (rule text from the `sonar-java` 6.15.1 plugin resources); CWE-396. SEI CERT ERR08-J "Do not catch NullPointerException or any of its ancestors".
