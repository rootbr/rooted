---
title: Illustrative code references must use generic placeholders, not real identifiers
rule_id: R-40
applies_to_target: [context-file, skill, agent-prompt]
check_kind: semantic
severity_default: medium
---

# Illustrative code references must use generic placeholders, not real identifiers

## Thesis
When a rule, anti-pattern, or example exists to teach a pattern rather than point to one specific call site, its identifiers must be of the form `Class#method`, `<Module>.<function>`, or `<service>/<endpoint>`. Real production names (`UserService.findById`, `OrderRepo.save`, `auth_middleware.py:42`) are reserved for direct pointers to that exact location.

## Rationale
A real name couples the illustration to a single revision. A rename rots the example silently, with nothing to detect the breakage. Readers also conflate "see this for the pattern" with "this is *the* implementation," which weakens the abstraction the example is meant to teach — a pattern-versus-pointer intent collision.

## Example
```
bad:  Builder pattern: see UserService.findById()
good: Builder pattern: see Class#method

bad:  Errors: throw OrderValidationError from PlaceOrderHandler.handle
good: Errors: throw <DomainError> subclasses from <UseCaseHandler>#handle
```

## Limits
Three intents split the policy. A pattern-teaching reference must use generic placeholders. A pointer to one specific location may use the real name but must carry no line number. A quoted snippet may use real names inside the fenced block, provided the surrounding sentence names the file path. If intent is ambiguous, treat the reference as illustrative and demand placeholders.

## Validator
For each code-shaped identifier in the target file, classify intent: is it pointing to *that exact entity* (pointer) or teaching a *class of entities* (pattern)? If pattern, the identifier must be a generic placeholder. If pointer, it must carry no line numbers. Build the classification from the surrounding sentence: "see X for the pattern" reads as illustrative; "the auth retry lives in X" reads as a pointer.

## Patch output
When auditing a code-shaped reference whose intent is illustrative, emit one patch (`rule_id: R-40`, location of the reference, severity medium) replacing the real identifier with `Class#method` or a domain placeholder; set `needs_human: true` when pattern-versus-pointer intent cannot be resolved from the surrounding prose.

## Source
Authoring heuristic on pattern-versus-pointer intent; verified hands-on experience maintaining portable instruction files.
