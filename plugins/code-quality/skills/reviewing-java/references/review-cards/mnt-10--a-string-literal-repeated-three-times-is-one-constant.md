---
title: A string literal repeated three or more times in a class is one named constant
rule_id: MNT-10
domain: maintainability
triggers: ['"[^"\n]{5,}"', 'static final String \w+ = "']
scope: file
check_kind: mechanical
severity_default: suggestion
---

# A string literal repeated three or more times in a class is one named constant

## Thesis
A string literal of five or more characters that occurs three or more times in one class — a property key, a header name, a format, a message — is declared once as a `static final String` constant (or an enum) and referenced by name, so that a change is made in one place.

## Rationale
A repeated literal is a value with no name and no single owner: renaming it means finding every copy, and one missed copy is a bug that compiles. The constant names the concept, gives the compiler the job of keeping copies equal, and the reader one place to learn what the value means. The analyzers report at three occurrences (SonarSource) or four (PMD), ignoring short literals; SonarSource also ignores annotation arguments, which PMD counts by default.

## Example
```java
bad:  headers.set("X-Request-Id", id);   ...   log.info("missing X-Request-Id");   ...   if (!h.containsKey("X-Request-Id"))
good: private static final String REQUEST_ID_HEADER = "X-Request-Id";
      headers.set(REQUEST_ID_HEADER, id);
```

## Limits
Literals inside annotations, literals shorter than five characters, and format strings that differ by a placeholder are not counted. A literal repeated in test code as an expected value is a lower-value finding. A repetition across classes points to a shared constant or a policy object, but the file-scope check counts one class.

## Validator
On the triggered hunk take each added string literal of five or more characters and open the file to count its occurrences outside annotations. Validator question: **does this literal now occur three or more times in the class without a named constant?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-10`, severity suggestion, `file`, `symbol`, `code` = the added literal and one earlier occurrence quoted verbatim from the diff, `fix` = the constant declaration and its use, `rationale` naming the places a change must reach).

## Source
SonarSource `java:S1192` "String literals should not be duplicated" — "Duplicated string literals make the process of refactoring error-prone, since you must be sure to update all occurrences … constants can be referenced from many places, but only need to be updated in a single place"; default threshold 3, literals under five characters and annotations excluded (rule text from the `sonar-java` 6.15.1 plugin resources). PMD `AvoidDuplicateLiterals` — "Code containing duplicate String literals can usually be improved by declaring the String as a constant field", `maxDuplicateLiterals` default 4, `minimumLength` default 3.
