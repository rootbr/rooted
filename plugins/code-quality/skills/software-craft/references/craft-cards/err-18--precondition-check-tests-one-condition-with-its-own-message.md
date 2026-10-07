---
title: Each precondition check tests one condition with its own message, so a failure names the precondition that was violated
rule_id: ERR-18
domain: errors
step: [implement, review]
applies_to: [universal]
triggers: ['\b(check(Argument|State|NotNull|ElementIndex|PositionIndex)|require|requireNonNull|verify|invariant|isTrue|state|validState)\s*\(.*(&&|\|\|)', '^\s*assert\b.*(&&|\|\||\s(and|or)\s)', '\b(debug_)?(assert|ensure)!\s*\(.*(&&|\|\|)', '\bif\b.*(==|!=|\bis\b)\s*(null|nil|None|undefined)\b.*(\|\||\sor\s)|\bif\b.*(\|\||\sor\s).*(==|!=|\bis\b)\s*(not\s+)?(null|nil|None|undefined)\b', '\bif\b.*(\|\||\sor\s|!\s*\(.*&&|\bnot\s*\(.*\sand\s).*(\b(throw|raise|panic)\b|[{:]\s*$)', '\b((debug_)?(assert|ensure)!?|check(Argument|State)|isTrue|state|validState|require|verify|invariant)\s*\(\s*$', '^\s*(\|\||&&|or\s|and\s)|(\|\||&&)\s*$']
scope: hunk
check_kind: mechanical
severity_default: suggestion
---

# Each precondition check tests one condition with its own message, so a failure names the precondition that was violated

## Thesis
A precondition check at a routine's entry, on the routine's arguments or on the object's state — the language's assertion, a library precondition call, or a conditional that fails the call when its condition holds — tests one precondition, stands on its own line and carries a helpful message of its own. Independent preconditions get one check each instead of sharing one failure, whether a logical and would join them in a condition that must hold or a logical or would join them in a condition that fails the call, so that the failure can show which precondition the caller violated.

## Rationale
A precondition check lets a routine tell its caller that the caller has made a mistake. An assertion that combines several independent conditions is harder to debug upon failure, since its failure message does not indicate which condition failed. Splitting the preconditions onto distinct lines can help find which one failed while debugging, and a helpful message is easier to write when each check is on its own line. Without a good custom message it is hard to understand what went wrong when an assertion fails, and some library checks of an argument, a state or a non-null value, called with no message argument, throw their exception without one. A conditional that fails the call tests the opposite of what a check call asserts, as when a test that a value is negative is replaced by a check that it is at least zero; a negated or is an and of the negated parts, so preconditions joined by or in a failing conditional are the same composite as preconditions joined by and in an assertion.

## Example
```rust
bad:  pub fn new(name: &str, size: usize) -> Self {
          assert!(!name.is_empty() && size.is_power_of_two(), "invalid arguments");
          Self { ... }
      }
good: pub fn new(name: &str, size: usize) -> Self {
          assert!(!name.is_empty(), "name must not be empty");
          assert!(size.is_power_of_two(), "size must be a power of two, got {size}");
          Self { ... }
      }
```

## Limits
Both bounds of one value's range form one precondition: a standard-library index check can test that an index lies from zero inclusive to a length exclusive in one call and report a failure at either bound with one message naming the index and the length. A condition that must hold as a disjunction, met when any one of its parts holds, is one precondition, since no part of it has to hold alone; only a conjunction, or a negated disjunction, splits into independent checks. A library check that tests several conditions in one call and builds its message from the part that failed, as a check of a start and an end index against a size does, already names the violated precondition. The lint rule that flags a combined assertion sits in its linter's pedantic category, and the one that flags an assertion without a message is allowed by default; a project context that documents combined argument checks as its style rejects the finding. What a message says beyond naming its precondition, such as the operation and the offending values, and whether a check that a build can strip is the right form, are judged by their own rules.

## Validator
Grep the added lines for an assertion, a library precondition call (a check of an argument, a state, a non-null value or an index, or a require, ensure, verify or invariant call) or a conditional that throws, raises, panics or returns an error, whose condition, on that line or on the lines that continue the statement, carries a logical and or or. Open the hunk and confirm that the check guards the routine's arguments or the object's state at entry; a conditional that steers ordinary control flow and an assertion inside a test are outside the rule. Put the condition in its must-hold form, negating the condition of a conditional that fails the call, and split it at its top-level and: two or more parts that could each be checked alone, in order, are independent preconditions under one failure. Count as one precondition both bounds of one value's range, a must-hold disjunction, a single predicate call, and a library check that builds its message from the part that failed. Validator question: **Does an added precondition check at a routine's entry test two or more independent preconditions under one failure, joined by a logical and in a condition that must hold or by a logical or in a condition that fails the call?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-18`, severity suggestion, `file`, `symbol`, `code` = the added check line that joins the preconditions, verbatim from the diff, `fix` = one check per precondition, each on its own line with a message of its own naming that precondition, in the file's language, `rationale` = the preconditions the check joins and that its failure cannot say which of them the caller violated).

## Source
- Guava User Guide, Preconditions (google/guava wiki `PreconditionsExplained.md`), closing recommendation — "We recommend that you split up preconditions into distinct lines, which can help you figure out which precondition failed while debugging. Additionally, you should provide helpful error messages, which is easier when each check is on its own line."; method variants — "No extra arguments. Any exceptions are thrown without error messages."; `checkArgument` — "Use for validating arguments to methods"; `checkState` — "Checks some state of the object, not dependent on the method arguments"; `checkPositionIndexes` — "Checks that `start` and `end` are both in the range `[0, size]` (and that `end` is at least as large as `start`). Comes with its own error message." (fetched)
- Guava `Preconditions` class Javadoc and `badPositionIndexes` (google/guava `guava/src/com/google/common/base/Preconditions.java`) — "check whether it was invoked correctly (that is, whether its *preconditions* were met)"; the exception "helps the method in which the exception was thrown communicate that its caller has made a mistake"; `if (value < 0) { throw new IllegalArgumentException(...) }` "to be replaced with the more compact" `checkArgument(value >= 0, ...)`; the range check's message names "start index", "end index" or "end index (%s) must not be less than start index (%s)" (fetched)
- Ruff `PT018` pytest-composite-assertion (astral-sh/ruff `crates/ruff_linter/src/rules/flake8_pytest_style/rules/assertion.rs`) — "Checks for assertions that combine multiple independent conditions"; "Composite assertion statements are harder to debug upon failure, as the failure message will not indicate which condition failed"; splits "`a and b` or `not (a or b)`. The latter is equivalent to `not a and not b` by De Morgan's laws", and leaves "`a or b or c`" whole (fetched; pedantic category; it runs on every assert statement, and its examples are test functions)
- clippy `missing_assert_message` (rust-lang/rust-clippy `clippy_lints/src/missing_assert_message.rs`) — "Without a good custom message, it'd be hard to understand what went wrong when the assertion fails." (fetched; restriction group, "allow" by default per the clippy README, test functions ignored)
- OpenJDK 21 `java.util.Objects.checkIndex` (openjdk/jdk `src/java.base/share/classes/java/util/Objects.java`; message in `jdk/internal/util/Preconditions.java`) — "Checks if the `index` is within the bounds of the range from `0` (inclusive) to `length` (exclusive)", out of bounds "if any of the following inequalities is true": "`index < 0`", "`index >= length`"; failure message "Index %s out of bounds for length %s" (fetched)
- Caveat: no study measures the debugging cost of a combined check; the rule rests on library documentation and two lint rules.
