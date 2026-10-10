---
title: Code is made more complex for speed or memory only where a profile or benchmark shows that its cost matters to the program, and otherwise keeps its plain form
rule_id: PRF-07
domain: performance
step: [implement, refactor, review]
applies_to: [universal]
triggers: ['(?i)(//|#|/\*|\*|--)\s*.*\b(for (speed|performance)|faster|speed\s*up|optimi[sz]\w*|hot\s*path|fast\s*path|micro-?optimi\w*|avoids?\s+(an?\s+)?(allocation|copy|copying|boxing))\b', '#\[inline\(always\)\]|\b(unreachable_unchecked|assert_unchecked|get_unchecked(_mut)?|debug_assert\w*!)', '\b(with_capacity|ensureCapacity|reserve)\s*\(|\bsync[.]Pool\b|\bmake\s*\(\s*(\[\]|map\[)[^,]*,\s*\w+', '(?i)\b(memoi[sz]\w*|lru_cache|functools[.]cache\b|precomput\w*|lookup[\s_]?table)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# Code is made more complex for speed or memory only where a profile or benchmark shows that its cost matters to the program, and otherwise keeps its plain form

## Thesis
A change that makes code harder to read or change for the sake of speed or memory (a hand-kept cache or lookup table, a size hint or preallocation, object reuse, an unchecked access or a check kept only in debug builds, a forced-inline hint, a lower-level rewrite, a rewrite that a performance guideline or lint suggests) is made only where a measurement shows the need: a profile of the running program that places that code among its hot spots, or a realistic benchmark of an operation the program needs faster. The added complexity comes with documentation, in the change, a comment at the code or a linked issue, that explains its rationale by naming that measurement; where no measurement shows the need, the code keeps its plain form.

## Rationale
Code tuning modifies correct code so that it runs more efficiently, and where there is no need for it the main result of the effort is more errors and higher maintenance costs. Tuning a part of a program that is not performance critical has no effect on system performance, while attempts at efficiency in noncritical parts have a strong negative impact when debugging and maintenance are considered. Small efficiencies are best forgotten about 97% of the time, yet the opportunities in the critical 3% are worth taking once that code has been identified. Intuition does not identify it: judging a priori which parts are critical is often a mistake, because programmers who use measurement tools find that their intuitive guesses fail, and modern hardware and optimizers defy naive assumptions. Complicated code is not necessarily faster than simple code, and low-level code sometimes inhibits optimizations. A profile of the running program shows where the hot spots are and where tuning effort belongs; where the performance does matter, both forms are profiled with a realistic benchmark before one is judged to outperform the other. A forced-inline hint pays only where the call it removes affects the runtime profile enough to make up for the added compile time, and most code needs no size hint or preallocation and can let the runtime grow the collection. No claim about performance is made without a measurement, and complexity that performance requires is added deliberately, with documentation or commentary that explains its rationale so that future maintainers can understand and navigate it and read it as a sign that the code is performance-critical; employed unnecessarily, the same complexity is a burden on everyone who needs to read or change the code in the future.

## Example
```rust
bad:  // faster: memoized digit count, cache sized up front
      thread_local! { static MEMO: RefCell<HashMap<u64, u64>> = RefCell::new(HashMap::with_capacity(4096)); }
      #[inline(always)]
      fn digits(n: u64) -> u64 { MEMO.with(|m| *m.borrow_mut().entry(n).or_insert_with(|| n.to_string().len() as u64)) }
good: fn digits(n: u64) -> u64 {
          n.to_string().len() as u64
      }
```

## Limits
A form that is faster and at least as easy to read and change as the plain one is outside the rule, since the cost the rule weighs is the complexity a change adds. Preallocating when the final size is known, as when converting one collection into another, is acceptable without a measurement, though it is not a readability requirement and may not be worth the clutter in small cases. A cache, a debug-only check or a capacity hint that serves correctness or an interface contract rather than speed or memory is outside the rule. A change of algorithm or data structure that changes how cost grows with input size is a design decision; the rule covers code tuning, the small-scale changes to a single class, a single routine or a few lines of code. A performance guideline or a lint's suggested rewrite is not itself a measurement: such guidelines apply only on the hot path, and a lint that flags a forced-inline hint is meant to be turned off by whoever has done the measurement. The rule stops at measuring before tuning; low-latency work such as cache-line layout, lock-free structures, allocation-free hot paths and runtime or garbage-collector tuning, and parallelization, are specialties it does not judge.

## Validator
Grep the hunk for an added comment that claims speed or avoided allocation, a forced-inline hint, an unchecked access or debug-only check, a capacity hint, preallocation or pooled object, and a memoization, precomputation or lookup table. Open the file and compare the added form with the plain form it replaces or could have used: confirm that it is harder to read or change and that speed or memory is its purpose, from the comment, the commit message or the replaced code. Look in the hunk, the comment at the code, the commit message and any linked issue for a profile that places this code among the hot spots or a realistic benchmark result for an operation the program needs faster. Set aside a form at least as clear as the plain one, preallocation to a final size already known, and a change of algorithm or data structure. Validator question: **Does the change add a form harder to read or change than the plain one for speed or memory, with no profile or realistic benchmark named in the change, a comment at the code, the commit message or a linked issue?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-07`, severity minor, `file`, `symbol`, `code` = the added tuned line verbatim from the diff, `fix` = the plain form in the file's language, or the tuned form with a comment naming the profile or benchmark that shows the need, `rationale` = names the complexity the change adds and the measurement that is missing).
