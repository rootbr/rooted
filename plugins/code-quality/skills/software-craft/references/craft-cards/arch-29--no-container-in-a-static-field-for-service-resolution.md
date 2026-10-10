---
title: No application code stores a dependency-injection container, injector or service provider in a static field, global variable or module-level name for other code to resolve services from, and code requests the container's static injection only while migrating from static factories
rule_id: ARCH-29
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['\bstatic\b[^=;(]*\b(?:IServiceProvider|ServiceProvider|ApplicationContext|BeanFactory|Injector|IContainer)\b', '\b\w*[Ss]tatic_?[Ii]njections?\b', '(?:@|\[)\s*Inject\w*(?:\([^)]*\))?\]?\s+(?:(?:public|protected|private|internal)\s+)*static\b', '\b(?:ServiceLocator|ApplicationContextHolder|SpringContext\w*|IoC|ServiceProviderAccessor)\s*[.]\s*(?:Current|Instance|get\w*|Get\w*|Resolve)\b', '^\s*(?:export\s+)?(?:(?:const|let|var)\s+)?(?:\w+[.])?(?:container|injector|serviceProvider|locator)\s*(?::[^=]+)?=\s*(?:new\s+)?(?:\w+[.])?\w*(?:Container|Injector|Provider|Locator)\w*\s*\(']
scope: callers
check_kind: semantic
severity_default: minor
---

# No application code stores a dependency-injection container, injector or service provider in a static field, global variable or module-level name for other code to resolve services from, and code requests the container's static injection only while migrating from static factories

## Thesis
The application's container, injector or service provider stays out of static fields, global variables and module-level names from which other code resolves services, and the application defines no service locator as a global. The container's static injection, the facility that injects a class's static members so that objects gain access to injected types without being injected themselves, is requested only while an application migrates from static factories to injection; a new application leaves it unused.

## Rationale
Dependency injection is an alternative to static and global object access, and mixed with static access its benefits may not be realised. Static state works against testability: non-constant values held by static fields are hard to manage, and a static singleton replaced by a test double is hard to tear down reliably, and that difficulty interferes with other tests. Global state is unsafe when otherwise independent functions of one program interact through it, when independent test cases interact through it, when users are tempted to replace it with a test double, or when users must respect an ordering requirement, such as whether initialisation has run or flags are parsed yet. A service locator defined as a global is one of these forms of global state. Static injection exists to ease migration from a statically configured application to an injected one: it lets objects participate in injection partially while that migration proceeds incrementally.

## Example
```java
bad:  final class ServiceLocator { static Injector injector; @Inject static Clock clock;
        static <T> T get(Class<T> type) { return injector.getInstance(type); } }
      ServiceLocator.injector = Guice.createInjector(new AppModule()); // in main
      Orders orders = ServiceLocator.get(Orders.class);
      requestStaticInjection(ServiceLocator.class); // in a module's configure()
good: final class Checkout {
        private final Orders orders;
        @Inject Checkout(Orders orders) { this.orders = orders; }
      }
      Checkout checkout = injector.getInstance(Checkout.class); // entry point only
```

## Limits
The static keyword alone is not the defect: static classes are acceptable and even preferred, and a static pure function such as a sort or a math routine is fine. Static injection serves its documented purpose in an application migrating from static factories to injection incrementally, where it is a helpful crutch. A locator that is not defined as a global is outside this rule, which concerns the locator being defined as a global. Exceptions to the recommendation against static access to services are rare and are mostly special cases within the framework itself. A framework's own documented static proxy or global helper over its container, whose documentation provides for replacing the resolved instance in tests, is the framework's convention and outside this rule; the rule governs a static field, global variable or module-level name, whoever declares it, into which application code stores a container, injector, provider or locator, by assignment or through a library's static setter.

## Validator
Grep the hunk for a static field, global variable or module-level name whose declared type or initializer is a container, injector, service provider, bean factory or application context; for a static holder or accessor that returns one; for a registration that requests static injection; and for an injection annotation on a static member. Open the callers at scope and trace whether code other than the place that builds the object graph resolves services through that static or global name, and whether application code stored a container, injector, provider or locator in that name, by assignment or through a library's static setter, or the name is a framework's documented static proxy or global helper over a container the framework builds and stores itself. For a static-injection hit, check whether the hunk belongs to a migration from static factories; a static member that holds no container, injector, provider or locator and that static injection does not fill, such as a constant or a pure function, is outside the rule. Validator question: **Is a container, injector, service provider or service locator stored by application code, by assignment or through a library's static setter, in a static field, global variable or module-level name that other code resolves services from, or does code outside a migration from static factories request static injection?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-29`, severity minor, `file`, `symbol`, `code` = the static or global declaration holding the container, or the static-injection request, and one call site resolving a service through it, verbatim from the diff, `fix` = the consumer taking the service as a constructor parameter and the container staying local to the place that builds the object graph, in the file's language, `rationale` = the static access to services that injection is an alternative to and the test interference that static state causes).
