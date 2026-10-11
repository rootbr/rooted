---
title: Functions that change for the same requirement are deployed in the same service, so that a change made for one requirement does not have to edit and redeploy two or more separately deployed services in step
rule_id: ARCH-35
domain: architecture
step: [design, review]
applies_to: [service-boundary]
triggers: ['\b(?:class|record|struct|interface|type|message)\s+\w*(?:Dto|DTO|Request|Response|Event|Message|Payload)\b']
scope: callers
check_kind: semantic
severity_default: minor
---

# Functions that change for the same requirement are deployed in the same service, so that a change made for one requirement does not have to edit and redeploy two or more separately deployed services in step

## Thesis
Functions that are likely to change together, for the same requirement, are packaged and deployed together in one service. A change made for one requirement that adds, copies or alters the same rule or calculation in two or more separately deployed services, so that those services have to be deployed in step, shows such functions split across a service boundary.

## Rationale
When functions that change together reside in separate services, those services are tightly coupled, because a change in one service requires updating the other. A change that affects several services cannot be implemented and deployed atomically; it has to be planned across each service's own release schedule. Reasoning about the interactions between every deployed version of every service is extremely challenging: in a case study of over 100 catastrophic upgrade failures of eight widely used distributed systems, two-thirds were caused by the interactions between multiple versions of a system. Overly chatty communication between two services might be a symptom of the same tight coupling and low cohesion. Placing the functions in one service gives that service high functional cohesion and keeps it loosely coupled to the other services.

## Example
```go
bad:  // billing service: Discount added to the event and to the total
      type OrderPricedEvent struct{ OrderID string; Net, Discount int }
      // shipping service: the same rule added and redeployed in step
      func insuredValue(e OrderPricedEvent) int { return e.Net - e.Discount }
good: // billing service owns the rule and publishes its result
      type OrderPricedEvent struct{ OrderID string; Total int }
      func total(net, discount int) int { return net - discount }
      // shipping service reads the published result
      func insuredValue(e OrderPricedEvent) int { return e.Total }
```

## Limits
A provider that adds new, backward-compatible functionality to its published contract releases it compatible with existing dependent software, and a consumer that starts to read the addition as published depends on the version that introduced it; when the consumer applies no rule or calculation the provider also applies, the two edits together are new functionality across a contract, not a split. The rule judges how deployable units are decomposed; the placement of authentication and transport security, retries, timeouts, idempotency and messaging guarantees across a boundary, and the evolution and deprecation of a published contract are judged by their own rules.

## Validator
List the separately deployed services the diff touches, by build unit, deployment manifest or top-level service directory, and stop when it touches one. Grep each service's hunk for message, event, request, response and payload types and for schema field declarations; open the callers of each changed type or field in every touched service. Trace whether the edits in two or more services serve one requirement: the same rule or calculation added, copied or altered in each, with any field added only to carry its inputs, so that deploying one service without the others leaves the behaviour wrong or inconsistent. Set aside a dependency version bump repeated across services, authentication, transport-security or resiliency code repeated across services, and a published contract field that the provider adds, renames, retypes or removes and a consumer follows without re-applying a rule or calculation the provider applies. Validator question: **Does this change add, copy or alter the same rule or calculation for one requirement in two or more separately deployed services that have to be deployed in step?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-35`, severity minor, `file`, `symbol`, `code` = the matching rule or calculation quoted verbatim from each service's hunk, `fix` = the function moved into the one service that owns the requirement, with its result published in that service's contract for the others to read, in the file's language, `rationale` = names the services edited in step, the one requirement behind the edits and the coordinated release it forces).

## Source
- Azure Architecture Center, 'Microservices architecture style', § Best practices (fetched): "Services should have loose coupling and high functional cohesion. Functions that are likely to change together should be packaged and deployed together. If they reside in separate services, those services end up being tightly coupled, because a change in one service requires updating the other service. Overly chatty communication between two services might be a symptom of tight coupling and low cohesion."
- doi:10.1145/3593856.3595909, §1, challenges C2 and C5 (fetched): "When making changes that affect multiple microservices, developers cannot implement and deploy the changes atomically. They have to carefully plan how to introduce the change across n microservices with their own release schedules." · "It is extremely challenging to reason about the interactions between every deployed version of every microservice. In a case study of over 100 catastrophic failures of eight widely used systems, two-thirds of failures were caused by the interactions between multiple versions of a system." The failure figure is the paper's citation (its ref. 78) of a separate study, 'Understanding and detecting software upgrade failures in distributed systems', SOSP 2021.
- Semantic Versioning 2.0.0, semver.md (fetched): "backward compatible API additions/changes increment the minor version" · "Since Firetruck uses some functionality that was first introduced in 3.1.0, you can safely specify the Ladder dependency as greater than or equal to 3.1.0 but less than 4.0.0. Now, when Ladder version 3.1.1 and 3.2.0 become available, you can release them to your package management system and know that they will be compatible with existing dependent software." Stated for a package's public API; the card applies it to a service's published contract.
