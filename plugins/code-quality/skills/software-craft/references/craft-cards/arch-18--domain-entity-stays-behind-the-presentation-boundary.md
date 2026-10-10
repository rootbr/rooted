---
title: In a component the project declares as a DDD domain model layer, a domain entity is not returned in a response, handed to a view or bound from client input by a client-facing handler, which receives and sends a view model or DTO that the application translates from and to the entity
rule_id: ARCH-18
domain: architecture
step: [design, implement, review]
applies_to: [service-boundary]
triggers: ['@(RestController|Controller|RequestBody|ResponseBody|GetMapping|PostMapping|PutMapping|PatchMapping|ModelAttribute)\b', '\[(ApiController|HttpGet|HttpPost|HttpPut|HttpPatch|FromBody|FromForm)\b', '\b(ResponseEntity|ActionResult|IActionResult|JsonResponse|HttpResponse)\b|\breturn\s+(Ok|Json|View|PartialView|Created\w*)\(', '\brender\s+json:|\bjsonify\(|\bres[.](status\([\w.]+\)[.])?(json|send|render)\(|\bc[.](JSON|Bind\w*|ShouldBind\w*)\(|\bjson[.]New(En|De)coder\([\w.]+\)[.](En|De)code\(', '\b\w+(ViewModel|Dto|DTO)\b', '@\w+[.](get|post|put|patch|delete|route)\(|@(Get|Post|Put|Patch|Delete|Body|Query|Param)\(|@(GET|POST|PUT|PATCH|DELETE)\b|\bJson(<\w+>|\()', '\b(app|router)[.](get|post|put|patch|delete)\(|\breturn\s+render\(|\brender_template\(|[.](addAttribute|addObject)\(']
scope: file
check_kind: semantic
severity_default: minor
---

# In a component the project declares as a DDD domain model layer, a domain entity is not returned in a response, handed to a view or bound from client input by a client-facing handler, which receives and sends a view model or DTO that the application translates from and to the entity

## Thesis
Where the project declares a component as a DDD domain model layer, a domain entity of that component does not cross into the responses, views or client-input bindings of a client-facing handler, whichever layer the project assigns that handler to. That handler receives and sends a view model or data transfer object, a data model for presentation needs only, and the application translates between that model and the entity in both directions.

## Rationale
The domain model layer and the presentation layer might have different types, and those types mandate a translation between them. Part of an entity's information, or an aggregation of it with data from other entities, can be sent to the client. Entities need to stay always valid under the control of their aggregate roots, while data at the presentation level might still not be validated; that gap is the reason an entity is not bound to a client view and a view model carries the data instead. A transfer object lets the data sent to the client change shape, to hide properties clients are not supposed to view, to avoid over-posting or to decouple the service layer from the database layer; an exposed database entity instead gives the client data that maps directly to the database tables. A domain entity is generally not safe for web binding because it likely contains more properties than the expected input, while a dedicated input object constrains binding to the expected input and holds only the fields the caller may edit.

## Example
```java
bad:  @PostMapping("/orders")
      Order create(@RequestBody Order order) { return orders.save(order); }
good: record NewOrder(String item, int quantity) {}
      record OrderView(long id, String status) {}
      @PostMapping("/orders")
      OrderView create(@RequestBody NewOrder in) {
          Order o = orders.place(in.item(), in.quantity());
          return new OrderView(o.id(), o.status());
      }
```

## Limits
The guidance this rule rests on describes the layering for applications with significant business and technical complexity, applies DDD approaches only to complex microservices with significant business rules, and leaves a simpler responsibility, such as a CRUD service, to simpler approaches. The case is contested. In a conventional framework-native application the framework's own guide has the controller make model data available to the view and save or update model data from user input, with each attribute explicitly permitted before mass assignment. What separates the two cases is the project's declaration of a DDD domain model layer; a component without that declaration, including one that a framework convention or generator only names domain, is outside this rule. For the security of inbound binding, the framework reference and the mass-assignment guidance accept an explicit allow-list of the fields bindable on an object with additional properties as the alternative to a dedicated input object; which fields input may set is an input-security question judged apart from this rule. This rule judges only which type crosses the boundary between the declared domain model layer and its client-facing handlers.

## Validator
Grep the hunk for a client-facing handler, whichever layer the project assigns it to: a controller or route annotation, attribute or registration call, a request-body or form binding, a response builder, a view render call or a write into a view's model. Open the file and, for each handler the hunk touches, name the declared type of what it returns or writes into a response, what it hands to a view or template model, and what it binds from the request body, form or query. Count a collection, an optional or a response wrapper by its element type. Trace each named type to its declaration, then open the project's declaration of layers — an architecture document or decision record, an architecture test or an import contract that declares the component a DDD domain model layer in those terms; a package, module or test layer that is only named domain or model is not such a declaration; where the project declares no DDD domain model layer, stop with no finding. Validator question: **Does a client-facing handler in this file return, render or bind an entity — a type with identity, such as an aggregate root — of the component the project declares as its DDD domain model layer?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-18`, severity minor, `file`, `symbol`, `code` = the handler signature or statement that returns, renders or binds the entity type, quoted verbatim from the diff, `fix` = a view model or input record carrying only the presentation fields, with the translation from and to the entity, in the file's language, `rationale` = names the entity, the declared domain model layer it belongs to, and the direction that crosses the boundary — response, view or input binding).
