---
title: A generator yields inputs that meet the property's precondition by construction, through its own bounds, a mapping or a composition, whenever a filter or discard would reject a large share of draws, and keeps a filter for a condition that random draws rarely violate
rule_id: TST-45
domain: tests
step: [test]
applies_to: [tests]
triggers: ['[.](?:[Ff]ilter|SuchThat)\(', '\bassume\w*\(|\bAssume[.]that\(', '\bprop_(?:assume|filter|filter_map)\b', '\bfc[.]pre\(', '\s==>\s', '\bsuppress_health_check\b|\bmax_(?:global|local)_rejects\b|\b(?:maxDiscardRatio|discardRatio|maxSkipsPerRun)\b', '\bTestResult::discard\(']
scope: hunk
check_kind: semantic
severity_default: minor
---

# A generator yields inputs that meet the property's precondition by construction, through its own bounds, a mapping or a composition, whenever a filter or discard would reject a large share of draws, and keeps a filter for a condition that random draws rarely violate

## Thesis
A property's generator produces only inputs that meet the property's precondition, through the generator's own bounds, a mapping of a freely drawn value into the valid domain, or a composition of valid parts, whenever the precondition is sparse under free generation, so that a filter or a discard rejects a large share of draws; a filter on a single generator stays for a condition that random draws rarely violate.

## Rationale
Filtering is rejection sampling: every rejected value is generated again, a strict filter rejects plenty of values for each one kept, and a filter that always rejects could in principle never produce an input. Where rejected values count against the sample size, a run can end with no value that passed the precondition. This much filtering may also distort the domain and the distribution of the inputs, leaving testing less rigorous than expected. Frameworks bound the waste by stopping the test: one raises a filtering health check once 50 draws are filtered out before 10 succeed, one aborts past 1024 rejected whole cases or 65,536 rejected individual inputs, and one gives up past 10 discarded cases per successful case. Shrinking loses as well: a value rejected while shrinking carries no pass or fail information, and in one framework such a rejection stops shrinking from reaching any simpler value, even one the filter would accept. A generator whose every output meets the precondition found more bugs, more quickly, with better quality tests: across binary-search-tree, red-black-tree and two typed lambda-calculus workloads it solved all tasks while a naive type-derived generator failed 43, and among tasks both solved its average time was significantly lower on 83 of 124 and its average count of valid inputs lower on 89 of 124. On red-black trees a type-based generator failed 23 tasks within a 60-second timeout, while the hand-written valid-by-construction generator solved all tasks in under ten seconds. Bounds and mappings remove the rejection: a string of at least two characters comes from a generator with a minimum length of two, a digit from a generator bounded to 0 through 9, an even integer from doubling a drawn integer, a sorted list from sorting a drawn list. Where some discarding remains, a filter on one generator costs less than a discard of the whole case: the rejected value is redrawn from that generator alone and retried several times, and a simple filter can often be rewritten into a more efficient sampling method, while a whole-case discard regenerates every input.

## Example
```python
bad:  @given(st.lists(st.integers()).filter(lambda xs: xs == sorted(xs)))
      def test_insert_keeps_order(xs):
          assert is_sorted(insert(xs, 0))
good: @given(st.lists(st.integers()).map(sorted))
      def test_insert_keeps_order(xs):
          assert is_sorted(insert(xs, 0))
```

## Limits
The precondition's sparseness under free generation separates the cases. Generate-and-filter works well in some circumstances: for binary search trees, generating trees by type and filtering out the invalid ones can rapidly find all the bugs of a published testing guide. The same approach breaks down with sparser preconditions: valid red-black trees are harder to generate at random, so type-driven strategies work less well there. Writing generators costs effort that developers see as a distraction, difficult and time-consuming, and they prefer derived generators, so the rule binds only where the precondition is sparse and the filter rejects a large share of draws. Where no bound, mapping or composition reaches the valid domain and that much filtering is expected, a framework permits disabling the filtering health check for that test, and its documentation strongly recommends suppressing health checks as they are encountered rather than through a blanket suppression. Tooling does not catch every over-filtered property: one framework by default gives up when 10,000 attempts fail to find 100 valid cases, and with its minimum of passing valid cases defaulting to 0 such a run counts as a success.

## Validator
Grep the hunk for a filter on a generator, a precondition or discard call inside a property body, a precondition implication, a suppressed filtering health check, or a raised rejection or discard limit. Open the generator and the predicate at hunk scope and judge the share of freely drawn values the predicate rejects: a sortedness, structural-invariant or narrow-range predicate over a wide free generator rejects most draws, and a distinctness predicate does so only when the elements come from a domain narrow relative to the collection's length, while excluding one value such as zero, or excluding equality between draws from a wide domain, rejects few. Trace whether the generator's own bounds, a mapping of a free draw or a composition of valid parts would produce the valid values directly. Validator question: **Does a filter, discard, suppressed filtering check or raised rejection limit in the hunk serve a predicate that rejects a large share of freely drawn values, where bounds, a mapping or a composition could produce the valid values directly?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-45`, severity minor, `file`, `symbol`, `code` = the filter, discard, implication, suppression or limit line quoted verbatim from the diff, `fix` = the generator rewritten with its own bounds, a mapping or a composition so that every draw meets the precondition, in the file's language, `rationale` = the predicate's share of rejected draws and the rejection limit, distortion or shrinking loss it risks).
