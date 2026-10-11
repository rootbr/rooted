---
title: A change to an accepted decision record or design proposal goes in as a very minor amendment or a superseding record rather than a rewrite of the recorded decision
rule_id: DOC-16
domain: docs
step: [design, document, review]
applies_to: [prose]
triggers: ['(?i)^\s*(?:[-*+]\s+)?[*_]{0,2}status[*_]{0,2}\s*[:|-]?[*_]{0,2}\s*["`]?(accepted|superseded|deprecated|rejected|final|proposed|active)\b', '(?i)^(?:#{2,4}\s+(?:status|decision|amendments?|updates?)\s*$|\s*"?decision"?\s*:)', '(?i)\b(?:we (?:will|shall|decided|chose)|chosen option)\b']
scope: base-compare
check_kind: semantic
severity_default: suggestion
---

# A change to an accepted decision record or design proposal goes in as a very minor amendment or a superseding record rather than a rewrite of the recorded decision

## Thesis
Once a decision record or design proposal has been accepted, or the code its design document describes has been implemented, a later change leaves the recorded decision, with its context and consequences, substantially as accepted. A very minor change, as the project defines one, goes in as an amendment to the record; a more substantial change goes in a new record, with a note added to the original, which may name its replacement, in which case the new record names the record it replaces. The expected current behaviour is maintained in formal documentation kept elsewhere, such as a language or library reference.

## Rationale
Once resolution is reached, an accepted record is a historical document rather than a living specification, and formal documentation of the expected behaviour is maintained elsewhere. After the code is implemented, a design document serves as an archive of the decisions taken, not as a half-correct document; design documents are often misused that way. A substantial change made as a new record leaves the original substantially unchanged apart from a note: the superseded record may carry the number of the record that replaces it, and the newer record then carries the number of the record it rendered obsolete.

## Example
```typescript
bad:  const record7 = {
        status: "accepted",
        decision: "We will store sessions in Redis", // edited in place over "in memory"
      };
good: const record7 = { status: "superseded by record 12",
        decision: "We will store sessions in memory" };
      const record12 = { status: "accepted", replaces: 7,
        decision: "We will store sessions in Redis" };
```

## Limits
The rule starts at acceptance or implementation: a proposal still under discussion exists to collect feedback on the design. A process may admit changes based on implementation experience and user feedback while a record is provisional, or accepted with approval, before it is final; those changes are noted in the record, so that it accurately describes the implementation at the point it is marked final. A record kept active to reflect development practices may be updated over time. What counts as a very minor change is the project's to decide. Both amending and superseding are sanctioned, and the size of the change separates them: a very minor change is an amendment to the existing record, and a more substantial change is a new record with a note added to the original. A change that updates only the formal documentation of current behaviour is outside the rule.

## Validator
Grep the hunk for a status line naming accepted, final, active, superseded, deprecated or rejected, for a decision field or a decision sentence ('We will', 'Chosen option'), and for a Status, Decision or Amendments heading. Open the file at the base revision and read its status; continue only when the base already marks the record accepted, final, superseded or deprecated, marks its design implemented, or keeps it where the project's process holds only accepted records, such as a directory of merged proposals, and stop when it is proposed, draft or provisional, or an active record meant to track current practice. Compare the base's decision, context and consequences text with the head's, counting a note or amendment added beside it as part of the change: a typo, link or formatting fix, a rewording that leaves the meaning of that text unchanged, or a note on the original naming the record that replaces it, is a very minor change and passes, and the project's own definition of a very minor change wins where it has one. Any other change to that text, made by editing it or by adding an amendment beside it, passes only when the project's process gives accepted records a later final status and admits changes noted in the record until then, the base does not yet mark the record final, and the change is noted there; a superseding record added in the same change carries the new decision and does not excuse such a change to the original. Validator question: **Does the change make more than a very minor change to the recorded decision, context or consequences of a record that the base revision already marks accepted, final, superseded, deprecated or implemented, or keeps among accepted records, other than a noted change that the project's process admits between acceptance and a later final status?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-16`, severity suggestion, `file`, `symbol`, `code` = the changed or added record line quoted verbatim from the diff, `fix` = the base record text restored, the change carried by a new record naming this one as replaced, and a note on this one naming the new record, `rationale` = the record's status at the base revision and the record text the change altered).

## Source
- PEP 1, § 'PEP Maintenance', python/peps `peps/pep-0001.rst` (fetched): "In general, PEPs are no longer substantially modified after they have reached the Accepted, Final, Rejected or Superseded state. Once resolution is reached, a PEP is considered a historical document rather than a living specification. Formal documentation of the expected behavior should be maintained elsewhere"; "If changes based on implementation experience and user feedback are made to Standards track PEPs while in the Provisional or (with SC approval) Accepted state, they should be noted in the PEP, such that the PEP accurately describes the implementation at the point where it is marked Final"; "Active (Informational and Process) PEPs may be updated over time to reflect changes to development practices"; header preamble: "PEPs may also have a Superseded-By header indicating that a PEP has been rendered obsolete by a later document ... The newer PEP must have a Replaces header".
- The Rust RFC process, rust-lang/rfcs `README.md` (fetched): "In general, once accepted, RFCs should not be substantially changed. Only very minor changes should be submitted as amendments. More substantial changes should be new RFCs, with a note added to the original RFC. Exactly what counts as a "very minor change" is up to the sub-team to decide".
- Google documentation guide, `docguide/best_practices.md` item 6 'Design docs, PRDs', google/styleguide (fetched): "A good design doc or PRD discusses the proposed implementation at length for the purpose of collecting feedback on that design. However, once the code is implemented, design docs should serve as archives of these decisions, not as half-correct docs (they are often misused)."
- Caveat: the two processes govern their own proposals and phrase the rule as "in general" and "should"; its reach to other decision records rests on the same accept-then-archive lifecycle.
