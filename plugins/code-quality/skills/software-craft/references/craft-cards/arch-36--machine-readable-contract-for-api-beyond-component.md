---
title: A resource-oriented HTTP API or event stream offered beyond its own functional component is declared in a machine-readable contract document under version control
rule_id: ARCH-36
domain: architecture
step: [design, implement, document]
applies_to: [service-boundary, public-api]
triggers: ['@(?:Get|Post|Put|Patch|Delete|Request)Mapping\b|@(?:GET|POST|PUT|PATCH|DELETE|Path|Get|Post|Put|Patch|Delete)\b', '\b(?:app|router|api|r|e|mux)[.](?:get|post|put|patch|delete|route|Get|Post|Put|Patch|Delete|GET|POST|PUT|PATCH|DELETE|HandleFunc|Handle)\s*\(', '@(?:app|router|bp|api)[.](?:route|get|post|put|patch|delete)\b', '\b(?:kafkaTemplate|producer|publisher|eventBus|bus)[.](?:send|publish|produce|emit|Send|Publish|Produce|Emit)\w*\s*\(', '#\[(?:get|post|put|patch|delete|route)\s*\(|(?:^\s*|\))[.]route\s*\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# A resource-oriented HTTP API or event stream offered beyond its own functional component is declared in a machine-readable contract document under version control

## Thesis
A resource-oriented HTTP API or an event stream that a service offers to consumers outside its own functional component, that is to any audience wider than component-internal, is specified in a machine-readable contract document: an OpenAPI file for the HTTP API, and a published event schema, such as AsyncAPI, JSON Schema, Protobuf or Avro, for events. The document is kept under version control. The deployment of the service that implements the HTTP API publishes its document, and an event schema is published with that deployment or registered in a schema or event-type registry that its consumers read.

## Rationale
An API is a contract with its users, who often write code against it and launch that code into production expecting it to keep working. An OpenAPI description of an HTTP API lets humans and computers discover and understand the capabilities of the service without access to its source code, other documentation or network traffic inspection; when the description is properly defined, a consumer can understand and interact with the service with a minimal amount of implementation logic. Events are part of a service's interface to the outside world, equivalent in standing to its REST API. A schema that the owning service publishes serves to automate the serialization and deserialization of events, and that approach avoids tight coupling between publishers and subscribers. Defining the API in a standard specification language outside the code is meant to facilitate early review feedback from peers and client developers, a review meant to support the development of client applications decoupled from the provider's engineering life cycle. APIs are classified by audience to facilitate differentiated standards for discoverability, changeability, and quality of design and documentation; a component-internal API is one whose consumers are restricted to applications of the same functional component, which typically represents one product whose services all belong to one dedicated owner and that owner's engineering team or teams. OpenAPI and AsyncAPI documents carry a version of their own: OpenAPI requires a document version distinct from the API implementation version, and AsyncAPI requires the version of the application API, not to be confused with the specification version.

## Example
```rust
bad:  // partner-facing route; its shape exists only in this handler's source
      router.route("/orders/{id}", get(get_order))
good: // api/orders.openapi.yaml is versioned in this repository, info.version 2.1.0
      const ORDERS_API: &str = include_str!("../api/orders.openapi.yaml");
      router.route("/orders/{id}", get(get_order))
            .route("/openapi.yaml", get(|| async { ORDERS_API }))
```

## Limits
For a component-internal API, called only by applications of the same functional component, a published contract document is optional and stays recommended. Compatibility guidance assumes an API whose producer has no control over how and when its consumers update. Where only the producer's own team writes the client code, or the deployment can enforce updates, the API's owners weigh its compatibility requirements for themselves. That narrower scope bears on which changes the document may take. The document stays required whenever a consumer sits outside the functional component. This rule asks that the contract document exists under version control and is published, with the service's deployment or, for an event schema, in a schema or event-type registry; which changes the document may take without breaking its consumers, how its version moves and how an operation is deprecated are rules of their own, and so are retries, timeouts, idempotency and delivery guarantees. A GraphQL or other RPC-style endpoint is outside this rule; the guidelines it rests on cover resource-oriented HTTP APIs and events.

## Validator
Grep the hunk for a route registration, a request-mapping annotation, or a publish or send call on a message producer. For each hit, establish the audience of the operation or event: open the service's audience declaration, its gateway or ingress configuration and the callers or subscribers that sit outside the service's functional component; an operation whose consumers are all applications of the same functional component is component-internal and passes, and a route that serves a GraphQL or other RPC-style endpoint is outside the rule and passes. For an operation or event with a wider audience, search the repository, and any contract repository or schema registry that its build or configuration references, for a contract document that declares it — an OpenAPI or AsyncAPI file, a `.proto`, an `.avsc` or a JSON Schema file — and check that the route or event type of the hit appears in it. Then check that the document reaches its consumers: the service's build or deployment serves it, ships it in the deployment artifact or registers it in an API catalogue, or, for an event, its schema is registered in a schema or event-type registry. Validator question: **does the hunk add or change an HTTP operation or event that consumers outside the service's own functional component use, while no version-controlled, machine-readable contract document that declares it is published with the service's deployment or, for an event, registered in a schema or event-type registry?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-36`, severity minor, `file`, `symbol`, `code` = the route registration, mapping annotation or publish call verbatim from the diff, `fix` = the path of the contract document with the operation or event schema it declares and, for an OpenAPI or AsyncAPI document, its `info.version` field, plus the line or build step that publishes the document, in the file's language, `rationale` = the consumers beyond the functional component that use the operation and the machine-readable contract that would let them understand the service without its source code).
