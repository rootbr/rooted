---
title: Each major version of a service contract declares its own copies of the message and schema types it shares with other major versions and imports nothing from them
rule_id: ARCH-39
domain: architecture
step: [design, implement, review]
applies_to: [service-boundary, public-api]
triggers: ['(?:\b(?:import|include|from|require|use)\b|\$ref\b).*(?:[/.]|::)v\d+\w*(?:[/.]|::|[;"''\s]|$)|^\s*(?:\w+\s+)?"[^"\s]*/v\d+\w*(?:/[^"\s]*)?"\s*$']
scope: file
check_kind: mechanical
severity_default: minor
---

# Each major version of a service contract declares its own copies of the message and schema types it shares with other major versions and imports nothing from them

## Thesis
A major version of a service contract imports nothing from any other major version of the same contract, earlier or later. Every contract-specific message and schema type the version uses is declared in that version's own major-versioned package, and a type that is effectively the same in two major versions is declared as a separate copy in each of them.

## Rationale
A contract-specific type that several major versions share from one package adds complexity to generating and packaging the client libraries, and it is inflexible in terms of versioning. Copies made because a type starts out the same in several versions can still diverge over time, as they are isolated from each other. The versions of one contract are meant to work at the same time within a single client application for a transition period, and the older version then goes through a deprecation period before it is shut down.

## Example
```typescript
bad:  // contract/v2/order.ts
      import { LineItem } from "../v1/line-item";
      export interface Order { id: string; items: LineItem[]; }
good: // contract/v2/order.ts
      export interface LineItem { sku: string; quantity: number; }
      export interface Order { id: string; items: LineItem[]; }
```

## Limits
A generic global common type, such as a timestamp or a postal address, may be used freely by any version of any contract. An organisation-wide common type may sit in a common package and be used by the contracts of that organisation, and by no contract outside it. Such common packages carry restrictions of their own: fields should not be added to their existing messages, nor values to their existing enums. The rule asks for one copy in each major version; it asks for no copies among the files of one version. A stability channel belongs to its major version, so a reference between `v2beta1` and `v2` is outside this rule. A client application may use several major versions of one contract at the same time; the rule governs the files that declare a version. How a contract makes an incompatible change, and how an older version is deprecated and shut down, are governed separately.

## Validator
Grep the hunk for every import, include or schema reference, and for a package declaration whose name carries a major-version segment (`v1`, `v2beta1`). Open the file and read its own major version from its package declaration or its directory path as the number after `v`, so `v2beta1` belongs to major version 2. Continue only when the file declares types or operations of that major version of the contract, as a schema, an API definition or a type module. Compare the referenced path with the file's own: flag a reference to any other major version of the same contract, lower or higher, and a reference to a package of the same contract that carries no major-version segment. Leave a reference to a generic global common package, to the organisation's own common type package, or to the file's own version unflagged. Validator question: **Does a file of one major version of a contract import or reference a type from another major version of the same contract, or from a contract-specific package with no major version?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-39`, severity minor, `file`, `symbol`, `code` = the import, include or schema-reference line that reaches the other major version or the unversioned contract package, `fix` = the shared type declared in the file's own major-version package with the reference pointed at that copy, in the file's language, `rationale` = names the shared type, the two versions it couples, and that separate copies can diverge as each version evolves).
