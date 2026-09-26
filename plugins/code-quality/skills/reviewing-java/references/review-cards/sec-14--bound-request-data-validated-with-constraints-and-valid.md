---
title: A request body or parameter bound in a controller is validated with Jakarta Bean Validation constraints and a @Valid or @Validated that actually triggers them
rule_id: SEC-14
domain: security
triggers: ['@RequestBody', '@RequestParam', '@PathVariable', '@ModelAttribute|@RequestPart', '@Valid|@Validated', '@(PostMapping|PutMapping|PatchMapping|DeleteMapping)']
scope: file
check_kind: mechanical
severity_default: major
---

# A request body or parameter bound in a controller is validated with Jakarta Bean Validation constraints and a @Valid or @Validated that actually triggers them

## Thesis
A `@RequestBody`, `@ModelAttribute` or `@RequestPart` parameter whose bound type declares constraints on its fields (`@NotNull`, `@NotBlank`, `@Size`, `@Pattern`, `@Min`/`@Max`, `@Email`, nested `@Valid`) is annotated `@Valid` (or `@Validated`), so that the constraints run before the handler body. Constraints declared on a type that is bound without `@Valid` never run and are the defect.

## Rationale
Bean Validation is applied to a method argument only when it is annotated `@Valid` or `@Validated`; a DTO whose fields carry constraints but whose parameter lacks the annotation is bound and accepted as-is, so every constraint the author wrote is a comment. `@Valid` is not itself a constraint: it turns on validation of the object's nested constraints, and a constraint annotation placed directly on a parameter turns on method validation, which covers both. Client-side validation is bypassed by disabling JavaScript or using a proxy, so the server-side declaration is the one that counts. A structural constraint — length, pattern, range — bounds what later sinks receive; it complements, and does not replace, parameterized queries and output encoding at those sinks.

## Example
```java
bad:  @PostMapping("/users") public User create(@RequestBody CreateUser body) { ... }
      record CreateUser(@NotBlank @Email String email, @Size(max = 64) String name) {}
good: @PostMapping("/users") public User create(@Valid @RequestBody CreateUser body) { ... }
```

## Limits
Applies to controller and handler methods (`@RestController`, `@Controller`, `@MessageMapping`, a `HandlerFunction`). A `@RequestParam` or `@PathVariable` scalar with no constraint is not this defect — nothing declared is bypassed — and is not flagged; where a project wants a scalar constrained (`@Pattern`, `@Size`, `@Max`), the constraint runs through method validation, which Spring MVC applies on its own from Spring Framework 6.1 when a constraint annotation is declared directly on a parameter, and before 6.1 only with `@Validated` on the controller class (an AOP proxy), so a bare scalar constraint in an older project is inert without it. A parameter typed as an enum, `UUID`, `long` or `LocalDate` is constrained by its conversion. A bound type that declares no constraints at all is outside this card. Validation done explicitly by calling a `Validator` in the handler, or by a business-rule layer named in the project context, is correct. Test code is out of scope.

## Validator
On the triggered hunk find each `@RequestBody`, `@ModelAttribute` or `@RequestPart` parameter. Open the bound type in the file, or its record or class in the diff, and check for constraint annotations on its fields; then check the parameter for `@Valid` or `@Validated`. Validator question: **is there a bound parameter whose type declares constraints and that carries no `@Valid` or `@Validated`?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-14`, severity major, `file`, `symbol`, `code` = the parameter declaration quoted verbatim from the diff, `fix` = the parameter with `@Valid`, `rationale` naming the constraints that never run).

## Source
Spring Framework reference, Web MVC "Validation" — Bean Validation "is applied individually to an @ModelAttribute, @RequestBody, and @RequestPart method parameter annotated with @jakarta.validation.Valid or Spring's @Validated"; method validation applies "when @Constraint annotations such as @Min, @NotBlank and others are declared directly on method parameters"; "@Valid is not a constraint annotation... by itself @Valid does not lead to method validation"; NOTE — with a class-level `@Validated`, method validation "is applied through an AOP proxy", as against "the Spring MVC built-in support for method validation added in Spring Framework 6.1". OWASP Bean Validation Cheat Sheet — add constraints to the model "and then utilize the @Valid annotation when passing your model around". OWASP Input Validation Cheat Sheet — "Input validation must be implemented on the server-side". OWASP ASVS 5.0 requirement 2.2.1.
