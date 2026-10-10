---
title: A service registered as a singleton takes no scoped service as a dependency, and no scoped service is resolved from the root container, since either one stretches the scoped service's lifetime to the whole application
rule_id: ARCH-30
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['(?i)(?:[.]\s*(?:try_?)?add_?singleton\s*[<(]|@singleton\b|[.]\s*in\s*\(\s*(?:singleton[.]class|scopes[.]singleton)\b)', '(?i)(?:[.]\s*(?:try_?)?add_?scoped\s*[<(]|@(?:request|session)_?scoped?\b|[.]\s*in\s*\(\s*(?:request|session)_?scoped[.]class\b|\bservlet_?scopes\s*[.]\s*(?:request|session)\b|\bscope_(?:request|session)\b|@scope\s*\(\s*(?:value\s*=\s*)?"(?:request|session)")', '(?i)\bvalidate_?scopes\s*[:=]\s*false\b', '(?i)\b(?:root_?(?:provider|container|scope|services?)|app[.]services)\s*[.]\s*(?:get_?(?:required_?)?service|resolve)\s*[<(]']
scope: callers
check_kind: semantic
severity_default: major
---

# A service registered as a singleton takes no scoped service as a dependency, and no scoped service is resolved from the root container, since either one stretches the scoped service's lifetime to the whole application

## Thesis
A service registered with the singleton lifetime keeps no scoped service for its own lifetime: it obtains one on each use, either from an explicit scope it creates, uses and disposes, or through an injected provider or proxy that resolves the service from the scope active for the current unit of work, such as a per-request scope. Every other resolution of a scoped service happens within a scope, either an implicit one such as a per-request scope or an explicit one, rather than from the root provider. Where the container offers scope validation, which checks that scoped services are neither injected into singletons nor resolved from the root provider, it is enabled.

## Rationale
A singleton is instantiated once and holds a scoped dependency it receives for its own lifetime, which is longer than the intended scoped lifetime of that dependency. Requesting the scoped service from the root provider inside the singleton has the same effect: the scoped service behaves like a singleton, which can lead to incorrect state when processing subsequent requests. A scoped service is disposed by the container that created it, so one created in the root container is disposed only when the application shuts down, and its lifetime is effectively promoted to singleton. Used as registered, a scoped service in a web application is created once per client request and disposed at the end of the request. A provider produces the value on demand, and a scoped proxy retrieves the real target from the relevant scope, such as the current request, on each call, so either one lets a singleton use a scoped service safely. Scope validation makes the container raise an error in both situations.

## Example
```python
bad:  services.add_scoped(DbSession)
      services.add_singleton(ReportCache)  # ReportCache(session: DbSession)
      root_provider = services.build_provider(validate_scopes=False)
      session = root_provider.resolve(DbSession)
good: services.add_scoped(DbSession)
      services.add_singleton(ReportCache)  # ReportCache(scopes: ScopeFactory)
      def refresh(self):  # on ReportCache, once per unit of work
          with self.scopes.create_scope() as scope:
              scope.resolve(DbSession).reload()
```

## Limits
A background worker or other singleton that needs a scoped service takes a scope factory, creates a scope, resolves the service from that scope, and disposes the scope when it is no longer needed; that resolution is an accepted form. In a container whose scope follows the current unit of work, a singleton may also take a provider or a proxy of the scoped service that resolves it from that scope on each call and keeps no resolved instance; that form is accepted as well. A proxy that the container injects for the scoped service counts as well, whether the scoped service's own registration declares it or the container proxies every reference to a service of that scope, so the walk reads that registration and the container's proxy rule for the scope before it flags a constructor parameter. These lifetime directions are fine: a scoped or transient service may depend on a singleton, and a scoped service may be resolved from another scoped service, or from a transient service that is itself resolved within a scope.

## Validator
Grep the hunk for singleton and scoped registrations, for resolutions called on a provider, and for an option that sets scope validation to false. For each singleton registration in the hunk or among the callers of a changed registration, open the implementation and list its constructor parameters and every provider call in its body, then look up the registered lifetime of each type it receives or requests, and for each transient one repeat the walk through that type's own constructor parameters, since a scoped service reached through a transient is held for the singleton's lifetime as well. For each scoped registration the hunk adds or changes, find the singletons registered elsewhere that receive or request the registered type, directly or through a transient, and walk each of them the same way. For each resolution of a scoped service, or of a transient service whose constructor chain reaches a scoped one, trace the provider it is called on back to its origin: a scope created around the unit of work, an implicit per-request scope, or the root provider built at startup. Validator question: **Does a singleton hold a scoped service it received at construction, directly or through a transient, or request one outside both an explicit scope it creates and the scope active for the current unit of work, does code resolve a scoped service from the root provider, or does the change switch scope validation off?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-30`, severity major, `file`, `symbol`, `code` = the singleton's registration with the constructor parameter or provider call that takes the scoped service, the root-provider resolution, or the line that disables scope validation, `fix` = the singleton taking a scope factory and resolving the scoped service inside a scope it creates and disposes per unit of work, or a provider or proxy that resolves it from the active scope on each call, or scope validation left enabled, in the file's language, `rationale` = the singleton and scoped lifetime pair and the state carried across units of work or the disposal deferred to application shutdown).
