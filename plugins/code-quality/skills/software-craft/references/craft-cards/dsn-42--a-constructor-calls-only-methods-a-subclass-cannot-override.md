---
title: A constructor of a class open to subclassing calls, directly or indirectly, only methods a subclass cannot override
rule_id: DSN-42
domain: design
step: [design, implement]
applies_to: [object-oriented]
triggers: ['^\s*(public|protected|private)\s+[A-Z]\w*\s*\(', '^\s*[A-Z]\w*\s*\([^)]*\)\s*(throws\s[^{]*)?\{', '^\s*((public|protected|private)\s+)?constructor\s*\(', '^\s*def\s+__(init|post_init|setstate|copy|deepcopy)__\s*\(', '\b(Object|void|[A-Z]\w*)\s+(clone|readObject)\s*\(']
scope: file
check_kind: semantic
severity_default: major
---

# A constructor of a class open to subclassing calls, directly or indirectly, only methods a subclass cannot override

## Thesis
A constructor of a class open to subclassing calls on the object under construction only methods a subclass cannot override: static, private or final methods, or a method reached through a class-private alias, an alias whose mangled name a subclass's same-named method does not replace. Where every method is effectively virtual and a private method is private only by naming convention, a static or private method called through the object can be overridden as well, so only a method marked final or reached through a class-private alias qualifies. Each method the constructor calls that way in turn calls no overridable method on that object. A routine that builds the object in a constructor's place, such as a copy routine or a deserialization routine, follows the same rule; in a copy routine the object under construction is the copy it builds.

## Rationale
Where a subclass's constructor starts by contract by calling its parent's constructor, the subclass's own initialization has not finished while the parent's constructor runs: fields that the subclass's constructor initializes are not yet set, and where the base class's fields are initialized and its constructor runs before the derived class's fields are initialized, a field the subclass initializes at its declaration is not yet set either. The actual type that executes a virtual method is not selected until run time, so when a subclass overrides a method its parent's constructor calls, the call runs the override on an incompletely constructed object. An override that depends on fields the subclass's constructor initializes, or that assumes, as a subclass usually does in all its methods, that its parent is completely initialized, then uses uninitialized data: bugs can appear in the constructor, for instance a field that is still null may cause a null-reference error, or the unset value is stored somewhere else to blow up later, and the failure can be difficult to debug. The call may also leak a reference to the partially constructed object. Static, private and final methods, where the language keeps a subclass from overriding them, are the ones safe to call from a constructor, and they stay safe only while they call no overridable method transitively. A deserialization routine plays the role of the object's constructor, so initialization is not complete until it exits, and an overridable method it calls gets access to the object's state before it is fully initialized; an overridable method a copy routine calls can likewise observe or modify the copy in a partially initialized state. Where every method is effectively virtual and a derived class's initializer calls the base initializer explicitly, a method of a base class that calls another method defined in the same base class may end up calling a derived class's override of it, so a base initializer reaches the override the same way; a class-private alias, whose mangled name a subclass's same-named method does not replace, lets subclasses override the method without breaking the initializer's call.

## Example
```java
bad:  class Base {
          public Base() { configure(); }
          protected void configure() { ... }
      }
good: class Base {
          public Base() { configureDefaults(); }
          private void configureDefaults() { ... }
      }
```

## Limits
A class closed to subclassing, such as a final class, is outside the rule: an analyzer that checks the rule reports only the constructor of a type that can be inherited. A class that lists the subclasses permitted to extend it stays within the rule, since each permitted subclass can override the methods its constructor calls. Where finality is enforced by a type checker rather than by the runtime, a class or method marked final counts as closed, since a type checker is to prohibit subclassing a class marked final and overriding a method marked final. A call on another object, one passed in or created by the constructor, is outside the rule; the rule concerns calls on the object under construction, which in a copy routine is the copy the routine builds, not the object being copied. A call made on purpose, such as a documented hook the constructor invokes, stays within the rule: none of the cited rules exempts it, and one says not to suppress the warning and to redesign the constructor to eliminate the call. Where a type reuses another by embedding, the embedded type's methods, when invoked, take the inner value as receiver and not the outer one, so a call through that receiver never reaches a method of the outer type; where no type can inherit another type's fields and method implementations, no parent constructor runs for a child type. The rule does not reach such types.

## Validator
Grep the added lines for a constructor or initializer signature, a copy or deserialization routine that builds the object, and a call added inside one of them. Open the file and read the class; skip it when the class is closed to subclassing. For each call the constructor or routine makes on the object under construction, through an explicit self-reference or an implicit receiver, or, in a copy routine, through the reference to the copy the routine builds, find the called method's declaration and decide whether a subclass can override it: a method is overridable unless it is static, private or final, or reached through a class-private alias; where every method is effectively virtual, every method called through the object is overridable unless it is marked final or reached through such an alias; a method the class inherits and the file does not declare counts as overridable unless it is known to be final. For each non-overridable callee, trace the calls it makes on the object the same way. Validator question: **Does a constructor, or a copy or deserialization routine that builds the object, of a class open to subclassing call on the object under construction, directly or through a non-overridable method, a method a subclass can override?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-42`, severity major, `file`, `symbol`, `code` = the call to the overridable method in the constructor or routine, or the call in the helper it reaches, verbatim from the diff, `fix` = the constructor calling in its place a method a subclass cannot override (a private, static or final one where the language keeps a subclass from overriding it, or one reached through a class-private alias), with the overridable step moved out of construction, or the class closed to subclassing, in the file's language, `rationale` = the overridable method called, the call path from the constructor to it, and the subclass state an override would find unset).
