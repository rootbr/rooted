---
title: A process builds its dependency-injection container once in its composition root, and no other code, registration code included, builds a second container from the application's registrations to resolve a service
rule_id: ARCH-23
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['\b(?:BuildServiceProvider|build_(?:service_)?provider)\s*\(', '\bGuice\s*[.]\s*createInjector\s*\(', '\b(?:new\s+)?(?:AnnotationConfig|ClassPathXml|FileSystemXml|Generic|Static)\w*ApplicationContext\s*\(', '\bDagger\w+\s*[.]\s*(?:create|builder|factory)\s*\(', '\b(?:fx|dig)\s*[.]\s*New\s*\(', '\b(?:new\s+)?(?:ServiceCollection|ContainerBuilder|Container|Injector)\s*\(|\bcontainers\s*[.]\s*DeclarativeContainer\b']
scope: callers
check_kind: semantic
severity_default: major
---

# A process builds its dependency-injection container once in its composition root, and no other code, registration code included, builds a second container from the application's registrations to resolve a service

## Thesis
A process builds its dependency-injection container from the application's registrations exactly once: in the composition root, the start-up code at the process entry point that wires implementation types to interfaces, or in the framework host that receives those registrations from it. Registration code that needs one service to construct another receives it through a registration whose factory the container calls with that service or with its provider, and builds no container of its own to resolve it.

## Rationale
A container keeps one instance of each singleton registration for its own lifetime, so the singleton guarantee holds per container and per registration. A second container built from the same registrations therefore creates a second copy of the singleton services, which might make the application behave incorrectly. Where a framework host builds the container from the registrations it receives, a build call in the application's own start-up code is already the second one. The extra build typically comes from code that wants to resolve one service while registering another, and a registration whose factory receives that service or the container's provider resolves it from the one container. Wiring implementation types to interfaces in one place at start-up is what lets dependency injection work properly at run time.

## Example
```rust
bad:  fn register(services: &mut Services) {
          let cache = services.build_provider().get::<Cache>();
          services.add_singleton(move |_| Repo::new(cache.clone()));
      }
good: fn register(services: &mut Services) {
          services.add_singleton(|provider| Repo::new(provider.get::<Cache>()));
      }
      fn main() { let mut services = Services::new(); register(&mut services);
                  services.build_provider().get::<Repo>().run(); }
```

## Limits
A container derived from the root is outside the rule: a child injector inherits all bindings, scopes, interceptors and type converters of its parent; a subcomponent inherits and extends its parent component's object graph to partition it or to use more than one scope; and a scope created through the container's scope factory serves services through its own provider for a limited lifetime. A test may build its own component to instantiate the objects it exercises, whether a larger component shared by many tests or a small one focused on a single test. Where removing an extra build from start-up code is non-trivial, a team may keep it and suppress the finding once thorough testing shows that it adds no second copy of a singleton service.

## Validator
Grep the hunk for a container build: a provider build call, an injector creation, an application-context constructor, a generated component's factory or builder, and a new registration collection or container builder. For each hit, open the enclosing routine and its callers up to the process entry point, and classify the build: the composition root's one build or its hand-off to a framework host; a child container, subcomponent or scope derived from an existing container; a component a test builds for itself; or a build from the application's registrations inside registration code, a module, a start-up hook the framework host calls, a request path or a library. Trace whether the same registrations already reach a container that the composition root or the framework host builds. Validator question: **does this code build a container from the application's registrations, beside the one the composition root or the framework host already builds from them, to resolve a service?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-23`, severity major, `file`, `symbol`, `code` = the second build call and the service resolution it feeds, quoted verbatim from the diff, `fix` = the registration rewritten to a factory that receives the service or the container's provider, or the service passed in from the composition root, in the file's language, `rationale` = each container keeps its own instance of every singleton, so the second build creates a second copy of the singleton services, which might make the application behave incorrectly).

## Source
- ASP.NET Core analyzer rule ASP0000, dotnet/AspNetCore.Docs `aspnetcore/diagnostics/asp0000.md` § Rule description: "Calling 'BuildServiceProvider' from application code results in more than one copy of singleton services being created which might result in incorrect application behavior. Consider alternatives such as dependency injecting services as parameters to 'Configure'."; § When to suppress warnings: "It is safe to suppress this rule if updating the application to remove the call to `BuildServiceProvider` is non-trivial and you have thoroughly tested the application to ensure multiple singleton services are not added." (fetched)
- .NET dependency-injection guidelines, dotnet/docs `docs/core/extensions/dependency-injection/guidelines.md` § Recommendations: "Calling `BuildServiceProvider` typically happens when the developer wants to resolve a service when registering another service. Instead, use an overload that includes the `IServiceProvider` for this reason."; § Shared instance, limited lifetime: "Register the instance with a scoped lifetime. Use `IServiceScopeFactory.CreateScope` to create a new `IServiceScope`. Use the scope's `IServiceProvider` to get required services." (fetched)
- .NET architecture guide, dotnet/docs `docs/architecture/modern-web-apps-azure/common-web-application-architectures.md` § UI Layer: "The `Startup` class or _Program.cs_ file is responsible for configuring the application, and for wiring up implementation types to interfaces. The place where this logic is performed is known as the app's *composition root*, and is what allows dependency injection to work properly at run time." (fetched)
- Guice wiki `GettingStarted.md`, comment in `main()`: "Most applications will call this method exactly once, in their main() method."; wiki `Scopes.md` § Singleton: "reuses the same instance during the lifetime of an application within a single injector"; google/guice `core/src/com/google/inject/Injector.java`, `createChildInjector`: "Returns a new injector that inherits all state from this injector. All bindings, scopes, interceptors and type converters are inherited" (fetched)
- Spring Framework reference, `framework-docs/modules/ROOT/pages/core/beans/factory-scopes.adoc` § The Singleton Scope: "The scope of the Spring singleton is best described as being per-container and per-bean." (fetched)
- Dagger dev guide `dev-guide/subcomponents.md`: "Subcomponents are components that inherit and extend the object graph of a parent component. You can use them to partition your application's object graph into subgraphs either to encapsulate different parts of your application from each other or to use more than one scope within a component."; § Subcomponents and scope: "In Dagger, a component can be associated with a scope by annotating it with a `@Scope` annotation. In that case, the component implementation holds references to all scoped objects so they can be reused."; `dev-guide/testing.md`: "It is generally recommended to create a Dagger component in your tests to instantiate objects, whether that is a larger test component for many tests or a small focused test component for the individual test." (fetched)
- Caveat: the analyzer and the guideline cover one container library, and the per-container scope quoted for three more, a generated component among them, carries the mechanism across.
