---
title: A change that reverses a decision an accepted record states, once any part of that decision has been implemented, adds a new record of the new decision that names the record it supersedes and marks the old record superseded
rule_id: ARCH-42
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['(?i)\bsupersed(e|es|ed|ing)\b|\breplaces\s+(ADR|RFC|record|decision)\b', '(?i)<(dependency|artifactId)>|\b(implementation|api|compileOnly|runtimeOnly)\s*[(\x22\x27]', '^\s*"(@[\w.-]+/)?[\w.-]+"\s*:\s*"(workspace:|file:|link:|npm:|[~^<>=]*\d)', '^\s*(require\s+)?[a-z0-9.-]+[.][a-z]{2,}/[\w./-]+\s+v\d', '(?i)^\s*[a-z0-9_.-]+\s*(\[[\w,\s]+\])?\s*(==|>=|~=|<=)\s*\d|\binstall_requires\b', '^\s*[\w-]+\s*=\s*(\{[^}]*\b(version|path|git)\s*=|"[~^<>=]*\d)', '^\s*import\s[^;]*\bfrom\s+[\x22\x27](@[\w.-]+/)?[a-z0-9][\w.-]*(/[\w.-]+)*[\x22\x27]|\brequire\s*\(\s*[\x22\x27](@[\w.-]+/)?[a-z0-9]']
scope: callers
check_kind: semantic
severity_default: minor
---

# A change that reverses a decision an accepted record states, once any part of that decision has been implemented, adds a new record of the new decision that names the record it supersedes and marks the old record superseded

## Thesis
Where a project keeps decision records, a change that reaches a different conclusion on a decision an accepted record states — it removes the component, framework, database or vendor the record adopted, or it adopts an option the record rejected — adds a new record when some implementation of the original decision has occurred. The new record explains the new decision with its context and rationale and names the record it replaces. The old record is marked superseded: once the new record is accepted, the old record's status — the status line, section or header field its format carries — reads superseded and links to the new record.

## Rationale
An accepted decision record remains an enduring record of the context and motivation of a past decision, which lets a team revisit that decision later and judge whether it still makes sense and whether the motivating circumstances have changed. Once an accepted decision has been implemented, its record takes only very minor amendments; a substantial change becomes a new record with a note added to the original, and the original is neither removed nor otherwise modified apart from the annotation pointing to its successor. The new record documents the context and rationale for the change, while the old one keeps the conclusion first reached. The link runs both ways: the newer record names the record it renders obsolete, and the older record names the record that replaces it.

## Example
```typescript
bad:  // decisions/0007-use-relational-store.md  Status: Accepted
      // removed by this change: import { Pool } from "pg";
      import { DocumentStore } from "document-store";
good: // decisions/0012-use-document-store.md  Status: Accepted, Supersedes 0007
      // decisions/0007-use-relational-store.md  Status: Superseded by 0012
      // removed by this change: import { Pool } from "pg";
      import { DocumentStore } from "document-store";
```

## Limits
A decision that was never implemented at all may instead be updated in its own record with the new decision, as long as the reviewers and other stakeholders agree. A clarification, or a consequence discovered during implementation, may update the existing record while its decision stands, and a very minor amendment is such an edit; what counts as very minor is for the project's reviewing team to decide. The superseded status and its link on the old record follow the new record's acceptance: while the new record is still proposed, the change carries the reference in the new record, and the old record's status changes once the new one is accepted. The rule reaches only a decision that an accepted record states, and it checks the new record and the old record's status; edits to the old record's decision text and the sections a record carries are outside it. A superseding record that an earlier change added satisfies the new-record half; once that superseding record is accepted, the change owes only the old record's superseded status.

## Validator
Grep the hunk for an added or removed dependency line in a build manifest, an added or removed package import, and an added or edited file under the project's decision-record directory (the path the project's config names, else a directory such as `docs/adr`, `doc/adr`, `docs/decisions` or `decisions`). Open the accepted records in that directory as the base revision holds them — a record counts as accepted when its status reads accepted or, where the project's records carry no status line, when the base revision holds it — and look for one whose decision adopted the component, framework, database or vendor the change removes, or rejected the option the change adopts. Open the base revision at the callers of the component the recorded decision adopted — the dependency the change removes, or the one the adopted option takes the place of — to confirm that some implementation of the recorded decision exists. Check the change and the records of the base revision for a record that names the reversed record as the one it supersedes, and, when that new record is accepted, for a superseded status linking to it in the old record's status line, section or header field. Validator question: **Does the change reverse an implemented decision that an accepted record states while no record in the change or the base revision names that record as the one it supersedes, or while that superseding record is accepted and the old record's status does not read superseded with a link to it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-42`, severity minor, `file`, `symbol`, `code` = the dependency or import line that reverses the recorded decision, verbatim from the diff, `fix` = whichever the repository lacks of the new record naming the record it supersedes and the old record's superseded status with its link, `rationale` = the accepted record whose decision the change reverses and the missing superseding record or status mark).

## Source
- The GDS Way, UK Government Digital Service, 'Documenting architecture decisions' (alphagov/gds-way, `source/standards/architecture-decisions.html.md.erb`), § Implementation and § "Superseded" status: "If there are clarifications, then updating your existing ADR may be appropriate. You might find additional consequences to your decision, so consider updating the Consequences section to reflect your evolving understanding of the problem space." … "If a decision was never implemented at all, then as long as your reviewers and other stakeholders agree then it may be appropriate to update your existing ADR with a new decision. However, if some implementation of the original decision has occurred, you should write a new ADR to explain the new decision." … "the old ADR must be clearly marked as "superseded". A "Status: superseded" line should appear directly under the heading. Add a link to the new ADR as soon as it's been accepted." (fetched)
- PEP 1, § PEP Header Preamble (python/peps, `peps/pep-0001.rst`): "PEPs may also have a Superseded-By header indicating that a PEP has been rendered obsolete by a later document; the value is the number of the PEP that replaces the current document. The newer PEP must have a Replaces header containing the number of the PEP that it rendered obsolete." (fetched)
- Rust RFC process (rust-lang/rfcs, `README.md`), § The RFC life-cycle: "In general, once accepted, RFCs should not be substantially changed. Only very minor changes should be submitted as amendments. More substantial changes should be new RFCs, with a note added to the original RFC. Exactly what counts as a "very minor change" is up to the sub-team to decide" (fetched)
- Arachne framework decision record `adr-001-use-adrs.md` (arachne-framework/architecture), § Context and § Decision, step 5: "We want to be able to revisit prior decisions to determine fairly if they still make sense, and if the motivating circumstances or conditions have changed." … "remain as an enduring record of the context and motivation of past decisions" … "If a decision is revisited and a different conclusion is reached, a new ADR should be created documenting the context and rationale for the change. The new ADR should reference the old one, and once the new one is accepted, the old one should (in its "status" section) be updated to point to the new one. The old ADR should not be removed or otherwise modified except for the annotation pointing to the new ADR." (fetched)
- Caveat: the evidence is process documentation of established projects, with no measured outcome; the implementation condition and the never-implemented exception rest on the GDS Way alone, while the Arachne record and the Rust RFC process ask for a new record on every substantial revisit of an accepted decision; the rule flags only the implemented case, on which all the sources agree.
