---
title: A multi-line string is written as a text block, not as a concatenation of line fragments with embedded newlines
rule_id: MNT-41
domain: maintainability
triggers: ['\\n"\s*\+', '\\n"\s*$', '^\s*\+\s*"', '"\s*\+\s*"', '\+\s*"\\n', '"""']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# A multi-line string is written as a text block, not as a concatenation of line fragments with embedded newlines

## Thesis
A string literal that spans several lines of text — SQL, JSON, HTML, a template, a multi-line message — is written as a text block (`"""` … `"""`), where the source shows the text as it is, rather than as `"line\n" + "line\n" + …`; escape sequences and `+` operators do not carry the structure of the text.

## Rationale
In the concatenated form the reader reconstructs the text from fragments, escapes and operators, and each edit risks a missing `\n`, a lost space at a join, or a mismatched quote; a text block shows the content laid out as it will be, strips the common indentation, and needs no escaping of embedded quotes. The concatenation is also folded by the compiler only while every operand is a constant, which a later inserted variable silently breaks.

## Example
```java
bad:  String sql = "SELECT id, name\n"
                 + "FROM users\n"
                 + "WHERE active = true";
good: String sql = """
          SELECT id, name
          FROM users
          WHERE active = true""";
```

## Limits
Code compiled below Java 15 has no text blocks; a JDK version in the project context settles it. A two-fragment concatenation that inserts a variable is a format or a template, not this finding; a text block with `formatted(...)` or a parameter placeholder replaces it when the text is long. A single line split only to satisfy the column limit is not a multi-line string.

## Validator
On the triggered hunk find each string expression built from three or more literal fragments joined by `+` that contain `\n` or that together form structured text. Validator question: **does this expression assemble a multi-line text from concatenated line fragments?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-41`, severity suggestion, `file`, `symbol`, `code` = the concatenation quoted verbatim from the diff, `fix` = the text block, `rationale` naming the join errors the fragments invite).

## Source
SonarSource `java:S6126` "Text blocks should be used" — "The most common pattern for multiline strings in Java < 15 was to write String concatenation. Now it's possible to do it in a more natural way using Text Blocks", with the `"<html>\n" + " <body>\n" …` versus `"""` example (rule text from the `sonar-java` 6.15.1 plugin resources). JEP 378 "Text Blocks" — a text block makes it easy to express strings that span several lines of source code while avoiding escape sequences in common cases.
