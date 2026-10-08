---
title: An equivalence or model-based property compares the unit with a simpler reference or model rather than a copy of the unit's own logic
rule_id: TST-42
domain: tests
step: [design, test, review]
applies_to: [tests]
triggers: ['(?i)\b(?:oracle|reference|naive|slow|model)_?\w*\s*\(', '\bquick[.]CheckEqual\(', '(?i)\b(?:class|struct|type|interface)\s+\w*Model\b', '(?i)\bassert\w*\W+\w+\(.*\)\s*(?:==|,)\s*\w+\(']
scope: file
check_kind: semantic
severity_default: minor
---

# An equivalence or model-based property compares the unit with a simpler reference or model rather than a copy of the unit's own logic

## Thesis
When a property checks a unit against an oracle, a reference implementation or a model on generated inputs, the counterpart is a simplified representation of the same functionality, such as a slower but clearly correct implementation, a built-in routine or an abstract model, rather than the unit's own code or a carbon copy of it.

## Rationale
An equivalence property calls the unit and its counterpart repeatedly with arbitrary values for each argument and looks for an input on which the two return different results. A differential property compares the system under test to a reference implementation of the same functionality that serves as a specification; it is called model-based especially when the reference is designed to be an abstract model of the original code. In 30 in-depth interviews with experienced users at one financial technology company, differential properties (17/30) were by far the most widely implemented kind of property. The classic oracle tests an optimised implementation against a slower, but clearly correct, one, such as a fast sorting algorithm against the built-in sort. A model's goal is to simplify the system: a model that mimics the system too closely risks errors, and the model is a simplified representation rather than a carbon copy, which would test the code by comparing it to itself.

## Example
```go
bad:  type sortModel struct{}
      func (sortModel) Sort(xs []int) []int { return fastSort(slices.Clone(xs)) } // calls the unit
      reference := sortModel{}.Sort
      assert.Equal(t, fastSort(xs), reference(xs))
      err := quick.CheckEqual(fastSort, reference, nil)
good: reference := func(xs []int) []int { s := slices.Clone(xs); slices.Sort(s); return s }
      err := quick.CheckEqual(fastSort, reference, nil)
```

## Limits
A property can also compare functions none of which is fully trusted, since any difference indicates a bug; running one function on different numbers of threads, or simply multiple times, is such a comparison of a unit with itself. One interviewee found property-based testing challenging in a particular situation in part because a good reference implementation was not available. The model is optional in model-based testing, and a model-based test run without one falls outside this rule. The finder sees the unit's helpers and logic only when the test file holds the unit's definition; elsewhere it flags only a counterpart that calls the unit itself.

## Validator
Grep the hunk for a property that compares two implementations on generated inputs: an equality-checking property runner, an assertion that equates the unit's result with a function named oracle, reference, naive, slow or model, or a type named as a model. Open the file and find the counterpart's definition, and the unit's definition when the file holds it. Trace the counterpart's body: note whether it calls the unit, calls a function of the code under test that the unit's definition also calls, or repeats that definition's statements, and whether it instead reaches the result by a simpler route such as a trusted library routine, a naive algorithm or an abstract state. Skip a comparison that the test presents as differential testing among functions none of which is fully trusted, such as one function run on different numbers of threads or simply multiple times. Skip a counterpart whose only use of the code under test is a comparator, key, equality or constructor function that supplies part of what the property specifies, such as the ordering under which a fast sort is checked against the library sort. Validator question: **Does the counterpart that the property treats as the trusted reference or model call the unit, call a function of the code under test that the unit's definition also calls, or copy the unit's logic?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-42`, severity minor, `file`, `symbol`, `code` = the line that defines or passes the counterpart, quoted verbatim from the diff, `fix` = a counterpart in the file's language that computes the same result by a simpler route, such as a trusted library call, a naive loop or an abstract state, `rationale` = names the unit code the counterpart reuses or copies and states that the property then compares the code with itself).

## Source
- fast-check documentation, 'Model based testing' (dubzzz/fast-check, main, website/docs/advanced/model-based-testing.md), warning 'The model, a simplified version of the system': "Model's goal is to simplify the system, but there is a risk that it may mimic the system too closely, leading to errors. The model should not be a carbon copy of the system but a simplified representation of it. It's crucial to avoid testing the code by comparing it to itself." (fetched); 'Overview': "it is entirely optional. Model-based testing can be performed without it as well." (fetched)
- hypothesis.extra.ghostwriter.equivalent docstring (HypothesisWorks/hypothesis, master, hypothesis/src/hypothesis/extra/ghostwriter.py): "This can be used as a classic 'oracle', such as testing a fast sorting algorithm against the :func:`python:sorted` builtin, or for differential testing where none of the compared functions are fully trusted but any difference indicates a bug (e.g. running a function on different numbers of threads, or simply multiple times)." (fetched); tutorial hypothesis/docs/tutorial/introduction.rst, 'Other examples of properties': "An optimized implementation is equivalent to a slower, but clearly correct, implementation." (fetched)
- 'Property-Based Testing in Practice', ICSE 2024, DOI 10.1145/3597503.3639581, §4.3 'Differential Properties (17/30)': "compares the system under test to a reference implementation of the same functionality that serves as a specification; these are often also called model-based properties ... especially when the reference implementation is designed to be an abstract model of the original code. Differential properties were by far the most widely implemented kind of property." and "a good reference implementation was not available (P1)" (fetched); abstract: "30 in-depth interviews with experienced users of PBT at Jane Street, a financial technology company". Caveat: interview frequencies from one company, with no measured defect rates.
- testing/quick, CheckEqual doc comment (golang/go, master, src/testing/quick/quick.go): "CheckEqual looks for an input on which f and g return different results. It calls f and g repeatedly with arbitrary values for each argument." (fetched)
