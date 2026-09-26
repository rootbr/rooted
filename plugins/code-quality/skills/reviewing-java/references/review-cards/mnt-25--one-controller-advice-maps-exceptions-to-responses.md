---
title: A controller does not catch exceptions to build error responses in each handler, and one @ControllerAdvice maps exceptions to responses
rule_id: MNT-25
domain: maintainability
triggers: ['@(Rest)?Controller\b', 'ResponseEntity[.](status|badRequest|notFound|internalServerError)\(', 'ResponseStatusException', '@ExceptionHandler', '@(Rest)?ControllerAdvice']
scope: file
check_kind: mechanical
severity_default: minor
---

# A controller does not catch exceptions to build error responses in each handler, and one @ControllerAdvice maps exceptions to responses

## Thesis
A `@Controller`/`@RestController` handler method lets exceptions propagate; the mapping from exception type to HTTP status and body (a `ProblemDetail`, an error DTO) is written once in `@ExceptionHandler` methods of a `@ControllerAdvice`/`@RestControllerAdvice` class, which applies to every controller; a `try`/`catch` inside a handler that returns `ResponseEntity.status(...)` for an exception repeats that mapping per method.

## Rationale
An error mapping copied into each handler drifts: one returns 404 with a body, another 400 with none, a third logs and returns 500, and a client sees three shapes for one condition. `@ExceptionHandler` methods declared in a `@ControllerAdvice` apply to any controller, match the thrown exception or a nested cause, and are the single place where status, body and logging for each exception type are decided; a handler method then contains the happy path and reads as such.

## Example
```java
bad:  @GetMapping("/{id}") ResponseEntity<Order> get(@PathVariable long id) {
          try { return ResponseEntity.ok(orders.get(id)); }
          catch (OrderNotFound e) { return ResponseEntity.status(404).build(); } }
good: @GetMapping("/{id}") Order get(@PathVariable long id) { return orders.get(id); }
      @RestControllerAdvice class ApiErrors {
          @ExceptionHandler(OrderNotFound.class) ProblemDetail notFound(OrderNotFound e) { ... } }
```

## Limits
A controller-local `@ExceptionHandler` method for an exception that only that controller raises is a documented Spring form and is not flagged. A handler that catches to add a response header or to choose between two success outcomes is not error translation. A non-Spring stack (JAX-RS `ExceptionMapper`, a servlet filter) has its own single mapping point, which the project context names.

## Validator
On the triggered hunk find each `catch` inside a controller handler method that returns a `ResponseEntity` with an error status or throws a `ResponseStatusException`. Open the file to confirm the class is a controller and the catch builds an error response. Validator question: **does this handler method translate an exception into an HTTP error response itself?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: MNT-25`, severity minor, `file`, `symbol`, `code` = the catch and the error `ResponseEntity` quoted verbatim from the diff, `fix` = the propagating handler and the `@ExceptionHandler` in a `@RestControllerAdvice`, `rationale` naming the per-handler drift of status and body).

## Source
Spring Framework reference, Web MVC → Annotated Controllers → Controller Advice — `@ExceptionHandler` methods "declared in an @ControllerAdvice or @RestControllerAdvice class … apply to any controller"; Exceptions — `@Controller` and `@ControllerAdvice` classes "can have @ExceptionHandler methods to handle exceptions from controller methods", matching "a top-level exception being propagated … or … a nested cause within a wrapper exception".
