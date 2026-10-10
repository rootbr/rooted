---
title: Where an unset enumeration value reads as its zero or first member, that member is an explicit unspecified value or an unused zero, unless it is the intended default
rule_id: DSN-48
domain: design
step: [design, implement]
applies_to: [universal]
triggers: ['=\s*iota\s*(?://.*)?$', '^\s*[A-Z]\w*(\s+\w+)?\s*=\s*0\s*[;,]?\s*(?://.*|#.*)?$', '\benum\s+[A-Z]\w*']
scope: hunk
check_kind: mechanical
severity_default: minor
---

# Where an unset enumeration value reads as its zero or first member, that member is an explicit unspecified value or an unused zero, unless it is the intended default

## Thesis
Where an unset value of an enumeration reads as one of its members — the member at zero where an unset variable or field holds zero, or the first member where the first is the default — that member has no meaning other than "this value was unspecified" and is distinct from every value code is expected to set. It is an explicit unspecified or unknown member; where the enumeration need not declare a member at zero, the meaningful members may instead start above zero and leave zero unnamed. The exception is a member whose meaning is the desirable default behaviour, or a clearly useful zero value: such a member may stay where the unset value reads.

## Rationale
Where a variable or field created without an explicit value holds its type's zero value, members counted from zero put the first member there, so an unset value is that member. Where a parsed message returns the default value for a field its encoded bytes do not contain, an enumeration field reads as the first member, which that schema requires to be zero. Where presence is not tracked, the zero member is synonymous with "not present" for purposes of serialization. Where a reader sets aside a value it does not recognize, a reader built before a member was added sees a field carrying the new member as unset and reads the default or the first-declared member. A domain meaning given to that member is therefore what every unset field, and on such a reader every value it did not understand, reads as. A member that means only "this value was unspecified" keeps those cases apart: when the zero value lies outside the domain's valid values, the default amounts to explicit presence, and an unset field can be told from a chosen member. Keeping that member free of domain meaning also aids the evolution of the enumeration as members are added over time.

## Example
```go
bad:  const (
          Approved Decision = iota
          Rejected
      )
good: const (
          DecisionUnspecified Decision = iota
          Approved
          Rejected
      )
```

## Limits
A zero or first member with a domain meaning is correct when that meaning is the desirable default behaviour, such as writing logs to the standard output unless another destination is chosen. A clearly useful zero value is correct as well, such as an unknown member, which is usually clearer and more useful at zero than beside a separate unspecified one. The rule does not reach an enumeration whose unset value is not one of its members. An enumeration already exchanged between separately built readers almost always keeps the member its unset value reads as: changing that member makes a reader on the old build and one on the new build see different results for the same unset value, so the rule reaches a declaration the change adds. The project context can reject the finding by stating that the member is the domain's intended default.

## Validator
In the hunk, find each added enumeration member whose value is zero, written as zero or counted from zero, and the first member of an added enumeration whose unset value reads as its first member. Read the enumeration's declaration and its comments in the hunk. Skip a member whose name or comment marks it as unspecified, unknown or unset, and a blank placeholder that leaves zero unnamed. Skip a member that the hunk moves or reformats from an existing declaration rather than adds. Skip a member whose meaning is the behaviour the domain wants when nothing was chosen, as its name, its comment or the project context shows, and a member that is a clearly useful zero value. Continue only where an unset variable or field of the type, or a message field absent from the encoded input, reads as this member; skip a type whose unset value is an absent value rather than a member. Validator question: **Does an unset value of this enumeration read as a member that carries a domain meaning other than the intended default?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-48`, severity minor, `file`, `symbol`, `code` = the member declaration at zero, or first where the first is the default, quoted verbatim from the diff, `fix` = the enumeration with an explicit unspecified member at zero, or with its meaningful members starting above zero, in the file's language, `rationale` = the domain meaning that an unset field, or a value a reader set aside as unrecognized, takes on through that member).
