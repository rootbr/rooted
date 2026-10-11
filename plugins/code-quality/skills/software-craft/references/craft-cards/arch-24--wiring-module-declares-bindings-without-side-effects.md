---
title: Code that declares a wiring module's bindings opens no connection, starts no server or thread and holds no other resource open, and the application starts its services after the container is built
rule_id: ARCH-24
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['\bextends\s+(?:Abstract|Private)Module\b', '\bvoid\s+configure\s*\(\s*\)', '[.]\s*to(?:Instance|ConstantValue)\s*\(|\buseValue\s*:|\bfx\s*[.]\s*Supply\s*\(', '\bbinder\s*[.]\s*bind\w*\s*\(', '\bIServiceCollection\b|\bConfigureServices\s*\(', '\b(?:builder|services)\s*[.]\s*(?:Services\s*[.]\s*)?Add\w*\s*[<(]']
scope: file
check_kind: semantic
severity_default: minor
---

# Code that declares a wiring module's bindings opens no connection, starts no server or thread and holds no other resource open, and the application starts its services after the container is built

## Thesis
Code that runs while a wiring module declares its bindings only describes the object graph: it opens no connection, starts no server, thread or scheduled task, and leaves no other resource open after the declaration returns. The work goes into a service with start and stop operations. The application's entry point starts that service after it builds the container, and adds a shutdown hook that releases the service's resources when the application stops.

## Rationale
Where the container gives a wiring module no shut-down step, a connection the module opens while it runs has no hook that closes it. A module that opens a database as it runs is difficult to unit-test. A container that supports overriding a module lets a lightweight or test service substitute for a production one; when the module creates the production service while it runs, that override is ineffective. A service that the entry point starts after the container is built, with a shutdown hook beside it, gives each resource a hook that releases it when the application stops.

## Example
```java
bad:  class StoreModule extends AbstractModule {
        protected void configure() { bind(Store.class).toInstance(Store.connect(url)); }
      }
good: protected void configure() { bind(Service.class).to(StoreService.class); }
      public static void main(String[] args) throws Exception {
        Service store = Guice.createInjector(new StoreModule()).getInstance(Service.class);
        store.start();
        Runtime.getRuntime().addShutdownHook(new Thread(store::stop));
      }
```

## Limits
The rule reaches the code that runs as part of the module's execution, which includes an instance the module constructs in order to bind it. The entry point that takes services from the built container, starts them and registers their shutdown hooks is where the work belongs, and its start calls are no finding. A factory function that the container calls when it creates a service runs after the bindings are declared and lies outside this check.

## Validator
Grep the hunk for a wiring module or a registration routine: a class extending the container's module base, a `configure()` override, a binding to a ready-made instance, a service-collection registration call. Open the file and read every statement that runs while the bindings are declared, including the constructors of instances bound as ready-made objects and the helpers those statements call where the file defines them; judge a call into code the file does not define by its name, its receiver and its arguments. Trace each call to what it does: opening a database or network connection, binding a socket or starting a server, starting a thread or a scheduled task, or leaving another resource open after the declaration returns; a log line and a configuration read that closes its file within the statement leave nothing open. Leave the entry point's start calls after the container is built, and factory functions the container calls later, outside this check. Validator question: **Does code that runs while the wiring module declares its bindings open a connection, start a server, thread or scheduled task, or leave another resource open after the declaration returns?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-24`, severity minor, `file`, `symbol`, `code` = the declaration-time statement that opens the connection, starts the server or thread, or leaves the resource open, `fix` = the work moved into a service with start and stop operations that the module only binds and the entry point starts after the container is built, with a shutdown hook, in the file's language, `rationale` = which of the three costs applies: the resource without a hook to close it, the module test that needs the real resource, or the override that the eager construction defeats).

## Source
- Google Guice wiki, "Modules should be fast and side-effect free", google/guice wiki `ModulesShouldBeFastAndSideEffectFree.md` (fetched): "It's tempting to connect to a database connection or to start an HTTP server in your Guice module. Don't do this! [...] Modules start up, but they don't shut down. Should you open a database connection in your module, you won't have any hook to close it. [...] If a module opens a database as a course of execution, it becomes difficult to write unit tests for it. [...] Guice modules support overrides, allowing a production service to be substituted with a lightweight or test one. When the production service is created as a part of module execution, such overrides are ineffective. Rather than doing work in the module itself, define an interface that can do the work at the proper level of abstraction. [...] After creating the Injector, we finish bootstrapping our application by starting its services. We also add shutdown hooks to cleanly release resources when the application is stopped."
- .NET documentation, "Dependency injection guidelines", dotnet/docs `docs/core/extensions/dependency-injection/guidelines.md` § Services not created by the service container (fetched): "builder.Services.AddSingleton(new ExampleService()); [...] The `ExampleService` instance is not created by the service container. The framework does not dispose of the services automatically. The developer is responsible for disposing the services."
- Caveat: both sources are container documentation; the problem list is stated for one container's modules, and the second container's documentation states the disposal gap for an instance constructed at registration.
