---
title: A @Transactional annotation sits on a method the proxy can intercept, never on a private method
rule_id: REL-11
domain: reliability
triggers: ['@Transactional']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A @Transactional annotation sits on a method the proxy can intercept, never on a private method

## Thesis
`@Transactional` is declared on a `public` method, or on a `protected` or package-visible method of a class proxied by a class-based (CGLIB) proxy; it is never declared on a `private` method, and on a bean proxied through its interface only `public` interface methods carry it.

## Rationale
Spring applies transaction semantics through a proxy that intercepts calls arriving from outside the bean. A private method cannot be overridden by a subclass proxy and is not part of any interface, so no proxy can intercept it: the annotation is metadata that nothing consumes, no transaction starts, and the method's writes join whatever transaction the caller had — or run in autocommit with each statement committed on its own — without a warning. As of Spring Framework 6.0, protected and package-visible methods are intercepted by class-based proxies; interface-based (JDK) proxies intercept only public methods declared on the proxied interface.

## Example
```java
bad:  @Transactional
      private void applyPayment(Payment p) { repo.save(p); ledger.post(p); }
good: @Transactional
      public void applyPayment(Payment p) { repo.save(p); ledger.post(p); }
```

## Limits
Applies to proxy mode, which is the default. A project that weaves with AspectJ (`mode = AdviceMode.ASPECTJ`), stated in the project context, intercepts private methods as well and rejects the finding. A `protected` or package-visible transactional method is correct only under a class-based proxy; when the project context states interface-based proxies or `publicMethodsOnly`, treat non-public as unintercepted.

## Validator
On the triggered hunk find each `@Transactional` on a method and read the method's modifier. Flag `private`. For `protected` or package-visible, flag when the project context states JDK (interface) proxies or `publicMethodsOnly`. Validator question: **is this transactional method one that the configured proxy cannot intercept?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-11`, severity major, `file`, `symbol`, `code` = the annotation and the method signature quoted verbatim from the diff, `fix` = the method made `public` (or moved to a public entry point of the bean), `rationale` naming the silently missing transaction).

## Source
Spring Framework reference, "Using @Transactional", note "Method visibility and @Transactional in proxy mode" — "The @Transactional annotation is typically used on methods with public visibility. As of 6.0, protected or package-visible methods can also be made transactional for class-based proxies by default. Note that transactional methods in interface-based proxies must always be public and defined in the proxied interface. For both kinds of proxies, only external method calls coming in through the proxy are intercepted"; "the mere presence of the @Transactional annotation is not enough to activate the transactional behavior".
