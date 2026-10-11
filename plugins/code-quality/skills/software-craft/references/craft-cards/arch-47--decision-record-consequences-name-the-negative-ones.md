---
title: A decision record that states the consequences of its decision names the negative ones, such as what becomes harder, the qualities it compromises and the risks it introduces, as well as the positive ones
rule_id: ARCH-47
domain: architecture
step: [design, document]
applies_to: [prose]
triggers: ['(?i)^\s*#{2,4}\s+((positive|negative)\s+)?consequences\s*$', '(?i)^\s*[*-]\s+(good|bad|neutral),?\s+because\b', '(?i)^\s*[*-]?\s*[*_]{0,2}(pros?|cons?|benefits?|drawbacks?|risks?)[*_]{0,2}\s*:']
scope: file
check_kind: semantic
severity_default: suggestion
---

# A decision record that states the consequences of its decision names the negative ones, such as what becomes harder, the qualities it compromises and the risks it introduces, as well as the positive ones

## Thesis
Where a decision record that a change adds states the consequences of its decision, in a consequences section or an equivalent list, it names the negative consequences alongside the positive ones, such as what becomes more difficult to do, a desired quality the decision compromises or a risk it introduces that will need to be mitigated. A consequences section that lists only benefits falls short of the rule.

## Rationale
A decision record preserves the reasoning behind a decision so that the team can include it as context when making its own decisions about later changes. The record templates in use put the negative side in the same place as the positive one: what becomes easier or more difficult to do, a "Bad, because" item beside a "Good, because" item, both positive and negative consequences of the decision. The section names the risks the change introduces that will need to be mitigated; a section of benefits alone leaves out what becomes more difficult and those risks.

## Example
```typescript
bad:  const record = `
      ## Consequences
      * Good, because each query is visible and tunable
      * Risks: none
      `;
good: const record = `
      ## Consequences
      * Good, because each query is visible and tunable
      * Bad, because a renamed column breaks a query at run time, which integration tests catch
      `;
```

## Limits
Some record templates mark the consequences section as optional and allow it to be removed; a record that carries no consequences section and no equivalent list is outside the rule. Negative consequences written in the record's own form meet the rule, whether as "Bad, because" items, as sentences on what becomes more difficult, or as risks that will need to be mitigated. A design document or a change description that is not a decision record is outside the rule's scope.

## Validator
Grep the hunk for an added decision record: a consequences heading, "Good, because" or "Bad, because" items, or a pros, cons, benefits, drawbacks or risks label. Open the record file and read the consequences section or the equivalent list that belongs to the chosen decision. Skip a record that carries no consequences section and no equivalent list. Check each item for one that names what becomes more difficult, a quality the decision compromises, or a risk it introduces. Validator question: **Does a decision record that the change adds state the consequences of its decision while naming none that is negative, nothing that becomes more difficult, no quality compromised and no risk introduced?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-47`, severity suggestion, `file`, `symbol` = the record's title, `code` = the consequences heading and its items quoted verbatim from the diff, `fix` = the same section with the negative consequences added in the record's own format, such as what becomes more difficult, a quality compromised or a risk that will need to be mitigated, `rationale` = names that a consequences section carries both the positive and the negative consequences of the decision, and that the risks the decision introduces will need to be mitigated).

## Source
- alphagov/gds-way, `source/standards/architecture-decisions.html.md.erb`, introduction: "It is important to preserve the reasoning so the current team can include it as context when making their own decisions about changes they need to make."; § How to document decisions: "**Consequences**: both positive and negative consequences of the decision" (fetched)
- npryce/adr-tools, `src/template.md`, § Consequences: "What becomes easier or more difficult to do and any risks introduced by the change that will need to be mitigated." (fetched)
- adr/madr, `template/adr-template.md` (develop), § Consequences: "<!-- This is an optional element. Feel free to remove. --> ### Consequences * Good, because {positive consequence, e.g., improvement of one or more desired qualities, …} * Bad, because {negative consequence, e.g., compromising one or more desired qualities, …}" (fetched)
- Caveat: the sources are record templates and an engineering standard that state what a consequences section contains; none measures the effect of leaving the negative consequences out.
