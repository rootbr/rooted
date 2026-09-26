---
title: Class.forName, getDeclaredMethod, getMethod and getField on a hot path run once and are cached
rule_id: PF-32
domain: performance
triggers: ['Class[.]forName\(', 'getDeclaredMethod\(', 'getMethod\(', 'getDeclaredField\(', 'getField\(', 'getDeclaredConstructor\(', 'MethodHandles[.]lookup\(', 'loadClass\(']
scope: file
check_kind: mechanical
severity_default: minor
---

# Class.forName, getDeclaredMethod, getMethod and getField on a hot path run once and are cached

## Thesis
A reflective lookup — `Class.forName(name)`, `loader.loadClass(name)`, `clazz.getDeclaredMethod(...)`, `getMethod`, `getDeclaredField`, `getDeclaredConstructor`, a `MethodHandles.Lookup.find*` — executes once per class or member, at class initialization or in a cache keyed by the name, and the resulting `Class`, `Method`, `Field` or `MethodHandle` is what the per-request code uses; the lookup itself never sits inside a request handler or a loop.

## Rationale
`Class.forName` attempts to locate and load the named class through the caller's loader and initializes it, so each call on a hot path repeats the name lookup for a class that is already loaded; and, when the loader's `loadClass` runs, that method — unless overridden — synchronizes on the class-loading lock for the entire class loading process and consults the parent loader before its own path. `getDeclaredMethod` and its siblings search the class's declared members by name and parameter types and return a fresh copy of the `Method` (or `Field`, `Constructor`) on every call — an allocation plus a scan per call. `Method.invoke` checks access on every invocation and passes arguments through an `Object[]` with boxing, whereas a method handle is access-checked when it is created and gives more direct and efficient access to the member — which is why the cached form of a hot call is a `MethodHandle` rather than a `Method`.

## Example
```java
bad:  Object call(Object target, String prop) throws Exception {
          Method m = target.getClass().getDeclaredMethod("get" + prop);   // per call
          return m.invoke(target);
      }
good: private static final MethodHandle GET_NAME;
      static {
          try { GET_NAME = MethodHandles.lookup().findVirtual(Person.class, "getName", MethodType.methodType(String.class)); }
          catch (ReflectiveOperationException e) { throw new ExceptionInInitializerError(e); }
      }
      String name(Person p) throws Throwable { return (String) GET_NAME.invokeExact(p); }
```

## Limits
A lookup at startup, in a static initializer, in a framework's one-time scan, or behind a `ConcurrentHashMap.computeIfAbsent` cache keyed by the class and member is correct. A lookup whose target name is unbounded per request (an arbitrary user-supplied property) is cached per distinct name with a bounded cache, or redesigned. A `Class.forName` used for its side effect of initializing a class once (driver registration) is not a hot-path pattern. Whether reflective access to a user-named member is safe is a security concern outside this rule.

## Validator
On the triggered hunk find each `Class.forName`, `loadClass`, `getDeclaredMethod`, `getMethod`, `getDeclaredField`, `getField`, `getDeclaredConstructor` and `Lookup.find*`. Open the file: is the call inside a method invoked per request, per message or per element, with no cache in front of it? Validator question: **does this hot path repeat a reflective lookup where a cached Class, Method or MethodHandle would serve?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-32`, severity minor, `file`, `symbol`, `code` = the lookup quoted verbatim from the diff, `fix` = the lookup hoisted into a `static final` field or a cache keyed by the name — a `MethodHandle` from `unreflect` or `findVirtual` rather than a cached `Method` where the call itself is hot, since `Method.invoke` re-checks access on every invocation — `rationale` naming the per-call lookup and, for `Class.forName`, the class-loading lock).

## Source
`java.lang.Class#forName(String)` Javadoc, Java SE 21 — equivalent to `Class.forName(className, true, currentLoader)`, which "attempts to locate and load the class or interface" and initializes it; `java.lang.ClassLoader#loadClass(String, boolean)` — "Unless overridden, this method synchronizes on the result of getClassLoadingLock method during the entire class loading process"; `#getClassLoadingLock` — a dedicated per-name object for parallel-capable loaders, otherwise the loader itself. `java.lang.Class#getDeclaredMethod` source, Java SE 21 — `searchMethods` scans the declared methods and the result is returned through `ReflectionFactory.copyMethod` (implementation detail). `java.lang.invoke.MethodHandle` class Javadoc — "Unlike with the Core Reflection API, where access is checked every time a reflective method is invoked, method handle access checking is performed when the method handle is created"; method handles converted from reflective objects "generally provide more direct and efficient access to the underlying class members".
