---
title: A test of code that slices, truncates or indexes strings includes input with characters that take more than one byte or code unit
rule_id: TOOL-37
domain: tooling
step: [test]
applies_to: [tests]
triggers: ['signal:test_file', '(?i)\b(truncate|slice|substring|substr|abbreviate|ellipsi[sz]e|pad_?(left|right|start|end)|char_?count)\w*\(']
scope: file
check_kind: semantic
severity_default: minor
---

# A test of code that slices, truncates or indexes strings includes input with characters that take more than one byte or code unit

## Thesis
Code that slices, truncates or indexes a string at a computed position is covered by at least one test whose input contains a character stored in more than one unit of the string's encoding (more than one byte in UTF-8, two code units in UTF-16), and a change that adds or modifies such slicing, truncation or index arithmetic adds or keeps that test.

## Rationale
In UTF-8 a character can take more than one byte: each letter of "Hola" takes 1 byte, while the "Ö" of "Ölkanne" takes 2 bytes, so that 7-letter word is 8 bytes long. In UTF-16 a character is encoded as one or two code units, so a length counted in code units need not match the number of characters. It is easy to inadvertently confuse character counts and string indices. Indexing a string's bytes yields bytes, not characters, and the first byte of a two-byte letter is not a valid character on its own; slicing through part of a character's bytes can panic at runtime and crash the program. When every character of the input takes 1 byte, as in "Hola", its byte length equals its letter count, so on that input a character count and a byte index coincide; slicing code therefore warrants some test cases containing wide UTF-8 characters, such as "Ölkanne", whose byte 1 falls inside its first character, so that a slice from byte 1 either panics or yields bytes that are not a valid character.

## Example
```go
bad:  func TestTruncate(t *testing.T) {
          if got := truncate("abcdef", 3); got != "abc" {
              t.Errorf("got %q", got)
          }
      }
good: func TestTruncate(t *testing.T) {
          if got := truncate("Ölkanne", 3); got != "Ölk" {
              t.Errorf("got %q", got)
          }
      }
```

## Limits
An index that comes from a known valid position, such as one obtained by iterating over the character boundaries of the same string, is correct as it stands; the rule reaches positions computed from a count, a length or a constant. In UTF-16 the common characters of scripts such as Latin, Cyrillic and CJK take one code unit each, so a test of code that counts UTF-16 code units needs a character such as an emoji, a mathematical symbol or an obscure Chinese character, and a letter such as "Ö" exercises only UTF-8 byte arithmetic. Which unit the code should count in (bytes, characters or grapheme clusters) is a separate decision; the rule asks only that a test exercise the difference. A string type indexed by code points stores every character in one unit, so the rule reaches code on such strings only where it slices their encoded bytes. A slice that the test code itself takes, to build an input or to check a result, is not code under test, and the rule does not reach it.

## Validator
Grep the hunk for a call to a routine under test whose name contains truncate, slice, substring, substr, abbreviate, ellipsize, pad or char count, and for a slice or index expression on a string with computed bounds. Open the file and collect every string input its tests pass to that routine. Trace, where the routine's body is visible, whether its positions come from a count, a length or a constant rather than from the string's own character boundaries, and whether the string it receives is encoded in UTF-8, whose unit is the byte, or in UTF-16, whose unit is the code unit; where the hunk holds neither such a call nor such an expression, the rule does not apply. Validator question: **Does a test in the file pass input to a routine under test that slices, truncates or indexes UTF-8 or UTF-16 encoded text at a position computed from a count, a length or a constant, while no test in the file passes that routine an input containing a character stored in more than one unit of that encoding?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TOOL-37`, severity minor, `file`, `symbol`, `code` = the test call with its single-unit input, quoted verbatim from the diff, `fix` = the same test case with an input containing a character stored in more than one unit of the string's encoding, such as "Ölkanne" for a UTF-8 string or an emoji for a UTF-16 string, and the result expected for it, in the file's language, `rationale` = names the string's encoding and its unit and the confusion of character counts with string indices that single-unit input leaves undetected).
