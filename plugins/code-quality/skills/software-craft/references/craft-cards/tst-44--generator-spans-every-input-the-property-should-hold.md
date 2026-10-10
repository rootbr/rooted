---
title: A property's generator spans every input for which the property should hold and narrows size or variety only after a substantial slowdown is seen, with run time controlled through the case budget instead
rule_id: TST-44
domain: tests
step: [test]
applies_to: [tests]
triggers: ['(?i)\b(?:min|max)(?:_?(?:size|value|length|leaves|depth|keys|codepoint))?\s*[=:]', '\b(?:\w*Range|size_range|StringLength|\w*OfN|StringN|of(?:Max|Min)?(?:Length|Size)|between)\(|@Size\(|[(,]\s*(?:\w+\s+in\s+)?-?\d+\w*\s*[.][.]', '(?i)\balphabet\s*[=:]|\b(?:alpha|numeric)(?:chars|numeric)?\b|char(?:acter)?s?range|[(,]\s*(?:\w+\s+in\s+)?["/]\^?\[']
scope: callers
check_kind: semantic
severity_default: minor
---

# A property's generator spans every input for which the property should hold and narrows size or variety only after a substantial slowdown is seen, with run time controlled through the case budget instead

## Thesis
A property's generator is the most general one for which the property should pass, so that it can in principle produce any edge case of that domain; its size or variety is limited only after a substantial slowdown has been seen without the limit, and run time is managed through the case count or the run phases rather than by weakening the test.

## Rationale
Limiting the size of generated inputs, and especially limiting their variety, can all too easily exclude the bug-triggering values from consideration, and can be the difference between a test that finds the bug and one that fails to do so. Finding bugs slowly is far better than not finding them at all, and the number of cases and the phases a run executes can manage its cost rather than weakening the test. Random testing is input domain testing: the input domain must be known in order to pick random points within it, and the domain of a generator is the set of inputs that should be possible to generate, so the generator is where the test states that domain.

## Example
```java
bad:  @Property
      boolean roundTrips(@ForAll @AlphaChars @StringLength(max = 5) String s) {
          return decode(encode(s)).equals(s);
      }
good: @Property(tries = 500)
      boolean roundTrips(@ForAll String s) {
          return decode(encode(s)).equals(s);
      }
```

## Limits
The most general generator is bounded by the inputs for which the test should pass, and selecting that domain falls to the test's author: values outside the unit's precondition, for which the property is not meant to hold, lie outside it, and a generator that leaves them out still spans its domain. A bound at least as wide as the library's own default for that type, including a size range the library requires as an argument, removes nothing the unbounded form of that generator would produce and is within the rule. Size limits are sometimes necessary for performance; once a substantial slowdown has been seen without one, the limit is within the rule. The rule governs the domain, not the distribution, which is the probability with which each element of the domain is generated. Libraries differ there: some expose a size scale or frequency weights, while others keep the distribution internal, partly because humans tend to overtune distributions for bugs they suspect and not enough for bugs they did not know were possible, and users still ask for that control. The rule takes neither side.

## Validator
Grep the hunk for bounds placed on a property's generated inputs: maximum or minimum sizes, lengths, depths and values, size ranges on collections, range or length annotations on generated parameters, and restricted alphabets or character classes. Open the test file and, for each bound, open the unit under test and read the precondition it documents or the guard it applies to that input; read the comment, test name or settings beside the bound for a recorded slowdown seen without it. Compare each bound with the library's own default for that type, and count as removed only the inputs that the generator without the bound would produce. Trace whether the property's stated relation is still expected to hold for the inputs the bound removes. Validator question: **Does a generator bound in this hunk, narrower than the library's own default for that type, exclude inputs for which the property should hold, with neither a precondition of the unit nor a recorded substantial slowdown behind it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-44`, severity minor, `file`, `symbol`, `code` = the bounded generator or annotated parameter quoted verbatim from the diff, `fix` = the same generator with the bound removed or widened to at least the library's own default for that type, or narrowed only to the unit's precondition and the run's cost set through the property's case count, in the file's language, `rationale` = the inputs the bound excludes and the absence of a precondition or recorded slowdown that would justify excluding them).
