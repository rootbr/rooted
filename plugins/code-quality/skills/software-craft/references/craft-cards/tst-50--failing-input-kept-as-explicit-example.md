---
title: A failing input that a property found is kept as an explicit example that every later run of the suite executes, and not only in a local failure database or a replay seed
rule_id: TST-50
domain: tests
step: [test, review]
applies_to: [tests]
triggers: ['@example\(|@reproduce_failure\(|@seed\(', '\bexamples\s*:\s*\[', '\bf[.]Add\(', 'testdata/fuzz|proptest-regressions|\bgo test fuzz v1\b|# shrinks to\b', '(?i)\bseed\s*[:=]\s*"?-?\d+|\bRngSeed::Fixed\(']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A failing input that a property found is kept as an explicit example that every later run of the suite executes, and not only in a local failure database or a replay seed

## Thesis
Once a property has found a failure and the bug is fixed, the minimised failing input is saved in the repository as an explicit example that every later run of the suite executes: an example attached to the property, a seed-corpus entry that holds the input value itself, kept in the repository's test data and submitted with the fix, or an ordinary example-based test. A framework's local failure store and a replay seed or replay blob reproduce the failure while it is diagnosed; the explicit example is the permanent record of the test case.

## Rationale
A local failure store may be invalidated by a framework upgrade that changes its internal format, and by an edit to the test function that changes the key its entries are stored under. A replay seed is bound to the framework version that produced it: replaying a seed saved under one version in another is unsupported, and a replay blob is not stable across versions. A persisted seed is also bound to the generator that consumed it: once the generator changes, the seed may or may not reproduce the failing value. Neither is to be relied on for the correctness of the suite. An explicit example runs every time, in addition to or before the generated inputs, and a failing input written to the seed corpus runs by default under the ordinary test command, serving as the regression test once the bug is fixed.

## Example
```python
bad:  @reproduce_failure("6.131.23", b"ACh/+AAAAAAAAA==")
      @given(st.text())
      def test_round_trip(s):
          assert decode(encode(s)) == s
good: @example("\x00")
      @given(st.text())
      def test_round_trip(s):
          assert decode(encode(s)) == s
```

## Limits
In some frameworks an explicit example does not shrink, so a failing one is reported as given; in others it is reduced like a generated input. In some frameworks an explicit example takes the place of a generated input instead of adding to the run, so five custom examples remove five generated values. A replay seed or replay blob added temporarily to replay a failure locally, for instance one found in continuous integration, is correct while the failure is diagnosed; the rule concerns what stays on the test after the fix. Whether the framework's own failure-persistence file is also committed is unsettled: one framework's documentation asks for its regression files to be added to source control alongside the copied unit test, while another keeps its store in a local directory and offers sharing it through a networked or continuous-integration-artifact store; the rule requires the explicit example either way and takes no side on a persistence file that stores seeds; a persistence entry that holds the input value and runs under the ordinary test command is itself the seed-corpus form.

## Validator
Grep the hunk for a replay decorator or blob, a seed setting on a property, an explicit-example decorator or examples list, a seed-corpus addition or a failure-persistence path. Open the test file at base and at head and trace whether the change fixes a failure that a property found, shown by a replay seed or blob, a failure-persistence entry or the fix's description naming the counterexample. When it does, check whether the head carries that input as an explicit example on the property, a seed-corpus entry in the repository's test data, or an example-based test. A replay decorator or blob still on the property at head counts as the seed form, and so does a committed failure-persistence file whose entries store a generator seed rather than the input value; a seed fixed to make the whole run deterministic, with no found failure behind it, is outside the rule. Validator question: **Does the change leave a failure that a property found recorded only in a replay seed, a replay blob or a local failure store, with no explicit example of that input that every run executes?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-50`, severity minor, `file`, `symbol`, `code` = the replay seed, replay blob, seed setting or failure-persistence line quoted verbatim from the diff, or the property's declaration line from the test file when only the change's description names the counterexample, `fix` = the property with the minimised failing input added as an explicit example, or an example-based test of that input, in the file's language, `rationale` = names that a stored seed or local failure store can be invalidated by a framework upgrade or a test edit while an explicit example runs on every run).
