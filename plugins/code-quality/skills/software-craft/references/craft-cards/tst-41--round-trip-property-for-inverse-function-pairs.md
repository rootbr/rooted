---
title: A pair of functions that invert each other, such as encode and decode, serialize and deserialize, or format and parse, is covered by a property that the round trip over generated values returns the original value
rule_id: TST-41
domain: tests
step: [design, test, review]
applies_to: [tests]
triggers: ['(?i)\b(?:(?:en|de)code|(?:de)?seriali[sz]e|(?:un)?marshal|parse|format|dumps|loads|to_?json|from_?json|from_?str|compress|decompress|encrypt|decrypt|escape|unescape)\w*\s*\(']
scope: callers
check_kind: semantic
severity_default: suggestion
---

# A pair of functions that invert each other, such as encode and decode, serialize and deserialize, or format and parse, is covered by a property that the round trip over generated values returns the original value

## Thesis
A pair of functions that are inverses of one another, such as encoding and decoding, serializing and deserializing, or printing and parsing, is covered by a round-trip property: for every generated value, applying one function and then its inverse gives a result that matches the original value. A function that is its own inverse, such as reversal, is covered by applying it twice to each generated value. To check that a parser parses correctly, the property starts from a generated expected value, renders it as input text, and checks that parsing gives that value back. Where a property for a unit is hard to come up with, an inverse pair in it is a recommended place to look.

## Rationale
With generated inputs the expected output of each input cannot be predicted, yet a round trip still has a checkable answer: the final result matches the original input. The property is succinct (call one function, then its inverse, then compare the result with the original input), so an inverse pair is easy to notice and easy to test, and such tests tend to be both powerful and easy to write. In 30 interviews with 31 users of property-based testing at one financial technology firm, round-trip properties came up in 11; they were heard so much more often than the other classical properties that the study calls them out on their own and counts them among the high-leverage properties. To check that a parser parses correctly, generating raw input text would mean reimplementing the parser in the test; starting from the expected value and rendering it avoids that.

## Example
```typescript
bad:  test("encode and decode", () => {
        expect(encode({ id: 1 })).toBe('{"id":1}');
        expect(decode('{"id":1}')).toEqual({ id: 1 });
      });
good: test("decode inverts encode", () => {
        fc.assert(fc.property(itemArb, (item) => {
          expect(decode(encode(item))).toEqual(item);
        }));
      }); // added beside the example test, which stays
```

## Limits
The rule reaches pairs that are inverses of one another over the generated values. A pair whose first function discards information from the generated value, such as rounding or normalising, so that its inverse cannot return that value, is not such a pair, and the evidence here states no property for it. The round-trip property is an addition to the example-based unit tests of the pair, not always a replacement for them.

## Validator
Grep the hunk for an added or changed definition or call whose name belongs to an inverse pair: encode and decode, serialize and deserialize, marshal and unmarshal, format or print and parse, dumps and loads, to-JSON and from-JSON, compress and decompress, encrypt and decrypt, escape and unescape. Open the matched function's callers and confirm that its inverse exists in the code; a parser counts when its tests can render the expected value as input text. Pass over a pair whose first function discards information from the generated value, such as rounding or normalising; a parser that ignores whitespace or other formatting in its input still counts. Open the tests among the callers and trace each test of the pair: look for one that generates values, applies the function and its inverse in sequence, and compares the result with the generated value, or, for a parser, renders a generated expected value and parses it back. Validator question: **Does the change add or modify one function of an inverse pair whose tests contain no property that applies the pair in sequence to generated values and compares the result with the original value?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-41`, severity suggestion, `file`, `symbol`, `code` = the added or changed signature of the encoding, decoding, serializing or parsing function, quoted verbatim from the diff, `fix` = a property test, in the file's language, that generates values, applies the function and its inverse in sequence and asserts that the result equals the generated value, `rationale` = names the inverse pair and states that the round trip checks every generated value without a predicted expected output).

## Source
- Official documentation, tutorial 'Introduction to Hypothesis' (HypothesisWorks/hypothesis, master, hypothesis/docs/tutorial/introduction.rst), section 'When to use Hypothesis and property-based testing': "If you're having trouble coming up with a property in your code to test, we recommend trying the following: Look for round-trip properties: encode/decode, serialize/deserialize, etc. These property-based tests tend to be both powerful and easy to write." and "Property-based testing is a powerful *addition* to unit testing. It is not always a replacement." (fetched)
- 'Property-Based Testing in Practice', ICSE 2024, DOI 10.1145/3597503.3639581, §4.3: "Round-Trip Properties (11/30) are also common in the literature; we heard about them so much more often than the other classical cases that they seem worth calling out on their own. These properties check that a pair of functions are inverses of one another—for example, parsing and pretty-printing or encoding and decoding functions. This situation is easy to notice and easy to test since the properties are incredibly succinct (you call one function, then its inverse, and then check that the final result matches the original input)"; observation OB4: "Other high-leverage properties include round-trip properties that check an inverse relationship between functions" (fetched). Caveat: the 30 interviews (31 participants) were held at one financial technology firm. The paper: "We recruited 31 participants and carried out 30 interviews (one was a joint interview)."
- Official documentation, proptest book 'Getting Started' (proptest-rs/proptest, main, book/src/proptest/getting-started.md), property parses_date_back_to_original: "The final property we want to check is that the dates are actually parsed _correctly_. Now, we can't do this by generating strings — we'd end up just reimplementing the date parser in the test! Instead, we start from the expected output, generate the string, and check that it gets parsed back." (fetched)
- Official documentation, 'Tutorial: Getting started with fuzzing' (golang/website, master, _content/doc/tutorial/fuzz.md), 'Add a fuzz test': "When fuzzing, you can't predict the expected output, since you don't have control over the inputs." and "Reversing a string twice preserves the original value" (fetched)
