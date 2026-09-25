---
title: A @Transactional method is invoked through the bean's proxy, never by self-invocation through this
rule_id: REL-12
domain: reliability
triggers: ['@Transactional', 'this[.]\w+\(', '@Async', '@Cacheable', '@Retryable']
scope: file
check_kind: semantic
severity_default: major
---

# A @Transactional method is invoked through the bean's proxy, never by self-invocation through this

## Thesis
A method annotated `@Transactional` (or another proxy-applied annotation such as `@Async`, `@Cacheable`, `@Retryable`) is reached only through a reference to the bean's proxy: from another bean, or through an injected self-reference. A call from another method of the same class — `this.save(o)` or the implicit `save(o)` — bypasses the proxy and the annotation has no effect on that call.

## Rationale
The client holds the proxy and calls go through it; once a call has reached the target object, "any method calls that it may make on itself, such as this.bar() or this.foo(), are going to be invoked against the this reference, and not the proxy", so "self invocation via an explicit or implicit this reference will bypass the advice". For `@Transactional` this means no transaction starts for the inner call: its writes run in the caller's transaction if one exists, or in autocommit otherwise, and `REQUIRES_NEW`, `readOnly` and rollback rules declared on the inner method are ignored. The code appears to work until a rollback scenario is tested.

## Example
```java
bad:  public void handle(Order o) { validate(o); save(o); }        // no transaction on handle
      @Transactional public void save(Order o) { repo.save(o); audit.record(o); }
good: public void handle(Order o) { validate(o); self.save(o); }   // self: injected proxy
      @Transactional public void save(Order o) { repo.save(o); audit.record(o); }
```

## Limits
A self-call from a method that is itself `@Transactional` with the same propagation and rollback rules behaves as intended, because the outer call already opened the transaction; flag only when the inner annotation would change the outcome (a non-transactional caller, `REQUIRES_NEW`, `NOT_SUPPORTED`, a different `rollbackFor`, `readOnly`). AspectJ weaving mode, stated in the project context, has no proxy and rejects the finding. Splitting the inner method into a second bean is an equally correct fix.

## Validator
On the triggered hunk find each call to a method of the same class (explicit `this.` or unqualified) and open the file to read whether the callee carries `@Transactional`, `@Async`, `@Cacheable`, `@Retryable` or another proxy-applied annotation. Check whether the caller is annotated with the same semantics or whether the call goes through an injected self-reference or `AopContext.currentProxy()`. Validator question: **does this self-invocation reach an annotated method whose annotation would change the behaviour if a proxy applied it?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-12`, severity major, `file`, `symbol`, `code` = the self-call and the callee's annotation quoted verbatim from the diff, `fix` = the call through an injected self-reference or the method moved to another bean, `rationale` naming the bypassed proxy and the missing transaction).

## Source
Spring Framework reference, "Proxying Mechanisms" ("Understanding AOP Proxies") — "any method calls that it may make on itself, such as this.bar() or this.foo(), are going to be invoked against the this reference, and not the proxy ... self invocation via an explicit or implicit this reference will bypass the advice"; the options "Avoid self invocation", "Inject a self reference", `AopContext.currentProxy()`. Spring Framework reference, "Using @Transactional" — "self-invocation ... does not lead to an actual transaction at runtime even if the invoked method is marked with @Transactional".
