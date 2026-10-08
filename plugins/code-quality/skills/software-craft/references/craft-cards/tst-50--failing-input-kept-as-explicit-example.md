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

## Source
- Hypothesis documentation, tutorial "Replaying failed tests" (HypothesisWorks/hypothesis, hypothesis/docs/tutorial/replaying-failures.rst), sections "Prefer @example over the database for correctness", "Inputs from @example do not shrink", "Replaying test cases with @reproduce_failure", "Sharing failures with the database": "Hypothesis may invalidate it when upgrading (because e.g. the internal format may have changed). Changes to the source code of a test function may also change its database key, invalidating its stored entries. We therefore recommend against relying on the database for the correctness of your tests. If you want to ensure an input is run every time, use @example."; "While the database is useful for quick local iteration"; "By default, this is a DirectoryBasedExampleDatabase in the local .hypothesis directory"; "examples provided using @example do not shrink ... Hypothesis will print `Failing explicit example: ...` instead of shrinking"; "the binary blob is not stable across Hypothesis versions, so you should not leave this decorator on your tests permanently. Use @example with an explicit input instead."; "This can be useful for locally replaying failures found by CI"; "another option is to share the Hypothesis database ... a networked database like RedisExampleDatabase ... GitHubArtifactDatabase will automatically replay any failures found by the connected CI artifact" (fetched)
- QuickCheck (nick8325/quickcheck, src/Test/QuickCheck/Test.hs), `data Args`, field `replay`: "saving a seed from one version of QuickCheck and replaying it in another is not supported. If you want to store a test case permanently you should save the test case itself." (fetched)
- proptest book, "Getting Started" (proptest-rs/proptest, book/src/proptest/getting-started.md): "The first thing we should do is add these to source control. ... The next thing we should do is copy the failing case to a traditional unit test since it has exposed a bug not similar to what we've tested in the past." (fetched)
- proptest book, "Failure Persistence" (proptest-rs/proptest, book/src/proptest/failure-persistence.md): "It is recommended to check these files in to your source control so that other test runners (e.g., collaborators or a CI system) also replay these cases."; "The other option is to store the _seed_ that was used to produce the failing test case. ... If the strategy in use differs from the one used to produce failing case that was persisted, the seed may or may not produce the problematic value, but nonetheless produces a valid value. Due to these advantages, this is the approach Proptest uses." (fetched)
- Go documentation, "Go Fuzzing" (golang/website, _content/doc/security/fuzz/index.md), "Running fuzz tests" > "Failing input": "the fuzzing engine will attempt to minimize the input to the smallest possible and most human readable value which will still produce an error ... The fuzzing engine wrote this failing input to the seed corpus for that fuzz test, and it will now be run by default with `go test`, serving as a regression test once the bug has been fixed ... submit the patch with the new testdata file acting as your regression test."; "Corpus file format": "Each of the lines following are the values that make up the corpus entry, and can be copied directly into Go code if desired." (fetched)
- fast-check documentation, "User definable values" (dubzzz/fast-check, website/docs/configuration/user-definable-values.md), "Run against custom values" and "Shrink custom values": "testing values that have previously caused your code to fail ... They will be executed before the other values generated by the framework ... if you add 5 custom examples, then 5 generated values will be removed from the run."; "User definable examples defined in `examples` will be automatically reduced by fast-check if they fail." (fetched)
- Caveat: the evidence is framework documentation for five frameworks; no cited study measures how often stored seeds or failure stores are lost.
