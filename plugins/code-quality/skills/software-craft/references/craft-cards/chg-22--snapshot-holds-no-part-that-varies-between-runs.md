---
title: A snapshot or golden value holds no part that can differ between runs of unchanged code unless the test fixes, redacts or matches that part by property
rule_id: CHG-22
domain: change
step: [test]
applies_to: [tests]
triggers: ['[.]toMatch(Inline)?Snapshot\(|\bassert_\w*snapshot!|\bApprovals?[.]verify\w*\(|==\s*snapshot\b|\bgolden\w*', '(?i)\bDate[.]now|\bnew Date\(\)|\bInstant[.]now|\bLocalDate(Time)?[.]now|\btime[.]Now|\bdatetime[.](now|utcnow)|\bSystemTime::now|\bUtc::now|\b(uuid\w*|randomUUID|Math[.]random|random[.]\w+|rand[.]\w+|rand::|nanoid)|[.]hashCode\(\)|\{:p\}|%p\b|object at 0x']
scope: callers
check_kind: semantic
severity_default: major
---

# A snapshot or golden value holds no part that can differ between runs of unchanged code unless the test fixes, redacts or matches that part by property

## Thesis
Every value a snapshot or golden-file test stores is the same on each run of unchanged code. A part that is not guaranteed to be the same on each run — the current date or time, a generated or random identifier, an identity hash code printed by a default object rendering, or the iteration order of a map or set whose order is unspecified or follows a per-process hash seed — enters the stored value only after the test fixes its source with a double that returns a constant (a mocked clock or identifier generator), stores a placeholder for it (a property matcher, saved to the stored value instead of the received value, or a snapshot serializer), or renders it in a defined order such as sorted keys.

## Rationale
A stored value that embeds a run-varying part can differ on the next run although the code has not changed: generated identifiers and dates force a snapshot to fail on every run, and in a grey-literature review of 50 documents on snapshot testing, three (6%) reported flaky snapshot tests, primarily due to non-deterministic data such as random UUIDs and the current date or time causing intermittent failures. Automatically generated unit tests show the same failure: tests on classes that make use of the system time may have failing assertions if executed at a different time than when they were generated. Regression testing assumes that an unmodified test either always passes or always fails for the same code under test; a test with non-deterministic outcomes undermines regression testing by making its results difficult to rely on. Platforms document the run-varying sources: a default identity hash code need not remain consistent from one execution of an application to another, and the default object rendering prints the class name followed by that hash code in hexadecimal; string hashes salted with an unpredictable random value stay constant within a process but are not predictable between invocations, and changing hash values affects the iteration order of sets; a map's iteration order may be left unspecified and not guaranteed to be the same from one iteration to the next. Replacing the source with a double that returns a consistent value generates the same stored value regardless of when the test runs, which restores the always-pass-or-always-fail property.

## Example
```go
bad:  func render(o order) string { return o.name + " " + time.Now().Format(time.RFC3339) }
      if got := render(o); got != golden(t, "render") { t.Errorf("got %q", got) }
good: func render(o order, now func() time.Time) string { return o.name + " " + now().Format(time.RFC3339) }
      fixed := func() time.Time { return time.Date(2020, 1, 2, 3, 4, 5, 0, time.UTC) }
      if got := render(o, fixed); got != golden(t, "render") { t.Errorf("got %q", got) }
```

## Limits
A formatter that prints maps in key-sorted order does so to ease testing, and a dictionary that preserves insertion order produces keys in the order they were added; storing such a rendering is not a finding when the keys are added in an order that does not vary between runs. A dictionary or list filled by iterating a map or set whose order is unspecified or follows a per-process hash seed carries that iteration order into the stored value, so it is traced like the iteration itself. A constant the test supplies for the time or an identifier fixes that part at its source, and a property matcher is saved to the stored value instead of the received value; both satisfy the rule. A salted hash stays constant within one process, so a comparison made inside a single run is unaffected; the rule concerns the value stored for a later run. A rendering documented as not stable across toolchain versions, such as a derived debug format, may change with a future version; that change follows an upgrade and calls for re-recording, which is outside this rule's run-to-run condition. Data that differs between platforms rather than between runs is outside this rule's run-to-run condition, although snapshot-testing documentation asks that stored snapshots exclude platform-specific data as well.

## Validator
Grep the hunk, and the rest of the test file it changes, for a snapshot or golden assertion: a snapshot matcher or macro, an approval verify call, or a comparison against a stored golden file. Trace the value handed to each such assertion back to what produces each of its parts: a read of the current time, a random or generated identifier, a default object rendering that prints an identity hash, or iteration over a map or set rendered without a defined order. For each such part, look for the test fixing its source with a double or injected function that returns a constant, a property matcher or serializer that stores a placeholder for it, or a rendering in a defined order such as sorted keys. Validator question: **Does a value stored by a snapshot or golden assertion in this file contain a part that is not guaranteed to be the same on each run of unchanged code, which the test neither fixes at its source, replaces with a placeholder, matches by property, nor renders in a defined order?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-22`, severity major, `file`, `symbol`, `code` = the snapshot or golden assertion and the line that produces the run-varying part, verbatim from the diff, `fix` = the test fixing that source with a double or injected function that returns a constant, a property matcher or redacting serializer, or a sorted rendering, in the file's language, `rationale` = names the run-varying part and that the stored value can differ on a later run of unchanged code).
