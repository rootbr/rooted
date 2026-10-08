---
title: A property that discards generated cases through a precondition labels or counts the cases it accepts, so that a run testing mostly trivial inputs is visible
rule_id: TST-47
domain: tests
step: [test, review]
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
          if !slices.IsSorted(xs) { r.Skip() }
          checkSort(r, xs) })
good: seen := map[bool]int{}
      rapid.Check(t, func(r *rapid.T) {
          xs := rapid.SliceOf(rapid.Int()).Draw(r, "xs")
          if !slices.IsSorted(xs) { r.Skip() }
          seen[len(xs) > 1]++; checkSort(r, xs) })
      t.Logf("accepted: %d non-trivial, %d trivial", seen[true], seen[false])
```

## Limits
The documentation phrases this as advice, to consider a coverage requirement to make sure the test data is still of good quality, so a finding is a suggestion. A proportion missed on one run may be bad luck, since coverage varies randomly, and a plain requirement only warns because it is not tested in a statistically sound way; a statistically checked requirement accounts for luck before it fails the property. A property whose generator always produces valid cases discards nothing, and such a generator is preferred to a filter, which is in turn preferred to skipping the case.

## Validator
Grep the hunk for a precondition that discards the current generated case inside a property body: an assume-style call, a precondition call, an implication operator, or a skip of the current case. Open the property at hunk scope and look for a classification of its accepted cases: label, classify, collect or tabulate calls, events, statistics, a coverage requirement, or per-class counters that the test reports after the run. A skip of the whole test outside a property body is not a discarded case. Validator question: **Does the property discard generated cases through a precondition while neither the property nor its test classifies the cases it accepts, by labels, events, statistics, a coverage requirement or per-class counters that the run reports?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-47`, severity suggestion, `file`, `symbol`, `code` = the precondition line and the property's header, `fix` = the same property in the file's language with the accepted cases labelled or counted and the counts reported, or with a coverage requirement on the class it relies on, `rationale` = names the precondition and the input class whose share among the passing cases goes unreported).

## Source
- `nick8325/quickcheck` master, `src/Test/QuickCheck/Property.hs`, doc comments of `(==>)`, `classify`, `cover`, `checkCoverage`, `checkCoverageWith` (fetched): "in which case the test case is discarded" · "Note that using implication carelessly can severely skew test case distribution: consider using 'cover' to make sure that your test data is still good quality." · "Reports how many test cases satisfy a given condition." · "+++ OK, passed 100 tests (22% non-trivial)." · "sorted xs ==> cover 50 (length xs > 1) "non-trivial" $ sort xs === xs" · "+++ OK, passed 100 tests; 135 discarded (26% non-trivial). … Only 26% non-trivial, but expected 50%" · "Checks that at least the given proportion of /successful/ test cases belong to the given class. Discarded tests (i.e. ones with a false precondition) do not affect coverage." · "prints out a warning, but the property does /not/ fail" · "Ordinarily, a failed coverage check does not cause the property to fail. This is because the coverage requirement is not tested in a statistically sound way." · "since the coverage varies randomly, you may have just been unlucky" · "uses a statistical test to account for the role of luck in coverage failures. It will run as many tests as needed until it is sure about whether the coverage requirements are met. If a coverage requirement is not met, the property fails."
- `HypothesisWorks/hypothesis` master, `hypothesis/docs/reference/api.rst`, section Control, `event` (fetched): "You can mark custom events in a test" · "These events appear in |observability| output, as well as the output of … when run with --hypothesis-show-statistics." · "100 passing, 0 failing, and 32 invalid test cases" · "Events: * 31.06%, i mod 3 = 2"
- `flyingmutant/rapid` master, `engine.go`, doc comment of `SkipNow` (fetched): "SkipNow marks the current test case as invalid" · "Prefer *Generator.Filter to SkipNow, and prefer generators that always produce valid test cases to Filter."
- DOI 10.1145/3597503.3639581, "Property-Based Testing in Practice", ICSE 2024, abstract, §3.1, §4.6, §5.2 RO6 (fetched): "in-depth interviews with experienced users of PBT" · "We recruited 31 participants and carried out 30 interviews" · "11 of them—more than a third—said they did not think as hard as they should about testing effectiveness, or whether they had adequately tested their software with their generators." · "tools should always announce counts of discarded test cases (i.e., ones that failed the property’s precondition) so the developer can catch problems early."
- DOI 10.1145/3654777.3676407, "Tyche: Making Sense of Property-Based Testing Effectiveness", UIST 2024, abstract, Figure 1, §5.2.2, §7.1 (fetched): "A self-guided online usability study" · "a novel ensemble of visualizations" · "leaving 40 valid responses" · "three sets of sampled inputs for testing that property, drawn from three different distributions" · "rank the distributions, in order of their bug-finding power" · "the control interface consisted of … “statistics” output and a list of pretty-printed test input examples" · "the developer can visualize features of the distribution by plotting numerical or categorical data extracted from their test inputs" · "For three of the four tasks (all but Python Interpreter), participants made significantly fewer incorrect comparisons when using Tyche"
- Caveat: the interviews come from one company, "a financial technology firm that uses PBT extensively"; in the online study "The majority of participants (24) described themselves as students" and "Half reported being beginners at PBT", and it compares visualisations with a statistics output, not a visible distribution with none.
