---
title: The properties written for a unit together assert every guarantee its contract gives a caller, so a sort's properties check that the result is sorted and is a permutation of the input
rule_id: TST-40
domain: tests
step: [design, test, review]
applies_to: [tests]
triggers: ['(?i)\b(?:is_?sorted|sorted|ordered|permutation)\b', '(?i)\b(?:len|length|size|count)\b.*==', '@given\(|\bfc[.](?:assert|property)\(|\bproptest!|\bf[.]Fuzz\(|\bquick[.]Check(?:Equal)?\(|@Property\b']
scope: file
check_kind: semantic
severity_default: minor
---

# The properties written for a unit together assert every guarantee its contract gives a caller, so a sort's properties check that the result is sorted and is a permutation of the input

## Thesis
For each unit tested with properties, the properties written for it together assert every invariant a caller can expect from it, every postcondition and invariant its contract states, so a sort's properties assert both that the result is sorted in ascending order and that it is a permutation of the input, holding each of its values as many times as the input does.

## Rationale
Property-based tests can specify all the invariants users can expect from a unit, and testing against a weaker specification detects fewer bugs. In experiments testing data-structure implementations, testing against strong specifications of functional properties, written as preconditions, postconditions and invariants, detected twice as many bugs as testing against standard contracts. For a sort, the invariants a user can expect include that the resulting array has the same values as the source array and is sorted in ascending order. Property-based tests can also help to document a unit's behaviour in a high-level way.

## Example
```python
bad:  @given(lists(integers()))
      def test_sort(xs):
          out = sort_list(xs)
          assert len(out) == len(xs) and is_sorted(out)
good: @given(lists(integers()))
      def test_sort(xs):
          out = sort_list(xs)
          assert is_sorted(out)
          assert Counter(out) == Counter(xs)
```

## Limits
The rule reaches only the functional guarantees a caller can expect of the unit's results: a behaviour the contract leaves open needs no property, and a guarantee on running time, memory or thread safety lies outside it. The bug count was measured on data-structure implementations in two languages, with the specifications written as preconditions, postconditions and invariants in the code under test rather than as properties in a test file. The strong specifications cost a reasonable overhead in annotation burden and run-time performance while testing.

## Validator
Grep the hunk for a property declaration, a decorator, annotation, macro or call that runs a predicate over generated inputs. Open the file and collect every property written for the same unit under test. Read the unit's contract as the file shows it, its name and the signature, documentation and stated postconditions where the file defines or quotes the unit, and list each guarantee it gives a caller. For each guarantee, find the property that asserts it. Probe the set with trivially wrong implementations, the identity, a constant result and an empty result: for a sort, the output 3 3 3 3 3 3 for the input 3 1 4 1 5 9 is ordered and as long as the input, so order plus length leaves the values unchecked; the output 1 2 2 for the input 1 1 2 is ordered, as long as the input and holds the same set of values, so a comparison of value sets leaves their counts unchecked. Validator question: **Does the unit's contract give a caller a guarantee about its results that none of the properties written for the unit asserts?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-40`, severity minor, `file`, `symbol`, `code` = the property declarations for the unit quoted verbatim from the diff, `fix` = the added property asserting the unasserted guarantee, in the file's language, `rationale` = names the guarantee no property asserts and a wrong implementation that passes every property).

## Source
- fast-check documentation, 'Why Property-Based Testing?', section 'Document the code' (dubzzz/fast-check main, website/docs/introduction/why-property-based.md) (fetched): "it can help to document the behavior of your code in a high-level way. For example, when testing a sorting algorithm, you can use property-based tests to specify all the invariants that users can expect from the algorithm, such as the resulting array having the same values as the source array and being sorted in ascending order."
- 'What good are strong specifications?', ICSE 2013, DOI 10.1109/ICSE.2013.6606572, abstract as recorded in maxxbw54/Paper-Repository paper_data/conf/icse/2013/conf-icse-2013.json (fetched): "We introduce a methodology that extends Design by Contract to write strong specifications of functional properties in the form of preconditions, postconditions, and invariants. ... In our extensive experiments, testing against strong specifications detects twice as many bugs as standard contracts, with a reasonable overhead in terms of annotation burden and run-time performance while testing."
- Caveat: the experiments tested data-structure implementations written in Eiffel and C# against in-code contracts; property sets in test files were not measured.
