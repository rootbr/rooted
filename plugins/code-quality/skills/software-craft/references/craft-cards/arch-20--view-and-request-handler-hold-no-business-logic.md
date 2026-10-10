---
title: A view paired with a view model or calling a model or a service, or a request handler, holds no business logic, a view paired with a view model keeping only display logic and a request handler only validating the request, calling the model or service that performs the business operation and choosing the response
rule_id: ARCH-20
domain: architecture
step: [design, implement, refactor, review]
applies_to: [universal]
triggers: ['\bclass\s+\w+(Controller|View|Widget|Page|Screen|Activity|Fragment|Component)\b', '(\bextends|:|<|\()\s*(StatelessWidget|StatefulWidget|State<|Controller|ControllerBase|ApplicationController|APIView|TemplateView|React[.]Component)\b', '^\s*@(Controller|RestController|Composable)\b|^\s*\[(ApiController|Route)\b|^\s*#\[(get|post|put|patch|delete|route)\s*\(', '\bdef\s+(get|post|put|patch|delete)\s*\(\s*self\s*,\s*request\b|\bWidget\s+build\s*\(\s*BuildContext\b', '\b(app|router|fastify)[.](get|post|put|patch|delete|route)\s*\(|\bhttp[.]ResponseWriter\b|\bfunction\s+[A-Z]\w*\s*\(|^\s*@(Component|Get|Post|Put|Patch|Delete)\s*\(|^\s*@(Get|Post|Put|Patch|Delete|Request)Mapping\b|^\s*\[Http(Get|Post|Put|Patch|Delete)\b', 'signal:long_routine']
scope: file
check_kind: semantic
severity_default: minor
---

# A view paired with a view model or calling a model or a service, or a request handler, holds no business logic, a view paired with a view model keeping only display logic and a request handler only validating the request, calling the model or service that performs the business operation and choosing the response

## Thesis
Where a view, meaning a UI widget, component, page or screen, is paired with a view model or calls a model or a service, it holds no business logic: it decides no pricing, eligibility, limit or state-transition rule and leaves that rule to the view model, model or service. Where the UI pairs each view with a view model, the view is passed all the data it renders from that view model and keeps only showing or hiding elements on a flag or a nullable field of the view model, animation, layout based on device information such as screen size or orientation, and simple routing; all other logic related to data sits in the view model. A request handler, meaning a web controller or one of its actions, is a UI-level abstraction. It ensures the request data is valid, maps the request to a business operation that a model or service performs, and maps that operation's result to the view or result it returns. The business decision itself is made in the model or the service.

## Rationale
As an application is modified and grows in size and scope, tight coupling between UI controls and business logic raises the cost of changing the UI and makes that code hard to unit test. With the data logic in a view model, tests can exercise the UI logic without the widgets, covering exactly the functionality the view uses, and the UI layer can maintain its state across configuration changes such as a screen rotation. The layers then hold separate concerns: the view holds the UI and UI logic, the view model holds presentation logic and state, and the model holds the business logic and data. A request handler is a UI-level abstraction as well. Its own responsibilities are to ensure the request data is valid and to choose the view or result returned, and the business concern it maps the request to is typically a service it reaches through dependency injection.

## Example
```typescript
bad:  class OrderController { constructor(private store: OrderStore) {}
        async create(req: OrderRequest): Promise<Reply> {
          const total = req.items.reduce((sum, i) => sum + i.price * i.qty, 0);
          const discount = total > 1000 ? 0.05 : 0;
          return created(await this.store.save({ ...req, total, discount })); } }
good: class OrderController {
        constructor(private orders: OrderService) {}
        async create(req: OrderRequest): Promise<Reply> {
          if (!isValid(req)) return badRequest(req);
          return created(await this.orders.place(req)); } }
```

## Limits
Display logic in a view passes: showing or hiding an element, animation, layout based on device information and simple routing. UI logic that implements visual behaviour difficult to express in declarative layout markup, such as an animation, may sit in the view's own code. Logic in the view model passes as well: retrieving data from repositories and filtering, sorting or aggregating it for display, keeping the state the view needs to rebuild, and exposing the commands that the view's event handlers call. Where the UI has no view-model layer and its framework's guidance derives display values in the component during rendering, that derivation passes: formatting a value, or filtering and sorting a list for display. The same guidance places the next-state computation in the component's own event handler, a limit or state-transition rule over the component's own state included, so a component that keeps its own state and calls no view model, model or service passes. A component that calls a model or a service and also computes a business rule itself fails. Where data access sits differs by framework. One framework's guidance has the handler delegate data access to services too, while another framework's conventional handler fetches or saves data through the model, which is the layer responsible for data and business logic. A handler that loads or saves through a model or a service and decides no business rule therefore passes. A range or limit check on a request field passes when a validation attribute, schema or validator declared on the request or model type holds it and the handler checks only its result. The same check coded inline in the handler is a limit rule computed there: model validation reports a value outside a field's expected range as data that does not conform to business rules. An authentication or authorization check in a handler or in its request filter is security design, which this rule does not judge. The rule judges the views and handlers of one file. An import of a framework, persistence or vendor type into domain code, the translation of a foreign model into domain types at a boundary, and an interface declared by its consumer are module-level neighbours that this rule does not judge.

## Validator
Grep the hunk for a view or request-handler declaration: a class named as a controller, view, widget, page, screen or component, a handler decorator or attribute, a route registration or a routine taking the response writer, a component function, a widget build routine, or a long routine inside one. Open the file and read each handler action and each view's build or render routine. In a view paired with a view model or calling a model or a service, list each business rule it applies: a pricing, eligibility, limit or state-transition rule. Where the view is paired with a view model, also list the logic beyond showing or hiding on a flag or nullable field, animation, device-based layout and simple routing: computing, filtering, sorting or aggregating data. In a handler, list the logic beyond validating the request, checking access, calling a model or service and mapping its result to a response: a pricing, eligibility, limit or state-transition rule computed inline, a range or limit check coded inline on a request field included. Trace each listed computation one call deep and drop it when it is a call into a view model, model or service method that holds the rule. Validator question: **Does a request handler, or a view paired with a view model or calling a model or a service, decide a business rule itself, or does a view paired with a view model compute data that its view model should supply?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-20`, severity minor, `file`, `symbol`, `code` = the lines of the view or handler that compute data or decide the business rule, `fix` = the view reduced to display logic or the handler reduced to validate, delegate and respond, with the rule moved into a view model, model or service method, in the file's language, `rationale` = names the view or handler holding the logic, the UI-level role that makes it the wrong home, and the view model, model or service that takes the rule).
