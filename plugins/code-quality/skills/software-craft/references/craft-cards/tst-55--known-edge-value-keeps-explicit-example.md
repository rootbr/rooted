---
title: A known single-value edge case of a property's large input domain keeps an explicit example that every run executes, unless the generator in use is documented to generate that value in every run
rule_id: TST-55
domain: tests
step: [test, refactor]
applies_to: [tests]
triggers: ['@given\(|@Property\b|\bproptest!\s*\{|\bfc[.](assert|property)\(|\bf[.](Fuzz|Add)\(|\bquick[.]Check\(|\bquickCheck\b|\bforAll\b', '\b(i8|i16|i32|i64|i128|isize)::MIN\b|\b(Integer|Long|Short)[.]MIN_VALUE\b|\bmath[.]MinInt\d*\b|\bNumber[.]MIN_SAFE_INTEGER\b|-2\s*\*\s*\*\s*(31|63)\b']
scope: base-compare
check_kind: semantic
severity_default: minor
---

# A known single-value edge case of a property's large input domain keeps an explicit example that every run executes, unless the generator in use is documented to generate that value in every run

## Thesis
When a property or fuzz target covers a large input domain in which one single value is known in advance to need its own check, that value stays as an explicit example that every run executes: an example attached to the property, a seed-corpus entry, or an example-based test beside it. Such a value is a type's minimum or maximum at which the operation overflows or wraps, a sentinel or special constant that the code under test treats apart, or a specific known edge case that an example test pinned before the property replaced it. The exception is a generator in use that is documented to generate that value in every run of the property.

## Rationale
Time is finite, so only a randomly sampled portion of the input space is explored, and sampling is extremely unlikely to find a single-value edge case in a large space. A generator that draws 64-bit integers uniformly distributed over the whole range has to pick one specific value out of 2^64, which is overwhelmingly unlikely, so an absolute-value property that fails only at the type's minimum virtually always passes. Example cases chosen by hand are therefore still necessary for many kinds of problems: property tests are best used to complement example tests, which cover specific known edge cases, simple inputs and inputs known in the past to reveal bugs, while the property searches for more complicated inputs. Boundary-value testing chooses cases on or near the boundaries of the input domain, with the rationale that many faults tend to concentrate near the extreme values of inputs. An explicit example attached to a property runs every time, in addition to the generated cases, and one fuzzing toolchain documents that its seed-corpus entries run by default with its plain test command, whether fuzzing or not.

## Example
```rust
bad:  proptest! {
          #[test]
          fn magnitude_is_abs(x: i64) { prop_assert_eq!(magnitude(x), x.unsigned_abs()); }
      }  // no example pins i64::MIN
good: proptest! { ... }
      #[test]
      fn magnitude_at_min() { assert_eq!(magnitude(i64::MIN), 1u64 << 63); }
```

## Limits
The two positions separate on whether the generator in use is documented to produce the value in every run. On the example side stand a generator documented as uniform over the whole range of a 64-bit integer, one whose integers' maximum absolute value depends on a size parameter, and one that chooses from the entire range of a bounded type but generates small numbers more often than big numbers; none is documented to produce a given extreme, so the example stays. A generator documented only to favour such values also keeps the example: one framework's integer strategy upweights range endpoints, yet the framework calls its distribution a deeply internal implementation detail that it sometimes changes, and it directs users to an explicit example to always run a specific input; another documents only that smaller or more extreme values are more likely. The opposing position holds that property-testing frameworks are fully able to find corner-cases with no help at all. A framework that lists the type's minimum among its default integer edge cases and is set to generate all edge cases before any randomly generated sample generates that value in every run whose tries cover its edge cases, as long as the value stays among the edge cases the framework keeps for that parameter (it caps the edge cases of each later parameter), so there the rule does not apply. The same framework's default only mixes edge cases in among the random samples and reports per run how many it tried against their total, so a property left at that default keeps the example. The rule covers a single value in a large space, the case the evidence describes; a small domain is outside it. A failing input that a property has already found, and a comparison boundary that example tests alone check, are outside this rule; it covers a value known in advance that the test trusts a property to reach.

## Validator
Grep the hunk for property or fuzz-target declarations and for example tests the change adds or removes. Open the test file at base and at head: list the example tests the change removes and the explicit examples, seed-corpus entries and example tests that remain beside the property. Name the single value the code under test treats specially (an overflow or wrap at a type's minimum or maximum, a sentinel, a constant it branches on, a value a removed example pinned), then trace the generator in use to its documentation and check whether that documentation states that the value is generated in every run. Validator question: **Does the change add a property over a large input domain, or replace example tests with one, where the code under test has a known single special value that no explicit example, seed-corpus entry or example test covers, while the generator in use is not documented to generate that value in every run?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-55`, severity minor, `file`, `symbol`, `code` = the property declaration with its generator, quoted verbatim from the diff, `fix` = an explicit example of the special value beside the property, as an attached example, a seed-corpus entry or an example-based test in the file's language, `rationale` = names the special value, the generator's documented distribution, and why random sampling of a large domain is unlikely to reach one value).
