---
title: A servlet, filter, controller or other singleton bean holds no mutable instance field unless the field's type is thread-safe
rule_id: CC-18
domain: concurrency
triggers: ['@(Rest)?Controller', '@(Service|Component|Repository|Configuration|ControllerAdvice)', 'HttpServlet', '(implements|extends)\s+\w*Filter\b', '@WebServlet', '@Singleton']
scope: file
check_kind: mechanical
severity_default: major
---

# A servlet, filter, controller or other singleton bean holds no mutable instance field unless the field's type is thread-safe

## Thesis
A class of which the container creates one instance and invokes from many request threads — a servlet or filter, a Spring singleton bean such as a `@Controller`, `@Service`, `@Component` or `@Repository`, an `@Singleton` — declares no instance field that a request writes: each field is `final` and holds an immutable or thread-safe object, and per-request state lives in method locals, in the request, or in a request- or prototype-scoped bean.

## Rationale
The servlet container may send concurrent requests through the `service` method of one servlet instance, and the developer "must make adequate provisions for concurrent processing with multiple threads". Spring manages "only one shared instance of a singleton bean" and returns it for every request; singleton is the default scope, and the reference recommends the prototype scope for stateful beans and the singleton scope for stateless ones. A plain instance field on such a class is therefore shared by every request thread at once: a counter loses increments, a "current user" field belongs to whichever request wrote it last, a `StringBuilder` or `HashMap` field is mutated concurrently. Synchronizing the `service` method is discouraged by the servlet specification for its effect on performance; removing the state is the fix.

## Example
```java
bad:  @RestController class OrderController {
          private Order current;                       // one instance, many threads
          @PostMapping("/orders") void create(@RequestBody Order o) { current = o; save(current); } }
good: @RestController class OrderController {
          private final OrderRepository repo;          // injected, thread-safe
          @PostMapping("/orders") void create(@RequestBody Order o) { repo.save(o); } }
```

## Limits
Applies to a class the container instantiates once. A field that is `final` and holds an injected collaborator, a `ConcurrentHashMap`, an `AtomicLong`, a `DateTimeFormatter` or another documented thread-safe object is not flagged. A bean declared `@Scope("prototype")` or `@RequestScope`, and a class the project context lists as single-threaded by construction (a test double, a command object), are out of scope. A non-final field assigned once in an `@PostConstruct` method before the bean serves requests, and never written again, is a tolerance the project context may state.

## Validator
On the triggered hunk take each class marked by the annotation or supertype. Open the file: list every instance field that is not `final`, or that is `final` but holds a mutable non-thread-safe object (a plain collection, a builder, a format), and find the methods that write or mutate it on a request path. Validator question: **does this single-instance class hold an instance field that a request thread writes or mutates without a lock?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CC-18`, severity major, `file`, `symbol`, `code` = the class annotation, the field and the request-path write quoted verbatim from the diff, `fix` = the field moved into a local, the request, or a request-scoped bean, or the thread-safe type, `rationale` naming the one shared instance and the requests that race on it).

## Source
Jakarta Servlet Specification, "Servlet Life Cycle" → "Request Handling" → "Multithreading Issues" — "A servlet container may send concurrent requests through the service method of the servlet. To handle the requests, the Application Developer must make adequate provisions for concurrent processing with multiple threads in the service method"; "It is strongly recommended that Developers not synchronize the service method ... because of the detrimental effects on performance". Spring Framework reference, "Bean Scopes" → "The Singleton Scope" — "Only one shared instance of a singleton bean is managed"; "you should use the prototype scope for all stateful beans and the singleton scope for stateless beans". SpotBugs `MSF_MUTABLE_SERVLET_FIELD`; SonarSource RSPEC-2226 "Servlets should not have mutable instance fields".
