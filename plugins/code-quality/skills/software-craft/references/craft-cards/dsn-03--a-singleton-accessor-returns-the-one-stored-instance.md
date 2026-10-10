---
title: A singleton's access operation returns the one stored instance on every call, and neither it nor an overload of it constructs a new object per call
rule_id: DSN-03
domain: design
step: [implement, refactor]
applies_to: [universal]
triggers: ['(?i)\b(get_?instance|instance|shared_?instance|default_?instance)\s*\(', '\b(INSTANCE|_instance|__instance|sharedInstance|defaultInstance)\b|\bstatic\b.*\binstance\b|\bdef\s+__new__\s*\(|\b(sync[.]Once\w*|OnceLock|LazyLock|OnceCell|get_or_init|lazy_static!)', '\breturn\s+(new\s+[A-Z]\w*\s*[(<]|&?[A-Z]\w*\s*\{|[A-Z]\w*::new\s*\(|cls\s*\(|(?!(Ok|Err|Some)\b)[A-Z]\w*\s*\()']
scope: file
check_kind: semantic
severity_default: major
---

# A singleton's access operation returns the one stored instance on every call, and neither it nor an overload of it constructs a new object per call

## Thesis
A type or module meant to have exactly one instance hands that instance to its clients through an access operation — an accessor such as `getInstance` or `instance()`, a static property, or a module- or package-level function — and that operation returns the instance that was created once, when the type or module loaded or on the first call, and stored; it returns that same stored instance on every later call. The accessor does not return a newly constructed object, and does not return an object it built into a local variable without also assigning it to the stored field. Every overload or variant of the accessor, including one that takes arguments, returns the same stored instance, not an object it constructs and not one the caller passed in.

## Rationale
A singleton class should only ever have one instance. Because there is only one instance, any change made to it is reflected everywhere it is used. An accessor that always creates a new object does not comply with the pattern, and one that fails to check whether an instance has already been created may create multiple instances; an overload whose instance is not cached creates a new object on every invocation. Each caller then holds a separate object, so the sharing that rests on there being one instance is lost. Storing the instance when it is created and returning the stored instance from every accessor restores the single object and, with it, the shared state.

## Example
```typescript
bad:  class Registry {
        private static instance?: Registry;
        static getInstance(): Registry { return new Registry(); }
      }
good: class Registry {
        private static instance?: Registry;
        static getInstance(): Registry {
          return (Registry.instance ??= new Registry());
        }
      }
```

## Limits
The rule reaches only the accessor of a type or module meant to have one instance. An operation whose documentation says that each call returns a new object keeps that contract whatever its name: a static `getInstance` that takes an algorithm name and returns a new object implementing that algorithm is not a singleton accessor. A type that keeps one instance per key, and whose accessor takes the key and returns the instance stored for it, meets its own contract: a type with a hidden constructor whose `getInstance` methods take a currency code or a locale and return the one instance for that currency is outside the rule. An instance created eagerly when the type or module loads and returned from the accessor satisfies the rule, and so does one created on first access by a once-only initialisation primitive or by a memoising wrapper around a parameterless accessor, which returns its cached result on later calls. Whether lazy creation stays single when several threads call the accessor at once — a lock around the check, double-checked locking, the choice of a once-only primitive — is a concurrency question outside this rule; an accessor that synchronises and then returns a new object still fails it. A tolerance stated in `project_context` that names an accessor as a deliberate per-call factory rejects the finding.

## Validator
Grep the added lines for an accessor named like `getInstance`, `instance`, `sharedInstance` or `defaultInstance`, a stored field such as `INSTANCE` or `_instance`, an instance-creation hook (`__new__`), a once-only initialisation primitive, and a `return` of a newly constructed object. Open the file and decide from it whether the type or module is meant to have one instance: a single field or module-level variable that holds the one instance of the type, a creation hook that checks for an existing instance, or a name or comment that says singleton or shared instance; a hidden constructor alone does not decide it. Drop an accessor whose comment or documentation says it returns a new object per call, and a type that keeps its instances in a map or table keyed by an accessor argument, which has one instance per key. For each accessor, overload or variant that the hunk adds or changes, trace every return path, reading the stored field and the other accessors in the file. The object that a once-only primitive, or a memoising wrapper around a parameterless accessor, creates on the first call and returns on every later one is the stored instance. A path that returns the stored instance passes when that instance is created at load, by such a primitive or wrapper, or only after a check finds no instance stored; a path that returns a newly constructed object, a local variable never assigned to the stored field, or an object the caller passed in fails, and so does a path that creates and stores a new object on a call that finds an instance already stored. Validator question: **does an access operation of a single-instance type or module, or an overload or variant of it, construct a new object on a call after the first, or return on some path an object other than the one stored instance — a newly constructed object, an unstored local or a caller's argument?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-03`, severity major, `file`, `symbol`, `code` = the accessor's or the overload's return statement quoted verbatim from the diff, `fix` = the accessor storing the instance when it is first created, or at load, and returning the stored instance on every path, in the file's language, `rationale` = naming the return path that hands out an object other than the stored instance and the state callers then no longer share).
