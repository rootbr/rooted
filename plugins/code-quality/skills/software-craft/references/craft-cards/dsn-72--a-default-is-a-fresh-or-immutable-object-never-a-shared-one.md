---
title: A default used when a caller omits an argument or field is a fresh or immutable object, never one mutable object shared by every call
rule_id: DSN-72
domain: design
step: [implement]
applies_to: [universal]
triggers: ['[(,]\s*(\w+\s*(:\s*[^=,()]+)?=\s*)?(this[.]|self[.])?_?\w*(DEFAULT|[Dd]efault)\w*\s*[,)]', '\b\w+\s*:?=\s*&?(this[.]|self[.]|\w+[.])?(DEFAULT|Default[A-Z]|default[A-Z])\w*\s*;?\s*$']
scope: file
check_kind: mechanical
severity_default: major
---

# A default used when a caller omits an argument or field is a fresh or immutable object, never one mutable object shared by every call

## Thesis
When a parameter or a field takes a default whenever the caller omits it, the default is an immutable object or a new object created for each call or each instance. This holds for a default written in the declaration and for one that an overload or a constructor supplies for the omitted argument. A default that is one mutable object, created once when the routine is defined or held in a class body or a field that the default refers to, is shared by every call or instance that omits the argument. A change made through one call then persists into every later call. The rule applies whether or not the code in view changes the default, because the shared object exposes mutable state that can couple the calls.

## Rationale
Every call that omits the argument receives the object the default yields, so when that object is one mutable object, all of those calls share it, and every instance that takes a field default from it shares it too. If the object is modified, the modification persists across calls, and a change made through one instance affects all other instances. The sharing is not obvious: it is often expected that a call creates a new object for its default, yet the calls are coupled through the one object, which can lead to unexpected behaviour and bugs. A final or read-only field that holds the default does not make it safe while the object itself is mutable, and neither does a read-only declared type, since the object could still get passed to unchecked code. An immutable object is safe from change. A new object created inside the routine or the constructor for each call or instance is shared with no other call or instance. Either form removes the coupling between the calls that omit the argument.

## Example
```java
bad:  private static final List<String> DEFAULT_PATHS = new ArrayList<>();
      private List<String> paths = DEFAULT_PATHS;
      void process(Item item) { process(item, DEFAULT_PATHS); }
good: private List<String> paths = new ArrayList<>();
      void process(Item item) { process(item, new ArrayList<>()); }
```

## Limits
Where the language evaluates a default initializer at each call, a new object written in the initializer, such as an empty-collection literal, is created anew for each call and meets the rule; there the rule reaches a default that refers to a mutable object stored outside the call. A mutable default kept on purpose to cache computation results across calls is outside the rule, since there the sharing is intended and a new or immutable default does not work for that use. So is a field that its declaration marks as one variable intended to be shared across all instances, while no instance takes it as its own default and no routine supplies it for an omitted argument. A field of a type whose framework copies the default into each new instance gives each instance its own object, and the rule does not reach it. The project context can reject the finding by naming a default the project shares on purpose.

## Validator
In the hunk, find each default a caller gets by omission: a default value in a routine signature, a field or class-body attribute initialised with a value each instance takes unless the caller sets it, an overload or constructor that passes a value for the argument its caller omitted, and a fallback such as `x ?? d` or `x or d` applied to an absent argument. Read what the default yields. Where it is a literal or a constructor call that creates a mutable collection or object, go on when the language evaluates the default once, at definition, or the value sits in a class body shared by the instances; skip it when the language evaluates the initializer at each call or the value is assigned inside the routine or the constructor. Where it is a name that refers to a stored object, such as a field, a constant or a module-level variable, open the file and read that name's declaration and initializer; go on only when the object is mutable, counting a mutable object behind a final or read-only reference, or behind a read-only declared type, as mutable. Skip a default named or commented as a cache of results across calls, a class-level field its declaration marks as shared across all instances on purpose while no instance takes it as its own default and no routine, overload or constructor supplies it for an omitted argument, a field of a type whose framework copies defaults into each new instance, and a default the project context names as shared on purpose. Validator question: **Does every call or instance that omits this argument or field receive the same mutable object?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-72`, severity major, `file`, `symbol`, `code` = the parameter default, field initializer or delegating call that supplies the shared default, quoted verbatim from the diff, `fix` = the default rewritten as an immutable object or as a new object created inside the routine or the constructor for each call or instance, in the file's language, `rationale` = the one mutable object every omitting call or instance shares, and how a change made through one call reaches all later ones).
