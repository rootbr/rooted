---
title: An object whose lifecycle states are mutually exclusive holds its current state in one variable of an enumerated type, not in two or more boolean flags that cannot vary independently
rule_id: CODE-17
domain: code
step: [design, implement, refactor]
applies_to: [universal]
triggers: ['(?i)\b(is|has|was)_?(loading|loaded|running|started|stopped|finished|done|complete|completed|pending|processing|paid|shipped|open|opened|closed|active|cancell?ed|failed|ready|connected|initiali[sz]ed|submitted|approved|published)\b\??\s*(:|=|bool)', '\b(bool|boolean|Boolean)\b', '\b\w+[.]\w+\s*=\s*(true|false|True|False)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# An object whose lifecycle states are mutually exclusive holds its current state in one variable of an enumerated type, not in two or more boolean flags that cannot vary independently

## Thesis
An object that moves through a fixed set of states and is in exactly one of them at a time holds its current state in one variable of an enumerated type, a single field of the object whose members are those states. Two or more boolean fields of one object that together encode those states and cannot vary independently, so that some combination of their values names no state, such as a processing flag and a finished flag both set, are the defect.

## Rationale
Boolean fields set independently of each other let the object reach combinations of values that no state of its state machine defines. In the documented peripheral example, a direction flag and an output-level flag, each set through its own setter, reach an input that is set high, a state the machine does not define; for some hardware this may not matter, and on other hardware it could cause unexpected or undefined behaviour. Two flags suffice for that. A documented lint calls excessive boolean fields in a record often a sign that the type is being used to represent a state machine, which is much better implemented as an enumeration, because an enumeration more easily forbids invalid states; its example replaces three fields, pending, processing and finished, with one enumeration of three members. The lint fires on a record with more than three boolean fields by default and belongs to a group, off by default, of lints that are rather strict or have occasional false positives; a count above its threshold is, in its words, often a sign of a state machine, not proof of one, and the defect is flags that cannot vary independently, which two flags already show. Where the language can declare one type per state as tagged variants, data that exists in one state only is declared, as required, in that state's variant: a state tag kept beside optional fields leaves the type checker no way to know from the tag whether those fields are present.

## Example
```rust
bad:  struct Job { is_processing: bool, is_finished: bool, exit_code: Option<i32> }
      fn finish(job: &mut Job, code: i32) {
          job.is_processing = false;
          job.is_finished = true;
          job.exit_code = Some(code);
      }
good: enum JobState { Pending, Processing, Finished { exit_code: i32 } }
      struct Job { state: JobState }
      fn finish(job: &mut Job, code: i32) { job.state = JobState::Finished { exit_code: code }; }
```

## Limits
A single boolean whose two values are the object's only two states leaves no combination undefined and is outside the rule. A state held in one place in another form, one field whose value is a state object with one type per state, or one type per state for the object itself, keeps no flags and is outside the rule. Flags for aspects that vary independently of each other, every combination of whose values is a state the object can be in, reach no undefined state and stay separate fields; the lint's documented help offers two remedies, a state machine or each boolean refactored into its own two-member enumeration, and only the first folds the flags into one type. A record whose memory layout is declared explicitly is skipped by the lint and is outside the rule. Flags and optional fields that stand for combinations of domain facts other than the states an object moves through are outside the rule, and so is the synchronization of a state shared between threads.

## Validator
Grep the hunk's added lines for boolean field declarations, boolean literals assigned to fields, and flag names built on a state word such as pending, processing, finished, paid or shipped. Open the file and find the record that declares each flag; list its boolean fields, every assignment to them, and every condition or derived predicate that reads two of them together. Trace whether the flags cannot vary independently: one is set only while another holds or is cleared when another is set, a condition rejects or ignores some combination of them, or a predicate combines them into one named state; note whether the record already declares an enumerated state field beside the flags. Pass a single boolean with two states, flags every combination of whose values is a state the object can be in, a record whose memory layout is declared explicitly, flags standing for domain facts rather than the states an object moves through, and a record the project context exempts. Validator question: **Does added code keep one object's mutually exclusive states in two or more boolean fields, some combination of whose values names no state the object can be in?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CODE-17`, severity minor, `file`, `symbol`, `code` = the boolean field declarations and the assignment, condition or predicate that ties one flag to another, verbatim from the diff, `fix` = one enumerated type listing the states and one field of that type replacing the flags, with data that exists in one state only moved into that state's variant where the language has tagged variants, in the file's language, `rationale` = the combination of flag values that names no state, and that an enumeration more easily forbids invalid states than a record of booleans).

## Source
- clippy `struct_excessive_bools`, group `pedantic` (rust-lang/rust-clippy `clippy_lints/src/excessive_bools.rs`; `max-struct-bools` in `book/src/lint_configuration.md`; group table in `README.md`): "Excessive bools in a struct is often a sign that the type is being used to represent a state machine, which is much better implemented as an enum."; "The reason an enum is better for state machines over structs is that enums more easily forbid invalid states."; example `is_pending`, `is_processing`, `is_finished` replaced by `enum S { Pending, Processing, Finished }`; help "consider using a state machine or refactoring bools into two-variant enums"; message "more than {} bools in a struct", `max-struct-bools` "**Default Value:** `3`"; `clippy::pedantic` "lints which are rather strict or have occasional false positives", default level allow; the check requires `!has_repr_attr(cx, item.hir_id())`. (fetched)
- The Embedded Rust Book, Peripherals as State Machines § Hardware Representation (rust-embedded/book `src/static-guarantees/state-machines.md`): `set_direction(&mut self, is_output: bool)`, `set_output_mode(&mut self, is_high: bool)`; "what happens if we set the `output_mode` field when our GPIO is configured as an input?"; "use of this structure would allow us to reach states not defined by our state machine above: e.g. an output that is pulled low, or an input that is set high. For some hardware, this may not matter. On other hardware, it could cause unexpected or undefined behavior!" (fetched)
- TypeScript Handbook, Narrowing § Discriminated unions (microsoft/TypeScript-Website `packages/documentation/copy/en/handbook-v2/Narrowing.md`): "The problem with this encoding of `Shape` is that the type-checker doesn't have any way to know whether or not `radius` or `sideLength` are present based on the `kind` property."; "we've properly separated `Shape` out into two types with different values for the `kind` property, but `radius` and `sideLength` are declared as required properties in their respective types." (fetched)
- The Rust Programming Language, Implementing an Object-Oriented Design Pattern (rust-lang/book `src/ch18-03-oo-design-patterns.md`): "a blog post struct that has a field to hold its state, which will be a state object from the set “draft,” “review,” or “published.”"; "You may have been wondering why we didn’t use an enum with the different possible post states as variants. That’s certainly a possible solution"; "we’ll encode the states into different types. Consequently, Rust’s type-checking system will prevent attempts to use draft posts where only published posts are allowed by issuing a compiler error." (fetched)
- Caveat: one lint's documentation and three official documentation pages, one about a hardware peripheral, one about a shape tag rather than a lifecycle, and one that bears on the Limits only; no study measuring defects from state held in boolean flags was found.
