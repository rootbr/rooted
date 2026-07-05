---
title: Priority markers used per RFC 2119
rule_id: R-63
applies_to_target: [context-file, skill, agent-prompt]
check_kind: mechanical
severity_default: low
---

# Priority markers used per RFC 2119

## Thesis
When ALL-CAPS markers appear, RFC 2119 keywords must carry RFC 2119 semantics:

| Marker | Meaning |
|--|--|
| MUST / REQUIRED / SHALL | Absolute requirement |
| MUST NOT / SHALL NOT | Absolute prohibition |
| SHOULD / RECOMMENDED | Strong default, deviation needs justification |
| SHOULD NOT / NOT RECOMMENDED | Discouraged, deviation needs justification |
| MAY / OPTIONAL | Truly optional, alternatives coexist |

NEVER, ALWAYS, and ONLY are not RFC 2119 keywords — they are house extensions that carry no RFC-defined meaning.

## Rationale
Mixing "MUST" with "should always" or "is recommended to always" creates parse ambiguity for both humans and models: the reader cannot tell which strictness level actually governs the rule.

## Example
```
bad:  "MUST avoid X where possible."
good: "MUST NOT use X."   (or, if conditional)  "SHOULD avoid X; if unavoidable, do Y."
```

## Limits
Concerns the consistency of priority-marker semantics, not how many markers appear or whether a marker is justified. The non-RFC house words (NEVER / ALWAYS / ONLY) are out of scope for the strictness-level check because they have no RFC-defined level to violate.

## Validator
For each MUST / SHOULD, check that the rest of the sentence respects the strictness level. "MUST avoid X where possible" is a contradiction — the "where possible" softens an absolute requirement. Flag the marker and resolve it: drop the softener to keep the MUST, or downgrade the marker to SHOULD.

## Patch output
When a priority marker's strictness conflicts with its clause, emit one patch (`rule_id: R-63`, `location` set to the heading and line hint, `current` = the ambiguous usage, severity low) proposing a consistent marker-plus-clause pairing.

## Source
RFC 2119 (keyword definitions for requirement levels).
