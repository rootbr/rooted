---
title: A contract document between separately deployed services is guarded by an automated check that runs before deployment and stops a change that can break a consumer, such as a comparison against its previous version or a contract test run on both consumer and provider
rule_id: ARCH-37
domain: architecture
step: [test, review]
applies_to: [service-boundary, build-config]
triggers: ['\b(openapi|swagger|asyncapi)[.](ya?ml|json)\b|^\s*["'']?openapi["'']?\s*:\s*["'']?3|^\s*["'']?swagger["'']?\s*:\s*["'']?2|^\s*["'']?asyncapi["'']?\s*:|^\s*syntax\s*=\s*["'']proto[23]["'']|"\$schema"\s*:\s*"https?://json-schema[.]org|^\s*["'']?(operationId|requestBody|\$ref)["'']?\s*:|^\s*(rpc\s+\w+\s*\(|(message|service)\s+[A-Z]\w*\s*\{|(repeated|optional)\s+[\w.]+\s+\w+\s*=\s*\d+|(string|bytes|u?int(32|64)|sint(32|64)|s?fixed(32|64))\s+\w+\s*=\s*\d+\s*[;\[])']
scope: callers
check_kind: semantic
severity_default: minor
---

# A contract document between separately deployed services is guarded by an automated check that runs before deployment and stops a change that can break a consumer, such as a comparison against its previous version or a contract test run on both consumer and provider

## Thesis
A contract document that describes the messages between separately deployed applications, such as an API description or a protocol definition, is guarded by an automated check that runs before deployment and stops it when a change can break a consumer. Two forms of the check are common. One compares each change to the document against its previous version and fails when a consumer that followed the old contract can stop working under the new one. The other is a contract test: the consumer's automated tests record the expectations it has of the provider, and a provider-side run verifies those recorded expectations against the provider. Documenting the boundary and sharing the document with consumer teams does not by itself stop integration bugs from happening.

## Rationale
An API description declares which requests and responses are valid, but most servers do not enforce it at runtime, and a server may quietly accept a request the contract says is invalid. Other consumers of the same contract do enforce it: gateways and validators reject non-conforming requests, and client SDKs generated from the contract turn it into typed code that no longer compiles. The server's leniency therefore does not mean the contract is unchanged. In a binary protocol definition, compatibility is also not one thing: renaming a field can break generated source code while preserving the wire format, whereas changing a field from a 32-bit integer to a string breaks every existing serialized message, and a comparison check can make that distinction explicit with a rule category for each level. Without contract testing, the only way to ensure that two applications work together is an integration test, which is expensive and brittle; a contract test checks each application in isolation against the shared contract.

## Example
```java
bad:  void release(Pipeline pipeline) {
          pipeline.publish(Path.of("api/openapi.yaml"));
          pipeline.deploy();
      }
good: void release(Pipeline pipeline) {
          pipeline.failOnBreakingChange(Path.of("api/openapi.yaml"), pipeline.lastRelease());
          pipeline.publish(Path.of("api/openapi.yaml"));
          pipeline.deploy();
      }
```

## Limits
The comparison against the previous version guards one condition: that a consumer written against the old document keeps working under the new one. It judges the document and not the deployed provider, which may accept what the document declares invalid, so a provider that changes its behaviour while the document stays the same passes it. Using the document as a contract before deployment also needs automated assurance that the document accurately represents the provider, error responses and polymorphic payloads included; that consumers send only requests and expect only responses the document allows; that changes to the document propagate to consumers automatically; and that deployments only ever place compatible versions in one environment. A check that the provider's behaviour conforms to its own document keeps code and documentation in sync, yet on its own gives no assurance that consumers call the provider correctly or that the provider meets all their expectations, so it prevents integration bugs less well than a contract test that involves the consumer. A contract test covers only the parts of the communication that current consumers use, and provider behaviour no current consumer uses stays free to change; a check against the published document serves external clients, and combining the two gives confidence both that the API meets its published document and that the known consumers' requirements are satisfied. Where the document does not hold enough information to decide whether a change breaks consumers, such as an object parameter whose serialization it leaves unspecified, a comparison tool can report the change as a warning rather than an error, and the project chooses whether a warning fails the run. Which changes count as breaking, how a breaking change is versioned and how an old version is deprecated belong to the rules on API evolution; delivery mechanics between services, such as retries, timeouts, idempotency and messaging guarantees, stay outside this rule.

## Validator
In the hunk, find a contract document that is added or changed (an API description, an event or message schema, a protocol definition) or a build or deployment step that publishes one. Open the callers at scope: the build, test and deployment pipeline definitions of the provider and, where the repository holds them, of its consumers. Trace the steps that run before the deployment step and look for a check whose failure stops the run when a change can break a consumer, such as a comparison of the document against its previous version (its version on the main branch in a run before merge, its last release in a run on the main branch) that fails on a breaking change, or a contract test whose consumer-side run records expectations that a provider-side run verifies. A check that only reports, a check that runs after deployment, and a check of the provider against its own document alone do not count; the last keeps code and document in sync, yet on its own gives no assurance that consumers call the provider correctly or that the provider meets all their expectations. Validator question: **Does a contract document crossing a boundary between separately deployed applications reach deployment without an automated pre-deployment check whose failure stops the deployment when a change can break a consumer?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-37`, severity minor, `file`, `symbol`, `code` = the line that adds or changes the contract document, or the pipeline step that publishes or deploys it, `fix` = a pipeline step placed before deployment that compares the document against its last released version and fails on a breaking change, or that runs the consumers' contract tests against the provider, `rationale` = names that sharing a document does not stop integration bugs and that a consumer which followed the old contract can stop working under the new one).
