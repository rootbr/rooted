---
title: A property that discards generated cases through a precondition labels or counts the cases it accepts, so that a run testing mostly trivial inputs is visible
rule_id: TST-47
domain: tests
step: [test]
applies_to: [tests]
triggers: ['\bassume\w*\(|\bAssume[.]that\(|\bfc[.]pre\(|\bprop_assume!|\s==>\s|[.]Skip(?:Now|f)?\(']
scope: hunk
check_kind: semantic
severity_default: suggestion
---

# A property that discards generated cases through a precondition labels or counts the cases it accepts, so that a run testing mostly trivial inputs is visible

## Thesis
A property that discards generated cases through a precondition records a classification of the cases it accepts, as labels, events, statistics or counters that the run reports, so that the share of non-trivial inputs among the passing cases can be read after the run; a class of input the property relies on can additionally carry a coverage requirement, which states the proportion of passing cases that class must reach.

## Rationale
A precondition discards every generated case for which it is false, and used carelessly it can severely skew the distribution of the cases that are actually tested. In a documented example, a property over lists guarded by a sortedness precondition reports success after 100 passing tests with 135 discarded, while only 26% of the passing cases are non-trivial lists of more than one element, against a required 50%. The classification is what reports that share: classifying the same kind of property makes the run print "22% non-trivial" beside its 100 passing tests. Discarded cases do not count toward a coverage requirement, which is measured over the passing cases only. A plain coverage requirement prints a warning when it is missed and leaves the property passing; a statistically checked requirement runs as many tests as needed to decide and fails the property when the requirement is not met. In one framework, recorded events appear in the run's statistics output as percentages beside the counts of passing and invalid cases. In 30 interviews with 31 experienced practitioners, 11 participants, more than a third, said they did not think as hard as they should about testing effectiveness or about whether their generators had adequately tested their software, and the study recommends that tools always announce the count of discarded cases so that the developer can catch problems early. In a self-guided online study with 40 participants who ranked three input distributions by bug-finding power, participants made significantly fewer incorrect comparisons in three of four tasks when using an ensemble of visualisations of the tested inputs, including charts of features extracted from them, than when using a statistics output with a list of example inputs.

## Example
```go
bad:  rapid.Check(t, func(r *rapid.T) {
          xs := rapid.SliceOf(rapid.Int()).Draw(r, "xs")
          if slices.Contains(xs, 0) { r.Skip() }
          checkSort(r, xs) })
good: seen := map[bool]int{}
      rapid.Check(t, func(r *rapid.T) {
          xs := rapid.SliceOf(rapid.Int()).Draw(r, "xs")
          if slices.Contains(xs, 0) { r.Skip() }
          seen[len(xs) > 1]++; checkSort(r, xs) })
      t.Logf("accepted: %d non-trivial, %d trivial", seen[true], seen[false])
```

## Limits
The documentation phrases this as advice, to consider a coverage requirement to make sure the test data is still of good quality, so a finding is a suggestion. A proportion missed on one run may be bad luck, since coverage varies randomly, and a plain requirement only warns because it is not tested in a statistically sound way; a statistically checked requirement accounts for luck before it fails the property. A property whose generator always produces valid cases discards nothing, and such a generator is preferred to a filter, which is in turn preferred to skipping the case.

Where the precondition is sparse under free generation, as sortedness of a freely drawn list is, a generator that yields valid cases by construction replaces the discard, and the classification this rule asks for is owed only by a discard that remains.

## Validator
Grep the hunk for a precondition that discards the current generated case inside a property body: an assume-style call, a precondition call, an implication operator, or a skip of the current case. Open the property at hunk scope and look for a classification of its accepted cases: label, classify, collect or tabulate calls, events, statistics, a coverage requirement, or per-class counters that the test reports after the run. A skip of the whole test outside a property body is not a discarded case. Validator question: **Does the property discard generated cases through a precondition while neither the property nor its test classifies the cases it accepts, by labels, events, statistics, a coverage requirement or per-class counters that the run reports?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-47`, severity suggestion, `file`, `symbol`, `code` = the precondition line and the property's header, `fix` = the same property in the file's language with the accepted cases labelled or counted and the counts reported, or with a coverage requirement on the class it relies on, `rationale` = names the precondition and the input class whose share among the passing cases goes unreported).
