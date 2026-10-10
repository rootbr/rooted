---
title: A test compares a result by its value, fields, parsed content or kind rather than by a string rendering, formatted output or serialized bytes whose exact form comes from code the project does not own
rule_id: TST-52
domain: tests
step: [test]
applies_to: [tests]
triggers: ['(\b(assert\w*|expect|assertThat|Equal\w*|toBe|toEqual)\b.*([.]toString\(\)|\b(JSON[.]stringify|json[.]dumps|serde_json::to_string\w*|repr|str)\()|format!\(\s*"[^"]*\{\w*:#?\?\}|\b(json[.]Marshal(Indent)?|proto(json|text)[.](Marshal|Format)|fmt[.]Sprint[fl]?)\()', '\b(assert\w*|expect|assertThat|Equal\w*|toBe|toEqual)\b.*[\x22\x27\x60]\s*[{\[]\s*\\?[\x22\x27]?\w+\\?[\x22\x27]?\s*:']
scope: callers
check_kind: semantic
severity_default: minor
---

# A test compares a result by its value, fields, parsed content or kind rather than by a string rendering, formatted output or serialized bytes whose exact form comes from code the project does not own

## Thesis
When a test checks a result whose text is rendered by code the project does not own (a library's text, JSON or binary serializer, the runtime's printed form of an unordered collection, a derived debug format or a default string conversion) and that text is not itself the behaviour under test, the test compares the semantically relevant information: the value or its fields by equality, the parsed content against an expected data structure, or the kind of the result rather than its display text.

## Rationale
A rendering produced by code the project does not own can change while the value it renders stays the same, and a test that performs string equality on it "may break" when the dependency changes how it serializes. A standard-library JSON encoder can change, and has changed in the past, the specific bytes it emits, and the same holds case by case for the other renderers: a protocol-buffer JSON encoder's output "will change across different builds of your program, even when using the same version" of its module; protocol-buffer serialization "is not (and cannot be) canonical", which defeats "comparing serialized payloads as a way of checking message equality"; derived debug formats "are not stable" and may change with future versions of the language; the root object type's string conversion "is not necessarily stable over time or across" virtual-machine invocations; and the order in which a set's elements are printed is not guaranteed. For functionality that returns a formatted string or serialized bytes, "it is generally not safe to assume that the output is stable". For errors, "semantic information that can be reliably observed" is separate from "display information that is intended for human debugging", which "is often subject to future changes". The alternative is to compare "semantically relevant information that is stable and resistant to changes in dependencies", and for serialized output to parse it and check that it "is semantically equivalent to some expected data structure".

## Example
```python
bad:  # order_json returns json.dumps of the order's fields
      assert order_json(order) == '{"id": 7, "rush": true}'
      assert str(active_tags(order)) == "{'gift', 'rush'}"
good: assert json.loads(order_json(order)) == {"id": 7, "rush": True}
      assert active_tags(order) == {"gift", "rush"}
```

## Limits
The rule is contested, and one condition separates the two practices: whether the exact form of the compared text comes from code the project owns and is the behaviour under test. Owned text that is the behaviour under test is compared as text: a source formatter's own tests compare its output byte for byte against stored golden files that an update flag regenerates, and a snapshot tool's guide says snapshots "should be used anytime the goal is testing whether the output is correct", and adds that the tests "should be deterministic". A rendering that a library, the runtime, a derive or a default implementation produces is compared by value: the rule applies only to results that may depend on output stability of a package the project does not own, and those renderings are documented as unstable. Snapshot or approval files that store a library's or a derived debug rendering and are regenerated and reviewed through the tool's update workflow are the mixed case and stay outside this rule: one snapshot tool compares "Debug outputs of values" and comes "with comprehensive tools to review changes", and another changed "the default snapshot formatting" in a major release while offering a setting to keep the old format. An error checked through its message text and an assertion that checks only a partial property of a result are outside this rule's scope.

## Validator
Grep the hunk for assertions whose one side is a string literal, a multi-line string or a stored file and whose other side is a string conversion, a debug format, a printed collection, a serializer call, or a call to the code under test that returns text. For each, open the code under test at the callers scope and trace where the compared text is produced. A library or runtime serializer, a default or derived string or debug implementation, or the printed form of an unordered collection makes the assertion a candidate. The project's own formatter or generator whose text is the specified output, snapshot or golden files maintained through an update workflow, and an error checked through its message text clear it. Validator question: **Does an assertion compare against a literal or stored text the exact rendering of a result whose format a library, the runtime, a derive or a default implementation produces, where that rendering is not the behaviour under test?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-52`, severity minor, `file`, `symbol`, `code` = the assertion with the rendered result and the expected text, verbatim from the diff, `fix` = the assertion rewritten to compare the value, its fields, its parsed content or its kind against an expected structure, in the file's language, `rationale` = names the code that renders the text and its documented instability).
